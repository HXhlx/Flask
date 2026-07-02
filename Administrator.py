from werkzeug.security import generate_password_hash, check_password_hash
from Database import Database


class Administrator(Database):
    ALLOWED_TABLES = ('newbook', 'oldbook')

    def __init__(self, admin_id, id_number, name, password, avatar, conn=None):
        super().__init__(conn)
        self.admin_id = admin_id
        self.id_number = id_number
        self.name = name
        self.password = password
        self.avatar = avatar

    @classmethod
    def login(cls, id_number, password):
        db = cls.__new__(cls)
        Database.__init__(db)
        db.cursor.execute("SELECT * FROM admin WHERE IDNo = %s", (id_number,))
        row = db.cursor.fetchone()
        if not row:
            db.close()
            return None
        admin_id, _, name, stored_pwd, avatar = row
        admin = cls.__new__(cls)
        admin.admin_id = admin_id
        admin.id_number = id_number
        admin.name = name
        admin.password = stored_pwd
        admin.avatar = avatar
        admin.cnx = db.cnx
        admin.cursor = db.cursor
        admin._owns_conn = True
        if not admin._verify_password(password):
            admin.close()
            return None
        return admin

    def _verify_password(self, plain):
        if self.password.startswith('pbkdf2:') or self.password.startswith('scrypt:'):
            return check_password_hash(self.password, plain)
        return self.password == plain

    def set_password(self, old_pwd, new_pwd):
        if not self._verify_password(old_pwd):
            return '旧密码错误'
        hashed = generate_password_hash(new_pwd)
        self.cursor.execute(
            "UPDATE admin SET Code = %s WHERE ANo = %s", (hashed, self.admin_id)
        )
        self.cnx.commit()
        self.password = hashed
        return True

    def statistics(self):
        self.cursor.execute(
            "SELECT date_format(BuyDate, '%%Y-%%m') AS month, SUM(BPay) "
            "FROM buybook GROUP BY month ORDER BY month DESC"
        )
        sales = self.cursor.fetchall()
        self.cursor.execute(
            "SELECT date_format(LDate, '%%Y-%%m') AS month, SUM(LPay) "
            "FROM leasebook WHERE LPay IS NOT NULL GROUP BY month ORDER BY month DESC"
        )
        rentals = self.cursor.fetchall()
        self.cursor.execute("SELECT COUNT(*) FROM members")
        member_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM newbook")
        book_count = self.cursor.fetchone()[0]
        return {
            'sales': sales,
            'rentals': rentals,
            'member_count': member_count,
            'book_count': book_count,
        }

    def supplement(self, table, isbn, num):
        if table not in self.ALLOWED_TABLES:
            raise ValueError(f"非法表名: {table}")
        self.cursor.execute(
            f"UPDATE {table} SET Stock = Stock + %s WHERE BNo = %s", (num, isbn)
        )
        self.cnx.commit()
        return True

    def get_all_members(self):
        self.cursor.execute("SELECT * FROM members")
        return self.cursor.fetchall()

    def search_member(self, keyword):
        like = '%' + keyword + '%'
        self.cursor.execute(
            "SELECT * FROM members WHERE Name LIKE %s OR Tel LIKE %s OR IDNo LIKE %s",
            (like, like, like)
        )
        return self.cursor.fetchall()
