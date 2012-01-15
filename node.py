import os


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

    def __iter__(self):
        return iter(self.children)

    def __nonzero__(self):
        return True

    def __len__(self):
        return len(self.children)

    def __getattr__(self, key):
        conf = self.config.get(key)
        if conf:
            return conf
        page = self.children.get(key)
        if page:
            return page
        return None


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


class AssetPageNode(Node):
    """
    Copies a file to a destination
    """
    def __init__(self, parent, name, config, target, source):
        super(AssetPageNode, self).__init__(parent, name, config, target)
        self.source = source

    def build(self, **context):
        super(FolderNode, self).build(**context)


class TemplatePageNode(PageNode):
    """
    A TemplatePageNode object is rendered before copied to its destination
    """
    def __init__(self, parent, name, config, target, template):
        super(TemplatePageNode, self).__init__(parent, name, config, target)
        self.template = template

    def build(self, **context):
        self.config.update(self.template.context)
        content = self.template.render(context)
        with open(self.target, 'w') as dest:
            dest.write(content)
