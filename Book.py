class NewBook:
    def __init__(self, row):
        self.isbn, self.name, self.author, self.press, price, stock = row
        self.price = float(price) if price is not None else 0.0
        self.stock = int(stock) if stock is not None else 0


class OldBook(NewBook):
    RENT_THRESHOLD = 60.0
    RENT_RATE = 0.08
    RENT_FIXED = 6.0

    def __init__(self, row):
        super().__init__(row)
        self.rent = self.price * self.RENT_RATE if self.price <= self.RENT_THRESHOLD else self.RENT_FIXED
