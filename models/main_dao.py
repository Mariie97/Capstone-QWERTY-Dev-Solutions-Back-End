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
