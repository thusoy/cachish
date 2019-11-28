import warnings
import shutil
import tempfile

import pytest

from cachish import create_app

# Ensure warnings are treated as errors when running tests
warnings.filterwarnings('error', module='cachish')


@pytest.fixture
def app():
    cache_dir = tempfile.mkdtemp()
    config = {
        'items': {
            '/heroku/database-url': {
                'module': 'Heroku',
                'parameters': {
                    'app': 'myapp',
                    'api_token': 'footoken',
                    'config_key': 'MYKEY',
                }
            },
            '/no-auth': {
                'module': 'JsonHttp',
                'disable_auth': True,
                'parameters': {
                    'url': 'https://api.github.com/meta',
                    'field': 'git',
                }
            },
        },
        'auth': {
            'client_name': {
                'token': 'footoken',
                'url': '/heroku/*',
            },
            'old_client': {
                'token': 'oldtoken',
                'url': [],
            },
        },
        'cache_dir': cache_dir,
    }

    yield create_app(**config)

    shutil.rmtree(cache_dir)



@pytest.fixture
def client(app): # pylint: disable=redefined-outer-name
    return app.test_client()
