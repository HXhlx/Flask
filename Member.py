class Account:
    def __init__(self, account_id, balance):
        self.account_id = account_id
        self.balance = balance

    def settle(self, price):
        self.balance -= price


class Member:
    def __init__(self, info):
        self.member_id, self.id, self.name, self.phone, self.face, self.score, self.address = info

    # def to_dict(self):
    #     return {
    #         '会员号': self.member_id,
    #         '身份证号': self.id,
    #         '姓名': self.name,
    #         '电话号码': self.phone,
    #         '头像': self.face,
    #         '积分': self.score,
    #         '住址': self.address
    #     }
