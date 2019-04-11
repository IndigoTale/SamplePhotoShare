import boto3
import uuid

BUCKET_NAME = "photoshare-bucket"
s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)


for object in bucket.objects.all():
    print(object.key)
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket=BUCKET_NAME,Key=object.key)


