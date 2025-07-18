from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os


def setup_static(app: FastAPI):
    static_directory = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "presentation", "static"
    )
    app.mount("/static", StaticFiles(directory=static_directory), name="static")
