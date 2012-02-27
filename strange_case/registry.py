

class Registry(object):
    """
    Mostly used to register processors, and ask those processors to get some nodes,
    but also acts as a global key-value store.  The Jinja environment is stored here,
    for example.
    """
    processors = {}
    misc = {}

    def __new__(cls):
        raise TypeError("Don't instantiate Registry.")

    @classmethod
    def register(cls, name, processor):
        cls.processors[name] = processor

    @classmethod
    def node(cls, name, *args, **kwargs):
        try:
            processor = cls.processors[name]

            if isinstance(processor, type):  # You can pass a class object,
                return processor().process(*args, **kwargs)  # and it gets instantiated here
            else:
                return processor(*args, **kwargs)
        except KeyError:
            raise NotImplementedError('Unknown processor "%s"' % name)

    @classmethod
    def set(cls, key, value):
        cls.misc[key] = value

    @classmethod
    def get(cls, key, *args):
        return cls.misc.get(key, *args)
