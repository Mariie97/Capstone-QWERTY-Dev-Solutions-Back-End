import psycopg2
from config.db_config import db_credentials


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
    def convert_to_list(cursor):
        list = []
        for row in cursor:
            list.append(row)
        return list
