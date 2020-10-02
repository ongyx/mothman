# cidercellar

![logo](https://raw.githubusercontent.com/ongyx/cidercellar/master/logo.png "cidercellar")

Make Cydia/Sileo repos the ez way.

**NOTE**: This project is **still** WIP and in alpha_ stage, so don't `git blame` me if anything goes wrong!

## Features
- No need to install `libapt`, especially on non-Debian systems
- Pure-Python dependencies, portable
- Automate repository management, including adding Debian packages and generating depictions for them (fields can be customised)
- Adds `Depiction` and `SileoDepiction` keys to `Packages` file for you
- Eazy config with `cidercellar config`

## Usage
WIP

## Depends
- `python` - At least version 3.6.
- `python-debian` - Debian package interface for Python

## Install

```
python(3) -m pip install cidercellar
```

## Build
All my python projects now use [flit](https://pypi.org/project/flit) to build and publish.
To build, do `flit build`.

## License

GNU GPL v3.

```
Copyright (C) 2020 Ong Yong Xin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
