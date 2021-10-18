from psycopg2 import DatabaseError


def exception_handler(func):
    def wrapper(*args):
        try:
            return func(*args)
        except DatabaseError as error:
            return None, error.pgerror
        except Exception as error:
            return None, error.args[0]
        finally:
            args[0].conn.close()
    return wrapper
