import redis

from app.config.settings import get_settings

settings = get_settings()

redis_client = redis.Redis(decode_responses=True).from_url(settings.cache_connection_string)


def get_cache():
    """Get the Redis client."""
    return redis_client
