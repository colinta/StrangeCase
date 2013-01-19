from strange_case.config_dict import ConfigDict
from strange_case.configurators import *

CONFIG = ConfigDict({
    ##|  ROOT URL
    'config_file': 'config.yaml',

    ##|  USED TO CLEAN DEPLOY PATH
    'remove_stale_files': True,
    'dont_remove': ['.*'],

    ##|  HOOKS
    'config_hook': None,

    ##|  EXTENSIONS
    'extensions': [],
    'filters': {},
    'processors': [],
    # most of these configurators are *very*
    # important, so if you're gonna go messing
    # with them, be warned.
    #
    # these are ensured to be loaded first
    '__configurators_pre__': [
        'strange_case.configurators.meta_before',
        'strange_case.configurators.override',
        'strange_case.configurators.file_types',
        'strange_case.configurators.page_types',
        'strange_case.configurators.merge_files_config',
        'strange_case.configurators.folder_config_file',
        'strange_case.configurators.front_matter_config',
        'strange_case.configurators.setdefault_name',
        'strange_case.configurators.setdefault_target_name',
        'strange_case.configurators.is_index',
        'strange_case.configurators.setdefault_iterable',
        'strange_case.configurators.ignore',
        'strange_case.configurators.skip_if_not_modified',  # sets 'skip' if mtime is new
    ],
    # these are the defaults
    'configurators': [
        'strange_case.extensions.configurators.order_from_name',
        'strange_case.extensions.configurators.created_at_from_name',
        'strange_case.extensions.configurators.title_from_name',
    ],
    # these are ensured to be loaded last
    '__configurators_post__': [
        'strange_case.configurators.set_url',
        'strange_case.configurators.meta_after',
    ],
})
