from strange_case.nodes import FileNode, check_config_first


class PageNode(FileNode):
    """
    I'm not sure what should be done in this class.  But dibs!
    """
    @property
    @check_config_first
    def is_page(self):
        if self.config.get('is_asset') is not None:
            return not self.is_asset
        return True
