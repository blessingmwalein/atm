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


@app.route('/users', methods=['GET', 'POST'])
def users():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users')

    users = cursor.fetchall()
    mysql.connection.commit()
    if request.method == 'POST':
        pin = request.form['pin']
        # get accountnnumber from query string
        accountnumber = request.form['account_number']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        id_number = request.form['id_number']

        print(accountnumber)
        print(pin)
        print(first_name)
        print(last_name)
        print(dob)
        print(id_number)

        newCursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        newCursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s,% s, % s, % s, % s)',
                          (first_name, last_name, dob, id_number, pin, "0", accountnumber,))
        mysql.connection.commit()

        return render_template('users.html', users=users, msg="User Added")

    return render_template('users.html', users=users, msg="")


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    msg = ''

    if request.method == 'POST' and 'accountNumber' in request.form and 'userPinInput' in request.form:

        #check if pin is empty
        


        pin = request.form['userPinInput']
        # get accountnnumber from query string
        accountnumber = request.form['accountNumber']
        print(accountnumber)
        print(pin)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.form['userPinInput'] == '':
            cursor.execute('SELECT * FROM users WHERE account_number = % s', (accountnumber,))
        else:
            cursor.execute('SELECT * FROM users WHERE account_number = % s AND pin = % s', (accountnumber, pin,))

        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['acount_number'] = account['account_number']
            msg = 'Logged in successfully !'

            account = getAcccount()
            return render_template('account_detail.html', msg=msg, account=account)
        else:
            # return redirect with query string
            return redirect(
                url_for('authenticate', accountNumber=[accountnumber], msg='Credentials do not match our records !'))
            # msg = 'Incorrect username / password !'
    return render_template('input_pin_fingerprint.html', msg=msg)
@app.route('/register', methods=['GET', 'POST'])
def regsiter_print():
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

            account = getAcccount()
            return render_template('account_detail.html', msg=msg, account=account)
        else:
            # return redirect with query string
            return redirect(
                url_for('authenticate', accountNumber=[accountnumber], msg='Incorrect username / password !'))
            # msg = 'Incorrect username / password !'
    return render_template('register_finger.html', msg=msg)

@app.route('/account', methods=['GET', 'POST'])
def account():
    account = getAcccount()

    return render_template('account_detail.html', account=account)


@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    account = getAcccount()
    return render_template('deposit.html', account=account)


@app.route('/deposit-cash', methods=['GET', 'POST'])
def deposit_cash():
    account = getAcccount()
    if request.method == 'POST' and 'amountToDeposit' in request.form:
        accountnumber = request.form['amountToDeposit']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE users SET balance=balance + %s WHERE id=%s",
                       (accountnumber, session.get('id'),))
        mysql.connection.commit()
        return render_template('deposit_cash.html', account=account, msg='Deposit successfully !')

    return render_template('deposit_cash.html', account=account, msg='')


@app.route('/deposit-check', methods=['GET', 'POST'])
def deposit_check():
    account = getAcccount()

    return render_template('deposit_check.html', account=account)


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    account = getAcccount()
    if request.method == 'POST' and 'userPinInput' in request.form:
        # convert string to float

        userPinInput = float(request.form['userPinInput'])

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE users SET balance=balance - %s WHERE id=%s",
                       (userPinInput, session.get('id'),))
        mysql.connection.commit()
        return render_template('withdraw.html', account=account, msg='Withdraw successfully !')

    return render_template('withdraw.html', account=account, msg="")


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    account = getAcccount()
    return render_template('transfer_money.html', account=account)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('acount_number', None)
    return redirect(url_for('authenticate'))


def getAcccount():
    account_number = session.get('acount_number')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE account_number = % s', (account_number,))
    return cursor.fetchone()


if __name__ == '__main__':
    app.run()
