"""
Jina2 customisation.
"""
from markdown import Extension
from markdown.preprocessors import Preprocessor


class JinjaMarkdownExtension(Extension):
    def __init__(self, template_env, model=None):
        self.config = {}
        self.template_env = template_env
        self.model = model if model is not None else {}

        super().__init__()

    # noinspection PyMethodOverriding
    def extendMarkdown(self, md, _md_globals):
        md.preprocessors.register(
            JinjaMarkdownProcessor(md, self.config, self.template_env, self.model),
            "jinja",
            10,
        )


class JinjaMarkdownProcessor(Preprocessor):
    def __init__(self, md, _config, template_env, model):
        """
        :type template_env: jinja2.environment.Environment
        :param template_env: Jinja2 template environment that has been
            primed to handle the markdown file as a template.
        """
        super().__init__(md)
        self._environment = template_env
        self._model = model

    def run(self, lines):
        # Jinja templating uses blocks, which means it must
        # process all text.
        text = "\n".join(lines)
        template = self._environment.from_string(text)
        new_text = template.render(**self._model)
        return new_text.split("\n")


class IgnoreMetaExtension(Extension):
    """
    Ignores the metadata section in markdown files.
    """

    def __init__(self):
        super().__init__()

    # noinspection PyMethodOverriding
    def extendMarkdown(self, md, _md_globals):
        md.preprocessors.register(IgnoreMetaProcessor(md), "ignore-meta", 20)


class IgnoreMetaProcessor(Preprocessor):
    def __init__(self, md):
        super().__init__(md)

    def run(self, lines):
        ignoring = False

        for index, line in enumerate(lines):
            counter = index
            if not ignoring:
                # first section marker
                if line.strip() == "---":
                    ignoring = not ignoring
            else:
                # second section marker
                if line.strip() == "---":
                    break
        else:
            counter = 0

        # When the section is present, the counter is
        # increased by 1 to exclude the closing marker
        # from the markdown parse.
        #
        # When no section is present, the increment would
        # slice off the first line of the markdown.
        if counter > 1:
            counter += 1

        # slice off the section
        return lines[counter:]
