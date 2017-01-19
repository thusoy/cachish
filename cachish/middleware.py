import time
import re
from collections import OrderedDict

from flask import request, g


WHITESPACE_RE = re.compile('\s')


class CanonicalLogLineMiddleware(object):
    '''See https://brandur.org/canonical-log-lines for an intro to canonical log lines'''

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

        # Set default status code in case after_request isn't called due to
        # an unhandled exception
        self.response_status = 500


    def init_app(self, app):
        self.app = app

        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)


    def before_request(self):
        self.start_time = time.time()


    def add_to_log(self, key, value):
        g.setdefault('log_extra', []).append((key, value))


    def after_request(self, response):
        self.response_status = response.status_code
        return response


    def teardown_request(self, exception):
        params = OrderedDict((
            ('service', 'cachish'),
            ('request_method', request.method),
            ('request_path', request.path),
            ('request_user_agent', request.headers.get('user-agent')),
            ('response_status', self.response_status),
            ('timing_total', '%.3f' % (time.time() - self.start_time)),
        ))

        for key, value in g.get('log_extra', ()):
            params[key] = value

        if exception:
            params['error'] = exception.__class__.__name__
            params['error_msg'] = str(exception)

        log_line_items = (format_key_value_pair(key, val) for (key, val) in params.items())
        print('canonical-log-line %s' % ' '.join(log_line_items))


def format_key_value_pair(key, value):
    if value:
        value = str(value)
    else:
        value = ''

    should_quote = WHITESPACE_RE.search(value)

    if should_quote:
        value = '"%s"' % value

    return '%s=%s' % (key, value)
