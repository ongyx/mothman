# mothman (formerly cidercellar)

[![logo](https://raw.githubusercontent.com/ongyx/mothman/master/logo.png "mothman")](https://youtube.com/watch?v=nYq46c59n8Q "mothman")

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mothman)](https://pypi.org/project/mothman)
![PyPI - License](https://img.shields.io/pypi/l/mothman)
![PyPI](https://img.shields.io/pypi/v/mothman)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mothman)
![Lines of code](https://img.shields.io/tokei/lines/github/ongyx/mothman)

[logo here](http://pixelartmaker.com/art/c16b3ffba7b238f)

Cydia/Sileo repository creation made ez.
Inspired by [repoman](https://github.com/JeremyGrosser/repoman).

**NOTE**: This project is **still** WIP and in alpha stage.

## Rationale

[repo.me](https://github.com/syns/repo.me) and [Reposi3](https://github.com/supermamon/Reposi3) are awesome Cydia repo templates, simplifying the creation of Cydia repos.
But it becomes tedious to manually create descriptions for every single package (which is actually done twice, for both Cydia and Sileo).

This project aims to automate the process of generating descriptions for all packages in a repo,
as well as creating the `Packages` and `Release`  file (without `apt`, especially on Windows).

## Hey, what about [Silica](https://github.com/Shugabuga/Silica)?

The main advantage of mothman is that it is entirely pure-Python. Silica shells out to dpkg-deb (Debian-based systems, WSL).
So you can use mothman on *both* WSL and native Windows.

## Features

- Pure-Python dependencies, portable (no more wrangling with `libapt.so` on non-Debian platforms)
- Automate repository management, including adding Debian packages and generating depictions for them (certain fields can be customised)
- Adds `Depiction` and `SileoDepiction` keys to `Packages` file for you

## CLI Usage

1. Create a new repo from an existing template:

```bash
$ mothman init -p example && cd example
# ...some log messages here...
INFO     :: Done! Place your Debian package files in the example/debians folder,
            customise the template if needed, and execute 'mothman build <host domain>' to build.
```

This will create a `mothman.json` config file in the root of the repository folder.
The config file is really, *really* important because it tells mothman about the template it's using. Don't delete it!

2. Add your Debian packages/tweaks to the aforementioned folder (in this case `example/debians`).

Optionally, you can change the template design around a bit and customize it to your liking.

3. Build the repo:

```bash
$ mothman build my-domain.com
```

where my-domain.com is the website where you are hosting your repo. Make sure it is just the domain **without** `http(s)://` in front.

If you are going to host the repo in a subdirectory (i.e <username>.github.io isn't just for your Cydia repo), then just append the path:

```bash
$ mothman build <username>.github.io/example  # assuming that you move the 'example' Cydia repo into the Github Pages repository.
```

Push the changes to your repo or your server.
If you add/update any packages, just repeat step 3.

## API Usage

If you want to use mothman as a Python module, the reference docs are [here](API.md).

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
Copyright 2020-2021 Ong Yong Xin

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
