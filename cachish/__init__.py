import binascii
import fnmatch
import hashlib
import json
import logging
import logging.config
import os
import time
from functools import wraps

import yaml
from flask import Flask, jsonify, request, Response, current_app, abort
from flask_canonical import CanonicalLogger

from . import backends
from . import cache
from . import utils
from ._version import __version__

_canonical_logger = CanonicalLogger()
_logger = logging.getLogger(__name__)


def create_app(
        auth=None,
        items=None,
        cache_dir='/var/cache/cachish',
        log_config=None,
    ): # pylint: disable=too-many-arguments
    app = Flask(__name__, static_folder=None)

    if items:
        add_item_views(items, app)

    _canonical_logger.init_app(app)
    configure_logging(log_config)

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
        _canonical_logger.tag = module.tag
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
            _logger.exception('Failed to get value from %s', module)
            fresh = False
            try:
                value = cache.read_from_cache()
            except FileNotFoundError:
                abort(503)

        cache_status = 'miss' if fresh else 'hit'
        _canonical_logger.add_measure('timing_backend', backend_end_time - backend_start_time)
        _canonical_logger.add('cache', cache_status)

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
        _logger.debug('Rejecting unknown token "%s"', token)
        abort(403)

    _canonical_logger.add('auth', token_spec['name'])

    token_globs = token_spec['url']

    # If there's only a single glob, transform to list
    if isinstance(token_globs, str):
        token_globs = [token_globs]

    for pattern in token_globs:
        if fnmatch.fnmatchcase(requested_url, pattern):
            break
    else:
        _logger.debug('Token "%s" has no patterns matching the current url of %s',
            token, requested_url)
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
        _canonical_logger.add('auth_method', None)
        basic_auth = request.authorization
        if basic_auth:
            token = basic_auth.username
            _canonical_logger.add('auth_method', 'basic')
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
            _canonical_logger.add('auth_method', 'bearer')

        if not check_auth(token):
            return authenticate()

        return view(*args, **kwargs)
    return decorated


def configure_logging(log_config):
    # Set some sensible default that can be overridden through for each deployment
    default_log_config = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(levelname)-10s %(name)s %(message)s',
            },
            'canonical': {
                'format': '%(asctime)s %(message)s',
            },
        },
        'handlers': {
            'stdout_canonical': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'canonical',
                'stream': 'ext://sys.stdout',
            },
            'stdout': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'cachish': {
                'level': 'INFO',
                'handlers': ['stdout'],
                'propagate': False,
            },
            'cachish.canonical': {
                'level': 'INFO',
                'handlers': ['stdout_canonical'],
                'propagate': False,
            },
            'werkzeug': {
                'level': 'WARNING',
                'handlers': ['stdout'],
                'propagate': False,
            },
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['stdout'],
        },
        'disable_existing_loggers': False,
    }

    if log_config:
        utils.merge_dicts(default_log_config, log_config)

    logging.config.dictConfig(default_log_config)
