from cachish.backends import JsonHttp

import responses


@responses.activate
def test_heroku_backend():
    response = {"key": "value"}
    responses.add(responses.GET, 'https://example.com',
        json=response)

    config = {
        'url': 'https://example.com',
        'field': 'key',
    }
    backend = JsonHttp(**config)
    value = backend.get()
    assert len(responses.calls) == 1
    assert value == response
