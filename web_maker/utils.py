"""
Miscellaneous utilities.
"""
from io import StringIO
from functools import reduce
from itertools import islice
import typing as T
import pathlib


MarshmallowErrors = T.Union[
    T.Dict[str, T.List[str]], T.Dict[str, T.Dict[str, T.List[str]]]
]


def format_validation_errors(errors: MarshmallowErrors):
    """
    Formats a dictionary of validation errors into a readable string.

    Args:
        errors: Validation errors as returned by the config schema.

    Returns:
        Human readable string.
    """
    if errors is None:
        raise ValueError("Argument errors is None")

    sb = StringIO()

    for field_name in errors:
        sb.write("%s:\n" % field_name)

        field_errors: T.List[str]

        if isinstance(errors[field_name], dict):
            # Flatten dictionary into list and discard keys.
            #
            # Sometimes ValidationError nests the messages an
            # extra level deep. The keys are just numbers that can be discarded.
            #
            # Example: {'field_name': {0: ['Not valid.']}}
            field_errors = reduce(
                lambda el, agg: agg + el, errors[field_name].values(), []
            )
        elif isinstance(errors[field_name], list):
            field_errors = errors[field_name]
        else:
            raise TypeError(
                f"Error map should container either dict or list, not {type(errors[field_name])}"
            )

        for i, err in enumerate(field_errors):
            sb.write("  %i. %s\n" % (i + 1, err))

    return sb.getvalue()


def extract_ext(filename: str) -> T.Optional[str]:
    """
    Extracts the file extension from the given file name.

    Returns:
        A file extension, excluding the period dot.
        None if no file extension could be determined.
    """
    # TODO: Handle hidden unix files
    parts = filename.split(".")
    if len(parts) == 1:
        return None
    return parts[-1:][0]


def replace_ext(filename: str, ext: str) -> str:
    """
    Utility to replace the file extension of the filename.

    If an existing file extension cannot be determined for the filename, then
    the filename is returned unmodified.

    Args:
        filename: Filename string that contains a file extension.
        ext: New file extension

    Returns:
        New filename with new file extension.
    """
    # Handle hidden unix files
    prefix = ""
    if filename.startswith("."):
        prefix = "."
        filename = filename.lstrip(".")

    parts = filename.split(".")
    if len(parts) == 1:
        # no file extension could be determined
        return prefix + filename

    # Ensure file extension input does not have dot
    ext = ext.lstrip(".")

    # Slice off last element
    parts = parts[:-1]
    parts.append(ext)
    return prefix + ".".join(parts)


def subtract_prefix(prefix: str, path: str) -> str:
    """
    Removes the given prefix from the path.

    >>> subtract_prefix('foo/bar', 'foo/bar/baz')
    'baz'

    Args:
        prefix: Start of relative path.
        path: File or directory path.

    Returns:
        Path with te prefix removed, if it is present. If
        there is nothing of the path left when the prefix is
        removed, an empty string is returned. If the prefix doesn't
        match, the path is returned as is.

    Raises:
        Raised when any of the arguments are None.
    """
    if prefix is None:
        raise ValueError("prefix is None")

    if path is None:
        raise ValueError("path is None")

    prefix_parts = pathlib.Path(prefix).parts
    path_parts = pathlib.Path(path).parts

    if prefix_parts == tuple(islice(path_parts, 0, len(prefix_parts))):
        rest = path_parts[len(prefix_parts) :]
        if rest:
            return "/".join(rest)

        # Nothing left of path
        return ""

    return path
