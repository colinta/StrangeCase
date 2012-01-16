from jinja2 import Environment
from strange_case_jinja import YamlFrontMatterLoader, YamlFrontMatterTemplate
import os
from shutil import copy2
from extensions.markdown2_extension import Markdown2Extension
from extensions.date_extension import date


environment = Environment(extensions=[Markdown2Extension],
                          loader=YamlFrontMatterLoader(os.getcwd()),
                          )
environment.filters['date'] = date

environment.template_class = YamlFrontMatterTemplate


def check_config_first(fn):
    """
    @property methods like title() get called instead of __getattr__().  This method helps
    to make sure that self.config is checked before returning the default.
    """
    def ret(self):
        if fn.__name__ in self.config:
            return self.config[fn.__name__]
        return fn(self)
    return ret


class Node(object):
    """
    Parent class for all nodes (pages and folders)
    """

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.parent = None

    def build(self, **context):
        pass

    ##|
    ##|  "special" keys
    ##|
    @property
    @check_config_first
    def type(self):
        return 'abstract'

    @property
    @check_config_first
    def is_folder(self):
        return False

    @property
    @check_config_first
    def is_page(self):
        return False

    @property
    @check_config_first
    def is_asset(self):
        return False

    @property
    @check_config_first
    def title(self):
        return self.name.replace('_', ' ')

    @property
    def next(self):
        if not self.parent:
            return None

        iterables = [page for page in self.parent]
        index = iterables.index(self)
        if len(iterables) > index + 1:
            return iterables[index + 1]

    @property
    def prev(self):
        if not self.parent:
            return None

        iterables = [page for page in self.parent]
        index = iterables.index(self)
        if index - 1 >= 0:
            return iterables[index - 1]

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
        if self.children.get(child.name):
            raise NameError("Duplicate name %s in %s" % (child.name, self.name or '<root>'))
        self.children[child.name] = child
        self.children_list.append(child)

    def remove_child(self, child):
        if child.name in self.children:
            del self.children[child.name]

        if child in self.children_list:
            self.children_list.remove(child)

    def build(self, **context):
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder, 0755)

        for child in self.children_list:
            child.build(**context)

    def __getattr__(self, key):
        ret = super(FolderNode, self).__getattr__(key)
        if ret is not None:
            return ret

        if key in self.children:
            return self.children[key]
        return None

    def __len__(self):
        return len([child for child in self.children_list if child.iterable])

    def __iter__(self):
        return iter([child for child in self.children_list if child.iterable])

    ##|
    ##|  "special" keys
    ##|
    @property
    @check_config_first
    def type(self):
        return 'folder'

    @property
    @check_config_first
    def is_folder(self):
        return True

    def all(self, folders=False, pages=True, assets=False, recursive=False):
        """ Returns ancestors, regardless of iterability. Ignores folders by default. """
        ret = []

        for child in self.children_list:
            if child.is_folder:
                if folders:
                    ret.append(child)

                if recursive:
                    ret.extend(child.all(folders, pages))
            elif child.is_page:
                if pages:
                    ret.append(child)
            elif child.is_asset:
                if assets:
                    ret.append(child)
        return ret


class PageNode(Node):
    """
    A PageNode object is an abstract parent class for a "leaf".
    """
    def __init__(self, name, config, target):
        super(PageNode, self).__init__(name, config)
        self.target = target

    ##|
    ##|  "special" keys
    ##|
    @property
    @check_config_first
    def type(self):
        return 'page' if self.is_page else 'asset'

    @property
    @check_config_first
    def is_page(self):
        _, ext = os.path.splitext(self.target)
        return True if ext == self.html_extension else False

    @property
    @check_config_first
    def is_asset(self):
        return not self.is_page


class StaticPageNode(PageNode):
    """
    Copies a file to a destination
    """
    def __init__(self, name, config, target, path):
        super(StaticPageNode, self).__init__(name, config, target)
        self.path = path

    def build(self, **context):
        copy2(self.path, self.target)
        super(StaticPageNode, self).build(**context)


class TemplatePageNode(PageNode):
    """
    A TemplatePageNode object is rendered before copied to its destination
    """
    def __init__(self, name, config, target, path):
        super(TemplatePageNode, self).__init__(name, config, target)
        self.path = path
        self.template = environment.get_template(path)
        self.config.update(self.template.context)

    def build(self, **context):
        content = self.template.render(self.config, my=self, **context)
        with open(self.target, 'w') as dest:
            dest.write(content.encode('utf-8'))
