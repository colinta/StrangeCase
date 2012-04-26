from strange_case.tests import get_test_file
from strange_case.nodes import *


class TestParentNode(Node):
    def __init__(self, name='test'):
        config = {
            'test_it': 'test_it',
            'target_name': name,
            'name': name,
        }
        super(TestParentNode, self).__init__(config=config,
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


class TestPageNode(PageNode):
    def __init__(self, name):
        config = {
            'target_name': name,
            'name': name,
        }
        super(TestPageNode, self).__init__(config=config,
                                  source_path=get_test_file('a_folder/a_file.txt'),
                                  target_folder='target')


class TestIndexNode(PageNode):
    def __init__(self, name):
        config = {
            'is_index': True,
            'target_name': name,
            'name': name,
        }
        super(TestIndexNode, self).__init__(config=config,
                                  source_path=get_test_file('a_folder/a_file.txt'),
                                  target_folder='target')


def test_check_config_first():
    n = TestParentNode()
    assert n.test_it == 'test_it'
    assert n.test_another == 'RIGHT'


def test_node_defaults():
    n = TestParentNode()
    assert n.config == {'test_it': 'test_it', 'target_name': 'test', 'name': 'test'}
    assert n.parent == None
    assert n.children == []


def test_parent_child_relationship():
    p = TestParentNode()
    c = TestChildNode()
    p.append(c)
    assert len(p.children) == 1
    assert c.parent == p
    p.remove(c)
    assert len(p.children) == 0
    assert c.parent == None

    p = TestParentNode()
    c1 = TestChildNode()
    c2 = TestChildNode()
    p.extend([c1, c2])
    assert len(p.children) == 2
    assert c1.parent == p
    assert c2.parent == p
    c3 = TestChildNode()
    p.insert(0, c3)
    assert p.children == [c3, c1, c2]
    assert c3.parent == p
    c4 = TestChildNode()
    c5 = TestChildNode()
    p.insert(1, [c4, c5])
    assert p.children == [c3, c4, c5, c1, c2]
    assert c4.parent == p


def test_contains_and_len_and_iter():
    p = TestParentNode('p')

    index = TestIndexNode('index')  # not iterable
    c1 = TestChildNode('c1')
    c2 = TestChildNode('c2')
    c3 = TestChildNode('c3')
    p.extend([index, c1, c2, c3])

    assert list(n for n in p) == [c1, c2, c3]
    assert len(p) == 3  # index is not iterable
    assert c1 in p
    assert c2 in p
    assert c3 in p
    assert index in p


def test_siblings():
    """
    - p1
      - c1
      - c2
      - c3
      - p2
        - c4
        - c5 (is_index: true, not iterable)
    """
    p1 = TestParentNode('p1')
    p2 = TestParentNode('p2')

    c1 = TestChildNode('c1')
    c2 = TestChildNode('c2')
    c3 = TestChildNode('c3')
    p1.extend([c1, c2, c3, p2])

    c4 = TestChildNode('c4')
    c5 = TestIndexNode('c5')
    p2.extend([c4, c5])

    assert len(p1.children) == 4
    assert c1.parent == p1
    assert c2.parent == p1
    assert c3.parent == p1
    assert p2.parent == p1

    assert len(p2.children) == 2
    assert c4.parent == p2
    assert c5.parent == p2

    print c1.ancestors
    assert c1.siblings == [c1, c2, c3, p2]
    assert c1.next == c2
    assert c2.next == c3
    assert c3.next == p2
    assert p2.next == None
    assert c1.prev == None
    assert c2.prev == c1
    assert c3.prev == c2
    assert p2.prev == c3

    print c4.ancestors
    assert c4.siblings == [c4]


def test_ancestors():
    """
    - p1
      - i1 (is_index: true, not iterable)
      - p2
        - i2 (is_index: true, not iterable)
        - p3
          - c
    """
    p1 = TestParentNode('p1')
    p2 = TestParentNode('p2')
    p3 = TestParentNode('p3')
    i1 = TestIndexNode('i1')
    i2 = TestIndexNode('i2')
    c = TestChildNode('c')
    p1.extend([i1, p2])
    p2.extend([i2, p3])
    p3.append(c)
    print c.ancestors
    assert c.ancestors == [i1, i2, c]


def test_config_copy():
    config = {
        'a': 'a',
        'b': 'b',
        'c': 'c',
        'd': 'd',
        'e': 'e',
        'f': 'f',
        'dont_inherit': ['a', 'b', 'c'],
    }
    n = Node(config, 'source')
    copy = n.config_copy()
    assert copy == {
        'd': 'd',
        'e': 'e',
        'f': 'f',
        'dont_inherit': ['a', 'b', 'c'],
    }


def test_getitem_and_getattr():
    from strange_case.registry import Registry
    config = {
        'key': 'value',
        'friend ->': 'site.bob.joe'
    }
    n = Node(config, 'node')
    Registry.set('root', n)
    config = {
        'name': 'bob',
    }
    bob = Node(config, 'bob')
    n.append(bob)

    config = {
        'name': 'joe',
    }
    joe = Node(config, 'joe')
    bob.append(joe)

    assert n['key'] == 'value'
    assert n.key == 'value'
    assert n['bob'] == bob
    assert n.bob == bob
    assert n.friend == joe
