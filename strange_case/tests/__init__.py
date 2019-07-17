# -*- encoding: utf-8 -*-
import os
import yaml
from os.path import join
import re
import shutil
from functools import wraps
import pytest
from strange_case.strange_case_config import CONFIG


def test_setup():
    assert True == os.path.isdir(get_test_file('a_folder'))

    assert True == os.path.exists(get_test_file('a_folder/2012_01_01_file.txt'))
    assert True == os.path.exists(get_test_file('a_folder/2012_01_file.txt'))
    assert True == os.path.exists(get_test_file('a_folder/2012_file.txt'))
    assert True == os.path.exists(get_test_file('a_folder/012_file.txt'))
    assert True == os.path.exists(get_test_file('a_folder/12_file.txt'))
    assert True == os.path.exists(get_test_file('a_folder/a_file.bin'))
    assert True == os.path.exists(get_test_file('a_folder/a_file.txt'))
    assert True == os.path.exists(get_test_file('a_folder/bad_page1.j2'))
    assert True == os.path.exists(get_test_file('a_folder/bad_page2.j2'))
    assert True == os.path.exists(get_test_file('a_folder/config.yaml'))
    assert True == os.path.exists(get_test_file('a_folder/files_config.yaml'))
    assert True == os.path.exists(get_test_file('a_folder/ignore_config.yaml'))
    assert True == os.path.exists(get_test_file('a_folder/page.j2'))
    assert True == os.path.exists(get_test_file('a_folder/page_ticks.j2'))

    assert False == os.path.exists(get_test_file('a_folder/HUH.yml'))
    assert False == os.path.exists(get_test_file('a_folder/not_a_file.j2'))


def get_test_file(source):
    return join(os.path.dirname(__file__), source)


def will_test(*configurators):
    def decorator(fn):
        @wraps(fn)
        def wrapper(**ignore):
            config = {
                'project_path': os.path.dirname(__file__),
                'site_path': get_test_file('a_site'),
                'deploy_path': get_test_file('a_public'),
            }
            for configurator in configurators:
                try:
                    config.update(configurator.defaults)
                except AttributeError:
                    pass
            for configurator in configurators:
                try:
                    config.on_start(config)
                except AttributeError:
                    pass
            return fn(config)
        return wrapper
    return decorator


@pytest.fixture
def basic_config():
    project_name = 'basic_site'
    project_path = get_test_file(project_name)
    deploy_path = join(project_path, 'public')
    config_file_path = join(project_path, 'config.yaml')

    if os.path.exists(deploy_path):
        shutil.rmtree(deploy_path)
    config = CONFIG.copy(all=True)

    config['project_path'] = project_path
    config['site_path'] = join(project_path, 'site')
    config['deploy_path'] = join(project_path, 'public')

    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as config_file:
            yaml_config = yaml.load(config_file, Loader=yaml.FullLoader)
            config.update(yaml_config)

    old_path = os.getcwd()
    try:
        os.chdir(project_path)
        yield config
    except Exception:
        tree(config['site_path'], config['project_path'])
        tree(config['deploy_path'], config['project_path'])
        raise
    finally:
        os.chdir(old_path)
    shutil.rmtree(deploy_path)


def will_generate(project_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(**ignore):
            project_path = get_test_file(project_name)
            deploy_path = join(project_path, 'public')
            config_file_path = join(project_path, 'config.yaml')

            if os.path.exists(deploy_path):
                shutil.rmtree(deploy_path)
            config = CONFIG.copy(all=True)

            config['project_path'] = project_path
            config['site_path'] = join(project_path, 'site')
            config['deploy_path'] = join(project_path, 'public')

            if os.path.exists(config_file_path):
                with open(config_file_path, 'r') as config_file:
                    yaml_config = yaml.load(config_file, Loader=yaml.FullLoader)
                    config.update(yaml_config)

            old_path = os.getcwd()
            try:
                os.chdir(project_path)
                ret = fn(config)
            except Exception:
                tree(config['site_path'], config['project_path'])
                tree(config['deploy_path'], config['project_path'])
                raise
            finally:
                os.chdir(old_path)
            shutil.rmtree(deploy_path)
            return ret
        return wrapper
    return decorator


def check_path_contents(path, path_contents):
    """
    Checks contents and file structure.  Any files not in path_contents that
    exist in path will raise an assertion error, and any content in
    path_contents that is not in path will raise an assertion error.
    """
    check_existing_files(path, path_contents)

    for filename, contents in path_contents.items():
        assert os.path.exists(join(path, filename))
        if isinstance(contents, dict):
            check_path_contents(join(path, filename), contents)
        elif isinstance(contents, list):
            for content in contents:
                check_file_contents(join(path, filename), content)
        else:
            check_file_contents(join(path, filename), contents)


def check_existing_files(path, should_exist):
    folders = [k for k in should_exist.keys() if isinstance(should_exist[k], dict)]
    files = [k for k in should_exist.keys() if not isinstance(should_exist[k], dict)]
    for filename in os.listdir(path):
        file = join(path, filename)
        if os.path.isfile(file):
            assert filename in files, "{filename} is not in {files}".format(**locals())
            del files[files.index(filename)]
        if os.path.isdir(file):
            assert filename in folders, "{filename} is not in {folders}".format(**locals())
            del folders[folders.index(filename)]
            check_existing_files(file, should_exist[filename])
    assert len(folders) == 0, 'folders contains "{folders!r}", but should be empty'.format(**locals())
    assert len(files) == 0, 'files contains "{files!r}", but should be empty'.format(**locals())


RegexType = type(re.compile(''))


def check_file_contents(file_name, search):
    with open(file_name) as f:
        content = f.read()

    if search is True:
        assert True
    elif isinstance(search, RegexType):
        file_name = os.path.basename(file_name)
        assert search.search(content), '{content!r} does not match {search.pattern!r}'.format(**locals())
    else:
        file_name = os.path.basename(file_name)
        assert search in content, '{content!r} does not contain {search!r}'.format(**locals())


LEFT_T = '|-- '  # u'\u251c\u2500\u2500'
LAST_T = '+-- '  # u'\u2514\u2500\u2500'
NEXT_T = '|   '  # u'\u2502\xa0\xa0'
NONE_T = '    '  # u'\u2502\xa0\xa0'


def tree(path, rel_to, indent=None):
    import sys
    from blessings import Terminal
    t = Terminal()

    # available in locals()
    left_t = LEFT_T
    last_t = LAST_T
    next_t = NEXT_T
    none_t = NONE_T

    if indent is None:
        sys.stdout.write(t.bold_blue(os.path.relpath(path, rel_to)) + "\n")
        indent = []

    last_index = len(os.listdir(path)) - 1
    for index, entry in enumerate(os.listdir(path)):
        is_last = index == last_index
        sys.stdout.write(u"{indent}{pre}{entry}\n".format(indent=''.join(indent), pre=is_last and last_t or left_t, entry=entry))
        file = join(path, entry)
        if os.path.isdir(file):
            if is_last:
                tree(file, rel_to, indent + [none_t])
            else:
                tree(file, rel_to, indent + [next_t])
