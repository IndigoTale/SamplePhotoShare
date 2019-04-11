import boto3
import uuid

BUCKET_NAME = "photoshare-bucket"
s3 = boto3.resource('s3')

image_id = uuid.uuid4().hex


s3.Bucket(BUCKET_NAME).upload_file('/home/ubuntu/kame.png','images/'+image_id+'.png')

