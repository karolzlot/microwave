import asyncio
import os

import jwt
from fastapi import APIRouter, Header, HTTPException, WebSocket
from loguru import logger

from microwave import CHANNEL_NAME, Microwave

router = APIRouter()
microwave = Microwave()

SECRET_KEY = os.environ["SECRET_KEY"]
assert len(SECRET_KEY) > 10


def validate_jwt(x_token: str = Header(None)):
    if x_token is None:
        raise HTTPException(status_code=403, detail="Unauthorized")
    try:
        jwt.decode(x_token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token or expired")


async def listen_for_incoming_actions(websocket: WebSocket):
    while True:
        data = await websocket.receive_json()

        logger.debug(f"Received action: {data}")

        if data["action"] == "power+10":
            await microwave.adjust_power(10)
        elif data["action"] == "power-10":
            await microwave.adjust_power(-10)
        elif data["action"] == "counter+10":
            await microwave.adjust_counter(10)
        elif data["action"] == "counter-10":
            await microwave.adjust_counter(-10)
        elif data["action"] == "cancel":
            if await microwave.get_state() == "ON":
                validate_jwt(data["token"])
                await microwave.cancel()
        else:
            logger.warning(f"Unknown action: {data['action']}")


async def listen_for_redis_changes(websocket: WebSocket):
    from redis_connection import redis

    pubsub = redis.pubsub()
    await pubsub.subscribe(CHANNEL_NAME)

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message is None:
            continue
        logger.info(f"Received message: {message}")

        microwave_data = await microwave.get_microwave_data()

        await websocket.send_text(
            f"""<div id="power">{ microwave_data["power"] }</div>
<div id="counter">{ microwave_data["counter"] }</div>
<div id="status">{ microwave_data["state"] }</div>"""
        )  # TODO: make counter more human readable (e.g. 1:30 instead of 90)
        logger.info(f"State broadcast: {microwave_data}")


@router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    listener_task = asyncio.create_task(listen_for_incoming_actions(websocket))
    broadcaster_task = asyncio.create_task(listen_for_redis_changes(websocket))
    await asyncio.gather(listener_task, broadcaster_task)