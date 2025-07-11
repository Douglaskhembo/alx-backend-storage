#!/usr/bin/env python3
"""
This module implements a simple web cache with Redis.
It caches the HTML content of a URL for 10 seconds
and keeps track of how many times each URL is accessed.
"""

import redis
import requests
from typing import Callable
from functools import wraps


# Initialize a Redis client
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL has been accessed.
    Increments Redis key `count:{url}` on each call.
    """

    @wraps(method)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)

    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    Returns the content of a URL, caching it in Redis for 10 seconds.
    If the URL is already cached, returns it from Redis.
    """
    cached = r.get(url)
    if cached:
        return cached.decode('utf-8')

    # Fetch the page and cache it
    response = requests.get(url)
    content = response.text
    r.setex(url, 10, content)  # Set with 10s expiry
    return content
