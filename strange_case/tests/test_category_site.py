import pytest
from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents


@will_generate('category_site')
def test_category_site(config):
    strange_case(config)

    path_contents = {
        'index.html': True,
        'blogs': {
            'index.html': True,
            '2012_01_01_post1.html': True,
            '2012_01_02_post2.html': True,
        },
        'zee_categories': {
            'index.html': [
                'Categories (2)',
                '<a href="/zee_categories/good.html">good</a>',
                '<a href="/zee_categories/bad.html">bad</a>'
            ],
            'good.html': ['Category: good', 'Boring category page.'],
            'bad.html': ['Category: bad', 'This category is bad.'],
        },
    }
    check_path_contents(config['deploy_path'], path_contents)


@will_generate('missing_category_site')
def test_missing_category_site(config):
    with pytest.raises(NotImplementedError):
        strange_case(config)


@will_generate('category_site')
def test_build_category_site_twice(config):
    strange_case(config)
    strange_case(config)

    path_contents = {
        'index.html': True,
        'blogs': {
            'index.html': True,
            '2012_01_01_post1.html': True,
            '2012_01_02_post2.html': True,
        },
        'zee_categories': {
            'index.html': [
                'Categories (2)',
                '<a href="/zee_categories/good.html">good</a>',
                '<a href="/zee_categories/bad.html">bad</a>'
            ],
            'good.html': ['Category: good', 'Boring category page.'],
            'bad.html': ['Category: bad', 'This category is bad.'],
        },
    }
    check_path_contents(config['deploy_path'], path_contents)
