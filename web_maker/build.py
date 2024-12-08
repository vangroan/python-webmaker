"""Content generator pipeline"""

import contextlib
import logging
import shutil
import os
from time import monotonic_ns

import rcssmin
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from markdown import Markdown

from .config import Config
from .loader import PageLoader
from .template import create_model
from .jinja import JinjaMarkdownExtension, IgnoreMetaExtension
from .utils import replace_ext, subtract_prefix


logger = logging.getLogger(__name__)


def build_content(config: Config):

    with stopwatch():
        logger.info("Building content")

        # Ensure output directory exists
        logger.info("Output directory: %s", config.dist_path)

        # Cache of loaded content files
        page_loader = PageLoader()

        # Common context model passed to all templates.
        model = create_model(config, page_loader)

        # Jinaj2 environment
        template_env = Environment(loader=FileSystemLoader(config.template_path))
        template_env.filters["cssmin"] = rcssmin.cssmin
        template_env.filters["first"] = lambda seq: seq[0] if seq else ""

        for root, _, files in os.walk(config.content_path):
            logger.debug("Walking %s", root)
            for filename in files:
                filepath = os.path.join(root, filename)
                logger.info("Processing %s", filepath)

                metadata = page_loader.get_meta(filepath)

                # Build template scoped model.
                page_model = {**model, "metadata": {**metadata}, "phase": "content"}

                file_str = page_loader.load_page(filepath).decode(config.encoding)

                # FIXME: Move parser out of loop
                md = Markdown(
                    tab_length=2,
                    extensions=[
                        "abbr",
                        "admonition",
                        "tables",
                        "codehilite",
                        "sane_lists",
                        "footnotes",
                        "toc",
                        JinjaMarkdownExtension(template_env, page_model),
                        IgnoreMetaExtension(),
                    ],
                )
                content_html = md.convert(file_str)

                # Recreate sub-directory tree by lifting paths out of content folder
                # and placing them in the root of the distribution folder.
                target_dir = os.path.join(
                    config.dist_path, subtract_prefix(config.content_path, root)
                )
                os.makedirs(target_dir, exist_ok=True)
                target_filepath = os.path.join(
                    target_dir, replace_ext(filename, "html")
                )

                # Build page object
                page = {
                    "metadata": {**metadata},
                    "content": content_html,
                    "original": file_str,
                    "file_location": filepath,
                }

                with open(target_filepath, "w", encoding="utf-8") as fp:
                    page_model["phase"] = "template"
                    template_name = metadata["template"] or config.default_template
                    logger.debug("Load template '%s'", template_name)
                    template = template_env.get_template(template_name)
                    page_html = template.render(page=page, **page_model)

                    # Prettify html output
                    soup = BeautifulSoup(page_html, features="html.parser")

                    logger.debug("Writing %s", target_filepath)
                    fp.write(soup.prettify(formatter="html5"))
                    # fp.write(page_html)

        # Copy static directory as-is.
        shutil.copytree("static/", os.path.join(config.dist_path), dirs_exist_ok=True)

        logger.info("Done")


@contextlib.contextmanager
def stopwatch():
    logger = logging.getLogger(__name__)
    start = monotonic_ns()
    yield
    time_taken = monotonic_ns() - start
    logger.info("Time taken: %.2fms", time_taken / 1000000.0)
