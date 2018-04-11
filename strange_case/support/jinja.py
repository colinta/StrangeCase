"""
Jinja support adds the following abilities:

1. Adds a ``YamlFrontMatterLoader``, which searchs the beginning of the file for
   YAML between two lines of an equal number of three or more dashes.

   These lines are stripped off before rendering.
2. Jinja has nice support for displaying errors, but the YAML front matter
   confuses things.  This module fixes that, too, using a ``StrangeCaseStr``
   which keeps track of how many lines to ignore.  The blank lines are included
   during compilation, and removed after the file is generated.
3. Provides a ``fix_paths`` function that returns a slash-separated relative path,
   even on Windows.

   Note: This function will also chomp any in-filename backslashes.
   Hopefully you don't have any of those in the relative path to your template.
"""
import re
import os
from jinja2 import FileSystemLoader, Environment, Template
from jinja2.utils import internalcode


class StrangeCaseEnvironment(Environment):
    def __init__(self, project_path, *args, **kwargs):
        project_path = fix_path(project_path)
        kwargs['loader'] = YamlFrontMatterLoader([project_path, os.getcwd() ,'/'])
        self.template_class = StrangeCaseTemplate
        super(StrangeCaseEnvironment, self).__init__(*args, **kwargs)


class StrangeCaseStr(str):
    def __new__(self, content, number_yaml_lines):
        s = str.__new__(self, content)
        s.__init__(number_yaml_lines)
        s.number_yaml_lines = number_yaml_lines
        return s


class StrangeCaseTemplate(Template):
    def render(self, *args, **kwargs):
        ret = super(StrangeCaseTemplate, self).render(*args, **kwargs)
        if hasattr(self, 'number_yaml_lines'):
            lines = ret.splitlines()
            ret = "\n".join(lines[self.number_yaml_lines:])
        return ret


class YamlFrontMatterLoader(FileSystemLoader):
    """
    After getting the file content, this loader parses out YAML front matter,
    which must be the first thing in the file.  It consists of three or more
    dashes or backticks, a newline, YAML content, a newline and then the same
    number of dashes or backticks, and a newline again.

    Examples::

        ----
        yaml: {goes: 'here'}
        ----
        <!-- template -->

        ````
        python = {'goes': 'here'}
        ````
        <!-- template -->

    When the python code is executed, it is given ``config`` as the local
    context, so changes to local variables result in changes to the page
    context.
    """
    def get_source(self, environment, template):
        """
        Matches 3 or more dashes or backticks to the beginning of the content,
        and then tries to match the same delimiter.
        """
        contents, filename, uptodate = super(YamlFrontMatterLoader, self).get_source(environment, template)
        front_matter_match = re.match(r"\A([-]{3,}|[`]{3,})(\r\n|\r|\n)", contents)
        number_yaml_lines = 0
        if front_matter_match:
            newline = front_matter_match.group(2)  # group(2) contains the newline/CRLF
            number_yaml_lines += 1
            offset = len(front_matter_match.group(0))
            delim = re.compile("^" + front_matter_match.group(1) + "$")
            lines = contents.splitlines()
            for line in lines[1:]:  # skip the first line, the opening front matter
                offset += len(line) + len(newline)
                number_yaml_lines += 1
                if delim.match(line):
                    break
            contents = (newline * number_yaml_lines) + contents[offset:]

        return StrangeCaseStr(contents, number_yaml_lines), filename, uptodate

    @internalcode
    def load(self, environment, name, globals=None):
        """
        If a ``StrangeCaseStr`` is found, ``str.number_yaml_lines`` are stripped
        off the front of the file after it is generated.
        """
        code = None
        if globals is None:
            globals = {}

        # first we try to get the source for this template together
        # with the filename and the uptodate function.
        source, filename, uptodate = self.get_source(environment, name)

        # try to load the code from the bytecode cache if there is a
        # bytecode cache configured.
        bcc = environment.bytecode_cache
        if bcc is not None:
            bucket = bcc.get_bucket(environment, name, filename, source)
            code = bucket.code

        # if we don't have code so far (not cached, no longer up to
        # date) etc. we compile the template
        if code is None:
            code = environment.compile(source, name, filename)

        # if the bytecode cache is available and the bucket doesn't
        # have a code so far, we give the bucket the new code and put
        # it back to the bytecode cache.
        if bcc is not None and bucket.code is None:
            bucket.code = code
            bcc.set_bucket(bucket)

        t = environment.template_class.from_code(environment, code, globals, uptodate)

        if isinstance(source, StrangeCaseStr):
            t.number_yaml_lines = source.number_yaml_lines
        return t


def fix_path(path):
    """
    Provides a ``fix_paths`` function that returns a slash-separated relative path,
    even on Windows.

    Jinja chokes on backslash-separated paths, and slash-separated paths work well
    enough in Windows anyway.  See also Jinja2-99_, Jinja2-98_.

    .. _Jinja2-98: https://github.com/mitsuhiko/jinja2/issues/98
    .. _Jinja2-99: https://github.com/mitsuhiko/jinja2/pull/99

    Note: This function will also chomp any in-filename backslashes.
    Hopefully you don't have any of those in the relative path to your template.
    """
    return path.replace(os.path.sep, '/')
