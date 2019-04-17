# AWS SDK
import boto3
from botocore.exceptions import ClientError
# My Module
from my_utils import*
# Others
import json

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
# S3の情報
BUCKET_NAME = 'photoshare-bucket'
PHOTO_FOLDER = "images/photo/"
PROFILE_ICON_FOLDER = "images/profile-icon/"
# S3操作用クラス
photoBucket = aws_session.resource('s3').Bucket(BUCKET_NAME)

def uploadPhoto(file,filename):
    try:
        photoBucket.upload_fileobj(file, PHOTO_FOLDER+filename, ExtraArgs={
                                   "ContentType": f"image/{filename.split('.')[1]}", 'ACL': 'public-read'})
    except boto3.exceptions.S3UploadFailedError:
        return {"status":400}
    else:
        return {"status":201}

def deletePhoto(filename):
    try:
        photoBucket.delete_objects(
            Delete={
                "Objects":[
                    {
                        "Key":PHOTO_FOLDER+filename
                    }
                ]
            }
        )
    except boto3.exceptions.S3UploadFailedError:
        return {"status":400}
    else:
        return {"status":201}

def uploadIcon(file,filename):
    try:
        photoBucket.upload_fileobj(file, PROFILE_ICON_FOLDER+filename, ExtraArgs={
                                   "ContentType": f"image/{filename.split('.')[1]}", 'ACL': 'public-read'})
    except boto3.exceptions.S3UploadFailedError:
        return {"status":400}
    else:
        return {"status":201}
