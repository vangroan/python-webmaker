"""
Website project configuration.
"""

import logging
import os
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError
import yaml

from . import osutils

__all__ = ["Config", "load_config"]


class Config(BaseModel):
    site_name: str
    content_path: str
    template_path: str
    dist_path: str
    base_url: str
    default_template: str

    encoding: str

    charset: str
    language: str
    keywords: list[str] = Field(default_factory=list)


class ConfigError(Exception):
    """
    Errors raised during config loading or handling.
    """

    pass


def load_config(dir_path: str, filename: str = "config.yaml") -> Config:
    """Load project configuration from the given directory path."""

    confpath = Path(dir_path) / filename
    with confpath.open("r") as fp:
        namespace = yaml.safe_load(fp)

    if not isinstance(namespace, dict):
        raise ConfigError(
            f"Loaded config should be a dictionary, but found '{type(namespace).__qualname__}'"
        )

    try:
        config = Config(**namespace)
    except ValidationError as err:
        # TODO: Print validation error fields in a fancy way.
        # errors = format_validation_errors(exc.normalized_messages())
        raise ConfigError("Config file has invalid fields") from err

    return config


def _eval_config(filename: str, dir_path: str) -> dict:
    """Load config file by executing it as a Python program."""
    # Values are extracted from the config file/program by
    # passing in a dictionary as the module globals.
    namespace = {}
    namespace["__file__"] = filename

    # Change current working directory to the config
    # directory, so the config file can access files
    # relative to itself.
    with osutils.cd(os.path.abspath(dir_path)):
        try:
            with open(filename, "r", encoding="utf-8") as fp:
                conf_source = fp.read()
                exec(conf_source, namespace)
        except SystemExit as exc:
            msg = "Config file or one of its imports called sys.exit()"
            raise ConfigError(msg) from exc

    return namespace


def setup_logging(verbose: bool = False):
    if verbose:
        level = logging.DEBUG
        format = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)s %(message)s"
    else:
        level = logging.INFO
        format = "[%(levelname)s] %(message)s"

    logging.basicConfig(
        level=level,
        format=format,
    )
