import os
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection
from dotenv import load_dotenv

load_dotenv()

_pool = MySQLConnectionPool(
    pool_name="bookstore_pool",
    pool_size=25,
    pool_reset_session=True,
    user=os.environ.get('DB_USER', 'root'),
    password=os.environ.get('DB_PASSWORD', ''),
    database=os.environ.get('DB_NAME', 'bookstore'),
    host=os.environ.get('DB_HOST', 'localhost'),
    port=int(os.environ.get('DB_PORT', 3306)),
)


def get_connection():
    return _pool.get_connection()


class Database:
    def __init__(self, conn=None):
        self._owns_conn = conn is None
        self.cnx = conn if conn else get_connection()
        self.cursor = self.cnx.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
        except Exception:
            pass
        try:
            if self._owns_conn and hasattr(self, 'cnx') and self.cnx:
                self.cnx.close()
        except Exception:
            pass
