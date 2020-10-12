# coding: utf8
"""Repo data.
This module contains a compressed copy of a Cydia repository structure (specifically, sys/repo.me).
Last updated 12/10/2020.
"""

import io
import base64
import pathlib
import tempfile
import shutil
import sys
import zipfile

IGNORED = [
    "depictions/web/me.syns.samplepackage",
    "depictions/native/me.syns.samplepackage",
    "debians/me.syns.sample.deb",
    "assets/repo/Screenshots/screenshot.png",
    "assets/repo/Screenshots/screenshot2.png",
    "assets/repo/Banners/RepoHeader.png",
]

DATA = """
"""