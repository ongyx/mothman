# coding: utf8
"""scan.py: Utilites to scan for Debian packages in a folder.
"""

import email
import email.message
import functools
import importlib
import logging
import pathlib
import sys
from types import ModuleType
from typing import Generator, Union

from . import pydpkg
from .__version__ import __version__ as ccver

# Type hints
Path = Union[str, pathlib.Path]

# Known compression methods for Packages file mapped to module names.
# These are (problably) the most common compression methods.
PACKAGES_COMPRESSION = {".gz": "gzip", ".bz2": "bz2", ".xz": "lzma"}

# Convinent constants for compression.
GZIP = ".gz"
BZIP2 = ".bz2"
XZ = ".xz"

_log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DebError(Exception):
    pass


def _actual(name: str) -> str:
    name = name.upper()
    if name == "MD5":
        name += "Sum"
    return name


def _debname(debinfo: pydpkg.Dpkg) -> str:
    return "_".join(debinfo[field] for field in ("Package", "Version", "Architecture"))


def lazy_import(module_name: str) -> ModuleType:
    """Import a module (if it has not been imported yet).

    Args:
        module_name: The module.

    Returns:
        The module itself.
    """

    # HACK: much nicer than a long block of elifs
    # so that we don't have to keep re-importing modules.
    _log.debug(f"lazy-importing {module_name}")
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

        _log.debug(f"decompressing {actual_file}")
        with compressor.open(str(actual_file), mode="rt") as f:
            # we'll just return the first one that exists
            _log.debug(f"parsing {actual_file}")
            return email.message_from_file(f)

    # compression not supported
    return None


def compute_hash(file: pathlib.Path, bsize: int = 8192) -> dict:
    """Compute the MD5, SHA1, SHA256 and SHA512 hashes of a file.

    Args:
        file: The path to the file.
        bsize: How many bytes to digest at a time. Defaults to 8192 (128 * 64).

    Returns:
        A dictionary of the MD5, SHA1, SHA256 and SHA512 hashes as strings,
            mapped to their hashlib names.
    """

    _log.debug(f"computing hash for {file}")

    hashes = {name: hash_class() for name, hash_class in pydpkg.HASHES.items()}

    with open(file, mode="rb") as f:
        while True:
            buffer = f.read(bsize)
            if not buffer:
                break

            for _, hash in hashes.items():
                hash.update(buffer)

    return {_actual(k): v.hexdigest() for k, v in hashes.items()}


def _compare_versions(versions: str) -> int:
    v1, v2 = versions

    if v1.count("/") == 1:
        v1 = v1.partition("/")[0]

    if v2.count("/") == 1:
        v2 = v2.partition("/")[0]

    return pydpkg.Dpkg.compare_versions(v1, v2)


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
        _log.debug(f"initalising repo {root}")
        self.root = pathlib.Path(root).resolve().expanduser()
        if str(deb_path) == ".":
            self.deb_path = self.root
        else:
            self.deb_path = self.root / deb_path
        self.release_path = self.root / "Release"

        with self.release_path.open() as f:
            _log.debug("parsing Release")
            self._release = email.message_from_file(f)

        # remove any hashes
        for hash in pydpkg.HASHES:
            if hash in self._release:
                # erase existing hashes of Packages file, will be added back in on build
                self._release[hash] = []

        self._debtype = debtype
        self._arch = arch
        self._multiversion = allow_multiversion
        self._tree = {}
        self._found_debs = False

    @property
    def root_str(self):
        return str(self.root)

    def _add_deb(self, debinfo: pydpkg.Dpkg) -> None:
        _log.debug(f"[{debinfo.Package}] adding deb")
        name, version, arch = [
            debinfo[f] for f in ("Package", "Version", "Architecture")
        ]

        if name not in self._tree:
            self._tree[name] = {}

        self._tree[name][f"{version}/{arch}"] = debinfo

    def find_debs(self) -> None:
        """Find all Debian package files in .deb_path, and add them to the tree.
        This should only be called once, subsequent calls will be ignored."""
        if self._found_debs:
            _log.warning(".find_debs() called more than once")
            return
        _log.info("finding debs")

        for debfile in self.deb_path.glob(f"*.{self._debtype}"):
            debinfo = pydpkg.Dpkg(debfile)

            # arch check (i use arch btw).
            if self._arch is not None:
                if debinfo["Architecture"] != self._arch:
                    continue

            self._add_deb(debinfo)

    def _build(self, package: str) -> Generator[pydpkg.Dpkg, None, None]:
        # need to reverse, so latest versions come first
        # simpler than changing the quicksort function itself
        _log.debug(f"[{package}] sorting versions")
        versions = self._tree[package]
        version_names = sorted(
            list(versions), key=functools.cmp_to_key(_compare_versions)
        )
        version_names.reverse()

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
        hashes = {_actual(h): [""] for h in pydpkg.HASHES}

        if not compress_using:
            raise DebError("no compression format(s) specified")

        self.find_debs()

        # iterate alphabetically
        for package in sorted(self._tree):
            for debinfo in self._build(package):
                debname = _debname(debinfo)
                _log.info(f"[{debname}] adding to Packages")
                msg = debinfo.message
                fileinfo = debinfo.fileinfo
                msg["Filename"] = str(
                    pathlib.Path(debinfo.filename).relative_to(self.root)
                )
                msg["Size"] = str(fileinfo.pop("filesize"))
                for name, digest in fileinfo.items():
                    _log.debug(f"[{debname}] adding {name} hash to Packages")
                    msg[_actual(name)] = digest
                paragraphs.append(str(msg))

        _log.info(
            f"[Packages] sucessfully built (total {len(self._tree)} unique packages)"
        )
        packages_text = "".join(paragraphs)
        packages_path = self.root / "Packages"

        for format in compress_using:
            compression = lazy_import(PACKAGES_COMPRESSION[format])
            packages_path = packages_path.with_suffix(format)

            _log.info(
                f"[{packages_path.name}] compressing using {compression.__name__}"
            )
            with compression.open(packages_path, mode="wt") as f:
                f.write(packages_text)

            # add hash of Packages file to Release
            for name, digest in compute_hash(packages_path).items():
                _log.debug(f"[{packages_path.name}] adding {name} hash to Release")
                hashes[name].append(
                    f"{digest} {packages_path.stat().st_size} {packages_path.name}"
                )

        for name, digests in hashes.items():
            self._release[name] = "\n".join(digests)

        _log.info("[Release] building file")
        with self.release_path.open(mode="w") as f:
            f.write(str(self._release))

        return packages_text


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="dpkg-scanpackages", description="dpkg-scanpackages, in Python."
    )

    parser.add_argument(
        "-t",
        "--type",
        help="Scan for *.type packages, instead of *.deb.",
        action="store",
        default="deb",
    )

    parser.add_argument(
        "-a",
        "--arch",
        help="Use a pattern consisting of *_all.deb and *_arch.deb instead of scanning for all debs.",
        action="store",
    )

    parser.add_argument(
        "-m",
        "--multiversion",
        help="Include all found packages in the output.",
        action="store_true",
    )

    parser.add_argument(
        "-c",
        "--compress",
        help="Formats to compress the Packages file in. Defaults to '.gz, .xz'.",
        nargs="+",
        choices=(".gz", ".bz2", ".xz"),
        action="store",
        default=[".gz", ".xz"],
    )

    parser.add_argument(
        "-V",
        "--version",
        help="Show the version and exit.",
        action="version",
        version=ccver,
    )

    parser.add_argument(
        "binary_path",
        help="The folder where the binary packages are stored, relative to the current directory",
        action="store",
    )

    args = parser.parse_args(sys.argv[1:])
    tree = DebianTree(
        ".",
        args.binary_path,
        debtype=args.type,
        arch=args.arch,
        allow_multiversion=args.multiversion,
    )

    tree.find_debs()
    print(tree.build(compress_using=args.compress))