import os
from functools import wraps


def test_test_setup():
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
    return os.path.join(os.path.dirname(__file__), source)


def will_test(*configurators):
    def decorator(fn):
        @wraps(fn)
        def wrapper():
            config = {}
            for configurator in configurators:
                try:
                    config.update(configurator.defaults)
                except AttributeError:
                    pass
            return fn(config)
        return wrapper
    return decorator
