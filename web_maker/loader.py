from copy import deepcopy
import os
from typing import Dict, Optional

import click
from marshmallow import fields, EXCLUDE, ValidationError, Schema
import yaml

from .utils import format_validation_errors


class PageLoadError(Exception):
    """
    Error raised during loading or processing page content files.
    """
    pass


class PageLoader(object):
    """
    Loader for page content files.

    The loader will extract metadata from content files, so the metadata
    can be used before the contents are parsed and rendered.

    Loaded metadata and content are cached, using the given path as a caching key.
    """

    def __init__(self):
        self._cache: Dict[str, PageLoader.CacheItem] = {}
        self._section_marker = b'---'

    def get_meta(self, file_path) -> dict:
        """
        Load and parse the metadata of the file at the given file path.

        :raise PageLoadError: On IO failures, metadata parsing or validation errors.
        """
        file_path = os.path.normpath(file_path)
        self._get_or_load(file_path)

        return deepcopy(self._cache[file_path].meta)

    def load_page(self, file_path) -> bytes:
        """
        Load the contents of the file at the given file path.

        :raise PageLoadError: On IO failure.
        """
        file_path = os.path.normpath(file_path)
        self._get_or_load(file_path)

        return self._cache[file_path].file_bytes

    def _get_or_load(self, file_path):
        # If cache item doesn't exist, load file.
        if file_path not in self._cache:
            click.echo("Page cache miss %s", file_path)
            self._load_page(file_path)

    def _load_page(self, file_path):
        try:
            with open(file_path, 'rb') as fp:
                data = fp.read()

                metadata_str = self._extract_metadata_section(data) or b''
                metadata = yaml.safe_load(metadata_str) or {}
                metadata = BuiltinMetaSchema(unknown=EXCLUDE).load(metadata)
                click.echo("Metadata %s", metadata)

                self._cache[file_path] = PageLoader.CacheItem(meta=metadata, file_bytes=data)
        except OSError as err:
            raise PageLoadError("Error opening file %s" % file_path) from err
        except PageLoadError as err:
            raise PageLoadError("Error while loading page %s" % file_path) from err
        except yaml.YAMLError as err:
            raise PageLoadError("Error while parsing metadata for %s" % file_path) from err
        except ValidationError as err:
            raise PageLoadError(
                "Built-in metadata validation errors:\n%s"
                % format_validation_errors(err.messages)
            ) from err

    def _extract_metadata_section(self, data) -> Optional[str]:
        """
        Metadata begins and ends with a marker line, splitting the
        file into three parts. When the parts are not exactly three,
        it is ignored and None is returned.
        """
        parts = data.split(self._section_marker, 2)
        if len(parts) == 3:
            # Section present
            return parts[1]
        elif len(parts) == 1:
            # Unbalanced section markers. No section present.
            return None

    class CacheItem(object):
        __slots__ = ('meta', 'file_bytes',)

        def __init__(self, meta=None, file_bytes=None):
            self.meta = meta
            self.file_bytes = file_bytes


class BuiltinMetaSchema(Schema):
    """
    Schema to validate content metadata that has special purposes within the script.
    """
    title = fields.String(missing='page')
    template = fields.String(missing=None)
    draft = fields.Boolean(missing=False)
    # FIXME: yaml loader outputs datetime.date, marshmallow expects a string
    created = fields.Inferred()
    published = fields.Inferred()


class PageSchema(Schema):
    meta = fields.Nested(BuiltinMetaSchema, required=True)
    content = fields.String(missing='', required=False)
    file_path = fields.String(required=True)
