import binascii
import hashlib
import json
import logging
import logging.config
import os
import time

import yaml
from flask import Flask, jsonify, request, Response, current_app, abort
from flask_events import Events

# Import early to prevent circular import issues
# pylint: disable=wrong-import-position
events = Events()

from . import backends
from . import cache
from . import utils
from ._version import __version__
from .auth import get_auth_token, check_auth

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

    events.init_app(app)
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
        disable_auth = endpoint_config.get('disable_auth', False)
        module = get_module(module_name, parameters)
        app.add_url_rule(url,
            endpoint=url,
            view_func=create_view_for_value(module, disable_auth),
        )


def create_app_from_file(filename=None):
    if filename is None:
        filename = os.environ['CACHISH_CONFIG_FILE']
    with open(filename) as fh:
        config = yaml.safe_load(fh) or {}
    return create_app(**config)


def get_module(name, parameters):
    constructor = getattr(backends, name)
    return constructor(**parameters)


def create_view_for_value(module, disable_auth):
    def view():
        if not disable_auth:
            auth_token = get_auth_token()
            # This will abort if token is invalid
            check_auth(auth_token)
        else:
            events.add('auth', 'disabled')

        fresh = True
        events.tag = module.tag
        headers = {
            'Content-Type': 'application/json',
            'Server': f'Cachish/{__version__}',
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
        events.add('backend_duration_seconds', backend_end_time - backend_start_time)
        events.add('cache', cache_status)

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
