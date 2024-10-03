import os
import boto3
from variables import *

aws_access_key_id = AWS_ACCESS_KEY_ID
aws_secret_access_key = AWS_SECRET_ACCESS_KEY


def upload_transcript(transcript, id):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    bucket_name = 'sukoontest'

    filename = f"{id}.txt"

    with open(filename, 'w') as file:
        file.write(transcript)

    with open(filename, 'rb') as data:
        s3.upload_fileobj(data, bucket_name, filename)

    os.remove(filename)

    url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"

    return url
