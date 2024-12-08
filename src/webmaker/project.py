"""
Tools for creating and managing a site project using web-maker from the command line.
"""

import logging
import shutil
from pathlib import Path

import jinja2

logger = logging.getLogger(__name__)

PACKAGE_DIR = Path(__file__).parent.expanduser().resolve()
PROJECT_TEMPLATE_DIR = PACKAGE_DIR / "project"
PROJECT_FILES = [".gitignore", "Makefile"]
PROJECT_DIRS = ["content", "static", "templates"]


def init_project(project_name: str):
    """
    Initialise a new project inside the current directory.

    Args:
        project_name: User readable name of the website
    """
    logger.debug("Project template directory: %s", PROJECT_TEMPLATE_DIR)

    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(PROJECT_TEMPLATE_DIR)))
    template_model = {"project_name": project_name}

    logger.info("Initialising project in: %s", Path.cwd())

    with open("config.yaml", "w") as fp:
        rendered = template_env.get_template("config.yaml").render(**template_model)
        fp.write(rendered)

    try:
        # Copy top-level files.
        for filename in PROJECT_FILES:
            logger.info("Creating: %s", filename)

            if Path(filename).exists():
                raise FileExistsError(f"File exists: '{filename}'")

            srcpath = PROJECT_TEMPLATE_DIR / filename
            shutil.copyfile(srcpath, filename)

        # Copy project directories.
        for dirname in PROJECT_DIRS:
            logger.info("Creating: %s/", dirname)
            srcpath = PROJECT_TEMPLATE_DIR / dirname
            shutil.copytree(srcpath, dirname)

    except FileExistsError as err:
        logger.error(err)
        exit(1)


class ProjectError(Exception):
    pass
