from flask import Flask, render_template, request, url_for
from Terminal import *

app = Flask(__name__)
app.debug = True
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json;charset=utf-8'
user = Application()
mem = dict()


@app.route('/home')
def home():
    return render_template('首页.html')


@app.route('/skip')
def skip():
    phone = request.args.get('phone')
    id = request.args.get('id')
    if phone:
        if user.login(phone):
            return home()
        else:
            return register(phone)
    elif id:
        mem['id'] = id
        mem['face'] = request.args.get('face')
        mem['name'] = request.args.get('name')
        mem['address'] = request.args.get('address')
        if user.register(mem):
            return home()
        else:
            return login()
    else:
        return '你正在尝试从非法途径访问该网页'


@app.route('/')
@app.route('/app')
def application():
    return render_template('APP界面.html')


@app.route('/my')
def my():
    return render_template('我的.html')


@app.route('/operator')
def operator():
    return render_template('操作.html')


@app.route('/login')
def login():
    return render_template('登录.html')


@app.route('/register/<phone>')
def register(phone):
    mem['phone'] = phone
    return render_template('注册.html')


@app.route('/shopping')
def shopping():
    num = eval(request.args.get('num', 0))
    if num > 0:
        if user.mem.member_id:
            user.sell(user.mem.member_id, '9787506380263', num)
            return render_template('购物车.html', num=num)
        else:
            return '请先注册或登录'
    else:
        return '输入有误'


@app.route('/detail')
def detail():
    return render_template('详情.html')


@app.route('/sell')
def sell():
    return render_template('购买.html')


if __name__ == '__main__':
    app.run()
    app.run(debug=True)
