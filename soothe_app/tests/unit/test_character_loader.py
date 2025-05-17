from soothe_app.src.models.character import (
    Character,
    load_character
)
from soothe_app.src.utils.file_loader import (
    load_json,
    load_character_data,
    save_json,
    load_text_file
)
import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, mock_open

# Add parent directory to path for importing from the main app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


class TestFileLoader(unittest.TestCase):
    """Test suite for file loading utilities."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test file
        self.test_data = {
            "name": "Test Character",
            "gender": "Female",
            "personality": {
                "mbti": "INFP",
                "mbti_description": "Test description"
            },
            "physical": {
                "race": {"name": "Chinese Singaporean"},
                "age": {"years": 17},
                "measurements": {"height": 164, "weight": 46, "bmi": 17.1},
                "appearance": "Test appearance"
            }
        }

        # Create a temporary file with test data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
            json.dump(self.test_data, temp)
            self.temp_file_path = temp.name

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary file
        if hasattr(self, 'temp_file_path') and os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)

    def test_load_json(self):
        """Test loading JSON from file."""
        # Test with existing file
        result = load_json(self.temp_file_path)
        self.assertEqual(result, self.test_data)

        # Test with non-existent file
        result = load_json('non_existent_file')
        self.assertEqual(result, {})

    def test_save_json(self):
        """Test saving JSON to file."""
        # Save to a new temporary file
        new_file = os.path.join(tempfile.gettempdir(), 'test_save.json')
        success = save_json(self.test_data, new_file)

        # Check if save was successful
        self.assertTrue(success)
        self.assertTrue(os.path.exists(new_file))

        # Check if data was saved correctly
        with open(new_file, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.test_data)

        # Clean up
        os.unlink(new_file)

    def test_load_text_file(self):
        """Test loading text content from file."""
        # Create a test text file
        test_text = "This is a test text file."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp:
            temp.write(test_text)
            text_file_path = temp.name

        # Test loading the file
        result = load_text_file(text_file_path)
        self.assertEqual(result, test_text)

        # Test with non-existent file
        result = load_text_file('non_existent_file.txt')
        self.assertIsNone(result)

        # Clean up
        os.unlink(text_file_path)

    @patch('soothe_app.src.utils.file_loader.load_json')
    def test_load_character_data(self, mock_load_json):
        """Test loading character data from various paths."""
        # Setup mock return value
        mock_load_json.return_value = self.test_data

        # Test loading character data
        result = load_character_data()

        # Verify the function tries to load from expected paths
        self.assertEqual(mock_load_json.call_count, 1)
        self.assertEqual(result, self.test_data)


class TestCharacterModel(unittest.TestCase):
    """Test suite for character model functionality."""

    def setUp(self):
        """Set up test data."""
        self.character_data = {
            "name": "Serena",
            "gender": "Female",
            "personality": {
                "mbti": "INFP",
                "mbti_description": "Soft-spoken, Shy, Determined",
                "traits": {
                    "attitudes": "Quietly confident",
                    "perception": "Highly observant"
                }
            },
            "physical": {
                "race": {"name": "Chinese Singaporean"},
                "age": {"years": 17},
                "measurements": {"height": 164, "weight": 46, "bmi": 17.1},
                "appearance": "Slim and soft-featured"
            },
            "class": {
                "name": "JC Student",
                "subjects": ["H2 Chemistry", "H2 Biology"],
                "cca": "Student Council"
            },
            "location": {
                "country": "Singapore",
                "school": "Raffles Junior College"
            },
            "behaviour": ["Takes meticulous notes", "Arrives early to lectures"],
            "anxiety_triggers": ["Being called on unexpectedly", "Group projects"]
        }

    def test_character_from_dict(self):
        """Test creating Character instance from dictionary."""
        character = Character.from_dict(self.character_data)

        # Check basic attributes
        self.assertEqual(character.name, "Serena")
        self.assertEqual(character.gender, "Female")

        # Check nested attributes
        self.assertEqual(character.personality.mbti, "INFP")
        self.assertEqual(
            character.physical.race["name"], "Chinese Singaporean")
        self.assertEqual(character.class_details.name, "JC Student")
        self.assertEqual(character.location.country, "Singapore")

        # Check lists
        self.assertEqual(len(character.class_details.subjects), 2)
        self.assertEqual(len(character.behaviour), 2)
        self.assertEqual(len(character.anxiety_triggers), 2)

    def test_character_to_dict(self):
        """Test converting Character to dictionary."""
        # Create character from data
        character = Character.from_dict(self.character_data)

        # Convert back to dictionary
        result = character.to_dict()

        # Check result has the expected structure
        self.assertIn("name", result)
        self.assertIn("personality", result)
        self.assertIn("physical", result)
        self.assertIn("class", result)
        self.assertIn("location", result)
        self.assertIn("behaviour", result)
        self.assertIn("anxiety_triggers", result)

        # Check values
        self.assertEqual(result["name"], "Serena")
        self.assertEqual(result["personality"]["mbti"], "INFP")

    def test_load_character(self):
        """Test the load_character helper function."""
        # Test with valid data
        character = load_character(self.character_data)
        self.assertIsInstance(character, Character)
        self.assertEqual(character.name, "Serena")

        # Test with empty data
        character = load_character({})
        self.assertIsInstance(character, Character)
        self.assertEqual(character.name, "Serena")  # Default value

    def test_default_values(self):
        """Test that default values are set correctly for missing data."""
        # Create with minimal data
        minimal_data = {"name": "Minimal"}
        character = Character.from_dict(minimal_data)

        # Check defaults are set
        self.assertEqual(character.name, "Minimal")
        self.assertEqual(character.gender, "Female")  # Default value
        self.assertEqual(character.personality.mbti, "INFP")  # Default value
        # Default value
        self.assertEqual(
            character.physical.race["name"], "Chinese Singaporean")


if __name__ == '__main__':
    unittest.main()
