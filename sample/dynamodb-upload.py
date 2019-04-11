import boto3
import json
import uuid
import hashlib
from boto3.dynamodb.conditions import Key, Attr

userId="x@d.com"
password="password"

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('userTable')

response = table.put_item(
    Item={
        "userId":userId,
        "password":hashlib.sha256(password).hexdigest()
    }
)

