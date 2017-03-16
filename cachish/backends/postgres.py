import psycopg2
import psycopg2.extras


class Postgres(object):
    def __init__(self, database_url, query):
        self.database_url = database_url
        self.query = query

    @property
    def connection(self):
        if not hasattr(self, '_connection'):
            self._connection = psycopg2.connect(self.database_url)
        return self._connection


    def get(self):
        results = []
        with self.connection as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(self.query)
                for row in cursor:
                    results.append(row)
        return results
