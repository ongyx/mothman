# coding: utf8

import io
import pathlib
import sys
import zipfile

import click
import requests

from . import repo


@click.group()
def cli():
    """Cydia/Sileo repository manager/configurator."""
    pass


@cli.command()
@click.argument("repo_path")
@click.option(
    "-t",
    "--template",
    "template_name",
    help=f"Name of the template to use ({', '.join(t for t in repo.TEMPLATES)})",
)
def init(repo_path, template_name):
    """Initalise a repository at path."""
    repo_path = pathlib.Path(repo_path)
    template = repo.TEMPLATES[template_name]
    user, repo = template["github"].split("/")
    response = requests.get(
        f"https://github.com/{user}/{repo}/archive/master.zip",
        allow_redirects=True
    )
    
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        folder = f"{repo}-master"
        for file in zf.namelist():
            if file.startswith(folder):
                zf.extract(file, path)
    
    # remove unecessary files
    for file in template["exclude"]:
        file = pathlib.Path(file)

    
@cli.command()
@click.argument("path")
@click.argument("host")
def build(path, host):
    """Build a repository at path, using hostname."""
    tree = repo.Repository(host, path)
    tree.find_debs()
    tree.build()