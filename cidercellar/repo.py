# coding: utf8
"""Cydia/Sileo repository stuff.
If you want a 'classical' Debian repository, see cidercellar.scan.DebianTree.
"""

import re
import textwrap

from . import scan

# for parsing repo.conf (in the syns/repo.me repo template).
RE_DECL = re.compile(r"^\s*([a-zA-Z]+) (\".+\"|.+);$", re.MULTILINE)


def _load_conf(conf: str) -> dict:
    return {k: v if not v.endswith("\"") else v[1:-1] for k, v in RE_DECL.findall(conf)}


def _dump_conf(conf: dict) -> str:
    return textwrap.dedent(
        """APT {
        FTPArchive {
        Release {
        %s
        };
        };
        };
        """
    ) % "\n".join(
        f"{k} \"{v}\";"
        if " " in v
        else f"{k} {v};"
        for k, v in conf.items()
    )


class Repository(scan.DebianTree):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)