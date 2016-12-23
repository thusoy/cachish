from cachish.backends import Heroku

import responses


@responses.activate
def test_heroku_backend():
    responses.add(responses.GET, 'https://api.heroku.com/apps/myapp/config-vars',
        json={"DATABASE_URL": "postgres://mydbhost"})

    config = {
        'api_token': 'foobar',
        'app': 'myapp',
        'config_key': 'DATABASE_URL',
    }
    backend = Heroku(**config)
    value = backend.get()
    assert len(responses.calls) == 1
    assert value == 'postgres://mydbhost'
    assert responses.calls[0].request.headers.get('Authorization') == 'Bearer foobar'
