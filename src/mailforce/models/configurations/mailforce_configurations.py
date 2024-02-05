import json
import os


class MailforceConfigurations:
    """ Holds Mailforce Configurations as stored as environment variables """

    def __init__(self):
        """
        This facility will look for a file at '../resources/local_setup.json' first in order to get the settings.
        If it does not find that file, or if the JSON mapping is empty, then it will default to using environment
        variables. Note that *all* of the keys specified in the README must have values assigned in order for this
        function to work.
        """
        try:
            with open('../resources/local_setup.json', 'r') as f:
                content = f.read()
                json_mapping = json.loads(content)
                setup_configs = json_mapping if len(json_mapping) > 0 else os.environ

        except Exception as e:
            print(f'Could not load mappings from file: {str(e)}')
            setup_configs = os.environ

        def safe_get(key: str, default: str = None):
            value = setup_configs.get(key, default)
            return value if len(value)> 0 else default

        """ Inits using values stored as environment variables """
        self.spaces_region: str = safe_get('SPACES_REGION', 'sfo3')
        self.spaces_endpoint: str = safe_get('SPACES_ENDPOINT', 'sfo3.digitaloceanspaces.com')
        self.spaces_key: str = safe_get('SPACES_KEY', )
        self.spaces_secret: str = safe_get('SPACES_SECRET')
        self.redis_password: str = safe_get('REDIS_PASSWORD')
        self.redis_username: str = safe_get('REDIS_USERNAME')
        self.redis_host: str = safe_get('REDIS_HOST')
        self.redis_port: str = safe_get('REDIS_PORT')
        self.redis_db: int = int(safe_get('REDIS_DB', '42'))
        self.sf_domain: str = safe_get('SF_DOMAIN')
        self.sf_refresh_token: str = safe_get('SF_REFRESH_TOKEN')
        self.sf_client_id: str = safe_get('SF_CLIENT_ID')
        self.elastic_password: str = safe_get('ELASTIC_PASSWORD')
        self.elastic_cloud_id: str = safe_get('ELASTIC_CLOUD_ID')
