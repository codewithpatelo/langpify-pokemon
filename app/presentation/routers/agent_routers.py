from fastapi import APIRouter, Depends, status
from fastapi.responses import HTMLResponse
from fastapi import Request
import os

from app.presentation.routers.endpoints import AGENT_PREFIX, AGENT_TEMPLATES
from app.infrastructure.container.container import Container
from dependency_injector.wiring import inject, Provide
from app.application.services.agent_management_service import AgentManagementService
from typing import Annotated
from fastapi import HTTPException
from app.domain.entities.routers.agents.routers import (
    ListAgentTemplatesResponse,
    CreateAgentRequest,
    CreateAgentResponse,
    AgentModel,
    InitEnvironmentResponse,
    ListAgentsResponse,
)
from fastapi import Query

router = APIRouter(prefix=AGENT_PREFIX, tags=["agents"])


@router.get("/battle_minimal", response_class=HTMLResponse)
async def serve_battle_minimal(request: Request):
    """
    Sirve la interfaz minimalista para probar el endpoint /agents/system/battle.
    IMPORTANTE: Antes de probar la batalla, asegúrate de inicializar el environment usando el endpoint POST /agents/environment.
    """
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "presentation/static")
    file_path = os.path.join(static_dir, "battle_minimal.html")
    if not os.path.exists(file_path):
        return HTMLResponse("<h2>Archivo battle_minimal.html no encontrado.</h2>", status_code=404)
    with open(file_path, encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


"""
List all available agent templates.
Templates allow users to create agents with predefined roles and configurations.
Inspired in ACP Manifests
Reference: https://agentcommunicationprotocol.dev/core-concepts/agent-manifest
"""


# List all available agent templates -> PokeExpert, Research, Supervisor, Visualizer, Evaluator, Strategy, Intelligence
@router.get(
    AGENT_TEMPLATES,
    status_code=status.HTTP_200_OK,
    response_model=ListAgentTemplatesResponse,
)
@inject
async def list_templates(
    agent_management_service: Annotated[
        AgentManagementService, Depends(Provide[Container.agent_management_service])
    ],
):
    try:
        templates = await agent_management_service.list_all_templates()
        return ListAgentTemplatesResponse(templates=templates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
Create an agent instance from a YAML template file.
"""


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=CreateAgentResponse
)
@inject
async def create(
    request: CreateAgentRequest,
    agent_management_service: Annotated[
        AgentManagementService, Depends(Provide[Container.agent_management_service])
    ],
):
    try:
        agent = await agent_management_service.create_agent_from_template(
            aid_prefix=request.aid_prefix
        )
        agent_model = AgentModel(
            aid=agent.aid,
            role_name=agent.role["name"] if agent.role else "",
            status=agent.status.value,
        )
        return CreateAgentResponse(agent=agent_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
Creates and activates all needed agents for the application
"""


@router.post("/environment", status_code=status.HTTP_201_CREATED)
@inject
async def init(
    agent_management_service: Annotated[
        AgentManagementService, Depends(Provide[Container.agent_management_service])
    ],
):
    try:
        agents = await agent_management_service.init_environment()
        return InitEnvironmentResponse(
            agents=[
                AgentModel(
                    aid=agent.aid,
                    role_name=agent.role["name"] if agent.role else "",
                    status=agent.status.value,
                )
                for agent in agents
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
List all agents created
"""


@router.get("/", status_code=status.HTTP_200_OK, response_model=ListAgentsResponse)
@inject
async def list_agents(
    agent_management_service: Annotated[
        AgentManagementService, Depends(Provide[Container.agent_management_service])
    ],
):
    try:
        agents = await agent_management_service.list_agents()
        return ListAgentsResponse(
            agents=[
                AgentModel(
                    aid=agent.aid,
                    role_name=agent.role["name"] if agent.role else "",
                    status=agent.status.value,
                )
                for agent in agents
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
Invoke an agent
"""


@router.post("/{aid}", status_code=status.HTTP_200_OK)
@inject
async def invoke_agent(
    aid: str,
    question: str,
    agent_management_service: Annotated[
        AgentManagementService, Depends(Provide[Container.agent_management_service])
    ],
):
    try:
        agent = await agent_management_service.invoke_agent(aid=aid, question=question)
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/chat", status_code=status.HTTP_200_OK)
@inject
async def chat(
    question: str,
    agent_management_service: Annotated[
        AgentManagementService, Depends(Provide[Container.agent_management_service])
    ],
):
    try:
        agent = await agent_management_service.invoke_agent(aid="supervisor@langpify.agents", question=question)
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/battle", status_code=status.HTTP_200_OK)
@inject
async def battle(
    pokemon1: Annotated[str, Query(..., description="First Pokémon for battle")],
    pokemon2: Annotated[str, Query(..., description="Second Pokémon for battle")],
    agent_management_service: Annotated[
        AgentManagementService, Depends(Provide[Container.agent_management_service])
    ],
):
    """
    Simulates a battle between two Pokémon using the supervisor agent.
    
    Args:
        pokemon1: First Pokémon name (e.g. 'pikachu')
        pokemon2: Second Pokémon name (e.g. 'bulbasaur')
    
    Returns:
        The agent's response with battle analysis
    """
    try:
        # Format the battle question
        question = f"Tell me who would win in a battle between {pokemon1} and {pokemon2}? Provide detailed analysis. Make sure to invoke researcher and pokemon expert."
        
        # Invoke the supervisor agent
        agent_response = await agent_management_service.invoke_agent(
            aid="supervisor@langpify.agents",
            question=question
        )
        
        return agent_response 
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing battle request: {str(e)}"
        )