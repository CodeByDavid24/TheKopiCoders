"""
Speech synthesis audit trail for SootheAI.
Provides accountability and logging for TTS operations.
"""

import hashlib  # For creating content hashes to protect privacy
import json  # For JSON serialization of log entries
import time  # For timestamps and session duration tracking
import os  # For file system operations
import logging  # For application logging
from datetime import datetime  # For human-readable date formatting
# Type hints for better code documentation
from typing import Dict, Optional, List, Any

# Set up logger for this module
logger = logging.getLogger(__name__)


class SpeechSynthesisAuditTrail:
    """
    Creates an accountability system for tracking Text-to-Speech usage
    while preserving privacy and providing valuable analytics.
    """

    def __init__(self, log_file_path: str = "logs/tts_audit_log.jsonl"):
        """
        Initialize the audit trail with logging configuration.

        Args:
            log_file_path: Path to the JSONL audit log file
        """
        self.log_file_path = log_file_path  # Store path to audit log file
        # Generate unique session identifier
        self.session_id = self._generate_session_id()
        self.synthesis_count = 0  # Counter for synthesis events in this session
        self.session_start_time = time.time()  # Record session start timestamp
        self.total_chars_synthesized = 0  # Track total characters processed
        # Track synthesis by category (narrative, dialogue, etc.)
        self.synthesis_categories = {}

        # Ensure log directory exists
        # Extract directory from file path
        log_dir = os.path.dirname(log_file_path)
        # Check if directory needs creation
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)  # Create directory recursively

        # Initialize log file with session start if it doesn't exist
        self._log_session_start()

        # Log initialization
        logger.info(
            f"Speech synthesis audit trail initialized with session ID: {self.session_id}")

    def _generate_session_id(self) -> str:
        """
        Generate a unique session ID based on timestamp and random value.

        Returns:
            str: Unique session identifier in format "ses_timestamp_randomhex"
        """
        timestamp = int(time.time())  # Get current Unix timestamp
        # Generate 4 random bytes as hex string
        random_val = os.urandom(4).hex()
        # Combine into unique session ID
        return f"ses_{timestamp}_{random_val}"

    def _log_session_start(self):
        """Log the start of a new TTS session with metadata."""
        entry = {
            "timestamp": time.time(),  # Unix timestamp for precise timing
            "event_type": "session_start",  # Categorize as session start event
            "session_id": self.session_id,  # Associate with current session
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Human-readable timestamp
        }

        self._write_log_entry(entry)  # Write session start to audit log

    def log_synthesis(self, text: str, category: str = "narrative",
                      was_successful: bool = True, metadata: Optional[Dict] = None) -> Dict:
        """
        Log a speech synthesis event with privacy-preserving measures.

        Args:
            text: The text that was synthesized
            category: The category of synthesis (narrative, dialogue, etc.)
            was_successful: Whether the synthesis was successful
            metadata: Additional metadata about the synthesis

        Returns:
            Dict: The log entry that was created
        """
        # Increment synthesis count for this session
        self.synthesis_count += 1

        # Update category counts for analytics
        self.synthesis_categories[category] = self.synthesis_categories.get(
            category, 0) + 1

        # Update total characters synthesized in this session
        self.total_chars_synthesized += len(text)

        # Create hash of content for privacy while maintaining traceability
        content_hash = hashlib.sha256(text.encode()).hexdigest()

        # Prepare log entry with comprehensive metadata
        timestamp = time.time()  # Record exact synthesis time
        entry = {
            "timestamp": timestamp,  # Unix timestamp for precise timing
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Human-readable date
            "session_id": self.session_id,  # Associate with current session
            "event_type": "synthesis",  # Categorize as synthesis event
            # Unique synthesis ID
            "synthesis_id": f"syn_{self.session_id}_{self.synthesis_count}",
            "content_hash": content_hash,  # SHA256 hash for privacy-preserving identification
            # Track text length for usage analytics
            "content_length": len(text),
            "category": category,  # Content category for analysis
            "successful": was_successful,  # Track success/failure rates
            # Include a small preview for context without revealing full content
            "content_preview": text[:30] + "..." if len(text) > 30 else text,
        }

        # Add optional metadata if provided (voice settings, model info, etc.)
        if metadata:
            entry["metadata"] = metadata

        # Write to log file
        self._write_log_entry(entry)

        # Log the event for application monitoring
        logger.info(
            f"Logged speech synthesis: ID={entry['synthesis_id']}, Length={len(text)}, Category={category}")

        return entry  # Return log entry for caller reference

    def log_synthesis_error(self, text: str, error_message: str, category: str = "narrative"):
        """
        Log a failed speech synthesis attempt.

        Args:
            text: Text that failed to synthesize
            error_message: Description of the error that occurred
            category: Content category for analysis

        Returns:
            Dict: Log entry that was created
        """
        entry = self.log_synthesis(
            text=text,  # Text that failed
            category=category,  # Content category
            was_successful=False,  # Mark as failed
            metadata={"error_message": error_message}  # Include error details
        )
        # Log warning with truncated error
        logger.warning(f"Logged speech synthesis error: {error_message[:100]}")
        return entry

    def log_session_end(self):
        """Log the end of the TTS session with summary statistics."""
        session_duration = time.time() - self.session_start_time  # Calculate total session time

        entry = {
            "timestamp": time.time(),  # Current timestamp
            "event_type": "session_end",  # Categorize as session end event
            "session_id": self.session_id,  # Associate with current session
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Human-readable timestamp
            "session_summary": {  # Comprehensive session statistics
                "total_synthesis_count": self.synthesis_count,  # Total synthesis events
                "total_chars_synthesized": self.total_chars_synthesized,  # Total characters processed
                "session_duration_seconds": session_duration,  # Session length in seconds
                "synthesis_categories": self.synthesis_categories  # Breakdown by content category
            }
        }

        self._write_log_entry(entry)  # Write session end to audit log
        logger.info(
            f"Logged end of speech synthesis session: {self.session_id}")  # Log session completion

        return entry

    def _write_log_entry(self, entry: Dict):
        """
        Write a log entry to the audit log file in JSONL format.

        Args:
            entry: Dictionary containing log entry data
        """
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:  # Open file in append mode
                # Write JSON entry followed by newline
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(
                f"Error writing to speech synthesis audit log: {str(e)}")  # Log file write errors

    def get_session_statistics(self) -> Dict:
        """
        Get statistics for the current session.

        Returns:
            Dict: Current session statistics including duration and usage metrics
        """
        session_duration = time.time(
        ) - self.session_start_time  # Calculate current session duration

        return {
            "session_id": self.session_id,  # Current session identifier
            "session_duration_seconds": session_duration,  # Time since session start
            "total_synthesis_count": self.synthesis_count,  # Number of synthesis events
            "total_chars_synthesized": self.total_chars_synthesized,  # Total characters processed
            # Average text length
            "average_length": (self.total_chars_synthesized / self.synthesis_count) if self.synthesis_count > 0 else 0,
            "synthesis_categories": self.synthesis_categories  # Category breakdown
        }

    @staticmethod
    def extract_audit_report(log_file_path: str = "logs/tts_audit_log.jsonl",
                             days: int = 7) -> Dict:
        """
        Extract an audit report from the log file for specified time period.

        Args:
            log_file_path: Path to the audit log file
            days: Number of days to include in the report

        Returns:
            Dict: Comprehensive audit report with usage statistics
        """
        if not os.path.exists(log_file_path):  # Check if log file exists
            return {"status": "No audit log found"}

        # Calculate cutoff time for report period
        cutoff_time = time.time() - (days * 24 * 60 * 60)  # Convert days to seconds

        # Initialize data collectors
        sessions = {}  # Track individual sessions
        synthesis_events = []  # Collect all synthesis events
        total_chars = 0  # Total characters across all sessions
        categories = {}  # Category usage breakdown

        try:
            with open(log_file_path, "r", encoding="utf-8") as f:  # Open log file for reading
                for line in f:  # Process each line (JSONL format)
                    try:
                        entry = json.loads(line.strip())  # Parse JSON entry

                        # Skip entries older than cutoff time
                        if entry.get("timestamp", 0) < cutoff_time:
                            continue

                        # Track session start events
                        if entry.get("event_type") == "session_start":
                            sessions[entry.get("session_id")] = {
                                # Session start timestamp
                                "start_time": entry.get("timestamp"),
                                # Human-readable start date
                                "date": entry.get("date")
                            }

                        # Track synthesis events for analysis
                        if entry.get("event_type") == "synthesis":
                            synthesis_events.append({
                                # Associate with session
                                "session_id": entry.get("session_id"),
                                # Event timestamp
                                "timestamp": entry.get("timestamp"),
                                # Text length
                                "length": entry.get("content_length"),
                                # Content category
                                "category": entry.get("category"),
                                # Success status
                                "successful": entry.get("successful", True)
                            })

                            # Update statistics for successful synthesis
                            if entry.get("successful", True):
                                # Add to character count
                                total_chars += entry.get("content_length", 0)
                                # Get category or default
                                category = entry.get("category", "unknown")
                                categories[category] = categories.get(
                                    category, 0) + 1  # Increment category counter

                        # Update session end information
                        if entry.get("event_type") == "session_end":
                            if entry.get("session_id") in sessions:  # Find matching session
                                sessions[entry.get("session_id")]["end_time"] = entry.get(
                                    "timestamp")  # Record end time
                                sessions[entry.get("session_id")]["summary"] = entry.get(
                                    "session_summary", {})  # Store session summary

                    except json.JSONDecodeError:
                        continue  # Skip malformed JSON lines

            # Generate comprehensive report
            report = {
                "period_days": days,  # Report time period
                "total_sessions": len(sessions),  # Number of sessions
                # Total synthesis events
                "total_synthesis_events": len(synthesis_events),
                "total_chars_synthesized": total_chars,  # Total characters processed
                "synthesis_by_category": categories,  # Usage breakdown by category
                # Detailed session information
                "sessions": list(sessions.values())
            }

            return report

        except Exception as e:
            # Return error information
            return {"status": "Error generating report", "error": str(e)}


# Singleton instance for global access
_audit_trail = None


def get_audit_trail() -> SpeechSynthesisAuditTrail:
    """
    Get a singleton audit trail instance for application-wide use.

    Returns:
        SpeechSynthesisAuditTrail: Singleton audit trail instance
    """
    global _audit_trail
    if _audit_trail is None:  # Create instance if not exists
        _audit_trail = SpeechSynthesisAuditTrail()
    return _audit_trail


def generate_tts_audit_report(days: int = 7) -> Dict:
    """
    Generate a report of TTS usage for specified time period.

    Args:
        days: Number of days to include in report (default: 7)

    Returns:
        Dict: Comprehensive audit report with usage statistics
    """
    audit_trail = get_audit_trail()  # Get singleton audit trail instance

    report = SpeechSynthesisAuditTrail.extract_audit_report(
        log_file_path=audit_trail.log_file_path,  # Use current audit trail log path
        days=days  # Specify report period
    )

    # Log report generation
    logger.info(f"Generated TTS audit report covering {days} days")

    return report
