import os
from os.path import join
from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents, basic_config


def test_basic_site(basic_config):
    strange_case(basic_config)

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
<li><p><a href="/blogs/2012_01_01_post1.html">Post1</a></p></li>
<li><p><a href="/blogs/2012_01_02_post2.html">Post2</a></p></li>
</ol>
<p>Hi!</p>

</body>""",
            '2012_01_01_post1.html': """<doctype html>
<body>
<p>My first post, on 2012-01-01.</p>
</body>""",
            '2012_01_02_post2.html': """<doctype html>
<body>
<p>My second post, on 2012-01-02.</p>
</body>""",
        },
    }
    check_path_contents(basic_config['deploy_path'], path_contents)


def test_basic_site_remove_existing(basic_config):
    # create extra files
    # this file does not exist in path_contents, and so
    # should be removed
    os.mkdir(basic_config['deploy_path'])
    with open(join(basic_config['deploy_path'], 'rm_this'), 'w') as f:
        f.write('blablabla')

    strange_case(basic_config)

    path_contents = {
        '001_2012_01_16_file.html': True,
        'index.html': True,
        'blogs': {
            'index.html': True,
            '2012_01_01_post1.html': True,
            '2012_01_02_post2.html': True,
        },
    }
    check_path_contents(basic_config['deploy_path'], path_contents)
