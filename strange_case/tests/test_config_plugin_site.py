from strange_case.__main__ import run
from strange_case.tests import will_generate, check_path_contents


@will_generate('config_plugin_site')
def test_config_plugin_site(config):
    run()

    path_contents = {
        'index.html': """<doctype html>
<body>
<h1 id="welcome-to-my-blog">Welcome to my blog!</h1>

<p>It is so UGLY!.</p>
</body>""",
            'blogs': {
                'index.html': """<doctype html>
<body>
<p>My blogs:</p>

<ol>
<li><p><a href="/blogs/2012_01_01_post1.html">BIRD Post1 BIRD</a></p></li>
<li><p><a href="/blogs/2012_01_02_post2.html">BIRD Post2 BIRD</a></p></li>
</ol>
<p>Hi!</p>

</body>""",
            '2012_01_01_post1.html': True,
            '2012_01_02_post2.html': True,
        },
    }
    check_path_contents(config['deploy_path'], path_contents)
