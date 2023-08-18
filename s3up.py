import boto3

def up_load_s3(file_path):
    s3 = boto3.resource('s3')
    bucket_name = 'aigc-bj-team4'
    s3.Bucket(bucket_name).upload_file(file_path, file_path)
    # Generate a pre-signed URL for the objecct "welcome.txt", valid for 1 hour
    url = s3.meta.client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': file_path
        },
        ExpiresIn=3600
    )
    # Print out the URL
    print(f"upload file {file_path} to s3, URL: {url}")
    return url