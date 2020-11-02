# coding: utf8
"""Generate Cydia/Sileo depictions (from deb packages) for Debian repos.
"""

import json
import re
from datetime import datetime
from xml.etree import ElementTree as etree

# regexes
RE_DEPENDS = re.compile(r"^([a-z0-9+\-\.]+)(?: *\(([<>=]{1,2}) *(.*)?\))?$")


def dict_to_xml(data: dict, rootname: str = "root") -> etree.Element:
    """Convert a dictionary to XML.
    All objects are converted to keys, and sub-dictionaries are treated as sub-elements.

    Args:
        data: The dictionary.
        rootname: The root element tag.
    """

    root = etree.Element(rootname)

    for key, value in data.items():

        if isinstance(value, dict):
            root.append(dict_to_xml(value, rootname=key))

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    root.append(dict_to_xml(item, rootname=key))

                else:
                    etree.SubElement(root, key).text = str(item)

        else:
            etree.SubElement(root, key).text = str(value)

    return root


class Generic:
    """A generic depiction.
    To create new representations, subclass this and override the .build() method,
    which should output the depiction representation as a string.

    Also, you should pass *args and **kwargs to super().__init__.

    Args:
        control: The Debian control headers as a dictionary.
        other_info: A dictionary of package info that does not appear in the control file.
            The dictionary should be in this format:
            {
                "price": "Free",  # price of package
                "header_image": "..."  # direct url to a banner
                "screenshots": [  # direct url(s) to screenshot images
                    "direct_url1",
                    "direct_url2",
                    ...
                ]
            }
            where price is the price, header_image is the direct url to a image to use as a banner, and screenshots is a list of URLs to images.
            (Price and header_image is used only by Sileo.)
            This is optional.

    Attributes:
        control: See Args.
        other_info: See Args.
    """

    def __init__(self, control: dict, other_info: dict = {}) -> None:
        self.control = control
        self.other_info = other_info

    def build(self) -> str:
        raise NotImplementedError


class Cydia(Generic):
    """A Cydia depiction.

    See GenericDepiction for args.
    """

    # map of the XML fields to Debian control file fields
    # most fields are one-to-one, some fields have multiple values
    # so they will be handled later.
    XML_ELEMENTS = {"id": "Package", "name": "Name", "version": "Version"}

    # template
    XML_DICT: dict = {
        "id": "",
        "name": "",
        "version": "",
        "compatibility": {"firmware": {}},
        "dependencies": {"package": []},
        "shortDescription": "",
        "descriptionlist": {"description": []},
        "screenshots": {"screenshot": []},
        "changelog": {"change": ["1.0.0", "Inital release."]},
        "links": {
            "link": [
                {
                    "name": "/r/jailbreak",
                    "url": "https://www.reddit.com/r/jailbreak",
                    "iconclass": "fa fa-reddit",
                }
            ]
        },
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # add control info to xml
        for k, v in self.XML_ELEMENTS.items():
            self.XML_DICT[k] = self.control[v]

    def build(self) -> str:
        """Export the depiction as an XML representation (for use in Web depiction),
        i.e in Reposi3/repo.me repo templates.

        Returns:
            The XML tree.
        """

        description = self.control["Description"].splitlines()
        self.XML_DICT["shortDescription"] = description[0]
        self.XML_DICT["descriptionlist"]["description"] = description

        dependencies = self.control["Depends"].split(", ")
        self.XML_DICT["dependencies"]["package"] = dependencies

        for dep in dependencies:

            if not dep.startswith("firmware"):
                continue

            _, operator, version = RE_DEPENDS.findall(dep)[0]

            # FIXME: No way to specify strictly less/more than for iOS version number
            if operator == "<<" or operator == "<=":
                firmware = {"maxiOS": version}

            elif operator == "=":
                firmware = {"miniOS": version, "maxiOS": version}

            elif operator == ">=" or operator == ">>":
                firmware = {"miniOS": version}

            self.XML_DICT["compatibility"]["firmware"] = firmware

        screenshots = self.other_info.get("screenshots")
        if screenshots is not None:
            for count, url in enumerate(screenshots, 1):
                self.XML_DICT["screenshots"]["screenshot"].append(
                    {"description": f"Screenshot {count}", "image": url}
                )

        return etree.tostring(
            dict_to_xml(self.XML_DICT, rootname="package"), encoding="unicode"
        )


class Sileo(Generic):
    # dictionary for sileo views
    # each view is an item in the 'views' list.
    SILEO_DICT: dict = {
        "minVersion": "0.1",
        "headerImage": "headerImage",
        "class": "DepictionTabView",
        "tintColor": "#0657bb",
        "tabs": [
            {
                "tabname": "Details",
                "views": [],
                "class": "DepictionStackView",
            }
        ],
    }

    def __init__(self, *args, **kwargs):
        self._views = []
        super().__init__(*args, **kwargs)

    def add_view(self, viewclass: str, properties: dict = {}) -> None:
        """Add a subview to the depiction root.

        Args:
            viewclass: The class name of the view.
            properties: The subview's properties.
        """

        properties["class"] = viewclass
        self.SILEO_DICT["tabs"][0]["views"].append(properties)

    def add_spacer(self) -> None:
        """Add a spacer view (to seperate depiction entries)."""

        self.add_view("DepictionSpacerView", {"spacing": 8})

    def build(self) -> str:
        """Export the depiction as an native representation (for use in Sileo depiction).

        Returns:
            The JSON as a string.
        """

        # package name
        self.add_view(
            "DepictionSubheaderView",
            {
                "title": self.control["Name"],
                "useBoldText": True,
                "useBottomMargin": False,
            },
        )

        # description (short)
        self.add_view(
            "DepictionMarkdownView",
            {
                "markdown": self.control["Description"].partition("\n")[0],
                "useSpacing": True,
            },
        )

        self.add_spacer()

        # screenshots (if any)
        screenshots = []

        if "screenshots" in self.other_info:
            for count, url in enumerate(self.other_info["screenshots"], 1):
                screenshots.append(
                    {"accessibilityText": f"Screenshot{count}", "url": url}
                )

            self.add_view(
                "DepictionScreenshotsView",
                {
                    "itemCornerRadius": 6,
                    "itemSize": "{160, 275.41333333333336}",
                    "screenshots": screenshots,
                },
            )

        # description (long)
        self.add_view(
            "DepictionMarkdownView",
            {
                "title": "markdown-description",
                "markdown": self.control["Description"],
                "useBoldText": True,
                "useBottomMargin": False,
            },
        )

        self.add_spacer()

        # version
        self.add_view(
            "DepictionTableTextView",
            {"title": "Version", "text": self.control["Version"]},
        )

        # date released
        self.add_view(
            "DepictionTableTextView",
            {"title": "Released", "text": datetime.today().strftime("%m-%d-%Y")},
        )

        # price (if any)
        self.add_view(
            "DepictionTableTextView",
            {"title": "Price", "text": self.other_info.get("price") or "Free"},
        )

        self.add_spacer()

        # author
        self.add_view(
            "DepictionTableTextView",
            {"title": "Developer", "text": self.control["Author"]},
        )

        # header image (if any)
        header = self.other_info.get("header_info")
        if header is not None:
            self.SILEO_DICT["headerImage"] = header

        return json.dumps(self.SILEO_DICT, indent=4)
