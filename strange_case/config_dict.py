import copy


class ConfigDict(dict):
    def __init__(self, d, parent=None):
        self.parent = parent
        super(ConfigDict, self).__init__(d)

    def update(self, other):
        super(ConfigDict, self).update(other)

    def copy(self):
        ret = ConfigDict({}, self)
        for key in self.keys():
            ret[key] = copy.deepcopy(self[key])
        return ret


def config_copy(source, parent=None):
    ret = ConfigDict({}, parent)
    for key in source.keys():
        ret[key] = copy.deepcopy(source[key])
    return ret
