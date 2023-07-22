import boto3


def create_s3_client(aws_access_key, aws_secret_key, aws_session_token=None):
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        aws_session_token=aws_session_token
    )


def upload_to_s3(s3_client, path, file_name, s3_bucket_name):
    extra_args = None
    if file_name.endswith(".gz"):
        extra_args = {
            'ContentType': 'application/json',
            'ContentEncoding': 'gzip',
            'ACL': 'public-read'
        }
    s3_client.upload_file(f"{path}{file_name}", s3_bucket_name, file_name, ExtraArgs=extra_args)


def upload_files_to_s3(s3_client, s3_bucket_name, file_path_to_file_name):
    for file_path in file_path_to_file_name:
        upload_to_s3(
            s3_client=s3_client,
            path=file_path,
            file_name=file_path_to_file_name[file_path],
            s3_bucket_name=s3_bucket_name
        )
