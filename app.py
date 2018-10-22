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


# /register/'joren111'/'jor'/'pacaldo'/'celeron0912'/'09156086751'/True
@app.route('/register/<string:username>/<string:name>/<string:fname>/<string:password>/<string:mobnum>/<string:admin_prev>')
def register(username,name,fname,password,mobnum,admin_prev):
    res = spcall('register', (username, name, fname, password, mobnum, admin_prev), True)

    if 'Error' in res[0][0]:
        return jsonify({'status': 'error', 'message': res[0][0]})
    else:
        return res[0][0]

@app.route('/dashboard/<string:id>', methods=['GET'])
def dashboard(id):
    res = spcall('user_credentials', (id,),)

    recs = []

    for r in res:
        recs.append({"firstname": r[0],"lastname": r[1], "mobile_number": r[2], "admin_prev": str(r[3])})
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