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
        target_url = 'https://api.heroku.com/apps/%s/config-vars' % app
        super(Heroku, self).__init__(url=target_url, field=config_key)
        self.session.headers.update({
            'Authorization': 'Bearer %s' % api_token,
            'Accept': 'application/vnd.heroku+json; version=3',
        })


    @property
    def tag(self):
        return 'Heroku/%s' % self.app
