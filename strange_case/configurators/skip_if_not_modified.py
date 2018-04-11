"""
This configurator is written as a class, and called using the __call__ method.
It was easier to write this way, since I needed to implement the `on_start` and
`on_finish` hooks.
"""
import os
import pickle
from strange_case.nodes import Node


class SkipIfNotModified(object):
    defaults = {
        'file_mtimes': {},
    }

    dont_inherit = [
        'skip'
    ]

    def on_start(self, config):
        timestamps = config.get('.timestamps', '.timestamps')
        if not timestamps:
            return

        # read timestamps file
        self.timestamps_file = os.path.join(config['project_path'], timestamps)
        if os.path.exists(self.timestamps_file):
            with open(self.timestamps_file, 'rb') as fp:
                config['file_mtimes'] = pickle.load(fp)

    def on_finish(self, config):
        timestamps = config.get('.timestamps', '.timestamps')
        if not timestamps:
            return

        timestamps = {}
        for file_tracked in Node.files_tracked:
            f = os.path.abspath(file_tracked)
            timestamps[f] = os.stat(file_tracked).st_mtime
        pickle.dump(timestamps, open(self.timestamps_file, 'w'))

    def __call__(self, source_file, config):
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

skip_if_not_modified = SkipIfNotModified()
