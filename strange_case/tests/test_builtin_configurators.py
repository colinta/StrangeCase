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
    assert a['dont_change_me'] == 'not changed'

    @provides('change_me')
    def should_do_something(source_file, config):
        config['change_me'] = 'changed'
        return config

    should_do_something(None, a)
    assert a['change_me'] == 'changed'


@will_test(file_types)
def test_file_types_folder(config):
    source_file = get_test_file('a_folder')
    config = file_types(source_file, config)
    assert config['type'] == 'folder'


@will_test(file_types)
def test_file_types_root(config):
    source_file = config['site_path']
    config = file_types(source_file, config)
    assert config['type'] == 'root'


@will_test(file_types)
def test_file_types_from_glob1(config):
    config.update({
        'file_types': [
            ('text', ('*.txt',)),
            ('bin', ('*.bin',)),
        ],
    })
    source_file = get_test_file('a_folder/a_file.txt')
    config = file_types(source_file, config)
    assert config['type'] == 'text'


@will_test(file_types)
def test_file_types_from_glob2(config):
    config.update({
        'file_types': [
            ('text', ('*.txt',)),
            ('bin', ('*.bin',)),
        ],
    })
    source_file = get_test_file('a_folder/a_file.bin')
    config = file_types(source_file, config)
    assert config['type'] == 'bin'


@will_test()
def test_file_types_from_default_type(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config.update({
        'default_type': 'file',
    })
    config = file_types(source_file, config)
    assert config['type'] == 'file'


@will_test(file_types)
def test_file_types_no_match(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config.update({
        'default_type': None,
        'file_types': (
            ('page', ['*.j2']),
        ),
    })
    assert None == file_types(source_file, config)


@will_test(file_types, folder_config_file)
def test_folder_config_file(config):
    source_file = get_test_file('a_folder')
    config.update({
        'config_file': 'config.yaml',
    })
    config = file_types(source_file, config)
    config = folder_config_file(source_file, config)
    assert config['test'] == 'test'


@will_test(file_types, folder_config_file)
def test_folder_config_file_missing_config_file(config):
    source_file = get_test_file('a_folder')
    config.update({
        'config_file': 'HUH.yml',
    })
    config = file_types(source_file, config)
    config = folder_config_file(source_file, config)
    assert not 'test' in config


@will_test(file_types, folder_config_file, ignore)
def test_folder_config_file_ignore(config):
    source_file = get_test_file('a_folder')
    config.update({
        'config_file': 'ignore_config.yaml',
    })
    config = file_types(source_file, config)
    config == folder_config_file(source_file, config)
    assert None == ignore(source_file, config)


@will_test(front_matter_config)
def test_front_matter_config_success(config):
    source_file = get_test_file('a_folder/page.j2')
    config.update({
        'type': 'page',
        'override': 'wrong',
    })
    config = front_matter_config(source_file, config)
    assert config['front'] == 'matter'
    assert config['override'] == 'overridden'


@will_test(front_matter_config)
def test_front_matter_config_ticks(config):
    source_file = get_test_file('a_folder/page_ticks.j2')
    config.update({
        'type': 'page',
        'modified': 1,
    })
    config = front_matter_config(source_file, config)
    assert config['ticks'] == 2
    assert config['modified'] == 2


@will_test(front_matter_config)
def test_front_matter_config_ignore_doesnt_exist(config):
    source_file = get_test_file('a_folder/not_a_file.j2')
    config.update({
        'type': 'page',
        'modified': 1,
    })
    config = front_matter_config(source_file, config)
    assert config['modified'] == 1


@will_test(front_matter_config)
def test_front_matter_config_bad1(config):
    source_file = get_test_file('a_folder/bad_page1.j2')
    config.update({
        'type': 'page',
    })
    config = front_matter_config(source_file, config)
    assert not 'front' in config


@will_test(front_matter_config)
def test_front_matter_config_bad2(config):
    source_file = get_test_file('a_folder/bad_page2.j2')
    config.update({
        'type': 'page',
    })
    config = front_matter_config(source_file, config)
    assert not 'front' in config


@will_test(ignore)
def test_ignore_true(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config.update({
        'ignore': True,
    })
    assert ignore(source_file, config) is None


@will_test(ignore)
def test_ignore_false(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config.update({
        'ignore': False,
    })
    assert ignore(source_file, config) == config


@will_test(ignore)
def test_ignore_true_pattern_match(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config.update({
        'ignore': ('*.txt'),
    })
    assert ignore(source_file, config) is None


@will_test(ignore)
def test_ignore_false_pattern_match(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config.update({
        'ignore': ('*.bfg',),
    })
    assert ignore(source_file, config) == config


@will_test(file_types, folder_config_file)
def test_merge_files_config(folder_config):
    source_file = get_test_file('a_folder')
    folder_config.update({
        'config_file': 'files_config.yaml'
    })
    folder_config = file_types(source_file, folder_config)
    folder_config = folder_config_file(source_file, folder_config)

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


@will_test(setdefault_name)
def test_setdefault_name_not_setup(config):
    source_file = get_test_file('a_folder/page.j2')
    config = setdefault_name(source_file, config)
    assert config['name'] == 'page'


@will_test(setdefault_name)
def test_setdefault_name_remove_extension(config):
    source_file = get_test_file('a_folder/page.j2')
    config.update({
        'rename_extensions': {
            '.j2': '.html',
        },
        'html_extension': '.html',
    })
    config = setdefault_name(source_file, config)
    assert config['name'] == 'page'


@will_test(setdefault_name)
def test_setdefault_name_keep_extension(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config.update({
        'rename_extensions': {
            '.j2': '.html',
        },
        'html_extension': '.html',
    })
    config = setdefault_name(source_file, config)
    assert config['name'] == 'a_file_txt'


@will_test(setdefault_target_name)
def test_setdefault_target_name_dont_rename_extension(config):
    source_file = get_test_file('a_folder/a_file.txt')
    config.update({
        'rename_extensions': {
            '.j2': '.html',
        },
    })
    config = setdefault_target_name(source_file, config)
    assert config['target_name'] == 'a_file.txt'


@will_test(skip_if_not_modified)
def test_skip_if_not_modified_not_modified(config):
    source_file = get_test_file('a_folder/a_file.txt')
    mtime = os.stat(source_file).st_mtime
    config.update({
        'file_mtimes': {source_file: mtime}
    })
    config = skip_if_not_modified(source_file, config)
    assert config['skip'] is True


@will_test(skip_if_not_modified)
def test_skip_if_not_modified_is_modified(config):
    source_file = get_test_file('a_folder/a_file.txt')
    mtime = os.stat(source_file).st_mtime
    config.update({
        'file_mtimes': {source_file: mtime - 1}
    })
    config = skip_if_not_modified(source_file, config)
    assert config['skip'] is False


@will_test(is_index, setdefault_target_name, setdefault_iterable)
def test_setdefault_iterable_true(config):
    source_file = get_test_file('a_folder/page.j2')
    config.update({
        'rename_extensions': {
            '.j2': '.html',
        },
        'index.html': 'page.html'
    })
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    assert config['target_name'] == config['index.html']
    config = setdefault_iterable(source_file, config)
    assert config['iterable'] is False


@will_test(is_index, setdefault_target_name, setdefault_iterable)
def test_setdefault_iterable_false(config):
    source_file = get_test_file('a_folder/page.j2')
    config.update({
        'rename_extensions': {
            '.j2': '.html',
        },
        'index.html': 'index.html'
    })
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    assert config['target_name'] != config['index.html']
    config = setdefault_iterable(source_file, config)
    assert config['iterable'] is True


@will_test(setdefault_iterable)
def test_setdefault_iterable_override_true(config):
    source_file = get_test_file('a_folder/bad_page1.j2')
    config.update({
        'index.html': 'bad_page1.j2',
        'iterable': True
    })
    config = setdefault_iterable(source_file, config)
    assert config['iterable'] is True


@will_test(setdefault_iterable)
def test_setdefault_iterable_override_false(config):
    source_file = get_test_file('a_folder/page.j2')
    config.update({
        'index.html': 'page.j2',
        'iterable': False
    })
    config = setdefault_iterable(source_file, config)
    assert config['iterable'] is False


@will_test(setdefault_name, setdefault_target_name, is_index, set_url)
def test_set_url(config):
    source_file = get_test_file('a_folder/page.j2')
    config.update({
        'rename_extensions': {
            '.j2': '.html',
        },
    })
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    config = set_url(source_file, config)
    assert config['url'] == 'page.html'


@will_test(setdefault_name, setdefault_target_name, is_index, set_url)
def test_set_url_index(config):
    source_file = get_test_file('a_folder/index.j2')
    config.update({
        'rename_extensions': {
            '.j2': '.html',
        },
        'index.html': 'index.html'
    })
    config = setdefault_name(source_file, config)
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    assert config['target_name'] == config['index.html']
    config = set_url(source_file, config)
    assert config['url'] == ''


@will_test(setdefault_name, setdefault_target_name, is_index, set_url)
def test_set_url_cant_override(config):
    source_file = get_test_file('a_folder/bad_page1.j2')
    config.update({
        'url': 'bad_page1',
    })
    config = setdefault_name(source_file, config)
    config = setdefault_target_name(source_file, config)
    config = is_index(source_file, config)
    config = set_url(source_file, config)
    assert config['url'] == 'bad_page1.html'


@will_test(override)
def test_override_preserves_local_config(config):
    source_file = get_test_file('a_folder/bad_page1.j2')
    config.update({
        'title': 'old title',
        'override': {
            'title': 'Overridden'
        }
    })
    config = override(source_file, config)
    assert config['title'] == 'old title'
