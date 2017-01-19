import binascii
import fnmatch
import hashlib
import json
import logging
import os
from functools import wraps

import yaml
from flask import Flask, jsonify, request, Response, current_app, abort

from . import backends

def create_app(auth=None, items=None, cache_dir='/var/cache/cachish'):
    app = Flask(__name__, static_folder=None)

    if items:
        add_item_views(items, app)

    app.config.auth = transform_auth(auth)
    app.config.cache_dir = cache_dir
    add_error_handlers(app)

    # Ensure errors are caught at start time and not at request time
    test_cache_dir_writeable(cache_dir)

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


def test_cache_dir_writeable(cache_dir):
    testfile = os.path.join(cache_dir, '.testfile')
    with open(testfile, 'w'):
        pass
    os.remove(testfile)


def get_module(name, parameters):
    constructor = getattr(backends, name)
    return constructor(**parameters)


def create_view_for_value(module):

    @requires_auth
    def view():
        fresh = True
        headers = {
            'Content-Type': 'application/json',
        }
        try:
            value = module.get()
        except: # pylint: disable=bare-except
            logging.exception('Failed to get value from %s', module)
            fresh = False
            try:
                value = read_from_cache()
            except FileNotFoundError:
                abort(503)

        if fresh:
            write_to_cache(value)

        headers['X-Cache'] = 'miss' if fresh else 'hit'

        return json.dumps(value), 200, headers

    return view


def add_error_handlers(app):

    def error_503(error): # pylint: disable=unused-argument
        return 'Upstream failure', 503, {
            'X-Cache': 'miss',
        }

    app.register_error_handler(503, error_503)


def write_to_cache(value):
    cache_file = get_cache_file()
    temp_filename = '.' + binascii.hexlify(os.urandom(16)).decode('utf-8')
    tempfile = os.path.join(current_app.config.cache_dir, temp_filename)
    with secure_open_file(tempfile, 'w') as fh:
        json.dump(value, fh)
    os.rename(tempfile, cache_file)


def read_from_cache():
    cache_file = get_cache_file()
    with open(cache_file) as fh:
        return json.load(fh)


def secure_open_file(filename, mode='wb'):
    """ Create a new file with 400 permissions, ensuring exclusive access.

    The motivation is to avoid information disclosure if any other users have
    access to the cache_dir and can create files. We thus need to ensure that
    when we open a file it's a new file that no-one else already has a file
    descriptor for. For subsequent accesses the permissions are set to 400,
    ensuring that the file is never modified directly, but can only be updated
    by replacing the entire file, forcing us to stay thread-safe.

    We could also have used the O_TMPFILE flag to avoid having a filesystem
    entry before replacing the file at all, but filesystem support for this is
    a bit spotty and requires another python package to access the linkat(2)
    function (and linux kernel 3.11 or later).
    """
    perms = 0o400
    fd = os.open(filename, os.O_CREAT | os.O_WRONLY | os.O_EXCL, perms)
    handle = os.fdopen(fd, mode)

    return handle


def get_cache_file():
    current_url = request.path
    cache_filename = get_cache_filename(current_url)
    return os.path.join(current_app.config.cache_dir, cache_filename)


def get_cache_filename(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()


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
