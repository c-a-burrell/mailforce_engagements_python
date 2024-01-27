from boto3 import client
from botocore.client import BaseClient

from mailforce import CONFIG

CLIENT: BaseClient = client('s3',
                            region_name=CONFIG.spaces_region,
                            enddpoint_url=f'https://{CONFIG.spaces_endpoint}',
                            aws_access_key=CONFIG.spaces_key,
                            aws_secret_access_key=CONFIG.spaces_secret)
