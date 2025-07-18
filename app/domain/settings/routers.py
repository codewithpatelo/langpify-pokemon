from fastapi import FastAPI
from app.presentation.routers import agent_routers


def setup_routers(app: FastAPI) -> None:
    """
    Configura la aplicación FastAPI con routers y middleware.
    """
    app.include_router(agent_routers.router)

