import pytest

import web_maker.template


@pytest.fixture(scope="module")
def test_dir():
    pass


@pytest.mark.parametrize(
    "base_url,exception",
    [
        (None, ValueError),
    ],
)
def test_url_lookup_invalid_input(base_url, exception):
    with pytest.raises(exception):
        web_maker.template.create_url_lookup(base_url)


def test_url_lookup():
    dir_paths = ["content/"]
    ext_map = {"md": "html"}
    url_lookup = web_maker.template.create_url_lookup(
        "http://github.com", dir_paths, ext_map
    )
    href = url_lookup("content/index.md")
    assert href == "http://github.com/index.html"
