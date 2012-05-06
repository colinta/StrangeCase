import os

from strange_case.configurators import provides


@provides('target_name')
def setdefault_target_name(source_file, config):
    ##|  ASSIGN TARGET_NAME
    # allow target_name override, otherwise it is
    # `name + ext`
    ##|  FIX EXTENSION
    # .jinja2, .j2, and .md files should be served as .html
    file_name = os.path.basename(source_file)
    base_name, ext = os.path.splitext(file_name)
    if 'rename_extensions' in config and ext in config['rename_extensions']:
        ext = config['rename_extensions'][ext]
        config['target_name'] = base_name + ext

    target_name = base_name + ext

    ### fix_target_name?
    ### this code makes target names "look purty", like their name counterpart
    ##
    # target_name = re.sub(r'/[\W -]/', '_', target_name, re.UNICODE)
    ##
    ### it's commented out because I'm not convinced target_names should get
    ### this treatment.  If you have a strange character in your URL, that's
    ### your business.  Or maybe I'll add something to the upcoming "renamers"
    config['target_name'] = target_name
    return config

setdefault_target_name.dont_inherit = [
    'target_name'
]
