from strange_case.nodes import PageNode
from strange_case.registry import Registry


class JinjaNode(PageNode):
    """
    A JinjaNode object is rendered before copied to its destination
    """
    def generate_file(self, site, source_path, target_path):
        content = self.render(site)

        with open(target_path, 'w') as dest:
            dest.write(content.encode('utf-8'))

        self.files_tracked.append(source_path)
        self.files_written.append(target_path)

    def render(self, site=None):
        source_path = self.source_path
        # source_path could be an absolute path, in which case jinja2 actually
        # gets confused.  remove the site_path from source_path so this doesn't
        # happen.
        if source_path[0] == '/':
            source_path = source_path[len(self.config['project_path']):]

        try:
            template = Registry.get('jinja_environment').get_template(source_path)
        except UnicodeDecodeError as e:
            e.args += "Could not process '%s' because of unicode error." % self.source_path
            raise
        return template.render(self.config, my=self, site=site)
