from mohawk import Sender
from .json_http import JsonHttp

class Hawk(JsonHttp):
    def __init__(self,
            secret_id=None,
            secret=None,
            algorithm='sha256',
            url=None,
            field=None,
            ): # pylint: disable=too-many-arguments
        assert secret_id is not None
        assert secret is not None
        assert algorithm is not None

        self.secret_id = secret_id
        self.secret = secret
        self.algorithm = algorithm
        super(Hawk, self).__init__(url=url, field=field) #sets self.target_url

    @property
    def tag(self):
        return f'Hawk/{self.target_url}'

    # For a GET request, Mohawk requires empty strings for content/content_type
    # See http://mohawk.readthedocs.io/en/latest/usage.html 'Sending a Request'
    def get(self):
        sender = Sender({
                'id': self.secret_id,
                'key': self.secret,
                'algorithm': self.algorithm,
            },
            self.target_url,
            'GET',
            '',
            '')
        # Mohawk provides this authorization header, should start with Hawk
        auth = {'authorization': sender.request_header}
        response = self.session.get(self.target_url, timeout=5, headers=auth)
        response.raise_for_status()
        response_json = response.json()

        if not self.fields:
            return response_json
        return {key: response_json[key] for key in self.fields}
