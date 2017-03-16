from unittest import mock

import psycopg2

from cachish.backends import Postgres


def test_postgres_backend():
    config = {
        'database_url': 'postgres://user:pw@host/db',
        'query': 'select * from mytable;',
    }
    mocked_return = [
        {'col1': 'val1', 'col2': 'val2'},
        {'col1': 'val3', 'col2': 'val4'},
    ]
    psycopg_mock = mock.MagicMock()
    (psycopg_mock
        .connect.return_value # connection
        .__enter__.return_value # conn
        .cursor.return_value # cursor()
        .__enter__.return_value # cursor
        .__iter__.return_value) = mocked_return
    psycopg_mock.cursor.return_value = 'asd'
    psycopg_mock.__iter__.return_value = mocked_return
    with mock.patch('cachish.backends.postgres.psycopg2', psycopg_mock):
        backend = Postgres(**config)
        value = backend.get()
    assert value == mocked_return
