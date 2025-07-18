import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.domain.entities.routers.agents.routers import (
    ListAgentTemplatesResponse,
    CreateAgentRequest,
    CreateAgentResponse,
    AgentModel,
    InitEnvironmentResponse,
    ListAgentsResponse,
)
from app.domain.agents.base_agent import LangpifyBaseAgent
from app.domain.entities.agent_status import AgentStatus


class TestAgentRoutes:
    """Tests for the agent routes"""

    client = TestClient(app)

    @patch(
        "app.application.services.agent_management_service.AgentManagementService.list_all_templates"
    )
    async def test_list_templates(self, mock_list_all_templates):
        """Test listing agent templates endpoint"""
        # Setup mock
        mock_list_all_templates.return_value = [
            {"name": "pokemon_expert", "description": "Pokemon Expert Agent"},
            {"name": "researcher", "description": "Researcher Agent"},
        ]

        # Make request
        response = self.client.get("/agents/templates")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) == 2
        assert data["templates"][0]["name"] == "pokemon_expert"
        assert data["templates"][1]["name"] == "researcher"

    @patch(
        "app.application.services.agent_management_service.AgentManagementService.create_agent_from_template"
    )
    async def test_create_agent(self, mock_create_agent):
        """Test creating an agent endpoint"""
        # Setup mock
        mock_agent = MagicMock(spec=LangpifyBaseAgent)
        mock_agent.aid = "pokemon_expert@langpify.agents"
        mock_agent.role = {"name": "Pokemon Expert"}
        mock_agent.status = AgentStatus.ACTIVE
        mock_create_agent.return_value = mock_agent

        # Make request
        response = self.client.post("/agents/", json={"aid_prefix": "pokemon_expert"})

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert "agent" in data
        assert data["agent"]["aid"] == "pokemon_expert@langpify.agents"
        assert data["agent"]["role_name"] == "Pokemon Expert"
        assert data["agent"]["status"] == "ACTIVE"

    @patch(
        "app.application.services.agent_management_service.AgentManagementService.init_environment"
    )
    async def test_init_environment(self, mock_init_environment):
        """Test initializing the environment endpoint"""
        # Setup mock
        mock_agent1 = MagicMock(spec=LangpifyBaseAgent)
        mock_agent1.aid = "pokemon_expert@langpify.agents"
        mock_agent1.role = {"name": "Pokemon Expert"}
        mock_agent1.status = AgentStatus.ACTIVE

        mock_agent2 = MagicMock(spec=LangpifyBaseAgent)
        mock_agent2.aid = "researcher@langpify.agents"
        mock_agent2.role = {"name": "Researcher"}
        mock_agent2.status = AgentStatus.ACTIVE

        mock_init_environment.return_value = [mock_agent1, mock_agent2]

        # Make request
        response = self.client.post("/agents/environment")

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) == 2
        assert data["agents"][0]["aid"] == "pokemon_expert@langpify.agents"
        assert data["agents"][1]["aid"] == "researcher@langpify.agents"

    @patch(
        "app.application.services.agent_management_service.AgentManagementService.list_agents"
    )
    async def test_list_agents(self, mock_list_agents):
        """Test listing agents endpoint"""
        # Setup mock
        mock_agent1 = MagicMock(spec=LangpifyBaseAgent)
        mock_agent1.aid = "pokemon_expert@langpify.agents"
        mock_agent1.role = {"name": "Pokemon Expert"}
        mock_agent1.status = AgentStatus.ACTIVE

        mock_agent2 = MagicMock(spec=LangpifyBaseAgent)
        mock_agent2.aid = "researcher@langpify.agents"
        mock_agent2.role = {"name": "Researcher"}
        mock_agent2.status = AgentStatus.ACTIVE

        mock_list_agents.return_value = [mock_agent1, mock_agent2]

        # Make request
        response = self.client.get("/agents/")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) == 2
        assert data["agents"][0]["aid"] == "pokemon_expert@langpify.agents"
        assert data["agents"][1]["aid"] == "researcher@langpify.agents"

    @patch(
        "app.application.services.agent_management_service.AgentManagementService.invoke_agent"
    )
    async def test_invoke_agent(self, mock_invoke_agent):
        """Test invoking an agent endpoint"""
        # Setup mock
        mock_invoke_agent.return_value = {
            "response": "Pikachu is an Electric-type Pokémon."
        }

        # Make request
        response = self.client.post(
            "/agents/pokemon_expert@langpify.agents?question=Tell me about Pikachu"
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Pikachu is an Electric-type Pokémon."

    @patch(
        "app.application.services.agent_management_service.AgentManagementService.invoke_agent"
    )
    async def test_chat(self, mock_invoke_agent):
        """Test chat endpoint"""
        # Setup mock
        mock_invoke_agent.return_value = {
            "response": "Pikachu is an Electric-type Pokémon."
        }

        # Make request
        response = self.client.post(
            "/agents/system/chat?question=Tell me about Pikachu"
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Pikachu is an Electric-type Pokémon."

    @patch(
        "app.application.services.agent_management_service.AgentManagementService.invoke_agent"
    )
    async def test_battle(self, mock_invoke_agent):
        """Test battle endpoint"""
        # Setup mock
        mock_invoke_agent.return_value = {
            "response": "In a battle between Pikachu and Bulbasaur, Pikachu would likely win."
        }

        # Make request
        response = self.client.get(
            "/agents/system/battle?pokemon1=pikachu&pokemon2=bulbasaur"
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "Pikachu" in data["response"]
        assert "Bulbasaur" in data["response"]
