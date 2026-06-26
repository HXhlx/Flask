from Book import *
from Member import *
from Database import Database
from datetime import datetime


class Application(Database):
    def __init__(self):
        Database.__init__(self)
        self.mem = Member((None, None, None, None, None, None, None))

    def register(self, mem):
        self.cursor.execute(
            "insert into members (IDNo, Name, Tel, Img, Addr) values (%(id)s, %(name)s, %(phone)s, %(face)s, %(address)s)",
            mem
        )
        self.cnx.commit()
        if self.login(mem['phone']):
            return True

    def login(self, phone):
        self.cursor.execute("select * from members where Tel = %s", (phone,))
        result = self.cursor.fetchone()
        if result:
            self.mem = Member(result)
            return True

    def sell(self, id, bno, num):
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from buybook where BuyNo like %s", ('B' + date + '%',))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from newbook where BNo = %s", (bno,))
        result = self.cursor.fetchone()
        if not result:
            return '图书不存在'
        new = NewBook(result)
        if new.number >= num:
            buy_no = 'B' + date + str(n + 1).zfill(5)
            self.cursor.execute(
                "insert into buybook values (%s, %s, %s, %s, %s, %s)",
                (buy_no, datetime.now(), id, bno, num, new.price * num)
            )
            self.cursor.execute("update newbook set Stock = Stock - %s where BNo = %s", (num, bno))
            self.cnx.commit()
        else:
            return '库存不足'

    def pre_sell(self, id, bno, num):
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from orderbook where ONo like %s", ('O' + date + '%',))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from newbook where BNo = %s", (bno,))
        result = self.cursor.fetchone()
        if not result:
            return '图书不存在'
        new = NewBook(result)
        order_no = 'O' + date + str(n + 1).zfill(5)
        self.cursor.execute(
            "insert into orderbook values (%s, %s, %s, %s, %s, %s)",
            (order_no, datetime.now(), id, bno, num, new.price * num)
        )
        self.cnx.commit()

    def unsubscribe(self, ono):
        self.cursor.execute("select MNo, BNo, ONum from orderbook where ONo = %s", (ono,))
        result = self.cursor.fetchone()
        if not result:
            return '订单不存在'
        member_no, bno, num = result
        self.cursor.execute("update newbook set Stock = Stock + %s where BNo = %s", (num, bno))
        self.cursor.execute("delete from orderbook where ONo = %s", (ono,))
        self.cnx.commit()
        return True

    def sales_return(self, buyno):
        self.cursor.execute("select MNo, BNo, BuyNum from buybook where BuyNo = %s", (buyno,))
        result = self.cursor.fetchone()
        if not result:
            return '购买记录不存在'
        member_no, bno, num = result
        self.cursor.execute("update newbook set Stock = Stock + %s where BNo = %s", (num, bno))
        self.cursor.execute("delete from buybook where BuyNo = %s", (buyno,))
        self.cnx.commit()
        return True

    def recommend(self, member_id):
        self.cursor.execute(
            "select distinct Press from buybook b join newbook n on b.BNo = n.BNo where b.MNo = %s",
            (member_id,)
        )
        presses = [row[0] for row in self.cursor.fetchall()]
        if not presses:
            self.cursor.execute("select * from newbook order by Stock desc limit 10")
            return self.cursor.fetchall()
        placeholders = ', '.join(['%s'] * len(presses))
        self.cursor.execute(
            f"select * from newbook where Press in ({placeholders}) and Stock > 0 order by rand() limit 10",
            presses
        )
        return self.cursor.fetchall()


class Cabinet(Database):
    def __init__(self):
        Database.__init__(self)

    def pick_up(self, lno):
        self.cursor.execute("select LState from leasebook where LNo = %s", (lno,))
        result = self.cursor.fetchone()
        if not result:
            return '借阅记录不存在'
        if result[0] != '在借':
            return '当前状态无法提货'
        self.cursor.execute(
            "update leasebook set LState = '已还', RDate = %s where LNo = %s",
            (datetime.now(), lno)
        )
        self.cnx.commit()
        return True


class Server(Database):
    def __init__(self):
        Database.__init__(self)

    def reserve(self, bno, num):
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from orderbook where ONo like %s", ('O' + date + '%',))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from newbook where BNo = %s", (bno,))
        result = self.cursor.fetchone()
        if not result:
            return '图书不存在'
        new = NewBook(result)
        order_no = 'O' + date + str(n + 1).zfill(5)
        self.cursor.execute(
            "insert into orderbook values (%s, %s, %s, %s, %s, %s)",
            (order_no, datetime.now(), None, bno, num, new.price * num)
        )
        self.cnx.commit()

    def sales_return(self, buyno):
        self.cursor.execute("select MNo, BNo, BuyNum from buybook where BuyNo = %s", (buyno,))
        result = self.cursor.fetchone()
        if not result:
            return '购买记录不存在'
        member_no, bno, num = result
        self.cursor.execute("update newbook set Stock = Stock + %s where BNo = %s", (num, bno))
        self.cursor.execute("delete from buybook where BuyNo = %s", (buyno,))
        self.cnx.commit()
        return True

    def give_back(self, lno):
        self.cursor.execute("select BNo, LState from leasebook where LNo = %s", (lno,))
        result = self.cursor.fetchone()
        if not result:
            return '借阅记录不存在'
        bno, state = result
        if state != '在借':
            return '当前状态无法归还'
        self.cursor.execute("select Price from oldbook where BNo = %s", (bno,))
        price_result = self.cursor.fetchone()
        if not price_result:
            return '图书信息异常'
        price = price_result[0]
        rent = price * 0.08 if price <= 60 else 6
        self.cursor.execute(
            "update leasebook set LState = '已还', RDate = %s, LPay = %s where LNo = %s",
            (datetime.now(), rent, lno)
        )
        self.cursor.execute("update oldbook set Stock = Stock + 1 where BNo = %s", (bno,))
        self.cnx.commit()
        return rent

    def unsubscribe(self, ono):
        self.cursor.execute("select MNo, BNo, ONum from orderbook where ONo = %s", (ono,))
        result = self.cursor.fetchone()
        if not result:
            return '订单不存在'
        member_no, bno, num = result
        self.cursor.execute("update newbook set Stock = Stock + %s where BNo = %s", (num, bno))
        self.cursor.execute("delete from orderbook where ONo = %s", (ono,))
        self.cnx.commit()
        return True


class BookStore(Database):
    def __init__(self):
        Database.__init__(self)

    def sell(self, id, bno, num):
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from buybook where BuyNo like %s", ('B' + date + '%',))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from newbook where BNo = %s", (bno,))
        result = self.cursor.fetchone()
        if not result:
            return '图书不存在'
        new = NewBook(result)
        if new.number >= num:
            buy_no = 'B' + date + str(n + 1).zfill(5)
            self.cursor.execute(
                "insert into buybook values (%s, %s, %s, %s, %s, %s)",
                (buy_no, datetime.now(), id, bno, num, new.price * num)
            )
            self.cursor.execute("update newbook set Stock = Stock - %s where BNo = %s", (num, bno))
            self.cnx.commit()
        else:
            return '库存不足'

    def rent(self, id, bno, num, rdate, state):
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from leasebook where LNo like %s", ('L' + date + '%',))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from oldbook where BNo = %s", (bno,))
        result = self.cursor.fetchone()
        if not result:
            return '图书不存在'
        old = OldBook(result)
        if old.number >= num:
            lease_no = 'L' + date + str(n + 1).zfill(5)
            self.cursor.execute(
                "insert into leasebook values (%s, %s, %s, %s, %s, %s, %s)",
                (lease_no, datetime.now(), id, bno, rdate, state, old.rent)
            )
            self.cursor.execute("update oldbook set Stock = Stock - %s where BNo = %s", (num, bno))
            self.cnx.commit()
        else:
            return '库存不足'
