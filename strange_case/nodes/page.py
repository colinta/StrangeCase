from strange_case.nodes import FileNode, check_config_first


class PageNode(FileNode):
    """
    I'm not sure what should be done in this class.  But dibs!
    """
    @property
    @check_config_first
    def is_page(self):
        return True
