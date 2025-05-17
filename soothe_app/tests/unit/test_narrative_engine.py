from soothe_app.src.models.game_state import GameState
from soothe_app.src.core.narrative_engine import (
    NarrativeEngine,
    create_narrative_engine,
    SYSTEM_PROMPT_TEMPLATE,
    CONSENT_MESSAGE
)
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for importing from the main app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


class TestNarrativeEngine(unittest.TestCase):
    """Test suite for the narrative engine."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test character data
        self.character_data = {
            "name": "Serena",
            "physical": {
                "race": {"name": "Chinese Singaporean"},
                "age": {"years": 17}
            },
            "class": {
                "name": "JC1",
                "subjects": ["H2 Chemistry", "H2 Biology", "H2 Mathematics"],
                "cca": "Student Council"
            },
            "location": {"school": "Raffles Junior College"},
            "daily_routine": {"morning": "5:30 AM"},
            "personality": {"mbti_description": "Soft-spoken, Shy, Determined"}
        }

        # Mock Claude client
        self.mock_claude_client = MagicMock()
        self.mock_claude_client.is_ready.return_value = True
        self.mock_claude_client.get_narrative.return_value = (
            "Initial narrative text", None)
        self.mock_claude_client.generate_response.return_value = (
            "Response text", None)

        # Create narrative engine with mocked client
        with patch('soothe_app.src.core.narrative_engine.get_claude_client', return_value=self.mock_claude_client):
            self.engine = NarrativeEngine(self.character_data)

    def test_system_prompt_building(self):
        """Test that system prompt is correctly built from character data."""
        # Verify system prompt contains character data
        system_prompt = self.engine._build_system_prompt()

        # Check character info is included
        self.assertIn("Serena", system_prompt)
        self.assertIn("Chinese Singaporean", system_prompt)
        self.assertIn("JC1", system_prompt)
        self.assertIn("Raffles Junior College", system_prompt)
        self.assertIn("5:30 AM", system_prompt)
        self.assertIn("Soft-spoken, Shy, Determined", system_prompt)

        # Check essential system instructions
        self.assertIn("HIDDEN GAME MECHANICS", system_prompt)
        self.assertIn("NARRATIVE DO'S", system_prompt)
        self.assertIn("NARRATIVE DON'TS", system_prompt)

    def test_initialize_game(self):
        """Test game initialization with starting narrative."""
        # Test successful initialization
        narrative, success = self.engine.initialize_game()

        # Verify results
        self.assertTrue(success)
        self.assertEqual(narrative, "Initial narrative text")

        # Verify the client was called with correct parameters
        self.mock_claude_client.get_narrative.assert_called_once()
        args, kwargs = self.mock_claude_client.get_narrative.call_args
        self.assertIn("Start the game", args[0])
        self.assertEqual(args[1], self.engine.system_prompt)

        # Test client not ready scenario
        self.mock_claude_client.is_ready.return_value = False
        self.mock_claude_client.get_error.return_value = "Error message"

        narrative, success = self.engine.initialize_game()
        self.assertFalse(success)
        self.assertIn("Error", narrative)

    def test_process_message_consent_flow(self):
        """Test the consent flow in message processing."""
        # Test initial consent request
        response, success = self.engine.process_message("Hello")
        self.assertTrue(success)
        self.assertEqual(response, CONSENT_MESSAGE)

        # Test consent given
        response, success = self.engine.process_message("i agree")
        self.assertTrue(success)
        self.assertIn("Thank you for agreeing", response)
        self.assertTrue(self.engine.game_state.is_consent_given())

        # Test start game command
        # Mock get_starting_narrative to avoid initialize_game call
        self.engine.game_state.set_starting_narrative("Test narrative")
        response, success = self.engine.process_message("start game")
        self.assertTrue(success)
        self.assertEqual(response, "Test narrative")

    def test_process_message_gameplay(self):
        """Test regular gameplay message processing."""
        # Setup game state for testing
        self.engine.game_state.give_consent()
        self.engine.game_state.set_starting_narrative("Initial narrative")

        # Mock input safety check
        with patch('soothe_app.src.core.narrative_engine.check_input_safety', return_value=(True, "Safe message")):
            # Mock response safety filter
            with patch('soothe_app.src.core.narrative_engine.filter_response_safety', return_value="Filtered response"):
                # Test normal gameplay interaction
                response, success = self.engine.process_message(
                    "What should I do?")

                # Verify results
                self.assertTrue(success)
                self.assertEqual(response, "Filtered response")

                # Verify client was called correctly
                self.mock_claude_client.generate_response.assert_called_once()

                # Verify game state is updated
                self.assertEqual(
                    self.engine.game_state.get_interaction_count(), 1)
                self.assertEqual(len(self.engine.game_state.get_history()), 1)

    def test_unsafe_input_handling(self):
        """Test handling of unsafe user input."""
        # Setup game state
        self.engine.game_state.give_consent()

        # Mock unsafe input detection
        with patch('soothe_app.src.core.narrative_engine.check_input_safety',
                   return_value=(False, "This content is not safe")):
            response, success = self.engine.process_message("Unsafe content")

            # Verify results
            self.assertTrue(success)  # Success is True even for unsafe inputs
            self.assertEqual(response, "This content is not safe")

            # Verify client was not called
            self.mock_claude_client.generate_response.assert_not_called()

    def test_generate_ending(self):
        """Test generation of story ending."""
        # Add some history to affect the ending
        self.engine.game_state.add_to_history(
            "I feel stressed", "Response about feelings")
        self.engine.game_state.add_to_history(
            "I'll study late tonight", "Response about studying")

        # Generate ending
        ending = self.engine.generate_ending()

        # Check for essential ending components
        self.assertIn("End of Serena's Story", ending)
        self.assertIn("Understanding Anxiety: Key Insights", ending)
        self.assertIn("Singapore Helplines", ending)

        # Check for personalized elements based on history
        self.assertIn("paying attention to your body's signals", ending)
        self.assertIn("late study nights", ending)

    def test_ending_triggering(self):
        """Test automatic ending triggering based on interaction count."""
        # Setup game state
        self.engine.game_state.give_consent()
        self.engine.game_state.set_starting_narrative("Initial narrative")

        # Mock needed functions to isolate testing
        with patch('soothe_app.src.core.narrative_engine.check_input_safety', return_value=(True, "Safe message")):
            with patch('soothe_app.src.core.narrative_engine.filter_response_safety', return_value="Response"):
                with patch.object(self.engine.game_state, 'should_trigger_ending', return_value=True):
                    with patch.object(self.engine, 'generate_ending', return_value="Story ending"):
                        # Test interaction that should trigger ending
                        response, success = self.engine.process_message(
                            "Continue story")

                        # Verify ending was triggered
                        self.assertTrue(success)
                        self.assertEqual(response, "Story ending")

    def test_error_handling(self):
        """Test handling of API errors."""
        # Setup game state
        self.engine.game_state.give_consent()

        # Mock the API to raise an exception
        self.mock_claude_client.generate_response.side_effect = Exception(
            "API error")

        # Test error handling
        response, success = self.engine.process_message("Test message")

        # Verify results
        self.assertFalse(success)
        self.assertIn("Error", response)


class TestNarrativeEngineFactory(unittest.TestCase):
    """Test the factory function for creating narrative engines."""

    def test_create_narrative_engine(self):
        """Test creation of narrative engine instance."""
        character_data = {"name": "Serena"}

        # Test factory function
        with patch('soothe_app.src.core.narrative_engine.NarrativeEngine') as mock_engine:
            engine = create_narrative_engine(character_data)

            # Verify engine was created with character data
            mock_engine.assert_called_once_with(character_data)


if __name__ == '__main__':
    unittest.main()
