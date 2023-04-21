import numpy
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import datetime
import pickle
import tensorflow as tf

app = Flask(__name__)

app.secret_key = 'bling'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'atm'

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def register():
    return render_template('insert_card_fingerprint.html')


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    msg = ''

    if request.method == 'POST' and 'accountNumber' in request.form and 'userPinInput' in request.form:
        pin = request.form['userPinInput']
        # get accountnnumber from query string
        accountnumber = request.form['accountNumber']
        print(accountnumber)
        print(pin)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE account_number = % s AND pin = % s', (accountnumber, pin,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['acount_number'] = account['account_number']
            msg = 'Logged in successfully !'
            return render_template('account_detail.html', msg=msg)
        else:
            # return redirect with query string
            return redirect(
                url_for('authenticate', accountNumber=[accountnumber], msg='Incorrect username / password !'))
            # msg = 'Incorrect username / password !'
    return render_template('input_pin_fingerprint.html', msg=msg)


@app.route('/account', methods=['GET', 'POST'])
def account():
    account_number = session.get('acount_number')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE account_number = % s', (account_number,))
    account = cursor.fetchone()

    return render_template('account_detail.html', account=account)


@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    return render_template('deposit.html')


@app.route('/deposit-cash', methods=['GET', 'POST'])
def deposit_cash():
    return render_template('deposit_cash.html')


@app.route('/deposit-check', methods=['GET', 'POST'])
def deposit_check():
    return render_template('deposit_check.html')


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    return render_template('withdraw.html')


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    return render_template('transfer_money.html')


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('acount_number', None)
    return redirect(url_for('authenticate'))


if __name__ == '__main__':
    app.run()
