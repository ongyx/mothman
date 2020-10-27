# coding: utf8
"""Cydia/Sileo repository stuff.
If you want a 'classical' Debian repository, see cidercellar.scan.DebianTree.
"""

import email
import email.message
import re
import textwrap
from typing import Generator

from . import scan
from . import depictions

# config for repo templates (paths to depictions, etc.)
TEMPLATES = {
    "repo.me": {
        "cydia": "depictions/web/{package}",
        "sileo": "depictions/native/{package}",
        "deb_path": "debians",
        "apt.conf": "assets/repo/repo.conf"
    }
    "Reposi3": {
        "cydia": "depictions/{package}",
        # Reposi3 doesn't support Sileo depictions ._.
        "deb_path": "debs"
    }
}

# for parsing repo.conf (in the syns/repo.me repo template).
RE_DECL = re.compile(r"^\s*([a-zA-Z]+) (\".+\"|.+);$", re.MULTILINE)


def _load_conf(conf: str) -> email.message.Message:
    msg = email.message.Message()
    
    for k, v in RE_DECL.findall(conf):
        if v.endswith("\"") and v.endswith("\""):
            v = [1:-1]
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
        f"{k} \"{v}\";"
        if " " in v
        else f"{k} {v};"
        for k, v in conf.items()
    )


class Repository(scan.DebianTree):
    """A Cydia/Sileo repository.
    
    Args:
        *args: Passed to super().__init__.
        template: Which template to use.
            Must be 'repo.me' or 'Reposi3'.
        **kwargs: Passed to super().__init__.
    """
    def __init__(self, *args, template: str, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._template = TEMPLATES[template]
        self._CYDIA = "cydia" in self._template
        self._SILEO = "sileo" in self._template
        
        # load apt.conf (if any)
        conf = self._template.get("apt.conf")
        
        if conf is not None:
            with open(self.root / conf) as f:
                self._release = _load_conf(f.read())
    
    def _build(self) -> Generator[email.message.Message, None, None]:
        for msg in super()._build():
            if self._CYDIA:
                pass
            
            if self._SILEO:
                pass
    
    def _build_depiction(fmt: str) -> depictions.GenericDepiction:
        pass