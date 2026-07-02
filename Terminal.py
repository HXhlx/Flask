from datetime import datetime
from Book import NewBook, OldBook
from Member import Member
from Database import Database, get_connection


def _make_id(prefix):
    ts = format(int(datetime.now().timestamp() * 1_000_000), 'x')
    return prefix + ts[-19:]


class BookstoreService(Database):
    def __init__(self, conn=None):
        super().__init__(conn)

    def register(self, id_number, name, phone, avatar=None, address=''):
        self.cursor.execute(
            "INSERT INTO members (IDNo, Name, Tel, Img, Addr) VALUES (%s, %s, %s, %s, %s)",
            (id_number, name, phone, avatar, address)
        )
        self.cnx.commit()

    def login_by_phone(self, phone):
        self.cursor.execute("SELECT * FROM members WHERE Tel = %s", (phone,))
        return self.cursor.fetchone()

    def get_member(self, member_id):
        self.cursor.execute("SELECT * FROM members WHERE MNo = %s", (member_id,))
        return self.cursor.fetchone()

    def get_newbook(self, isbn):
        self.cursor.execute("SELECT * FROM newbook WHERE BNo = %s", (isbn,))
        row = self.cursor.fetchone()
        if row:
            return NewBook(row)
        return None

    def _next_buy_id(self):
        return _make_id('B')

    def _next_order_id(self):
        return _make_id('O')

    def _next_lease_id(self):
        return _make_id('L')

    def sell(self, member_id, isbn, num):
        self.cursor.execute("SELECT * FROM newbook WHERE BNo = %s", (isbn,))
        row = self.cursor.fetchone()
        if not row:
            return '图书不存在'
        book = NewBook(row)
        if book.stock < num:
            return '库存不足'
        buy_no = self._next_buy_id()
        self.cursor.execute(
            "INSERT INTO buybook VALUES (%s, %s, %s, %s, %s, %s)",
            (buy_no, datetime.now(), member_id, isbn, num, book.price * num)
        )
        self.cursor.execute(
            "UPDATE newbook SET Stock = Stock - %s WHERE BNo = %s", (num, isbn)
        )
        self.cnx.commit()
        return buy_no

    def pre_sell(self, member_id, isbn, num):
        self.cursor.execute("SELECT * FROM newbook WHERE BNo = %s", (isbn,))
        row = self.cursor.fetchone()
        if not row:
            return '图书不存在'
        book = NewBook(row)
        order_no = self._next_order_id()
        self.cursor.execute(
            "INSERT INTO orderbook VALUES (%s, %s, %s, %s, %s, %s)",
            (order_no, datetime.now(), member_id, isbn, num, book.price * num)
        )
        self.cnx.commit()
        return order_no

    def unsubscribe(self, order_no, member_id=None):
        if member_id:
            self.cursor.execute(
                "SELECT BNo, ONum FROM orderbook WHERE ONo = %s AND MNo = %s",
                (order_no, member_id)
            )
        else:
            self.cursor.execute(
                "SELECT BNo, ONum FROM orderbook WHERE ONo = %s", (order_no,)
            )
        row = self.cursor.fetchone()
        if not row:
            return '订单不存在'
        _isbn, _num = row
        self.cursor.execute("DELETE FROM orderbook WHERE ONo = %s", (order_no,))
        self.cnx.commit()
        return True

    def sales_return(self, buy_no, member_id=None):
        if member_id:
            self.cursor.execute(
                "SELECT BuyNum FROM buybook WHERE BuyNo = %s AND MNo = %s",
                (buy_no, member_id)
            )
        else:
            self.cursor.execute(
                "SELECT BuyNum FROM buybook WHERE BuyNo = %s", (buy_no,)
            )
        row = self.cursor.fetchone()
        if not row:
            return '购买记录不存在'
        num = row[0]
        self.cursor.execute("SELECT BNo FROM buybook WHERE BuyNo = %s", (buy_no,))
        isbn = self.cursor.fetchone()[0]
        self.cursor.execute(
            "UPDATE newbook SET Stock = Stock + %s WHERE BNo = %s", (num, isbn)
        )
        self.cursor.execute("DELETE FROM buybook WHERE BuyNo = %s", (buy_no,))
        self.cnx.commit()
        return True

    def recommend(self, member_id, limit=10):
        self.cursor.execute(
            "SELECT DISTINCT n.Press "
            "FROM buybook b JOIN newbook n ON b.BNo = n.BNo "
            "WHERE b.MNo = %s", (member_id,)
        )
        presses = [r[0] for r in self.cursor.fetchall()]
        if not presses:
            self.cursor.execute(
                "SELECT * FROM newbook WHERE Stock > 0 ORDER BY Stock DESC LIMIT %s",
                (limit,)
            )
            return self.cursor.fetchall()
        placeholders = ', '.join(['%s'] * len(presses))
        self.cursor.execute(
            f"SELECT * FROM newbook WHERE Press IN ({placeholders}) "
            f"AND Stock > 0 ORDER BY RAND() LIMIT %s",
            presses + [limit]
        )
        return self.cursor.fetchall()

    def pick_up(self, lease_no, member_id=None):
        if member_id:
            self.cursor.execute(
                "SELECT BNo, LState FROM leasebook WHERE LNo = %s AND MNo = %s",
                (lease_no, member_id)
            )
        else:
            self.cursor.execute(
                "SELECT BNo, LState FROM leasebook WHERE LNo = %s", (lease_no,)
            )
        row = self.cursor.fetchone()
        if not row:
            return '借阅记录不存在'
        isbn, state = row
        if state != '在借':
            return '当前状态无法提货'
        self.cursor.execute(
            "UPDATE leasebook SET LState = '已还', RDate = %s WHERE LNo = %s",
            (datetime.now(), lease_no)
        )
        self.cursor.execute(
            "UPDATE oldbook SET Stock = Stock + 1 WHERE BNo = %s", (isbn,)
        )
        self.cnx.commit()
        return True

    def give_back(self, lease_no, member_id=None):
        if member_id:
            self.cursor.execute(
                "SELECT BNo, LState FROM leasebook WHERE LNo = %s AND MNo = %s",
                (lease_no, member_id)
            )
        else:
            self.cursor.execute(
                "SELECT BNo, LState FROM leasebook WHERE LNo = %s", (lease_no,)
            )
        row = self.cursor.fetchone()
        if not row:
            return '借阅记录不存在'
        isbn, state = row
        if state != '在借':
            return '当前状态无法归还'
        self.cursor.execute("SELECT Price FROM oldbook WHERE BNo = %s", (isbn,))
        price_row = self.cursor.fetchone()
        if not price_row:
            return '图书信息异常'
        price = price_row[0]
        rent = float(OldBook((None, None, None, None, price, None)).rent)
        self.cursor.execute(
            "UPDATE leasebook SET LState = '已还', RDate = %s, LPay = %s WHERE LNo = %s",
            (datetime.now(), rent, lease_no)
        )
        self.cursor.execute(
            "UPDATE oldbook SET Stock = Stock + 1 WHERE BNo = %s", (isbn,)
        )
        self.cnx.commit()
        return rent

    def rent_book(self, member_id, isbn, state='在借'):
        self.cursor.execute("SELECT * FROM oldbook WHERE BNo = %s", (isbn,))
        row = self.cursor.fetchone()
        if not row:
            return '图书不存在'
        book = OldBook(row)
        if book.stock < 1:
            return '库存不足'
        lease_no = self._next_lease_id()
        self.cursor.execute(
            "INSERT INTO leasebook VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (lease_no, datetime.now(), member_id, isbn, None, state, book.rent)
        )
        self.cursor.execute(
            "UPDATE oldbook SET Stock = Stock - 1 WHERE BNo = %s", (isbn,)
        )
        self.cnx.commit()
        return lease_no

    def search_books(self, keyword):
        like = '%' + keyword.replace('%', '\\%').replace('_', '\\_') + '%'
        self.cursor.execute(
            "SELECT * FROM newbook "
            "WHERE BName LIKE %s OR Author LIKE %s OR Press LIKE %s "
            "UNION "
            "SELECT * FROM oldbook "
            "WHERE BName LIKE %s OR Author LIKE %s OR Press LIKE %s "
            "ORDER BY BName LIMIT 20",
            (like, like, like, like, like, like)
        )
        return self.cursor.fetchall()


    def get_buy_orders(self, member_id):
        self.cursor.execute(
            "SELECT b.BuyNo, b.BuyDate, n.BName, b.BuyNum, b.BPay "
            "FROM buybook b JOIN newbook n ON b.BNo = n.BNo "
            "WHERE b.MNo = %s ORDER BY b.BuyDate DESC", (member_id,)
        )
        return self.cursor.fetchall()

    def get_order_orders(self, member_id):
        self.cursor.execute(
            "SELECT o.ONo, o.ODate, n.BName, o.ONum, o.OPay "
            "FROM orderbook o JOIN newbook n ON o.BNo = n.BNo "
            "WHERE o.MNo = %s ORDER BY o.ODate DESC", (member_id,)
        )
        return self.cursor.fetchall()

    def get_lease_records(self, member_id):
        self.cursor.execute(
            "SELECT l.LNo, l.LDate, b.BName, l.LState, l.LPay "
            "FROM leasebook l JOIN oldbook b ON l.BNo = b.BNo "
            "WHERE l.MNo = %s ORDER BY l.LDate DESC", (member_id,)
        )
        return self.cursor.fetchall()


CATEGORY_LIST = ['儿童读物', '文学', '青少年读物', '考试图书', '人文历史', '科学', '金融经济', '中小学教辅']
