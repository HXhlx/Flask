import os
import re
from dotenv import load_dotenv
from flask import Flask, render_template, request
from Terminal import Application

load_dotenv()

app = Flask(__name__)
app.debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json;charset=utf-8'
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
user = Application()


def validate_phone(phone):
    return bool(re.match(r'^1[3-9]\d{9}$', str(phone)))


def validate_id_card(id_card):
    return bool(re.match(r'^\d{17}[\dXx]$', str(id_card)))


@app.route('/home')
def home():
    return render_template('首页.html')


@app.route('/skip')
def skip():
    phone = request.args.get('phone')
    id = request.args.get('id')
    if phone:
        if not validate_phone(phone):
            return '手机号格式不正确', 400
        if user.login(phone):
            return home()
        else:
            return register(phone)
    elif id:
        if not validate_id_card(id):
            return '身份证号格式不正确', 400
        mem = {
            'id': id,
            'face': request.args.get('face'),
            'name': request.args.get('name'),
            'address': request.args.get('address'),
            'phone': phone if phone else request.args.get('phone')
        }
        if user.register(mem):
            return home()
        else:
            return login()
    else:
        return '你正在尝试从非法途径访问该网页', 403


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
    return render_template('注册.html', phone=phone)


@app.route('/shopping')
def shopping():
    try:
        num = int(request.args.get('num', 0))
    except (ValueError, TypeError):
        return '输入有误', 400
    if num > 0:
        if user.mem.member_id:
            user.sell(user.mem.member_id, '9787506380263', num)
            return render_template('购物车.html', num=num)
        else:
            return '请先注册或登录', 401
    else:
        return '输入有误', 400


@app.route('/detail')
def detail():
    return render_template('详情.html')


@app.route('/sell')
def sell():
    return render_template('购买.html')


@app.route('/book/<category>')
def book_category(category):
    allowed = ['儿童读物', '文学', '青少年读物', '考试图书', '人文历史', '科学', '金融经济', '中小学教辅']
    if category not in allowed:
        return '分类不存在', 404
    return render_template(f'图书分类/{category}.html')


@app.route('/share')
def share():
    return render_template('分享.html')


@app.route('/my/<feature>')
def my_feature(feature):
    allowed = ['已完成', '已借阅', '已取消', '已购买', '待收货', '已预订', '其他管理', '成员管理']
    if feature not in allowed:
        return '功能不存在', 404
    return render_template(f'我的功能/{feature}.html')


@app.route('/unsubscribe/<ono>')
def unsubscribe(ono):
    result = user.unsubscribe(ono)
    if result is True:
        return '退订成功'
    return str(result), 400


@app.route('/return/<buyno>')
def sales_return(buyno):
    result = user.sales_return(buyno)
    if result is True:
        return '退货成功'
    return str(result), 400


@app.route('/recommend')
def recommend():
    if not user.mem.member_id:
        return '请先登录', 401
    books = user.recommend(user.mem.member_id)
    return render_template('推荐.html', books=books)


@app.route('/pick_up/<lno>')
def pick_up(lno):
    result = user.pick_up(lno)
    if result is True:
        return '提货成功'
    return str(result), 400


@app.route('/give_back/<lno>')
def give_back(lno):
    result = user.give_back(lno)
    if isinstance(result, (int, float)):
        return f'归还成功，租金: {result}元'
    return str(result), 400


@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
