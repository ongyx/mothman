# coding: utf8
"""scan.py: Utilites to scan for Debian packages in a folder.
Forked by ongyx from the original dpkg-scanpackages.py to use python-debian as the backend.
"""

# Copyright (C) 2018 Raymond Velasquez, 2020 Ong Yong Xin
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import collections
import collections.abc
import glob
import hashlib
import importlib
import os
import pathlib
import sys

import debian.debfile
import debian.deb822
import debian.debian_support

# Known compression methods for Packages file mapped to module names.
# These are (problably) the most common compression methods.
PACKAGES_COMPRESS = {
    ".gz": "gzip",
    ".bz2": "bz2",
    ".xz": "lzma"
}


class DebError(Exception):
    pass


def lazy_import(module_name):
    """Import a module (if it has not been imported yet).
    
    Args:
        module_name (str): The module.
    
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


def extract_packages(dir):
    """Get the Packages file from a directory.
    This searches for the Packages file with different extensions in the directory
    (Packages.bz2, Packages.gz, et al.), extracts and returns the first one it finds.
    If not, it will fallback to just getting the normal Packages file (no compression).
    
    Args:
        dir (str/pathlib.Path): The path to the folder containing the Packages file.
    
    Raises:
        FileNotFoundError, if the Packages file could not be gotten.
    
    Returns:
        The Packages file as a debian.deb822.Packages object.
    """
    
    file = pathlib.Path(dir) / "Packages"
    
    for ext, module_name in PACKAGES_COMPRESSION.items():
        
        compressor = lazy_import(module_name)
        
        actual_file = file.with_suffix(ext)
        if not actual_file.exists():
            continue
        
        with compressor.open(str(actual_file), mode="rt") as f:
            # we'll just return the first one that exists
            return debian.deb822.Packages(f.read())
    
    # file does not have compression, return as it is
    with file.open() as f:
        return debian.deb822.Packages(f.read())


def compute_hash(file, bsize=8192):
    """Compute the MD5, SHA1 and SHA256 hashes of a file.
    
    Args:
        file (str): The path to the file.
        bsize (int): How many bytes to digest at a time. Defaults to 8192 (128 * 64).
    
    Returns:
        A namedtuple of the MD5, SHA1, SHA256 and SHA512 hashes as strings, mapped to their hashlib names.
    """
    
    hashes = {
        "MD5sum": hashlib.md5(),
        "SHA1": hashlib.sha1(),
        "SHA256": hashlib.sha256(),
        "SHA512": hashlib.sha512()
    }
    
    with open(file, mode="rb") as f:
        while True:
            buffer = f.read(bsize)
            if not buffer:
                break
            
            for _, hash in hashes.items():
                hash.update(buffer)
    
    return {k: v.hexdigest() for k, v in hashes.items()}


def _compare_version(vers):
    nvers = []
    for v in vers:
        if v.count("/") == 1:
            v = v.split("/", maxsplit=1)[0]
            nvers.append(v)
    
    return debian.debian_support.version_compare(*nvers)


def sort_versions(versions):
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


class DebianInfo(collections.abc.MutableMapping):
    """A Debian package, formatted as an entry in a Packages file.
    
    Usage:
    >>> debinfo = DebianInfo(path_to_deb)
    
    Args:
        path (str/pathlib.Path): The path to the Debian package.
    
    Attributes:
        path (pathlib.Path): See Args.
        path_str (str): .path, as a string.
        deb (debian.debfile.Deb822): The package's control file.
        hashinfo (dict): The MD5/SHA hashes of the package file.
    """
    
    field_order = [
        'Package','Version','Architecture','Maintainer',
        'Depends','Conflicts','Breaks','Replaces',
        'Filename','Size',
        'MD5sum','SHA1','SHA256','SHA512',
        'Section','Description'
    ]

    def __init__(self, path, relpath=None):
        self.path = pathlib.Path(path)
        self.deb = debian.debfile.DebFile(self.path_str)
        
        self._headers = self.deb.debcontrol()
        self._headers["Filename"] = self.path_str
        self._headers["Size"] = str(self.path.stat().st_size)
        
        self._hashinfo = None
        for hash, digest in self.hashinfo.items():
            self._headers[hash] = digest
    
    # dict methods
    def __getitem__(self, key): 
        return self._headers[key]
    
    def __setitem__(self, key, value):
        self._headers[key] = value
    
    def __delitem__(self, key):
        del self._headers[key]

    def __len__(self):
        return len(self._headers)

    def __iter__(self):
        return iter(self._headers)
    # end dict methods
    
    @property
    def path_str(self):
        return str(self.path)
    
    @property
    def hashinfo(self):
        if self._hashinfo is None:
            self._hashinfo = compute_hash(self.path)
        
        return self._hashinfo

    def __str__(self):
        return self._headers.dump()


class DebianRepo(object):
    """A Debian repository.
    
    Args:
        root (str/pathlib.Path): The path to the repository.
        deb_path (str/pathlib.Path): The relative path to the directory containing
            the Debian package files.
    
    Attributes:
        root (pathlib.Path): See Args.
        deb_path (pathlib.Path): See Args.
        root_str (str): .path, as a string.
    
    Raises:
        DebError, if deb_path is invalid.
    """
    
    def __init__(self, root, deb_path):
        self.root = pathlib.Path(root).resolve().expanduser()
        self.deb_path = self.root / deb_path
        self._tree = {}
    
    @property
    def root_str(self):
        return str(self.root)
    
    def _add_deb(self, debinfo):
        """Add a DebianInfo object to the repository.
        You should not use this directly, because the 'Filename' field will not be
            formatted correctly.
        
        Args:
            debinfo (DebianInfo): The package to add.
        """
        name, version, arch = [
            debinfo[f] for f in ("Package", "Version", "Architecture")
        ]
        
        if name not in self._tree:
            self._tree[name] = {}
        
        self._tree[name][f"{version}/{arch}"] = debinfo
    
    def find_debs(self, arch=None):
        """Find all Debian package files in .deb_path, and add them to the tree.
        
        Args:
            arch (str): The architecture of the packages to add. If None, all package
                architectures will be allowed. Defaults to None.
        """
        
        for debfile in self.deb_path.glob("*.deb"):
            debinfo = DebianInfo(debfile)
            
            # arch check (i use arch btw).
            if arch is not None:
                if debinfo["Architecture"] != arch:
                    continue
            
            # replace filename (must be relative to root).
            rel_fname = str(self.deb_path.relative_to(self.root))
            debinfo["Filename"] = rel_fname
            
            self._add_deb(debinfo)
            
    def build(self, compress_using=[], **kwargs):
        """Build the Packages file for this repo.
        
        Args:
            compress_using (list): Formats to compress the Packages file in.
                Format must be present in PACKAGES_COMPRESSION.
                Defaults to an empty list.
            **kwargs: Passed to .find_debs.
        
        Returns:
            The Packages file content as a string.
        """
        
        paragraphs = []
        
        self.find_debs(**kwargs)
        
        for package, versions in self._tree.items():
            for version in sort_versions(versions.keys()):
                debinfo = versions[version]
                paragraphs.append(str(debinfo))
        
        paragraphs.append("")
        return "\n".join(paragraphs)