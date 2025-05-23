"""
Compatibility layer for SootheAI blacklist functionality.
Provides simple interface to the enhanced content filtering system.

This module serves as a bridge between the main application and the
content filtering system, providing backward compatibility and graceful
fallbacks if the enhanced filter is not available.
"""

from typing import List, Tuple  # Type hints for function signatures
import logging                  # Standard logging for debugging and monitoring

# Try to import the enhanced content filter with graceful fallback
try:
    from soothe_app.src.core.content_filter import EnhancedContentFilter, ContentFilterResult, SeverityLevel
    # Flag indicating enhanced features are available
    ENHANCED_FILTER_AVAILABLE = True
except ImportError:
    ENHANCED_FILTER_AVAILABLE = False  # Flag indicating fallback to simple filter

# Configure logger for this module
# Create logger with module name for identification
logger = logging.getLogger(__name__)

# Global filter instance using singleton pattern
_content_filter = None  # Module-level variable to store filter instance


def initialize_content_filter():
    """
    Initialize the content filter (enhanced or simple).

    Attempts to initialize the enhanced filter first, falling back
    to a simple implementation if the enhanced version is unavailable.
    This ensures the application continues to function even with
    missing dependencies.
    """
    global _content_filter  # Access module-level singleton variable

    # Try to use enhanced filter if available
    if ENHANCED_FILTER_AVAILABLE:
        _content_filter = EnhancedContentFilter()  # Initialize with full features
        # Log successful initialization
        logger.info("Enhanced content filter initialized")
    else:
        _content_filter = SimpleContentFilter()   # Use fallback implementation
        # Log fallback initialization
        logger.info("Simple content filter initialized")


class SimpleContentFilter:
    """
    Simple fallback content filter if enhanced version is not available.

    Provides basic phrase-matching functionality to ensure content
    filtering continues to work even without the full enhanced system.
    """

    def __init__(self):
        """
        Initialize simple filter with basic blacklisted phrases.

        Contains essential harmful phrases that should be caught
        even in the most basic filtering scenario.
        """
        # Define core blacklisted phrases for essential safety
        self.blacklisted_phrases = [
            # Self-harm terms
            "self harm", "hurt myself", "end my life", "commit suicide", "kill myself",
            # Distress/eating terms
            "want to die", "better off dead", "stop eating", "skip meals"
        ]

    def analyze_content(self, text: str):
        """
        Simple content analysis that returns a compatible result.

        Performs basic phrase matching and returns a result object
        compatible with the enhanced filter interface.

        Args:
            text: Text content to analyze

        Returns:
            SimpleFilterResult: Analysis result object
        """
        result = SimpleFilterResult(text)  # Initialize simple result object

        text_lower = text.lower()  # Convert to lowercase for matching

        # Check each blacklisted phrase
        for phrase in self.blacklisted_phrases:
            if phrase in text_lower:           # Case-insensitive phrase matching
                result.has_violations = True    # Mark violation found
                result.matched_phrases.append(phrase)  # Track matched phrase

        return result  # Return analysis results


class SimpleFilterResult:
    """
    Simple result object that mimics the enhanced version.

    Provides basic compatibility with the enhanced filter's
    result interface while maintaining simplicity.
    """

    def __init__(self, original_text: str):
        """
        Initialize simple filter result.

        Args:
            original_text: The text that was analyzed
        """
        self.original_text = original_text    # Store original text
        # Start with original (no filtering in simple mode)
        self.filtered_text = original_text
        self.has_violations = False           # Flag for violations found
        self.matched_phrases = []             # List of matched harmful phrases

    def get_severity(self):
        """
        Get severity level (simple version based on phrase types).

        Provides basic severity assessment based on the types
        of phrases that were matched.

        Returns:
            str: Severity level as string
        """
        # No violations means no severity
        if not self.has_violations:
            return "NONE"

        # Check for critical phrases indicating immediate danger
        elif any(phrase in ["commit suicide", "kill myself", "end my life"] for phrase in self.matched_phrases):
            return "CRITICAL"  # Highest severity for self-harm terms
        else:
            return "MEDIUM"    # Default severity for other harmful content


# Initialize the filter on module import
initialize_content_filter()  # Set up filter when module is loaded

# Public API functions that maintain compatibility with main.py


def load_blacklist_from_file(filename: str = 'blacklist.txt') -> List[str]:
    """
    Load blacklisted phrases from file - compatibility function.

    Maintains backward compatibility with existing blacklist loading
    functionality while leveraging enhanced filter when available.

    Args:
        filename: Path to blacklist file (default: 'blacklist.txt')

    Returns:
        List[str]: List of blacklisted phrases
    """
    global _content_filter  # Access global filter instance

    # Use enhanced filter's phrase database if available
    if ENHANCED_FILTER_AVAILABLE and hasattr(_content_filter, 'blacklist_phrases'):
        # Extract phrases from enhanced filter's internal database
        return list(_content_filter.blacklist_phrases.keys())
    else:
        # Simple file loading for fallback mode
        phrases = []  # Initialize empty phrases list

        try:
            with open(filename, 'r', encoding='utf-8') as file:  # Open with explicit encoding
                for line in file:
                    line = line.strip()  # Remove whitespace
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        phrases.append(line.lower())  # Add phrase in lowercase

        except FileNotFoundError:
            # Log missing file
            logger.warning(f"Blacklist file {filename} not found")

            # Return default phrases if file not found
            phrases = [
                "self harm", "hurt myself", "end my life", "commit suicide", "kill myself",
                "want to die", "better off dead", "stop eating", "skip meals"
            ]

        return phrases  # Return loaded or default phrases


def contains_blacklisted_content(text: str, blacklist: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if text contains blacklisted content - compatibility function.

    Provides unified interface for checking harmful content regardless
    of whether enhanced or simple filtering is being used.

    Args:
        text: Text to check for violations
        blacklist: List of blacklisted phrases (may be ignored in enhanced mode)

    Returns:
        Tuple[bool, List[str]]: (has_violations, matched_phrases)
    """
    global _content_filter  # Access global filter instance

    # Handle empty input gracefully
    if not text:
        return False, []

    # Use enhanced filtering if available
    if ENHANCED_FILTER_AVAILABLE:
        # Use comprehensive enhanced filtering analysis
        result = _content_filter.analyze_content(text)

        if result.has_violations:
            # Extract matched phrases from enhanced results
            matched_phrases = [match.phrase for match in result.matches]
            return True, matched_phrases  # Return violations found
        return False, []  # No violations found
    else:
        # Simple checking using provided blacklist
        text_lower = text.lower()  # Convert to lowercase for matching
        matched_phrases = []       # Track matched phrases

        # Check each phrase in the blacklist
        for phrase in blacklist:
            if phrase.lower() in text_lower:  # Case-insensitive matching
                matched_phrases.append(phrase)  # Add to matched list

        # Return results based on whether any phrases matched
        return len(matched_phrases) > 0, matched_phrases


def filter_content(text: str, blacklist: List[str] = None, replacement: str = "[content filtered]") -> str:
    """
    Filter blacklisted content from text - compatibility function.

    Applies content filtering with appropriate replacement text,
    using enhanced filtering when available or simple replacement otherwise.

    Args:
        text: Text to filter
        blacklist: List of phrases to filter (may be ignored in enhanced mode)
        replacement: Replacement text for simple mode (default: "[content filtered]")

    Returns:
        str: Filtered text with harmful content replaced
    """
    global _content_filter  # Access global filter instance

    # Handle empty input gracefully
    if not text:
        return text

    # Use enhanced filtering if available
    if ENHANCED_FILTER_AVAILABLE:
        # Use sophisticated filtering with contextual replacements
        result = _content_filter.analyze_content(text)
        return result.filtered_text  # Return professionally filtered text
    else:
        # Simple filtering using string replacement
        filtered_text = text  # Start with original text

        if blacklist:
            # Replace each blacklisted phrase with the replacement text
            for phrase in blacklist:
                filtered_text = filtered_text.replace(phrase, replacement)

        return filtered_text  # Return simply filtered text


def get_safety_disclaimer() -> str:
    """
    Get safety disclaimer text.

    Provides appropriate safety information and contact details
    for users who may be experiencing distress.

    Returns:
        str: Formatted safety disclaimer
    """
    global _content_filter  # Access global filter instance

    # Use enhanced filter's disclaimer if available
    if ENHANCED_FILTER_AVAILABLE and hasattr(_content_filter, '_get_safety_disclaimer'):
        return _content_filter._get_safety_disclaimer()  # Use comprehensive disclaimer
    else:
        # Simple fallback disclaimer
        return (
            "\n\n**Important:** If you're experiencing distress, please seek help:\n"
            "Singapore helplines: SOS 1-767, IMH 6389-2222, National Care Hotline 1800-202-6868"
        )


def get_safe_response_alternative(context: str = "") -> str:
    """
    Get safe alternative response when harmful content is detected.

    Provides constructive redirection with context-appropriate suggestions
    when harmful content needs to be addressed.

    Args:
        context: Context of the harmful content for targeted response

    Returns:
        str: Safe alternative response with support information
    """
    global _content_filter  # Access global filter instance

    # Use enhanced filter's contextual response if available
    if ENHANCED_FILTER_AVAILABLE and hasattr(_content_filter, 'get_safe_response_alternative'):
        # Use sophisticated response
        return _content_filter.get_safe_response_alternative(context)
    else:
        # Simple fallback response
        return (
            "I understand you might be going through a difficult time. "
            "Let's focus on healthy ways to cope with stress and challenges. "
            "Would you like to explore some positive coping strategies? "
            + get_safety_disclaimer()  # Always include safety information
        )

# Additional utility functions for extended functionality


def is_content_critical(text: str) -> bool:
    """
    Check if content contains critical violations requiring immediate attention.

    Identifies content that poses immediate safety concerns and requires
    urgent intervention or response.

    Args:
        text: Text content to analyze

    Returns:
        bool: True if critical violations found, False otherwise
    """
    global _content_filter  # Access global filter instance

    # Use enhanced filter's severity analysis if available
    if ENHANCED_FILTER_AVAILABLE:
        result = _content_filter.analyze_content(
            text)  # Get comprehensive analysis

        if result.has_violations:
            # Check if any matches are critical severity
            for match in result.matches:
                if match.severity.value >= SeverityLevel.CRITICAL.value:
                    return True  # Critical content found
        return False  # No critical content found
    else:
        # Simple check for critical phrases in fallback mode
        critical_phrases = ["commit suicide", "kill myself",
                            "end my life"]  # Most serious phrases
        text_lower = text.lower()  # Convert for case-insensitive matching

        # Check if any critical phrases are present
        return any(phrase in text_lower for phrase in critical_phrases)


def get_filter_report() -> dict:
    """
    Get report about filtering activity and capabilities.

    Provides information about the current filter configuration
    and available features for monitoring and debugging.

    Returns:
        dict: Report containing filter status and capabilities
    """
    global _content_filter  # Access global filter instance

    # Enhanced filter report if available
    if ENHANCED_FILTER_AVAILABLE and hasattr(_content_filter, 'generate_report'):
        # Enhanced version would need to track results, but for compatibility return basic info
        return {
            "filter_type": "enhanced",     # Indicates enhanced filtering active
            "status": "active",            # Current operational status
            # Available features
            "features": ["pattern_matching", "severity_scoring", "context_analysis"]
        }
    else:
        # Simple filter report
        return {
            "filter_type": "simple",       # Indicates simple filtering active
            "status": "active",            # Current operational status
            "features": ["basic_phrase_matching"]  # Available features
        }

# For debugging and testing functionality


def test_filter() -> bool:
    """
    Test that the filter is working correctly.

    Runs basic test cases to verify that the content filter
    is functioning properly and catching harmful content.

    Returns:
        bool: True if all tests pass, False if any test fails
    """
    # Define test cases with expected results
    test_cases = [
        # Safe content should not trigger violations
        ("This is safe content", False),
        # Self-harm content should trigger violations
        ("I want to hurt myself", True),
        # Direct harmful phrase should trigger violations
        ("commit suicide", True)
    ]

    # Run each test case
    for text, expected_violation in test_cases:
        # Check if violations are detected as expected
        has_violation, _ = contains_blacklisted_content(text, [])

        if has_violation != expected_violation:
            # Log test failure with details
            logger.error(f"Filter test failed for: {text}")
            return False  # Return failure immediately

    # All tests passed
    logger.info("Content filter test passed")  # Log successful test completion
    return True  # Return success
