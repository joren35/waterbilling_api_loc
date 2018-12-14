from flask import Flask, jsonify, request, session, render_template, url_for, redirect
from model import DBconn
import flask, sys, os

app = Flask(__name__)
app.secret_key = 'celeron0912'


# app.config['SESSION_TYPE'] = 'filesystem'

def spcall(qry, param, commit=False):
    try:
        dbo = DBconn()
        cursor = dbo.getcursor()
        cursor.callproc(qry, param)
        res = cursor.fetchall()
        if commit:
            dbo.dbcommit()
        return res
    except:
        res = [("Error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]),)]
    return res


@app.route('/')
def index():
    return "<h2>Welcome to WaterBillingAPI<h2>"


@app.route('/login', methods=['POST'])
def login():
    params = request.get_json()
    username = params["username"]
    password = params["password"]
    res = spcall('login', (username, password), True)

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    else:
        return jsonify({'status': res[0][0]})


@app.route('/register', methods=['POST'])
def register():
    params = request.get_json()
    username = params["username"]
    password = params["password"]
    number = params["number"]
    reg_key = params["reg_key"]
    res = spcall('register', (username, password, number, reg_key), True)

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    elif 'Invalid' in res[0][0]:
        return jsonify({'status': 'error', 'reason': 'Invalid Registration Key'})
    elif 'used' in res[0][0]:
        return jsonify({'status': 'error', 'reason': 'used'})
    else:
        return jsonify({'status': 'ok', 'user': res[0][0]})


@app.route('/account/new', methods=['POST'])
def add_account():
    params = request.get_json()
    firstname = params["firstname"]
    lastname = params["lastname"]
    address = params["address"]
    act_key = params["act_key"]
    reading = params["reading"]
    amount = params["amount"]
    rate = params["rate"]
    cmused = params["cmused"]
    date_issued = params["date_issued"]
    due_date = params["due_date"]
    s_status = params["s_status"]
    res = spcall('add_account', (
    firstname, lastname, address, act_key, reading, amount, rate, cmused, date_issued, due_date, s_status), True)

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    else:
        return jsonify({'status': 'ok', 'user': res[0][0]})


@app.route('/registration_admin', methods=['POST'])
def register_admin():
    params = request.get_json()
    username = params["username"]
    first_name = params["first_name"]
    last_name = params["last_name"]
    password = params["password"]
    mobile_num = params["mobile_num"]
    admin_prev = params["admin_prev"]
    address = params["address"]
    g_name = params["group_name"]
    res = spcall('register_admin', (username, first_name, last_name, password, mobile_num, admin_prev, g_name, address),
                 True)

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    else:
        return res[0][0]


@app.route('/user/<string:id>', methods=['GET'])
def dashboard(id):
    res = spcall('user_credentials', (id,), )

    recs = []

    for r in res:
        recs.append({"firstname": r[0], "lastname": r[1], "mobile_number": r[2], "admin_prev": str(r[3])})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/validate/username', methods=['POST'])
def validator_username():
    params = request.get_json()
    username = params["username"]
    res = spcall('username_validator', (username,), )

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    elif 'exist' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0], 'specific': 'exist'})
    else:
        return jsonify({'status': res[0][0]})


@app.route('/validate/key', methods=['POST'])
def validator_key():
    params = request.get_json()
    actCode = params["actCode"]
    res = spcall('key_validator', (actCode,), )

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    elif 'exist' in res[0][0]:
        return jsonify({'status': 'exist', 'message': res[0][0]})
    else:
        return jsonify({'status': res[0][0]})


@app.route('/bill/<string:id>', methods=['GET'])
def get_bill_date(id):
    res = spcall('get_bills', (id,), )

    recs = []

    for r in res:
        recs.append(
            {"id": r[0], "date": r[1], "due_date": r[2], "reading": r[3], "amount": str(r[4]), "cubic_meters": r[5],
             "status": r[6]})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/account/status/<string:status>', methods=['GET'])
def get_acc_status(status):
    res = spcall('activation_status', (status,), )

    recs = []

    for r in res:
        recs.append({"name": r[0], "code": r[1]})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/search/<string:name>', methods=['GET'])
def search(name):
    res = spcall('searchbill', (name,), )

    recs = []

    for r in res:
        recs.append({"id": r[0], "firstname": r[1], "lastname": r[2], "address": r[3]})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/users', methods=['GET'])
def users():
    res = spcall('get_names', (), )

    recs = []
    for r in res:
        recs.append({"id": r[0], "lastname": r[1], "firstname": r[2], "issued": r[3], "prev_reading": r[4]})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/user/bills/month/', methods=['GET'])
def billing_users():
    res = spcall('get_names', (), )

    recs = []
    for r in res:
        recs.append({"id": r[0], "lastname": r[1], "firstname": r[2], "issued": r[3], "prev_reading": r[4]})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/bill/user/<string:id>', methods=['GET'])
def user_bill(id):
    res = spcall('get_latestbill_user', (id,), )

    recs = []

    for r in res:
        recs.append({"reading": r[0], "date_issued": r[1], "due_date": r[2], "amount": str(r[3]), "used_cm": r[4],
                     "payment_status": r[5], "unpaid_count": r[6], "arrears": str(r[7]), "total_amount": str(r[8]),
                     "status": r[9]})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.route('/billing', methods=['POST'])
def billing():
    params = request.get_json()
    cur_user = params["cur_user"]
    cur_date = params["cur_date"]
    reading = params["reading"]
    rate = params["rate"]

    res = spcall('add_bill', (cur_user, cur_date, reading, rate), True)

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    else:
        return jsonify({'status': 'ok'})


@app.route('/viewpaid/<string:views>', methods=['GET'])
def viewpaid(views):
    res = spcall('viewpaid', (views,), )

    recs = []

    for r in res:
        recs.append({"firstname": r[0], "lastname": r[1],'date_of_bill': r[2], "reading": r[3], "amount": str(r[4])})
    return jsonify({'status': 'ok', 'entries': recs, 'count': len(recs)})


@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get(
        'Origin', '*')
    resp.headers['Access-Control-Allow-Credentials'] = True
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET, PUT, DELETE'
    resp.headers['Access-Control-Allow-Headers'] = flask.request.headers.get('Access-Control-Request-Headers',
                                                                             'Authorization')

    # set low for debugging

    if app.debug:
        resp.headers["Access-Control-Max-Age"] = '1'
    return resp


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
