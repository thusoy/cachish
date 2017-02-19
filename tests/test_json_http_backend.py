from cachish.backends import JsonHttp

import responses


@responses.activate
def test_heroku_backend():
    response = {
        "key1": "value1",
        "key2": "value2",
    }
    responses.add(responses.GET, 'https://example.com',
        json=response)

    config = {
        'url': 'https://example.com',
        'field': 'key1',
    }
    backend = JsonHttp(**config)
    value = backend.get()
    assert len(responses.calls) == 1
    assert value == {'key1': 'value1'}


@responses.activate
def test_heroku_backend_no_field():
    response = {
        "key1": "value1",
        "key2": "value2",
    }
    responses.add(responses.GET, 'https://example.com',
        json=response)

    config = {
        'url': 'https://example.com',
    }
    backend = JsonHttp(**config)
    value = backend.get()
    assert len(responses.calls) == 1
    assert value == response
