# coding: utf8
"""scan.py: Utilites to scan for Debian packages in a folder.
Forked by ongyx from the original dpkg-scanpackages.py to use python-debian as the backend.
"""

import collections
import collections.abc
import email
import email.message
import glob
import hashlib
import importlib
import os
import pathlib
import sys
from types import ModuleType
from typing import Generator, Union

from cidercellar import pydpkg
import debian.deb822
import debian.debfile
import debian.debian_support

# Type hints
Path = Union[str, pathlib.Path]

# Known compression methods for Packages file mapped to module names.
# These are (problably) the most common compression methods.
PACKAGES_COMPRESSION = {".gz": "gzip", ".bz2": "bz2", ".xz": "lzma"}

# Convinent constants for compression.
GZIP = ".gz"
BZIP2 = ".bz2"
XZ = ".xz"

# Standard hashes for checksums.
HASHES = {
    "MD5Sum": hashlib.md5,
    "SHA1": hashlib.sha1,
    "SHA256": hashlib.sha256,
    "SHA512": hashlib.sha512,
}


class DebError(Exception):
    pass


def lazy_import(module_name: str) -> ModuleType:
    """Import a module (if it has not been imported yet).

    Args:
        module_name: The module.

    Returns:
        The module itself.
    """

    # HACK: much nicer than a long block of elifs
    # so that we don't have to keep re-importing modules.
    module = sys.modules.get(module_name)
    if module is None:
        # not imported yet
        module = importlib.import_module(module_name)

    return module


def extract_packages(dir: Path) -> email.message.Message:
    """Get the Packages file from a directory.
    This searches for the Packages file with different extensions in the directory
    (Packages.bz2, Packages.gz, et al.), extracts and returns the first one it finds.
    If not, it will fallback to just getting the normal Packages file
    (no compression).

    Args:
        dir: The path to the folder containing the Packages file.

    Raises:
        FileNotFoundError, if the Packages file could not be gotten.

    Returns:
        The Packages file as a Message object.
    """

    file = pathlib.Path(dir) / "Packages"

    for ext, module_name in PACKAGES_COMPRESSION.items():

        compressor = lazy_import(module_name)

        actual_file = file.with_suffix(ext)
        if not actual_file.exists():
            continue

        with compressor.open(str(actual_file), mode="rt") as f:
            # we'll just return the first one that exists
            return email.message_from_file(f)

    # compression not supported
    return None


def compute_hash(file: pathlib.Path, bsize: int = 8192) -> dict:
    """Compute the MD5, SHA1, SHA256 and SHA512 hashes of a file.

    Args:
        file: The path to the file.
        bsize: How many bytes to digest at a time. Defaults to 8192 (128 * 64).

    Returns:
        A dictionary of the MD5, SHA1, SHA256 and SHA512 hashes as strings, mapped to their hashlib names.
    """

    hashes = {name: hash_class() for name, hash_class in HASHES.items()}

    with open(file, mode="rb") as f:
        while True:
            buffer = f.read(bsize)
            if not buffer:
                break

            for _, hash in hashes.items():
                hash.update(buffer)

    return {k: v.hexdigest() for k, v in hashes.items()}


def _compare_version(v1: str, v2: str) -> int:

    if v1.count("/") == 1:
        v1 = v1.partition("/")[0]

    if v2.count("/") == 1:
        v2 = v2.partition("/")[0]

    return pydpkg.Dpkg.compare_versions(v1, v2)


def sort_versions(versions: list) -> list:
    """Quicksort, for Debian package versions.
    Sorts from earliest to latest.
    Adapted from https://stackoverflow.com/a/18262384.

    Args:
        versions (list): The versions to sort.

    Returns:
        The sorted list (**not** sorted in-place).
    """

    less = []
    equal = []
    greater = []

    if len(versions) > 1:
        pivot = versions[0]

        for version in versions:
            cmp = _compare_version(version, pivot)

            if cmp < 0:
                less.append(version)
            elif cmp == 0:
                equal.append(version)
            elif cmp > 0:
                greater.append(version)

        return sort_versions(less) + equal + sort_versions(greater)

    else:
        return versions


class DebianTree(object):
    """A tree representing a Debian repo as a Packages file.

    Args:
        root: The path to the repository.
        deb_path: The relative path to the directory containing
            the Debian package files.
        deb_type: The type of the packages to scan for. Defaults to 'deb'.
        arch: The architecture of the packages to scan for. If None, all
            package architectures will be allowed. Defaults to None.
        allow_multiversion: Whether or not to allow multiple versions of
            the same package to be scanned for. Defaults to True.

    Attributes:
        root (pathlib.Path): See Args.
        deb_path (pathlib.Path): See Args.
        root_str (str): .path, as a string.
    """

    def __init__(
        self,
        root: Path,
        deb_path: Path,
        debtype: str = "deb",
        arch: str = None,
        allow_multiversion: bool = True,
    ) -> None:
        self.root = pathlib.Path(root).resolve().expanduser()
        self.deb_path = self.root / deb_path

        with (self.root / "Release").open() as f:
            self._release = email.message_from_file(f)

        # remove any hashes
        for hash in HASHES:
            if hash in self._release:
                # erase existing hashes of Packages file, will be added back in on build
                self._release[hash] = []

        self._debtype = debtype
        self._arch = arch
        self._multiversion = allow_multiversion
        self._tree = {}

    @property
    def root_str(self):
        return str(self.root)

    def _add_deb(self, debinfo: pydpkg.Dpkg) -> None:
        name, version, arch = [
            debinfo[f] for f in ("Package", "Version", "Architecture")
        ]

        if name not in self._tree:
            self._tree[name] = {}

        self._tree[name][f"{version}/{arch}"] = debinfo

    def find_debs(self) -> None:
        """Find all Debian package files in .deb_path, and add them to the tree."""

        for debfile in self.deb_path.glob(f"*.{self._debtype}"):
            debinfo = pydpkg.Dpkg(debfile)

            # arch check (i use arch btw).
            if self._arch is not None:
                if debinfo["Architecture"] != self._arch:
                    continue

            self._add_deb(debinfo)

    def _build(self, package: str) -> Generator[DebianInfo, None, None]:
        # need to reverse, so latest versions come first
        # simpler than changing the quicksort function itself
        versions = self._tree[package]
        version_names = versions.sort(key=_compare_versions).reverse()

        if not self._multiversion:
            latest_version = version_names[0].partition("/")[0]
            # because version name has the format 'actual_ver/arch',
            # there may be multiple archs for each version.
            # (Hence the .startswith().)
            version_names = [v for v in version_names if v.startswith(latest_version)]

        for v in version_names:
            yield versions[v]

    def build(self, compress_using: list = [GZIP]) -> str:
        """Build the Packages/Release file for this repo.

        Args:
            compress_using: Formats to compress the Packages file in.
                Format must be one of the module-level constants GZIP, BZIP2, or XZ.
                Defaults to [GZIP] (.gz compression).

        Returns:
            The Packages file content as a string.
        """

        paragraphs = []

        if not compress_using:
            raise DebError("no compression format(s) specified")

        self.find_debs()

        # iterate alphabetically
        for package in sorted(self._tree.items()):
            for debinfo in self._build(package):
                msg = debinfo.message
                paragraphs.append(str(debinfo))

        paragraphs.append("")

        packages_text = "\n".join(paragraphs)
        packages_path = self.root / "Packages"

        for format in compress_using:
            compression = lazy_import(PACKAGES_COMPRESSION[format])
            packages_path = packages_path.with_suffix(format)

            with compression.open(packages_path, mode="wt") as f:
                f.write(packages_text)

            # add hashes
            for name, digest in compute_hash(packages_path).items():
                self._release[name].append(
                    {
                        name.lower(): digest,
                        "size": packages_path.stat().st_size,
                        "name": packages_path.name,
                    }
                )

        with open("Release", mode="w") as f:
            f.write(str(self._release))

        return packages_text
