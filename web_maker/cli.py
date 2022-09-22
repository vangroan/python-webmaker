"""Command line interface."""
from functools import wraps
import logging
import os
import click

from web_maker.project import init_project

from .build import build_content
from .config import load_config, setup_logging


class StdCommand(click.Command):
    """
    Command with shared options common to all commands.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = [
            *self.params,
            click.Option(
                ("-v", "--verbose"),
                is_flag=True,
                help="Print debug log level with more information",
            ),
        ]


def inject_logger(func):
    """Decorator for replacing the ``verbose`` option with a configured logger object."""

    @wraps(func)
    def inner(*args, **kwargs):
        setup_logging(kwargs.pop("verbose"))
        logger = logging.getLogger(__name__)
        kwargs = {**kwargs, "logger": logger}
        return func(*args, **kwargs)

    return inner


@click.group()
def main():
    pass


@main.command(cls=StdCommand)
@inject_logger
def init(logger: logging.Logger):
    """
    Creates a new project in the current working directory.
    """
    project_dir = os.path.abspath(os.curdir)

    # Directory must be empty
    for _, dirnames, filenames in os.walk(project_dir):
        if dirnames or filenames:
            logger.error("Failed to create project: directory must be empty")
            exit(1)

    # Use current directory as project name
    dirname = os.path.basename(project_dir)
    project_name = click.prompt(f"Site name", default=dirname)

    init_project(project_name, project_dir)


@main.command(cls=StdCommand)
@inject_logger
def build(logger: logging.Logger):
    """
    Generates the site.
    """
    config = load_config(".")
    logger.debug(config)

    build_content(config)


@main.command()
def clean():
    """
    Deletes the output directory.
    """
    click.echo("Clean")
