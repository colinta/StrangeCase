from strange_case import strange_case
from strange_case.tests import will_generate, check_path_contents


@will_generate('override_site')
def test_override(config):
    # override configs that are otherwise not inherited,
    # but config.yaml and front matter should
    # override *that*
    strange_case(config)

    path_contents = {
        'overridden_from_files.html': '<h1>Overridden from files</h1>',
        'overridden_from_front_matter.html': '<h1>Overridden from front matter</h1>',
        'not_overridden.html': '<h1>Overridden</h1>',
        'index.html': '''<h1>Root title</h1>

/not_overridden.html => <h2>Overridden</h2>
/overridden_from_files.html => <h2>Overridden from files</h2>
/overridden_from_front_matter.html => <h2>Overridden from front matter</h2>''',
    }
    check_path_contents(config['deploy_path'], path_contents)
