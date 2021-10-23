import psycopg2
from config.config import db_credentials


class MainDao:

    def __init__(self):
        connection_url = 'dbname={name} user={user} password={pswd} port={port} host={host}'.format(
            name=db_credentials['name'],
            user=db_credentials['user'],
            pswd=db_credentials['pswd'],
            port=db_credentials['port'],
            host=db_credentials['host'],
            )
        
        self.conn = psycopg2.connect(connection_url)

    @staticmethod
    def get_user_ratings(user_id, cursor):
        query = 'select AVG(value) from rates where user_id=%s;'
        cursor.execute(query, (user_id,))
        rate = cursor.fetchone()[0]
        if rate is None:
            return None
        else:
            rate_value = float(rate)
            return int(rate_value) if rate_value.is_integer() else format(rate_value, ".2f")

    @staticmethod
    def convert_to_list(cursor):
        return [row for row in cursor.fetchall()]
