from __future__ import absolute_import
import re
from strange_case.nodes import PageNode
from strange_case.registry import Registry
from strange_case.support.jinja import fix_path
from plywood import Plywood


@Registry.register_engine('plywood')
class PlywoodNode(PageNode):
    """
    A PlywoodNode object is rendered before copied to its destination
    """
    def generate_file(self, site, source_path, target_path):
        content = self.render(site)

        with open(target_path, 'w') as dest:
            dest.write(content.encode('utf-8'))

        self.files_tracked.append(source_path)
        self.files_written.append(target_path)

    def render(self, site=None):
        try:
            env = Registry.get('plywood_environment')
            template_path = fix_path(self.source_path)
            with open(template_path) as f:
                contents = f.read()
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

        except UnicodeDecodeError as e:
            e.args += "Could not process '%s' because of unicode error." % self.source_path
            raise
        env.scope.push()
        env.scope['site'] = site
        env.scope['my'] = self
        retval = Plywood(contents).run(self.config, env)
        env.scope.pop()
        return retval
