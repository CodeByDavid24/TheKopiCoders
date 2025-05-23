"""
Updated TTS handler with audit trail integration for SootheAI.
"""

import atexit
import time
import logging
import threading
import subprocess
import re
from collections import deque
from typing import Optional, Tuple, Dict

from .speech_audit_trail import get_audit_trail

# Set up logger
logger = logging.getLogger(__name__)


class TTSRateLimiter:
    """Rate limiter for text-to-speech requests."""

    def __init__(self, max_requests_per_minute: int = 10, max_chars_per_request: int = 1000):
        """
        Initialize the rate limiter.

        Args:
            max_requests_per_minute: Maximum requests allowed per minute
            max_chars_per_request: Maximum characters allowed per request
        """
        self.max_requests = max_requests_per_minute
        self.max_chars = max_chars_per_request
        self.requests = deque()
        self.total_chars_today = 0
        self.daily_char_limit = 50000  # ElevenLabs free tier limit
        self.last_reset = time.time()

        logger.info(f"TTS rate limiter initialized with {max_requests_per_minute} requests/min, "
                    f"{max_chars_per_request} chars/request, {self.daily_char_limit} daily char limit")

    def _reset_daily_counter_if_needed(self) -> None:
        """Reset daily counter if it's a new day."""
        current_time = time.time()
        if current_time - self.last_reset > 24 * 60 * 60:  # 24 hours
            self.total_chars_today = 0
            self.last_reset = current_time
            logger.info("Daily TTS character count reset")

    def can_process_tts(self, text: str) -> Tuple[bool, str]:
        """
        Check if TTS request should be processed.

        Args:
            text: Text to be converted to speech

        Returns:
            Tuple of (can_process, reason)
        """
        self._reset_daily_counter_if_needed()
        now = time.time()

        # Remove old requests (older than 1 minute)
        while self.requests and now - self.requests[0] > 60:
            self.requests.popleft()

        # Check rate limits
        if len(self.requests) >= self.max_requests:
            return False, "Audio rate limit exceeded. Please wait before requesting more audio."

        if len(text) > self.max_chars:
            return False, f"Text too long for audio ({len(text)} chars). Maximum {self.max_chars} characters."

        if self.total_chars_today + len(text) > self.daily_char_limit:
            return False, "Daily audio limit reached. Audio will resume tomorrow."

        # Record this request
        self.requests.append(now)
        self.total_chars_today += len(text)

        logger.info(f"TTS rate limiter: {len(self.requests)}/{self.max_requests} requests, "
                    f"{self.total_chars_today}/{self.daily_char_limit} daily chars")

        return True, ""

    def get_status(self) -> dict:
        """
        Get current rate limiter status.

        Returns:
            Dictionary with current status
        """
        return {
            "requests_in_last_minute": len(self.requests),
            "max_requests_per_minute": self.max_requests,
            "chars_used_today": self.total_chars_today,
            "daily_char_limit": self.daily_char_limit,
            "time_until_reset": 24*60*60 - (time.time() - self.last_reset)
        }


class VoiceConsentManager:
    """Manager for user consent to voice narration."""

    def __init__(self):
        """Initialize the voice consent manager."""
        self.voice_consent_given = False
        # Update the consent message to be more concise for integration with the main consent flow
        self.voice_consent_message = """
        **Audio Feature Option**
        
        Would you like to enable AI voice narration for this story?
        - Type 'enable audio' to activate voice narration
        - Type 'disable audio' or 'no audio' to continue with text only
        - You can change this setting at any time
        """

        logger.info("Voice consent manager initialized")

    def check_voice_consent(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Check if user has given or is giving voice consent.

        Args:
            message: User message

        Returns:
            Tuple of (consent_status_changed, response_message)
        """
        message_lower = message.lower().strip()

        # Check for consent commands
        if message_lower == 'enable audio':
            if not self.voice_consent_given:
                self.voice_consent_given = True
                logger.info("User enabled audio narration")
                return True, "✅ Audio narration enabled! The story will now be read aloud."
            else:
                return False, "Audio narration is already enabled."

        elif message_lower == 'disable audio':
            if self.voice_consent_given:
                self.voice_consent_given = False
                logger.info("User disabled audio narration")
                return True, "🔇 Audio narration disabled. You'll continue with text only."
            else:
                return False, "Audio narration is already disabled."

        # Check if this is the first time and user hasn't given consent
        elif not self.voice_consent_given and message_lower not in ['i agree', 'start game']:
            return True, self.voice_consent_message

        return False, None

    def is_consent_given(self) -> bool:
        """
        Check if voice consent has been given.

        Returns:
            True if consent is given, False otherwise
        """
        return self.voice_consent_given

    def give_consent(self) -> None:
        """Mark voice consent as given."""
        self.voice_consent_given = True
        logger.info("Voice consent explicitly given")

    def revoke_consent(self) -> None:
        """Revoke voice consent."""
        self.voice_consent_given = False
        logger.info("Voice consent revoked")


class TTSHandler:
    """Handler for text-to-speech functionality."""

    def __init__(self, elevenlabs_client=None):
        """
        Initialize the TTS handler.

        Args:
            elevenlabs_client: ElevenLabs client instance
        """
        self.elevenlabs_client = elevenlabs_client
        self.rate_limiter = TTSRateLimiter()
        self.consent_manager = VoiceConsentManager()
        self.tts_session_started = False
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default female voice
        self.model_id = "eleven_flash_v2_5"

        # Get the audit trail instance
        self.audit_trail = get_audit_trail()

        logger.info("TTS handler initialized")
        if not elevenlabs_client:
            logger.warning(
                "ElevenLabs client not provided, TTS will be disabled")

    def add_voice_disclaimer(self, text: str) -> str:
        """
        Add AI voice disclaimer to the beginning of narration.

        Args:
            text: Text to be processed

        Returns:
            Text with disclaimer added if needed
        """
        # Check if this is the beginning of a new narration session
        if not self.tts_session_started:
            # Mark that TTS session has started
            self.tts_session_started = True
            disclaimer = "This story is narrated by an AI-generated voice. "
            return disclaimer + text
        else:
            return text

    def mark_tts_session_started(self) -> None:
        """Mark TTS session as started for tracking."""
        self.tts_session_started = True
        logger.info("TTS session marked as started")

    def detect_content_category(self, text: str) -> str:
        """
        Detect the category of content for audit purposes.

        Args:
            text: The text to categorize

        Returns:
            str: Content category
        """
        # Check for dialogue (text in quotation marks with speaker attribution)
        if re.search(r'"[^"]+"\s*(?:said|asked|replied)', text):
            return "dialogue"

        # Check for inner thoughts (second person perspective)
        if re.search(r'\byou (think|feel|wonder|worry|consider)\b', text, re.IGNORECASE):
            return "inner_thoughts"

        # Check for options/choices
        if re.search(r'\d+\.\s+', text) or "what do you want to do?" in text.lower():
            return "options"

        # Default to narrative
        return "narrative"

    def speak_text(self, text: str, category: str = "narrative") -> None:
        """
        Stream text to speech using ElevenLabs API and play with ffmpeg.

        Args:
            text: Text to convert to speech
            category: Category of speech content
        """
        if not self.elevenlabs_client:
            logger.warning("TTS disabled: ElevenLabs client not initialized")
            self.audit_trail.log_synthesis_error(
                text=text[:100] + "..." if len(text) > 100 else text,
                error_message="TTS disabled: ElevenLabs client not initialized",
                category=category
            )
            return

        try:
            logger.info("[DEBUG] Starting TTS stream with ffmpeg pipe...")
            stream_start = time.time()

            # Log the synthesis start
            synthesis_entry = self.audit_trail.log_synthesis(
                text=text,
                category=category,
                metadata={
                    "voice_id": self.voice_id,
                    "model_id": self.model_id
                }
            )

            process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            for chunk in self.elevenlabs_client.text_to_speech.convert_as_stream(
                voice_id=self.voice_id,
                output_format="mp3_44100_128",
                text=text,
                model_id=self.model_id
            ):
                if process.stdin:
                    process.stdin.write(chunk)
            if process.stdin:
                process.stdin.close()

            process.wait()
            stream_elapsed = time.time() - stream_start
            logger.info(
                f"[DEBUG] TTS streaming duration: {stream_elapsed:.2f} seconds")

        except Exception as tts_error:
            logger.error(f"TTS Error: {tts_error}")
            # Log the synthesis error
            self.audit_trail.log_synthesis_error(
                text=text[:100] + "..." if len(text) > 100 else text,
                error_message=str(tts_error),
                category=category
            )

    def delayed_tts(self, text: str, category: str = "narrative") -> None:
        """
        Delay TTS by a short time to allow UI to update first.

        Args:
            text: Text to speak
            category: Category of speech content
        """
        time.sleep(0.1)  # Short delay to allow UI to update
        self.speak_text(text, category)

    def cleanup(self):
        """Perform cleanup operations when shutting down."""
        try:
            # Log end of session
            if hasattr(self, 'audit_trail'):
                stats = self.audit_trail.get_session_statistics()
                logger.info(f"TTS session stats: {stats}")
                self.audit_trail.log_session_end()
        except Exception as e:
            logger.error(f"Error during TTS cleanup: {e}")

    def run_tts_with_consent_and_limiting(self, text: str) -> None:
        """
        Run TTS with voice consent and rate limiting checks.

        Args:
            text: Text to convert to speech
        """
        # Check if TTS is disabled at the client level
        if not self.elevenlabs_client:
            logger.debug("TTS is disabled: ElevenLabs client not initialized")
            return

        # Check voice consent - but don't interrupt narrative flow by asking for consent
        if not self.consent_manager.is_consent_given():
            logger.debug("TTS skipped: Voice consent not given")
            return

        # Check rate limiting
        can_process, limit_message = self.rate_limiter.can_process_tts(text)
        if not can_process:
            logger.warning(f"TTS rate limited: {limit_message}")
            # Log the rate limiting in audit trail
            self.audit_trail.log_synthesis_error(
                text=text[:100] + "..." if len(text) > 100 else text,
                error_message=f"Rate limiting: {limit_message}",
                category="rate_limited"
            )
            return

        # Detect content category
        category = self.detect_content_category(text)

        # Add voice disclaimer if needed
        text_with_disclaimer = self.add_voice_disclaimer(text)

        # Run TTS in thread to avoid blocking
        threading.Thread(target=self.delayed_tts, args=(
            text_with_disclaimer, category), daemon=True).start()
        logger.info(f"Started TTS thread for text: {text[:50]}...")

    def process_command(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Process potential TTS-related commands.

        Args:
            message: User message

        Returns:
            Tuple of (is_tts_command, response_message)
        """
        # Check for voice consent commands
        message_lower = message.lower().strip()

        if message_lower == 'enable audio':
            if not self.consent_manager.is_consent_given():
                self.consent_manager.give_consent()
                logger.info("User enabled audio narration")
                return True, "✅ Audio narration enabled! The story will now be read aloud."
            else:
                return True, "Audio narration is already enabled."

        elif message_lower == 'disable audio' or message_lower == 'no audio':
            if self.consent_manager.is_consent_given():
                self.consent_manager.revoke_consent()
                logger.info("User disabled audio narration")
                return True, "🔇 Audio narration disabled. You'll continue with text only."
            else:
                return True, "Audio narration is already disabled."

        # Handle the combined consent command
        elif message_lower == 'i agree with audio':
            self.consent_manager.give_consent()
            logger.info(
                "User enabled audio narration through combined consent")
            return False, None  # Return False so the main flow continues

        elif message_lower == 'i agree without audio':
            self.consent_manager.revoke_consent()
            logger.info(
                "User disabled audio narration through combined consent")
            return False, None  # Return False so the main flow continues

        # Check for other TTS commands
        if message_lower == 'tts status':
            status = self.rate_limiter.get_status()
            audit_stats = self.audit_trail.get_session_statistics()

            status_msg = (
                f"TTS Status:\n"
                f"- Audio enabled: {'Yes' if self.consent_manager.is_consent_given() else 'No'}\n"
                f"- Rate limit: {status['requests_in_last_minute']}/{status['max_requests_per_minute']} requests/min\n"
                f"- Daily usage: {status['chars_used_today']}/{status['daily_char_limit']} characters\n"
                f"- Reset in: {status['time_until_reset']/3600:.1f} hours\n"
                f"- Session stats: {audit_stats['total_synthesis_count']} TTS events, "
                f"{audit_stats['total_chars_synthesized']} characters synthesized"
            )
            return True, status_msg

        elif message_lower == 'tts report':
            # Generate a simple report from the audit trail
            try:
                report = self.audit_trail.extract_audit_report(days=1)
                report_msg = (
                    f"TTS Audit Report (Last 24 hours):\n"
                    f"- Total sessions: {report.get('total_sessions', 0)}\n"
                    f"- Total synthesis events: {report.get('total_synthesis_events', 0)}\n"
                    f"- Characters synthesized: {report.get('total_chars_synthesized', 0)}\n"
                    f"- Categories: {', '.join(report.get('synthesis_by_category', {}).keys())}"
                )
                return True, report_msg
            except Exception as e:
                logger.error(f"Error generating TTS report: {e}")
                return True, "Error generating TTS report. Please check logs."

        return False, None


# Singleton instance
_tts_handler = None


def get_tts_handler(elevenlabs_client=None):
    """
    Get a singleton TTS handler instance.

    Args:
        elevenlabs_client: ElevenLabs client instance

    Returns:
        TTSHandler instance
    """
    global _tts_handler
    if _tts_handler is None:
        _tts_handler = TTSHandler(elevenlabs_client)
    return _tts_handler


# Register the cleanup function to run at exit


def cleanup_on_exit():
    """Perform cleanup when the application exits."""
    global _tts_handler

    if _tts_handler is not None:
        try:
            _tts_handler.cleanup()
            logger.info("TTS handler cleanup completed")
        except Exception as e:
            logger.error(f"Error during TTS handler cleanup: {e}")


atexit.register(cleanup_on_exit)
