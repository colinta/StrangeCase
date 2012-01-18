from node import *

##|
##|  The long and short of it: extend Processor and implement process().  return (nodes, ...).
##|


class Processor(object):
    processors = {}

    @classmethod
    def register(cls, name, processor):
        cls.processors[name] = processor

    @classmethod
    def registerDefault(cls, name, processor):
        if not name in cls.processors:
            cls.processors[name] = processor

    @classmethod
    def get(cls, name, *args, **kwargs):
        try:
            processor = cls.processors[name]
            return processor().process(*args, **kwargs)
        except KeyError:
            raise NotImplementedError('Unknown processor "%s"' % processor)


class FolderProcessor(Processor):
    def process(self, config, source, target):
        return (FolderNode(config, source, target), )


class AssetProcessor(Processor):
    def process(self, config, source, target):
        return (StaticNode(config, source, target), )


class PageProcessor(Processor):
    def process(self, config, source, target):
        return (JinjaNode(config, source, target), )


Processor.registerDefault('folder', FolderProcessor)
Processor.registerDefault('asset', AssetProcessor)
Processor.registerDefault('page', PageProcessor)
