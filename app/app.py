from flask import Flask, render_template, request, url_for, redirect, session
from flask_login import LoginManager, login_user, login_required
from flask_cors import CORS
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
CORS(app)

FQDN = "https://photoshare.tk"
userIdTable = userIdTable()
userNameTable = userNameTable()
photoTable = photoTable()
photoTimeSeriesTable = photoTimeSeriesTable()


@app.route('/')
def index():
    res = photoTimeSeriesTable.photoTimeSeriesTable.query(
        KeyConditionExpression=Key("dummy").eq("dummy") & Key(
            "created_at").lte(get_cuurent_timestamp()),
        Limit=20,
        ScanIndexForward=False
    )

    photos = []
    if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
        for item in res["Items"]:
            res_in = photoTable.get(item["photo_id"])
            if res_in["status"] == 200:
                photos.append(res_in["record"]["Item"])

    if session.get('user_id') is None:
        return render_template("index.html", photos=photos)
    res = userIdTable.get(session.get('user_id'))
    if res['status'] == 200:
        return render_template('login-index.html', username=res["record"]["Item"]['username'], photos=photos)
    else:
        return render_template("index.html", photos=photos)




@app.route('/login', methods=["GET"])
def loginForm():
    return render_template("login.html")


@app.route('/login', methods=["POST"])
def login():
    if request.form.get("email") and request.form.get("password"):
        user_id, password = request.form.get(
            "email"), request.form.get("password")
    else:
        return render_template("login.html", form=False)

    res = userIdTable.login(user_id, password)
    if res.get("status") == 404:
        return render_template("login.html", user=False)
    elif res.get("status") == 401:
        return render_template("login.html", password=False)
    elif res.get("status") == 400:
        return render_template("login.html", format=False)
    else:
        session['user_id'] = user_id
        return redirect(FQDN)


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
        res_name = userNameTable.put(username, user_id)
        if res_name.get("status") == 201:
            flag["name"] = True

    if flag["id"] and flag["name"]:
        return redirect(FQDN+"/login")
    else:
        if flag["id"]:
            userIdTable.delete(user_id)
        if flag["name"]:
            userNameTable.delete(username)

        return render_template("signup.html", id=flag["id"], name=flag["name"])


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
    # フォーム記入漏れがないか
    if request.form.get('upload-title') and request.form.get('upload-comment') and request.files.get('upload-file'):
        title = request.form.get('upload-title')
        self_comment = request.form.get('upload-comment')
        img_file = request.files.get('upload-file')
    else:
        return render_template("upload.html", form=False)
    # ログインしているか
    if session.get('user_id') is None:
        return redirect(FQDN+"/login")
    user_id = session.get('user_id')
    res = userIdTable.get(user_id)
    # ユーザデータが存在する
    if res['status'] == 200:
        pass
    # 存在しない
    elif res['status'] == 404:
        return redirect(FQDN+"/signup")
    else:
        return redirect(FQDN)

    username = res["record"]["Item"]["username"]

    # フォームが揃っている　and ログイン中　and ユーザデータが存在する　
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
    now = datetime.now(JST)
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
            photoTimeSeriesTable.delete(created_at)
        return render_template("upload.html", upload=False)

@app.route('/heart', methods=['POST'])
def  heart():

    if session.get("user_id") is None:
        return None, 403 # Forbidden 
    if request.json.get("photo_id") is None:
        return None,400 # Bad Request
    user_id , photo_id = session["user_id"] , request.json["photo_id"]
    
    res = photoTable.get(photo_id)
    if res["status"] == 200:
        hearts = res["record"]["Item"]["hearts"]
        print(hearts)
        username = userIdTable.get(user_id).get("record").get("Item").get("username")
        # ハートを押す
        if username not in hearts:
            hearts.append(username)

            photoTable.update(photo_id,{"hearts":{"Value":hearts,"Action":"PUT"}})
            return json.dumps({"push":True}),200
        # ハートを取り消し
        else:
            hearts.pop(hearts.index(username))
            photoTable.update(photo_id,{"hearts":{"Value":hearts,"Action":"PUT"}})
            return json.dumps({"push":False}),200

    elif res["status"] == 404:
        return None, 404 # Not Found
    else:
        return None, 400 # Server Down


@app.route('/photo/<photo_id>', methods=["GET"])
def photo(photo_id):
    res = photoTable.get(photo_id)
    if res["status"] == 200:
        filename = res["record"]["Item"]["filename"]

    if session.get("user_id") is None:
        return render_template("photo.html",filename = filename)
    else:
        return render_template("photo-login.html",filename = filename)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True,threaded=True)
