import jinja2
import jinja2.ext


# canhaz block
class CanHazExtension(jinja2.ext.Extension):
    """
    Wraps a section of code in <script type="text/html" id="ID">

    ID is a required argument.

    Example, using underscore/ejs::

        {% canhaz "user" %}
        <div class="user">
            <p><%= name %></p>
        </div>
        {% endcanhaz %}

    Outputs::

        <script type="text/html" id="user">
        <div class="user">
            <p><%= name %></p>
        </div>
        </script>

    If you are using mustache, use the {% raw %} tags::

        {% canhaz "user" %}{% raw %}
        <div class="user">
            <p>{{ name }}</p>
        </div>
        {% endraw %}{% endcanhaz %}
    """
    tags = ('canhaz',)

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        try:
            args = [parser.parse_expression()]
        except jinja2.exceptions.TemplateSyntaxError as e:
            e.args = ("Expected canhaz script id",)
            raise

        body = parser.parse_statements(
            ['name:endcanhaz'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('canhaz_support', args),
            [],
            [],
            body
        ).set_lineno(lineno)

    def canhaz_support(self, script_id, caller):
        return u"""<script type="text/html" id="{script_id}">{content}</script>""".format(script_id=script_id, content=caller())
