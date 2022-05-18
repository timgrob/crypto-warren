from contextlib import contextmanager
import psycopg2


@contextmanager
def postgres_manager(url: str):
    """Context manager for postgres database"""
    try:
        connection = psycopg2.connect(url)
        cursor = connection.cursor()
        yield cursor
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        connection.commit()
        cursor.close()
        connection.close()
