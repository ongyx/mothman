# coding: utf8
"""Cydia/Sileo repository stuff.
If you want a 'classical' Debian repository, see mothman.scan.DebianTree.
"""

import email
import email.message
import pathlib
import re
import textwrap
from typing import Generator

from . import scan
from . import depictions

# config for repo templates (paths to depictions, etc.)
TEMPLATES = {
    "repo.me": {
        # Depiction -> path to store depiction (info.xml)
        # Depiction_url -> url to depiction itself
        "Depiction": "depictions/web/{package}/info.xml",
        "Depiction_url": "{host}/depictions/web/?p={package}",
        # SileoDepiction -> path to store Native depiction (depiction.json)
        # SileoDepiction_url -> ditto
        "SileoDepiction": "depictions/native/{package}/depiction.json",
        "SileoDepiction_url": "{host}/depictions/native/{package}/depiction.json",
        # where the debian packages are
        "deb_path": "debians",
        # apt config (if any)
        "apt.conf": "assets/repo/repo.conf"
    },
    "Reposi3": {
        "Depiction": "depictions/{package}/info.xml",
        "Depiction_url": "depictions/?p={package}",
        # Reposi3 doesn't support Sileo depictions ._.
        "deb_path": "debs"
    }
}

DEPICTIONS = {
    "Depiction": depictions.Cydia,
    "SileoDepiction": depictions.Sileo
}

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
        f'{k} "{v}";'
        if " " in v
        else f"{k} {v};"
        for k, v in conf.items()
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
    def __init__(self, host, *args, template: str, **kwargs):
        self._template = TEMPLATES[template]
        super().__init__(*args, deb_path=self._template["deb_path"], **kwargs)
        
        self._host = host
        self._depictions = {k: v for k, v in DEPICTIONS.items() if k in self._template}
        
        # load apt.conf (if any)
        conf = self._template.get("apt.conf")
        
        if conf is not None:
            with open(self.root / conf) as f:
                self._release = _load_conf(f.read())
    
    def _build(self) -> Generator[email.message.Message, None, None]:
        for msg in super()._build():
            self._build_depiction(msg)
            yield msg
    
    def _build_depiction(self, debinfo: email.message.Message) -> None:
        for dep, dep_class in self._depictions.items():
            dep_path = self.root / self._template[dep].format(
                package=debinfo["Package"]
            )
            
            (dep_path.parent).mkdir(parents=True, exist_ok=True)
            with dep_path.open("w") as f:
                f.write(dep_class(debinfo).build())
            
            debinfo[dep] = self._template[f"{dep}_url"].format(
                host=self._host,
                package=debinfo["Package"]
            )