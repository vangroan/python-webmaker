"""
Website project configuration.
"""
import os

from marshmallow import fields, Schema, ValidationError
import yaml

from .utils import format_validation_errors


class ConfigSchema(Schema):
    site_name = fields.String(missing="website")
    content_dir = fields.String(required=True)
    template_dir = fields.String(required=True)
    dist_dir = fields.String(required=True)
    base_url = fields.Url(required=True)
    default_template = fields.String(required=True)
    language = fields.String(missing='en-gb')
    charset = fields.String(missing='UTF-8')


class ConfigError(Exception):
    """
    Errors raised during config loading or handling.
    """
    pass


def load_config(*directories, config_filename=('config.yaml', 'config.yml')) -> dict:
    """
    Walks the given directories, looking for config files. The first file with a matching
    filename will be loaded as the script's config.

    :param directories: Directory paths to search for config files.
    :param config_filename: Config file name to match during search.
    :return: Config values in dictionary.
    :raise ConfigError: No config file is found, file is malformed or doesn't pass validation.
    """
    for directory in directories:
        # Convert to absolute path
        absolute_path = os.path.normpath(directory)

        for root, _, files in os.walk(absolute_path):
            for filename in files:
                if filename in config_filename:
                    file_path = os.path.join(root, filename)
                    with open(file_path) as fp:
                        try:
                            config = yaml.safe_load(fp)
                        except yaml.YAMLError as ex:
                            raise ConfigError("Failed to deserialize file %s" % file_path) from ex

                        try:
                            return ConfigSchema().load(config)
                        except ValidationError as err:
                            raise ConfigError(
                                "Config validation errors:\n%s" % format_validation_errors(err.messages)) from err

    raise ConfigError("No config file was found")
