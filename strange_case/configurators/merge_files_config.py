import os


def merge_files_config(source_file, config):
    ##|  MERGE FILES CONFIG
    # these use the physical file_name
    file_name = os.path.basename(source_file)
    if 'files' in config:
        if file_name in config['files']:
            config.update(config['files'][file_name])
        # the 'files' setting is not passed on to child pages
        del config['files']
    return config
