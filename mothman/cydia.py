# coding: utf8
"""Cydia/Sileo repository stuff.
If you want a 'classical' Debian repository, see mothman.scan.DebianTree.
"""

import email
import email.message
import logging
import re
import textwrap
from typing import Generator

from . import depictions, scan

__all__ = ["Repository"]

_log = logging.getLogger("mothman")

# config for repo templates (paths to depictions, etc.)
TEMPLATES = {
    "repo.me": {
        "github": "syns/repo.me",
        "Depiction": {
            "path": "depictions/web/{package}/info.xml",
            "url": "{host}/depictions/web/?p={package}",
        },
        "SileoDepiction": {
            "path": "depictions/native/{package}/depiction.json",
            "url": "{host}/depictions/native/{package}/depiction.json",
        },
        # where the debian packages are
        "deb_path": "debians",
        # apt config (if any)
        "apt.conf": "assets/repo/repo.conf",
        # files/folders that should not be here
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
            "path": "depictions/{package}/info.xml",
            "url": "{host}/depictions/?p={package}",
        },
        # Reposi3 doesn't support Sileo depictions ._.
        "deb_path": "debs",
        "exclude": [
            "debs/com.supermamon.*",
            "depictions/com.supermamon.*",
            "Packages*",
        ],
    },
}

DEPICTIONS = {"Depiction": depictions.Cydia, "SileoDepiction": depictions.Sileo}

# for parsing repo.conf (in the syns/repo.me repo template).
RE_DECL = re.compile(r"^\s*([a-zA-Z]+) (\".+\"|.+);$", re.MULTILINE)


def _load_conf(conf: str) -> email.message.Message:
    msg = email.message.Message()

    for k, v in RE_DECL.findall(conf):
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        msg[k] = v

    return msg


def _dump_conf(conf: email.message.Message) -> str:
    return (
        textwrap.dedent(
            """APT {
        FTPArchive {
        Release {
        %s
        };
        };
        };
        """
        )
        % "\n".join(f'{k} "{v}";' if " " in v else f"{k} {v};" for k, v in conf.items())
    )


class Repository(scan.DebianTree):
    """A Cydia/Sileo repository.

    Args:
        host: The website host URL, i.e 'username.github.io/repo'.
        *args: Passed to super().__init__.
        template: Which template to use.
            Must be 'repo.me' or 'Reposi3'.
        **kwargs: Passed to super().__init__.
    """

    def __init__(self, host: str, *args, template: str = "repo.me", **kwargs):
        self._template: dict = TEMPLATES[template]
        kwargs["deb_path"] = self._template["deb_path"]
        super().__init__(*args, **kwargs)

        self._host = host
        self._depictions = {k: v for k, v in DEPICTIONS.items() if k in self._template}

        # load apt.conf (if any)
        conf = self._template.get("apt.conf")

        if conf is not None:
            with open(self.root / conf) as f:  # type: ignore
                self._release = _load_conf(f.read())

    def _build(self, package: str) -> Generator[email.message.Message, None, None]:
        for version in super()._build(package):
            self._build_depiction(version)
            yield version

    def _build_depiction(self, debinfo: email.message.Message) -> None:
        for dep, dep_class in self._depictions.items():
            _log.debug("[%s] making %s depiction", debinfo["Package"], dep)
            dep_path = self.root / self._template[dep]["path"].format(
                package=debinfo["Package"]
            )

            # make parent directories, if ti does not exist yet
            (dep_path.parent).mkdir(parents=True, exist_ok=True)

            # write actual depiction
            with dep_path.open("w") as f:
                f.write(dep_class(debinfo).build())

            # add depiction field to debinfo
            debinfo[dep] = self._template[dep]["url"].format(
                host=self._host, package=debinfo["Package"]
            )
