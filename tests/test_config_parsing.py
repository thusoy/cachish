import contextlib
import os
import tempfile
import textwrap

from cachish import create_app_from_file

def test_parsing_normal():
    config = textwrap.dedent('''\
        items:
            /database-url:
                module: "Heroku"
                parameters:
                    app: "myapp"
                    api_token: "footoken"
                    config_key: "MYKEY"

        auth:
            footoken: "/database-url"

        cache_dir: "/tmp"
    ''')

    with create_test_config(config) as config_file:
        app = create_app_from_file(config_file)

    has_url_endpoint = False
    for rule in app.url_map.iter_rules():
        if rule.rule == '/database-url':
            has_url_endpoint = True
            break
    assert has_url_endpoint
    assert app.config.auth == {
        'footoken': '/database-url',
    }
    assert app.config.cache_dir == '/tmp'


@contextlib.contextmanager
def create_test_config(contents):
    config_file = tempfile.NamedTemporaryFile(delete=False)
    config_file.write(contents.encode('utf-8'))
    config_file.close()

    yield config_file.name

    try:
        os.remove(config_file.name)
    except OSError:
        pass
