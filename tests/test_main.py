import base64
import hashlib
import json
import os
import stat
from unittest import mock

import pytest
import responses
from requests.exceptions import HTTPError


@responses.activate
def test_working_call(client):
    responses.add(responses.GET, 'https://api.heroku.com/apps/myapp/config-vars',
        json={"MYKEY": "MYVALUE"})

    heroku_mock = mock.Mock(return_value='postgres://mydbhost')

    with mock.patch('cachish.backends.Heroku', heroku_mock):
        response = client.get('/heroku/database-url', headers={
            'authorization': 'Bearer footoken',
        })

    assert response.status_code == 200
    assert response.headers.get('x-cache') == 'miss'

    # Should have written to cache
    cache_filename = hashlib.sha256(b'/heroku/database-url').hexdigest()
    cache_file = os.path.join(client.application.config.cache_dir, cache_filename)
    with open(cache_file) as fh:
        assert json.load(fh) == {'MYKEY': 'MYVALUE'}
    cache_stat = os.stat(cache_file)
    cache_mode = stat.S_IMODE(cache_stat.st_mode)
    assert cache_mode == 0o400
    assert 'Cachish' in response.headers['server']


@responses.activate
def test_working_username_auth(client):
    responses.add(responses.GET, 'https://api.heroku.com/apps/myapp/config-vars',
        json={"MYKEY": "MYVALUE"})

    heroku_mock = mock.Mock(return_value='postgres://mydbhost')

    with mock.patch('cachish.backends.Heroku', heroku_mock):
        response = client.get('/heroku/database-url', headers={
            'authorization': create_basic_auth_header('footoken'),
        })

    assert response.status_code == 200
    assert response.headers.get('x-cache') == 'miss'


def create_basic_auth_header(token):
    username = '%s:' % token
    encoded_username = base64.b64encode(username.encode('utf-8'))
    return 'Basic %s' % encoded_username.decode('utf-8')


def test_auth_404(client):
    assert client.get('/some/path').status_code == 404
    assert client.get('/heroku/database-url/some/subpath').status_code == 404


@pytest.mark.parametrize('invalid_auth', (
    '',
    'foo',
    'unknown thing',
    'lots of stuff',
))
def test_invalid_auth(client, invalid_auth):
    response = client.get('/heroku/database-url', headers={
        'authorization': invalid_auth,
    })
    assert response.status_code == 400


@pytest.mark.parametrize('unknown_token', (
    create_basic_auth_header('badtoken'),
    'Bearer badtoken',
))
def test_unknown_auth_token(client, unknown_token):
    response = client.get('/heroku/database-url', headers={
        'authorization': unknown_token,
    })
    assert response.status_code == 403


def test_token_without_allowed_urls(client):
    response = client.get('/heroku/database-url', headers={
        'authorization': 'Bearer oldtoken',
    })
    assert response.status_code == 403


def test_no_token(client):
    response = client.get('/heroku/database-url')
    assert response.status_code == 401


@responses.activate
def test_backend_failure_no_cached(client):
    error = HTTPError('oops')
    responses.add(responses.GET, 'https://api.heroku.com/apps/myapp/config-vars',
        body=error)

    response = client.get('/heroku/database-url', headers={
        'authorization': 'bearer footoken',
    })
    assert response.status_code == 503
    assert response.headers.get('x-cache') == 'miss'


@responses.activate
def test_backend_failure_cached(client):
    error = HTTPError('oops')
    responses.add(responses.GET, 'https://api.heroku.com/apps/myapp/config-vars',
        body=error)

    application_cache_dir = client.application.config.cache_dir
    cache_filename = hashlib.sha256(b'/heroku/database-url').hexdigest()
    cache_file = os.path.join(application_cache_dir, cache_filename)
    with open(cache_file, 'w') as fh:
        fh.write('{"MYKEY": "MYCACHEDVALUE"}')

    response = client.get('/heroku/database-url', headers={
        'authorization': 'bearer footoken',
    })
    assert response.status_code == 200
    assert json.loads(response.data.decode('utf-8')) == {
        'MYKEY': 'MYCACHEDVALUE',
    }
    assert response.headers.get('x-cache') == 'hit'
