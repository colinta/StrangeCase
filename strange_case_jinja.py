import yaml
import re
from jinja2 import Template, FileSystemLoader


class YamlFrontMatterLoader(FileSystemLoader):
    """
    After getting the file content, this loader parses out YAML front matter,
    which must be the first thing in the file.  It consists of three or more dashes, newline
    YAML content, and then the same number of dashes, and a newline.

    The YAML content is placed in a dictionary - YamlFrontMatterLoader.template_dict - and
    the YamlFrontMatterTemplate will look in that dictionary for additional context
    variables.  This is merged into the global config.yaml and any folder settings.
    """
    template_dict = {}

    def get_source(self, environment, template):
        contents, filename, uptodate = super(YamlFrontMatterLoader, self).get_source(environment, template)
        front_matter_match = re.match(r"\A([-]{3,})$", contents, re.MULTILINE)
        if front_matter_match:
            offset = len(front_matter_match.group(0)) + 1  # +1 for newline
            delim = re.compile("^" + front_matter_match.group(1) + "$")
            front_matter = ""
            lines = contents.split("\n")[1:]
            for line in lines:
                offset += len(line) + 1
                if delim.match(line):
                    break
                front_matter += line + "\n"
            contents = contents[offset:]
            self.template_dict[template] = yaml.load(front_matter)
        else:
            self.template_dict[template] = {}

        return contents, filename, uptodate

    def load(self, environment, name, globals=None):
        template = super(YamlFrontMatterLoader, self).load(environment, name, globals)
        try:
            template.context.update(YamlFrontMatterLoader.template_dict[name])
        except KeyError:
            pass

        return template


class YamlFrontMatterTemplate(Template):
    """
    Looks in YamlFrontMatterLoader.template_dict for additional context variables which
    might have been loaded from the YAML front matter.
    """
    @classmethod
    def from_code(self, *args, **kwargs):
        ret = super(YamlFrontMatterTemplate, self).from_code(*args, **kwargs)
        ret.context = {}
        return ret

    def render(self, *args, **kwargs):
        """
        merge in the context variables from the YAML front matter - they have the final say.
        """
        page = kwargs.get('page', {})
        page.update(self.context)
        kwargs['page'] = page
        return super(YamlFrontMatterTemplate, self).render(*args, **kwargs)
