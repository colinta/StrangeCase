from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents


@will_generate('basic_site')
def test_strip_extensions_and_meta_site(config):
    config['configurators'].append('strange_case.extensions.configurators.strip_extensions')
    config['strip_metadata_from_name'] = True
    config['strip_metadata_from_target_name'] = True

    strange_case(config)

    path_contents = {
        'file.html': '1. 2012-01-16',
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
<li><p><a href="/blogs/post1">Post1</a></p></li>
<li><p><a href="/blogs/post2">Post2</a></p></li>
</ol>
<p>Hi!</p>

</body>""",
            'post1.html': """<doctype html>
<body>
<p>My first post, on 2012-01-01.</p>
</body>""",
            'post2.html': """<doctype html>
<body>
<p>My second post, on 2012-01-02.</p>
</body>""",
        },
    }
    check_path_contents(config['deploy_path'], path_contents)
