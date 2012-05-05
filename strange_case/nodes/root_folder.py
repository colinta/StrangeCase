import os
from strange_case.nodes import FolderNode


class RootFolderNode(FolderNode):
    """
    A RootFolderNode object does not append a target_name
    """
    @property
    def url(self):
        return self.config['root_url']

    def generate(self):
        """
        This is the only Node.generate method that doesn't require the 'site'
        argument.  It *is* the site arqument!
        """
        folder = self.target_folder
        if not os.path.isdir(folder):
            os.mkdir(folder)
        self.files_tracked.append(self.source_path)
        self.files_written.append(folder)

        # before generation, give
        # processor "nodes" their
        # chance to disappear
        processors = self.processors(recursive=True)
        while len(processors):
            for child in processors:
                ret = child.populate(self)
                if ret is not None:
                    child.replace_with(ret)

            processors = self.processors(recursive=True)

        for child in self.children:
            child.generate(self)
