import unittest
from unittest.mock import patch, mock_open
import os
import sys

from soothe_app.blacklist import (
    EnhancedContentFilter,
    ContentFilterResult,
    ContentMatch,
    SeverityLevel
)


class TestBlacklist(unittest.TestCase):
    """Test suite for the blacklist content filtering system."""

    def test_contains_blacklisted_content(self):
        """Test that blacklisted content is properly detected."""
        # Create a simple test blacklist
        test_blacklist = ["harmful phrase", "dangerous content", "bad word"]

        # Test with content containing a blacklisted phrase
        text_with_harmful = "This contains a harmful phrase that should be detected."
        has_blacklisted, matched = contains_blacklisted_content(
            text_with_harmful, test_blacklist)
        self.assertTrue(has_blacklisted)
        self.assertIn("harmful phrase", matched)

        # Test with safe content
        safe_text = "This is completely safe text with no issues."
        has_blacklisted, matched = contains_blacklisted_content(
            safe_text, test_blacklist)
        self.assertFalse(has_blacklisted)
        self.assertEqual(len(matched), 0)

    def test_filter_content(self):
        """Test that blacklisted content is properly filtered."""
        # Create a simple test blacklist
        test_blacklist = ["harmful phrase", "dangerous content", "bad word"]

        # Test basic filtering
        text_to_filter = "This contains a harmful phrase that should be filtered."
        filtered = filter_content(text_to_filter, "[FILTERED]", test_blacklist)
        self.assertIn("[FILTERED]", filtered)
        self.assertNotIn("harmful phrase", filtered)

        # Test with no matches
        safe_text = "This is completely safe text with no issues."
        filtered = filter_content(safe_text, "[FILTERED]", test_blacklist)
        self.assertEqual(filtered, safe_text)

    def test_get_safety_disclaimer(self):
        """Test the safety disclaimer content."""
        disclaimer = get_safety_disclaimer()
        self.assertIn("Safety Notice:", disclaimer)
        self.assertIn("mental health helpline", disclaimer)
        self.assertIn("seeking help is a sign of strength", disclaimer)

    def test_get_safe_response_alternative(self):
        """Test the safe response alternative content."""
        alternative = get_safe_response_alternative()
        self.assertIn("healthy coping strategies", alternative)
        self.assertIn("constructive approaches", alternative)

        # Check safety disclaimer is included
        self.assertIn("Safety Notice:", alternative)

    @patch('builtins.open')
    def test_load_blacklist_from_file(self, mock_open_func):
        """Test loading blacklist from a file."""
        # Create mock file content with comments and empty lines
        mock_file_content = """# Comment line - should be ignored
harmful phrase

# Another comment
dangerous content
   
bad word"""

        # Setup the mock
        mock_open_func.return_value = mock_open(
            read_data=mock_file_content).return_value

        # Call the function with default blacklist for simplicity
        with patch('soothe_app.blacklist.BLACKLISTED_PHRASES', ['existing_phrase']):
            result = load_blacklist_from_file("test_blacklist.txt")

            # Check our file phrases are in the result
            phrases_from_file = ["harmful phrase",
                                 "dangerous content", "bad word"]
            for phrase in phrases_from_file:
                self.assertTrue(any(phrase == item for item in result),
                                f"Expected {phrase} to be in result")


if __name__ == '__main__':
    unittest.main()
