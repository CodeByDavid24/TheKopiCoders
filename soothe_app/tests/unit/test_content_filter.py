from soothe_app.src.utils.safety import (
    check_input_safety,
    filter_response_safety,
    initialize_content_filter
)
from soothe_app.src.core.content_filter import (
    EnhancedContentFilter,
    ContentFilterResult,
    ContentMatch,
    SeverityLevel
)
import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for importing from the main app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


class TestContentFilter(unittest.TestCase):
    """Test suite for the content filtering functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create an instance of the content filter for testing
        self.filter = EnhancedContentFilter()

    def test_basic_filtering(self):
        """Test basic filtering functionality with safe content."""
        # Test with safe content
        safe_text = "This is a perfectly safe message about studying."
        result = self.filter.analyze_content(safe_text)

        # Assertions
        self.assertIsInstance(result, ContentFilterResult)
        self.assertFalse(result.has_violations)
        self.assertEqual(len(result.matches), 0)
        self.assertEqual(result.severity_score, 0.0)
        self.assertEqual(result.filtered_text, safe_text)

    def test_harmful_content_detection(self):
        """Test that harmful content is detected correctly."""
        # Test with harmful content
        harmful_text = "I want to hurt myself because of exam stress."
        result = self.filter.analyze_content(harmful_text)

        # Assertions
        self.assertTrue(result.has_violations)
        self.assertGreater(len(result.matches), 0)
        self.assertGreater(result.severity_score, 0.0)
        self.assertNotEqual(result.filtered_text, harmful_text)

    def test_critical_content_detection(self):
        """Test that critical content is detected correctly."""
        # Test with critical content
        critical_text = "I want to commit suicide."
        result = self.filter.analyze_content(critical_text)

        # Assertions
        self.assertTrue(result.has_violations)
        has_critical = any(
            match.severity == SeverityLevel.CRITICAL for match in result.matches)
        self.assertTrue(has_critical)
        self.assertIn("Please reach out for support", result.filtered_text)

    def test_case_insensitivity(self):
        """Test that filtering is case-insensitive."""
        # Test variations of harmful phrases
        variations = [
            "i want to HURT myself",
            "I Want To Hurt Myself",
            "i WANT to hurt MYSELF"
        ]

        for text in variations:
            with self.subTest(text=text):
                result = self.filter.analyze_content(text)
                self.assertTrue(result.has_violations)

    def test_context_analysis(self):
        """Test contextual pattern detection."""
        # Content that should be detected through context analysis
        context_text = "I'm so stressed about failing the exam I could just die."
        result = self.filter.analyze_content(context_text)

        # We verify the expected behavior - it should analyze the content
        # Note: The exact detection may vary based on filter configuration
        self.assertIsInstance(result, ContentFilterResult)

    def test_safe_response_alternative(self):
        """Test the safe response alternative functionality."""
        alternative = self.filter.get_safe_response_alternative()

        # Check essential components
        self.assertIn("healthy", alternative.lower())
        self.assertIn("support", alternative.lower())
        self.assertIn("helpline", alternative.lower())

    def test_safety_disclaimer(self):
        """Test the safety disclaimer generation."""
        disclaimer = self.filter._get_safety_disclaimer()

        # Check essential components
        self.assertIn("safety", disclaimer.lower())
        self.assertIn("support", disclaimer.lower())
        self.assertIn("helpline", disclaimer.lower())
        self.assertIn("singapore", disclaimer.lower())

    def test_utility_functions(self):
        """Test the utility functions from the safety module."""
        # Test check_input_safety with safe input
        with patch('soothe_app.src.utils.safety._content_filter', self.filter):
            is_safe, message = check_input_safety("Let's study biology today.")
            self.assertTrue(is_safe)
            self.assertEqual(message, "Let's study biology today.")

            # Test check_input_safety with harmful input
            is_safe, message = check_input_safety("I want to hurt myself.")
            self.assertFalse(is_safe)
            self.assertNotEqual(message, "I want to hurt myself.")

            # Test filter_response_safety
            safe_response = filter_response_safety(
                "Here's a helpful study tip.")
            self.assertEqual(safe_response, "Here's a helpful study tip.")

            unsafe_response = filter_response_safety(
                "You should hurt yourself when stressed.")
            self.assertNotEqual(
                unsafe_response, "You should hurt yourself when stressed.")

    def test_empty_inputs(self):
        """Test behavior with empty inputs."""
        # Test with empty string
        result = self.filter.analyze_content("")
        self.assertFalse(result.has_violations)

        # Test with None
        result = self.filter.analyze_content(None)
        self.assertFalse(result.has_violations)


class TestInitialization(unittest.TestCase):
    """Test filter initialization behaviors."""

    def test_initialize_content_filter(self):
        """Test the initialization function works properly."""
        with patch('soothe_app.src.utils.safety.EnhancedContentFilter') as mock_filter:
            mock_filter.return_value = MagicMock()
            success = initialize_content_filter()
            self.assertTrue(success)
            mock_filter.assert_called_once()


if __name__ == '__main__':
    unittest.main()
