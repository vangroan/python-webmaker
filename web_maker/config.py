"""
Website project configuration.
"""
import logging
import os
import typing as T

from marshmallow import fields, Schema, ValidationError, EXCLUDE

from .utils import format_validation_errors
from . import osutils


class ConfigSchema(Schema):
    site_name = fields.String(missing="website")
    content_path = fields.String(required=True)
    template_path = fields.String(required=True)
    dist_path = fields.String(required=True)
    default_template = fields.String(required=True)

    # HTML
    html_base_url = fields.Url(required=True)
    html_language = fields.String(missing="en-gb")
    html_charset = fields.String(missing="UTF-8")

    class Meta:
        unknown = EXCLUDE


class ConfigError(Exception):
    """
    Errors raised during config loading or handling.
    """

    pass


def load_config(dir_path: str, filename="conf.py") -> dict:
    """Load project configuration from the given directory path."""
    namespace = _eval_config(filename, dir_path)

    try:
        config = ConfigSchema().load(namespace)
    except ValidationError as exc:
        # TODO: Print validation error fields in a fancy way.
        errors = format_validation_errors(exc.normalized_messages())
        raise ConfigError(f"Config file has invalid fields: \n{errors}") from exc

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


def setup_logging(level: T.Union[str, int] = "DEBUG"):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)s %(message)s",
    )
