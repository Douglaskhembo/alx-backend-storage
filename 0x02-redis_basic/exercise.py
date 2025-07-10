import redis
import uuid
from typing import Union


class Cache:
    """Cache class for storing and retrieving data using Redis."""

    def __init__(self):
        """Initialize the Cache instance and flush the Redis database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Generate a random key and store the input data in Redis using the key.

        Args:
            data (Union[str, bytes, int, float]): Data to be stored in Redis.

        Returns:
            str: The randomly generated key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
