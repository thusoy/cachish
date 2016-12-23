import warnings
import shutil
import tempfile

import pytest

from cachish import create_app

# Ensure warnings are treated as errors when running tests
# TODO: Temporarily disabled since responses uses a deprecated API (inspect.getargspec) that is
# restored in 3.6 (ref. https://github.com/getsentry/responses/issues/90 and
# https://bugs.python.org/issue25486). Might or might not be fixed in 3.5.2, at least restored in
# 3.6. Might fork responses to use inspect.signature instead.
#warnings.filterwarnings('error')


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
        },
        'auth': {
            'footoken': '/heroku/*'
        },
        'cache_dir': cache_dir,
    }

    yield create_app(**config)

    shutil.rmtree(cache_dir)



@pytest.fixture
def client(app): # pylint: disable=redefined-outer-name
    return app.test_client()
