from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from routers import router

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")


app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    from microwave import Microwave

    microwave = Microwave()
    microwave_data = await microwave.get_microwave_data()

    return templates.TemplateResponse(
        "index.html", {"request": request, "microwave_data": microwave_data}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
