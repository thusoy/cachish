import binascii
import fnmatch
import hashlib
import json
import logging
import os
import time
from functools import wraps

import yaml
from flask import Flask, jsonify, request, Response, current_app, abort

from . import backends
from . import cache
from .middleware import CanonicalLoggerMiddleware
from ._version import __version__

canonical_logger = CanonicalLoggerMiddleware()


def create_app(auth=None, items=None, cache_dir='/var/cache/cachish'):
    app = Flask(__name__, static_folder=None)

    if items:
        add_item_views(items, app)

    canonical_logger.init_app(app)

    app.config.auth = transform_auth(auth)
    app.config.cache_dir = cache_dir
    add_error_handlers(app)

    # Ensure errors are caught at start time and not at request time
    cache.test_cache_dir_writeable(cache_dir)

    return app


def transform_auth(auth):
    ''' Transform a name: {token, url} to token: {name, url} to enable
    constant-time lookup based on the token
    '''
    if not auth:
        return {}

    transformed_auth = {}
    for name, params in auth.items():
        assert 'url' in params, 'auth must specify a url'
        assert 'token' in params, 'auth must specify a token'
        transformed_auth[params['token']] = {
            'name': name,
            'url': params['url'],
        }

    return transformed_auth


def add_item_views(items, app):
    for url, endpoint_config in items.items():
        module_name = endpoint_config['module']
        parameters = endpoint_config.get('parameters', {})
        module = get_module(module_name, parameters)
        app.add_url_rule(url, endpoint=url, view_func=create_view_for_value(module))


def create_app_from_file(filename=None):
    if filename is None:
        filename = os.environ['CACHISH_CONFIG_FILE']
    with open(filename) as fh:
        config = yaml.load(fh) or {}
    return create_app(**config)


def get_module(name, parameters):
    constructor = getattr(backends, name)
    return constructor(**parameters)


def create_view_for_value(module):

    @requires_auth
    def view():
        fresh = True
        canonical_logger.tag = module.tag
        headers = {
            'Content-Type': 'application/json',
            'Server': 'Cachish/%s' % __version__,
        }
        backend_start_time = time.time()
        try:
            value = module.get()
            backend_end_time = time.time()
        except: # pylint: disable=bare-except
            backend_end_time = time.time()
            logging.exception('Failed to get value from %s', module)
            fresh = False
            try:
                value = cache.read_from_cache()
            except FileNotFoundError:
                abort(503)

        cache_status = 'miss' if fresh else 'hit'
        canonical_logger.add_measure('timing_backend', backend_end_time - backend_start_time)
        canonical_logger.add_to_log('cache', cache_status)

        if fresh:
            cache.write_to_cache(value)

        headers['X-Cache'] = cache_status

        return json.dumps(value), 200, headers

    return view


def add_error_handlers(app):

    def error_503(error): # pylint: disable=unused-argument
        return 'Upstream failure', 503, {
            'X-Cache': 'miss',
        }

    app.register_error_handler(503, error_503)


def check_auth(token):
    """This function is called to check if a token /
    url combination is valid.
    """
    requested_url = request.path
    token_spec = current_app.config.auth.get(token)
    if not token_spec:
        print('no accesses for token %s' % token)
        abort(403)

    token_globs = token_spec['url']

    # If there's only a single glob, transform to list
    if isinstance(token_globs, str):
        token_globs = [token_globs]

    for pattern in token_globs:
        if fnmatch.fnmatchcase(requested_url, pattern):
            break
    else:
        print('No patterns for token %s' % token)
        abort(403)

    return True


def authenticate():
    """Sends a 401 response that enables basic auth"""
    message = ('Could not verify your access level for that URL.\n'
        'Send a Bearer authorization header with your access token')
    return Response(message, 401, {})


def requires_auth(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        auth = request.headers.get('authorization')
        if not auth:
            abort(401)
        auth_parts = auth.split()
        if not len(auth_parts) == 2:
            abort(400)
        scheme, token = auth_parts
        if not scheme.lower() == 'bearer':
            abort(400)

        if not check_auth(token):
            return authenticate()

        return view(*args, **kwargs)
    return decorated
