from strange_case.tests import get_test_file
from strange_case.nodes import *
from strange_case.registry import Registry


class MockingConfigNode(Node):
    def __init__(self, name='test', addl_config={}):
        config = {
            'test_it': 'test_it',
            'target_name': name,
            'name': name,
            'iterable': True,
        }
        config.update(addl_config)
        super(MockingConfigNode, self).__init__(config=config,
                                  target_folder='target')

    @property
    @check_config_first
    def test_it(self):
        return 'WRONG'

    @property
    @check_config_first
    def test_another(self):
        return 'RIGHT'


class MockingRootNode(RootFolderNode):
    def __init__(self, name='test', addl_config={}):
        config = {
            'target_name': name,
            'name': name,
            'iterable': True,
            'root_url': '/',
        }
        config.update(addl_config)
        Registry.set('root', self)
        super(MockingRootNode, self).__init__(config=config,
                                  source_path=get_test_file('a_folder/'),
                                  target_folder='target')


class MockingFolderNode(FolderNode):
    def __init__(self, name='test', addl_config={}):
        config = {
            'target_name': name,
            'name': name,
            'url': name,
            'iterable': True,
        }
        config.update(addl_config)
        super(MockingFolderNode, self).__init__(config=config,
                                  source_path=get_test_file('a_folder/'),
                                  target_folder='target')


class MockingPageNode(PageNode):
    def __init__(self, name, addl_config={}):
        config = {
            'target_name': name,
            'name': name,
            'url': name,
            'iterable': True,
        }
        config.update(addl_config)
        super(MockingPageNode, self).__init__(config=config,
                                  source_path=get_test_file('a_folder/a_file.txt'),
                                  target_folder='target')


class MockingIndexNode(PageNode):
    def __init__(self, name, addl_config={}):
        config = {
            'target_name': name,
            'name': name,
            'url': '',
            'iterable': False,
            'is_index': True,
        }
        config.update(addl_config)
        super(MockingIndexNode, self).__init__(config=config,
                                  source_path=get_test_file('a_folder/a_file.txt'),
                                  target_folder='target')


def test_check_config_first():
    n = MockingConfigNode()
    assert n.test_it == 'test_it'
    assert n.test_another == 'RIGHT'


def test_node_defaults():
    n = MockingRootNode()
    assert n.parent == None
    assert n.children == []


def test_parent_child_relationship():
    p = MockingRootNode()
    c = MockingPageNode('c')
    p.append(c)
    assert len(p.children) == 1
    assert c.parent == p
    p.remove(c)
    assert len(p.children) == 0
    assert c.parent == None

    p = MockingRootNode()
    c1 = MockingPageNode('c1')
    c2 = MockingPageNode('c2')
    p.extend([c1, c2])
    assert len(p.children) == 2
    assert c1.parent == p
    assert c2.parent == p
    c3 = MockingPageNode('c3')
    p.insert(0, c3)
    assert p.children == [c3, c1, c2]
    assert c3.parent == p
    c4 = MockingPageNode('c4')
    c5 = MockingPageNode('c5')
    p.insert(1, [c4, c5])
    assert p.children == [c3, c4, c5, c1, c2]
    assert c4.parent == p


def test_contains_and_len_and_iter():
    p = MockingRootNode('p')

    index = MockingIndexNode('index')  # not iterable
    c1 = MockingPageNode('c1')
    c2 = MockingPageNode('c2')
    c3 = MockingPageNode('c3')
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
    p1 = MockingRootNode('p1')
    p2 = MockingRootNode('p2')

    c1 = MockingPageNode('c1')
    c2 = MockingPageNode('c2')
    c3 = MockingPageNode('c3')
    p1.extend([c1, c2, c3, p2])

    c4 = MockingPageNode('c4')
    c5 = MockingIndexNode('c5')
    p2.extend([c4, c5])

    assert len(p1.children) == 4
    assert c1.parent == p1
    assert c2.parent == p1
    assert c3.parent == p1
    assert p2.parent == p1

    assert len(p2.children) == 2
    assert c4.parent == p2
    assert c5.parent == p2

    assert c1.siblings == [c1, c2, c3, p2]
    assert c1.next == c2
    assert c2.next == c3
    assert c3.next == p2
    assert p2.next == None
    assert c1.prev == None
    assert c2.prev == c1
    assert c3.prev == c2
    assert p2.prev == c3

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
    p1 = MockingRootNode('p1')
    p2 = MockingFolderNode('p2')
    p3 = MockingFolderNode('p3')
    i1 = MockingIndexNode('i1')
    i2 = MockingIndexNode('i2')
    c = MockingPageNode('c')
    p1.extend([i1, p2])
    p2.extend([i2, p3])
    p3.append(c)
    assert c.ancestors == [i1, i2, p3]


def test_ancestors_no_index():
    """
    - p1
      - i1 (is_index: true, not iterable)
      - p2
        - i2 (is_index: true, not iterable)
        - p3
          - c
    """
    p1 = MockingRootNode('p1')
    p2 = MockingFolderNode('p2')
    p3 = MockingFolderNode('p3')
    c = MockingPageNode('c')
    p1.extend([p2])
    p2.extend([p3])
    p3.append(c)
    assert c.ancestors == [p1, p2, p3]


def test_ancestors_some_index():
    """
    - p1
      - i1 (is_index: true, not iterable)
      - p2
        - i2 (is_index: true, not iterable)
        - p3
          - c
    """
    p1 = MockingRootNode('p1')
    i1 = MockingIndexNode('i1')
    p2 = MockingFolderNode('p2')
    p3 = MockingFolderNode('p3')
    c = MockingPageNode('c')
    p1.extend([i1, p2])
    p2.extend([p3])
    p3.append(c)
    assert c.ancestors == [i1, p2, p3]


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


def test_node_pointer():
    p = MockingRootNode(name='site')
    a = MockingPageNode('a')
    b = MockingPageNode('b', {'a ->': 'site.a'})
    p.extend([a, b])
    assert b.a == a
    assert b['a'] == a


def test_getitem_and_getattr():
    config = {
        'key': 'value',
        'friend ->': 'site.bob.joe'
    }
    n = MockingRootNode('node', config)
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
    assert n['friend'] == joe


def test_url():
    config = {
        'root_url': '/',
        'iterable': True,
    }
    root = RootFolderNode(config, '', '')

    config = {
        'name': 'parent',
        'target_name': 'parent',
        'iterable': True,
    }
    parent = FolderNode(config, 'parent', 'parent')
    root.append(parent)

    config = {
        'name': 'bob',
        'target_name': 'bob.html',
        'iterable': True,
    }
    bob = JinjaNode(config, get_test_file('a_folder/page.j2'), '')

    config = {
        'name': 'jane',
        'target_name': 'jane.html',
        'iterable': True,
    }
    jane = JinjaNode(config, get_test_file('a_folder/page.j2'), '')

    parent.extend([bob, jane])

    assert bob.url == '/parent/bob.html'
    assert jane.url == '/parent/jane.html'


def test_url_override():
    config = {
        'root_url': '/foo/',
        'iterable': True,
    }
    root = RootFolderNode(config, '', '')

    config = {
        'name': 'parent',
        'target_name': 'parent',
        'type': 'folder',
        'iterable': True,
    }
    parent = FolderNode(config, 'parent', 'parent')
    root.append(parent)

    config = {
        'name': 'bob',
        'target_name': 'bob.html',
        'url': 'bob',
        'iterable': True,
    }
    bob = JinjaNode(config, get_test_file('a_folder/page.j2'), '')

    config = {
        'name': 'jane',
        'target_name': 'jane.xml',
        'url': 'jane',
        'iterable': True,
    }
    jane = AssetNode(config, get_test_file('a_folder/a_file.txt'), '')

    parent.extend([bob, jane])

    assert bob.url == '/foo/parent/bob'
    assert jane.url == '/foo/parent/jane'


def test_is_correct_type():
    config = {
        'name': 'folder',
        'target_name': 'folder',
        'type': 'folder',
    }
    folder = FolderNode(config, 'folder', 'folder')

    config = {
        'name': 'page',
        'target_name': 'page.html',
        'url': 'page',
    }
    page = JinjaNode(config, get_test_file('a_folder/page.j2'), '')

    config = {
        'name': 'asset',
        'target_name': 'asset.xml',
        'url': 'asset'
    }
    asset = AssetNode(config, get_test_file('a_folder/a_file.txt'), '')

    assert folder.is_folder == True
    assert folder.is_page == False
    assert folder.is_asset == False

    assert page.is_folder == False
    assert page.is_page == True
    assert page.is_asset == False

    assert asset.is_folder == False
    assert asset.is_page == False
    assert asset.is_asset == True


def test_is_correct_type_override():
    config = {
        'name': 'page',
        'target_name': 'page.html',
        'url': 'page',
        'is_page': False,
    }
    page = JinjaNode(config, get_test_file('a_folder/page.j2'), '')

    config = {
        'name': 'asset',
        'target_name': 'asset.xml',
        'url': 'asset',
        'is_asset': False,
    }
    asset = AssetNode(config, get_test_file('a_folder/a_file.txt'), '')

    assert page.is_folder == False
    assert page.is_page == False
    assert page.is_asset == True

    assert asset.is_folder == False
    assert asset.is_page == True
    assert asset.is_asset == False


def test_is_correct_type_reversed_override():
    config = {
        'name': 'page',
        'target_name': 'page.html',
        'url': 'page',
        'is_asset': True,
    }
    page = JinjaNode(config, get_test_file('a_folder/page.j2'), '')

    config = {
        'name': 'asset',
        'target_name': 'asset.xml',
        'url': 'asset',
        'is_page': True,
    }
    asset = AssetNode(config, get_test_file('a_folder/a_file.txt'), '')

    assert page.is_folder == False
    assert page.is_page == False
    assert page.is_asset == True

    assert asset.is_folder == False
    assert asset.is_page == True
    assert asset.is_asset == False
