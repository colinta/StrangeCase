import os
from strange_case.configurators import *
from strange_case.tests import *


def test_provides_decorator():
    a = {'dont_change_me': 'not changed'}

    @provides('dont_change_me')
    def should_do_nothing(source_file, config):
        config['dont_change_me'] = 'changed'
        return config

    should_do_nothing(None, a)

    @provides('change_me')
    def should_do_something(source_file, config):
        config['change_me'] = 'changed'
        return config

    should_do_something(None, a)

    assert a['dont_change_me'] == 'not changed'
    assert a['change_me'] == 'changed'


def test_file_types_folder():
    source_file = get_test_file('a_folder')
    config = {}
    config = file_types(source_file, config)
    assert config['type'] == 'folder'


def test_file_types_from_glob1():
    config = {
        'file_types': [
            ('text', ('*.txt',)),
            ('bin', ('*.bin',)),
        ],
    }
    source_file = get_test_file('a_folder/a_file.txt')
    config = file_types(source_file, config)
    assert config['type'] == 'text'


def test_file_types_from_glob2():
    config = {
        'file_types': [
            ('text', ('*.txt',)),
            ('bin', ('*.bin',)),
        ],
    }
    source_file = get_test_file('a_folder/a_file.bin')
    config = file_types(source_file, config)
    assert config['type'] == 'bin'


def test_file_types_from_default_type():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'default_type': 'file',
    }
    config = file_types(source_file, config)
    assert config['type'] == 'file'


def test_file_types_no_match():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {}
    assert None == file_types(source_file, config)


def test_folder_config_file():
    source_file = get_test_file('a_folder')
    config = {
        'config_file': 'config.yaml',
    }
    config = file_types(source_file, config)
    config = folder_config_file(source_file, config)
    assert config['test'] == 'test'


def test_folder_config_file_missing_config_file():
    source_file = get_test_file('a_folder')
    config = {
        'config_file': 'HUH.yml',
    }
    config = file_types(source_file, config)
    config = folder_config_file(source_file, config)
    assert not 'test' in config


def test_folder_config_file_ignore():
    source_file = get_test_file('a_folder')
    config = {
        'config_file': 'ignore_config.yaml',
    }
    config = file_types(source_file, config)
    assert None == folder_config_file(source_file, config)


def test_front_matter_config_success():
    source_file = get_test_file('a_folder/page.j2')
    config = {
        'type': 'page',
        'override': 'wrong',
    }
    config = front_matter_config(source_file, config)
    assert config['front'] == 'matter'
    assert config['override'] == 'overridden'


def test_front_matter_config_ticks():
    source_file = get_test_file('a_folder/page_ticks.j2')
    config = {
        'type': 'page',
        'modified': 1,
    }
    config = front_matter_config(source_file, config)
    assert config['ticks'] == 2
    assert config['modified'] == 2


def test_front_matter_config_ignore_doesnt_exist():
    source_file = get_test_file('a_folder/not_a_file.j2')
    config = {
        'type': 'page',
        'modified': 1,
    }
    config = front_matter_config(source_file, config)
    assert config['modified'] == 1


def test_front_matter_config_bad():
    source_file = get_test_file('a_folder/bad_page1.j2')
    config = {
        'type': 'page',
    }
    config = front_matter_config(source_file, config)
    assert not 'front' in config

    source_file = get_test_file('a_folder/bad_page2.j2')
    config = {
        'type': 'page',
    }
    config = front_matter_config(source_file, config)
    assert not 'front' in config


def test_ignore_true():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'ignore': True,
    }
    assert ignore(source_file, config) is None


def test_ignore_false():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'ignore': False,
    }
    assert ignore(source_file, config) == config


def test_ignore_true_pattern_match():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'ignore': ('*.txt'),
    }
    assert ignore(source_file, config) is None


def test_ignore_false_pattern_match():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'ignore': ('*.bfg',),
    }
    assert ignore(source_file, config) == config


def test_merge_files_config():
    source_file = get_test_file('a_folder')
    folder_config = {
        'config_file': 'files_config.yaml'
    }
    file_types(source_file, folder_config)
    folder_config_file(source_file, folder_config)

    def _folder_config():
        config = {}
        config.update(folder_config)
        return config

    config = _folder_config()
    assert len(config['files'].keys()) == 3

    config = _folder_config()
    source_file = get_test_file('a_folder/a_file.txt')
    config = merge_files_config(source_file, config)
    assert 'files' not in config
    assert config['is_a_file'] is True

    config = _folder_config()
    source_file = get_test_file('a_folder/bad_page1.j2')
    config = merge_files_config(source_file, config)
    assert 'files' not in config
    assert 'is_a_file' not in config

    config = _folder_config()
    source_file = get_test_file('a_folder/page.j2')
    config = merge_files_config(source_file, config)
    assert 'files' not in config
    assert config['is_a_file'] is False


def test_setdefault_name_not_setup():
    source_file = get_test_file('a_folder/page.j2')
    config = {}
    config = setdefault_name(source_file, config)
    assert config['name'] == 'page_j2'


def test_setdefault_name_remove_extension():
    source_file = get_test_file('a_folder/page.j2')
    config = {
        'rename_extensions': {
            '.j2': '.html',
        },
        'html_extension': '.html',
    }
    config = setdefault_name(source_file, config)
    assert config['name'] == 'page'


def test_setdefault_name_keep_extension():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'rename_extensions': {
            '.j2': '.html',
        },
        'html_extension': '.html',
    }
    config = setdefault_name(source_file, config)
    assert config['name'] == 'a_file_txt'


def test_setdefault_target_name_dont_rename_extension():
    source_file = get_test_file('a_folder/a_file.txt')
    config = {
        'rename_extensions': {
            '.j2': '.html',
        },
    }
    config = setdefault_target_name(source_file, config)
    assert config['target_name'] == 'a_file.txt'


def skip_if_not_modified_not_modified():
    source_file = get_test_file('a_folder/a_file.txt')
    mtime = os.stat(source_file).st_mtime
    config = {
        'file_mtimes': {source_file: mtime}
    }
    config = skip_if_not_modified(source_file, config)
    assert config['skip'] is False


def skip_if_not_modified_is_modified():
    source_file = get_test_file('a_folder/a_file.txt')
    mtime = os.stat(source_file).st_mtime
    config = {
        'file_mtimes': {source_file: mtime - 1}
    }
    config = skip_if_not_modified(source_file, config)
    assert config['skip'] is True


def test_setdefault_iterable_true():
    source_file = get_test_file('a_folder/page.j2')
    config = {
        'rename_extensions': {
            '.j2': '.html',
        },
        'index.html': 'page.html'
    }
    config = setdefault_target_name(source_file, config)
    assert config['target_name'] == config['index.html']
    config = setdefault_iterable(source_file, config)
    assert config['iterable'] is False


def test_setdefault_iterable_false():
    source_file = get_test_file('a_folder/page.j2')
    config = {
        'rename_extensions': {
            '.j2': '.html',
        },
        'index.html': 'index.html'
    }
    config = setdefault_target_name(source_file, config)
    assert config['target_name'] != config['index.html']
    config = setdefault_iterable(source_file, config)
    assert config['iterable'] is True


def test_setdefault_iterable_override_true():
    source_file = get_test_file('a_folder/bad_page1.j2')
    config = {
        'index.html': 'bad_page1.j2',
        'iterable': True
    }
    config = setdefault_iterable(source_file, config)
    assert config['iterable'] is True


def test_setdefault_iterable_override_false():
    source_file = get_test_file('a_folder/page.j2')
    config = {
        'index.html': 'page.j2',
        'iterable': False
    }
    config = setdefault_iterable(source_file, config)
    assert config['iterable'] is False


def test_set_url():
    source_file = get_test_file('a_folder/page.j2')
    config = {
        'rename_extensions': {
            '.j2': '.html',
        },
    }
    config = setdefault_target_name(source_file, config)
    config = set_url(source_file, config)
    assert config['url'] == 'page.html'


def test_set_url_index():
    source_file = get_test_file('a_folder/index.j2')
    config = {
        'rename_extensions': {
            '.j2': '.html',
        },
        'index.html': 'index.html'
    }
    config = setdefault_target_name(source_file, config)
    assert config['target_name'] == config['index.html']
    config = set_url(source_file, config)
    assert config['url'] == ''


def test_set_url_override():
    source_file = get_test_file('a_folder/bad_page1.j2')
    config = {
        'index.html': 'bad_page1.j2',
        'url': 'bad_page1'
    }
    config = set_url(source_file, config)
    assert config['url'] == 'bad_page1'
