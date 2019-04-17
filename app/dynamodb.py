# AWS SDK
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
# Others
import json
from datetime import datetime,timedelta,timezone
# MyFunctions
from my_utils import get_cuurent_timestamp, hashed_password


# Session  Flask <-> AWS
with open("/app/aws_session_info.json", "r") as f:
    aws_session_info = json.load(f)
if aws_session_info is None:
    exit(1)
aws_session = boto3.Session(
    aws_access_key_id=aws_session_info["ACCESS_KEY_ID"],
    aws_secret_access_key=aws_session_info["SECRET_ACCESS_KEY"],
    region_name=aws_session_info["REGION_NAME"]
)
# TimeZone
JST = timezone(timedelta(hours=+9), 'JST')

# DynamoDB Tables
class userIdTable:
    def __init__(self):
        self.userIdTable = aws_session.resource(
            'dynamodb').Table('userIdTable')
    def put(self,user_id, created_at, username, hashed_password):
        item = {
            "user_id":user_id, # Hash Key
            "created_at": created_at,
            "username":username,
            "password":hashed_password,
            "profile_icon":"undefined",
            "profile_text":"undefined"
        }
        try:
            self.userIdTable.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            return {"status":201}

    def get(self,user_id):
        key = {"user_id":user_id}
        try:
            record = self.userIdTable.get_item(
                Key=key
            )
        except  ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            if record.get("Item"):
                return {"status":200,"record":record}
            else:
                return {"status":404}

    def delete(self,user_id):
        key = {"user_id":user_id}
        try:
            record = self.userIdTable.delete_item(
                Key=key
            )
        except  ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            if record.get("Attributes"):
                return {"status":200,"record":record}
            else:
                return {"status":404} 

    def sign_up(self,user_id,username,password,repeat_password):
        if password != repeat_password:
            return {"status":401}
        res = self.get(user_id)
        if res.get('status') == 400:
            return {"status":400}
        elif res.get('status') == 200:
            return {"status":409}
        elif res.get('status') == 404:
            created_at = get_cuurent_timestamp()

            res_in = self.put(user_id,created_at,username,hashed_password(user_id,password,created_at))
            if res_in.get('status') == 201:
                return {"status":201}
            else:
                return {"status":400}
        else:
            return {"status":400}

    def login(self,user_id,password):
        print(user_id,password)
        res = self.get(user_id)
        print(res)

        if res.get('status') == 400:
            return {"status":400}

        elif res.get('status') == 200:
            created_at = res["record"]["Item"]["created_at"]
            stored_password = res["record"]["Item"]["password"]

            if hashed_password(user_id,password,created_at) ==  stored_password:
                return {"status":200}
            else:
                return {"status":401}

        elif res.get('status') == 404:
            return {"status":404}    
        else:
            return {"status":400}


class userNameTable:
    def __init__(self):
        self.userNameTable = aws_session.resource(
            'dynamodb').Table('userNameTable')
    def put(self,username,user_id):
        item = {
            "username":username, # Hash Key
            "user_id":user_id 
        }
        try:
            self.userNameTable.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            return {"status":201}   
    def get(self,username):
        key = {"username":username}
        try:
            record = self.userNameTable.get_item(
                Key=key
            )
        except  ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            if record.get("Item"):
                return {"status":200,"record":record.get("Item")}
            else:
                return {"status":404}
    def delete(self,username):
        key = {"username":username}
        try:
            record = self.userNameTable.delete_item(
                Key=key
            )
        except  ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            if record.get("Attributes"):
                return {"status":200,"record":record}
            else:
                return {"status":404} 

class userPhotoTimeSeriesTable:
    def __init__(self):
        self.userPhotoTimeSeriesTable = aws_session.resource(
            'dynamodb').Table('userPhotoTimeSeriesTable')
    def put(self,user_id, created_at, photo_id):
        item = {
            "user_id":user_id, # Hash Key
            "created_at": created_at, # Sort Key
            "photo_id":photo_id,
        }
        try:
            self.userPhotoTimeSeriesTable.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            return {"status":200}   
    def query(self,KeyConditionExpression,**kwargs):
        if kwargs.get('Limit') and kwargs.get('FilterExpression'):
            try:
                records = self.userPhotoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    FilterExpression=kwargs.get('FilterExpression'),
                    Limit = kwargs.get('Limit')
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        
        elif kwargs.get('FilterExpression'):
            try:
                records = self.userPhotoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    FilterExpression=kwargs.get('FilterExpression'),
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        elif kwargs.get('Limit'):
            try:
                records = self.userPhotoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    Limit = kwargs.get('Limit')
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        else:
            try:
                records = self.userPhotoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        
        if records.get("Item"):
            return {"status":200,"records":records}
        else:
            return {"status":404,"records":records}
        
        
class userActionTable:
    def __init__(self):
        self.userActionTable = aws_session.resource(
            'dynamodb').Table('userActionTable')
    def put(self,user_id, created_at, photo_id,comment:bool,heart:bool):
        item = {
            "user_id":user_id, # Hash Key
            "created_at": created_at, # Sort Key
            "photo_id":photo_id,
            "comment" : comment,
            "heart" : heart   
        }
        try:
            self.userActionTable.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            return {"status":200}

class photoTable:
    def __init__(self):
        self.photoTable = aws_session.resource('dynamodb').Table('photoTable')

    def put(self, photo_id, created_at, user_id, username, title, self_comment, filename,**kwargs):
        # Default
        item = {
            "photo_id": photo_id, # Hash
            "created_at": created_at, 
            "user_id": user_id,  
            "username": username, 
            "title": title,
            "self-comment": self_comment, 
            "filename": filename,  # S3 Path 
            "updated_at": "undefined",
            "hearts": [],  # Array of user_id
            "comments": []  # Array of comment_id
        }   
        if kwargs.keys():
            for key in kwargs.keys():
                if key in item.keys():
                    item[key] = kwargs[key]
        try:
            self.photoTable.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            return {"status":201}

    def get(self,photo_id):
        key = {"photo_id":photo_id}
        try:
            record = self.photoTable.get_item(
                Key=key
            )
        except  ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            if record.get("Item"):
                return {"status":200,"record":record}
            else:
                return {"status":404} 

    def delete(self,photo_id):
        key = {"photo_id":photo_id}
        try:
            record = self.photoTable.delete_item(
                Key=key
            )
        except  ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            if record.get("ResponseMetadata").get("HTTPStatusCode")==200:
                return {"status":200}
            else:
                return {"status":404} 

class photoTimeSeriesTable:
    def __init__(self):
        self.photoTimeSeriesTable = aws_session.resource(
            'dynamodb').Table('photoTimeSeriesTable')
    def put(self,created_at,photo_id):
    # Default
        item = {
            "dummy":"dummy", # Hash Key
            "created_at": created_at, # Sort Key
            "photo_id": photo_id,
        }   
        try:
            self.photoTimeSeriesTable.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            return {"status":201}
        
    def delete(self,created_at):
        try:
            record = self.photoTimeSeriesTable.delete_item(
                Key={'dummy':'dummy','created_at':created_at}
            )
        except  ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:

            if record.get("Attributes"):
                return {"status":200,"record":record}
            else:
                return {"status":404} 
    
    def query(self,KeyConditionExpression,**kwargs):
        if kwargs.get('Limit') and kwargs.get('FilterExpression') and kwargs.get("ScanIndexForward"):
            try:
                records = self.photoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    FilterExpression=kwargs.get('FilterExpression'),
                    Limit = kwargs.get('Limit'),
                    ScanIndexForward= kwargs.get("ScanIndexForward")
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        
        elif kwargs.get('Limit') and kwargs.get('FilterExpression') :
            try:
                records = self.photoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    FilterExpression=kwargs.get('FilterExpression'),
                    Limit = kwargs.get('Limit'),
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        elif kwargs.get('Limit') and kwargs.get("ScanIndexForward"):
            try:
                records = self.photoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    Limit = kwargs.get('Limit'),
                    ScanIndexForward= kwargs.get("ScanIndexForward")
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        elif kwargs.get('FilterExpression') and kwargs.get("ScanIndexForward"):
            try:
                records = self.photoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    FilterExpression=kwargs.get('FilterExpression'),
                    ScanIndexForward= kwargs.get("ScanIndexForward")
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass

        elif kwargs.get('Limit'):
            try:
                records = self.photoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    Limit = kwargs.get('Limit')
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        elif kwargs.get('FilterExpression'):
            try:
                records = self.photoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    FilterExpression=kwargs.get('FilterExpression'),
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        elif kwargs.get("ScanIndexForward"):
            try:
                records = self.photoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression,
                    ScanIndexForward= kwargs.get("ScanIndexForward")
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        else:
            try:
                records = self.photoTimeSeriesTable.query(
                    KeyConditionExpression = KeyConditionExpression
                )
            except  ClientError as e:
                print(e.response['Error']['Message'])
                return {"status":400}
            else:
                pass
        
        if records.get("ItemsCondi"):
            return {"status":200,"records":records}
        else:
            return {"status":404,"records":records}    
    

class commentTable:
    def __init__(self):
        self.commentTable = aws_session.resource(
            'dynamodb').Table('commentTable')
    def put(self, comment_id, created_at):
        # Default
        item = {
            "comment_id":comment_id, # Hash Key
            "created_at": created_at
        }
        try:
            self.commentTable.put_item(Item=item)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {"status":400}
        else:
            return {"status":200}