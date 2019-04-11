from flask import render_template
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import hashlib,json,os

with open("/app/aws_session_info.json","r") as f:
    aws_session_info= json.load(f)

if aws_session_info is None:
    exit(1)
print(os.getcwd())
print(os.listdir(os.getcwd()))

aws_session = boto3.Session(
    aws_access_key_id=aws_session_info["ACCESS_KEY_ID"],
    aws_secret_access_key=aws_session_info["SECRET_ACCESS_KEY"],
    region_name=aws_session_info["REGION_NAME"]
)
userTable = boto3.resource('dynamodb',region_name='us-east-1').Table('userTable')
postTable = boto3.resource('dynamodb',region_name='us-east-1').Table('postTable')


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
    if res is not None:
        return False, 3

    userTable.put_item(
        Item={
            "userId": email, "password": hashlib.sha256(password.encode()).hexdigest(), "userName": username
        }
    )
    return True, 0
