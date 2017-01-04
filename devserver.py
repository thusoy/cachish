#!./venv/bin/python

import os

from cachish import create_app

items = {
    # TODO: Add your test items here
}

auth = {
    'development-token': {
        'token': 'devtoken',
        'url': '/*',
    },
}

cache_dir = os.path.abspath('.cache')
try:
    os.makedirs(cache_dir)
except FileExistsError:
    pass

app = create_app(items=items, auth=auth, cache_dir=cache_dir)

app.run(debug=True, port=2469)
