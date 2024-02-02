import os
"""
The following are the keys required for local execution.
Do **NOT** check in this file with secret values configured!!!
"""
setup_configs: dict[str, str] = {'SPACES_REGION': 'sfo',
                                 'SPACES_ENDPOINT': 'sfo3.digitaloceanspaces.com',
                                 'SPACES_KEY': '',
                                 'SPACES_SECRET': '',
                                 'REDIS_PASSWORD': '',
                                 'REDIS_USERNAME': '',
                                 'REDIS_HOST': '',
                                 'REDIS_PORT': '',
                                 'REDIS_DB': '',
                                 'SF_DOMAIN': '',
                                 'SF_REFRESH_TOKEN': '',
                                 'SF_CLIENT_ID': '',
                                 'ELASTIC_PASSWORD': '',
                                 'ELASTIC_CLOUD_ID': ''}


def setup():
    print('Setting the following keys:')
    for key, value in setup_configs.items():
        os.environ[key] = value
        print(f'{key}={os.environ[key]}')
