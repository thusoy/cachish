import fnmatch
import logging

from flask import abort, current_app, request

from . import events

_logger = logging.getLogger(__name__)


def get_auth_token():
    events.add('auth_method', None)
    auth = request.authorization
    if not auth:
        abort(401)

    if auth.type not in ('bearer', 'basic'):
        abort(400)

    token = auth.token if auth.type == 'bearer' else auth.parameters['username']
    events.add('auth_method', auth.type)

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
