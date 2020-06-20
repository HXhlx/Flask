from Database import Database


class Administrator(Database):
    def __init__(self, admin_id, id, name, password, face):
        Database.__init__(self)
        self.admin_id = admin_id
        self.id = id
        self.name = name
        self.password = password
        self.face = face

    def statistics(self):
        pass

    def set_password(self):
        pass

    def supplement(self, schemas, no, num):
        self.cursor.execute("update {} set Stock = Stock + {} where BNo = '{}'".format(schemas, num, no))
