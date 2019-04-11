import boto3
import json
from boto3.dynamodb.conditions import Key, Attr


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('userTable')
res = table.query(
        IndexName='userId',
        KeyConditionExpression=Key('userId').eq("uid-00000001")
    )
for row in res['Items']:
    print(row)