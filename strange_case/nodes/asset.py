import os
from shutil import copy2
from strange_case.nodes import FileNode


class AssetNode(FileNode):
    """
    Copies a file to a destination
    """
    def generate(self, site):
        target_path = os.path.join(self.target_folder, self.target_name)
        copy2(self.source_path, target_path)

        super(AssetNode, self).generate(site)
