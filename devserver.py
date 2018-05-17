#!./venv/bin/python

import os

from cachish import create_app

items = {
    '/amazon': {
        'module': 'JsonHttp',
        'parameters': {
            'url': 'https://ip-ranges.amazonaws.com/ip-ranges.json',
        }
    }
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
