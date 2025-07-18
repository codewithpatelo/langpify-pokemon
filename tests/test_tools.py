import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.application.tools.tools import (
    analyze_battle,
    explain_stats,
    fetch_pokemon_info,
)


class TestTools:
    """Tests for the tools.py module"""

    @patch("app.application.tools.tools.analyze_pokemon_battle")
    def test_analyze_battle(self, mock_analyze_battle):
        """Test analyze_battle function"""
        # Setup mock
        mock_analyze_battle.return_value = (
            "pikachu",
            "Pikachu is faster and would attack first.",
        )

        # Test data
        pokemon1_data = {"name": "pikachu", "types": ["electric"]}
        pokemon2_data = {"name": "bulbasaur", "types": ["grass", "poison"]}

        # Call the function
        result = analyze_battle(pokemon1_data, pokemon2_data)

        # Assertions
        assert result == ("pikachu", "Pikachu is faster and would attack first.")
        mock_analyze_battle.assert_called_once_with(pokemon1_data, pokemon2_data)

    @patch("app.application.tools.tools.ChatOpenAI")
    @patch("app.application.tools.tools.ChatGroq")
    @patch("app.application.tools.tools.os.getenv")
    def test_explain_stats_openai(self, mock_getenv, mock_chatgroq, mock_chatopenai):
        """Test explain_stats function with OpenAI model"""
        # Setup mocks
        mock_getenv.return_value = "openai"
        mock_model = MagicMock()
        mock_model.invoke.return_value.content = (
            "Pikachu is an Electric-type Pokémon with high speed."
        )
        mock_chatopenai.return_value = mock_model

        # Test data
        pokemon_data = {
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

        # Call the function
        result = explain_stats(pokemon_data)

        # Assertions
        assert result == "Pikachu is an Electric-type Pokémon with high speed."
        assert mock_chatopenai.called
        assert not mock_chatgroq.called

    @patch("app.application.tools.tools.ChatOpenAI")
    @patch("app.application.tools.tools.ChatGroq")
    @patch("app.application.tools.tools.os.getenv")
    def test_explain_stats_groq(self, mock_getenv, mock_chatgroq, mock_chatopenai):
        """Test explain_stats function with Groq model"""
        # Setup mocks
        mock_getenv.return_value = "groq"
        mock_model = MagicMock()
        mock_model.invoke.return_value.content = (
            "Pikachu is an Electric-type Pokémon with high speed."
        )
        mock_chatgroq.return_value = mock_model

        # Test data
        pokemon_data = {
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

        # Call the function
        result = explain_stats(pokemon_data)

        # Assertions
        assert result == "Pikachu is an Electric-type Pokémon with high speed."
        assert not mock_chatopenai.called
        assert mock_chatgroq.called

    @patch("app.application.tools.tools.fetch_pokemon_data")
    def test_fetch_pokemon_info_success(self, mock_fetch_pokemon_data):
        """Test fetch_pokemon_info function success case"""
        # Setup mock
        mock_fetch_pokemon_data.return_value = {
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

        # Call the function
        result = fetch_pokemon_info("Pikachu")

        # Assertions
        assert result["name"] == "pikachu"
        assert result["types"] == ["electric"]
        mock_fetch_pokemon_data.assert_called_once_with("pikachu")

    @patch("app.application.tools.tools.fetch_pokemon_data")
    def test_fetch_pokemon_info_error(self, mock_fetch_pokemon_data):
        """Test fetch_pokemon_info function error case"""
        # Setup mock to raise an exception
        mock_fetch_pokemon_data.side_effect = Exception("Pokemon not found")

        # Call the function
        result = fetch_pokemon_info("nonexistentpokemon")

        # Assertions
        assert "error" in result
        assert result["error"] == "Pokemon not found"
