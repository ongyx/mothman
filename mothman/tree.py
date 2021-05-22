# coding: utf8
"""Utilities to scan for Debian packages in a folder.
Forked from 'https://github.com/supermamon/dpkg-scanpackages.py'.
"""

import email
import email.message
import logging
import pathlib
from collections import defaultdict
from typing import Dict, Generator, Optional

from mothman import pydpkg, utils
from mothman.utils import BZIP2, CAT, GZIP, XZ, Path

__all__ = ["CAT", "GZIP", "BZIP2", "XZ", "DebianTree"]

_log = logging.getLogger("mothman")


class DebError(Exception):
    pass


def _sort(versions):
    return sorted(list(versions), key=pydpkg.Dpkg.compare_versions_key)


class DebianTree:
    """A tree representing a Debian repo as a Packages file.

    Args:
        root: The path to the repository.
        debtype: The type of the packages to scan for. Defaults to 'deb'.
        arch: The architecture of the packages to scan for. If None, all
            package architectures will be allowed. Defaults to None.
        allow_multiversion: Whether or not to allow multiple versions of
            the same package to be scanned for. Defaults to True.

    Attributes:
        root (pathlib.Path): See Args.
        root_str (str): .path, as a string.
    """

    def __init__(
        self,
        root: Path,
        debtype: str = "deb",
        arch: str = None,
        allow_multiversion: bool = True,
    ) :
        _log.debug("initalising repo %s", root)
        self.root = pathlib.Path(root).resolve().expanduser()
        self.release_path = self.root / "Release"

        with self.release_path.open() as f:
            _log.debug("parsing Release")
            self._release = email.message_from_file(f)

        # remove any hashes
        for hash_field in ("MD5Sum", "SHA1", "SHA256", "SHA512"):
            if hash_field in self._release:
                # erase existing hashes of Packages file, will be added back in on build
                del self._release[hash_field]

        # remove any Packages files
        for file in self.root.glob("Packages"):
            file.unlink()

        self._debtype = debtype
        self._arch = arch
        self._multiversion = allow_multiversion
        self._tree: Dict[str, Dict[str, dict]] = defaultdict(lambda: defaultdict(dict))

    @property
    def root_str(self):
        return str(self.root)

    def add_deb(self, file: pathlib.Path):
        """Add a Debian package file to the tree.

        Args:
            file: The path to the package file.
        """

        debinfo = pydpkg.Dpkg(file)

        # arch check (i use arch btw).
        if self._arch is not None:
            if debinfo["Architecture"] != self._arch:
                return

        _log.debug("[%s] adding deb", debinfo.Package)
        name, version, arch = [debinfo[f] for f in pydpkg.REQUIRED_HEADERS]

        self._tree[name][version][arch] = debinfo

    def add_debs(self, folder: Optional[pathlib.Path] = None) :
        """Find any Debian package files and add them to the tree.

        Args:
            folder: The path to search for packages.
                No recursive searching is done.
        """
        _log.info("[%s] finding debs", folder)

        for debfile in folder.glob(f"*.{self._debtype}"):
            self.add_deb(debfile)

    def _build(self, package: str) -> Generator[email.message.Message, None, None]:
        # need to reverse, so latest versions come first
        # simpler than changing the quicksort function itself
        _log.debug("[%s] sorting versions", package)
        versions = self._tree[package]
        version_names = _sort(versions)
        version_names.reverse()

        if not self._multiversion:
            latest_version = version_names[0].partition("/")[0]
            # because version name has the format 'actual_ver/arch',
            # there may be multiple archs for each version.
            # (Hence the .startswith().)
            version_names = [v for v in version_names if v.startswith(latest_version)]

        for v in version_names:
            for _, debinfo in versions[v].items():
                debname = debinfo.debian_name
                fileinfo = debinfo.fileinfo
                msg = debinfo.message

                _log.info("[%s] adding to Packages", debname)

                msg["Filename"] = str(
                    pathlib.Path(debinfo.filename).relative_to(self.root)
                )
                msg["Size"] = str(fileinfo.pop("filesize"))
                for name, digest in fileinfo.items():
                    _log.debug("[%s] adding %s hash to Packages", debname, name)
                    msg[name] = digest

                yield msg

    def build(self, compress_using: list = [CAT, GZIP]) -> str:
        """Build the Packages/Release file for this repo.

        Args:
            compress_using: Formats to compress the Packages file in.
                Format must be one of the module-level constants CAT, GZIP,
                BZIP2, or XZ.
                Defaults to [CAT, GZIP] (plaintext and .gz compression).

        Returns:
            The Packages file content as a string.

        Raises:
            DebError, if there are no packages added to this repo.
        """

        paragraphs = []
        hashes: Dict[str, list] = {}

        if not self._tree:
            raise DebError(
                "refusing to build without any packages; "
                "did you forget to add any packages using .add_debs()?"
            )

        # iterate alphabetically
        for package in sorted(self._tree):
            for msg in self._build(package):
                paragraphs.append(str(msg))

        _log.info(
            "[Packages] sucessfully built (total %s unique packages)",
            str(len(self._tree)),
        )
        packages_text = "".join(paragraphs)
        packages_path = self.root / "Packages"

        for fmt in compress_using:
            compression = utils._lazy_import_compression(fmt)
            packages_path = packages_path.with_suffix(fmt)

            _log.info(
                "[%s] compressing using %s", packages_path.name, compression.__name__
            )
            with compression.open(packages_path, mode="wt") as f:  # type: ignore
                f.write(packages_text)

            packages_hashes = utils.fileinfo(packages_path)
            packages_size = packages_hashes.pop("filesize")

            # add hash of Packages file to Release
            for name, digest in packages_hashes.items():

                if name not in hashes:
                    hashes[name] = []

                _log.debug("[%s] adding %s hash to Release", packages_path.name, name)
                hashes[name].append(f" {digest} {packages_size} {packages_path.name}")

        for name, digests in hashes.items():
            self._release[name] = "\n".join(digests)

        _log.info("[Release] building file")
        with self.release_path.open(mode="w") as f:
            f.write(str(self._release))

        return packages_text


if __name__ == "__main__":
    import click

    @click.command()
    @click.option(
        "-t",
        "--type",
        help="Scan for *.type packages, instead of *.deb.",
        default="deb",
    )
    @click.option(
        "-a",
        "--arch",
        help=(
            "Use a pattern consisting of *_all.deb and *_arch.deb instead of"
            " scanning for all debs."
        ),
    )
    @click.option(
        "-m",
        "--multiversion",
        help="Include all found packages in the output.",
        is_flag=True,
    )
    @click.option(
        "-c",
        "--compress",
        help=(
            "Formats to compress the Packages file in (cat = no compression)."
            " Defaults to 'cat, gz'."
        ),
        multiple=True,
        type=click.Choice(["cat", "gz", "bz2", "xz"]),
        default=["cat", "gz"],
    )
    @click.argument("binary_path")
    def main(type, arch, multiversion, compress, binary_path):
        """Scan for debian packages in binary_path, like dpkg-scanpackages."""
        tree = DebianTree(
            ".",
            binary_path,
            debtype=type,
            arch=arch,
            allow_multiversion=multiversion,
        )

        tree.find_debs()
        compressions = [f".{c}" if c != "cat" else "" for c in compress]

        tree.build(compress_using=compressions)

    main()
