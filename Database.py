from mysql.connector import connect


class Database:
    def __init__(self):
        self.cnx = connect(user="root", password="hx19990627", database="bookstore")
        self.cursor = self.cnx.cursor()

    def __del__(self):
        self.cursor.close()
        self.cnx.close()
