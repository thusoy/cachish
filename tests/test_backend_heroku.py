from cachish.backends import Heroku

import responses


@responses.activate
def test_heroku_backend():
    response = {"DATABASE_URL": "postgres://mydbhost"}
    responses.add(responses.GET, 'https://api.heroku.com/apps/myapp/config-vars',
        json=response)

    config = {
        'api_token': 'foobar',
        'app': 'myapp',
        'config_key': 'DATABASE_URL',
    }
    backend = Heroku(**config)
    value = backend.get()
    assert len(responses.calls) == 1
    assert value == response
    assert responses.calls[0].request.headers.get('Authorization') == 'Bearer foobar'


@responses.activate
def test_heroku_backend_multiple_keys():
    response = {
        "DATABASE_URL": "postgres://mydbhost",
        "SESSION_SECRET": "supersecret",
    }
    responses.add(responses.GET, 'https://api.heroku.com/apps/myapp/config-vars',
        json=response)

    config = {
        'api_token': 'foobar',
        'app': 'myapp',
        'config_key': [
            'DATABASE_URL',
            'SESSION_SECRET',
        ],
    }
    backend = Heroku(**config)
    value = backend.get()
    assert len(responses.calls) == 1
    assert value == response
    assert responses.calls[0].request.headers.get('Authorization') == 'Bearer foobar'
