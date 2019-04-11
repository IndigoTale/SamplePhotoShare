import boto3
import json
import uuid
import hashlib
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

userId="x@d.com"
password="password"

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('userTable')

try:
    response = table.get_item(
        Key={
            'userId': userId,
        }
    )
except ClientError as e:
    print(e.response['Error']['Message'])
else:
    item = response['Item']
    print(item)