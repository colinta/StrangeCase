import os
from strange_case.nodes import PageNode
from strange_case.registry import Registry


class JinjaNode(PageNode):
    """
    A JinjaNode object is rendered before copied to its destination
    """
    def generate(self, site):
        content = self.render(site)

        target_path = os.path.join(self.target_folder, self.target_name)
        with open(target_path, 'w') as dest:
            dest.write(content.encode('utf-8'))
            self.files_written.append(target_path)

        super(JinjaNode, self).generate(site)

    def render(self, site=None):
        try:
            template = Registry.get('jinja_environment').get_template(self.source_path)
        except UnicodeDecodeError:
            print "Could not process '%s' because of unicode error." % self.source_path
            raise
        return template.render(self.config, my=self, site=site)
