# coding: utf8

import io
import sys
import zipfile

import click
import requests

from . import repo


def main(args: list = sys.argv[1:]):
    @click.group()
    def cli():
        """Cydia/Sileo repository manager/configurator."""
        pass

    @cli.command()
    @click.argument("path")
    @click.option(
        "-t",
        "--template",
        "template_name",
        help=f"Name of the template to use ({', '.join(t for t in repo.TEMPLATES)})",
    )
    def init(template_name):
        github_repo = repo.TEMPLATES.get[template_name]["github"]
        response = requests.get(
            f"https://github.com/{github_repo}/archive/master.zip", allow_redirects=True
        )
        zip_buffer = zipfile.ZipFile(io.BytesIO(response.content))

    @cli.command()
    @click.argument("path")
    @click.argument("host")
    def build(path, host):
        """Build a repository at path, using hostname."""
        tree = repo.Repository(host, path)
        tree.find_debs()
        tree.build()

    cli()