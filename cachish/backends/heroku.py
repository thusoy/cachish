from requests import Session


class Heroku(object):
    def __init__(self,
            heroku_api_token=None,
            heroku_app=None,
            config_key=None,
            ):
        assert heroku_api_token is not None
        assert heroku_app is not None
        assert config_key is not None
        self.config_key = config_key
        self.session = Session()
        self.target_url = 'https://api.heroku.com/apps/%s/config-vars' % heroku_app
        self.session.headers.update({
            'Authorization': 'Bearer %s' % heroku_api_token,
        })


    def get(self):
        response = self.session.get(self.target_url, timeout=5)
        response.raise_for_status()
        config = response.json()
        return config[self.config_key]
