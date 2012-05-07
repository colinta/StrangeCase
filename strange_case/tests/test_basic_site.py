import os
from os.path import join
import yaml
from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents, tree


@will_generate('basic_site/public')
def test_basic_site(config):
    config['project_path'] = project_path = join(os.path.dirname(__file__), 'basic_site')
    config_path = join(project_path, 'config.yaml')
    config['site_path'] = join(project_path, 'site')
    config['deploy_path'] = join(project_path, 'public')

    with open(config_path, 'r') as config_file:
        yaml_config = yaml.load(config_file)
        config.update(yaml_config)

    try:
        strange_case(config)

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
<p>My first post</p>
</body>""",
            '2012_01_02_post2.html': """<doctype html>
<body>
<p>My second post</p>
</body>""",
            },
        }
        check_path_contents(config['deploy_path'], path_contents)
    except Exception:
        tree(config['site_path'], config['project_path'])
        tree(config['deploy_path'], config['project_path'])
        raise


@will_generate('basic_site/public')
def test_basic_site_remove_existing(config):
    config['project_path'] = project_path = join(os.path.dirname(__file__), 'basic_site')
    config_path = join(project_path, 'config.yaml')
    config['site_path'] = join(project_path, 'site')
    config['deploy_path'] = join(project_path, 'public')

    with open(config_path, 'r') as config_file:
        yaml_config = yaml.load(config_file)
        config.update(yaml_config)

    # create extra files
    # this file does not exist in path_contents, and so
    # should be removed
    os.mkdir(config['deploy_path'])
    with open(join(config['deploy_path'], 'rm_this'), 'w') as f:
        f.write('blablabla')

    try:
        strange_case(config)
    except Exception:
        tree(config['site_path'], config['project_path'])
        tree(config['deploy_path'], config['project_path'])
        raise

    path_contents = {
        '001_2012_01_16_file.html': True,
        'index.html': True,
        'blogs': {
            'index.html': True,
            '2012_01_01_post1.html': True,
            '2012_01_02_post2.html': True,
        },
    }
    check_path_contents(config['deploy_path'], path_contents)
