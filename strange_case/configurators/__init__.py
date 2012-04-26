from functools import wraps


def provides(conf):
    def decorator(function):
        @wraps(function)
        def wrapper(source_file, config):
            if conf not in config:
                return function(source_file, config)
            return config
        return wrapper
    return decorator


def is_index(conf):
    return conf['target_name'] == conf.get('index.html', 'index.html')


from file_types import file_types
from folder_config_file import folder_config_file
from front_matter_config import front_matter_config
from ignore import ignore
from merge_files_config import merge_files_config
from setdefault_name import setdefault_name
from setdefault_target_name import setdefault_target_name
from setdefault_url import setdefault_url
from setdefault_iterable import setdefault_iterable
from skip_if_not_modified import skip_if_not_modified
