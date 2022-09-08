"""Command line interface."""
import logging
import click

from .build import build_content
from .config import load_config, setup_logging


@click.group()
def main():
    pass


@main.command()
@click.option("--log-level", "-l", default="info")
def build(log_level: str):
    """
    Generates the site.
    """
    setup_logging(level=log_level.upper())
    logger = logging.getLogger(__name__)
    logger.info("foobar")
    logger.info("baz")

    # from pprint import pprint
    config = load_config(".")
    # pprint(config)

    build_content(config)

    click.echo(click.style("Hello World!", fg="green"))
    click.echo(click.style("Some more text", bg="blue", fg="white"))
    click.echo(click.style("ATTENTION", blink=True, bold=True))
    click.secho("Hello World!", fg="green")
    click.secho("Some more text", bg="blue", fg="white")
    click.secho("ATTENTION", blink=True, bold=True)
    click.secho("⠯", fg="green")


@main.command()
def clean():
    """
    Deletes the output directory.
    """
    click.echo("Clean")
