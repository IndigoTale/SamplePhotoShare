import boto3
s3 = boto3.resource('s3')
BUCKET_NAME = "photoshare-bucket"
bucket = s3.Bucket(BUCKET_NAME)
i=0

for object in bucket.objects.all():
    print(object.key)
    s3.meta.client.download_file(BUCKET_NAME, object.key, './'+('%06d' % i) + '.png')
    i +=1