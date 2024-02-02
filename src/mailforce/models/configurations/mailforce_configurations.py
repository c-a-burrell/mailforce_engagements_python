import os


class MailforceConfigurations:
    """ Holds Mailforce Configurations as stored as environment variables """

    def __init__(self):
        """ Inits using values stored as environment variables """
        self.spaces_region: str = os.environ.get('SPACES_REGION', 'sfo3')
        self.spaces_endpoint: str = os.environ.get('SPACES_ENDPOINT', 'sfo3.digitaloceanspaces.com')
        self.spaces_key: str = os.environ['SPACES_KEY']
        self.spaces_secret: str = os.environ['SPACES_SECRET']
        self.redis_password: str = os.environ['REDIS_PASSWORD']
        self.redis_username: str = os.environ['REDIS_USERNAME']
        self.redis_host: str = os.environ['REDIS_HOST']
        self.redis_port: str = os.environ['REDIS_PORT']
        self.redis_db: int = int(os.environ['REDIS_DB'])
        self.sf_domain: str = os.environ['SF_DOMAIN']
        self.sf_refresh_token: str = os.environ['SF_REFRESH_TOKEN']
        self.sf_client_id: str = os.environ['SF_CLIENT_ID']
        self.elastic_password = os.environ['ELASTIC_PASSWORD']
        self.elastic_cloud_id = os.environ['ELASTIC_CLOUD_ID']
