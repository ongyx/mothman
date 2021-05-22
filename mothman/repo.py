# coding: utf8
"""Cydia/Sileo repository stuff.
If you want a 'classical' Debian repository, see mothman.tree.DebianTree.
"""

import email
import email.message
import json
import logging
import re
from typing import Generator, Optional

from mothman import depictions, tree

__all__ = ["Repository"]

_log = logging.getLogger("mothman")

CONFIG_NAME = "mothman.json"
# config for repo templates (paths to depictions, etc.)
# all urls are relative to the root.
TEMPLATES = {
    "repo.me": {
        "github": "syns/repo.me",
        "Depiction": {
            "class": "CydiaXML",  # specifies which class is used in mothman.depictions to make depiction
            "path": "depictions/web/{package}/info.xml",
            "url": "{host}/depictions/web/?p={package}",
        },
        "SileoDepiction": {
            "class": "Sileo",  # Sileo only has one representation.
            "path": "depictions/native/{package}/depiction.json",
            "url": "{host}/depictions/native/{package}/depiction.json",
        },
        # where the debian packages are
        "deb_path": "debians",
        # apt config (if any)
        "apt.conf": "assets/repo/repo.conf",
        # files/folders that are not needed
        "exclude": [
            "Packages*",
            "debians/me.syns.sample.deb",
            "depictions/web/me.syns.samplepackage",
            "depictions/native/me.syns.samplepackage",
            # user-generated files, should be customised by repo maintainer
            "assets/repo/Banners/*",
            "assets/repo/Screenshots/*",
            "sileo-featured.json",
        ],
    },
    "Reposi3": {
        "github": "supermamon/Reposi3",
        "Depiction": {
            "class": "CydiaXML",
            "path": "depictions/{package}/info.xml",
            "url": "{host}/depictions/?p={package}",
        },
        # Reposi3 doesn't support Sileo depictions ._.
        "deb_path": "debs",
        "exclude": [
            "debs/com.supermamon.*",
            "depictions/com.supermamon.*",
            "Packages*",
            "Release",
        ],
    },
}

# for parsing repo.conf (in the syns/repo.me repo template).
RE_DECL = re.compile(r"^\s*([a-zA-Z]+) (\".+\"|.+);$", re.MULTILINE)


class Repository(tree.DebianTree):
    """A Cydia/Sileo repository.

    Args:
        host: The website host URL, i.e 'username.github.io/repo'.
        *args: Passed to super().__init__.
        template: The repo template as a dict (see TEMPLATES for an example).
            If None, template will be loaded from mothman.json
            (in the repo root).
        **kwargs: Passed to super().__init__
    """

    def __init__(self, host: str, *args, template: Optional[dict] = None, **kwargs):
        super().__init__(*args, **kwargs)
        if template is None:
            with (self.root / CONFIG_NAME).open() as f:
                self._template = json.load(f)
        else:
            self._template = template

        deb_path = self.root / self._template["deb_path"]
        self.add_debs(deb_path)

        self._host = host
        self._depictions = {
            k: self._template[k]["class"]
            for k in ("Depiction", "SileoDepiction")
            if k in self._template
        }

    def _build(self, package: str) -> Generator[email.message.Message, None, None]:
        versions = super()._build(package)
        latest = next(versions)

        # only build depiction for latest version
        self._build_depiction(latest)
        yield latest

        for version in versions:
            yield version

    def _build_depiction(self, debinfo: email.message.Message):
        for dep, _dep_class in self._depictions.items():
            _log.debug("[%s] making %s depiction", debinfo["Package"], dep)

            dep_class = getattr(depictions, _dep_class)

            dep_path = self.root / self._template[dep]["path"].format(
                package=debinfo["Package"]
            )

            # make parent directories, if it does not exist yet
            (dep_path.parent).mkdir(parents=True, exist_ok=True)

            # write actual depiction
            with dep_path.open("w") as f:
                f.write(dep_class(debinfo).build())

            # add depiction field to debinfo
            debinfo[dep] = self._template[dep]["url"].format(
                host=self._host, package=debinfo["Package"]
            )
