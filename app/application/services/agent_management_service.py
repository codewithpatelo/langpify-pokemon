import yaml
import os
import logging
from app.infrastructure.entities.base_agent import LangpifyBaseAgent
from app.domain.agents.templates import templates
from app.infrastructure.entities.entities import LangpifyStatus, LangpifyAgentTemplate
from app.application.ai_settings.ai_settings_provider import AISettingsProvider
import traceback
from app.domain.agents.supervisor.supervisor_models import (
    SupervisorResponse,
    SupervisorState,
)

from app.domain.agents.researcher.researcher_models import (
    ResearcherResponse,
    ResearcherState,
    RESEARCHER_TOOLS,
)

from app.domain.agents.pokemon_expert.pokemon_expert_models import (
    PokemonExpertResponse,
    PokemonExpertState,
    POKEMON_EXPERT_TOOLS,
)
from app.application.tools.tools import fetch_pokemon_info

from langsmith import traceable
from langchain.schema import SystemMessage, HumanMessage
#from circuitbreaker import circuit

# Configure logger
logger = logging.getLogger(__name__)


class AgentManagementService:
    """
    Agent Management Service

    This service implements the operations inspired in the FIPA protocol Agent Management System (AMS),
    allowing to create, modify, suspend, reactivate, and delete agents.
    Additionally, it provides functionality to manage Agent Templates.
    In production environments, this should be a micro-service.
    """

    def __init__(self, ai_settings_provider: AISettingsProvider):
        """
        Initialize the AgentManagementService.

        Args:
            ai_settings_provider: Provider for AI settings
        """
        self._agents: list[LangpifyBaseAgent] = []
        self.ai_settings_provider = ai_settings_provider
        logger.info(
            f"Creating new instance of AgentManagementService with ID: {id(self)}"
        )

    async def list_all_templates(self) -> list:
        """
        Get all templates from the repository.
        """
        try:
            return templates
        except Exception as e:
            logger.error(f"Error while retrieving all agent templates. {str(e)}")
            return []

    async def create_agent_from_template(self, aid_prefix: str) -> LangpifyBaseAgent:
        """
        Create an agent instance from an agent template.

        Args:
            aid_prefix: Prefix identifier for the agent template

        Returns:
            An instance of LangpifyBaseAgent initialized with the configuration

        Raises:
            FileNotFoundError: If the template file doesn't exist
            KeyError: If required fields (aid, role) are missing
            yaml.YAMLError: If the YAML is malformed
        """
        try:
            # Find the template that matches the given aid_prefix
            template_filename = None
            for template in templates:  # Use the imported templates directly
                if template.get("aid_prefix") == aid_prefix:
                    template_filename = template.get("file_name")
                    break

            if not template_filename:
                raise ValueError(f"No template found with aid_prefix: {aid_prefix}")

            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            )  # Go up to app directory
            template_path = os.path.join(
                base_dir, "domain", "agents", template_filename
            )

            with open(template_path, "r") as f:
                data = yaml.safe_load(f)

            # Validate required fields
            if not all(key in data for key in ["aid", "role"]):
                raise KeyError("YAML template must contain 'aid' and 'role' fields")

            template = LangpifyAgentTemplate(**data)

            settings = self.ai_settings_provider.ai_settings

            if template.aid == "supervisor@langpify.agents":
                response_model = SupervisorResponse
                state_schema = SupervisorState
                tools = []
            elif template.aid == "researcher@langpify.agents":
                response_model = ResearcherResponse
                state_schema = ResearcherState
                tools = RESEARCHER_TOOLS
            elif template.aid == "pokemon_expert@langpify.agents":
                response_model = PokemonExpertResponse
                state_schema = PokemonExpertState
                tools = POKEMON_EXPERT_TOOLS
                

                
            sub_workflows = []
            
            if template.aid == "supervisor@langpify.agents":
                sub_workflows.append(self._agents[0].planning["workflow"]["graph"])
                sub_workflows.append(self._agents[1].planning["workflow"]["graph"])

            agent = LangpifyBaseAgent(
                aid=template.aid,
                name=template.name,
                type=template.type,
                role=template.role,
                settings=settings,
                language=template.language,
                planning=template.planning,
                safety=template.safety,
                response_model=response_model,
                state_schema=state_schema,
                tools=tools,
                sub_workflows=sub_workflows,
            )

            self._agents.append(agent)

            return agent

        except Exception as e:
            logger.error(
                f"Error while creating agent from template {aid_prefix}: {str(e)}\n{traceback.format_exc()}"
            )
            return None

    async def list_agents(self) -> list[LangpifyBaseAgent]:
        return self._agents

    async def init_environment(self) -> list[LangpifyBaseAgent]:
        """
        Initialize the environment by creating agents from all available templates
        and setting their status to ACTIVE.

        Returns:
            A list of activated LangpifyBaseAgent instances
        """
        # Get all available templates from the class method
        templates_list = await self.list_all_templates()

        # Create an agent for each template
        agents = []

        try:
            # Create agent from template using the class method
            researcher_agent = await self.create_agent_from_template("researcherAgent")
            pokemon_expert_agent = await self.create_agent_from_template("pokemonExpertAgent")
            

            # Set agent status to ACTIVE
            if researcher_agent:
                researcher_agent.status = LangpifyStatus.ACTIVE
                agents.append(researcher_agent)
            if pokemon_expert_agent:
                pokemon_expert_agent.status = LangpifyStatus.ACTIVE
                agents.append(pokemon_expert_agent)
                
                
            if researcher_agent and pokemon_expert_agent:
                supervisor_agent = await self.create_agent_from_template("supervisorAgent")
                
                
            if supervisor_agent:
                supervisor_agent.status = LangpifyStatus.ACTIVE
                agents.append(supervisor_agent)

            return agents
        
        except Exception as e:
            logger.error(
                f"Error creating agent from template {aid_prefix}: {str(e)}"
            )
            

        return agents

    @traceable
    #@circuit(failure_threshold=3, recovery_timeout=60)
    async def invoke_agent(self, aid: str, question: str) -> None:
        try:
            for agent in self._agents:
                if agent.aid == aid:
                    if agent.status == LangpifyStatus.ACTIVE:
                        messages = [
                            SystemMessage(content=agent.role["prompt"]),
                            HumanMessage(content=question)
                        ]
                    
                        
                        initial_state = {
                            "input": question,
                            "messages": messages,
                            "remaining_steps": 20,
                            "structured_response": None,
                        }
                        logger.info(f"Invoking agent: {agent.aid}")
                        workflow = agent.planning["workflow"]["graph"]
                        state = await workflow.ainvoke(initial_state)
                        return state
                    else:
                        logger.error(f"Agent {aid} is not active")
                        raise ValueError(f"Agent {aid} is not active")
            logger.error(f"Agent {aid} not found")
            raise ValueError(f"Agent {aid} not found")
        except Exception as e:
            logger.error(f"Error invoking agent {aid}: {str(e)}", exc_info=True)
            raise ValueError(f"Error invoking agent {aid}: {str(e)}")

