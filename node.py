import os
from shutil import copy2
import urllib
from copy import deepcopy


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

    def generate(self, site):
        raise NotImplementedError("Your node should implement generate(), and don't call super() unless you're extending a \"leaf\" class like FolderNode, AssetNode, or JinjaNode")

    def config_copy(self):
        node_config = deepcopy(self.config)

        # not merged
        if 'name' in node_config:
            del node_config['name']
        if 'target_name' in node_config:
            del node_config['target_name']

        return node_config

    ##|                        |##
    ##|  "special" properties  |##
    ##|                        |##
    @property
    def url(self):
        url = self.target_name
        if self.parent:
            url = self.parent.url + url  # you might be tempted to add a '/' here, but you'd be wrong!  (folders add a slash to themselves)
        return urllib.quote(url)

    @property
    @check_config_first
    def iterable(self):
        # if this file is an index file, it will not be included in the pages iterator.
        # all other pages and assets are iterable.
        if self.target_name != self.config['index']:
            return True
        return False

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
        return self.name.titlecase()

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
        return "(url: %s type:%s)" % (self.url, str(type(self)))


class FolderNode(Node):
    """
    A FolderNode object creates itself in the target folder (mkdir).
    """
    def __init__(self, config, source, folder):
        super(FolderNode, self).__init__(config)
        self.source = source
        self.folder = folder

        self.children = []

    def generate(self, site):
        folder = os.path.join(self.folder, self.target_name)
        if not os.path.isdir(folder):
            os.mkdir(folder, 0755)

        for child in self.children:
            child.generate(site)

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

    ##|                        |##
    ##|  "special" properties  |##
    ##|                        |##
    @property
    def url(self):
        url = super(FolderNode, self).url
        return url + '/'

    @property
    @check_config_first
    def type(self):
        return 'folder'

    @property
    @check_config_first
    def is_folder(self):
        return True

    def all(self, everything=False, folders=False, pages=True, assets=False, recursive=False):
        """
        Returns descendants, ignoring iterability. Folders, assets, and
        pages can all be included or excluded as the case demands.  An easy
        trick is to call all(True), which will return everything, recursively.
        """
        ret = []

        for child in self.children:
            if child.is_folder:
                if everything or folders:
                    ret.append(child)

                if everything or recursive:
                    ret.extend(child.all(everything, folders, pages, assets, recursive))
            elif child.is_page:
                if everything or pages:
                    ret.append(child)
            elif child.is_asset:
                if everything or assets:
                    ret.append(child)
        return ret


class RootFolderNode(FolderNode):
    """
    A RootFolderNode object does not append a target_name
    """
    def __init__(self, config, source, folder):
        super(RootFolderNode, self).__init__(config, source, folder)

    @property
    def url(self):
        return '/'

    def generate(self):
        """
        This is the only Node.generate method that doesn't require the 'site' argument.  'self' *is* the site arqument!
        """
        folder = self.folder
        if not os.path.isdir(folder):
            os.mkdir(folder, 0755)

        for child in self.children:
            child.generate(self)


class FileNode(Node):
    """
    A FileNode object is an abstract parent class for a "leaf".
    """
    def __init__(self, config, source, target):
        super(FileNode, self).__init__(config)
        self.source = source
        self.target = target

    ##|                        |##
    ##|  "special" properties  |##
    ##|                        |##
    @property
    def url(self):
        if self.target_name == self.config['index']:
            url = ''
        else:
            url = self.target_name

        if self.parent:
            url = self.parent.url + url

        return urllib.quote(url)

    @property
    @check_config_first
    def type(self):
        return 'page' if self.is_page else 'asset'

    @property
    @check_config_first
    def is_page(self):
        _, ext = os.path.splitext(self.target_name)
        return True if ext == self.html_extension else False

    @property
    @check_config_first
    def is_asset(self):
        return not self.is_page


class AssetNode(FileNode):
    """
    Copies a file to a destination
    """
    def generate(self, site):
        target = os.path.join(self.target, self.target_name)
        copy2(self.source, target)


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

    def generate(self, site):
        template = self.get_environment().get_template(self.source)
        content = template.render(self.config, my=self, site=site)

        target = os.path.join(self.target, self.target_name)
        with open(target, 'w') as dest:
            dest.write(content.encode('utf-8'))
