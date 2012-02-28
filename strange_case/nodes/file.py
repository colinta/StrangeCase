import os
import urllib
from strange_case.nodes import Node, check_config_first


class FileNode(Node):
    """
    A FileNode object is an abstract parent class for a "leaf".
    """
    def __init__(self, config, source_path, target_folder):
        super(FileNode, self).__init__(config, target_folder)
        if not source_path:
            raise TypeError('source_path is a required argument in FileNode()')
        if not os.path.exists(source_path):
            raise TypeError('source_path "%s" does not exist in FileNode()' % source_path)
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

    def generate(self, site):
        target_path = os.path.join(self.target_folder, self.target_name)
        os.chmod(target_path, 0755)
        super(FileNode, self).generate(site)
