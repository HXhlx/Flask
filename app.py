import os
import re
import functools
from decimal import Decimal
from flask import Flask, render_template, request, session, redirect, url_for, abort
from dotenv import load_dotenv
from Terminal import BookstoreService, CATEGORY_LIST
from Administrator import Administrator
from Member import Member

load_dotenv()

app = Flask(__name__)
app.debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json;charset=utf-8'
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')


def _validate_phone(phone):
    return bool(re.match(r'^\+?[1-9]\d{6,14}$', str(phone)))


def _validate_id_card(id_card):
    return bool(re.match(r'^\d{17}[\dXx]$', str(id_card)))


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'member_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return wrapper


@app.before_request
def _load_user():
    from flask import g
    g.member = None
    if 'member_id' in session:
        with BookstoreService() as svc:
            row = svc.get_member(session['member_id'])
            if row:
                g.member = Member(row)


@app.context_processor
def _inject_user():
    from flask import g
    return {'member': getattr(g, 'member', None)}


@app.route('/home')
def home():
    return render_template('首页.html', categories=CATEGORY_LIST)


@app.route('/')
@app.route('/app')
def app_page():
    if 'member_id' in session:
        return redirect(url_for('home'))
    return render_template('APP界面.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        if not _validate_phone(phone):
            return render_template('登录.html', error='手机号格式不正确')
        with BookstoreService() as svc:
            row = svc.login_by_phone(phone)
            if row:
                session['member_id'] = row[0]
                session['member_name'] = row[2]
                return redirect(url_for('home'))
            session['pending_phone'] = phone
            return redirect(url_for('register_page'))
    return render_template('登录.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    phone = session.get('pending_phone')
    if not phone and request.method == 'GET':
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        id_number = request.form.get('id', '').strip()
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        if not _validate_id_card(id_number):
            return render_template('注册.html', phone=phone, error='身份证号格式不正确')
        if not name:
            return render_template('注册.html', phone=phone, error='请输入姓名')
        with BookstoreService() as svc:
            svc.register(id_number, name, phone, None, address)
            row = svc.login_by_phone(phone)
            if row:
                session['member_id'] = row[0]
                session['member_name'] = row[2]
            session.pop('pending_phone', None)
        return redirect(url_for('home'))
    return render_template('注册.html', phone=phone)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('app_page'))


@app.route('/my')
@login_required
def my():
    return render_template('我的.html')


@app.route('/operator')
def operator():
    return render_template('操作.html')


@app.route('/shopping', methods=['GET', 'POST'])
@login_required
def shopping():
    if request.method == 'POST':
        try:
            num = int(request.form.get('num', 0))
        except (ValueError, TypeError):
            return render_template('购物车.html', error='请输入正确的数量')
        isbn = request.form.get('isbn', '9787506380263')
        if num <= 0:
            return render_template('购物车.html', error='数量必须大于0')
        with BookstoreService() as svc:
            result = svc.sell(session['member_id'], isbn, num)
            if result is True or (isinstance(result, str) and result.startswith('B')):
                return render_template('购物车.html', num=num, success='购买成功')
            return render_template('购物车.html', error=str(result))
    return render_template('购物车.html')


@app.route('/sell')
def sell_page():
    return render_template('购买.html')


@app.route('/detail')
def detail():
    return render_template('详情.html')


@app.route('/book/<category>')
def book_category(category):
    if category not in CATEGORY_LIST:
        abort(404)
    return render_template(f'图书分类/{category}.html', category=category)


@app.route('/share')
def share():
    return render_template('分享.html')


@app.route('/my/<feature>')
@login_required
def my_feature(feature):
    allowed = ['已完成', '已借阅', '已取消', '已购买', '待收货', '已预订', '其他管理', '成员管理']
    if feature not in allowed:
        abort(404)
    data = None
    with BookstoreService() as svc:
        mid = session['member_id']
        if feature == '已购买':
            data = svc.get_buy_orders(mid)
        elif feature == '已预订':
            data = svc.get_order_orders(mid)
        elif feature == '已借阅':
            data = svc.get_lease_records(mid)
        elif feature == '已取消':
            data = []
        elif feature == '已完成':
            data = svc.get_buy_orders(mid)
        elif feature == '待收货':
            data = svc.get_order_orders(mid)
    return render_template(f'我的功能/{feature}.html', data=data)


@app.route('/unsubscribe/<order_no>', methods=['POST'])
@login_required
def unsubscribe(order_no):
    with BookstoreService() as svc:
        result = svc.unsubscribe(order_no, session['member_id'])
    if result is True:
        return redirect(url_for('my_feature', feature='已取消'))
    return str(result), 400


@app.route('/return/<buy_no>', methods=['POST'])
@login_required
def sales_return(buy_no):
    with BookstoreService() as svc:
        result = svc.sales_return(buy_no, session['member_id'])
    if result is True:
        return redirect(url_for('my_feature', feature='已完成'))
    return str(result), 400


@app.route('/pick_up/<lease_no>', methods=['POST'])
@login_required
def pick_up(lease_no):
    with BookstoreService() as svc:
        result = svc.pick_up(lease_no, session['member_id'])
    if result is True:
        return redirect(url_for('my_feature', feature='已完成'))
    return str(result), 400


@app.route('/give_back/<lease_no>', methods=['POST'])
@login_required
def give_back(lease_no):
    with BookstoreService() as svc:
        result = svc.give_back(lease_no, session['member_id'])
    if isinstance(result, (int, float, Decimal)):
        return redirect(url_for('my_feature', feature='已借阅'))
    return str(result), 400


@app.route('/recommend')
@login_required
def recommend():
    with BookstoreService() as svc:
        books = svc.recommend(session['member_id'])
    return render_template('推荐.html', books=books)


@app.route('/search')
def search():
    keyword = request.args.get('q', '').strip()
    books = []
    if keyword:
        with BookstoreService() as svc:
            books = svc.search_books(keyword)
    return render_template('搜索结果.html', books=books, keyword=keyword)


@app.route('/rent/<isbn>', methods=['POST'])
@login_required
def rent_book(isbn):
    with BookstoreService() as svc:
        result = svc.rent_book(session['member_id'], isbn)
    if result is True or (isinstance(result, str) and result.startswith('L')):
        return redirect(url_for('my_feature', feature='已借阅'))
    return str(result), 400


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        id_number = request.form.get('id_number', '').strip()
        password = request.form.get('password', '').strip()
        admin = Administrator.login(id_number, password)
        if admin:
            session['admin_id'] = admin.admin_id
            session['admin_name'] = admin.name
            admin.close()
            return redirect(url_for('admin_dashboard'))
        return render_template('管理员登录.html', error='身份证或密码错误')
    return render_template('管理员登录.html')


@app.route('/admin')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    admin = Administrator(
        session['admin_id'], None,
        session.get('admin_name', ''), None, None
    )
    stats = admin.statistics()
    admin.close()
    return render_template('管理员面板.html', stats=stats)


@app.route('/admin/password', methods=['POST'])
def admin_change_password():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    old_pwd = request.form.get('old_password', '')
    new_pwd = request.form.get('new_password', '')
    admin = Administrator(
        session['admin_id'], None,
        session.get('admin_name', ''), None, None
    )
    result = admin.set_password(old_pwd, new_pwd)
    admin.close()
    if result is True:
        return redirect(url_for('admin_dashboard'))
    return render_template('管理员面板.html', error=str(result))


@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port,
            debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
