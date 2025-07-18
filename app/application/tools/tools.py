from app.application.tools.utils.pokemon_utils import (
    fetch_pokemon_data,
    analyze_pokemon_battle,
)
from typing import Dict, Any, Tuple
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os


load_dotenv()


def analyze_battle(
    pokemon1_data: Dict[str, Any], pokemon2_data: Dict[str, Any]
) -> Tuple[str, str]:
    """
    Analyze a battle between two Pokémon and determine the likely winner

    Args:
        pokemon1_data: Data for the first Pokémon
        pokemon2_data: Data for the second Pokémon

    Returns:
        Tuple containing (winner name, reasoning)
    """
    return analyze_pokemon_battle(pokemon1_data, pokemon2_data)


def explain_stats(pokemon_data: Dict[str, Any]) -> str:
    """
    Generate an explanation of a Pokémon's stats

    Args:
        pokemon_data: Pokémon data

    Returns:
        Explanation of the Pokémon's stats
    """
    stats = pokemon_data["base_stats"]
    pokemon_name = pokemon_data["name"].capitalize()
    types = ", ".join(t.capitalize() for t in pokemon_data["types"])

    # Generate a user-friendly explanation using the LLM
    stats_prompt = PromptTemplate.from_template(
        """
        Please provide a concise explanation of the following Pokémon's stats:
        
        Pokémon: {name}
        Type(s): {types}
        Stats:
        - HP: {hp}
        - Attack: {attack}
        - Defense: {defense}
        - Special Attack: {special_attack}
        - Special Defense: {special_defense}
        - Speed: {speed}
        
        Focus on the Pokémon's strengths and weaknesses based on these stats.
        Keep your explanation under 100 words.
        """
    )

    if os.getenv("MODEL_PROVIDER") == "openai":
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, verbose=True)
    else:
        model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, verbose=True)

    # Query the model
    response = model.invoke(
        [
            HumanMessage(
                content=stats_prompt.format(
                    name=pokemon_name,
                    types=types,
                    hp=stats["hp"],
                    attack=stats["attack"],
                    defense=stats["defense"],
                    special_attack=stats["special_attack"],
                    special_defense=stats["special_defense"],
                    speed=stats["speed"],
                )
            )
        ]
    )

    return response.content


def fetch_pokemon_info(pokemon_name: str) -> Dict[str, Any]:
    """
    Fetch information about a specific Pokémon from the PokéAPI

    Args:
        pokemon_name: Name of the Pokémon (case-insensitive)

    Returns:
        Dictionary containing Pokémon data
    """
    try:
        return fetch_pokemon_data(pokemon_name.lower())
    except Exception as e:
        return {"error": str(e)}
