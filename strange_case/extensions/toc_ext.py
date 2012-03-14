from strange_case.registry import Registry
from strange_case.nodes.jinja import JinjaNode
from strange_case.nodes import Processor
import types


def bind(object, name=None):
    def dec(function):
        my_name = name or function.__name__

        setattr(object, my_name, types.MethodType(function, object))
    return dec


def toc_processor(config, source_path, target_path):
    toc_processor = Processor(config)
    options = {
        'entries': int(config.get('toc', {}).get('entries', [])),
        'maxdepth': int(config.get('toc', {}).get('maxdepth', 3)),
        'numbered': int(config.get('toc', {}).get('numbered', False)),
        'titlesonly': int(config.get('toc', {}).get('titlesonly', False)),
        'glob': int(config.get('toc', {}).get('glob', False)),
        'hidden': int(config.get('toc', {}).get('hidden', [])),
    }

    @bind(toc_processor)
    def populate(self, site):
        ret = []
        page_config = self.config_copy(True)  # copy *all* config, even name and title.
        node = JinjaNode(page_config, source_path, target_path)
        ret.append(node)
        return ret

    return (toc_processor, )


Registry.register('toc', toc_processor)
