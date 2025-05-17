from soothe_app.src.models.game_state import GameState
from soothe_app.src.ui.gradio_interface import GradioInterface
from soothe_app.src.core.narrative_engine import NarrativeEngine
from soothe_app.src.core.api_client import ClaudeClient
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for importing from the main app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


class TestFullFlow(unittest.TestCase):
    """Integration tests for the full application flow."""

    def setUp(self):
        """Set up test environment and mock dependencies."""
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
        self.mock_claude_client = MagicMock(spec=ClaudeClient)
        self.mock_claude_client.is_ready.return_value = True
        self.mock_claude_client.get_narrative.return_value = (
            "Initial narrative", None)
        self.mock_claude_client.generate_response.return_value = (
            "Response text", None)

        # Patch the get_claude_client function
        self.claude_client_patcher = patch(
            'soothe_app.src.core.narrative_engine.get_claude_client',
            return_value=self.mock_claude_client
        )
        self.claude_client_mock = self.claude_client_patcher.start()

        # Create narrative engine
        self.engine = NarrativeEngine(self.character_data)

        # Mock TTS handler
        self.tts_handler_patcher = patch(
            'soothe_app.src.ui.tts_handler.get_tts_handler',
            return_value=MagicMock()
        )
        self.tts_handler_mock = self.tts_handler_patcher.start()

    def tearDown(self):
        """Clean up mocks."""
        self.claude_client_patcher.stop()
        self.tts_handler_patcher.stop()

    def test_consent_to_gameplay_flow(self):
        """Test the full flow from consent to gameplay."""
        # Create gradio interface with narrative engine
        with patch('soothe_app.src.core.narrative_engine.create_narrative_engine', return_value=self.engine):
            interface = GradioInterface(self.character_data)

            # Step 1: Initial consent message
            response = interface.main_loop(None, [])
            self.assertIn("Warning & Consent", response)

            # Step 2: Agree to consent
            response = interface.main_loop("I agree", [])
            self.assertIn("Thank you", response)
            self.assertTrue(self.engine.game_state.is_consent_given())

            # Step 3: Start game
            response = interface.main_loop("start game", [])
            self.assertEqual(response, "Initial narrative")
            self.mock_claude_client.get_narrative.assert_called_once()

            # Step 4: First gameplay interaction
            self.mock_claude_client.generate_response.return_value = (
                "Your heart beats faster as you raise your hand.", None)
            response = interface.main_loop(
                "I want to raise my hand in class", [])
            self.assertEqual(
                response, "Your heart beats faster as you raise your hand.")
            self.mock_claude_client.generate_response.assert_called_once()

            # Verify game state was updated
            self.assertEqual(self.engine.game_state.get_interaction_count(), 1)
            history = self.engine.game_state.get_history()
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0][0], "I want to raise my hand in class")
            self.assertEqual(
                history[0][1], "Your heart beats faster as you raise your hand.")

    def test_error_handling_flow(self):
        """Test error handling in the full flow."""
        # Create gradio interface with narrative engine
        with patch('soothe_app.src.core.narrative_engine.create_narrative_engine', return_value=self.engine):
            interface = GradioInterface(self.character_data)

            # Step 1: Setup for error
            self.engine.game_state.give_consent()
            self.mock_claude_client.generate_response.side_effect = Exception(
                "API error")

            # Step 2: Attempt gameplay interaction
            response = interface.main_loop("What should I do?", [])
            self.assertIn("Error", response)

    def test_safety_checks_flow(self):
        """Test safety checks in the full flow."""
        # Create gradio interface with narrative engine
        with patch('soothe_app.src.core.narrative_engine.create_narrative_engine', return_value=self.engine):
            interface = GradioInterface(self.character_data)

            # Step 1: Setup
            self.engine.game_state.give_consent()
            self.engine.game_state.set_starting_narrative("Initial narrative")

            # Step 2: Test unsafe input
            with patch('soothe_app.src.core.narrative_engine.check_input_safety',
                       return_value=(False, "This content is not safe")):
                response = interface.main_loop("Unsafe content", [])
                self.assertEqual(response, "This content is not safe")
                self.mock_claude_client.generate_response.assert_not_called()

            # Step 3: Test unsafe output
            with patch('soothe_app.src.core.narrative_engine.check_input_safety',
                       return_value=(True, "Safe content")):
                with patch('soothe_app.src.core.narrative_engine.filter_response_safety',
                           return_value="Filtered safe response"):
                    response = interface.main_loop("Safe content", [])
                    self.assertEqual(response, "Filtered safe response")

    def test_ending_generation_flow(self):
        """Test the story ending generation flow."""
        # Create gradio interface with narrative engine
        with patch('soothe_app.src.core.narrative_engine.create_narrative_engine', return_value=self.engine):
            interface = GradioInterface(self.character_data)

            # Step 1: Setup
            self.engine.game_state.give_consent()
            self.engine.game_state.set_starting_narrative("Initial narrative")

            # Step 2: Mock the should_trigger_ending check
            with patch.object(self.engine.game_state, 'should_trigger_ending', return_value=True):
                # Step 3: Mock the ending generation
                with patch.object(self.engine, 'generate_ending', return_value="End of story"):
                    response = interface.main_loop("Continue the story", [])
                    self.assertEqual(response, "End of story")

    @patch('gradio.ChatInterface')
    def test_interface_creation_and_launch(self, mock_chat_interface):
        """Test interface creation and launch."""
        # Create mock for the chat interface
        mock_interface = MagicMock()
        mock_chat_interface.return_value = mock_interface

        # Create gradio interface
        interface = GradioInterface(self.character_data)

        # Test interface creation
        created_interface = interface.create_interface()
        self.assertEqual(created_interface, mock_interface)
        mock_chat_interface.assert_called_once()

        # Test interface launch
        interface.launch(share=False, server_name="localhost",
                         server_port=7860)
        mock_interface.launch.assert_called_once_with(
            share=False, server_name="localhost", server_port=7860
        )

        # Test interface close
        interface.close()
        mock_interface.close.assert_called_once()


class TestGameStatePersistence(unittest.TestCase):
    """Tests for game state persistence through interactions."""

    def setUp(self):
        """Set up test environment."""
        self.game_state = GameState({})

    def test_history_tracking(self):
        """Test that conversation history is correctly tracked."""
        # Add several interactions
        self.game_state.add_to_history("Message 1", "Response 1")
        self.game_state.add_to_history("Message 2", "Response 2")
        self.game_state.add_to_history("Message 3", "Response 3")

        # Check history
        history = self.game_state.get_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], ("Message 1", "Response 1"))
        self.assertEqual(history[1], ("Message 2", "Response 2"))
        self.assertEqual(history[2], ("Message 3", "Response 3"))

    def test_interaction_counting(self):
        """Test interaction count tracking."""
        # Initial count should be 0
        self.assertEqual(self.game_state.get_interaction_count(), 0)

        # Increment several times
        for i in range(5):
            count = self.game_state.increment_interaction_count()
            self.assertEqual(count, i + 1)

        # Check final count
        self.assertEqual(self.game_state.get_interaction_count(), 5)

    def test_ending_trigger(self):
        """Test ending trigger based on interaction count."""
        # Initially should not trigger ending
        self.assertFalse(self.game_state.should_trigger_ending())

        # Increment to just below threshold
        for _ in range(11):
            self.game_state.increment_interaction_count()

        self.assertFalse(self.game_state.should_trigger_ending())

        # Increment to threshold
        self.game_state.increment_interaction_count()
        self.assertTrue(self.game_state.should_trigger_ending())

    def test_consent_tracking(self):
        """Test consent tracking in game state."""
        # Initial state
        self.assertFalse(self.game_state.is_consent_given())

        # Give consent
        self.game_state.give_consent()
        self.assertTrue(self.game_state.is_consent_given())


if __name__ == '__main__':
    unittest.main()
