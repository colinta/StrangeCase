from jinja2 import Environment
from strange_case_jinja import YamlFrontMatterLoader, YamlFrontMatterTemplate
import os


env = Environment(loader=YamlFrontMatterLoader(os.getcwd()))
env.template_class = YamlFrontMatterTemplate


class Node(object):
    """
    Parent class for all nodes (pages and folders)
    """

    def __init__(self, parent, name, config):
        self.name = name
        self.parent = parent
        self.config = config

        self.children_list = []
        self.children = {}

        if parent:
            parent.add_child(self)

    def build(self, **context):
        for child in self.children_list:
            child.build(**context)

    def add_child(self, child):
        if not self.children.get(child.name):
            self.children[child.name] = child
            self.children_list.append(child)

    def __nonzero__(self):
        return True

    def __len__(self):
        return len(self.children_list)

    def __iter__(self):
        return iter(self.children_list)

    def __getattr__(self, key):
        conf = self.config.get(key)
        if conf:
            return conf
        page = self.children.get(key)
        if page:
            return page
        return None

    def __repr__(self, indent=''):
        return "%s (%s)" % (self.name, str(type(self)))


class FolderNode(Node):
    """
    A FolderNode object creates itself.
    """
    def __init__(self, parent, name, config, folder):
        super(FolderNode, self).__init__(parent, name, config)
        self.folder = folder

    def build(self, **context):
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder, 0755)
        super(FolderNode, self).build(**context)


class PageNode(Node):
    """
    A PageNode object is an abstract parent class for a "leaf".
    """
    def __init__(self, parent, name, config, target):
        super(PageNode, self).__init__(parent, name, config)
        self.target = target


class AssetPageNode(PageNode):
    """
    Copies a file to a destination
    """
    def __init__(self, parent, name, config, target, path):
        super(AssetPageNode, self).__init__(parent, name, config, target)
        self.path = path

    def build(self, **context):
        super(FolderNode, self).build(**context)


class TemplatePageNode(AssetPageNode):
    """
    A TemplatePageNode object is rendered before copied to its destination
    """
    def __init__(self, parent, name, config, target, path):
        super(TemplatePageNode, self).__init__(parent, name, config, target, path)
        self.template = env.get_template(path)

        self.config.update(self.template.context)

    def build(self, **context):
        content = self.template.render(self.config, **context)
        with open(self.target, 'w') as dest:
            dest.write(content)
