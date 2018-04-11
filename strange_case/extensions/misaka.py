from __future__ import absolute_import
import re
try:
    import misaka
    # from misaka import Markdown, HtmlRenderer, EXT_FENCED_CODE, EXT_NO_INTRA_EMPHASIS, HTML_SMARTYPANTS
except ImportError:
    from strange_case import require_package
    require_package('misaka')
import jinja2
import jinja2.ext
from plywood.env import PlywoodEnv

try:
    import pygments as p
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
except ImportError:
    from strange_case import recommend_package
    recommend_package('pygments', 'Pygments is used for syntax highlighting code blocks')

slug_remove = re.compile('\W+')
unidecode = None
try:
    import unidecode
except ImportError:
    from strange_case import recommend_package
    recommend_package('unidecode', 'Unidecode is used to convert headers with non-ASCII characters into ids for <h1> tags')


def sluggify(s):
    if unidecode:
        s = unidecode.unidecode(s)
    s = s.lower()
    return slug_remove.sub('-', s).strip('-')


class HeaderRenderer(misaka.HtmlRenderer):
    def header(self, header, n):
        header = header.strip()
        slug = sluggify(header)
        return "\n<h{n} id=\"{slug}\">{header}</h{n}>\n".format(**locals())


class PygmentsRenderer(misaka.HtmlRenderer):
    def block_code(self, text, lang):
        # pygments code highlighting
        if lang is None:
            return u'<pre><code>{}</pre></code>'.format(text)
        return p.highlight(text, get_lexer_by_name(lang), HtmlFormatter(cssclass='codehilite'))


class MyRenderer(HeaderRenderer, PygmentsRenderer):
    pass

renderer = MyRenderer()
markdowner = misaka.Markdown(renderer, extensions=(misaka.EXT_FENCED_CODE, misaka.EXT_NO_INTRA_EMPHASIS,
                                  misaka.EXT_STRIKETHROUGH, misaka.EXT_SUPERSCRIPT,
                                  misaka.EXT_TABLES))


# markdown filter
def markdown(markdown):
    return misaka.smartypants(markdowner(markdown).strip())


# plywood extension
@PlywoodEnv.register_fn('markdown', accepts_block=True)
def plywood_markdown(block, content=None):
    if content:
        return markdown(content)
    return markdown(block())


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
