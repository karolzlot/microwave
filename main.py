from fastapi import FastAPI

# from routers import router
from redis import asyncio as aioredis

app = FastAPI()

# app.include_router(router)


@app.on_event("startup")
async def startup_event() -> None:
    global redis
    redis = await aioredis.from_url("redis://localhost")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
