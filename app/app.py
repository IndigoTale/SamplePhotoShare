from flask import Flask, render_template, request, url_for, redirect, session
from flask_login import LoginManager,login_user,login_required
import json
import lib
from lib import *
from datetime import timedelta
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/add_user')
def add_user():
    return "Hello World!"


@app.route('/login', methods=["GET"])
def loginForm():
    return render_template("login.html")


@app.route('/login', methods=["POST"])
def login():
    result = lib.login_by_email(request.form["email"],request.form["password"])
    if result[0] is True:
        session['user_id'] =  result[1]
        return redirect(url_for('index'))
    else:
        return render_template('login.html', code=result[1])


@app.route('/signup', methods=["GET"])
def signupForm():
    return render_template("signup.html", code=0)


@app.route('/signup', methods=["POST"])
def signup():

    flag = lib.signUpCheck(request.form["username"], request.form["email"],
                           request.form["password"], request.form["repeat-password"])
    if flag[0]:
        return redirect('https://photoshare.tk')
    else:
        return render_template('signup.html',code=flag[1]) 


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
