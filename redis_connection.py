import asyncio

from redis import asyncio as aioredis


async def connect_to_redis():
    global redis
    redis = await aioredis.from_url("redis://localhost")
    return redis


redis = asyncio.run(connect_to_redis())
