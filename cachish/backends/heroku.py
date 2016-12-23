from requests import Session


class Heroku(object):
    def __init__(self,
            api_token=None,
            app=None,
            config_key=None,
            ):
        assert api_token is not None
        assert app is not None
        assert config_key is not None
        self.config_key = config_key
        self.session = Session()
        self.target_url = 'https://api.heroku.com/apps/%s/config-vars' % app
        self.session.headers.update({
            'Authorization': 'Bearer %s' % api_token,
            'Accept': 'application/vnd.heroku+json; version=3',
        })


    def get(self):
        response = self.session.get(self.target_url, timeout=5)
        response.raise_for_status()
        config = response.json()
        return config[self.config_key]
