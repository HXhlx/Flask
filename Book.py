from datetime import datetime


class NewBook:
    def __init__(self, new):
        self.ISBN, self.name, self.author, self.press, self.price, self.number = new


class OldBook(NewBook):
    def __init__(self, old):
        NewBook.__init__(self, old)
        if self.price <= 60:
            self.rent = self.price * 0.08
        else:
            self.rent = 6
