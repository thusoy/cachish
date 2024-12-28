from .json_http import JsonHttp


class Heroku(JsonHttp):
    def __init__(self,
            api_token=None,
            app=None,
            config_key=None,
            ): # pylint: disable=too-many-arguments
        assert api_token is not None
        assert app is not None
        assert config_key is not None

        self.app = app
        target_url = f'https://api.heroku.com/apps/{app}/config-vars'
        super(Heroku, self).__init__(url=target_url, field=config_key)
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Accept': 'application/vnd.heroku+json; version=3',
        })


    @property
    def tag(self):
        return f'Heroku/{self.app}'
