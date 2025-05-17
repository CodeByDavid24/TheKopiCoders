"""
Compatibility layer for SootheAI blacklist functionality
Provides simple interface to the enhanced content filtering system
"""

from typing import List, Tuple
import logging

# Try to import the enhanced content filter, fall back to simple version if not available
try:
    from soothe_app.src.core.content_filter import EnhancedContentFilter, ContentFilterResult, SeverityLevel
    ENHANCED_FILTER_AVAILABLE = True
except ImportError:
    ENHANCED_FILTER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global filter instance
_content_filter = None


def initialize_content_filter():
    """Initialize the content filter (enhanced or simple)"""
    global _content_filter

    if ENHANCED_FILTER_AVAILABLE:
        _content_filter = EnhancedContentFilter()
        logger.info("Enhanced content filter initialized")
    else:
        _content_filter = SimpleContentFilter()
        logger.info("Simple content filter initialized")


class SimpleContentFilter:
    """Simple fallback content filter if enhanced version is not available"""

    def __init__(self):
        self.blacklisted_phrases = [
            "self harm", "hurt myself", "end my life", "commit suicide", "kill myself",
            "want to die", "better off dead", "stop eating", "skip meals"
        ]

    def analyze_content(self, text: str):
        """Simple content analysis that returns a compatible result"""
        result = SimpleFilterResult(text)

        text_lower = text.lower()
        for phrase in self.blacklisted_phrases:
            if phrase in text_lower:
                result.has_violations = True
                result.matched_phrases.append(phrase)

        return result


class SimpleFilterResult:
    """Simple result object that mimics the enhanced version"""

    def __init__(self, original_text: str):
        self.original_text = original_text
        self.filtered_text = original_text
        self.has_violations = False
        self.matched_phrases = []

    def get_severity(self):
        """Get severity level (simple version just returns based on matches)"""
        if not self.has_violations:
            return "NONE"
        elif any(phrase in ["commit suicide", "kill myself", "end my life"] for phrase in self.matched_phrases):
            return "CRITICAL"
        else:
            return "MEDIUM"


# Initialize the filter on import
initialize_content_filter()

# Public API functions that maintain compatibility with main.py


def load_blacklist_from_file(filename: str = 'blacklist.txt') -> List[str]:
    """
    Load blacklisted phrases from file - compatibility function

    Args:
        filename: Path to blacklist file

    Returns:
        List of blacklisted phrases
    """
    global _content_filter

    if ENHANCED_FILTER_AVAILABLE and hasattr(_content_filter, 'blacklist_phrases'):
        # Extract phrases from enhanced filter
        return list(_content_filter.blacklist_phrases.keys())
    else:
        # Simple file loading
        phrases = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        phrases.append(line.lower())
        except FileNotFoundError:
            logger.warning(f"Blacklist file {filename} not found")
            # Return default phrases
            phrases = [
                "self harm", "hurt myself", "end my life", "commit suicide", "kill myself",
                "want to die", "better off dead", "stop eating", "skip meals"
            ]
        return phrases


def contains_blacklisted_content(text: str, blacklist: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if text contains blacklisted content - compatibility function

    Args:
        text: Text to check
        blacklist: List of blacklisted phrases (may be ignored in enhanced mode)

    Returns:
        Tuple of (has_violations, matched_phrases)
    """
    global _content_filter

    if not text:
        return False, []

    if ENHANCED_FILTER_AVAILABLE:
        # Use enhanced filtering
        result = _content_filter.analyze_content(text)
        if result.has_violations:
            matched_phrases = [match.phrase for match in result.matches]
            return True, matched_phrases
        return False, []
    else:
        # Simple checking
        text_lower = text.lower()
        matched_phrases = []

        for phrase in blacklist:
            if phrase.lower() in text_lower:
                matched_phrases.append(phrase)

        return len(matched_phrases) > 0, matched_phrases


def filter_content(text: str, blacklist: List[str] = None, replacement: str = "[content filtered]") -> str:
    """
    Filter blacklisted content from text - compatibility function

    Args:
        text: Text to filter
        blacklist: List of phrases to filter (may be ignored in enhanced mode)
        replacement: Replacement text

    Returns:
        Filtered text
    """
    global _content_filter

    if not text:
        return text

    if ENHANCED_FILTER_AVAILABLE:
        # Use enhanced filtering
        result = _content_filter.analyze_content(text)
        return result.filtered_text
    else:
        # Simple filtering
        filtered_text = text
        if blacklist:
            for phrase in blacklist:
                filtered_text = filtered_text.replace(phrase, replacement)
        return filtered_text


def get_safety_disclaimer() -> str:
    """Get safety disclaimer text"""
    global _content_filter

    if ENHANCED_FILTER_AVAILABLE and hasattr(_content_filter, '_get_safety_disclaimer'):
        return _content_filter._get_safety_disclaimer()
    else:
        return (
            "\n\n**Important:** If you're experiencing distress, please seek help:\n"
            "Singapore helplines: SOS 1-767, IMH 6389-2222, National Care Hotline 1800-202-6868"
        )


def get_safe_response_alternative(context: str = "") -> str:
    """Get safe alternative response"""
    global _content_filter

    if ENHANCED_FILTER_AVAILABLE and hasattr(_content_filter, 'get_safe_response_alternative'):
        return _content_filter.get_safe_response_alternative(context)
    else:
        return (
            "I understand you might be going through a difficult time. "
            "Let's focus on healthy ways to cope with stress and challenges. "
            "Would you like to explore some positive coping strategies? "
            + get_safety_disclaimer()
        )

# Additional utility functions


def is_content_critical(text: str) -> bool:
    """Check if content contains critical violations"""
    global _content_filter

    if ENHANCED_FILTER_AVAILABLE:
        result = _content_filter.analyze_content(text)
        if result.has_violations:
            for match in result.matches:
                if match.severity.value >= SeverityLevel.CRITICAL.value:
                    return True
        return False
    else:
        # Simple check for critical phrases
        critical_phrases = ["commit suicide", "kill myself", "end my life"]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in critical_phrases)


def get_filter_report() -> dict:
    """Get report about filtering activity"""
    global _content_filter

    if ENHANCED_FILTER_AVAILABLE and hasattr(_content_filter, 'generate_report'):
        # Enhanced version would need to track results, but for compatibility just return basic info
        return {
            "filter_type": "enhanced",
            "status": "active",
            "features": ["pattern_matching", "severity_scoring", "context_analysis"]
        }
    else:
        return {
            "filter_type": "simple",
            "status": "active",
            "features": ["basic_phrase_matching"]
        }

# For debugging and testing


def test_filter() -> bool:
    """Test that the filter is working correctly"""
    test_cases = [
        ("This is safe content", False),
        ("I want to hurt myself", True),
        ("commit suicide", True)
    ]

    for text, expected_violation in test_cases:
        has_violation, _ = contains_blacklisted_content(text, [])
        if has_violation != expected_violation:
            logger.error(f"Filter test failed for: {text}")
            return False

    logger.info("Content filter test passed")
    return True
