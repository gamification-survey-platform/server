
import boto3
from django.conf import settings

def generate_presigned_url(key, expiration=3600, http_method='GET'):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    client_method = {
        'GET': 'get_object',
        'PUT': 'put_object',
        'DELETE': 'delete_object'
    }.get(http_method, 'get_object')

    response = s3_client.generate_presigned_url(
        ClientMethod=client_method,
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': key
        },
        ExpiresIn=expiration,
        HttpMethod=http_method
    )

    return response

def generate_presigned_post(key, expiration=3600):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    response = s3_client.generate_presigned_post(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        ExpiresIn=expiration,
    )

    return response
