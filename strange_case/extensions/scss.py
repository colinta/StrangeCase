from __future__ import absolute_import
import jinja2
import jinja2.ext
try:
    import sass
except ImportError:
    from strange_case import require_package
    require_package('libsass')

from strange_case.registry import Registry
from strange_case.nodes import AssetNode


def compile_file(file):
    return sass.compile(filename=file, output_style='compressed')

def compile_string(string):
    return sass.compile(string=string, output_style='compressed')


class ScssExtension(jinja2.ext.Extension):
    tags = set(['scss'])

    def __init__(self, environment):
        super(ScssExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(
            ['name:endscss'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('_scss_support'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _scss_support(self, caller):
        return compile_string(caller())


class ScssNode(AssetNode):
    """
    Converts a .scss file into css
    """
    def generate_file(self, site, source_path, target_path):
        if not self['skip']:
            output = compile_file(source_path)
            with open(target_path, 'wb') as f:
                f.write(output.encode('utf-8'))
        self.files_tracked.append(source_path)
        self.files_written.append(target_path)


def processor(config, source_path, target_path):
    if config['target_name'].endswith('.scss') or config['target_name'].endswith('.sass'):
        config['target_name'] = config['target_name'][:-4] + 'css'

    scss_node = ScssNode(config, source_path, target_path)
    return (scss_node,)


Registry.register('scss', processor)
Registry.associate('scss', ['*.scss'])
