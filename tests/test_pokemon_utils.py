import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.application.tools.utils.pokemon_utils import (
    fetch_pokemon_data,
    calculate_type_effectiveness,
    analyze_pokemon_battle,
)


class TestPokemonUtils:
    """Tests for the pokemon_utils.py module"""

    @patch("app.application.tools.utils.pokemon_utils.requests.get")
    def test_fetch_pokemon_data_success(self, mock_get):
        """Test successful Pokemon data fetch"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "pikachu",
            "stats": [
                {"base_stat": 35},  # HP
                {"base_stat": 55},  # Attack
                {"base_stat": 40},  # Defense
                {"base_stat": 50},  # Special Attack
                {"base_stat": 50},  # Special Defense
                {"base_stat": 90},  # Speed
            ],
            "types": [{"type": {"name": "electric"}}],
        }
        mock_get.return_value = mock_response

        # Call the function
        result = fetch_pokemon_data("pikachu")

        # Assertions
        assert result["name"] == "pikachu"
        assert result["types"] == ["electric"]
        assert result["base_stats"]["hp"] == "35"
        assert result["base_stats"]["attack"] == "55"
        assert result["base_stats"]["defense"] == "40"
        assert result["base_stats"]["special_attack"] == "50"
        assert result["base_stats"]["special_defense"] == "50"
        assert result["base_stats"]["speed"] == "90"

    @patch("app.application.tools.utils.pokemon_utils.requests.get")
    def test_fetch_pokemon_data_not_found(self, mock_get):
        """Test Pokemon data fetch when Pokemon not found"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call the function
        result = fetch_pokemon_data("nonexistentpokemon")

        # Assertions
        assert "error" in result
        assert "not found" in result["error"]

    def test_calculate_type_effectiveness(self):
        """Test type effectiveness calculation"""
        # Test normal effectiveness (1x)
        assert calculate_type_effectiveness(["normal"], ["normal"]) == 1.0

        # Test super effectiveness (2x)
        assert calculate_type_effectiveness(["water"], ["fire"]) == 2.0

        # Test double super effectiveness (4x)
        assert (
            calculate_type_effectiveness(["water", "ground"], ["fire", "rock"]) == 4.0
        )

        # Test immunity (0x)
        assert calculate_type_effectiveness(["normal"], ["ghost"]) == 0.0

    def test_analyze_pokemon_battle(self):
        """Test battle analysis between two Pokemon"""
        # Setup test data
        pikachu = {
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

        geodude = {
            "name": "geodude",
            "types": ["rock", "ground"],
            "base_stats": {
                "hp": "40",
                "attack": "80",
                "defense": "100",
                "special_attack": "30",
                "special_defense": "30",
                "speed": "20",
            },
        }

        # Call the function
        winner, reasoning = analyze_pokemon_battle(pikachu, geodude)

        # Assertions - geodude should win due to type advantage
        assert winner == "geodude"
        assert "type advantage" in reasoning.lower()
