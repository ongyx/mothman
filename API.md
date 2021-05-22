# Table of Contents

* [mothman.depictions](#mothman.depictions)
  * [dict\_to\_xml](#mothman.depictions.dict_to_xml)
  * [Generic](#mothman.depictions.Generic)
  * [CydiaXML](#mothman.depictions.CydiaXML)
    * [build](#mothman.depictions.CydiaXML.build)
  * [Sileo](#mothman.depictions.Sileo)
    * [add\_view](#mothman.depictions.Sileo.add_view)
    * [add\_spacer](#mothman.depictions.Sileo.add_spacer)
    * [build](#mothman.depictions.Sileo.build)
* [mothman.pydpkg](#mothman.pydpkg)
  * [DpkgError](#mothman.pydpkg.DpkgError)
  * [DscError](#mothman.pydpkg.DscError)
  * [DpkgVersionError](#mothman.pydpkg.DpkgVersionError)
  * [DpkgMissingControlFile](#mothman.pydpkg.DpkgMissingControlFile)
  * [DpkgMissingControlGzipFile](#mothman.pydpkg.DpkgMissingControlGzipFile)
  * [DpkgMissingRequiredHeaderError](#mothman.pydpkg.DpkgMissingRequiredHeaderError)
  * [DscMissingFileError](#mothman.pydpkg.DscMissingFileError)
  * [DscBadChecksumsError](#mothman.pydpkg.DscBadChecksumsError)
  * [DscBadSignatureError](#mothman.pydpkg.DscBadSignatureError)
  * [Dpkg](#mothman.pydpkg.Dpkg)
    * [\_\_init\_\_](#mothman.pydpkg.Dpkg.__init__)
    * [\_\_getattr\_\_](#mothman.pydpkg.Dpkg.__getattr__)
    * [\_\_getitem\_\_](#mothman.pydpkg.Dpkg.__getitem__)
    * [message](#mothman.pydpkg.Dpkg.message)
    * [control\_str](#mothman.pydpkg.Dpkg.control_str)
    * [headers](#mothman.pydpkg.Dpkg.headers)
    * [fileinfo](#mothman.pydpkg.Dpkg.fileinfo)
    * [md5](#mothman.pydpkg.Dpkg.md5)
    * [sha1](#mothman.pydpkg.Dpkg.sha1)
    * [sha256](#mothman.pydpkg.Dpkg.sha256)
    * [filesize](#mothman.pydpkg.Dpkg.filesize)
    * [epoch](#mothman.pydpkg.Dpkg.epoch)
    * [upstream\_version](#mothman.pydpkg.Dpkg.upstream_version)
    * [debian\_revision](#mothman.pydpkg.Dpkg.debian_revision)
    * [debian\_name](#mothman.pydpkg.Dpkg.debian_name)
    * [get](#mothman.pydpkg.Dpkg.get)
    * [get\_header](#mothman.pydpkg.Dpkg.get_header)
    * [compare\_version\_with](#mothman.pydpkg.Dpkg.compare_version_with)
    * [get\_epoch](#mothman.pydpkg.Dpkg.get_epoch)
    * [get\_upstream](#mothman.pydpkg.Dpkg.get_upstream)
    * [split\_full\_version](#mothman.pydpkg.Dpkg.split_full_version)
    * [get\_alphas](#mothman.pydpkg.Dpkg.get_alphas)
    * [get\_digits](#mothman.pydpkg.Dpkg.get_digits)
    * [listify](#mothman.pydpkg.Dpkg.listify)
    * [dstringcmp](#mothman.pydpkg.Dpkg.dstringcmp)
    * [compare\_revision\_strings](#mothman.pydpkg.Dpkg.compare_revision_strings)
    * [compare\_versions](#mothman.pydpkg.Dpkg.compare_versions)
    * [compare\_versions\_key](#mothman.pydpkg.Dpkg.compare_versions_key)
    * [dstringcmp\_key](#mothman.pydpkg.Dpkg.dstringcmp_key)
  * [Dsc](#mothman.pydpkg.Dsc)
    * [\_\_getattr\_\_](#mothman.pydpkg.Dsc.__getattr__)
    * [\_\_getitem\_\_](#mothman.pydpkg.Dsc.__getitem__)
    * [get](#mothman.pydpkg.Dsc.get)
    * [message](#mothman.pydpkg.Dsc.message)
    * [headers](#mothman.pydpkg.Dsc.headers)
    * [pgp\_message](#mothman.pydpkg.Dsc.pgp_message)
    * [source\_files](#mothman.pydpkg.Dsc.source_files)
    * [all\_files\_present](#mothman.pydpkg.Dsc.all_files_present)
    * [all\_checksums\_correct](#mothman.pydpkg.Dsc.all_checksums_correct)
    * [corrected\_checksums](#mothman.pydpkg.Dsc.corrected_checksums)
    * [missing\_files](#mothman.pydpkg.Dsc.missing_files)
    * [sizes](#mothman.pydpkg.Dsc.sizes)
    * [message\_str](#mothman.pydpkg.Dsc.message_str)
    * [checksums](#mothman.pydpkg.Dsc.checksums)
    * [validate](#mothman.pydpkg.Dsc.validate)
* [mothman.repo](#mothman.repo)
  * [Repository](#mothman.repo.Repository)
* [mothman.tree](#mothman.tree)
  * [DebianTree](#mothman.tree.DebianTree)
    * [add\_deb](#mothman.tree.DebianTree.add_deb)
    * [add\_debs](#mothman.tree.DebianTree.add_debs)
    * [build](#mothman.tree.DebianTree.build)
* [mothman.utils](#mothman.utils)
  * [extract\_packages](#mothman.utils.extract_packages)
  * [fileinfo](#mothman.utils.fileinfo)

<a name="mothman.depictions"></a>
# mothman.depictions

Generate Cydia/Sileo depictions (from deb packages) for Debian repos.

<a name="mothman.depictions.dict_to_xml"></a>
#### dict\_to\_xml

```python
dict_to_xml(data: dict, rootname: str = "root") -> etree.Element
```

Convert a dictionary to XML.
All objects are converted to keys, and sub-dictionaries are treated as sub-elements.

**Arguments**:

- `data` - The dictionary.
- `rootname` - The root element tag.

<a name="mothman.depictions.Generic"></a>
## Generic Objects

```python
class Generic()
```

A generic depiction.
To create new representations, subclass this and override the .build() method,
which should output the depiction representation as a string.

Also, you should pass *args and **kwargs to super().__init__.

**Arguments**:

- `control` - The Debian control headers as a dictionary.
- `other_info` - A dictionary of package info that does not appear in the
  control file. The dictionary should be in this format:
  {
- `"price"` - "Free",  # price of package
- `"header_image"` - "..."  # direct url to a banner
- `"screenshots"` - [  # direct url(s) to screenshot images
  "direct_url1",
  "direct_url2",
  ...
  ]
  }
  where price is the price, header_image is the direct url to a image
  to use as a banner, and screenshots is a list of URLs to images.
  (Price and header_image is used only by Sileo.)
  This is optional.
  

**Attributes**:

- `control` - See Args.
- `other_info` - See Args.

<a name="mothman.depictions.CydiaXML"></a>
## CydiaXML Objects

```python
class CydiaXML(Generic)
```

A Cydia depiction as XML (used in Reposi3 and repo.me).

See GenericDepiction for args.

<a name="mothman.depictions.CydiaXML.build"></a>
#### build

```python
 | build() -> str
```

Export the depiction as an XML representation (for use in Web depiction),
i.e in Reposi3/repo.me repo templates.

**Returns**:

  The XML tree.

<a name="mothman.depictions.Sileo"></a>
## Sileo Objects

```python
class Sileo(Generic)
```

<a name="mothman.depictions.Sileo.add_view"></a>
#### add\_view

```python
 | add_view(viewclass: str, properties: dict = {})
```

Add a subview to the depiction root.

**Arguments**:

- `viewclass` - The class name of the view.
- `properties` - The subview's properties.

<a name="mothman.depictions.Sileo.add_spacer"></a>
#### add\_spacer

```python
 | add_spacer()
```

Add a spacer view (to seperate depiction entries).

<a name="mothman.depictions.Sileo.build"></a>
#### build

```python
 | build() -> str
```

Export the depiction as an native representation (for use in Sileo depiction).

**Returns**:

  The JSON as a string.

<a name="mothman.pydpkg"></a>
# mothman.pydpkg

pydpkg: tools for inspecting dpkg archive files in python
            without any dependency on libapt

Modifications:
- commented out logging.basicConfig call
- made pgpy import optional
- (mypy) ignore imports for untyped modules imported
- abstracted filesize property to util function

<a name="mothman.pydpkg.DpkgError"></a>
## DpkgError Objects

```python
class DpkgError(Exception)
```

Base error class for Dpkg errors

<a name="mothman.pydpkg.DscError"></a>
## DscError Objects

```python
class DscError(Exception)
```

Base error class for Dsc errors

<a name="mothman.pydpkg.DpkgVersionError"></a>
## DpkgVersionError Objects

```python
class DpkgVersionError(DpkgError)
```

Corrupt or unparseable version string

<a name="mothman.pydpkg.DpkgMissingControlFile"></a>
## DpkgMissingControlFile Objects

```python
class DpkgMissingControlFile(DpkgError)
```

No control file found in control.tar.gz/xz

<a name="mothman.pydpkg.DpkgMissingControlGzipFile"></a>
## DpkgMissingControlGzipFile Objects

```python
class DpkgMissingControlGzipFile(DpkgError)
```

No control.tar.gz/xz file found in dpkg file

<a name="mothman.pydpkg.DpkgMissingRequiredHeaderError"></a>
## DpkgMissingRequiredHeaderError Objects

```python
class DpkgMissingRequiredHeaderError(DpkgError)
```

Corrupt package missing a required header

<a name="mothman.pydpkg.DscMissingFileError"></a>
## DscMissingFileError Objects

```python
class DscMissingFileError(DscError)
```

We were not able to find some of the files listed in the dsc

<a name="mothman.pydpkg.DscBadChecksumsError"></a>
## DscBadChecksumsError Objects

```python
class DscBadChecksumsError(DscError)
```

Some of the files in the dsc have incorrect checksums

<a name="mothman.pydpkg.DscBadSignatureError"></a>
## DscBadSignatureError Objects

```python
class DscBadSignatureError(DscError)
```

A dsc file has an invalid openpgp signature(s)

<a name="mothman.pydpkg.Dpkg"></a>
## Dpkg Objects

```python
class Dpkg()
```

Class allowing import and manipulation of a debian package file.

<a name="mothman.pydpkg.Dpkg.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(filename=None, ignore_missing=False, logger=None)
```

Constructor for Dpkg object

**Arguments**:

- `filename`: string
- `ignore_missing`: bool
- `logger`: logging.Logger

<a name="mothman.pydpkg.Dpkg.__getattr__"></a>
#### \_\_getattr\_\_

```python
 | __getattr__(attr)
```

Overload getattr to treat control message headers as object
attributes (so long as they do not conflict with an existing
attribute).

**Arguments**:

- `attr`: string

**Returns**:

string
:raises: AttributeError

<a name="mothman.pydpkg.Dpkg.__getitem__"></a>
#### \_\_getitem\_\_

```python
 | __getitem__(item)
```

Overload getitem to treat the control message plus our local
properties as items.

**Arguments**:

- `item`: string

**Returns**:

string
:raises: KeyError

<a name="mothman.pydpkg.Dpkg.message"></a>
#### message

```python
 | @property
 | message()
```

Return an email.Message object containing the package control
structure.

**Returns**:

email.Message

<a name="mothman.pydpkg.Dpkg.control_str"></a>
#### control\_str

```python
 | @property
 | control_str()
```

Return the control message as a string

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.headers"></a>
#### headers

```python
 | @property
 | headers()
```

Return the control message headers as a dict

**Returns**:

dict

<a name="mothman.pydpkg.Dpkg.fileinfo"></a>
#### fileinfo

```python
 | @property
 | fileinfo()
```

Return a dictionary containing md5/sha1/sha256 checksums
and the size in bytes of our target file.

**Returns**:

dict

<a name="mothman.pydpkg.Dpkg.md5"></a>
#### md5

```python
 | @property
 | md5()
```

Return the md5 hash of our target file

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.sha1"></a>
#### sha1

```python
 | @property
 | sha1()
```

Return the sha1 hash of our target file

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.sha256"></a>
#### sha256

```python
 | @property
 | sha256()
```

Return the sha256 hash of our target file

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.filesize"></a>
#### filesize

```python
 | @property
 | filesize()
```

Return the size of our target file

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.epoch"></a>
#### epoch

```python
 | @property
 | epoch()
```

Return the epoch portion of the package version string

**Returns**:

int

<a name="mothman.pydpkg.Dpkg.upstream_version"></a>
#### upstream\_version

```python
 | @property
 | upstream_version()
```

Return the upstream portion of the package version string

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.debian_revision"></a>
#### debian\_revision

```python
 | @property
 | debian_revision()
```

Return the debian revision portion of the package version string

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.debian_name"></a>
#### debian\_name

```python
 | @property
 | debian_name()
```

Return the debian name used for a package's filename.

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.get"></a>
#### get

```python
 | get(item, default=None)
```

Return an object property, a message header, None or the caller-
provided default.

**Arguments**:

- `item`: string
- `default`: 

**Returns**:

string

<a name="mothman.pydpkg.Dpkg.get_header"></a>
#### get\_header

```python
 | get_header(header)
```

Return an individual control message header

**Returns**:

string or None

<a name="mothman.pydpkg.Dpkg.compare_version_with"></a>
#### compare\_version\_with

```python
 | compare_version_with(version_str)
```

Compare my version to an arbitrary version

<a name="mothman.pydpkg.Dpkg.get_epoch"></a>
#### get\_epoch

```python
 | @staticmethod
 | get_epoch(version_str)
```

Parse the epoch out of a package version string.
Return (epoch, version); epoch is zero if not found.

<a name="mothman.pydpkg.Dpkg.get_upstream"></a>
#### get\_upstream

```python
 | @staticmethod
 | get_upstream(version_str)
```

Given a version string that could potentially contain both an upstream
revision and a debian revision, return a tuple of both.  If there is no
debian revision, return 0 as the second tuple element.

<a name="mothman.pydpkg.Dpkg.split_full_version"></a>
#### split\_full\_version

```python
 | @staticmethod
 | split_full_version(version_str)
```

Split a full version string into epoch, upstream version and
debian revision.
:param: version_str

**Returns**:

tuple

<a name="mothman.pydpkg.Dpkg.get_alphas"></a>
#### get\_alphas

```python
 | @staticmethod
 | get_alphas(revision_str)
```

Return a tuple of the first non-digit characters of a revision (which
may be empty) and the remaining characters.

<a name="mothman.pydpkg.Dpkg.get_digits"></a>
#### get\_digits

```python
 | @staticmethod
 | get_digits(revision_str)
```

Return a tuple of the first integer characters of a revision (which
may be empty) and the remains.

<a name="mothman.pydpkg.Dpkg.listify"></a>
#### listify

```python
 | @staticmethod
 | listify(revision_str)
```

Split a revision string into a list of alternating between strings and
numbers, padded on either end to always be "str, int, str, int..." and
always be of even length.  This allows us to trivially implement the
comparison algorithm described at section 5.6.12 in:
https://www.debian.org/doc/debian-policy/ch-controlfields.html#version

<a name="mothman.pydpkg.Dpkg.dstringcmp"></a>
#### dstringcmp

```python
 | @staticmethod
 | dstringcmp(a, b)
```

debian package version string section lexical sort algorithm

"The lexical comparison is a comparison of ASCII values modified so
that all the letters sort earlier than all the non-letters and so that
a tilde sorts before anything, even the end of a part."

<a name="mothman.pydpkg.Dpkg.compare_revision_strings"></a>
#### compare\_revision\_strings

```python
 | @staticmethod
 | compare_revision_strings(rev1, rev2)
```

Compare two debian revision strings as described at
https://www.debian.org/doc/debian-policy/ch-controlfields.html#version

<a name="mothman.pydpkg.Dpkg.compare_versions"></a>
#### compare\_versions

```python
 | @staticmethod
 | compare_versions(ver1, ver2)
```

Function to compare two Debian package version strings,
suitable for passing to list.sort() and friends.

<a name="mothman.pydpkg.Dpkg.compare_versions_key"></a>
#### compare\_versions\_key

```python
 | @staticmethod
 | compare_versions_key(x)
```

Uses functools.cmp_to_key to convert the compare_versions()
function to a function suitable to passing to sorted() and friends
as a key.

<a name="mothman.pydpkg.Dpkg.dstringcmp_key"></a>
#### dstringcmp\_key

```python
 | @staticmethod
 | dstringcmp_key(x)
```

Uses functools.cmp_to_key to convert the dstringcmp()
function to a function suitable to passing to sorted() and friends
as a key.

<a name="mothman.pydpkg.Dsc"></a>
## Dsc Objects

```python
class Dsc()
```

Class allowing import and manipulation of a debian source
description (dsc) file.

<a name="mothman.pydpkg.Dsc.__getattr__"></a>
#### \_\_getattr\_\_

```python
 | __getattr__(attr)
```

Overload getattr to treat message headers as object
attributes (so long as they do not conflict with an existing
attribute).

**Arguments**:

- `attr`: string

**Returns**:

string
:raises: AttributeError

<a name="mothman.pydpkg.Dsc.__getitem__"></a>
#### \_\_getitem\_\_

```python
 | __getitem__(item)
```

Overload getitem to treat the message plus our local
properties as items.

**Arguments**:

- `item`: string

**Returns**:

string
:raises: KeyError

<a name="mothman.pydpkg.Dsc.get"></a>
#### get

```python
 | get(item, ret=None)
```

Public wrapper for getitem

<a name="mothman.pydpkg.Dsc.message"></a>
#### message

```python
 | @property
 | message()
```

Return an email.Message object containing the parsed dsc file

<a name="mothman.pydpkg.Dsc.headers"></a>
#### headers

```python
 | @property
 | headers()
```

Return a dictionary of the message items

<a name="mothman.pydpkg.Dsc.pgp_message"></a>
#### pgp\_message

```python
 | @property
 | pgp_message()
```

Return a pgpy.PGPMessage object containing the signed dsc
message (or None if the message is unsigned)

<a name="mothman.pydpkg.Dsc.source_files"></a>
#### source\_files

```python
 | @property
 | source_files()
```

Return a list of source files found in the dsc file

<a name="mothman.pydpkg.Dsc.all_files_present"></a>
#### all\_files\_present

```python
 | @property
 | all_files_present()
```

Return true if all files listed in the dsc have been found

<a name="mothman.pydpkg.Dsc.all_checksums_correct"></a>
#### all\_checksums\_correct

```python
 | @property
 | all_checksums_correct()
```

Return true if all checksums are correct

<a name="mothman.pydpkg.Dsc.corrected_checksums"></a>
#### corrected\_checksums

```python
 | @property
 | corrected_checksums()
```

Returns a dict of the CORRECT checksums in any case
where the ones provided by the dsc file are incorrect.

<a name="mothman.pydpkg.Dsc.missing_files"></a>
#### missing\_files

```python
 | @property
 | missing_files()
```

Return a list of all files from the dsc that we failed to find

<a name="mothman.pydpkg.Dsc.sizes"></a>
#### sizes

```python
 | @property
 | sizes()
```

Return a list of source files found in the dsc file

<a name="mothman.pydpkg.Dsc.message_str"></a>
#### message\_str

```python
 | @property
 | message_str()
```

Return the dsc message as a string

**Returns**:

string

<a name="mothman.pydpkg.Dsc.checksums"></a>
#### checksums

```python
 | @property
 | checksums()
```

Return a dictionary of checksums for the source files found
in the dsc file, keyed first by hash type and then by filename.

<a name="mothman.pydpkg.Dsc.validate"></a>
#### validate

```python
 | validate()
```

Raise exceptions if files are missing or checksums are bad.

<a name="mothman.repo"></a>
# mothman.repo

Cydia/Sileo repository stuff.
If you want a 'classical' Debian repository, see mothman.tree.DebianTree.

<a name="mothman.repo.Repository"></a>
## Repository Objects

```python
class Repository(tree.DebianTree)
```

A Cydia/Sileo repository.

**Arguments**:

- `host` - The website host URL, i.e 'username.github.io/repo'.
- `*args` - Passed to super().__init__.
- `template` - The repo template as a dict (see TEMPLATES for an example).
  If None, template will be loaded from mothman.json
  (in the repo root).
- `**kwargs` - Passed to super().__init__

<a name="mothman.tree"></a>
# mothman.tree

Utilities to scan for Debian packages in a folder.
Forked from 'https://github.com/supermamon/dpkg-scanpackages.py'.

<a name="mothman.tree.DebianTree"></a>
## DebianTree Objects

```python
class DebianTree()
```

A tree representing a Debian repo as a Packages file.

**Arguments**:

- `root` - The path to the repository.
- `debtype` - The type of the packages to scan for. Defaults to 'deb'.
- `arch` - The architecture of the packages to scan for. If None, all
  package architectures will be allowed. Defaults to None.
- `allow_multiversion` - Whether or not to allow multiple versions of
  the same package to be scanned for. Defaults to True.
  

**Attributes**:

- `root` _pathlib.Path_ - See Args.
- `root_str` _str_ - .path, as a string.

<a name="mothman.tree.DebianTree.add_deb"></a>
#### add\_deb

```python
 | add_deb(file: pathlib.Path)
```

Add a Debian package file to the tree.

**Arguments**:

- `file` - The path to the package file.

<a name="mothman.tree.DebianTree.add_debs"></a>
#### add\_debs

```python
 | add_debs(folder: Optional[pathlib.Path] = None)
```

Find any Debian package files and add them to the tree.

**Arguments**:

- `folder` - The path to search for packages.
  No recursive searching is done.

<a name="mothman.tree.DebianTree.build"></a>
#### build

```python
 | build(compress_using: list = [CAT, GZIP]) -> str
```

Build the Packages/Release file for this repo.

**Arguments**:

- `compress_using` - Formats to compress the Packages file in.
  Format must be one of the module-level constants CAT, GZIP,
  BZIP2, or XZ.
  Defaults to [CAT, GZIP] (plaintext and .gz compression).
  

**Returns**:

  The Packages file content as a string.
  

**Raises**:

  DebError, if there are no packages added to this repo.

<a name="mothman.utils"></a>
# mothman.utils

Utils.

<a name="mothman.utils.extract_packages"></a>
#### extract\_packages

```python
extract_packages(dir: Path) -> Union[email.message.Message, None]
```

Get the Packages file from a directory.
This searches for the Packages file with different extensions in the directory
(Packages.bz2, Packages.gz, et al.), extracts and returns the first one it finds.
If not, it will fallback to just getting the normal Packages file
(no compression).

**Arguments**:

- `dir` - The path to the folder containing the Packages file.
  

**Raises**:

  FileNotFoundError, if the Packages file could not be gotten.
  

**Returns**:

  The Packages file as a Message object.

<a name="mothman.utils.fileinfo"></a>
#### fileinfo

```python
fileinfo(path: Path, chunksize: int = 1024) -> Dict[str, Any]
```

Get info for a file in a dictionary format:
{
"md5": ... # hashes
"sha1": ...
"sha256": ...
"filesize": ... # size in bytes (as int)
}

**Arguments**:

- `path` - The path to the file.
- `chunksize` - How many bytes to update the hashes with.
  Defaults to 1024 (1kB).
  

**Returns**:

  The file info.

