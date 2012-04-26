from strange_case.nodes import *


class TestParentNode(Node):
    def __init__(self):
        super(TestParentNode, self).__init__(config={'test_it': 'test_it'},
                                  target_folder='target')

    @property
    @check_config_first
    def test_it(self):
        return 'WRONG'

    @property
    @check_config_first
    def test_another(self):
        return 'RIGHT'


class TestChildNode(TestParentNode):
    pass


def test_check_config_first():
    n = TestParentNode()
    assert n.test_it == 'test_it'
    assert n.test_another == 'RIGHT'


def test_node_defaults():
    n = TestParentNode()
    assert n.config == {'test_it': 'test_it'}
    assert n.parent == None
    assert n.children == []


def test_parent_child_relationship():
    p = TestParentNode()
    c = TestChildNode()
    p.append(c)
    assert len(p.children) == 1
    assert c.parent == p
