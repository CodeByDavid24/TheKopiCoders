"""
Utils for working with the speech synthesis audit trail.

This module provides simplified access to speech audit functions
for other parts of the application.
"""

import logging
from typing import Dict, Optional, List

# Import the audit trail
from ..ui.speech_audit_trail import get_audit_trail, generate_tts_audit_report

# Set up logger
logger = logging.getLogger(__name__)


def log_tts_event(text: str, category: str = "narrative",
                  successful: bool = True, metadata: Optional[Dict] = None) -> Dict:
    """
    Log a TTS event to the audit trail.

    Args:
        text: Text that was synthesized
        category: Category of content (narrative, dialogue, etc.)
        successful: Whether synthesis was successful
        metadata: Additional metadata

    Returns:
        Dict: Log entry that was created
    """
    audit_trail = get_audit_trail()
    return audit_trail.log_synthesis(
        text=text,
        category=category,
        was_successful=successful,
        metadata=metadata
    )


def log_tts_error(text: str, error: str, category: str = "narrative") -> Dict:
    """
    Log a TTS error to the audit trail.

    Args:
        text: Text that failed to synthesize
        error: Error message
        category: Category of content

    Returns:
        Dict: Log entry that was created
    """
    audit_trail = get_audit_trail()
    return audit_trail.log_synthesis_error(
        text=text,
        error_message=error,
        category=category
    )


def get_tts_statistics() -> Dict:
    """
    Get current TTS usage statistics.

    Returns:
        Dict: Current TTS statistics
    """
    audit_trail = get_audit_trail()
    return audit_trail.get_session_statistics()


def create_tts_report(days: int = 7) -> Dict:
    """
    Create a report of TTS usage.

    Args:
        days: Number of days to include in report

    Returns:
        Dict: TTS usage report
    """
    return generate_tts_audit_report(days)


def format_tts_report_for_display(report: Dict) -> str:
    """
    Format a TTS report for display to the user.

    Args:
        report: TTS report from create_tts_report

    Returns:
        str: Formatted report text
    """
    if "status" in report and "No audit log found" in report["status"]:
        return "No TTS audit data available yet."

    lines = [
        "## TTS Usage Report",
        f"Period: Last {report.get('period_days', 7)} days",
        f"Total sessions: {report.get('total_sessions', 0)}",
        f"Total synthesis events: {report.get('total_synthesis_events', 0)}",
        f"Characters synthesized: {report.get('total_chars_synthesized', 0)}",
        "",
        "### Usage by category:",
    ]

    # Add category breakdown
    categories = report.get('synthesis_by_category', {})
    for category, count in categories.items():
        lines.append(f"- {category}: {count} events")

    # Add session details
    lines.extend([
        "",
        "### Recent sessions:",
    ])

    sessions = report.get('sessions', [])
    for session in sessions[-5:]:  # Show only 5 most recent
        start_time = session.get('date', 'Unknown')
        summary = session.get('summary', {})

        if summary:
            lines.append(f"- Session {start_time}: {summary.get('total_synthesis_count', 0)} events, " +
                         f"{summary.get('total_chars_synthesized', 0)} chars")

    return "\n".join(lines)


def end_tts_session() -> Dict:
    """
    End the current TTS session and log statistics.

    Returns:
        Dict: Session end log entry
    """
    audit_trail = get_audit_trail()
    return audit_trail.log_session_end()
