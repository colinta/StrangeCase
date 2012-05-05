import os
import re
from os.path import join
import yaml
from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents, tree


@will_generate('category_site/public')
def test_category_site(config):
    config['project_path'] = project_path = join(os.path.dirname(__file__), 'category_site')
    config_path = join(project_path, 'config.yaml')
    config['site_path'] = join(project_path, 'site')
    config['deploy_path'] = join(project_path, 'public')

    with open(config_path, 'r') as config_file:
        yaml_config = yaml.load(config_file)
        config.update(yaml_config)

    try:
        strange_case(config)

        path_contents = {
            'index.html': True,
            'blogs': {
                'index.html': True,
                '2012_01_01_post1.html': True,
                '2012_01_02_post2.html': True,
            },
            'categories': {
                'index.html': [
                    'Categories (2)',
                    '<a href="/categories/good.html">good</a>',
                    '<a href="/categories/bad.html">bad</a>'
                ],
                'good.html': ['Category: good'],
                'bad.html': ['Category: bad'],
            },
        }
        check_path_contents(config['deploy_path'], path_contents)
    except Exception:
        tree(config['site_path'], config['project_path'])
        tree(config['deploy_path'], config['project_path'])
        raise
