import contextlib
import os
import shutil
import tempfile
import textwrap
from unittest import mock

from cachish import create_app_from_file

CONFIG = textwrap.dedent('''\
    items:
        /database-url:
            module: "Heroku"
            parameters:
                app: "myapp"
                api_token: "footoken"
                config_key: "MYKEY"

    auth:
        client_name:
            token: footoken
            url: "/database-url"

    cache_dir: "{cache_dir}"
''')

MULTI_ENDPOINT_CONFIG = textwrap.dedent('''\
    items:
        /item1:
            module: "Heroku"
            parameters:
                app: "app1"
                api_token: "token1"
                config_key: "key1"

        /item2:
            module: "Heroku"
            parameters:
                app: "app2"
                api_token: "token2"
                config_key: "key2"

    auth:
        client1:
            token: clienttoken1
            url: "/item1"
        client2:
            token: clienttoken2
            url: "/item2"

    cache_dir: "{cache_dir}"
''')


def test_parsing_normal():
    with create_test_config(CONFIG) as config_file:
        app = create_app_from_file(config_file)

    has_url_endpoint = False
    for rule in app.url_map.iter_rules():
        if rule.rule == '/database-url':
            has_url_endpoint = True
            break
    assert has_url_endpoint
    assert app.config.auth == {
        'footoken': {
            'name': 'client_name',
            'url': '/database-url',
        },
    }


def test_parsing_multiple():
    with create_test_config(MULTI_ENDPOINT_CONFIG) as config_file:
        app = create_app_from_file(config_file)


def test_parsing_env_var():
    with create_test_config(CONFIG) as config_file:
        env = {
            'CACHISH_CONFIG_FILE': config_file,
        }
        with mock.patch.dict(os.environ, env):
            app = create_app_from_file()

    assert app.config.auth == {
        'footoken': {
            'name': 'client_name',
            'url': '/database-url',
        },
    }


@contextlib.contextmanager
def create_test_config(contents):
    config_file = tempfile.NamedTemporaryFile(delete=False)
    tempdir = tempfile.mkdtemp()
    config_file.write(contents.format(cache_dir=tempdir).encode('utf-8'))
    config_file.close()

    yield config_file.name

    try:
        os.remove(config_file.name)
    except OSError:
        pass

    shutil.rmtree(tempdir)
