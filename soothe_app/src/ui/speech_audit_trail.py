"""
Speech synthesis audit trail for SootheAI.
Provides accountability and logging for TTS operations.
"""

import hashlib
import json
import time
import os
import logging
from datetime import datetime
from typing import Dict, Optional, List, Any

# Set up logger
logger = logging.getLogger(__name__)


class SpeechSynthesisAuditTrail:
    """
    Creates an accountability system for tracking Text-to-Speech usage
    while preserving privacy and providing valuable analytics.
    """

    def __init__(self, log_file_path: str = "logs/tts_audit_log.jsonl"):
        """
        Initialize the audit trail.

        Args:
            log_file_path: Path to the log file
        """
        self.log_file_path = log_file_path
        self.session_id = self._generate_session_id()
        self.synthesis_count = 0
        self.session_start_time = time.time()
        self.total_chars_synthesized = 0
        self.synthesis_categories = {}

        # Ensure log directory exists
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Initialize log file with session start if it doesn't exist
        self._log_session_start()

        # Log initialization
        logger.info(
            f"Speech synthesis audit trail initialized with session ID: {self.session_id}")

    def _generate_session_id(self) -> str:
        """Generate a unique session ID based on timestamp and random value."""
        timestamp = int(time.time())
        random_val = os.urandom(4).hex()
        return f"ses_{timestamp}_{random_val}"

    def _log_session_start(self):
        """Log the start of a new TTS session."""
        entry = {
            "timestamp": time.time(),
            "event_type": "session_start",
            "session_id": self.session_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self._write_log_entry(entry)

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
        # Increment synthesis count
        self.synthesis_count += 1

        # Update category counts
        self.synthesis_categories[category] = self.synthesis_categories.get(
            category, 0) + 1

        # Update total characters synthesized
        self.total_chars_synthesized += len(text)

        # Create hash of content for privacy while maintaining traceability
        content_hash = hashlib.sha256(text.encode()).hexdigest()

        # Prepare log entry
        timestamp = time.time()
        entry = {
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": self.session_id,
            "event_type": "synthesis",
            "synthesis_id": f"syn_{self.session_id}_{self.synthesis_count}",
            "content_hash": content_hash,
            "content_length": len(text),
            "category": category,
            "successful": was_successful,
            # Include a small preview for context without revealing full content
            "content_preview": text[:30] + "..." if len(text) > 30 else text,
        }

        # Add optional metadata if provided
        if metadata:
            entry["metadata"] = metadata

        # Write to log file
        self._write_log_entry(entry)

        # Log the event
        logger.info(
            f"Logged speech synthesis: ID={entry['synthesis_id']}, Length={len(text)}, Category={category}")

        return entry

    def log_synthesis_error(self, text: str, error_message: str, category: str = "narrative"):
        """Log a failed speech synthesis attempt."""
        entry = self.log_synthesis(
            text=text,
            category=category,
            was_successful=False,
            metadata={"error_message": error_message}
        )
        logger.warning(f"Logged speech synthesis error: {error_message[:100]}")
        return entry

    def log_session_end(self):
        """Log the end of the TTS session with summary statistics."""
        session_duration = time.time() - self.session_start_time

        entry = {
            "timestamp": time.time(),
            "event_type": "session_end",
            "session_id": self.session_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_summary": {
                "total_synthesis_count": self.synthesis_count,
                "total_chars_synthesized": self.total_chars_synthesized,
                "session_duration_seconds": session_duration,
                "synthesis_categories": self.synthesis_categories
            }
        }

        self._write_log_entry(entry)
        logger.info(
            f"Logged end of speech synthesis session: {self.session_id}")

        return entry

    def _write_log_entry(self, entry: Dict):
        """Write a log entry to the audit log file."""
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(
                f"Error writing to speech synthesis audit log: {str(e)}")

    def get_session_statistics(self) -> Dict:
        """Get statistics for the current session."""
        session_duration = time.time() - self.session_start_time

        return {
            "session_id": self.session_id,
            "session_duration_seconds": session_duration,
            "total_synthesis_count": self.synthesis_count,
            "total_chars_synthesized": self.total_chars_synthesized,
            "average_length": (self.total_chars_synthesized / self.synthesis_count) if self.synthesis_count > 0 else 0,
            "synthesis_categories": self.synthesis_categories
        }

    @staticmethod
    def extract_audit_report(log_file_path: str = "logs/tts_audit_log.jsonl",
                             days: int = 7) -> Dict:
        """
        Extract an audit report from the log file.

        Args:
            log_file_path: Path to the log file
            days: Number of days to include in the report

        Returns:
            Dict: Audit report
        """
        if not os.path.exists(log_file_path):
            return {"status": "No audit log found"}

        # Calculate cutoff time
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        sessions = {}
        synthesis_events = []
        total_chars = 0
        categories = {}

        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())

                        # Skip entries older than cutoff
                        if entry.get("timestamp", 0) < cutoff_time:
                            continue

                        # Track sessions
                        if entry.get("event_type") == "session_start":
                            sessions[entry.get("session_id")] = {
                                "start_time": entry.get("timestamp"),
                                "date": entry.get("date")
                            }

                        # Track synthesis events
                        if entry.get("event_type") == "synthesis":
                            synthesis_events.append({
                                "session_id": entry.get("session_id"),
                                "timestamp": entry.get("timestamp"),
                                "length": entry.get("content_length"),
                                "category": entry.get("category"),
                                "successful": entry.get("successful", True)
                            })

                            # Update statistics
                            if entry.get("successful", True):
                                total_chars += entry.get("content_length", 0)
                                category = entry.get("category", "unknown")
                                categories[category] = categories.get(
                                    category, 0) + 1

                        # Update session end info
                        if entry.get("event_type") == "session_end":
                            if entry.get("session_id") in sessions:
                                sessions[entry.get("session_id")]["end_time"] = entry.get(
                                    "timestamp")
                                sessions[entry.get("session_id")]["summary"] = entry.get(
                                    "session_summary", {})

                    except json.JSONDecodeError:
                        continue

            # Generate report
            report = {
                "period_days": days,
                "total_sessions": len(sessions),
                "total_synthesis_events": len(synthesis_events),
                "total_chars_synthesized": total_chars,
                "synthesis_by_category": categories,
                "sessions": list(sessions.values())
            }

            return report

        except Exception as e:
            return {"status": "Error generating report", "error": str(e)}


# Singleton instance
_audit_trail = None


def get_audit_trail() -> SpeechSynthesisAuditTrail:
    """
    Get a singleton audit trail instance.

    Returns:
        SpeechSynthesisAuditTrail instance
    """
    global _audit_trail
    if _audit_trail is None:
        _audit_trail = SpeechSynthesisAuditTrail()
    return _audit_trail


def generate_tts_audit_report(days: int = 7) -> Dict:
    """
    Generate a report of TTS usage.

    Args:
        days: Number of days to include in report

    Returns:
        Dict: Audit report
    """
    audit_trail = get_audit_trail()

    report = SpeechSynthesisAuditTrail.extract_audit_report(
        log_file_path=audit_trail.log_file_path,
        days=days
    )

    logger.info(f"Generated TTS audit report covering {days} days")

    return report
