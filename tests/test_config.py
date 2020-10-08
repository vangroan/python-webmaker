import os

import pytest

from web_maker.config import load_config


SAMPLE_YAML = """# Test configuration file

site_name: Test Site
"""


@pytest.fixture(scope='module')
def config_directory():
    cwd = os.path.realpath(os.path.dirname(__file__))
    print("Configuration directory:", cwd)
    yield cwd


def test_config_walk(config_directory):
    config = load_config(config_directory)
    print(config)
    assert config['site_name'] == "Test Site"
    assert config['content_dir'] == "content/"
