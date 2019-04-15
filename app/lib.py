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
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg')

# Flask App (Docker Container On EC2) からアクセスするのでセッションが必要
with open("/app/aws_session_info.json", "r") as f:
    aws_session_info = json.load(f)
aws_session = boto3.Session(
    aws_access_key_id=aws_session_info["ACCESS_KEY_ID"],
    aws_secret_access_key=aws_session_info["SECRET_ACCESS_KEY"],
    region_name=aws_session_info["REGION_NAME"]
)
# S3の情報
with open("/app/aws_s3_info.json", "r") as fi:
    aws_s3_info = json.load(fi)

# S3操作用クラス
photoBucket = aws_session.resource('s3').Bucket(aws_s3_info["BUCKET_NAME"])


if aws_session_info and aws_s3_info:
    exit(1)

# DynamoDBのテーブル操作用クラス
userIdTable = aws_session.resource('dynamodb').Table('userIdTable')
userNameTable = aws_session.resource('dynamodb').Table('userNameTable')
photoTable = aws_session.resource('dynamodb').Table('photoTable')
infoTable = aws_session.resource('dynamodb').Table('infoTable')


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


def upload_photo_to_s3(file, filename):

    try:
        photoBucket.upload_fileobj(file, aws_s3_info['PHOTO_FOLDER']+filename)
    except:
        return False
    else:
        return True


def upload_photo_info_to_dynamodb(filename, title, comment,user_id,username):
    try:
        res = infoTable.get_item(
            Key={
                "tableName": "photoTable"
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        pass
    if res.get('Item').get('photoNumber'):
        photo_number = str(int(res.get('Item').get('photoNumber')) + 1)
    else:
        return False
    try:
        infoTable.update_item(
            Key={
                "tableName":"photoTable"
            },
            UpdateExpression="set photoNumber = :p",
            ExpressionAttributeValues={
                ":p":photo_number
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        pass
    try:
        upload_date = datetime.now(JST)
        photoTable.put_item(
            Item={
                "photoCount":photo_number,
                "userId": user_id,
                "userName": username,
                "uploadDate": upload_date.strftime('%Y-%m-%d %H:%M:%S'),
                "uploadYear": upload_date.strftime('%Y'),
                "uploadMonth": upload_date.strftime('%m'),
                "uploadDay": upload_date.strftime('%d'),
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        pass

    return True

    

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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
