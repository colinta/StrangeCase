import os
from strange_case.nodes import Node, check_config_first


class FileNode(Node):
    """
    A FileNode object is an abstract parent class for a file in the site folder
    that is going to be copied or rendered into the destination folder
    """
    def __init__(self, config, source_path, target_folder):
        super(FileNode, self).__init__(config, target_folder)
        if not source_path:
            raise TypeError('source_path is a required argument in FileNode()')
        if not os.path.exists(source_path):
            raise TypeError('source_path "%s" does not exist in FileNode()' % source_path)
        self.source_path = source_path

    def generate(self, site):
        target_path = os.path.join(self.target_folder, self.target_name)
        self.generate_file(site, self.source_path, target_path)
        super(FileNode, self).generate(site)

    def generate_file(self, site, source_path, target_path):
        pass

    ##|                        |##
    ##|  "special" properties  |##
    ##|                        |##
    @property
    @check_config_first
    def is_asset(self):
        return not self.is_page

    @property
    @check_config_first
    def is_page(self):
        if self.config.get('is_asset') is not None:
            return not self.is_asset
        return False

    @property
    def skip(self):
        """
        Override config to return False if target_path does not exist.
        """
        target_path = os.path.join(self.target_folder, self.target_name)
        return self.config.get('skip') and os.path.exists(target_path)
