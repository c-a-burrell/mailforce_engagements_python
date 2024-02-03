import os


class MailforceConfigurations:
    """ Holds Mailforce Configurations as stored as environment variables """

    def __init__(self):
        def safe_get(key:str, default:str = None):
            return os.environ.get(key, default)
        """ Inits using values stored as environment variables """
        self.spaces_region: str = safe_get('SPACES_REGION', 'sfo3')
        self.spaces_endpoint: str = safe_get('SPACES_ENDPOINT', 'sfo3.digitaloceanspaces.com')
        self.spaces_key: str = safe_get('SPACES_KEY', )
        self.spaces_secret: str = safe_get('SPACES_SECRET')
        self.redis_password: str = safe_get('REDIS_PASSWORD')
        self.redis_username: str = safe_get('REDIS_USERNAME')
        self.redis_host: str = safe_get('REDIS_HOST')
        self.redis_port: str = safe_get('REDIS_PORT')
        self.redis_db: int = int(safe_get('REDIS_DB','42'))
        self.sf_domain: str = safe_get('SF_DOMAIN')
        self.sf_refresh_token: str = safe_get('SF_REFRESH_TOKEN')
        self.sf_client_id: str = safe_get('SF_CLIENT_ID')
        self.elastic_password: str = safe_get('ELASTIC_PASSWORD')
        self.elastic_cloud_id: str = safe_get('ELASTIC_CLOUD_ID')
