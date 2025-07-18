from pydantic import BaseModel, Field
from typing import Optional, List
from langchain.schema import BaseMessage
from app.application.tools.tools import fetch_pokemon_info


RESEARCHER_TOOLS = [fetch_pokemon_info]


class PokemonBaseStats(BaseModel):
    hp: str
    attack: str
    defense: str
    special_attack: str
    special_defense: str
    speed: str


class ResearcherResponse(BaseModel):
    name: str = Field(..., description="The name of the Pokémon")
    base_stats: PokemonBaseStats = Field(
        ..., description="The base stats of the Pokémon"
    )
    types: List[str] = Field(..., description="The types of the Pokémon")


class ResearcherState(BaseModel):
    messages: List[BaseMessage] = Field(
        default_factory=list,
        description="Puede contener mensajes LangChain o diccionarios",
    )
    input: str
    remaining_steps: int = Field(default=5)
    structured_response: Optional[ResearcherResponse] = Field(default=None)
