import copy


class ConfigDict(dict):
    def __init__(self, d, parent=None):
        self.parent = parent
        super(ConfigDict, self).__init__(d)

    def update(self, other):
        super(ConfigDict, self).update(other)

    def copy(self, all=False):
        return config_copy(source=self, parent=self, all=all)

    def __setitem__(self, key, value):
        if key.endswith(' ->'):
            try:
                del self[key[:-3]]
            except KeyError:
                pass
        return super(ConfigDict, self).__setitem__(key, value)


def config_copy(source, parent=None, all=False):
    ret = ConfigDict({}, parent)
    for key in source.keys():
        ret[key] = copy.deepcopy(source[key])

    # not merged
    if not all:
        for key in source['dont_inherit']:
            if key in ret:
                del ret[key]
    return ret
