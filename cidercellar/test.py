# coding: utf8

from cidercellar import scan

repo = scan.DebianRepo(".", "debs")
repo.build()