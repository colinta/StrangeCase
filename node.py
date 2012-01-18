import os
from shutil import copy2


def check_config_first(fn):
    """
    @property methods like title() get called instead of __getattr__().  This method
    makes sure that self.config is checked before returning the default.
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

    def __init__(self, config):
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

    ##|
    ##|  TRAVERSAL
    ##|   see FolderNode for the children property
    ##|
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
        if key in self.config:
            return self.config.get(key)
        return None

    def __repr__(self, indent=''):
        return "%s (%s)" % (self.name, str(type(self)))


class FolderNode(Node):
    """
    A FolderNode object creates itself in the target folder (mkdir).
    """
    def __init__(self, config, source, folder):
        super(FolderNode, self).__init__(config)
        self.source = source
        self.folder = folder

        self.children = []

    def append(self, child):
        if child.parent:
            child.parent.remove(child)

        child.parent = self
        self.children.append(child)

    def extend(self, children):
        for child in children:
            self.append(child)

    def remove(self, child):
        if child in self.children:
            self.children.remove(child)

    def build(self, **context):
        if not os.path.isdir(self.folder):
            os.mkdir(self.folder, 0755)

        for child in self.children:
            child.build(**context)

    def __getattr__(self, key):
        ret = super(FolderNode, self).__getattr__(key)
        if ret is not None:
            return ret

        for child in self.children:
            if child.name == key:
                return child
        return None

    def __len__(self):
        return len([child for child in self.children if child.iterable])

    def __iter__(self):
        return iter([child for child in self.children if child.iterable])

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
        """ Returns descendants, ignoring iterability. Folders, assets, and
            pages can all be included or excluded as the case demands."""
        ret = []

        for child in self.children:
            if child.is_folder:
                if folders:
                    ret.append(child)

                if recursive:
                    ret.extend(child.all(folders, pages, assets, recursive))
            elif child.is_page:
                if pages:
                    ret.append(child)
            elif child.is_asset:
                if assets:
                    ret.append(child)
        return ret


class FileNode(Node):
    """
    A FileNode object is an abstract parent class for a "leaf".
    """
    def __init__(self, config, source, target):
        super(FileNode, self).__init__(config)
        self.source = source
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


class StaticNode(FileNode):
    """
    Copies a file to a destination
    """
    def __init__(self, config, source, target):
        super(StaticNode, self).__init__(config, source, target)

    def build(self, **context):
        copy2(self.source, self.target)
        super(StaticNode, self).build(**context)


class JinjaNode(FileNode):
    """
    A JinjaNode object is rendered before copied to its destination
    """
    ENVIRONMENT = None

    @classmethod
    def get_environment(cls):
        if not cls.ENVIRONMENT:
            ENVIRONMENT = None
            try:
                from config import ENVIRONMENT
            except ImportError:
                if not ENVIRONMENT:
                    from strange_case_jinja import StrangeCaseEnvironment
                    ENVIRONMENT = StrangeCaseEnvironment()
            cls.ENVIRONMENT = ENVIRONMENT
        return cls.ENVIRONMENT

    def __init__(self, config, source, target):

        super(JinjaNode, self).__init__(config, source, target)
        self.template = self.get_environment().get_template(source)
        if 'url' in self.template.context:
            raise KeyError('You cannot specify "url" in yaml front matter.  It is determined by its location in the tree, and the target_names of itself and all its parents')
        self.config.update(self.template.context)

    def build(self, **context):
        content = self.template.render(self.config, my=self, **context)
        with open(self.target, 'w') as dest:
            dest.write(content.encode('utf-8'))
