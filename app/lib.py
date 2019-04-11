from flask import render_template
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import hashlib
userTable = boto3.resource('dynamodb').Table('userTable')
postTable = boto3.resource('dynamodb').Table('postTable')


def signUpCheck(username, email, password, repeat_password):
    # コード
    # 0 異常なし
    # 1 再入力パスワードが一致しない
    # 2 同じuserId(メールアドレス)が存在
    # 3 同じUsernameが存在
    # 4 入力パラメタがおかしい　or サーバの不調

    if password != repeat_password:
        return False, 1
    res = None
    try:
        res = userTable.get_item(
            Key={
                'userId': email
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False, 4

    if res["Item"] is not None:
        return False, 2
    try:
        res = userTable.get_item(
            Key={
                'userName': username
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False, 4
    if res["Item"] is not None:
        return False, 3

    userTable.put_item(
        Item={
            "userId": email, "password": hashlib.sha256(password.encode()).hexdigest(), "userName": username
        }
    )
    return True, 0
