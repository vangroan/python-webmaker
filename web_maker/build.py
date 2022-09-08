"""Content generator pipeline"""
import contextlib
import logging
import os
from time import monotonic_ns

import rcssmin
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from markdown import Markdown

from .loader import PageLoader
from .template import create_model
from .jinja import JinjaMarkdownExtension, IgnoreMetaExtension
from .utils import replace_ext, subtract_prefix


def build_content(config: dict):
    logger = logging.getLogger(__name__)

    with stopwatch():
        logger.info("Building content")

        # Ensure output directory exists
        logger.info("Output directory: %s", config["dist_path"])

        # Cache of loaded content files
        page_loader = PageLoader()

        # Common context model passed to all templates.
        model = create_model(config, page_loader)

        # Jinaj2 environment
        template_env = Environment(loader=FileSystemLoader(config["template_path"]))
        template_env.filters["cssmin"] = rcssmin.cssmin
        template_env.filters["first"] = lambda seq: seq[0] if seq else ""

        for root, _, files in os.walk(config["content_path"]):
            logger.debug("Walking %s", root)
            for filename in files:
                filepath = os.path.join(root, filename)
                logger.info("Processing %s", filepath)

                metadata = page_loader.get_meta(filepath)

                # Build template scoped model.
                template_model = {**model}
                template_model["get_meta"] = lambda name: metadata.get(name)

                file_bytes = page_loader.load_page(filepath)
                file_str = file_bytes.decode("utf-8")

                # FIXME: Move parser out of loop
                md = Markdown(
                    extensions=[
                        "abbr",
                        "admonition",
                        "tables",
                        "codehilite",
                        "sane_lists",
                        "footnotes",
                        "toc",
                        JinjaMarkdownExtension(template_env, template_model),
                        IgnoreMetaExtension(),
                    ]
                )
                content_html = md.convert(file_str)

                # Recreate sub-directory tree by lifting paths out of content folder
                # and placing them in the root of the distribution folder.
                target_dir = os.path.join(
                    config["dist_path"], subtract_prefix(config["content_path"], root)
                )
                os.makedirs(target_dir, exist_ok=True)
                target_filepath = os.path.join(
                    target_dir, replace_ext(filename, "html")
                )

                # Build page object
                page = {
                    "meta": {**metadata},
                    "content": content_html,
                    "file_location": filepath,
                }

                with open(target_filepath, "w", encoding="utf-8") as fp:
                    template_name = metadata["template"] or config["default_template"]
                    logger.info("Load template '%s'", template_name)
                    template = template_env.get_template(template_name)
                    page_html = template.render(page=page, **template_model)

                    # Prettify html output
                    soup = BeautifulSoup(page_html, features="html.parser")

                    logger.debug("Writing %s", target_filepath)
                    fp.write(soup.prettify())

        logger.info("Done")


@contextlib.contextmanager
def stopwatch():
    logger = logging.getLogger(__name__)
    start = monotonic_ns()
    yield
    time_taken = monotonic_ns() - start
    logger.info("Time taken: %.2fms", time_taken / 1000000.0)
