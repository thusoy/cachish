from . import backends

from flask import Flask, jsonify, request, Response, current_app, abort

import binascii
import hashlib
import os
from functools import wraps
from fnmatch import fnmatch


def create_app(auth=None, items=None, cache_dir='/var/cache/cachish'):
    app = Flask(__name__)

    if items:
        for url, endpoint_config in items.items():
            module_name = endpoint_config['module']
            parameters = endpoint_config.get('parameters', {})
            module = get_module(module_name, parameters)
            app.add_url_rule(url, view_func=create_view_for_value(module))

    app.config.auth = auth or {}
    app.config.cache_dir = cache_dir

    # Ensure errors are caught at start time and not at request time
    test_cache_dir_writeable(cache_dir)

    return app


def test_cache_dir_writeable(cache_dir):
    with open(os.path.join(cache_dir, '.testfile'), 'w') as fh:
        pass


def get_module(name, parameters):
    constructor = getattr(backends, name)
    return constructor(**parameters)


def create_view_for_value(module):

    @requires_auth
    def view():
        fresh = True
        try:
            value = module.get()
        except:
            fresh = False
            try:
                return read_from_cache(), 203, {}
            except FileNotFoundError as e:
                abort(503)

        if fresh:
            write_to_cache(value)

        return value

    return view


def write_to_cache(value):
    cache_file = get_cache_file()
    temp_filename = '.' + binascii.hexlify(os.urandom(16)).decode('utf-8')
    tempfile = os.path.join(current_app.config.cache_dir, temp_filename)
    with open(tempfile, 'wb') as fh:
        fh.write(value.encode('utf-8'))
    os.rename(tempfile, cache_file)


def read_from_cache():
    cache_file = get_cache_file()
    with open(cache_file) as fh:
        return fh.read()


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
    token_globs = current_app.config.auth.get(token)
    if not token_globs:
        print('no accesses for token %s' % token)
        abort(403)

    # If there's only a single glob, transform to list
    if isinstance(token_globs, str):
        token_globs = [token_globs]

    for pattern in token_globs:
        print('testing %s against %s' % (requested_url, pattern))
        if fnmatch(requested_url, pattern):
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


def requires_auth(f):
    @wraps(f)
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

        return f(*args, **kwargs)
    return decorated
