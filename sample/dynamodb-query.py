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
response = table.get_item(
    Key={
        "userId": userId,
        "signUpDate":"dsdaw"
    }
)