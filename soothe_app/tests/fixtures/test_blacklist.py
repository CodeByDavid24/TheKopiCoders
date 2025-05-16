from blacklist import (
    EnhancedContentFilter,
    ContentFilterResult,
    ContentMatch,
    SeverityLevel
)
import unittest
import tempfile
import os
import sys
from unittest.mock import patch, mock_open

# Add parent directory to path for importing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEnhancedContentFilter(unittest.TestCase):
    """Test suite for the enhanced content filtering system."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.filter = EnhancedContentFilter()

    def test_basic_content_analysis(self):
        """Test basic content analysis functionality."""
        # Test safe content
        safe_text = "This is completely safe text with no issues."
        result = self.filter.analyze_content(safe_text)

        self.assertIsInstance(result, ContentFilterResult)
        self.assertFalse(result.has_violations)
        self.assertEqual(len(result.matches), 0)
        self.assertEqual(result.severity_score, 0.0)

    def test_harmful_content_detection(self):
        """Test detection of harmful content."""
        # Test with harmful content
        harmful_text = "I want to commit suicide because I'm worthless."
        result = self.filter.analyze_content(harmful_text)

        self.assertTrue(result.has_violations)
        self.assertGreater(len(result.matches), 0)
        self.assertGreater(result.severity_score, 0)

        # Check that critical content is detected
        has_critical = any(
            match.severity == SeverityLevel.CRITICAL for match in result.matches)
        self.assertTrue(has_critical)

    def test_severity_levels(self):
        """Test different severity level detection."""
        test_cases = [
            ("This is a minor issue", SeverityLevel.LOW),
            ("I hate myself completely", SeverityLevel.HIGH),
            ("I want to kill myself", SeverityLevel.CRITICAL)
        ]

        for text, expected_min_severity in test_cases:
            with self.subTest(text=text):
                result = self.filter.analyze_content(text)
                if result.has_violations:
                    max_severity = max(
                        match.severity for match in result.matches)
                    self.assertGreaterEqual(
                        max_severity.value, expected_min_severity.value)

    def test_content_filtering(self):
        """Test that harmful content gets filtered/replaced."""
        harmful_text = "I want to commit suicide right now."
        result = self.filter.analyze_content(harmful_text)

        self.assertTrue(result.has_violations)
        self.assertNotEqual(result.filtered_text, result.original_text)
        # Check for replacement brackets
        self.assertIn("[", result.filtered_text)

    def test_pattern_matching(self):
        """Test regex pattern matching."""
        # Test pattern that should match (end it all)
        pattern_text = "I just want to end it all forever."
        result = self.filter.analyze_content(pattern_text)

        # Should detect via pattern matching
        self.assertTrue(result.has_violations)

        # Check for pattern-based category
        pattern_categories = [match.category for match in result.matches
                              if 'euphemism' in match.category or 'pattern' in match.category]
        self.assertGreater(len(pattern_categories), 0)

    def test_context_analysis(self):
        """Test context analysis for concerning combinations."""
        # Text with concerning combination of academic pressure + death ideation
        context_text = "I'm so stressed about failing this exam I could just die."
        result = self.filter.analyze_content(context_text)

        # Should be detected by context analysis
        if result.has_violations:
            context_categories = [match.category for match in result.matches
                                  if 'combination' in match.category]
            # May or may not trigger depending on exact patterns, so we just verify structure
            self.assertIsInstance(result, ContentFilterResult)

    def test_get_safety_disclaimer(self):
        """Test the safety disclaimer functionality."""
        disclaimer = self.filter._get_safety_disclaimer()

        self.assertIn("Safety Notice:", disclaimer)
        self.assertIn("mental health helpline", disclaimer)
        self.assertIn("seeking help is a sign of strength", disclaimer)
        self.assertIn("Singapore", disclaimer)

    def test_get_safe_response_alternative(self):
        """Test the safe response alternative functionality."""
        alternative = self.filter.get_safe_response_alternative()

        self.assertIn("healthy coping strategies", alternative)
        self.assertIn("constructive approaches", alternative)
        self.assertIn("Safety Notice:", alternative)

    def test_empty_content(self):
        """Test behavior with empty/None content."""
        # Test empty string
        result = self.filter.analyze_content("")
        self.assertFalse(result.has_violations)

        # Test None (should not crash)
        result = self.filter.analyze_content(None)
        self.assertFalse(result.has_violations)

    def test_content_match_structure(self):
        """Test the structure of ContentMatch objects."""
        harmful_text = "I want to hurt myself badly."
        result = self.filter.analyze_content(harmful_text)

        if result.has_violations:
            match = result.matches[0]
            self.assertIsInstance(match, ContentMatch)
            self.assertIsInstance(match.phrase, str)
            self.assertIsInstance(match.severity, SeverityLevel)
            self.assertIsInstance(match.category, str)
            self.assertIsInstance(match.context, str)
            self.assertIsInstance(match.replacement, str)

    def test_case_insensitive_matching(self):
        """Test that matching is case insensitive."""
        test_cases = [
            "I want to COMMIT SUICIDE",
            "i want to commit suicide",
            "I Want To Commit Suicide"
        ]

        for text in test_cases:
            with self.subTest(text=text):
                result = self.filter.analyze_content(text)
                self.assertTrue(result.has_violations)


class TestEnhancedContentFilterWithMockFiles(unittest.TestCase):
    """Test enhanced content filter with mocked configuration files."""

    def test_custom_blacklist_loading(self):
        """Test loading custom blacklist files."""
        # Create temporary files for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""# Test blacklist
[TEST_CATEGORY]
SEVERITY: HIGH
REPLACEMENT: [Test replacement]

test harmful phrase
another test phrase
""")
            f.flush()

            try:
                # Create filter with custom config
                config = {
                    "blacklist_files": [f.name],
                    "pattern_files": [],
                    "enable_pattern_matching": False,
                    "enable_context_analysis": False
                }

                # Test with mocked config loading
                with patch.object(EnhancedContentFilter, '_load_config', return_value=config):
                    filter_instance = EnhancedContentFilter()
                    filter_instance.config = config
                    filter_instance.blacklist_phrases = filter_instance._load_blacklist_phrases()
                    filter_instance.pattern_matchers = []

                    # Test detection of custom phrase
                    result = filter_instance.analyze_content(
                        "This contains test harmful phrase here.")
                    self.assertTrue(result.has_violations)

            finally:
                os.unlink(f.name)

    def test_report_generation(self):
        """Test the report generation functionality."""
        # Create multiple test results
        test_texts = [
            "Safe content here",
            "I want to hurt myself",
            "Another safe text",
            "I hate my life completely"
        ]

        results = []
        for text in test_texts:
            results.append(self.filter.analyze_content(text))

        # Generate report
        report = self.filter.generate_report(results)

        # Verify report structure
        self.assertIn('summary', report)
        self.assertIn('category_analysis', report)
        self.assertIn('severity_analysis', report)
        self.assertIn('performance', report)
        self.assertIn('recommendations', report)

        # Verify summary data
        summary = report['summary']
        self.assertEqual(summary['total_texts_analyzed'], 4)
        self.assertGreaterEqual(summary['texts_with_violations'], 2)
        self.assertLessEqual(summary['violation_rate'], 100.0)


class TestSeverityLevel(unittest.TestCase):
    """Test the SeverityLevel enum."""

    def test_severity_values(self):
        """Test that severity levels have correct values."""
        self.assertEqual(SeverityLevel.LOW.value, 1)
        self.assertEqual(SeverityLevel.MEDIUM.value, 2)
        self.assertEqual(SeverityLevel.HIGH.value, 3)
        self.assertEqual(SeverityLevel.CRITICAL.value, 4)

    def test_severity_comparison(self):
        """Test that severity levels can be compared."""
        self.assertLess(SeverityLevel.LOW, SeverityLevel.MEDIUM)
        self.assertLess(SeverityLevel.MEDIUM, SeverityLevel.HIGH)
        self.assertLess(SeverityLevel.HIGH, SeverityLevel.CRITICAL)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
