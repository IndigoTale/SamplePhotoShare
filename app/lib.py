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

# S3の情報
BUCKET_NAME = 'photoshare-bucket'
PHOTO_FOLDER = "images/photo/"
PROFILE_ICON_FOLDER = "images/profile-icon/"
# S3操作用クラス
photoBucket = aws_session.resource('s3').Bucket(BUCKET_NAME)





# 画像ファイルの拡張子を確認する関数
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ユーザを新規登録する関数
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
            "user_id": email,
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "username": username,
            "created_at": sign_up_date.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": "undefined",
            "profile_photo_path": PROFILE_ICON_FOLDER+"undefined.jpg",
            "profile_text": ""
        }
    )

    userNameTable.put_item(
        Item={
            "user_id": email,
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "username": username,
            "created_at": sign_up_date.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": "undefined",
            "profile_photo_path": PROFILE_ICON_FOLDER+"undefined.jpg",
            "profile_text": ""
        }
    )


def putUserIdTable(user_id, username, password):
    # デフォルト
    item = {
        "user_id": email,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "username": username,
        "created_at": sign_up_date.strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at": "undefined",
        "profile_photo_path": PROFILE_ICON_FOLDER+"undefined.jpg",
        "profile_text": ""
    }
    # オプション
    if kwargs.keys():
        for key in kwargs.keys():
            if key in item.keys():
                item[key] = kwargs[key]
    # テーブルへの追加
    try:
        userIdTable.put_item(Item=item)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        pass
def putUserNameTable(user_id, username, password,**kwargs):
    item = {
        "user_id": email,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "username": username,
        "created_at": sign_up_date.strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at": "undefined",
        "profile_photo_path": PROFILE_ICON_FOLDER+"undefined.jpg",
        "profile_text": ""
    }
    # オプション
    if kwargs.keys():
        for key in kwargs.keys():
            if key in item.keys():
                item[key] = kwargs[key]
    # テーブルへの追加
    try:
        userIdTable.put_item(Item=item)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        pass      

# Email と Password でログイン
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


# Username と Password でログイン
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


def getUserIdTable(user_id):
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
        return res.get('Item')
    else:
        return None




def getPhotoTable(photo_id):
    try:
        res = photoTable.get_item(
            Key={
                'photoId': photo_id
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        pass
    if res.get('Item'):
        return res.get('Item')
    else:
        return None





def putPhotoTimeSeriesTable(photo_id, **kwargs):
    # デフォルト
    item = {
        "dummy": "dummy",  # ダミー/主キー
        # 投稿日時/ソートキー
        "ordered_at": datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S'),
        "photo_id": photo_id
    }
    # オプション
    if kwargs.keys():
        for key in kwargs.keys():
            if key in item.keys():
                item[key] = kwargs[key]
    # テーブルへの追加
    try:
        photoTimeSeriesTable.put_item(Item=item)
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        return True


def getCommentTable(comment_id):
    try:
        res = commentTable.get_item(
            Key={
                'commentId': comment_id
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        pass
    if res.get('Item'):
        return res.get('Item')
    else:
        return None





# S3に写真を保存する


def upload_photo_to_s3(file, filename):

    try:
        photoBucket.upload_fileobj(file, PHOTO_FOLDER+filename, ExtraArgs={
                                   "ContentType": f"image/{filename.split('.')[1]}", 'ACL': 'public-read'})
    except boto3.exceptions.S3UploadFailedError:
        return {"status":400}
    else:
        return {"status":201}


# DynamoDBに写真に関するレコードを保存する


def upload_photo_info_to_dynamodb(photo_id, filename, title, self_comment, user_id, username):
    # 写真の新規投稿を追加する．
    putPhotoTable(photo_id,)
    # ユーザ自身の投稿時系列データを更新
    try:
        userPhotoTimeSeriesTable.update_item(
            Key={
                "userId": "photoTable"
            },
            UpdateExpression="set photoNumber = :p",
            ExpressionAttributeValues={
                ":p": ""
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        pass

    return True


def get_photos_from_dynamodb(page=1, **kwargs):
    # 写真投稿IDを取得
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
    # 写真投稿IDに基づいて，最新の
    photos = []
    while photo_number < 1:
        try:
            res = photoTable.get_item(
                Key={
                    "photoNumber": photo_number
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False
        else:
            pass
        if res.get('Item'):
            photos
