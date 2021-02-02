# coding: utf8
"""Utils."""

import email
import hashlib
import importlib
import logging
import os
import pathlib
import re
import sys

from typing import Any, Dict, Union

# Type hints
Path = Union[str, pathlib.Path]

_log = logging.getLogger("mothman")

# Known compression methods for Packages file mapped to stdlib modules.
# These are (problably) the most common compression methods.
PACKAGES_COMPRESSION = {"": "io", ".gz": "gzip", ".bz2": "bz2", ".xz": "lzma"}

# Convinent constants for compression.
CAT = ""
GZIP = ".gz"
BZIP2 = ".bz2"
XZ = ".xz"

FILEINFO_HASHES = ("md5", "sha1", "sha256")


def _lazy_import(module_name):
    # HACK: much nicer than a long block of elifs
    # so that we don't have to keep re-importing modules.
    _log.debug("lazy-importing %s", module_name)
    module = sys.modules.get(module_name)
    if module is None:
        # not imported yet
        module = importlib.import_module(module_name)

    return module


def _lazy_import_compression(fmt):
    return _lazy_import(PACKAGES_COMPRESSION[fmt])


def _filename(response):
    return re.findall(r"filename=(.+)", response.headers["content-disposition"])[0]


def extract_packages(dir: Path) -> Union[email.message.Message, None]:
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

        compressor = _lazy_import(module_name)

        actual_file = file.with_suffix(ext)
        if not actual_file.exists():
            continue

        _log.debug("decompressing %s", actual_file)
        with compressor.open(str(actual_file), mode="rt") as f:  # type: ignore
            # we'll just return the first one that exists
            _log.debug("parsing %s", actual_file)
            return email.message_from_file(f)

    # compression not supported
    return None


def fileinfo(path: Path, chunksize: int = 1024) -> Dict[str, Any]:
    """Get info for a file in a dictionary format:
    {
        "md5": ... # hashes
        "sha1": ...
        "sha256": ...
        "filesize": ... # size in bytes (as int)
    }

    Args:
        path: The path to the file.
        chunksize: How many bytes to update the hashes with.
            Defaults to 1024 (1kB).

    Returns:
        The file info.
    """

    hashes = [getattr(hashlib, h)() for h in FILEINFO_HASHES]

    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if not chunk:
                break

            for hash_object in hashes:
                hash_object.update(chunk)

    fileinfo = {h.name: h.hexdigest() for h in hashes}
    fileinfo["filesize"] = os.path.getsize(path)

    return fileinfo
