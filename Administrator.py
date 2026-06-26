from Database import Database


class Administrator(Database):
    ALLOWED_TABLES = ('newbook', 'oldbook')

    def __init__(self, admin_id, id, name, password, face):
        Database.__init__(self)
        self.admin_id = admin_id
        self.id = id
        self.name = name
        self.password = password
        self.face = face

    def statistics(self):
        self.cursor.execute(
            "select date_format(BuyDate, '%%Y-%%m') as month, sum(BPay) "
            "from buybook group by month order by month desc"
        )
        sales = self.cursor.fetchall()
        self.cursor.execute(
            "select date_format(LDate, '%%Y-%%m') as month, sum(LPay) "
            "from leasebook where LPay is not null group by month order by month desc"
        )
        rentals = self.cursor.fetchall()
        return {'sales': sales, 'rentals': rentals}

    def set_password(self, old_pwd, new_pwd):
        if self.password != old_pwd:
            return '旧密码错误'
        self.cursor.execute("update admin set Code = %s where ANo = %s", (new_pwd, self.admin_id))
        self.cnx.commit()
        self.password = new_pwd
        return True

    def supplement(self, schemas, no, num):
        if schemas not in self.ALLOWED_TABLES:
            raise ValueError(f"非法表名: {schemas}")
        self.cursor.execute(f"update {schemas} set Stock = Stock + %s where BNo = %s", (num, no))
        self.cnx.commit()
