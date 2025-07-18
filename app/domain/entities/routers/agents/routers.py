from pydantic import BaseModel, Field

from typing import List, Optional

from app.infrastructure.entities.base_agent import LangpifyBaseAgent


class AgentTemplateModel(BaseModel):
    aid_prefix: str
    file_name: str


class AgentModel(BaseModel):
    aid: str
    role_name: Optional[str]
    status: Optional[str]


class ListAgentTemplatesResponse(BaseModel):
    templates: List[AgentTemplateModel] = Field(
        default=None, description="List of available agent templates"
    )


class CreateAgentRequest(BaseModel):
    aid_prefix: str = Field(
        default=None, description="AID prefix for the corresponding template/manifest"
    )


class CreateAgentResponse(BaseModel):
    agent: AgentModel = Field(default=None, description="Created agent")


class InitEnvironmentResponse(BaseModel):
    agents: List[AgentModel] = Field(
        default=None, description="List of agents in the environment"
    )


class ListAgentsResponse(BaseModel):
    agents: List[AgentModel] = Field(default=None, description="List of agents created")
