from pydantic import BaseModel, Field
from typing import Optional, List
from langchain.schema import BaseMessage
from app.application.tools.tools import analyze_battle, explain_stats


POKEMON_EXPERT_TOOLS = [analyze_battle, explain_stats]


class PokemonExpertResponse(BaseModel):
    winner: str = Field(..., description="The name of the winner")
    reasoning: str = Field(..., description="The reasoning for the prediction")


class PokemonExpertState(BaseModel):
    """
    State of the PokemonExpert agent.

    messages: Contains all the messages exchanged with the user.
    input: The user's input.
    remaining_steps: The number of remaining steps in the conversation.
    structured_response: The structured output of the agent.
    """

    messages: List[BaseMessage] = Field(
        default_factory=list,
        description="Puede contener mensajes LangChain o diccionarios",
    )
    input: str
    remaining_steps: int = Field(default=5)
    structured_response: Optional[PokemonExpertResponse] = Field(default=None)
