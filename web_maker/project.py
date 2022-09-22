"""
Tools for creating and managing a site project using web-maker from the command line.
"""
import logging
import os

import jinja2


def new_project():
    """
    Create a sub-directory and initialize a new project inside it.
    """
    raise NotImplementedError()


def init_project(project_name: str, project_dir: str):
    """
    Initialize a new project inside the current directory.

    Args:
        project_name: User readable name of the website
        project_dir: Directory path where the project wll be created
    """
    logger = logging.getLogger(__name__)

    # Directory contining project template
    template_dir = os.path.join(os.path.dirname(__file__), "project")

    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template_model = {"project_name": project_name}

    with open("config.yaml", "w") as fp:
        rendered = template_env.get_template("config.yaml").render(**template_model)
        logger.debug("render: %s", rendered)
        fp.write(rendered)

    # TODO: conf.py or config.yaml
    # TODO: templates/
    # TODO: styles/
    # TODO: content/
    raise NotImplementedError()


class ProjectError(Exception):
    pass
