from Book import *
from Member import *
from Database import Database
from datetime import datetime


class Application(Database):  # app(手机端)
    mem = Member((None, None, None, None, None, None, None))

    def register(self, mem):
        self.cursor.execute("insert into members (IDNo, Name, Tel, Img, Addr) values (%(id)s, %(name)s, %(phone)s, %(face)s, %(address)s)", mem)
        self.cnx.commit()
        if self.login(mem['phone']):
            return True

    def login(self, phone):  # 注册/登录
        self.cursor.execute("select * from members where Tel = '{}'".format(phone))
        result = self.cursor.fetchone()
        if result:
            self.mem = Member(result)
            return True

    def sell(self, id, bno, num):  # 销售
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from buybook where BuyNo like 'B{}%'".format(date))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from newbook where BNo = '{}'".format(bno))
        new = NewBook(self.cursor.fetchone())
        if new.number >= num:
            self.cursor.execute("insert into buybook values (%s, %s, %s, %s, %s, %s)", ('B' + date + str(n + 1).zfill(5), datetime.now(), id, bno, num, new.price * num))
            self.cursor.execute("update newbook set Stock = Stock - %s where BNo = %s", (num, bno))
            self.cnx.commit()
        else:
            return '库存不足'

    def pre_sell(self, id, bno, num):  # 预售
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from olderbook where ONo like 'O{}%'".format(date))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from newbook where BNo = '{}'".format(bno))
        new = NewBook(self.cursor.fetchone())
        self.cursor.execute("insert into buybook values (%s, %s, %s, %s, %s, %s)", ('O' + date + str(n + 1).zfill(5), datetime.now(), id, bno, num, new.price * num))
        self.cnx.commit()

    def unsubscribe(self):  # 退订
        pass

    def sales_return(self):  # 退货
        pass

    def recommend(self):  # 图书推荐
        pass


class Cabinet(Database):  # 自提柜
    def pick_up(self):  # 提货
        pass


class Server(Database):  # 自助服务器(PC端)
    def reserve(self, bno, num):  # 预订
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from olderbook where ONo like 'O{}%'".format(date))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from newbook where BNo = '{}'".format(bno))
        new = NewBook(self.cursor.fetchone())
        self.cursor.execute("insert into buybook values (%s, %s, %s, %s, %s, %s)", ('O' + date + str(n + 1).zfill(5), datetime.now(), id, bno, num, new.price * num))
        self.cnx.commit()

    def sales_return(self):  # 退货
        pass

    def give_back(self):  # 归还
        pass

    def unsubscribe(self):  # 退订
        pass


class BookStore(Database):  # 书店
    def sell(self, id, bno, num):  # 销售
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from buybook where BuyNo like 'B{}%'".format(date))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from newbook where BNo = '{}'".format(bno))
        new = NewBook(self.cursor.fetchone())
        if new.number >= num:
            self.cursor.execute("insert into buybook values (%s, %s, %s, %s, %s, %s)", ('B' + date + str(n + 1).zfill(5), datetime.now(), id, bno, num, new.price * num))
            self.cursor.execute("update newbook set Stock = Stock - %s where BNo = %s", (num, bno))
            self.cnx.commit()
        else:
            return '库存不足'

    def rent(self, id, bno, num, rdate, state):  # 租借
        date = datetime.now().date().__str__().replace('-', '')
        self.cursor.execute("select * from leasebook where LNo like 'L{}%'".format(date))
        n = len(self.cursor.fetchall())
        self.cursor.execute("select * from oldbook where BNo = '{}'".format(bno))
        old = OldBook(self.cursor.fetchone())
        if old.number >= num:
            self.cursor.execute("insert into leasebook values (%s, %s, %s, %s, %s, %s,%s)", ('L' + date + str(n + 1).zfill(5), datetime.now(), id, bno, rdate, state, old.rent))
            self.cursor.execute("update oldbook set Stock = Stock - %s where BNo = %s", (num, bno))
            self.cnx.commit()
        else:
            return '库存不足'
