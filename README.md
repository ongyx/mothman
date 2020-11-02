# mothman (formerly cidercellar)

[![logo](https://raw.githubusercontent.com/ongyx/mothman/master/logo.png "mothman")](https://youtube.com/watch?v=nYq46c59n8Q "mothman")

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mothman)](https://pypi.org/project/mothman)
![PyPI - License](https://img.shields.io/pypi/l/mothman)
![PyPI](https://img.shields.io/pypi/v/mothman)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mothman)
![Lines of code](https://img.shields.io/tokei/lines/github/ongyx/mothman)

Cydia/Sileo repository creation made ez.
Inspired by [repoman](https://github.com/JeremyGrosser/repoman).

**NOTE**: This project is **still** WIP and in alpha stage.

## Rationale

[repo.me](https://github.com/syns/repo.me) and [Reposi3](https://github.com/supermamon/Reposi3) are awesome Cydia repo templates, simplifying the creation of Cydia repos.
But it becomes tedious to manually create descriptions for every single package (which is actually done twice, for both Cydia and Sileo).
This project aims to automate the process of generating descriptions for all packages in a repo, as well as creating the `Packages` and `Release`  file (without `apt`, especially on Windows).

## Features

- Pure-Python dependencies, portable (no more wrangling with `libapt.so` on non-Debian platforms)
- Automate repository management, including adding Debian packages and generating depictions for them (certain fields can be customised)
- Adds `Depiction` and `SileoDepiction` keys to `Packages` file for you

## Usage (WIP)

```bash
$ mothman init example
$ cd example
# add your packages to debs folder
$ mothman build
```

## Depends

- `python` - At least version 3.6.
- `python-dpkg` - Debian package interface (already vendorised)
- `arpy` - Access `ar` archives

## Install

```bash
python(3) -m pip install mothman
```

## Build

All my python projects now use [flit](https://pypi.org/project/flit) to build and publish.
To build, do `flit build`.

## License

Apache License v2.

```text
Copyright 2020 Ong Yong Xin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
