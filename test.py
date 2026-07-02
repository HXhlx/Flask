import unittest
from decimal import Decimal
from Book import NewBook, OldBook
from Member import Member
from Database import Database, get_connection
from Terminal import BookstoreService, CATEGORY_LIST, _make_id
from Administrator import Administrator


class NewBookTest(unittest.TestCase):
    def test_init(self):
        book = NewBook(('9787506380263', '人间失格', '太宰治', '作家出版社', Decimal('25.00'), 22))
        self.assertEqual(book.isbn, '9787506380263')
        self.assertEqual(book.name, '人间失格')
        self.assertEqual(book.author, '太宰治')
        self.assertEqual(book.press, '作家出版社')
        self.assertEqual(book.price, Decimal('25.00'))
        self.assertEqual(book.stock, 22)

    def test_init_with_float_price(self):
        book = NewBook(('1', '书名', '作者', '出版社', 50.0, 10))
        self.assertEqual(book.price, 50.0)
        self.assertEqual(book.stock, 10)


class OldBookTest(unittest.TestCase):
    def test_rent_low_price(self):
        book = OldBook(('1', '书名', '作者', '出版社', 40, 10))
        self.assertAlmostEqual(book.rent, 40 * 0.08, places=2)

    def test_rent_high_price(self):
        book = OldBook(('1', '书名', '作者', '出版社', 80, 10))
        self.assertEqual(book.rent, 6)

    def test_rent_threshold_price(self):
        book = OldBook(('1', '书名', '作者', '出版社', 60, 10))
        self.assertAlmostEqual(book.rent, 60 * 0.08, places=2)

    def test_rent_at_75(self):
        book = OldBook(('1', '书名', '作者', '出版社', 75, 10))
        self.assertEqual(book.rent, 6)

    def test_rent_at_61(self):
        book = OldBook(('1', '书名', '作者', '出版社', 61, 10))
        self.assertEqual(book.rent, 6)

    def test_inherits_new_book(self):
        book = OldBook(('9787506380263', '人间失格', '太宰治', '作家出版社', 25, 5))
        self.assertIsInstance(book, NewBook)
        self.assertEqual(book.isbn, '9787506380263')
        self.assertEqual(book.name, '人间失格')


class MemberTest(unittest.TestCase):
    def test_init(self):
        m = Member(('M1', 'ID1', '张三', '13800138000', None, 100, '翻斗花园'))
        self.assertEqual(m.member_id, 'M1')
        self.assertEqual(m.id_number, 'ID1')
        self.assertEqual(m.name, '张三')
        self.assertEqual(m.phone, '13800138000')
        self.assertIsNone(m.avatar)
        self.assertEqual(m.score, 100)
        self.assertEqual(m.address, '翻斗花园')

    def test_init_with_none_fields(self):
        m = Member((None, None, None, None, None, None, None))
        self.assertIsNone(m.member_id)
        self.assertIsNone(m.name)


class DatabaseTest(unittest.TestCase):
    def test_context_manager(self):
        with Database() as db:
            db.cursor.execute("SELECT 1")
            result = db.cursor.fetchone()
            self.assertEqual(result[0], 1)

    def test_connection_pool(self):
        conn1 = get_connection()
        conn2 = get_connection()
        self.assertIsNot(conn1, conn2)
        conn1.close()
        conn2.close()


class MakeIdTest(unittest.TestCase):
    def test_buy_id_format(self):
        bid = _make_id('B')
        self.assertTrue(bid.startswith('B'))
        self.assertLessEqual(len(bid), 20)

    def test_order_id_format(self):
        oid = _make_id('O')
        self.assertTrue(oid.startswith('O'))
        self.assertLessEqual(len(oid), 20)

    def test_lease_id_format(self):
        lid = _make_id('L')
        self.assertTrue(lid.startswith('L'))
        self.assertLessEqual(len(lid), 20)


class BookstoreServiceLoginTest(unittest.TestCase):
    def setUp(self):
        self.svc = BookstoreService()

    def tearDown(self):
        self.svc.close()

    def test_login_existing_phone(self):
        row = self.svc.login_by_phone('15861165153')
        self.assertIsNotNone(row)
        self.assertEqual(row[2], '萧萧')

    def test_login_nonexistent_phone(self):
        row = self.svc.login_by_phone('10000000000')
        self.assertIsNone(row)

    def test_get_member_existing(self):
        row = self.svc.get_member(100001)
        self.assertIsNotNone(row)
        self.assertEqual(row[2], '萧萧')

    def test_get_member_nonexistent(self):
        row = self.svc.get_member(999999)
        self.assertIsNone(row)


class BookstoreServiceSellTest(unittest.TestCase):
    def setUp(self):
        self.svc = BookstoreService()
        self.member_id = 100001
        self.isbn = '9787506380263'
        self.svc.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        self.original_stock = self.svc.cursor.fetchone()[0]

    def tearDown(self):
        self.svc.cursor.execute(
            "UPDATE newbook SET Stock = %s WHERE BNo = %s",
            (self.original_stock, self.isbn)
        )
        self.svc.cursor.execute(
            "DELETE FROM buybook WHERE BuyNo LIKE %s", ('B%',)
        )
        self.svc.cnx.commit()
        self.svc.close()

    def test_sell_success(self):
        result = self.svc.sell(self.member_id, self.isbn, 1)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('B'))
        self.svc.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        new_stock = self.svc.cursor.fetchone()[0]
        self.assertEqual(new_stock, self.original_stock - 1)

    def test_sell_multiple(self):
        result = self.svc.sell(self.member_id, self.isbn, 3)
        self.assertIsInstance(result, str)
        self.svc.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        new_stock = self.svc.cursor.fetchone()[0]
        self.assertEqual(new_stock, self.original_stock - 3)

    def test_sell_insufficient_stock(self):
        result = self.svc.sell(self.member_id, self.isbn, 99999)
        self.assertEqual(result, '库存不足')

    def test_sell_book_not_found(self):
        result = self.svc.sell(self.member_id, '0000000000000', 1)
        self.assertEqual(result, '图书不存在')

    def test_sell_creates_buy_record(self):
        buy_no = self.svc.sell(self.member_id, self.isbn, 2)
        self.svc.cursor.execute("SELECT * FROM buybook WHERE BuyNo = %s", (buy_no,))
        row = self.svc.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[4], 2)


class BookstoreServicePreSellTest(unittest.TestCase):
    def setUp(self):
        self.svc = BookstoreService()
        self.member_id = 100001

    def tearDown(self):
        self.svc.cursor.execute(
            "DELETE FROM orderbook WHERE ONo LIKE %s", ('O%',)
        )
        self.svc.cnx.commit()
        self.svc.close()

    def test_pre_sell_success(self):
        result = self.svc.pre_sell(self.member_id, '9787506380263', 2)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('O'))

    def test_pre_sell_book_not_found(self):
        result = self.svc.pre_sell(self.member_id, '0000000000000', 1)
        self.assertEqual(result, '图书不存在')

    def test_pre_sell_creates_order_record(self):
        order_no = self.svc.pre_sell(self.member_id, '9787506380263', 3)
        self.svc.cursor.execute("SELECT * FROM orderbook WHERE ONo = %s", (order_no,))
        row = self.svc.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[4], 3)


class BookstoreServiceUnsubscribeTest(unittest.TestCase):
    """Bug 1 修复验证：unsubscribe 不应加回库存，因为 pre_sell 不会减库存"""

    def setUp(self):
        self.svc = BookstoreService()
        self.member_id = 100001
        self.isbn = '9787506380263'
        self.order_no = self.svc.pre_sell(self.member_id, self.isbn, 2)

    def tearDown(self):
        self.svc.close()

    def test_unsubscribe_success(self):
        self.svc.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        stock_before = self.svc.cursor.fetchone()[0]
        result = self.svc.unsubscribe(self.order_no)
        self.assertTrue(result)
        self.svc.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        stock_after = self.svc.cursor.fetchone()[0]
        self.assertEqual(stock_before, stock_after,
                         "BUG1: unsubscribe 不应改变库存，但库存发生了变化")

    def test_unsubscribe_removes_order(self):
        self.svc.unsubscribe(self.order_no)
        self.svc.cursor.execute("SELECT * FROM orderbook WHERE ONo = %s", (self.order_no,))
        row = self.svc.cursor.fetchone()
        self.assertIsNone(row)

    def test_unsubscribe_not_found(self):
        result = self.svc.unsubscribe('NONEXISTENT')
        self.assertEqual(result, '订单不存在')

    def test_unsubscribe_wrong_member(self):
        result = self.svc.unsubscribe(self.order_no, member_id=999999)
        self.assertEqual(result, '订单不存在')

    def test_unsubscribe_correct_member(self):
        result = self.svc.unsubscribe(self.order_no, member_id=self.member_id)
        self.assertTrue(result)


class BookstoreServiceSalesReturnTest(unittest.TestCase):
    def setUp(self):
        self.svc = BookstoreService()
        self.member_id = 100001
        self.isbn = '9787506380263'
        self.svc.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        self.original_stock = self.svc.cursor.fetchone()[0]
        self.buy_no = self.svc.sell(self.member_id, self.isbn, 2)

    def tearDown(self):
        self.svc.cursor.execute(
            "UPDATE newbook SET Stock = %s WHERE BNo = %s",
            (self.original_stock, self.isbn)
        )
        self.svc.cursor.execute(
            "DELETE FROM buybook WHERE BuyNo NOT LIKE %s", ('B2020%',)
        )
        self.svc.cnx.commit()
        self.svc.close()

    def test_sales_return_success(self):
        result = self.svc.sales_return(self.buy_no)
        self.assertTrue(result)

    def test_sales_return_restores_stock(self):
        self.svc.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        stock_after_sell = self.svc.cursor.fetchone()[0]
        self.svc.sales_return(self.buy_no)
        self.svc.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        stock_after_return = self.svc.cursor.fetchone()[0]
        self.assertEqual(stock_after_return, stock_after_sell + 2)

    def test_sales_return_not_found(self):
        result = self.svc.sales_return('NONEXISTENT')
        self.assertEqual(result, '购买记录不存在')

    def test_sales_return_wrong_member(self):
        result = self.svc.sales_return(self.buy_no, member_id=999999)
        self.assertEqual(result, '购买记录不存在')

    def test_sales_return_correct_member(self):
        result = self.svc.sales_return(self.buy_no, member_id=self.member_id)
        self.assertTrue(result)

    def test_sales_return_deletes_record(self):
        self.svc.sales_return(self.buy_no)
        self.svc.cursor.execute("SELECT * FROM buybook WHERE BuyNo = %s", (self.buy_no,))
        row = self.svc.cursor.fetchone()
        self.assertIsNone(row)


class BookstoreServiceRecommendTest(unittest.TestCase):
    def setUp(self):
        self.svc = BookstoreService()

    def tearDown(self):
        self.svc.close()

    def test_recommend_with_history(self):
        books = self.svc.recommend(100001)
        self.assertIsInstance(books, list)

    def test_recommend_without_history(self):
        books = self.svc.recommend(999999)
        self.assertIsInstance(books, list)
        if books:
            self.assertTrue(len(books) <= 10)

    def test_recommend_respects_limit(self):
        books = self.svc.recommend(100001, limit=3)
        self.assertTrue(len(books) <= 3)

    def test_recommend_returns_tuples(self):
        books = self.svc.recommend(100001)
        if books:
            self.assertIsInstance(books[0], tuple)
            self.assertEqual(len(books[0]), 6)


class BookstoreServicePickUpTest(unittest.TestCase):
    """Bug 3 修复验证：pick_up 应恢复 oldbook 库存"""

    def setUp(self):
        self.svc = BookstoreService()
        self.lease_isbn = '9787506380263'
        self._stock_before = self._get_old_stock(self.lease_isbn)
        self.lease_no = self.svc.rent_book(100001, self.lease_isbn)
        self.stock_after_rent = self._get_old_stock(self.lease_isbn)

    def _get_old_stock(self, isbn):
        self.svc.cursor.execute("SELECT Stock FROM oldbook WHERE BNo = %s", (isbn,))
        return self.svc.cursor.fetchone()[0]

    def tearDown(self):
        self.svc.cursor.execute(
            "UPDATE oldbook SET Stock = %s WHERE BNo = %s",
            (self._stock_before, self.lease_isbn)
        )
        self.svc.cursor.execute(
            "DELETE FROM leasebook WHERE LNo LIKE %s", ('L%',)
        )
        self.svc.cnx.commit()
        self.svc.close()

    def test_pick_up_success(self):
        result = self.svc.pick_up(self.lease_no)
        self.assertTrue(result)

    def test_pick_up_restores_stock(self):
        self.svc.pick_up(self.lease_no)
        stock_after = self._get_old_stock(self.lease_isbn)
        self.assertEqual(stock_after, self.stock_after_rent + 1,
                         "BUG3: pick_up 应将 oldbook 库存 +1")

    def test_pick_up_updates_state(self):
        self.svc.pick_up(self.lease_no)
        self.svc.cursor.execute("SELECT LState FROM leasebook WHERE LNo = %s", (self.lease_no,))
        state = self.svc.cursor.fetchone()[0]
        self.assertEqual(state, '已还')

    def test_pick_up_not_found(self):
        result = self.svc.pick_up('NONEXISTENT')
        self.assertEqual(result, '借阅记录不存在')

    def test_pick_up_already_returned(self):
        self.svc.pick_up(self.lease_no)
        result = self.svc.pick_up(self.lease_no)
        self.assertEqual(result, '当前状态无法提货')

    def test_pick_up_wrong_member(self):
        result = self.svc.pick_up(self.lease_no, member_id=999999)
        self.assertEqual(result, '借阅记录不存在')


class BookstoreServiceGiveBackTest(unittest.TestCase):
    """Bug 4 修复验证：give_back 应返回 float/int，非 decimal.Decimal"""

    def setUp(self):
        self.svc = BookstoreService()
        self.lease_isbn = '9787506380263'
        self._original_stock = self._get_old_stock(self.lease_isbn)
        self.lease_no = self.svc.rent_book(100001, self.lease_isbn)

    def _get_old_stock(self, isbn):
        self.svc.cursor.execute("SELECT Stock FROM oldbook WHERE BNo = %s", (isbn,))
        return self.svc.cursor.fetchone()[0]

    def tearDown(self):
        self.svc.cursor.execute(
            "UPDATE oldbook SET Stock = %s WHERE BNo = %s",
            (self._original_stock, self.lease_isbn)
        )
        self.svc.cursor.execute(
            "DELETE FROM leasebook WHERE LNo LIKE %s", ('L%',)
        )
        self.svc.cnx.commit()
        self.svc.close()

    def test_give_back_returns_numeric(self):
        result = self.svc.give_back(self.lease_no)
        self.assertIsInstance(result, (int, float),
                            "BUG4: give_back 应返回 int/float，不能是 Decimal")
        self.assertFalse(isinstance(result, Decimal),
                         "BUG4: 返回值不应是 Decimal 类型")
        self.assertGreater(result, 0)

    def test_give_back_updates_state(self):
        self.svc.give_back(self.lease_no)
        self.svc.cursor.execute("SELECT LState FROM leasebook WHERE LNo = %s", (self.lease_no,))
        state = self.svc.cursor.fetchone()[0]
        self.assertEqual(state, '已还')

    def test_give_back_records_payment(self):
        rent = self.svc.give_back(self.lease_no)
        self.svc.cursor.execute("SELECT LPay FROM leasebook WHERE LNo = %s", (self.lease_no,))
        lpay = self.svc.cursor.fetchone()[0]
        self.assertAlmostEqual(float(lpay), rent, places=2)

    def test_give_back_restores_stock(self):
        stock_before = self._get_old_stock(self.lease_isbn)
        self.svc.give_back(self.lease_no)
        stock_after = self._get_old_stock(self.lease_isbn)
        self.assertEqual(stock_after, stock_before + 1)

    def test_give_back_not_found(self):
        result = self.svc.give_back('NONEXISTENT')
        self.assertEqual(result, '借阅记录不存在')

    def test_give_back_already_returned(self):
        self.svc.give_back(self.lease_no)
        result = self.svc.give_back(self.lease_no)
        self.assertEqual(result, '当前状态无法归还')


class BookstoreServiceRentTest(unittest.TestCase):
    def setUp(self):
        self.svc = BookstoreService()
        self.member_id = 100001
        self.isbn = '9787506380263'
        self.svc.cursor.execute("SELECT Stock FROM oldbook WHERE BNo = %s", (self.isbn,))
        self._original_stock = self.svc.cursor.fetchone()[0]

    def tearDown(self):
        self.svc.cursor.execute(
            "UPDATE oldbook SET Stock = %s WHERE BNo = %s",
            (self._original_stock, self.isbn)
        )
        self.svc.cursor.execute(
            "DELETE FROM leasebook WHERE LNo LIKE %s", ('L%',)
        )
        self.svc.cnx.commit()
        self.svc.close()

    def test_rent_success(self):
        result = self.svc.rent_book(self.member_id, self.isbn)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('L'))

    def test_rent_decrements_stock(self):
        self.svc.rent_book(self.member_id, self.isbn)
        self.svc.cursor.execute("SELECT Stock FROM oldbook WHERE BNo = %s", (self.isbn,))
        new_stock = self.svc.cursor.fetchone()[0]
        self.assertEqual(new_stock, self._original_stock - 1)

    def test_rent_book_not_found(self):
        result = self.svc.rent_book(self.member_id, '0000000000000')
        self.assertEqual(result, '图书不存在')

    def test_rent_creates_lease_record(self):
        lease_no = self.svc.rent_book(self.member_id, self.isbn)
        self.svc.cursor.execute("SELECT * FROM leasebook WHERE LNo = %s", (lease_no,))
        row = self.svc.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[2], self.member_id)
        self.assertEqual(row[5], '在借')


class BookstoreServiceSearchTest(unittest.TestCase):
    """Bug 6 修复验证：search_books 不接受无效 category 参数"""

    def setUp(self):
        self.svc = BookstoreService()

    def tearDown(self):
        self.svc.close()

    def test_search_by_name(self):
        books = self.svc.search_books('人间')
        self.assertTrue(len(books) > 0)
        self.assertTrue(any('人间' in str(b[1]) for b in books))

    def test_search_by_author(self):
        books = self.svc.search_books('太宰治')
        self.assertTrue(len(books) > 0)

    def test_search_by_press(self):
        books = self.svc.search_books('作家出版社')
        self.assertTrue(len(books) > 0)

    def test_search_no_results(self):
        books = self.svc.search_books('这本书绝对不存在XYZ123')
        self.assertEqual(len(books), 0)

    def test_search_sql_injection_attempt(self):
        books = self.svc.search_books("'; DROP TABLE newbook; --")
        self.assertIsInstance(books, list)
        self.svc.cursor.execute("SELECT COUNT(*) FROM newbook")
        count = self.svc.cursor.fetchone()[0]
        self.assertGreater(count, 0, "SQL injection should not drop table")

    def test_search_returns_tuple_format(self):
        books = self.svc.search_books('人间')
        self.assertTrue(len(books) > 0)
        self.assertEqual(len(books[0]), 6)


class BookstoreServiceQueryTest(unittest.TestCase):
    def setUp(self):
        self.svc = BookstoreService()

    def tearDown(self):
        self.svc.close()

    def test_get_buy_orders(self):
        orders = self.svc.get_buy_orders(100001)
        self.assertIsInstance(orders, list)

    def test_get_buy_orders_nonexistent(self):
        orders = self.svc.get_buy_orders(999999)
        self.assertEqual(orders, [])

    def test_get_buy_orders_format(self):
        orders = self.svc.get_buy_orders(100001)
        if orders:
            self.assertEqual(len(orders[0]), 5)

    def test_get_order_orders(self):
        orders = self.svc.get_order_orders(100001)
        self.assertIsInstance(orders, list)

    def test_get_order_orders_nonexistent(self):
        orders = self.svc.get_order_orders(999999)
        self.assertEqual(orders, [])

    def test_get_lease_records(self):
        records = self.svc.get_lease_records(100001)
        self.assertIsInstance(records, list)

    def test_get_lease_records_nonexistent(self):
        records = self.svc.get_lease_records(999999)
        self.assertEqual(records, [])

    def test_get_lease_records_format(self):
        records = self.svc.get_lease_records(100001)
        if records:
            self.assertEqual(len(records[0]), 5)


class BookstoreServiceRegisterTest(unittest.TestCase):
    def setUp(self):
        self.svc = BookstoreService()

    def tearDown(self):
        self.svc.cursor.execute(
            "DELETE FROM members WHERE IDNo = %s",
            ('999999999999999999',)
        )
        self.svc.cnx.commit()
        self.svc.close()

    def test_register_success(self):
        self.svc.register('999999999999999999', '测试用户', '19900000000', None, '测试地址')
        row = self.svc.login_by_phone('19900000000')
        self.assertIsNotNone(row)
        self.assertEqual(row[2], '测试用户')

    def test_register_and_login(self):
        self.svc.register('999999999999999999', '测试用户', '19900000000')
        row = self.svc.login_by_phone('19900000000')
        self.assertIsNotNone(row)
        self.assertIsNone(row[4])


class AdminLoginTest(unittest.TestCase):
    """Bug 2 修复验证：login 返回的 admin.cnx 应该是正确的连接"""

    def test_login_plaintext_password(self):
        admin = Administrator.login('352230199803030024', '123456')
        self.assertIsNotNone(admin)
        self.assertEqual(admin.name, '张三')
        admin.close()

    def test_login_wrong_password(self):
        admin = Administrator.login('352230199803030024', 'wrongpass')
        self.assertIsNone(admin)

    def test_login_nonexistent_admin(self):
        admin = Administrator.login('000000000000000000', '123')
        self.assertIsNone(admin)

    def test_login_cnx_is_valid(self):
        admin = Administrator.login('352230199803030024', '123456')
        self.assertIsNotNone(admin)
        self.assertIsNotNone(admin.cnx)
        self.assertIsNotNone(admin.cursor)
        admin.cursor.execute("SELECT 1")
        result = admin.cursor.fetchone()
        self.assertEqual(result[0], 1,
                         "BUG2: admin.cnx/cursor 应能正常执行查询")
        admin.close()


class AdminPasswordTest(unittest.TestCase):
    def setUp(self):
        self.admin = Administrator.login('352230199803030024', '123456')

    def tearDown(self):
        if self.admin:
            self.admin.close()

    def test_verify_plaintext_correct(self):
        self.assertTrue(self.admin._verify_password('123456'))

    def test_verify_plaintext_wrong(self):
        self.assertFalse(self.admin._verify_password('wrong'))

    def test_set_password_wrong_old(self):
        result = self.admin.set_password('wrongpass', 'newpass')
        self.assertEqual(result, '旧密码错误')

    def test_verify_hashed_password(self):
        from werkzeug.security import generate_password_hash
        self.admin.password = generate_password_hash('testpass123')
        self.assertTrue(self.admin._verify_password('testpass123'))
        self.assertFalse(self.admin._verify_password('wrongpass'))


class AdminStatisticsTest(unittest.TestCase):
    def setUp(self):
        self.admin = Administrator(1, '352230199803030024', '张三', '123456', None)

    def tearDown(self):
        self.admin.close()

    def test_statistics_keys(self):
        stats = self.admin.statistics()
        self.assertIn('sales', stats)
        self.assertIn('rentals', stats)
        self.assertIn('member_count', stats)
        self.assertIn('book_count', stats)

    def test_statistics_member_count(self):
        stats = self.admin.statistics()
        self.assertIsInstance(stats['member_count'], int)
        self.assertGreater(stats['member_count'], 0)

    def test_statistics_book_count(self):
        stats = self.admin.statistics()
        self.assertIsInstance(stats['book_count'], int)
        self.assertGreater(stats['book_count'], 0)


class AdminSupplementTest(unittest.TestCase):
    def setUp(self):
        self.admin = Administrator(1, '352230199803030024', '张三', '123456', None)
        self.isbn = '9787506380263'
        self.admin.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        self._original_stock = self.admin.cursor.fetchone()[0]

    def tearDown(self):
        self.admin.cursor.execute(
            "UPDATE newbook SET Stock = %s WHERE BNo = %s",
            (self._original_stock, self.isbn)
        )
        self.admin.cnx.commit()
        self.admin.close()

    def test_supplement_newbook(self):
        result = self.admin.supplement('newbook', self.isbn, 5)
        self.assertTrue(result)
        self.admin.cursor.execute("SELECT Stock FROM newbook WHERE BNo = %s", (self.isbn,))
        new_stock = self.admin.cursor.fetchone()[0]
        self.assertEqual(new_stock, self._original_stock + 5)

    def test_supplement_oldbook(self):
        result = self.admin.supplement('oldbook', self.isbn, 3)
        self.assertTrue(result)

    def test_supplement_invalid_table(self):
        with self.assertRaises(ValueError):
            self.admin.supplement('buybook', self.isbn, 1)

    def test_supplement_sql_injection_table(self):
        with self.assertRaises(ValueError):
            self.admin.supplement('newbook; DROP TABLE members;', self.isbn, 1)


class AdminMemberQueryTest(unittest.TestCase):
    def setUp(self):
        self.admin = Administrator(1, '352230199803030024', '张三', '123456', None)

    def tearDown(self):
        self.admin.close()

    def test_get_all_members(self):
        members = self.admin.get_all_members()
        self.assertIsInstance(members, list)
        self.assertGreater(len(members), 0)

    def test_search_member_by_name(self):
        members = self.admin.search_member('萧萧')
        self.assertTrue(len(members) > 0)
        self.assertEqual(members[0][2], '萧萧')

    def test_search_member_by_phone(self):
        members = self.admin.search_member('15861165153')
        self.assertTrue(len(members) > 0)

    def test_search_member_no_result(self):
        members = self.admin.search_member('NOTEXISTUSER')
        self.assertEqual(len(members), 0)


class CategoryListTest(unittest.TestCase):
    def test_categories_defined(self):
        self.assertIsInstance(CATEGORY_LIST, list)
        self.assertEqual(len(CATEGORY_LIST), 8)
        self.assertIn('文学', CATEGORY_LIST)
        self.assertIn('儿童读物', CATEGORY_LIST)


class FlaskAppTest(unittest.TestCase):
    def setUp(self):
        import app as app_module
        app_module.app.config['TESTING'] = True
        app_module.app.config['SECRET_KEY'] = 'test-secret'
        self.client = app_module.app.test_client()

    def test_home_page(self):
        resp = self.client.get('/home')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'XXXX', resp.data)

    def test_app_page_anonymous(self):
        resp = self.client.get('/app')
        self.assertEqual(resp.status_code, 200)

    def test_app_root_anonymous(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_login_page_get(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)

    def test_login_post_invalid_phone(self):
        resp = self.client.post('/login', data={'phone': 'invalid'})
        self.assertIn('手机号格式不正确'.encode('utf-8'), resp.data)

    def test_login_post_valid_phone_exists(self):
        resp = self.client.post('/login', data={'phone': '15861165153'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/home', resp.headers['Location'])

    def test_login_post_new_phone_redirects_register(self):
        resp = self.client.post('/login', data={'phone': '13900001111'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/register', resp.headers['Location'])

    def test_logout_post(self):
        self.client.post('/login', data={'phone': '15861165153'})
        resp = self.client.post('/logout')
        self.assertEqual(resp.status_code, 302)

    def test_my_requires_login(self):
        resp = self.client.get('/my')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers['Location'])

    def test_my_logged_in(self):
        self.client.post('/login', data={'phone': '15861165153'})
        resp = self.client.get('/my')
        self.assertEqual(resp.status_code, 200)

    def test_shopping_requires_login(self):
        resp = self.client.get('/shopping')
        self.assertEqual(resp.status_code, 302)

    def test_recommend_requires_login(self):
        resp = self.client.get('/recommend')
        self.assertEqual(resp.status_code, 302)

    def test_search_empty(self):
        resp = self.client.get('/search')
        self.assertEqual(resp.status_code, 200)

    def test_search_with_keyword(self):
        resp = self.client.get('/search?q=人间')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('人间'.encode('utf-8'), resp.data)

    def test_detail_page(self):
        resp = self.client.get('/detail')
        self.assertEqual(resp.status_code, 200)

    def test_sell_page(self):
        resp = self.client.get('/sell')
        self.assertEqual(resp.status_code, 200)

    def test_book_category_valid(self):
        resp = self.client.get('/book/文学')
        self.assertEqual(resp.status_code, 200)

    def test_book_category_invalid(self):
        resp = self.client.get('/book/不存在的分类')
        self.assertEqual(resp.status_code, 404)

    def test_share_page(self):
        resp = self.client.get('/share')
        self.assertEqual(resp.status_code, 200)

    def test_operator_page(self):
        resp = self.client.get('/operator')
        self.assertEqual(resp.status_code, 200)

    def test_my_feature_requires_login(self):
        resp = self.client.get('/my/已购买')
        self.assertEqual(resp.status_code, 302)

    def test_my_feature_invalid(self):
        self.client.post('/login', data={'phone': '15861165153'})
        resp = self.client.get('/my/不存在的功能')
        self.assertEqual(resp.status_code, 404)

    def test_my_feature_valid_features(self):
        self.client.post('/login', data={'phone': '15861165153'})
        features = ['已购买', '已预订', '已借阅', '待收货', '已完成', '已取消', '其他管理', '成员管理']
        for f in features:
            resp = self.client.get(f'/my/{f}')
            self.assertEqual(resp.status_code, 200, f"Feature '{f}' should return 200")

    def test_unsubscribe_requires_login(self):
        resp = self.client.post('/unsubscribe/test')
        self.assertEqual(resp.status_code, 302)

    def test_sales_return_requires_login(self):
        resp = self.client.post('/return/test')
        self.assertEqual(resp.status_code, 302)

    def test_rent_requires_login(self):
        resp = self.client.post('/rent/9787506380263')
        self.assertEqual(resp.status_code, 302)

    def test_rent_requires_post(self):
        self.client.post('/login', data={'phone': '15861165153'})
        resp = self.client.get('/rent/9787506380263')
        self.assertEqual(resp.status_code, 405)

    def test_admin_login_page_get(self):
        resp = self.client.get('/admin/login')
        self.assertEqual(resp.status_code, 200)

    def test_admin_login_wrong_creds(self):
        resp = self.client.post('/admin/login', data={
            'id_number': '000000000000000000',
            'password': 'wrong'
        })
        self.assertIn('身份证或密码错误'.encode('utf-8'), resp.data)

    def test_admin_login_success(self):
        resp = self.client.post('/admin/login', data={
            'id_number': '352230199803030024',
            'password': '123456'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin', resp.headers['Location'])

    def test_admin_dashboard_requires_login(self):
        resp = self.client.get('/admin')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin/login', resp.headers['Location'])

    def test_admin_dashboard_with_session(self):
        self.client.post('/admin/login', data={
            'id_number': '352230199803030024',
            'password': '123456'
        })
        resp = self.client.get('/admin')
        self.assertEqual(resp.status_code, 200)

    def test_shopping_get_logged_in(self):
        self.client.post('/login', data={'phone': '15861165153'})
        resp = self.client.get('/shopping')
        self.assertEqual(resp.status_code, 200)

    def test_shopping_post_success(self):
        self.client.post('/login', data={'phone': '15861165153'})
        resp = self.client.post('/shopping', data={
            'isbn': '9787108063106',
            'num': '1'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('购买成功'.encode('utf-8'), resp.data)

    def test_shopping_post_bad_num(self):
        self.client.post('/login', data={'phone': '15861165153'})
        resp = self.client.post('/shopping', data={
            'isbn': '9787506380263',
            'num': 'abc'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('请输入正确的数量'.encode('utf-8'), resp.data)

    def test_shopping_post_zero_num(self):
        self.client.post('/login', data={'phone': '15861165153'})
        resp = self.client.post('/shopping', data={
            'isbn': '9787506380263',
            'num': '0'
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('数量必须大于0'.encode('utf-8'), resp.data)

    def test_404_handler(self):
        resp = self.client.get('/nonexistent/page')
        self.assertEqual(resp.status_code, 404)
        self.assertIn(b'404', resp.data)


class PhoneValidationTest(unittest.TestCase):
    def setUp(self):
        from app import _validate_phone
        self.validate = _validate_phone

    def test_china_phone(self):
        self.assertTrue(self.validate('13800138000'))

    def test_us_phone(self):
        self.assertTrue(self.validate('+12025551234'))

    def test_uk_phone(self):
        self.assertTrue(self.validate('+447911123456'))

    def test_with_plus(self):
        self.assertTrue(self.validate('+8613800138000'))

    def test_without_plus(self):
        self.assertTrue(self.validate('8613800138000'))

    def test_too_short(self):
        self.assertFalse(self.validate('123'))

    def test_too_long(self):
        self.assertFalse(self.validate('12345678901234567'))

    def test_starts_with_zero(self):
        self.assertFalse(self.validate('012345678'))

    def test_contains_letter(self):
        self.assertFalse(self.validate('138abc12345'))

    def test_empty(self):
        self.assertFalse(self.validate(''))

    def test_plus_only(self):
        self.assertFalse(self.validate('+'))


class IdCardValidationTest(unittest.TestCase):
    def setUp(self):
        from app import _validate_id_card
        self.validate = _validate_id_card

    def test_valid_all_digits(self):
        self.assertTrue(self.validate('110101199003071234'))

    def test_valid_ending_x(self):
        self.assertTrue(self.validate('11010119900307123X'))

    def test_valid_ending_lowercase_x(self):
        self.assertTrue(self.validate('11010119900307123x'))

    def test_too_short(self):
        self.assertFalse(self.validate('12345678901234567'))

    def test_too_long(self):
        self.assertFalse(self.validate('1234567890123456789'))

    def test_contains_letter_middle(self):
        self.assertFalse(self.validate('110101199A03071234'))

    def test_empty(self):
        self.assertFalse(self.validate(''))


if __name__ == '__main__':
    unittest.main(verbosity=2)
