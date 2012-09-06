import datetime
from strange_case.configurators import *
from strange_case.extensions.configurators import *
from strange_case.tests import *


@will_test(setdefault_target_name, setdefault_name, created_at_from_name)
def test_created_at_from_name_YMD(config):
    source_file = get_test_file('a_folder/2012_01_01_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['created_at'] == datetime.date(2012, 1, 1)


@will_test(setdefault_target_name, setdefault_name, created_at_from_name)
def test_created_at_from_name_YM(config):
    source_file = get_test_file('a_folder/2012_01_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['created_at'] == datetime.date(2012, 1, 1)


@will_test(setdefault_target_name, setdefault_name, created_at_from_name)
def test_created_at_from_name_Y(config):
    source_file = get_test_file('a_folder/2012_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['created_at'] == datetime.date(2012, 1, 1)


@will_test(setdefault_target_name, setdefault_name, created_at_from_name)
def test_created_at_from_name_no_match_012(config):
    source_file = get_test_file('a_folder/012_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert 'created_at' not in config


@will_test(setdefault_target_name, setdefault_name, created_at_from_name)
def test_created_at_from_name_no_match_12(config):
    source_file = get_test_file('a_folder/12_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert 'created_at' not in config


@will_test(setdefault_target_name, setdefault_name, order_from_name)
def test_order_from_name_match(config):
    source_file = get_test_file('a_folder/012_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = order_from_name(source_file, config)
    assert config['order'] == 12


@will_test(setdefault_target_name, setdefault_name, order_from_name)
def test_order_from_name_no_match(config):
    source_file = get_test_file('a_folder/12_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = order_from_name(source_file, config)
    assert 'order' not in config


@will_test(setdefault_target_name, setdefault_name, order_from_name,
           created_at_from_name)
def test_order_and_created_at_from_name_match(config):
    source_file = get_test_file('a_folder/001_2012_05_04_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = order_from_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['order'] == 1
    assert config['created_at'] == datetime.date(2012, 5, 4)


@will_test(setdefault_target_name, setdefault_name, order_from_name,
           created_at_from_name)
def test_order_and_created_at_from_name_strip_target_name(config):
    config['strip_metadata_from_target_name'] = True
    source_file = get_test_file('a_folder/001_2012_05_04_file.txt')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = order_from_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['order'] == 1
    assert config['created_at'] == datetime.date(2012, 5, 4)
    assert config['target_name'] == 'file.txt'


@will_test(setdefault_target_name, setdefault_name, order_from_name,
           front_matter_config, created_at_from_name)
def test_order_and_created_at_from_name_with_yaml_strip_target_name(config):
    config['type'] = 'page'
    config['strip_metadata_from_name'] = True
    config['strip_metadata_from_target_name'] = True
    source_file = get_test_file('a_folder/001_2012_05_04_page_with_created_at.j2')
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = front_matter_config(source_file, config)
    config = order_from_name(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['order'] == 1
    assert config['created_at'] == datetime.date(2012, 5, 4)
    assert config['name'] == 'page_with_created_at'
    assert config['target_name'] == 'page_with_created_at.html'


@will_test(setdefault_target_name, is_index, set_url, strip_extensions)
def test_strip_extensions_strip(config):
    config.update({
        'strip_extensions': ['.txt']
    })
    source_file = get_test_file('a_folder/a_file-txt.txt')
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    config = set_url(source_file, config)
    config = strip_extensions(source_file, config)
    assert config['url'] == 'a_file-txt'


@will_test(setdefault_target_name, strip_extensions)
def test_strip_extensions_strip_url_already_set(config):
    config.update({
        'strip_extensions': ['.txt'],
        'url': 'a_file.txt'
    })
    source_file = get_test_file('a_folder/a_file.txt')

    config = setdefault_target_name(source_file, config)
    config = strip_extensions(source_file, config)
    assert config['url'] == 'a_file'


@will_test(setdefault_target_name, is_index, set_url, strip_extensions)
def test_strip_extensions_strip_default(config):
    config.update({
        'rename_extensions': {'.j2': '.html'}
    })
    source_file = get_test_file('a_folder/page.j2')
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    config = set_url(source_file, config)
    config = strip_extensions(source_file, config)
    assert config['url'] == 'page'


@will_test(setdefault_target_name, is_index, set_url, strip_extensions)
def test_strip_extensions_no_strip(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    config = set_url(source_file, config)
    config = strip_extensions(source_file, config)
    assert config['url'] == 'a_file.txt'


@will_test(setdefault_name, setdefault_target_name, is_index, title_from_name)
def test_title_from_name(config):
    config.update({
        'name': 'the_file_is_a_file_the_file'
    })
    source_file = get_test_file('a_folder/a_file.txt')
    config = setdefault_name(source_file, config)
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    config = title_from_name(source_file, config)
    assert config['title'] == 'The File Is a File the File'


@will_test(file_ctime, file_mtime)
def test_file_stats(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config = file_ctime(source_file, config)
    config = file_mtime(source_file, config)
    assert isinstance(config['file_ctime'], datetime.datetime)
    assert isinstance(config['file_mtime'], datetime.datetime)


@will_test(file_types, front_matter_config, setdefault_target_name,
           setdefault_name, is_index, set_url, created_at_from_name)
def test_target_name_changes_url(config):
    source_file = get_test_file('a_folder/2012_01_01_file.txt')
    config.update({
        'file_types': [
            ('page', ('*.txt',)),
        ],
        'type': 'page',
        'rename_extensions': {
            '.j2': '.html',
        },
        'target_name': 'a_file.txt'
    })
    config = file_types(source_file, config)
    config = front_matter_config(source_file, config)
    config = setdefault_target_name(source_file, config)
    config = setdefault_name(source_file, config)
    config = is_index(source_file, config)
    config = set_url(source_file, config)
    config = created_at_from_name(source_file, config)
    assert config['target_name'] == 'a_file.txt'
    assert config['url'] == 'a_file.txt'
