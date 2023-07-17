from typing import Literal, TypedDict

from loguru import logger
from redis import asyncio as aioredis

from main import redis

State = Literal["ON", "OFF"]


class MicrowaveDict(TypedDict):
    power: int
    counter: int
    state: State


CHANNEL_NAME = "microwave_updates"


class Microwave:
    """
    Microwave class

    `power` and `counter` are integers >= 0

    `state` can be "ON" or "OFF" and is derived from current `power` and `counter` (it is not stored in redis)
    """

    async def get_power(self) -> int:
        power = int(await redis.get("microwave_power") or 0)
        assert power >= 0
        return power

    async def get_counter(self) -> int:
        counter = int(await redis.get("microwave_counter") or 0)
        assert counter >= 0
        return counter

    async def get_microwave(self) -> MicrowaveDict:
        """Get all microwave data"""
        async with redis.pipeline(transaction=True) as pipe:
            pipe.get("microwave_power")
            pipe.get("microwave_counter")
            power_result, counter_result = await pipe.execute()

        power: int = int(power_result) if power_result else 0
        assert power >= 0
        counter: int = int(counter_result) if counter_result else 0
        assert counter >= 0

        state: State = "ON" if counter > 0 or power > 0 else "OFF"

        microwave = MicrowaveDict({"power": power, "counter": counter, "state": state})
        return microwave

    async def get_state(self) -> State:
        """State is derived from current power and counter"""
        microwave: MicrowaveDict = await self.get_microwave()
        return microwave["state"]

    async def adjust_power(self, increment=10) -> None:
        """Adjust power by increment (increment can be negative, but value after can't be negative so `incrby` is not suitable)"""
        retries = 10
        while retries:
            try:
                async with redis.pipeline(transaction=True) as pipe:
                    await pipe.watch("microwave_power")
                    current_power = int(await pipe.get("microwave_power") or 0)
                    assert current_power >= 0

                    pipe.multi()

                    new_power: int = current_power + increment
                    if new_power < 0:
                        new_power = 0
                    pipe.set("microwave_power", new_power)
                    results: list = await pipe.execute()
                assert all(results)
                await self.notify_subscribers(
                    f"Power adjusted. Old power: {current_power} New power: {new_power}"
                )
                break
            except aioredis.WatchError:
                retries -= 1
                continue
        else:
            logger.error("Could not adjust power")
            raise Exception("Could not adjust power")

    async def adjust_counter(self, increment=10) -> None:
        """Adjust counter by increment (increment can be negative, but value after can't be negative so `incrby` is not suitable)"""
        retries = 10
        while retries:
            try:
                async with redis.pipeline(transaction=True) as pipe:
                    await pipe.watch("microwave_counter")
                    current_counter = int(await pipe.get("microwave_counter") or 0)
                    assert current_counter >= 0

                    pipe.multi()

                    new_counter: int = current_counter + increment
                    if new_counter < 0:
                        new_counter = 0
                    pipe.set("microwave_counter", new_counter)
                    results: list = await pipe.execute()
                assert all(results)
                await self.notify_subscribers(
                    f"Counter adjusted. Old counter: {current_counter} New counter: {new_counter}"
                )
                break
            except aioredis.WatchError:
                retries -= 1
                continue
        else:
            logger.error("Could not adjust counter")
            raise Exception("Could not adjust counter")

    async def cancel(self) -> None:
        """Cancel microwave, set `power` and `counter` to 0, which will also set state to 'OFF'"""
        async with redis.pipeline(transaction=True) as pipe:
            pipe.set("microwave_power", 0)
            pipe.set("microwave_counter", 0)
            results: list = await pipe.execute()
        assert all(results)
        await self.notify_subscribers("Microwave canceled. Power and Counter set to 0.")

    async def notify_subscribers(self, message: str) -> None:
        """Notify subscribers of changes"""
        pubsub = await redis.publish(CHANNEL_NAME, message)
        logger.info(f"Published message: '{message}' to '{pubsub}' subscribers")
