from cachish.backends import Hawk

import responses

@responses.activate
def test_hawk_backend():
    response = {
        "key1": "value1",
        "key2": "value2",
    }
    responses.add(responses.GET, 'https://example.com',
        json=response)
    config = {
        'secret_id': 'mysecretID',
        'secret': 'youreawizardharry',
        'algorithm': 'sha256',
        'url': 'https://example.com',
    }
    backend = Hawk(**config)
    value = backend.get()

    assert value == response
    auth_header = responses.calls[0].request.headers.get('authorization')

    assert auth_header.startswith('Hawk')
    assert'id=\"mysecretID\"' in auth_header

@responses.activate
def test_hawk_field():
    response = {
        "key1": "value1",
        "key2": "value2",
    }
    responses.add(responses.GET, 'https://example.com',
        json=response)
    config = {
        'secret_id': 'mysecretID',
        'secret': 'youreawizardharry',
        'algorithm': 'sha256',
        'url': 'https://example.com',
        'field': 'key1'
    }
    backend = Hawk(**config)
    value = backend.get()

    auth_header = responses.calls[0].request.headers.get('authorization')
    assert auth_header.startswith('Hawk')
    assert'id=\"mysecretID\"' in auth_header

    assert len(responses.calls) == 1
    assert value == {'key1': 'value1'}
