import urllib.parse

from strange_case.config_dict import config_copy
from strange_case.registry import Registry


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

    # stores the tracked files, which is used to write the timestamps file
    files_tracked = []
    # stores a list of files written, so that stale files can be removed
    files_written = []

    def __init__(self, config, target_folder):
        self.config = config
        self.parent = None
        self.target_folder = target_folder

        self.children = []

    def generate(self, site):
        for child in self.children:
            child.generate(site)

    def all(self, recursive=False, folders=None, pages=None, assets=None, processors=None):
        """
        Returns descendants, ignoring iterability. Folders, assets, and
        pages can all be included or excluded as the case demands.

        If you specify any of folders, pages, assets or processors, only those objects
        will be returned. Otherwise all node types will be returned.

        recursive defaults to False.  Since it is in first position, calling `all(True)` is
        the same as `all(recursive=True)`.
        """
        everything = folders is None and pages is None and assets is None and processors is None

        ret = []
        for child in self.children:
            if everything:
                ret.append(child)
            elif folders and child.is_folder:
                ret.append(child)
            elif pages and child.is_page:
                ret.append(child)
            elif assets and child.is_asset:
                ret.append(child)
            elif processors and child.is_processor:
                ret.append(child)

            if child.is_folder and recursive:
                ret.extend(child.all(recursive, folders, pages, assets, processors))
        return ret

    def iter_pages(self, recursive=False):
        return iter([child for child in self.pages(recursive) if child.iterable])

    def iter_folders(self, recursive=False):
        return iter([child for child in self.folders(recursive) if child.iterable])

    def iter_assets(self, recursive=False):
        return iter([child for child in self.assets(recursive) if child.iterable])

    def pages(self, recursive=False):
        return self.all(recursive=recursive, pages=True)

    def folders(self, recursive=False):
        return self.all(recursive=recursive, folders=True)

    def assets(self, recursive=False):
        return self.all(recursive=recursive, assets=True)

    def files(self, recursive=False):
        return self.all(recursive=recursive, pages=True, assets=True)

    def processors(self, recursive=False):
        return self.all(recursive=recursive, processors=True)

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

    def remove(self, child):
        if child.parent == self:
            child.parent = None
        if child in self.children:
            self.children.remove(child)

    def insert(self, i, child_or_children):
        if isinstance(child_or_children, list) or isinstance(child_or_children, tuple):
            children = child_or_children
        else:
            children = [child_or_children]

        for child in children:
            if child.parent:
                child.parent.remove(child)

            child.parent = self
            self.children.insert(i, child)
            i += 1

    ##|
    ##|  TRAVERSAL
    ##|
    @property
    def siblings(self):
        """
        Returns a list of siblings.  Does not include the index page of the parent folder.
        """
        if not self.parent:
            return self.iterable and [self] or []

        return [page for page in self.parent]

    @property
    def ancestors(self):
        """
        Returns the list of ancestors, top-most first.
        """
        current = self
        ret = []
        while current.parent:
            try:
                if current.parent.index != self:
                    ret.insert(0, current.parent.index)
            except AttributeError:
                ret.insert(0, current.parent)
            current = current.parent
        return ret

    @property
    def next(self):
        """
        Returns the next node, or None if this is the last node or if this node does not
        have a parent.
        """
        if not self.parent:
            return None

        iterables = [page for page in self.parent]
        index = iterables.index(self)
        if len(iterables) > index + 1:
            return iterables[index + 1]

    @property
    def prev(self):
        """
        Returns the previous node, or None if this is the first node or if this node does not
        have a parent.
        """
        if not self.parent:
            return None

        iterables = [page for page in self.parent]
        index = iterables.index(self)
        if index - 1 >= 0:
            return iterables[index - 1]

    ##|
    ##|  CONFIG COPY
    ##|
    def config_copy(self, all=False, **kwargs):
        node_config = config_copy(self.config, self, all=all)

        if kwargs:
            node_config.update(kwargs)

        return node_config

    ##|                        |##
    ##|  "special" properties  |##
    ##|                        |##
    @property
    def url(self):
        if self.parent:
            prefix = self.parent.url
        else:
            prefix = '/'

        url = self.config.get('url', urllib.parse.quote(self.target_name))

        return prefix + url

    @property
    @check_config_first
    def index(self):
        """
        If the node contains a child that `is_index`, this method returns that
        page.
        """
        for page in self.children:
            if page.config.get('is_index'):
                return page
        raise AttributeError('index')

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

    ##|
    ##|  OBJECT-MODEL STUFF
    ##|
    def __bool__(self):
        return True

    def __getitem__(self, key):
        if isinstance(key, int) or isinstance(key, slice):
            return [child for child in self.children if child.iterable][key]
        else:
            try:
                return self.__getattribute__(key)
            except AttributeError:
                pass

            try:
                return self.__getattr__(key)
            except AttributeError:
                pass

        return None

    def __getattr__(self, key):
        if key == 'config':
            return {}

        if key in self.config:
            return self.config.get(key)

        child_by_name = [child for child in self.children if child.name == key]
        if len(child_by_name) > 1:
            raise KeyError('There are multiple results for the node named "{0}" '
                'in folder "{1}"'.format(key, self.name))
        elif child_by_name:
            return child_by_name[0]

        # look for a "pointer" attribute
        if not key.endswith(' ->'):
            try:
                ret = self[key + ' ->']
                path = ret.split('.')
                assert path.pop(0) == 'site'
                search_in = Registry.get('root')
                while path:
                    part = path.pop(0)
                    search_in = search_in[part]
                return search_in
            except AttributeError:
                pass

        raise AttributeError(key)

    def __len__(self):
        return len([child for child in self.children if child.iterable])

    def __iter__(self):
        return iter([child for child in self.children if child.iterable])

    def __contains__(self, obj):
        return obj in self.children

    def __str__(self, indent=''):
        return self.url

    def __repr__(self, indent=''):
        return "%s<url: %s type:%s>" % (indent, self.config.get('url', 'None'), str(type(self)))
