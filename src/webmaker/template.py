"""
Functions for use inside templates.
"""

import glob
import os
import pathlib
from collections.abc import Mapping, Sequence
from typing import Any, Callable
from urllib.parse import urljoin

from .config import Config
from .loader import Page, PageLoader
from .utils import extract_ext, replace_ext


def create_model(config: Config, page_cache: PageLoader) -> dict[str, Any]:
    """
    Creates the top scope template model.

    :param config: Config dictionary.
    :param page_cache: Page loader that can retrieve page metadata.
    :return: Dictionary of values that can be passed to all templates.
    """
    model: dict[str, Any] = {"config": config.model_dump()}

    model[Concat.name] = Concat()
    model[Join.name] = Join()
    model[InlineFile.name] = InlineFile()
    model["url"] = create_url_lookup(config.base_url, (config.content_path,), ext_map={"md": "html"})
    model[ListPages.name] = ListPages(config.content_path, page_cache)

    return model


class Concat:
    """
    Concatenate strings together.
    """

    name = "concat"

    def __call__(self, *parts: str) -> str:
        return "".join(parts)


class Join:
    """
    Join strings together using the given seperator.
    """

    name = "join"

    def __call__(self, seperator: str, *parts: str) -> str:
        return seperator.join(parts)


class InlineFile:
    """
    Loads a file's contents, and outputs it as a string.
    """

    name = "inline_file"

    def __call__(self, file_path: str, encoding: str = "utf-8") -> str:
        with open(file_path, "r", encoding=encoding) as fp:
            return fp.read()


class ListPages:
    """
    Recursively list pages in a content directory.
    """

    name = "list_pages"

    def __init__(self, content_dir: str, page_cache: PageLoader):
        self.content_dir = pathlib.Path(content_dir)
        self.page_cache = page_cache

    def __call__(self, glob_pattern: str = "*") -> list[Page]:
        glob_pathname = os.path.join(self.content_dir, glob_pattern)
        result = []

        for path in glob.glob(glob_pathname, recursive=True):
            metadata = self.page_cache.get_meta(path)
            filepath = os.path.normpath(path)
            result.append(Page(metadata=metadata, filepath=filepath))

        return result


def create_url_lookup(
    base_url: str, directory_paths: Sequence[str] = (), ext_map=Mapping[str, str]
) -> Callable[[str], str]:
    """
    Creates a helper function for use in templates that can translate file paths
    to resource URLs for use in html pages in the website.

    Args:
        base_url: The base URL that will be prepended to the path.
            Importantly the end must trail with a slash, otherwise
            the last part of the path will be treated as a file
            when resolving relative paths.
        directory_paths: Directories to search for file.
        ext_map: Mapping of files extension, used to convert file names
            from a source type to a target type.

    Raises:
        ValueError: When base URL is None.

    Return:
        Function that translates project file paths to site resource URLs.
    """
    # TODO: Support for permalinks
    # TODO: Support for URL rewriting

    if base_url is None:
        raise ValueError("base_url is None")

    dir_paths = tuple(pathlib.Path(p).parts for p in directory_paths)

    if ext_map is None:
        ext_map = {}

    # Validate extension map
    for key, value in ext_map.items():
        message = "File extension map should not include leading dot. Replace '{incorrect}' with '{correct}'"
        if key.startswith("."):
            raise ValueError(message.format(incorrect=key, correct=key.lstrip(".")))

        if value.startswith("."):
            raise ValueError(message.format(incorrect=value, correct=value.lstrip(".")))

    def url_lookup(file_location: str) -> str:
        """
        Given a path to a file in the project directory, return the equivalent URL path
        in the generated site's file.

        Args:
            file_location: Filesystem path to the content file.

        Returns:
            Absolute path to the site file.
        """
        # Subtract 'content' from the file location
        file_path_parts = pathlib.Path(file_location).parts
        for path in dir_paths:
            path_len = len(path)
            if file_path_parts[:path_len] == path:
                file_location = "/".join(file_path_parts[path_len:])

        # Change file extension
        file_ext = extract_ext(file_location)
        if file_ext:
            new_file_ext = ext_map.get(file_ext, None)
            if new_file_ext:
                file_location = replace_ext(file_location, new_file_ext)

        return urljoin(base_url, file_location)

    return url_lookup
