import fnmatch
import logging

from flask import abort, current_app, request

from . import events

_logger = logging.getLogger(__name__)


def get_auth_token():
    events.add('auth_method', None)
    basic_auth = request.authorization
    if basic_auth:
        token = basic_auth.username
        events.add('auth_method', 'basic')
    else:
        auth = request.headers.get('authorization')
        if auth is None:
            abort(401)
        try:
            scheme, token = auth.split(None, 1)
        except ValueError:
            abort(400)
        if not scheme.lower() == 'bearer':
            abort(400)
        events.add('auth_method', 'bearer')

    return token


def check_auth(token):
    """This function is called to check if a token /
    url combination is valid.
    """
    requested_url = request.path
    token_spec = current_app.config.auth.get(token)
    if not token_spec:
        _logger.debug('Rejecting unknown token "%s"', token)
        abort(403)

    events.add('auth', token_spec['name'])

    token_globs = token_spec['url']

    # If there's only a single glob, transform to list
    if isinstance(token_globs, str):
        token_globs = [token_globs]

    for pattern in token_globs:
        if fnmatch.fnmatchcase(requested_url, pattern):
            return

    _logger.debug('Token "%s" has no patterns matching the current url of %s',
        token, requested_url)
    abort(403)
