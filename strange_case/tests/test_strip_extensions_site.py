from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents, tree


@will_generate('basic_site')
def test_strip_extensions_site(config):
    config['configurators'].append('strange_case.extensions.configurators.strip_extensions')

    try:
        strange_case(config)
    except Exception:
        tree(config['site_path'], config['project_path'])
        tree(config['deploy_path'], config['project_path'])
        raise

    path_contents = {
        '001_2012_01_16_file.html': '1. 2012-01-16',
        'index.html': """<doctype html>
<body>
<h1 id="welcome-to-my-blog">Welcome to my blog!</h1>

<p>It is pretty great.</p>
</body>""",
            'blogs': {
                'index.html': """<doctype html>
<body>
<p>My blogs:</p>

<ol>
<li><p><a href="/blogs/2012_01_01_post1">Post1</a></p></li>
<li><p><a href="/blogs/2012_01_02_post2">Post2</a></p></li>
</ol>
<p>Hi!</p>

</body>""",
            '2012_01_01_post1.html': """<doctype html>
<body>
<p>My first post</p>
</body>""",
            '2012_01_02_post2.html': """<doctype html>
<body>
<p>My second post</p>
</body>""",
        },
    }
    check_path_contents(config['deploy_path'], path_contents)
