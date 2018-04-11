from __future__ import absolute_import
import sys
import jinja2
import jinja2.ext
try:
    import clevercss
except ImportError:
    from strange_case import require_package
    require_package('CleverCSS')

from strange_case.registry import Registry
from strange_case.nodes import AssetNode

clevercss_compiler = clevercss.convert


class CleverCssExtension(jinja2.ext.Extension):
    tags = set(['clevercss'])

    def __init__(self, environment):
        super(CleverCssExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(
            ['name:endclevercss'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('_clevercss_support'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _clevercss_support(self, caller):
        return clevercss_compiler(caller()).strip()


class CleverCssNode(AssetNode):
    """
    Converts a .ccss file into css
    """
    def generate_file(self, site, source_path, target_path):
        if not self['skip']:
            ccss_content = open(source_path, 'r').read()
            css_content = clevercss_compiler(ccss_content)
            with open(target_path, 'w') as f:
                f.write(css_content)
        elif self['__verbose']:
            sys.stderr.write("Skipping %s\n" % target_path)
        self.files_tracked.append(source_path)
        self.files_written.append(target_path)


def processor(config, source_path, target_path):
    if config['target_name'].endswith('ccss'):
        config['target_name'] = config['target_name'][:-4] + 'css'
    if config['target_name'].endswith('clevercss'):
        config['target_name'] = config['target_name'][:-9] + 'css'

    ccss_node = CleverCssNode(config, source_path, target_path)
    return (ccss_node,)


Registry.register('clevercss', processor)
Registry.associate('clevercss', ['*.ccss', '*.clevercss'])
