import boto3
import uuid
import os

input_bucket = os.getenv('DOCUMENT_BUCKET_NAME')
output_bucket = os.getenv('OUTPUT_BUCKET_NAME')
comprehend_role_arn = os.getenv("COMPREHEND_ROLE_ARN")
aws_account_id = os.getenv("AWS_ACCOUNT_ID")

def handler(event, lambda_context):
    client = boto3.client('comprehend')

    job_name = f"entity-job-{uuid.uuid4()}"
    input_s3_uri = f's3://{input_bucket}/'
    output_s3_uri = f's3://{output_bucket}/'
    response = client.start_entities_detection_job(
        InputDataConfig={
            'S3Uri': input_s3_uri,
            'InputFormat': 'ONE_DOC_PER_FILE',
        },
        OutputDataConfig={
            'S3Uri': output_s3_uri
        },
        DataAccessRoleArn=comprehend_role_arn,
        LanguageCode='en',
        JobName=job_name
    )

    print("Started job:", response['JobId'])
