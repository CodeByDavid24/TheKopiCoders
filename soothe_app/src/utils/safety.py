"""
Safety utilities for SootheAI.
Handles content filtering and safety checks.
"""

import logging
import re
from typing import Tuple, List, Optional, Dict, Any

# Set up logger
logger = logging.getLogger(__name__)

# Try to import enhanced content filter
try:
    from src.core.content_filter import (  # Fixed import path
        EnhancedContentFilter,
        ContentFilterResult,
        ContentMatch,
        SeverityLevel
    )
    ENHANCED_FILTER_AVAILABLE = True
    logger.info("Enhanced content filter imported successfully")
except ImportError:
    ENHANCED_FILTER_AVAILABLE = False
    logger.warning(
        "Enhanced content filter not available, using basic filtering")

# Initialize content filter
_content_filter = None


def initialize_content_filter() -> bool:
    """
    Initialize the content filter.

    Returns:
        True if successful, False otherwise
    """
    global _content_filter

    if not ENHANCED_FILTER_AVAILABLE:
        logger.warning(
            "Enhanced content filter not available, cannot initialize")
        return False

    try:
        _content_filter = EnhancedContentFilter()
        logger.info("Content filter initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing content filter: {str(e)}")
        return False


# Try to initialize filter on module load
if ENHANCED_FILTER_AVAILABLE:
    initialize_content_filter()


def check_input_safety(message: str) -> Tuple[bool, str]:
    """
    Check user input for potentially harmful content using enhanced filter.

    Args:
        message: User's input message

    Returns:
        Tuple of (is_safe, safe_message)
    """
    global _content_filter

    if not ENHANCED_FILTER_AVAILABLE or not _content_filter:
        # Fallback to simple check if filter not available
        return _basic_safety_check(message)

    # Use enhanced filter to analyze content
    result = _content_filter.analyze_content(message)

    if result.has_violations:
        # Log detected violations
        logger.warning(
            f"Detected harmful content in user input. Severity: {result.severity_score}")
        categories = ", ".join(result.categories_violated)
        logger.warning(f"Categories violated: {categories}")

        # Determine response based on severity
        max_severity = max(
            (match.severity for match in result.matches), default=SeverityLevel.LOW)

        if max_severity == SeverityLevel.CRITICAL:
            # For critical content, provide strong safety message
            safety_message = (
                "I notice your message contains content about serious safety concerns. "
                "Please know that support is available and you don't have to face these feelings alone. "
                "\n\n**Immediate Support:**\n"
                "- National Care Hotline (Singapore): 1800-202-6868 (24 hours)\n"
                "- Samaritans of Singapore (SOS): 1-767 (24 hours)\n"
                "- Emergency: 999\n\n"
                "In SootheAI, let's explore healthier ways Serena might cope with difficult feelings."
            )
        else:
            # For other violations, use contextual response
            safety_message = _content_filter.get_safe_response_alternative(
                context=message)

        return False, safety_message

    return True, message


def filter_response_safety(response: str) -> str:
    """
    Filter LLM response for safety using enhanced filter.

    Args:
        response: LLM response to filter

    Returns:
        Filtered safe response
    """
    global _content_filter

    if not ENHANCED_FILTER_AVAILABLE or not _content_filter:
        # Fallback to original response if filter not available
        return response

    # Analyze the response for harmful content
    result = _content_filter.analyze_content(response)

    if result.has_violations:
        # Log the violation details
        logger.warning(
            f"Detected harmful content in LLM response. Severity: {result.severity_score}")
        categories = ", ".join(result.categories_violated)
        logger.warning(f"Categories violated: {categories}")

        # Check if any violations are critical
        critical_violations = [
            match for match in result.matches if match.severity == SeverityLevel.CRITICAL]

        if critical_violations:
            # For critical content, replace entirely with safe alternative
            logger.error(
                "Critical content detected in LLM response, replacing entirely")
            return _content_filter.get_safe_response_alternative(context="LLM response contained critical content")
        else:
            # For non-critical violations, use the filtered text
            # The enhanced filter automatically replaces harmful content
            filtered_response = result.filtered_text

            # Add safety notice for high severity content
            high_severity = any(match.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
                                for match in result.matches)
            if high_severity:
                filtered_response += "\n\n" + _get_safety_disclaimer()

            return filtered_response

    return response


def _basic_safety_check(message: str) -> Tuple[bool, str]:
    """
    Basic safety check for when enhanced filter is not available.

    Args:
        message: Message to check

    Returns:
        Tuple of (is_safe, message_or_warning)
    """
    # List of critical harmful patterns
    critical_patterns = [
        r'\b(?:kill|comm?it).{0,20}(?:suicide|myself)\b',
        r'\b(?:end|take).{0,20}(?:my|own).{0,20}life\b',
        r'\bsuicid(?:e|al)\b',
        r'\b(?:hurt|harm|cut|slash).{0,20}(?:myself|arms|wrists)\b',
        r'\bways to d(?:ie|eath)\b'
    ]

    message_lower = message.lower()

    # Check for critical patterns
    for pattern in critical_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            logger.warning(
                f"Basic filter detected potentially harmful content: {pattern}")
            safety_message = (
                "I notice your message contains concerning content. "
                "If you're experiencing difficult thoughts, please reach out for support. "
                "\n\n**Available Resources:**\n"
                "- National Care Hotline (Singapore): 1800-202-6868\n"
                "- Samaritans of Singapore (SOS): 1-767\n"
                "- IMH Mental Health Helpline: 6389-2222\n\n"
                "For the purposes of this story, let's explore healthier approaches."
            )
            return False, safety_message

    return True, message


def _get_safety_disclaimer() -> str:
    """
    Get a standard safety disclaimer.

    Returns:
        Safety disclaimer text
    """
    return (
        "**Safety Notice:** If you're feeling overwhelmed, remember that professional support is available. "
        "Reach out to a trusted adult, school counselor, or contact a helpline like the "
        "National Care Hotline (1800-202-6868) or Samaritans of Singapore (1-767)."
    )


def log_content_analysis_metrics(result: Any, text_type: str) -> None:
    """
    Log detailed metrics about content analysis for monitoring.

    Args:
        result: ContentFilterResult from enhanced filter
        text_type: Type of text analyzed ('user_input' or 'llm_response')
    """
    if not ENHANCED_FILTER_AVAILABLE:
        return

    if not hasattr(result, 'has_violations'):
        logger.warning(
            f"Cannot log metrics for {text_type}: Invalid result object")
        return

    logger.info(f"Content analysis [{text_type}]:")
    logger.info(f"  - Has violations: {result.has_violations}")

    if hasattr(result, 'severity_score'):
        logger.info(f"  - Severity score: {result.severity_score}")

    if hasattr(result, 'processing_time'):
        logger.info(
            f"  - Processing time: {result.processing_time*1000:.2f}ms")

    if hasattr(result, 'categories_violated'):
        logger.info(f"  - Categories violated: {result.categories_violated}")

    if result.has_violations and hasattr(result, 'matches'):
        for match in result.matches:
            logger.debug(
                f"  - Match: {match.phrase} (Severity: {match.severity.name}, Category: {match.category})"
            )
