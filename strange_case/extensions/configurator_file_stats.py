import os
import datetime

from strange_case.configurators import provides


@provides('file_ctime')
def file_ctime(source_file, config):
    try:
        f = os.path.abspath(source_file)
        ctime = os.path.getctime(f)
        config['file_ctime'] = datetime.datetime.fromtimestamp(ctime)
    except OSError:
        pass
    return config


@provides('file_mtime')
def file_mtime(source_file, config):
    try:
        f = os.path.abspath(source_file)
        mtime = os.path.getmtime(f)
        config['file_mtime'] = datetime.datetime.fromtimestamp(mtime)
    except OSError:
        pass
    return config
