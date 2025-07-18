from pydantic import BaseModel, Field
from typing import Optional, List
from langchain.schema import BaseMessage
from app.domain.agents.researcher.researcher_models import ResearcherResponse
from app.domain.agents.pokemon_expert.pokemon_expert_models import PokemonExpertResponse

class SupervisorResponse(BaseModel):
    answer: str = Field(..., description="The chatbot's response")
    reasoning: Optional[str] = Field(..., description="The chatbot's reasoning")


class SupervisorState(BaseModel):
    messages: List[BaseMessage] = Field(
        default_factory=list,
        description="Puede contener mensajes LangChain o diccionarios",
    )
    input: str
    remaining_steps: int = Field(default=5)
    structured_response: Optional[SupervisorResponse] = Field(default=None)
    research_response: Optional[ResearcherResponse] = Field(default=None)
    pokemon_expert_response: Optional[PokemonExpertResponse] = Field(default=None)
    
