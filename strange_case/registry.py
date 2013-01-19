

class Registry(object):
    """
    Mostly used to register processors, and ask those processors to get some nodes,
    but also acts as a global key-value store.  The Jinja environment is stored here,
    for example.
    """
    processors = {}
    listeners = {}
    file_types = []
    page_types = {}
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
    def listen(cls, event, callable):
        """
        Adds a listener to `event`
        """
        cls.listeners[event] = cls.listeners.get(event, []) + [callable]

    @classmethod
    def trigger(cls, event, *args, **kwargs):
        """
        Adds a listener to `event`
        """
        for callable in cls.listeners.get(event, []):
            callable(*args, **kwargs)

    @classmethod
    def associate(cls, node_type, globs):
        """
        Assigns a default type to files that match `globs`
        """
        cls.file_types.append((node_type, globs))

    @classmethod
    def register_engine(cls, engine_name):
        """
        Class decorator that associates a node class with a page_type
        """
        def decorator(node_type):
            cls.page_types[engine_name] = node_type
            return node_type
        return decorator

    @classmethod
    def get_engine(cls, engine_name):
        return cls.page_types[engine_name]

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
    def reset_configurators(cls):
        """
        Adds a configurator callables.
        """
        cls.configurators = []

    @classmethod
    def add_configurator(cls, configurator):
        """
        Adds a configurator callables.
        """
        cls.configurators.append(configurator)
