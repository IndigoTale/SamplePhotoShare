from flask import Flask, render_template, request, url_for, redirect, session
from flask_login import LoginManager, login_user, login_required
from werkzeug.utils import secure_filename
import json
# MyModule
from dynamodb import*
import s3
from my_utils import*
# Others
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

FQDN = "https://photoshare.tk"
userIdTable = userIdTable()
userNameTable = userNameTable()
photoTable = photoTable()
photoTimeSeriesTable = photoTimeSeriesTable()


@app.route('/')
@app.route('/index/')
def index():
    if session.get('user_id') is not None:
        res = userIdTable.get(session.get('user_id'))
        if res['status'] == 200:
            return render_template('login-index.html', username=res['username'])
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
    if request.form.get("user_id") and request.form.get("password"):

        res = userIdTable.login(request.form.get(
            "user_id"), request.form.get("password"))
        if res.get("status") == 200:
            session['user_id'] = request.form.get("user_id")
            return redirect(FQDN)
        else:
            return render_template('login.html', status=res.get("status"))
    else:
        return render_template('login.html', status=400)


@app.route('/logout', methods=['GET'])
def logout():
    if session.get('user_id') is not None:
        session.pop('user_id', None)
        return redirect(FQDN)
    else:
        return redirect(FQDN)


@app.route('/signup', methods=["GET"])
def signup_form():
    return render_template("signup.html")


@app.route('/signup', methods=["POST"])
def signup():
    # フォーム記入漏れ確認
    if request.form.get("username") and \
            request.form.get("email") and \
            request.form.get("password") and\
            request.form.get("repeat-password"):
        user_id, username, password, repeat_password = \
            request.form["email"], request.form["username"], request.form["password"], request.form["repeat-password"]
    else:
        return render_template("signup.html", form=False)

    flag = {"id": False, "name": False}
    res_id = userIdTable.sign_up(user_id, username, password, repeat_password)
    if res_id.get("status") == 201:
        flag["id"] = True
    elif res_id.get("status") == 409:
        return render_template('signup.html', id=False)
    elif res_id.get("status") == 401:
        return render_template('signup.html', password=False)
    else:
        return render_template('signup.html', format=False)

    
    res_name = userNameTable.get(username)
    if res_name.get("status") == 404:
        res_name = userNameTable.put(username,user_id)
        if res_name.get("status") == 201:
            flag["name"] = True

    if flag["id"] and flag["name"]:
        return redirect(FQDN+"/login")
    else:
        if flag["id"]:
            userIdTable.delete(user_id)
        if flag["name"]:
            userNameTable.delete(username)
        
        return render_template("signup.html",id=flag["id"],name=flag["name"])

@app.route('/upload', methods=['GET'])
def upload_form():

    if session.get('user_id') is not None:

        res = userIdTable.get(session.get('user_id'))
        # 認証されたユーザ
        if res['status'] == 200:
            return render_template('upload.html', username=res['record']["Item"]['username'])
        # ユーザが存在しない
        elif res['status'] == 404:
            return redirect(FQDN+"/signup")
        else:
            return redirect(FQDN)
    else:
        return redirect(FQDN+"/login")


@app.route('/upload', methods=['POST'])
def upload():
    # フォームが足りているか
    if request.form.get('upload-title') and request.form.get('upload-comment') and request.files.get('upload-file'):
        title = request.form.get('upload-title')
        self_comment = request.form.get('upload-comment')
        img_file = request.files.get('upload-file')
    else:
        return render_template("upload.html", form=False)
    # ログインしているか
    if session.get('user_id') is not None:
        user_id = session.get('user_id')
        username = userNameTable.get(username).get(
            "record").get("Item")["username"]
        res = userIdTable.get(user_id)
        # ユーザが存在する
        if res['status'] == 200:
            pass
        # 存在しない
        elif res['status'] == 404:
            return redirect(FQDN+"/signup")
        # エラー
        else:
            return redirect(FQDN)
    # ログインしていない
    else:
        return redirect(FQDN+"/login")

    # フォームが揃っている　and ログイン中　and ユーザが存在する　
    # ファイルの拡張子を確認
    if allowed_file(img_file.filename) is not True:
        return render_template('upload.html', file_extention=False)

    filename = f"{uuid.uuid4().hex}.{img_file.filename.split('.')[1]}"
    photo_id = uuid.uuid4().hex

    flag = {"s3": False, "photoTable": False, "photoTimeSeriesTable": False}

    # S3に写真をアップロード
    res = s3.uploadPhoto(img_file, filename)
    if res.get("status") == 201:
        flag["s3"] = True

    # photoTableにレコードを追加
    created_at = get_cuurent_timestamp()

    res = photoTable.put(photo_id, created_at, user_id,
                         username, title, self_comment, filename)
    if res.get("status") == 201:
        flag["photoTable"] = True
    # photoTimeSeriesTableにレコードを追加
    res = photoTimeSeriesTable.put(created_at, photo_id)
    if res.get("status") == 201:
        flag["photoTimeSeriesTable"] = True

    if flag["s3"] and flag["photoTable"] and flag["photoTimeSeriesTable"]:
        return redirect(FQDN)
    else:
        if flag["s3"]:
            s3.deletePhoto(filename)
        if flag["photoTable"]:
            photoTable.delete(photo_id)
        if flag["photoTimeSeriesTable"]:
            photoTimeSeriesTable.delete(created_at, photo_id)
        return render_template("upload.html", upload=False)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
