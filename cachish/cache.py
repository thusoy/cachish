import os
import json
import binascii
import hashlib

from flask import current_app, request


def test_cache_dir_writeable(cache_dir):
    testfile = os.path.join(cache_dir, '.testfile')
    with open(testfile, 'w'):
        pass
    os.remove(testfile)


def write_to_cache(value):
    cache_file = _get_cache_file()
    temp_filename = '.' + binascii.hexlify(os.urandom(16)).decode('utf-8')
    tempfile = os.path.join(current_app.config.cache_dir, temp_filename)
    with _secure_open_file(tempfile, 'w') as fh:
        json.dump(value, fh)
    os.rename(tempfile, cache_file)


def read_from_cache():
    cache_file = _get_cache_file()
    with open(cache_file) as fh:
        return json.load(fh)


def _secure_open_file(filename, mode='wb'):
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


def _get_cache_file():
    current_url = request.path
    cache_filename = _get_cache_filename(current_url)
    return os.path.join(current_app.config.cache_dir, cache_filename)


def _get_cache_filename(url):
    return hashlib.sha256(url.encode('utf-8')).hexdigest()
