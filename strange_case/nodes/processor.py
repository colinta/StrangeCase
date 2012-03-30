from strange_case.nodes import Node, check_config_first


class Processor(Node):
    """
    Look at *this* nifty node class.  It masquerades as a node so
    that it can be placed in the site tree, but later it modifies the
    tree to include other nodes.  Neat!
    """
    def __init__(self, config, target_folder=None):
        super(Processor, self).__init__(config, target_folder)

    @property
    @check_config_first
    def is_processor(self):
        return True

    @property
    @check_config_first
    def iterable(self):
        return False

    ##|
    ##|  POPULATING METHODS              |##
    ##|                                  |##
    def populate(self, site):
        raise NotImplementedError("Your processor \"" + self.__class__.__name__ + "\" should implement populate(), and don't call super()")

    def remove_self(self):
        """
        Removes self from its parent's children
        """
        if self.parent:
            self.parent.remove(self)

    def replace_with(self, children):
        """
        Removes self from its parent's children
        """
        if self in self.parent.children:
            idx = self.parent.children.index(self)
            self.parent.insert(idx, children)
            self.remove_self()
        else:
            self.parent.extend(children)
