import os
from mysql.connector import connect


class Database:
    def __init__(self):
        self.cnx = connect(
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'bookstore'),
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', 3306))
        )
        self.cursor = self.cnx.cursor()

    def __del__(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
        except Exception:
            pass
        try:
            if hasattr(self, 'cnx') and self.cnx:
                self.cnx.close()
        except Exception:
            pass
