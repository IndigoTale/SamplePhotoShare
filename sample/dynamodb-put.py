import boto3
import json
import uuid
import hashlib
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
username="user0"
userId = "user0@test.com"
password = "password0"
sign_up_date = datetime.now()

with open("../app/aws_session_info.json", "r") as f:
    aws_session_info = json.load(f)

if aws_session_info is None:
    exit(1)

aws_session = boto3.Session(
    aws_access_key_id=aws_session_info["ACCESS_KEY_ID"],
    aws_secret_access_key=aws_session_info["SECRET_ACCESS_KEY"],
    region_name=aws_session_info["REGION_NAME"]
)
dynamodb = aws_session.resource('dynamodb')
table = dynamodb.Table('userIdTable')
response = table.put_item(
    Item={
        "userId": userId,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "userName": username,
        "signUpDate":sign_up_date.strftime('%Y-%m-%d %H:%M:%S'),
        "signUpYear": sign_up_date.strftime('%Y'),
        "signUpMonth": sign_up_date.strftime('%m'),
        "signUpDay": sign_up_date.strftime('%d'),
        "signUpHour": sign_up_date.strftime('%H'),
        "signUpMinute": sign_up_date.strftime('%M'),
        "signUpSecond": sign_up_date.strftime('%S')
    }
)
