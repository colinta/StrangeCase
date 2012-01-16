from jinja2 import Environment
from strange_case_jinja import YamlFrontMatterLoader, YamlFrontMatterTemplate
import os
from shutil import copy2


env = Environment(loader=YamlFrontMatterLoader(os.getcwd()))
env.template_class = YamlFrontMatterTemplate


class Node(object):
    """
    Parent class for all nodes (pages and folders)
    """

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def build(self, **context):
        pass
    ##|
    ##|  "special" keys
    ##|
    @property
    def title(self):
        return self.name.replace('_', ' ')

    def __nonzero__(self):
        return True

    def __getattr__(self, key):
        if key == "name":
            return self.name

        conf = self.config.get(key)
        if conf:
            return conf
        return None

    def __repr__(self, indent=''):
        return "%s (%s)" % (self.name, str(type(self)))


class FolderNode(Node):
    """
    A FolderNode object creates itself.
    """
    def __init__(self, name, config, folder):
        super(FolderNode, self).__init__(name, config)
        self.folder = folder

        self.children_list = []
        self.children = {}

    def add_child(self, child):
        if child.parent:
            child.parent.remove_child(child)

        child.parent = self
        if not self.children.get(child.name):
            self.children[child.name] = child
            self.children_list.append(child)

    def remove_child(self, child):
        if self.children.get(child.name):
            del self.children[child.name]

        if child in self.children_list:
            self.children_list.remove(child)

    def build(self, **context):
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder, 0755)

        for child in self.children_list:
            child.build(**context)

    ##|
    ##|  "special" keys
    ##|
    @property
    def next(self):
        if not self.parent:
            return None
        index = self.parent.children_list.index(self)
        if len(self.parent.children_list) > index + 1:
            return self.parent.children_list[index + 1]

    @property
    def prev(self):
        if not self.parent:
            return None
        index = self.parent.children_list.index(self)
        if index - 1 >= 0:
            return self.parent.children_list[index - 1]

    def __getattr__(self, key):
        ret = super(FolderNode, self).__getattr__(key)
        if ret is not None:
            return ret

        page = self.children.get(key)
        if page:
            return page
        return None

    def __len__(self):
        return len(self.children_list)

    def __iter__(self):
        return iter(self.children_list)


class PageNode(Node):
    """
    A PageNode object is an abstract parent class for a "leaf".
    """
    def __init__(self, name, config, target):
        super(PageNode, self).__init__(name, config)
        self.target = target


class AssetPageNode(PageNode):
    """
    Copies a file to a destination
    """
    def __init__(self, name, config, target, path):
        super(AssetPageNode, self).__init__(name, config, target)
        self.path = path

    def build(self, **context):
        copy2(self.path, self.target)
        super(AssetPageNode, self).build(**context)


class TemplatePageNode(PageNode):
    """
    A TemplatePageNode object is rendered before copied to its destination
    """
    def __init__(self, name, config, target, path):
        super(TemplatePageNode, self).__init__(name, config, target)
        self.path = path
        self.template = env.get_template(path)
        self.config.update(self.template.context)

    def build(self, **context):
        content = self.template.render(self.config, my=self, **context)
        with open(self.target, 'w') as dest:
            dest.write(content)
        super(TemplatePageNode, self).build(**context)
