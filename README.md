# cidercellar

![logo](https://raw.githubusercontent.com/ongyx/cidercellar/master/logo.png "cidercellar")

Cydia/Sileo repository creation made ez.

**NOTE**: This project is **still** WIP and in alpha stage.

## Why?
[repo.me](https://github.com/syns/repo.me), a modern Cydia repository template is awesome, and it really simplifies getting a repo up and running.
But it becomes tedious to manually create descriptions for every single package(which is actually done twice, for both Cydia and Sileo).
Therefore, this project aims to automate the process of generating descriptions for all packages in a repo, as well as creating the `Packages` and `Release`  file (without `apt`, especially on Windows).

## Features
- Pure-Python dependencies, portable (no more wrangling with `libapt.so` on non-Debian platforms)
- Automate repository management, including adding Debian packages and generating depictions for them (certain fields can be customised)
- Adds `Depiction` and `SileoDepiction` keys to `Packages` file for you

## Usage (WIP)
```
$ mkdir example && cd example
$ cidercellar init
# add your packages to the 'debians' folder
$ cidercellar pour
$ cidercellar serve  # if you want to preview the repo
```

## Depends
- `python` - At least version 3.6.
- `python-dpkg` - Debian package interface (already vendorised)
- `arpy` - Access `ar` archives

## Install

```
python(3) -m pip install cidercellar
```

## Build
All my python projects now use [flit](https://pypi.org/project/flit) to build and publish.
To build, do `flit build`.

## License

Apache License v2.
