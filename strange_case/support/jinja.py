import re
import os
from jinja2 import FileSystemLoader, Environment


class StrangeCaseEnvironment(Environment):
    def __init__(self, *args, **kwargs):
        kwargs['loader'] = YamlFrontMatterLoader(os.getcwd())
        super(StrangeCaseEnvironment, self).__init__(*args, **kwargs)


class YamlFrontMatterLoader(FileSystemLoader):
    """
    After getting the file content, this loader parses out YAML front matter,
    which must be the first thing in the file.  It consists of three or more dashes, newline
    YAML content, and then the same number of dashes, and a newline.
    """

    def get_source(self, environment, template):
        contents, filename, uptodate = super(YamlFrontMatterLoader, self).get_source(environment, template)
        front_matter_match = re.match(r"\A([-]{3,})$", contents, re.MULTILINE)
        if front_matter_match:
            offset = len(front_matter_match.group(0)) + 1  # +1 for newline
            delim = re.compile("^" + front_matter_match.group(1) + "$")
            lines = contents.split("\n")[1:]
            for line in lines:
                offset += len(line) + 1
                if delim.match(line):
                    break
            contents = contents[offset:]

        return contents, filename, uptodate
