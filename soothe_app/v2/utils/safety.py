"""
Safety utilities for SootheAI.
Handles content filtering and safety checks.
"""

import logging  # For application logging
import re  # For regular expression pattern matching
# Type hints for better code documentation
from typing import Tuple, List, Optional, Dict, Any

# Set up logger for this module
logger = logging.getLogger(__name__)

# Try to import enhanced content filter with graceful fallback
try:
    from v2.core.content_filter import (  # Import enhanced content filtering components
        EnhancedContentFilter,  # Main content filter class
        ContentFilterResult,    # Result object from content analysis
        ContentMatch,          # Individual content match details
        SeverityLevel          # Severity levels for content violations
    )
    ENHANCED_FILTER_AVAILABLE = True  # Flag indicating enhanced filter is available
    # Log successful import
    logger.info("Enhanced content filter imported successfully")
except ImportError:
    ENHANCED_FILTER_AVAILABLE = False  # Enhanced filter not available
    logger.warning(
        "Enhanced content filter not available, using basic filtering")  # Log fallback to basic filtering

# Initialize content filter instance
_content_filter = None


def initialize_content_filter() -> bool:
    """
    Initialize the content filter with error handling.

    Returns:
        bool: True if successful, False otherwise

    Example:
        >>> success = initialize_content_filter()
        >>> if success:
        ...     print("Content filter ready")
    """
    global _content_filter

    if not ENHANCED_FILTER_AVAILABLE:  # Check if enhanced filter is available
        logger.warning(
            "Enhanced content filter not available, cannot initialize")  # Log unavailability
        return False  # Return failure if enhanced filter not available

    try:
        _content_filter = EnhancedContentFilter()  # Initialize enhanced content filter
        # Log successful initialization
        logger.info("Content filter initialized successfully")
        return True  # Return success
    except Exception as e:
        # Log initialization error
        logger.error(f"Error initializing content filter: {str(e)}")
        return False  # Return failure on exception


# Try to initialize filter on module load
if ENHANCED_FILTER_AVAILABLE:  # Only attempt if enhanced filter is available
    initialize_content_filter()  # Initialize content filter automatically


def check_input_safety(message: str) -> Tuple[bool, str]:
    """
    Check user input for potentially harmful content using enhanced filter.

    Args:
        message: User's input message to analyze

    Returns:
        Tuple[bool, str]: (is_safe, safe_message_or_warning)

    Example:
        >>> is_safe, response = check_input_safety("I want to hurt myself")
        >>> if not is_safe:
        ...     print("Harmful content detected")
    """
    global _content_filter

    if not ENHANCED_FILTER_AVAILABLE or not _content_filter:  # Check filter availability
        # Fallback to simple check if filter not available
        return _basic_safety_check(message)

    # Use enhanced filter to analyze content for safety violations
    result = _content_filter.analyze_content(message)

    if result.has_violations:  # Check if any safety violations were detected
        # Log detected violations for monitoring
        logger.warning(
            f"Detected harmful content in user input. Severity: {result.severity_score}")
        # Join violation categories
        categories = ", ".join(result.categories_violated)
        # Log specific categories
        logger.warning(f"Categories violated: {categories}")

        # Determine response based on severity level
        max_severity = max(
            (match.severity for match in result.matches), default=SeverityLevel.LOW)  # Find highest severity

        if max_severity == SeverityLevel.CRITICAL:  # Handle critical content
            # For critical content, provide strong safety message with resources
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
            # For other violations, use contextual response from filter
            safety_message = _content_filter.get_safe_response_alternative(
                context=message)  # Get contextually appropriate safe response

        return False, safety_message  # Return unsafe with safety message

    return True, message  # Return safe with original message


def filter_response_safety(response: str) -> str:
    """
    Filter LLM response for safety using enhanced filter.

    Args:
        response: LLM response to filter for safety

    Returns:
        str: Filtered safe response

    Example:
        >>> safe_response = filter_response_safety(llm_output)
        >>> print(safe_response)  # Guaranteed to be safe
    """
    global _content_filter

    if not ENHANCED_FILTER_AVAILABLE or not _content_filter:  # Check filter availability
        # Fallback to original response if filter not available
        return response

    # Analyze the response for harmful content
    result = _content_filter.analyze_content(response)

    if result.has_violations:  # Check if violations detected in response
        # Log the violation details for monitoring
        logger.warning(
            f"Detected harmful content in LLM response. Severity: {result.severity_score}")
        # Join violation categories
        categories = ", ".join(result.categories_violated)
        # Log specific categories
        logger.warning(f"Categories violated: {categories}")

        # Check if any violations are critical level
        critical_violations = [
            match for match in result.matches if match.severity == SeverityLevel.CRITICAL]

        if critical_violations:  # Handle critical content in LLM response
            # For critical content, replace entirely with safe alternative
            logger.error(
                "Critical content detected in LLM response, replacing entirely")  # Log critical replacement
            return _content_filter.get_safe_response_alternative(context="LLM response contained critical content")
        else:
            # For non-critical violations, use the filtered text
            # The enhanced filter automatically replaces harmful content
            filtered_response = result.filtered_text

            # Add safety notice for high severity content
            high_severity = any(match.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
                                for match in result.matches)  # Check for high severity violations
            if high_severity:
                filtered_response += "\n\n" + _get_safety_disclaimer()  # Append safety disclaimer

            return filtered_response  # Return filtered response

    return response  # Return original response if no violations


def _basic_safety_check(message: str) -> Tuple[bool, str]:
    """
    Basic safety check for when enhanced filter is not available.

    Args:
        message: Message to check for harmful patterns

    Returns:
        Tuple[bool, str]: (is_safe, message_or_warning)

    Example:
        >>> is_safe, response = _basic_safety_check("I want to end my life")
        >>> print(f"Safe: {is_safe}")  # Safe: False
    """
    # List of critical harmful patterns using regex
    critical_patterns = [
        # Suicide ideation patterns
        r'\b(?:kill|comm?it).{0,20}(?:suicide|myself)\b',
        # Life-ending expressions
        r'\b(?:end|take).{0,20}(?:my|own).{0,20}life\b',
        # Direct suicide references
        r'\bsuicid(?:e|al)\b',
        # Self-harm patterns
        r'\b(?:hurt|harm|cut|slash).{0,20}(?:myself|arms|wrists)\b',
        # Death method seeking
        r'\bways to d(?:ie|eath)\b'
    ]

    # Convert to lowercase for case-insensitive matching
    message_lower = message.lower()

    # Check for critical patterns using regex
    for pattern in critical_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):  # Case-insensitive pattern search
            logger.warning(
                f"Basic filter detected potentially harmful content: {pattern}")  # Log pattern match
            # Provide comprehensive safety message with resources
            safety_message = (
                "I notice your message contains concerning content. "
                "If you're experiencing difficult thoughts, please reach out for support. "
                "\n\n**Available Resources:**\n"
                "- National Care Hotline (Singapore): 1800-202-6868\n"
                "- Samaritans of Singapore (SOS): 1-767\n"
                "- IMH Mental Health Helpline: 6389-2222\n\n"
                "For the purposes of this story, let's explore healthier approaches."
            )
            return False, safety_message  # Return unsafe with safety resources

    return True, message  # Return safe with original message


def _get_safety_disclaimer() -> str:
    """
    Get a standard safety disclaimer for appending to filtered content.

    Returns:
        str: Standard safety disclaimer text

    Example:
        >>> disclaimer = _get_safety_disclaimer()
        >>> filtered_content += disclaimer
    """
    return (
        "**Safety Notice:** If you're feeling overwhelmed, remember that professional support is available. "
        "Reach out to a trusted adult, school counselor, or contact a helpline like the "
        "National Care Hotline (1800-202-6868) or Samaritans of Singapore (1-767)."
    )


def log_content_analysis_metrics(result: Any, text_type: str) -> None:
    """
    Log detailed metrics about content analysis for monitoring and debugging.

    Args:
        result: ContentFilterResult from enhanced filter analysis
        text_type: Type of text analyzed ('user_input' or 'llm_response')

    Example:
        >>> log_content_analysis_metrics(filter_result, 'user_input')
        >>> # Logs detailed analysis metrics to application logs
    """
    if not ENHANCED_FILTER_AVAILABLE:  # Skip if enhanced filter not available
        return

    if not hasattr(result, 'has_violations'):  # Validate result object
        logger.warning(
            f"Cannot log metrics for {text_type}: Invalid result object")  # Log invalid result
        return

    # Log comprehensive analysis metrics
    logger.info(f"Content analysis [{text_type}]:")  # Log analysis type
    # Log violation status
    logger.info(f"  - Has violations: {result.has_violations}")

    if hasattr(result, 'severity_score'):  # Log severity if available
        logger.info(f"  - Severity score: {result.severity_score}")

    if hasattr(result, 'processing_time'):  # Log processing performance if available
        logger.info(
            f"  - Processing time: {result.processing_time*1000:.2f}ms")

    if hasattr(result, 'categories_violated'):  # Log violated categories if available
        logger.info(f"  - Categories violated: {result.categories_violated}")

    # Log detailed match information for debugging
    if result.has_violations and hasattr(result, 'matches'):
        for match in result.matches:  # Iterate through individual matches
            logger.debug(
                f"  - Match: {match.phrase} (Severity: {match.severity.name}, Category: {match.category})"
            )
