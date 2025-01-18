from app import templates
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .router import homepage, root, laps, telemetry, download

app = FastAPI()
app.include_router(homepage.router)
app.include_router(root.router)

app.include_router(download.router)
app.include_router(laps.router)
app.include_router(telemetry.router)

app.mount("/static", StaticFiles(directory="../static"), name="static")