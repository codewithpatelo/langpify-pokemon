import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.domain.agents.base_agent import LangpifyBaseAgent
from app.domain.entities.agent_status import AgentStatus
from app.application.services.agent_management_service import AgentManagementService


@pytest.fixture
def mock_agent_management_service():
    """Fixture for mocking AgentManagementService"""
    service = MagicMock(spec=AgentManagementService)

    # Mock async methods
    service.list_all_templates = AsyncMock()
    service.create_agent_from_template = AsyncMock()
    service.init_environment = AsyncMock()
    service.list_agents = AsyncMock()
    service.invoke_agent = AsyncMock()

    return service


@pytest.fixture
def mock_pokemon_expert_agent():
    """Fixture for mocking a Pokemon Expert agent"""
    agent = MagicMock(spec=LangpifyBaseAgent)
    agent.aid = "pokemon_expert@langpify.agents"
    agent.role = {"name": "Pokemon Expert", "prompt": "You are a Pokemon Expert."}
    agent.status = AgentStatus.ACTIVE
    return agent


@pytest.fixture
def mock_researcher_agent():
    """Fixture for mocking a Researcher agent"""
    agent = MagicMock(spec=LangpifyBaseAgent)
    agent.aid = "researcher@langpify.agents"
    agent.role = {"name": "Researcher", "prompt": "You are a Researcher."}
    agent.status = AgentStatus.ACTIVE
    return agent


@pytest.fixture
def mock_supervisor_agent():
    """Fixture for mocking a Supervisor agent"""
    agent = MagicMock(spec=LangpifyBaseAgent)
    agent.aid = "supervisor@langpify.agents"
    agent.role = {"name": "Supervisor", "prompt": "You are a Supervisor."}
    agent.status = AgentStatus.ACTIVE
    return agent


@pytest.fixture
def pikachu_data():
    """Fixture for Pikachu data"""
    return {
        "name": "pikachu",
        "types": ["electric"],
        "base_stats": {
            "hp": "35",
            "attack": "55",
            "defense": "40",
            "special_attack": "50",
            "special_defense": "50",
            "speed": "90",
        },
    }


@pytest.fixture
def bulbasaur_data():
    """Fixture for Bulbasaur data"""
    return {
        "name": "bulbasaur",
        "types": ["grass", "poison"],
        "base_stats": {
            "hp": "45",
            "attack": "49",
            "defense": "49",
            "special_attack": "65",
            "special_defense": "65",
            "speed": "45",
        },
    }
