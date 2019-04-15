from flask import Flask, render_template, request, url_for, redirect, session
from flask_login import LoginManager, login_user, login_required
from werkzeug.utils import secure_filename
import json
import lib
from lib import *
from datetime import timedelta
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


@app.route('/')
@app.route('/index/')
def index():
    if session.get('user_id') is not None:
        res = queryUserIdTable(session.get('user_id'))
        if res[0] is True:
            return render_template('login-index.html', username=res[2])
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")


@app.route('/add_user')
def add_user():
    return "Hello World!"


@app.route('/login', methods=["GET"])
def loginForm():
    return render_template("login.html")


@app.route('/login', methods=["POST"])
def login():
    result = lib.login_by_email(
        request.form["email"], request.form["password"])
    if result[0] is True:
        session['user_id'] = result[1]
        return redirect('https://photoshare.tk')
    else:
        return render_template('login.html', code=result[1])


@app.route('/logout', methods=['GET'])
def logout():
    if session.get('user_id') is not None:
        session.pop('user_id', None)
        return redirect('https://photoshare.tk')
    else:
        return redirect('https://photoshare.tk')


@app.route('/signup', methods=["GET"])
def signup_form():
    return render_template("signup.html", code=0)


@app.route('/signup', methods=["POST"])
def signup():
    flag = lib.signUpCheck(request.form["username"], request.form["email"],
                           request.form["password"], request.form["repeat-password"])
    if flag[0]:
        session['user_id'] = request.form['email']

        return redirect('https://photoshare.tk')
    else:
        return render_template('signup.html', code=flag[1])


@app.route('/upload', methods=['GET'])
def upload_form():
    if session.get('user_id') is not None:
        res = queryUserIdTable(session.get('user_id'))
        if res[0] is True:
            return render_template('upload.html', username=res[2])
        else:
            return redirect("https://photoshare.tk/signup")
    else:
        return redirect("https://photoshare.tk/login")

    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    # 認証
    if session.get('user_id') is not None:
        res = queryUserIdTable(session.get('user_id'))
        if res[0] is True:
            user_id = res[0]
            username = res[1]
        else:
            return redirect("https://photoshare.tk/signup")
    else:
        return redirect("https://photoshare.tk/login")
    # フォームが揃っているか
    if request.form.get('upload-title') and request.form.get('upload-comment') and request.file.get('upload-file'):
        title = request.form.get('upload-title')
        comment = request.form.get('upload-comment')
        img_file = request.file.get('upload-file')
        if img_file and allowed_file(img_file.filename):
            filename = f"{uuid.uuid4().hex}.{img_file.filename.split('.')[1]}"            
            if lib.upload_photo_to_s3(img_file,filename) and \
                lib.upload_photo_info_to_dynamodb(filename,title,comment,user_id,username):
                    return redirect(request.url)

    return "Fail"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
