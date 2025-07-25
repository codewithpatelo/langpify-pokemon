import uuid
from app.infrastructure.entities.entities import (
    LangpifyStatus,
    LangpifyRole,
    LangpifyAgentType,
    LangpifyAuthorizations,
    LangpifyTemplateLanguage,
    AISettings,
    LangpifyLanguage,
    LangpifyTemplatePlanning,
    LangpifyPlanning,
    LangpifySafety,
)
from typing import Optional, Type, List, Callable
from app.domain.utils.utils import (
    get_llm,
    template_planning_converter,
    to_dynamic_prompt,
)
import logging
from langgraph.graph import StateGraph

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LangpifyBaseAgent:
    def __init__(
        self,
        aid: Optional[str] = None,
        name: str = None,
        type: Optional[LangpifyAgentType] = None,
        role: Optional[LangpifyRole] = None,
        authorizations: Optional[LangpifyAuthorizations] = None,
        safety: Optional[LangpifySafety] = None,
        status: LangpifyStatus = LangpifyStatus.INITIATED,
        settings: Optional[AISettings] = None,
        language: Optional[LangpifyTemplateLanguage] = None,
        planning: Optional[LangpifyTemplatePlanning] = None,
        response_model: Optional[Type[BaseModel]] = None,
        state_schema: Optional[Type[BaseModel]] = None,
        tools: Optional[List[Callable]] = None,
        sub_workflows: Optional[list[StateGraph]] = None,
    ):
        """IDENTITY"""
        self.aid: Optional[str] = aid if aid is not None else f"agent_{uuid.uuid4()}"
        self.name: str = name
        self.role: Optional[LangpifyRole] = role
        self.type: Optional[LangpifyAgentType] = type

        """
        At productive levels Langpify supports A2A :)
        self._agent_card = AgentCard(
            name=self._role.get("name", f"Agente-{self._aid}"),
            description=self._role.get("content", ""),
            version="0.1.0",
            url="",
            capabilities=[],
            skills=[],
        )
        """

        """ LIFECYCLE """
        self.status: LangpifyStatus = status

        """ GOVERNANCE """
        self.authorizations: LangpifyAuthorizations = authorizations or {
            "access_token": "*",
            "organizations": ["*"],
            "applications": ["*"],
            "projects": ["*"],
            "roles": ["*"],
        }
        self.safety: LangpifySafety = safety or {"guardrails": {"prompt": "*"}}
        self.settings: Optional[AISettings] = settings

        """ LANGUAGE MENTAL PROCESSES """
        self.language: Optional[LangpifyLanguage] = get_llm(
            self.settings["_framework"], language
        )

        """ PLANNING MENTAL PROCESSES """
        self.planning: Optional[LangpifyPlanning] = template_planning_converter(
            template=planning,
            state=state_schema,
            response_model=response_model,
            framework=self.settings["_framework"],
            type=self.type,
            name=self.name,
            llm=self.language["llm"],
            prompt=to_dynamic_prompt(self.role, planning, self.safety),
            tools=tools,
            sub_workflows=sub_workflows,
        )

        """ MEMORY MENTAL PROCESSES 
        Reserved for Memory Engines (short-term, long-term)
        
        Short-Term -> Session Context | Example: Langgraph's MemorySaver
        Long-Term -> Episodic, Semantic, Procedural | Example: Langgprah's Store with PostgreSQL + Milvus
        
        In productive environments we would work with SQL, Mongodb and/or Vectorial/Graph Databases accordingly
        """

        """ REASONING MENTAL PROCESSES 
        Reserved for CoT and Inference Engines like Prolog
        
        In Langpify we include Decision-Support Algorithms like TOPSIS and other Multi-Criteria Methods.
        """

        """ PERCEPTION MENTAL PROCESSES 
        Reserved for Event Communication 
        
        Event-based Sensors and Actuators | Fuzzy Thresholds for Reactions
        """
