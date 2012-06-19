import os
from os.path import join
from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents


@will_generate('filters_site')
def test_filters_site(config):
    strange_case(config)

    path_contents = {
        'index.html': """
12 May 2012
Sat May 12 09:59:11 2012

12 May 2012
Sat May 12 09:59:11 2012

<p>Some <em>markdown</em> text</p>

d8f4590320e1343a915b6394170650a8f35d6926

words

["more\\n\\ttext"]

d15aacfd-62b6-594e-93cf-85baa5e441ec""",
    }
    check_path_contents(config['deploy_path'], path_contents)


@will_generate('basic_site')
def test_basic_site_remove_existing(config):
    # create extra files
    # this file does not exist in path_contents, and so
    # should be removed
    os.mkdir(config['deploy_path'])
    with open(join(config['deploy_path'], 'rm_this'), 'w') as f:
        f.write('blablabla')

    strange_case(config)

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
