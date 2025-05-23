"""
Utils for working with the speech synthesis audit trail.

This module provides simplified access to speech audit functions
for other parts of the application.
"""

import logging  # For application logging
# Type hints for better code documentation
from typing import Dict, Optional, List

# Import the audit trail components
from ..ui.speech_audit_trail import get_audit_trail, generate_tts_audit_report

# Set up logger for this module
logger = logging.getLogger(__name__)


def log_tts_event(text: str, category: str = "narrative",
                  successful: bool = True, metadata: Optional[Dict] = None) -> Dict:
    """
    Log a TTS event to the audit trail with simplified interface.

    Args:
        text: Text that was synthesized
        category: Category of content (narrative, dialogue, etc.)
        successful: Whether synthesis was successful
        metadata: Additional metadata about the synthesis

    Returns:
        Dict: Log entry that was created

    Example:
        >>> entry = log_tts_event("Hello, this is Serena speaking.", "dialogue", True)
        >>> print(f"Logged synthesis with ID: {entry['synthesis_id']}")
    """
    audit_trail = get_audit_trail()  # Get singleton audit trail instance
    return audit_trail.log_synthesis(  # Log synthesis event with details
        text=text,  # Text content that was synthesized
        category=category,  # Content category for analytics
        was_successful=successful,  # Success/failure status
        metadata=metadata  # Additional context information
    )


def log_tts_error(text: str, error: str, category: str = "narrative") -> Dict:
    """
    Log a TTS error to the audit trail for troubleshooting.

    Args:
        text: Text that failed to synthesize
        error: Error message describing the failure
        category: Category of content that failed

    Returns:
        Dict: Log entry that was created

    Example:
        >>> entry = log_tts_error("Failed text", "API timeout", "narrative")
        >>> print(f"Logged error: {entry['synthesis_id']}")
    """
    audit_trail = get_audit_trail()  # Get singleton audit trail instance
    return audit_trail.log_synthesis_error(  # Log synthesis error with details
        text=text,  # Text that failed to synthesize
        error_message=error,  # Error description
        category=category  # Content category for analysis
    )


def get_tts_statistics() -> Dict:
    """
    Get current TTS usage statistics for monitoring.

    Returns:
        Dict: Current TTS statistics including session data

    Example:
        >>> stats = get_tts_statistics()
        >>> print(f"Total synthesis events: {stats['total_synthesis_count']}")
    """
    audit_trail = get_audit_trail()  # Get singleton audit trail instance
    return audit_trail.get_session_statistics()  # Return current session statistics


def create_tts_report(days: int = 7) -> Dict:
    """
    Create a comprehensive report of TTS usage over specified period.

    Args:
        days: Number of days to include in report (default: 7)

    Returns:
        Dict: TTS usage report with detailed analytics

    Example:
        >>> report = create_tts_report(30)  # Last 30 days
        >>> print(f"Total sessions: {report['total_sessions']}")
    """
    return generate_tts_audit_report(days)  # Generate report for specified period


def format_tts_report_for_display(report: Dict) -> str:
    """
    Format a TTS report for user-friendly display.

    Args:
        report: TTS report from create_tts_report function

    Returns:
        str: Formatted report text ready for display

    Example:
        >>> report = create_tts_report(7)
        >>> formatted = format_tts_report_for_display(report)
        >>> print(formatted)
    """
    # Handle case where no audit data exists
    if "status" in report and "No audit log found" in report["status"]:
        return "No TTS audit data available yet."  # User-friendly no data message

    # Build formatted report with sections
    lines = [
        "## TTS Usage Report",  # Report title
        # Time period covered
        f"Period: Last {report.get('period_days', 7)} days",
        # Number of sessions
        f"Total sessions: {report.get('total_sessions', 0)}",
        # Total TTS events
        f"Total synthesis events: {report.get('total_synthesis_events', 0)}",
        # Total character count
        f"Characters synthesized: {report.get('total_chars_synthesized', 0)}",
        "",  # Empty line for spacing
        "### Usage by category:",  # Category breakdown section
    ]

    # Add category breakdown with counts
    categories = report.get('synthesis_by_category', {})  # Get category data
    for category, count in categories.items():  # Iterate through categories
        lines.append(f"- {category}: {count} events")  # Add category line

    # Add session details section
    lines.extend([
        "",  # Empty line for spacing
        "### Recent sessions:",  # Recent sessions section header
    ])

    # Add details for recent sessions (last 5)
    sessions = report.get('sessions', [])  # Get session data
    for session in sessions[-5:]:  # Show only 5 most recent sessions
        start_time = session.get('date', 'Unknown')  # Get session start time
        summary = session.get('summary', {})  # Get session summary

        if summary:  # Only add if summary data exists
            lines.append(f"- Session {start_time}: {summary.get('total_synthesis_count', 0)} events, " +
                         f"{summary.get('total_chars_synthesized', 0)} chars")  # Session summary line

    return "\n".join(lines)  # Join all lines with newlines


def end_tts_session() -> Dict:
    """
    End the current TTS session and log final statistics.

    Returns:
        Dict: Session end log entry with summary

    Example:
        >>> session_summary = end_tts_session()
        >>> print(f"Session ended: {session_summary['session_id']}")
    """
    audit_trail = get_audit_trail()  # Get singleton audit trail instance
    return audit_trail.log_session_end()  # Log session end with summary statistics
