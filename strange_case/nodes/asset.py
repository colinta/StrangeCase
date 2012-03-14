from shutil import copy2
from strange_case.nodes import FileNode


class AssetNode(FileNode):
    """
    Copies a file to a destination
    """
    def generate_file(self, site, source_path, target_path):
        copy2(source_path, target_path)
        self.files_written.append(target_path)
