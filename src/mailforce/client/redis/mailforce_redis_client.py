from mailforce import CONFIG
from redis import Redis


class MailforceRedisClient:
    """ Wrapper around the third party Redis Client """
    def __init__(self):
        self._client = Redis(host=CONFIG.redis_host,
                             port=CONFIG.redis_port,
                             username=CONFIG.redis_username,
                             password=CONFIG.redis_password,
                             db=CONFIG.redis_db)
