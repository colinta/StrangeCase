import os
import re
from os.path import join
import yaml
from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents, tree


@will_generate('paginated_site/public')
def test_paginated_site(config):
    config['project_path'] = project_path = join(os.path.dirname(__file__), 'paginated_site')
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
                'index.html': [
                    '<li><a href="/blogs/2012_01_01_post1.html">Post1</a></li>',
                    '<li><a href="/blogs/2012_01_02_post2.html">Post2</a></li>',
                    '<p>&lsaquo; First</p>',
                    '<p>Page 1 of 3, items 1 to 2</p>',
                    '<a href="/blogs/pagina2.html">Página 2</a> &rsaquo;'
                ],
                'pagina2.html': [
                    '<li><a href="/blogs/2012_01_03_post3.html">Post3</a></li>',
                    '<li><a href="/blogs/2012_01_04_post4.html">Post4</a></li>',
                    '<p>&lsaquo; <a href="/blogs/">Blogs</a></p>',
                    '<p>Page 2 of 3, items 3 to 4</p>',
                    '<a href="/blogs/pagina3.html">Página 3</a> &rsaquo;'
                ],
                'pagina3.html': [
                    '<li><a href="/blogs/2012_01_05_post5.html">Post5</a></li>',
                    '<p>&lsaquo; <a href="/blogs/pagina2.html">Página 2</a></p>',
                    '<p>Page 3 of 3, item 5</p>',
                    '<p>&rsaquo; Last</p>'
                ],
                '2012_01_01_post1.html': True,
                '2012_01_02_post2.html': True,
                '2012_01_03_post3.html': True,
                '2012_01_04_post4.html': True,
                '2012_01_05_post5.html': True,
            },
        }
        check_path_contents(config['deploy_path'], path_contents)
    except Exception:
        tree(config['site_path'], config['project_path'])
        tree(config['deploy_path'], config['project_path'])
        raise
