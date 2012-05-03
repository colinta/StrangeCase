import os


def skip_if_not_modified(source_file, config):
    if config.get('skip') == False:
        config['skip'] = False
    else:
        try:
            f = os.path.abspath(source_file)
            mtime = os.stat(f).st_mtime
            stored_mtime = config['file_mtimes'].get(f)

            if stored_mtime and stored_mtime == mtime:
                config['skip'] = True
            else:
                config['skip'] = False
        except OSError:
            pass
    return config


skip_if_not_modified.defaults = {
    'file_mtimes': {},
}