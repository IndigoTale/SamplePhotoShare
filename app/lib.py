from flask import render_template
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import hashlib
import json
import os
import uuid
# タイムゾーンの作成
from datetime import datetime, timedelta, timezone
JST = timezone(timedelta(hours=+9), 'JST')
# 投稿可能な画像の拡張子
ALLOWED_EXTENSIONS = ('png', 'jpeg')


with open("/app/aws_session_info.json", "r") as f:
    aws_session_info = json.load(f)

if aws_session_info is None:
    exit(1)

aws_session = boto3.Session(
    aws_access_key_id=aws_session_info["ACCESS_KEY_ID"],
    aws_secret_access_key=aws_session_info["SECRET_ACCESS_KEY"],
    region_name=aws_session_info["REGION_NAME"]
)

userIdTable = aws_session.resource(
    'dynamodb').Table('userIdTable')
userNameTable = aws_session.resource(
    'dynamodb').Table('userNameTable')
photoTable = aws_session.resource(
    'dynamodb').Table('photoTable')


def signUpCheck(username, email, password, repeat_password):
    # コード
    # 0 異常なし
    # 1 再入力パスワードが一致しない
    # 2 同じuserId(メールアドレス)が存在
    # 3 同じUsernameが存在
    # 4 入力パラメタがおかしい　or サーバの不調

    if password != repeat_password:
        return False, 1
    try:
        res = userIdTable.get_item(
            Key={
                'userId': email
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False, 4

    if res.get('Item'):
        return False, 2

    try:
        res = userNameTable.get_item(
            Key={
                'userName': username
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False, 4
    if res.get('Item'):
        return False, 3

    sign_up_date = datetime.now(JST)
    userIdTable.put_item(
        Item={
            "userId": email,
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "userName": username,
            "signUpDate": sign_up_date.strftime('%Y-%m-%d %H:%M:%S'),
            "signUpYear": sign_up_date.strftime('%Y'),
            "signUpMonth": sign_up_date.strftime('%m'),
            "signUpDay": sign_up_date.strftime('%d'),
        }
    )
    try:
       userNameTable.put_item(
            Item={
                "userId": email,
                "password": hashlib.sha256(password.encode()).hexdigest(),
                "userName": username,
                "signUpDate": sign_up_date.strftime('%Y-%m-%d %H:%M:%S'),
                "signUpYear": sign_up_date.strftime('%Y'),
                "signUpMonth": sign_up_date.strftime('%m'),
                "signUpDay": sign_up_date.strftime('%d'),
            }
        )
    except Exception as e:
        print(e)
    else:
        pass
    return True, 0


def login_by_email(email, password):
    # コード
    # 1 パスワードが間違っている．
    # 2 ユーザが存在しない
    try:
        res = userIdTable.get_item(
            Key={
                'userId': email
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        pass

    if res.get('Item'):
        if res.get('Item')['password'] == hashlib.sha256(password.encode()).hexdigest():
            return True, res.get('Item')['userId'], res.get('Item')['userName']
        else:
            return False, 1
    else:
        return False, 2


def login_by_username(username, password):
    # コード
    # 1 パスワードが間違っている．
    # 2 ユーザが存在しない
    try:
        res = userNameTable.get_item(
            Key={
                'userName': username
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        pass

    if res.get('Item'):
        if res.get('Item')['password'] == hashlib.sha256(password.encode()).hexdigest():
            return True, res.get('Item')['userId'], res.get('Item')['userName']
        else:
            return False, 1
    else:
        return False, 2


def queryUserIdTable(user_id):
    # コード
    # 1 ユーザが存在しない
    try:
        res = userIdTable.get_item(
            Key={
                'userId': user_id
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        pass
    if res.get('Item'):
        return True, res.get('Item')['userId'], res.get('Item')['userName']
    else:
        return False, 1


def uploadPhoto(user_id, username):
    photo_id = uuid.uuid4()

    photoTable.put_item(
        Item={
            "photo_id": photo_id,
            "user_id": user_id,
            "username": username,
            "heart": 0,
            "comments": [],
        }
    )


def updatePhoto(photo_id, user_id):
    try:
        res = photoTable.get_item(
            Key={
                'photo_id': photo_id
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        pass