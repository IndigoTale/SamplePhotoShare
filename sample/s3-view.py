import boto3
s3 = boto3.resource('s3')
BUCKET_NAME = "photoshare-bucket"
bucket = s3.Bucket(BUCKET_NAME)

for object in bucket.objects.all():
    print(object.key)
