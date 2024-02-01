from redis import Redis

from mailforce import CONFIG

REDIS: Redis = Redis(host=CONFIG.redis_host,
              port=CONFIG.redis_port,
              username=CONFIG.redis_username,
              password=CONFIG.redis_password,
              db=CONFIG.redis_db)
