# coding: utf8
from typing import Generator, Tuple, Optional

from . import scan
from . import depictions

# constants representing depiction types
DEPICTIONS = {"cydia": scan.CydiaDepiction, "sileo": scan.SileoDepiction}


class Repository(scan.DebianTree):
    """A Cydia/Sileo repository.
    If you want a 'normal' Debian repository, see cidercellar.scan.DebianTree.

    Args:
        *args: Passed to DebianTree.
        depiction: What kind of depiction to generate for each package.
            Defaults to ('cydia', 'sileo').
        **kwargs: Passed to DebianTree.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _build(
        self, package: str, depiction: Optional[tuple] = None
    ) -> Generator[scan.DebianInfo, None, None]:
        for debinfo in super()._build(package):
            pass
