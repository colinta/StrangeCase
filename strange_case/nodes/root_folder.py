import os
from strange_case.nodes import FolderNode


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
        processors = self.processors(recursive=True)
        while len(processors):
            for child in processors:
                child.populate(self)
            processors = self.processors(recursive=True)

        for child in self.children:
            child.generate(self)
