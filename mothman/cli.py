# coding: utf8

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
import requests

from . import cydia
from .__version__ import __version__

VERBOSITY = (
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING,
    logging.INFO,
    logging.DEBUG,
)
_log = logging.getLogger("mothman")

logging.getLogger("urllib3").setLevel(logging.WARNING)


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
    logging.basicConfig(format=" %(name)s :: %(levelname)-8s :: %(message)s")
    _log.setLevel(VERBOSITY[verbosity - 1])


@cli.command()
@click.argument("repo_path")
@click.option(
    "-t",
    "--template",
    "template_name",
    help=f"Name of the template to use ({', '.join(t for t in cydia.TEMPLATES)})",
    default="repo.me",
)
def init(repo_path, template_name):
    """Initalise a repository at path."""
    repo_path = pathlib.Path(repo_path)
    template = cydia.TEMPLATES[template_name]
    username, reponame = template["github"].split("/")
    _log.info("downloading template %s/%s", username, reponame)
    response = requests.get(
        f"https://github.com/{username}/{reponame}/archive/master.zip",
        allow_redirects=True,
    )

    if repo_path.is_dir():
        raise ValueError(f"repo folder {str(repo_path)} already exists")

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        _log.info("extracting zip file")
        folder = f"{reponame}-master"
        for file in zf.namelist():
            if file.startswith(folder):
                _log.debug("extracting %s", file)
                zf.extract(file, repo_path.parent)

        (repo_path.parent / folder).rename(repo_path)  # rename to actual name

    # remove unecessary files
    for pattern in template["exclude"]:
        for path in repo_path.glob(pattern):
            _log.debug("deleting excluded file %s", path)
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    _log.info("writing config")
    with (repo_path / cydia.CONFIG_NAME).open("w") as f:
        template["name"] = template_name
        json.dump(template, f, indent=4)


def _build(host, path):
    tree = cydia.Repository(host, path)
    tree.find_debs()
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
    current_ip = get_ip()
    _build(current_ip, ".")

    with socketserver.TCPServer(
        ("", port), http.server.SimpleHTTPRequestHandler
    ) as httpd:
        _log.info("serving at %s, port %s", current_ip, port)
        httpd.serve_forever()
