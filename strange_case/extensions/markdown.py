import jinja2
import jinja2.ext
try:
    import markdown2
except ImportError:
    from strange_case import require_package
    require_package('Markdown2')

try:
    import pygments
except ImportError:
    from strange_case import recommend_package
    recommend_package('pygments', 'Pygments is used for syntax highlighting code blocks')


markdowner = markdown2.Markdown(extras=["fenced-code-blocks", "header-ids",
    "code-friendly"])


# markdown filter
def markdown(markdown):
    return markdowner.convert(markdown).strip()


# markdown block
class MarkdownExtension(jinja2.ext.Extension):
    tags = ('markdown',)

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(
            ['name:endmarkdown'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('markdown'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def markdown(self, caller):
        return markdown(caller())
