"""
Functions for use inside templates.
"""
from copy import deepcopy
import glob
import os
import pathlib
from typing import Callable, Generator
from urllib.parse import urljoin

from .loader import PageSchema
from .utils import extract_ext, replace_ext


def create_model(config, page_cache):
    """
    Creates the top scope template model.

    :param config: Config dictionary.
    :param page_cache: Page loader that can retrieve page metadata.
    :return: Dictionary of values that can be passed to all templates.
    """
    model = deepcopy(config)

    def inline_file(file_path) -> str:
        """
        Loads a file's contents, and outputs it as a string.
        """
        with open(file_path) as fp:
            return fp.read()

    model['site_name'] = config['site_name']
    model['concat'] = lambda sep, *parts: sep.join(parts)
    model['inline_file'] = inline_file
    model['url'] = create_url_lookup(config['base_url'], (config['content_dir'],), ext_map={'md': 'html'})
    model['list_pages'] = create_list_pages(config['content_dir'], page_cache)

    return model


def create_url_lookup(base_url, directory_paths=(), ext_map=None) -> Callable[[str], str]:
    """
    Creates a helper function for use in templates that can translate file paths
    to resource URLs for use in html pages in the website.

    :type base_url: str
    :type directory_paths: Sequence[str]
    :type ext_map: Dict[str, str]
    :param base_url: The base URL that will be prepended to the
        path. Importantly the end must trail with a slash, otherwise
        the last part of the path will be treated as a file
        when resolving relative paths.
    :param directory_paths:
    :param ext_map: Mapping of files extensions, used to convert file names
        from a source type to a target type.
    :return: Function that translates project file paths to site resource URLs.
    :raise ValueError: When base URL is None.
    """
    # TODO: Support for permalinks
    # TODO: Support for URL rewriting

    if base_url is None:
        raise ValueError("base_url is None")

    dir_paths = tuple(pathlib.Path(p).parts for p in directory_paths)

    if ext_map is None:
        ext_map = {}

    def url_lookup(file_location) -> str:
        """
        Given a path to a file in the project directory, return the equivalent URL path
        in the generated site's file.

        :return: Absolute path to the site file.
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


def create_list_pages(content_dir, page_cache, root_dir=None) -> Callable[[str], Generator[dict, None, None]]:
    """
    Creates a helper function for use in templates for recursively listing pages
    in the content folder.

    :param content_dir: Directory where page files are kept.
    :param page_cache: Page loader that can retrieve page metadata.
    :param root_dir: Optional root directory where the content directory is located.
        If None, the current working directory is used.
    :return: Function that takes a file path glob, and returns a generator
        that yields page objects.
    """
    root_dir = root_dir or os.path.curdir
    target_dir = os.path.join(root_dir, content_dir)

    def list_pages(glob_pathname: str) -> Generator[dict, None, None]:
        glob_pathname = os.path.join(target_dir, glob_pathname)

        for path in glob(glob_pathname, recursive=True):
            metadata = page_cache.get_meta(path)
            # FIXME: Do we need the processed markdown content here?
            file_path = os.path.normpath(path)
            yield PageSchema().load({'meta': metadata, 'file_path': file_path})

    return list_pages
