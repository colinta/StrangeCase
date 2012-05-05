import os
from strange_case.nodes import Node, check_config_first


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
            os.mkdir(folder)

        # folders can be 'virtual', like the category folder
        if self.source_path and os.path.exists(self.source_path):
            self.files_tracked.append(self.source_path)
        self.files_written.append(folder)
        super(FolderNode, self).generate(site)

    ##|                        |##
    ##|  "special" properties  |##
    ##|                        |##
    @property
    def url(self):
        return super(FolderNode, self).url + '/'

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
        indent += '    '
        for child in self.children:
            ret += "\n" + child.__repr__(indent)
        return ret
