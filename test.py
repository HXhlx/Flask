import unittest
from Terminal import Application
from mysql.connector import connect
from Administrator import Administrator


class ApplicationTest(unittest.TestCase):
    def setUp(self):
        self.app = Application()
        self.admin = Administrator(1, '352230199803030024', '张三', '123456', None)
        self.mem = {
            'id': '987654200006014321',
            'name': '胡图图',
            'face': r'D:\Python\bookstore_flask\static\photo\头像.jpg',
            'address': '翻斗大街翻斗花园二号楼1001室',
            'phone': 20000601
        }

    def test_register(self):
        self.assertTrue(self.app.register(self.mem))
        self.cnx = connect(user="root", password="hx19990627", database="bookstore")
        self.cursor = self.cnx.cursor()
        self.cursor.execute("delete from members where IDNo = {}".format(self.mem['id']))
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

    def test_login(self):
        self.assertTrue(self.app.login(15861165153))
        self.assertIsNone(self.app.login(123))

    def test_sell(self):
        self.assertIsNone(self.app.sell(100007, '9787506380263', 20))
        self.assertIsNone(self.admin.supplement('newbook', '9787506380263', 20))
        self.assertEqual(self.app.sell(100007, '9787506380263', 23), '库存不足')


if __name__ == '__main__':
    unittest.main()
