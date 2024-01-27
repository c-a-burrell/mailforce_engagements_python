from mailforce import CONFIG
from mailforce.client.aws import CLIENT
ENDPOINT: str = CONFIG.spaces_endpoint


def upload_file(bucket: str, sub_folder: str, filename: str, file_path: str, content: str = None) -> str:
    """
    :param bucket: Bucket to upload file to
    :param sub_folder: Subfolder of prescribed bucket to upload file to.
    :param filename: Name of file written to the external storage.
    :param file_path: Path to file to be read. If the `content` parameter is specified then this will be skipped.
    :param content: Optional content to be written to the external storage. If this is missing then the file
        specified in `filepath` will be read instead.
    :return: Path to S3 file uploaded.
    """
    full_name: str = f'https://{ENDPOINT}/{bucket}/{sub_folder}/{filename}'
    if content:
        temp_file_path: str = f'local.{filename}.tmp'
        with open(temp_file_path, 'w') as f:
            f.write(content)
    else:
        temp_file_path = file_path
    try:
        CLIENT.upload_file(temp_file_path, bucket, f'{sub_folder}/{filename}')
        return f'https://{ENDPOINT}/{full_name}'
    except Exception as e:
        print(f'Error caught when attempting to upload {temp_file_path} to {full_name}: {str(e)}')


def get_file(bucket: str, key: str) -> str:
    """
    Gets the content of a file from remote storage
    :param bucket: Bucket in which file is located.
    :param key: Key under which file is stored.
    :return: String content of file
    """
    full_name: str = f'https://{ENDPOINT}/{bucket}/{key}'
    try:
        response = CLIENT.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except Exception as e:
        print(f'Error caught when attempting to get file from {full_name}: {str(e)}')

