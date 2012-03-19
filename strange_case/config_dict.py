import copy


class ConfigDict(dict):
    def __init__(self, d, parent=None):
        self.parent = parent
        super(ConfigDict, self).__init__(d)


def config_copy(source, parent=None):
    ret = ConfigDict({}, parent)
    for key in source.keys():
        ret[key] = copy.deepcopy(source[key])
    return ret
