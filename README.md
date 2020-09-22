# cidercellar

![logo](logo.png "cidercellar")

Make Cydia/Sileo repos the ez way.
**NOTE**: This project is still WIP and in _alpha_ stage, so don't `git blame` me if anything goes wrong!

## Features
- No need to install `libapt`, especially on non-Debian systems
- Pure-Python dependencies, portable
- Automate repository management, including adding Debian packages and generating depictions for them (fields can be customised)
- Adds `Depiction` and `SileoDepiction` keys to `Packages` file for you

## Depends
- `python` - At least version 3.6.
- `pydpkg` - Debian package interface for Python

## Install

```
python(3) -m pip install cidercellar
```

## License
Apache 2.0: [license text here](license.txt)
