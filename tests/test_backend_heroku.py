from cachish.backends import Heroku

import responses


@responses.activate
def test_heroku_backend():
	responses.add(responses.GET, 'https://api.heroku.com/apps/myapp/config-vars',
		body='{"DATABASE_URL": "postgres://mydbhost"}', content_type='application/json')

	config = {
		'heroku_api_token': 'foobar',
		'heroku_app': 'myapp',
		'config_key': 'DATABASE_URL',
	}
	backend = Heroku(**config)
	value = backend.get()
	assert len(responses.calls) == 1
	assert value == 'postgres://mydbhost'
