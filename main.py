from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


from routers import router

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
