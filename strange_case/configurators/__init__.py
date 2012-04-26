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


from file_types import file_types
from folder_config_file import folder_config_file
from front_matter_config import front_matter_config
from ignore import ignore
from merge_files_config import merge_files_config
from setdefault_is_index import setdefault_is_index
from setdefault_name import setdefault_name
from setdefault_target_name import setdefault_target_name
from skip_if_not_modified import skip_if_not_modified
