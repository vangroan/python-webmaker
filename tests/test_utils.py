import pytest

import web_maker.utils


@pytest.mark.parametrize(
    "filename,ext",
    [
        ("index.md", "md"),
        ("unknown", None),
        ("content/index.md", "md"),
        ("a.b/index.md", "md"),
    ],
)
def test_extract_ext(filename, ext):
    assert web_maker.utils.extract_ext(filename) == ext


@pytest.mark.parametrize(
    "filename,ext,new_filename",
    [
        ("index.md", "html", "index.html"),
        ("content/index.md", "html", "content/index.html"),
        ("index", "html", "index"),
        (".index.md", "html", ".index.html"),
        (".index", "html", ".index"),
    ],
)
def test_replace_ext(filename, ext, new_filename):
    assert web_maker.utils.replace_ext(filename, ext) == new_filename


@pytest.mark.parametrize(
    "prefix,path,exception",
    [
        (None, "foo/bar/baz", ValueError),
        ("foo/bar", None, ValueError),
        # ("foo/bar", "foo/bar/baz"),
    ],
)
def test_subtract_prefix_invalid_input(prefix, path, exception):
    with pytest.raises(exception):
        web_maker.utils.subtract_prefix(prefix, path)


@pytest.mark.parametrize(
    "prefix,path,result",
    [
        ("foo/bar", "foo/bar/baz", "baz"),
        ("foo/bar", "foo/bar", ""),
        ("mismatched", "foo/bar", "foo/bar"),
    ],
)
def test_subtract_prefix(prefix, path, result):
    assert web_maker.utils.subtract_prefix(prefix, path) == result
