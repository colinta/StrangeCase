import datetime
from strange_case.configurators import *
from strange_case.extensions.configurators import *
from strange_case.tests import *


def test_created_at_from_name_YMD():
    source_file = get_test_file('a_folder/2012_01_01_file.txt')
    config = {}
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['created_at'] == datetime.date(2012, 1, 1)


def test_created_at_from_name_YM():
    source_file = get_test_file('a_folder/2012_01_file.txt')
    config = {}
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['created_at'] == datetime.date(2012, 1, 1)


def test_created_at_from_name_Y():
    source_file = get_test_file('a_folder/2012_file.txt')
    config = {}
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['created_at'] == datetime.date(2012, 1, 1)


def test_created_at_from_name_no_match():
    source_file = get_test_file('a_folder/012_file.txt')
    config = {}
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert 'created_at' not in config

    source_file = get_test_file('a_folder/12_file.txt')
    config = {}
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert 'created_at' not in config


def test_order_from_name_match():
    source_file = get_test_file('a_folder/012_file.txt')
    config = {}
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = order_from_name(source_file, config)
    assert config['order'] == 12


def test_order_from_name_no_match():
    source_file = get_test_file('a_folder/12_file.txt')
    config = {}
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = order_from_name(source_file, config)
    assert 'order' not in config


def test_strip_extensions_strip():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'strip_extensions': ['.txt']
    }
    config = setdefault_target_name(source_file, config)
    config = strip_extensions(source_file, config)
    assert config['url'] == 'a_file'


def test_strip_extensions_strip_default():
    source_file = get_test_file('a_folder/page.j2')
    config = {
        'rename_extensions': {'.j2': '.html'}
    }
    config = setdefault_target_name(source_file, config)
    config = strip_extensions(source_file, config)
    assert config['url'] == 'page'


def test_strip_extensions_no_strip():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {}
    config = setdefault_target_name(source_file, config)
    config = strip_extensions(source_file, config)
    assert 'url' not in config


def test_title_from_name():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'name': 'the_file_is_a_file_the_file'
    }
    config = setdefault_name(source_file, config)
    config = setdefault_target_name(source_file, config)
    config = title_from_name(source_file, config)
    assert config['title'] == 'The File Is a File the File'


def test_file_stats():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {}
    config = file_ctime(source_file, config)
    config = file_mtime(source_file, config)
    assert isinstance(config['file_ctime'], datetime.datetime)
    assert isinstance(config['file_mtime'], datetime.datetime)


def test_target_name_changes_url():
    source_file = get_test_file('a_folder/2012_01_01_file.txt')
    config = {
        'file_types': [
            ('page', ('*.txt',)),
        ],
        'type': 'page',
        'rename_extensions': {
            '.j2': '.html',
        },
        'target_name': 'a_file.txt'
    }
    config = file_types(source_file, config)
    config = front_matter_config(source_file, config)
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = setdefault_url(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['target_name'] == 'a_file.txt'
    assert config['url'] == 'a_file.txt'
