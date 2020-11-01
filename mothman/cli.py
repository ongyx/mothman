# coding: utf8

import io
import logging
import pathlib
import shutil
import sys
import zipfile

import click
import requests

from . import cydia
from .__version__ import __version__

VERBOSITY = (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)
_log = logging.getLogger("mothman")


@click.group()
@click.version_option(__version__)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    help="be more chatty",
    default=2,
    count=True
)
def cli(verbosity, version):
    """Cydia/Sileo repository manager/configurator."""
    _log.setLevel(VERBOSITY[verbosity])


@cli.command()
@click.argument("repo_path")
@click.option(
    "-t",
    "--template",
    "template_name",
    help=f"Name of the template to use ({', '.join(t for t in cydia.TEMPLATES)})",
    default="repo.me"
)
def init(repo_path, template_name):
    """Initalise a repository at path."""
    repo_path = pathlib.Path(repo_path)
    template = cydia.TEMPLATES[template_name]
    username, reponame = template["github"].split("/")
    response = requests.get(
        f"https://github.com/{username}/{reponame}/archive/master.zip",
        allow_redirects=True
    )
    
    repo_path.mkdir()
    
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        folder = f"{reponame}-master"
        for file in zf.namelist():
            if file.startswith(folder):
                zf.extract(file, repo_path.parent)
    
        (repo_path.parent / folder).rename(repo_path)  # rename to actual name
    
    # remove unecessary files
    for pattern in template["exclude"]:
        for path in repo_path.glob(pattern):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    
@cli.command()
@click.argument("path")
@click.argument("host")
def build(path, host):
    """Build a repository at path, using hostname."""
    tree = cydia.Repository(host, path)
    tree.find_debs()
    tree.build()