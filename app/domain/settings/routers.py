from fastapi import FastAPI
from app.presentation.routers import agent_routers


def setup_routers(app: FastAPI) -> None:
    """
    FastAPI Routers Set-Up
    In productive environments we would have more services...
    Such as a (MCP-Based) Tool Management Service, a Feedback and Eval Service, Memory Management Service, etc...
    """
    app.include_router(agent_routers.router)
    
