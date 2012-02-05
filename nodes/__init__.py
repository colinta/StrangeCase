import os
from shutil import copy2
import urllib
from registry import Registry
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


class FolderNode(Node):
    """
    A FolderNode object creates itself in the target folder (mkdir).
    """
    def __init__(self, config, source_path, target_folder):
        super(FolderNode, self).__init__(config, target_folder)
        self.source_path = source_path

    def generate(self, site):
        folder = os.path.join(self.target_folder, self.target_name)
        if not os.path.isdir(folder):
            os.mkdir(folder, 0755)
        super(FolderNode, self).generate(site)

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

    def __repr__(self, indent=''):
        ret = super(FolderNode, self).__repr__(indent)
        indent += ' '
        for child in self.children:
            ret += "\n" + child.__repr__(indent)
        return ret


class RootFolderNode(FolderNode):
    """
    A RootFolderNode object does not append a target_name
    """
    @property
    def url(self):
        return '/'

    def generate(self):
        """
        This is the only Node.generate method that doesn't require the 'site' argument.  it *is* the site arqument!
        """
        folder = self.target_folder
        if not os.path.isdir(folder):
            os.mkdir(folder, 0755)

        # before generation, give
        # processor "nodes" their
        # chance to disappear
        processors = self.all(processors=True, pages=False, recursive=True)
        while len(processors):
            for child in processors:
                child.populate(self)
            processors = self.all(processors=True, pages=False, recursive=True)

        for child in self.children:
            child.generate(self)


class Processor(Node):
    """
    Look at *this* nifty node class.  It masquerades as a node so
    that it can be placed in the site tree, but later it modifies the
    tree to include other nodes.  Neat!
    """
    @property
    @check_config_first
    def is_processor(self):
        return True

    ##|
    ##|  POPULATING METHODS              |##
    ##|                                  |##
    def populate(self, site):
        raise NotImplementedError("Your processor \"" + self.__class__.__name__ + "\" should implement populate(), and don't call super()")

    def remove_self(self):
        """
        Removes self from its parent's children
        """
        if self.parent:
            self.parent.remove(self)

    def replace_with(self, children):
        """
        Removes self from its parent's children
        """
        if self.parent:
            idx = self.parent.index(self)
            self.parent.insert(idx, children)
            self.remove_self()


class FileNode(Node):
    """
    A FileNode object is an abstract parent class for a "leaf".
    """
    def __init__(self, config, source_path, target_folder):
        super(FileNode, self).__init__(config, target_folder)
        if not source_path or not os.path.exists(source_path):
            raise TypeError('source_path is a required argument in FileNode()')
        self.source_path = source_path

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
        target_path = os.path.join(self.target_folder, self.target_name)
        copy2(self.source_path, target_path)

        super(AssetNode, self).generate(site)


class PageNode(FileNode):
    """
    I'm not sure what should be done in this class.  But dibs!
    """
    pass


class JinjaNode(PageNode):
    """
    A JinjaNode object is rendered before copied to its destination
    """
    def generate(self, site):
        template = Registry.get('jinja_environment').get_template(self.source_path)
        content = template.render(self.config, my=self, site=site)

        target_path = os.path.join(self.target_folder, self.target_name)
        with open(target_path, 'w') as dest:
            dest.write(content.encode('utf-8'))

        super(JinjaNode, self).generate(site)
