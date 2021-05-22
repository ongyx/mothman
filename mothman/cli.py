# coding: utf8

import email.message
import functools
import http.server
import io
import json
import logging
import pathlib
import shutil
import socket
import socketserver
import zipfile

import click
import coloredlogs  # type: ignore
import requests

from mothman import repo
from .__version__ import __version__

click.option = functools.partial(click.option, show_default=True)  # type: ignore

VERBOSITY = (
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
)
_log = logging.getLogger("mothman")

logging.getLogger("urllib3").setLevel(logging.WARNING)

# used to prompt for creating a new Release file.
RELEASE_PROMPT = {
    "Origin": ("name of this repo", None),
    "Label": ("nickname of this repo", None),
    "Suite": ("the repo's stability", "stable"),
    "Version": ("version", "1.0.0"),
    "Codename": ("what system to target (ignore if only targeting iOS)", "tangelo"),
    "Architectures": ("what arch to target (ditto)", "iphoneos-arm"),
    "Components": ("the repo's components", "main"),
    "Description": ("gist of what your repo is for", ""),
}


def release_prompt():
    release = {}
    for field, (help_msg, default) in RELEASE_PROMPT.items():
        while True:
            value = input(f"{field} - {help_msg} [{default}]: ")
            if not value:
                if default is None:
                    click.echo("Field is required, try again.")
                    continue
                else:
                    value = default

            release[field] = value
            break
    return release


# https://stackoverflow.com/a/28950776
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


@click.group()
@click.version_option(__version__)
@click.option(
    "-v", "--verbose", "verbosity", help="be more chatty", default=4, count=True
)
def cli(verbosity):
    """Cydia/Sileo repository manager/configurator."""
    # set up logger
    coloredlogs.install(
        fmt=" %(levelname)-8s :: %(message)s",
        level=VERBOSITY[verbosity - 1],
        logger=logging.getLogger("mothman"),
    )


@cli.command()
@click.option(
    "-p",
    "--path",
    "repo_path",
    help="path to the repo",
    default=".",
)
@click.option(
    "-t",
    "--template",
    "template_name",
    help=f"name of the template to use ({', '.join(t for t in repo.TEMPLATES)})",
    default="repo.me",
)
def init(repo_path, template_name):
    """Initalise a repository at path."""
    repo_path = pathlib.Path(repo_path)

    template = repo.TEMPLATES[template_name]

    username, reponame = template["github"].split("/")

    _log.info("downloading template %s/%s", username, reponame)

    response = requests.get(
        f"https://github.com/{username}/{reponame}/archive/master.zip",
        allow_redirects=True,
    )

    repo_path.mkdir(exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:

        _log.info("extracting zip file")
        template_root = f"{reponame}-master"

        for zinfo in zf.infolist():
            _log.debug("extracting %s", zinfo.filename)
            zinfo.filename = zinfo.filename.replace(template_root, "")

            zf.extract(zinfo, str(repo_path))

    # remove unecessary files
    for pattern in template["exclude"]:
        for path in repo_path.glob(pattern):
            _log.debug("deleting excluded file %s", path)
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    existing_release = (repo_path / "Release").is_file()

    if existing_release:
        answer = click.confirm(
            "A Release file in this repo already exists. Do you want to create a new one? [y/n]: "
        )
    else:
        answer = True  # always create a new release if it does not exist

    if answer:
        release = release_prompt()
        msg = email.message.Message()
        for key, value in release.items():
            msg[key] = value

        with (repo_path / "Release").open("w") as f:
            f.write(str(msg))

    _log.info("writing config")
    with (repo_path / repo.CONFIG_NAME).open("w") as f:
        template["name"] = template_name
        json.dump(template, f, indent=4)

    _log.info(
        f"Done! Place your Debian package files in the {repo_path}/{template['deb_path']} folder,\n"
        "customise the template if needed, and execute 'mothman build <host domain>' to build."
    )


def _build(host, path):
    tree = repo.Repository(host, path)
    tree.build()


@cli.command()
@click.argument("host")
@click.option("-p", "--path", help="path to the repo", default=".")
def build(host, path):
    """Build a repository at path, using hostname."""
    _build(host, path)


@cli.command()
@click.option("-p", "--port", help="port to serve at", default=8000)
def demo(port):
    """Build a repo with the current IP address as the host."""
    current_ip = "0.0.0.0"
    _build(f"current_ip:{port}", ".")

    with socketserver.TCPServer(
        ("", port), http.server.SimpleHTTPRequestHandler
    ) as httpd:
        _log.info("serving at %s, port %s", current_ip, port)
        httpd.serve_forever()
