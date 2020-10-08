"""
Miscellaneous utilities.
"""
from io import StringIO
from functools import reduce
from itertools import islice
import pathlib
from typing import Optional


def format_validation_errors(errors):
    """
    Formats a dictionary of validation errors into a readable string.

    :type errors: Union[Dict[str, List[str]], Dict[str, Dict[str, List[str]]]]
    :param errors: Validation errors as returned by the config schema.
    :return: Human readable string.
    """
    if errors is None:
        raise ValueError("Argument errors is None")

    sb = StringIO()

    for field_name in errors:
        sb.write("%s:\n" % field_name)

        if type(errors[field_name]) is dict:
            # Flatten dictionary into list and discard keys.
            #
            # Sometimes ValidationError nests the messages an
            # extra level deep. The keys are just numbers that can be discarded.
            #
            # Example: {'field_name': {0: ['Not valid.']}}
            field_errors = reduce(lambda el, agg: agg + el, errors[field_name].values(), [])
        else:
            field_errors = errors[field_name]

        for i, err in enumerate(field_errors):
            sb.write("  %i. %s\n" % (i + 1, err))

    return sb.getvalue()


def extract_ext(filename) -> Optional[str]:
    """
    Extracts the file extension from the given file name.

    :return: A file extension, excluding the period dot. None if no file
        extension could be determined.
    """
    # TODO: Handle hidden unix files
    parts = filename.split(".")
    if len(parts) == 1:
        return None
    return parts[-1:][0]


def replace_ext(filename, ext) -> str:
    """
    Utility to replace the file extension of the filename.

    If an existing file extension cannot be determined for the filename, then
    the filename is returned unmodified.

    :type filename: str
    :type ext: str
    :param filename: Filename string that contains a file extension.
    :param ext: New file extension.
    :return: New filename with new file extension.
    """
    # TODO: Handle hidden unix files
    parts = filename.split(".")
    if len(parts) == 1:
        return filename
    # Slice off last element
    parts = parts[:-1]
    parts.append(ext)
    return ".".join(parts)


def subtract_prefix(prefix, path) -> str:
    """
    Removes the given prefix from the path.

    >>> subtract_prefix('foo/bar', 'foo/bar/baz')
    'baz'

    :param prefix: Start of relative path.
    :param path: File or directory path.
    :return: Path with te prefix removed, if it is present. If
        there is nothing of the path left when the prefix is
        removed, an empty string is returned. If the prefix doesn't
        match, the path is returned as is.
    :raise ValueError: Raised when any of the arguments are None.
    """
    if prefix is None:
        raise ValueError("prefix is None")

    if path is None:
        raise ValueError("path is None")

    prefix_parts = pathlib.Path(prefix).parts
    path_parts = pathlib.Path(path).parts

    if prefix_parts == tuple(islice(path_parts, 0, len(prefix_parts))):
        rest = path_parts[len(prefix_parts):]
        if rest:
            return "/".join(rest)

        # Nothing left of path
        return ""

    return path
