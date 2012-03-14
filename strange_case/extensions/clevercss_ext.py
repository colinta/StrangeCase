import jinja2
import jinja2.ext
import clevercss

from strange_case.registry import Registry
from strange_case.nodes import FileNode

clevercss_compiler = clevercss.convert


class CleverCssExtension(jinja2.ext.Extension):
    tags = set(['clevercss'])

    def __init__(self, environment):
        super(CleverCssExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
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


class CleverCssNode(FileNode):
    """
    Converts a .ccss file into css
    """
    def generate_file(self, site, source_path, target_path):
        ccss_content = open(source_path, 'r').read()
        css_content = clevercss_compiler(ccss_content)
        with open(self.target_path) as f:
            f.write(css_content)
        self.files_written.append(target_path)

        super(CleverCssNode, self).generate(site)


def clevercss_processor(config, source_path, target_path):
    if config['target_name'][-4:] == 'ccss':
        config['target_name'][-4:] = 'css'
    if config['target_name'][-9:] == 'clevercss':
        config['target_name'][-9:] = 'css'

    ccss_node = CleverCssNode(config, source_path, target_path)
    return (ccss_node,)


Registry.register('clevercss', clevercss_processor)
Registry.associate('clevercss', ['*.ccss', '*.clevercss'])
