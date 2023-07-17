import asyncio

from redis import asyncio as aioredis


def connect_to_redis():
    global redis
    redis = aioredis.from_url("redis://localhost")
    return redis


redis = connect_to_redis()
