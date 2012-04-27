

class Registry(object):
    """
    Mostly used to register processors, and ask those processors to get some nodes,
    but also acts as a global key-value store.  The Jinja environment is stored here,
    for example.
    """
    processors = {}
    file_types = []
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
    def associate(cls, node_type, globs):
        """
        Assigns a default type to files that match `globs`
        """
        cls.file_types.append((node_type, globs))

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

    @classmethod
    def configurate(cls, source_file, config):
        configurators = Registry.configurators
        # Run the config through each configurator.
        # If a configurator returns a falsey
        # value, the node will be ignored.
        for configurator in configurators:
            config = configurator(source_file, config)
            if not config:
                return
        return config
