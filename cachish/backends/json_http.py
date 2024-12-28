from requests import Session

from .._version import __version__


class JsonHttp(object):
    user_agent = f'cachish/{__version__} (https://github.com/thusoy/cachish)'

    def __init__(self,
            url=None,
            field=None,
            ):
        assert url is not None
        self.session = Session()
        self.session.trust_env = False # ignore .netrc auth
        self.session.headers.update({
            'User-Agent': self.user_agent,
        })
        self.target_url = url

        if field:
            self.fields = [field] if isinstance(field, str) else field
        else:
            self.fields = None


    def get(self):
        response = self.session.get(self.target_url, timeout=5)
        response.raise_for_status()
        response_json = response.json()
        if not self.fields:
            return response_json
        return {key: response_json[key] for key in self.fields}


    @property
    def tag(self):
        return f'JsonHttp/{self.target_url}'
