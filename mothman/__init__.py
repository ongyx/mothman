# coding: utf8
"""Cydia/Sileo repo configurator/generator"""

import logging

import coloredlogs

from .__version__ import __version__  # noqa: F401

coloredlogs.install(
    fmt=" %(name)s :: %(levelname)-8s :: %(message)s",
    logger=logging.getLogger("mothman"),
)
