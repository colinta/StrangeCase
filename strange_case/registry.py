

class Registry(object):
    """
    Mostly used to register processors, and ask those processors to get some nodes,
    but also acts as a global key-value store.  The Jinja environment is stored here,
    for example.
    """
    processors = {}
    misc = {}
    configurators = []

    def __new__(cls):
        raise TypeError("Don't instantiate Registry.")

    @classmethod
    def register(cls, node_type, processor):
        """
        Adds (or overrides) a processor to handle `node_type`
        """
        cls.processors[node_type] = processor

    @classmethod
    def nodes(cls, node_type, *args, **kwargs):
        """
        Returns a node, instantiating it using the proper processor,
        if it has been registered for `node_type`.
        Other raises NotImplementedError
        """
        try:
            processor = cls.processors[node_type]
        except KeyError:
            raise NotImplementedError('Unknown processor "%s"' % node_type)

        if isinstance(processor, type):  # You can pass a class object,
            return processor().process(*args, **kwargs)  # and it gets instantiated here
        else:
            return processor(*args, **kwargs)

    @classmethod
    def set(cls, key, value):
        """
        Sets a generic system global.
        """
        cls.misc[key] = value

    @classmethod
    def get(cls, key, *args):
        """
        Gets a generic system global.
        """
        return cls.misc.get(key, *args)

    @classmethod
    def add_configurator(cls, configurator):
        """
        Adds a configurator callables.
        """
        cls.configurators.append(configurator)
