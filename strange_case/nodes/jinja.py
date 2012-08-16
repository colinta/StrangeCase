from strange_case.nodes import PageNode
from strange_case.registry import Registry
from strange_case.support.jinja import fix_path

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
        #print "self.source_path is '{}', fixed to '{}'".format(self.source_path, fix_path(self.source_path))
        try:
            template = Registry.get('jinja_environment').get_template(fix_path(self.source_path))
        except UnicodeDecodeError as e:
            e.args += "Could not process '%s' because of unicode error." % self.source_path
            raise
        return template.render(self.config, my=self, site=site)
