from soothe_app.src.core.api_client import (
    ClaudeClient,
    get_claude_client
)
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for importing from the main app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


class TestClaudeClient(unittest.TestCase):
    """Integration tests for the Claude API client."""

    def setUp(self):
        """Set up test environment with mock API key."""
        # Save original environment
        self.original_api_key = os.environ.get('CLAUDE_API_KEY')

        # Set test API key
        os.environ['CLAUDE_API_KEY'] = 'test_api_key'

    def tearDown(self):
        """Restore original environment."""
        # Restore original API key or remove if not present
        if self.original_api_key:
            os.environ['CLAUDE_API_KEY'] = self.original_api_key
        else:
            os.environ.pop('CLAUDE_API_KEY', None)

    @patch('anthropic.Anthropic')
    def test_client_initialization(self, mock_anthropic):
        """Test Claude client initialization."""
        # Setup mock response
        mock_instance = MagicMock()
        mock_anthropic.return_value = mock_instance

        # Create client
        client = ClaudeClient()

        # Verify client was initialized properly
        self.assertTrue(client.is_ready())
        self.assertEqual(client.error_message, '')
        mock_anthropic.assert_called_once_with(api_key='test_api_key')

    @patch('anthropic.Anthropic')
    def test_client_initialization_error(self, mock_anthropic):
        """Test handling of initialization errors."""
        # Setup mock to raise exception
        mock_anthropic.side_effect = Exception("API error")

        # Create client
        client = ClaudeClient()

        # Verify error handling
        self.assertFalse(client.is_ready())
        self.assertIn("API error", client.error_message)

    @patch('anthropic.Anthropic')
    def test_missing_api_key(self, mock_anthropic):
        """Test behavior when API key is missing."""
        # Remove API key from environment
        os.environ.pop('CLAUDE_API_KEY', None)

        # Create client
        client = ClaudeClient()

        # Verify error handling
        self.assertFalse(client.is_ready())
        self.assertIn("API_KEY", client.error_message)
        mock_anthropic.assert_not_called()

    @patch('anthropic.Anthropic')
    def test_generate_response_new_sdk(self, mock_anthropic):
        """Test response generation with newer SDK version."""
        # Setup mock for new SDK
        mock_instance = MagicMock()
        mock_messages = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Response text"
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_messages.create.return_value = mock_response
        mock_instance.messages = mock_messages
        mock_anthropic.return_value = mock_instance

        # Create client
        client = ClaudeClient()

        # Test generate_response
        messages = [{"role": "user", "content": "Test message"}]
        response, error = client.generate_response(messages, "System prompt")

        # Verify results
        self.assertIsNone(error)
        self.assertEqual(response, "Response text")
        mock_messages.create.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_generate_response_old_sdk(self, mock_anthropic):
        """Test response generation with older SDK version."""
        # Setup mock for old SDK (no messages attribute)
        mock_instance = MagicMock()
        delattr(mock_instance, 'messages') if hasattr(
            mock_instance, 'messages') else None
        mock_instance.completion.return_value.completion = "Completion text"
        mock_anthropic.return_value = mock_instance

        # Create client
        client = ClaudeClient()
        client.client = mock_instance

        # Test generate_response
        messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
            {"role": "user", "content": "Second message"}
        ]
        response, error = client.generate_response(messages, "System prompt")

        # Verify results
        self.assertIsNone(error)
        self.assertEqual(response, "Completion text")
        mock_instance.completion.assert_called_once()

        # Check prompt formatting for older SDK
        call_args = mock_instance.completion.call_args[1]
        self.assertIn("Human:", call_args["prompt"])
        self.assertIn("Assistant:", call_args["prompt"])

    @patch('anthropic.Anthropic')
    def test_generate_response_error(self, mock_anthropic):
        """Test error handling during response generation."""
        # Setup mock to raise exception
        mock_instance = MagicMock()
        mock_messages = MagicMock()
        mock_messages.create.side_effect = Exception("API error")
        mock_instance.messages = mock_messages
        mock_anthropic.return_value = mock_instance

        # Create client
        client = ClaudeClient()

        # Test generate_response with error
        messages = [{"role": "user", "content": "Test message"}]
        response, error = client.generate_response(messages, "System prompt")

        # Verify error handling
        self.assertIsNone(response)
        self.assertIsNotNone(error)
        self.assertIn("API error", error)

    @patch('anthropic.Anthropic')
    def test_get_narrative(self, mock_anthropic):
        """Test the get_narrative helper function."""
        # Setup mock
        mock_instance = MagicMock()
        mock_messages = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Narrative response"
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_messages.create.return_value = mock_response
        mock_instance.messages = mock_messages
        mock_anthropic.return_value = mock_instance

        # Create client
        client = ClaudeClient()

        # Test get_narrative
        narrative, error = client.get_narrative("Prompt text", "System prompt")

        # Verify results
        self.assertIsNone(error)
        self.assertEqual(narrative, "Narrative response")
        mock_messages.create.assert_called_once()
        call_args = mock_messages.create.call_args[1]
        self.assertEqual(call_args["messages"][0]["content"], "Prompt text")
        self.assertEqual(call_args["system"], "System prompt")

    @patch('soothe_app.src.core.api_client.ClaudeClient')
    def test_get_claude_client_singleton(self, mock_client_class):
        """Test that get_claude_client returns a singleton instance."""
        # Setup mock
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        # Call twice
        client1 = get_claude_client()
        client2 = get_claude_client()

        # Verify singleton behavior
        self.assertEqual(client1, client2)
        mock_client_class.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_proxy_configuration_error(self, mock_anthropic):
        """Test handling of proxy configuration errors."""
        # Setup mock to raise TypeError with proxies message
        mock_anthropic.side_effect = [
            TypeError("unexpected keyword argument 'proxies'"),
            MagicMock()  # Second call succeeds
        ]

        # Create client
        with patch('httpx.Client') as mock_http_client:
            mock_http_client.return_value = "http_client_instance"
            client = ClaudeClient()

        # Verify error handling with fallback
        self.assertTrue(client.is_ready())
        self.assertEqual(mock_anthropic.call_count, 2)
        # Second call should include http_client
        second_call_kwargs = mock_anthropic.call_args[1]
        self.assertIn('http_client', second_call_kwargs)


class TestClaudeClientWithRealAPI(unittest.TestCase):
    """Optional tests that can use the real API if credentials are available."""

    @unittest.skipIf('CLAUDE_API_KEY' not in os.environ, "No API key available")
    def test_real_api_initialization(self):
        """Test initialization with real API key."""
        # Only runs if API key is available
        client = ClaudeClient()
        self.assertTrue(client.is_ready())

    @unittest.skipIf('CLAUDE_API_KEY' not in os.environ, "No API key available")
    def test_real_api_simple_query(self):
        """Test a simple query to the real API."""
        # Only runs if API key is available
        client = ClaudeClient()
        messages = [{"role": "user", "content": "Say hello in one word."}]
        response, error = client.generate_response(messages, "Be concise.")

        self.assertIsNone(error)
        self.assertIsNotNone(response)
        self.assertLess(len(response.split()), 5)  # Should be very short


if __name__ == '__main__':
    unittest.main()
