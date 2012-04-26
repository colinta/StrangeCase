import os

from strange_case.configurators import provides


@provides('file_ctime')
def file_ctime(source_file, config):
    try:
        f = os.path.abspath(source_file)
        config['file_ctime'] = os.path.getctime(f)
    except OSError:
        pass
    return config


@provides('file_mtime')
def file_mtime(source_file, config):
    try:
        f = os.path.abspath(source_file)
        config['file_mtime'] = os.path.getmtime(f)
    except OSError:
        pass
    return config
