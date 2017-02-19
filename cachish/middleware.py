# pylint: disable=protected-access,no-self-use

import time
import re
from collections import OrderedDict
from logging import getLogger

from flask import request, g
from werkzeug.routing import RequestRedirect, MethodNotAllowed, NotFound

from ._version import __version__

WHITESPACE_RE = re.compile(r'\s')

_logger = getLogger('cachish.canonical')


class CanonicalLoggerMiddleware(object):
    '''See https://brandur.org/canonical-log-lines for an intro to canonical log lines'''

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)


    def init_app(self, app):
        self.app = app

        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)


    def before_request(self):
        g._canonical_start_time = time.time()


    def add_to_log(self, key, value):
        self._add_extra(key, value)


    def add_measure(self, key, value):
        self._add_extra('measure#%s' % key, '%.3fs' % value)


    def _add_extra(self, key, value):
        g.setdefault('_canonical_log_extra', []).append((key, value))


    @property
    def tag(self):
        return g.get('_canonical_tag') or get_default_tag(self.app)


    @tag.setter
    def tag(self, tag):
        g._canonical_tag = tag


    def after_request(self, response):
        g._canonical_response_status = response.status_code
        return response


    def teardown_request(self, exception):
        params = OrderedDict((
            ('service', 'cachish'),
            ('service_version', __version__),
            ('fwd', ','.join(request.access_route)),
            ('tag', self.tag),
            ('request_method', request.method),
            ('request_path', request.full_path if request.args else request.path),
            ('response_status', g.get('_canonical_response_status', 500)),
            ('#timing_total', '%.3f' % (time.time() - g._canonical_start_time)),
        ))

        for key, value in g.get('_canonical_log_extra', ()):
            params[key] = value

        if exception:
            params['error'] = exception.__class__.__name__
            params['error_msg'] = str(exception)

        log_line_items = (format_key_value_pair(key, val) for (key, val) in params.items())
        _logger.info('canonical-log-line %s', ' '.join(log_line_items))


def get_default_tag(app):
    '''Get the name of the view function used to prevent having to set the tag
    manually for every endpoint'''
    view_func = get_view_function(app, request.path, request.method)
    if view_func:
        return view_func.__name__


def get_view_function(app, url, method):
    """Match a url and return the view and arguments
    it will be called with, or None if there is no view.
    Creds: http://stackoverflow.com/a/38488506
    """
    # pylint: disable=too-many-return-statements

    adapter = app.create_url_adapter(request)

    try:
        match = adapter.match(url, method=method)
    except RequestRedirect as ex:
        # recursively match redirects
        return get_view_function(app, ex.new_url, method)
    except (MethodNotAllowed, NotFound):
        # no match
        return None

    try:
        return app.view_functions[match[0]]
    except KeyError:
        # no view is associated with the endpoint
        return None


def format_key_value_pair(key, value):
    if value:
        value = str(value)
    else:
        value = ''

    should_quote = WHITESPACE_RE.search(value)

    if should_quote:
        value = '"%s"' % value

    return '%s=%s' % (key, value)
