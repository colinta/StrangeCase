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

    def __init__(self, config, target_folder):
        self.config = config
        self.parent = None
        self.target_folder = target_folder

        self.children = []

    def generate(self, site):
        for child in self.children:
            child.generate(site)

    def all(self, everything=False, folders=False, pages=True, assets=False, processors=False, recursive=False):
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
                    ret.extend(child.all(everything, folders, pages, assets, processors, recursive))
            elif child.is_page:
                if everything or pages:
                    ret.append(child)
            elif child.is_asset:
                if everything or assets:
                    ret.append(child)
            elif child.is_processor:
                if everything or processors:
                    ret.append(child)
            elif everything:
                ret.append(child)
        return ret

    ##|
    ##|  CHILDREN
    ##|
    def append(self, child):
        if child.parent:
            child.parent.remove(child)

        child.parent = self
        self.children.append(child)

    def extend(self, children):
        for child in children:
            self.append(child)

    def index(self, child):
        return self.children.index(child)

    def remove(self, child):
        if child in self.children:
            self.children.remove(child)

    def insert(self, i, children):
        for child in children:
            if child.parent:
                child.parent.remove(child)

            child.parent = self
            self.children.insert(i, child)
            i += 1

    def config_copy(self, **kwargs):
        node_config = deepcopy(self.config)

        # not merged
        for key in ['name', 'target_name', 'type']:
            if key in node_config:
                del node_config[key]

        if kwargs:
            node_config.update(kwargs)

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
    def is_processor(self):
        return False

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

    @title.setter
    def title(self, title):
        self.config['title'] = title

    ##|
    ##|  TRAVERSAL
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

    def __setitem__(self, key, value):
        self.config[key] = value

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, key):
        if key in self.config:
            return self.config.get(key)

        for child in self.children:
            if child.name == key:
                return child

        return ''

    def __len__(self):
        return len([child for child in self.children if child.iterable])

    def __iter__(self):
        return iter([child for child in self.children if child.iterable])

    def __repr__(self, indent=''):
        return "%s(url: %s type:%s)" % (indent, self.url, str(type(self)))
