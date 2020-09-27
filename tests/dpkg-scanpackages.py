# coding: utf8

# dpkg-scanpackages, using Python

from cidercellar import scan

repo = scan.DebianRepo(".", "debs")
repo.find_debs()

with open("Packages", mode="w") as f:
    f.write(repo.build())