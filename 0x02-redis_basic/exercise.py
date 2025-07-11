#!/usr/bin/env python3
"""
A module that provides a Cache class to interact with Redis,
with advanced features such as storing values, counting calls,
recording call history, and replaying call data.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a method is called.
    Stores count in Redis under key of method’s qualified name.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs
    for a particular method in Redis.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        return output
    return wrapper


def replay(method: Callable):
    """
    Display the history of calls for a particular method.
    Shows inputs and outputs in call order.
    """
    r = method.__self__._redis
    name = method.__qualname__
    inputs = r.lrange(f"{name}:inputs", 0, -1)
    outputs = r.lrange(f"{name}:outputs", 0, -1)
    count = r.get(name).decode("utf-8") if r.get(name) else 0
    print(f"{name} was called {count} times:")
    for i, o in zip(inputs, outputs):
        print(f"{name}(*{i.decode('utf-8')}) -> {o.decode('utf-8')}")


class Cache:
    """
    Cache class for storing and retrieving data using Redis backend.
    Includes decorators for counting calls and storing call history.
    """

    def __init__(self):
        """
        Initialize Redis connection and flush database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated UUID key.
        Returns the generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis by key.
        Optionally applies a conversion function if provided.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        return fn(value) if fn else value

    def get_str(self, key: str) -> str:
        """
        Retrieve data from Redis and decode as UTF-8 string.
        """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve data from Redis and convert to integer.
        """
        return self.get(key, fn=int)
