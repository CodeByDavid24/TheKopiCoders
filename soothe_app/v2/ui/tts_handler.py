"""
Updated TTS handler with audit trail integration for SootheAI.
"""

import atexit  # For cleanup on application exit
import time  # For rate limiting and timing operations
import logging  # For application logging
import threading  # For non-blocking TTS processing
import subprocess  # For ffplay audio playback
import re  # For pattern matching in content detection
from collections import deque  # For efficient request tracking
# Type hints for better code documentation
from typing import Optional, Tuple, Dict

# Import audit trail for TTS usage tracking
from .speech_audit_trail import get_audit_trail

# Set up logger for this module
logger = logging.getLogger(__name__)


class TTSRateLimiter:
    """Rate limiter for text-to-speech requests to prevent API abuse."""

    def __init__(self, max_requests_per_minute: int = 10, max_chars_per_request: int = 3000):
        """
        Initialize the rate limiter with configurable limits.

        Args:
            max_requests_per_minute: Maximum requests allowed per minute
            max_chars_per_request: Maximum characters allowed per request
        """
        self.max_requests = max_requests_per_minute  # Store max requests limit
        self.max_chars = max_chars_per_request  # Store max characters limit
        self.requests = deque()  # Track request timestamps using efficient deque
        self.total_chars_today = 0  # Track daily character usage
        # ElevenLabs free tier limit (50k chars/day)
        self.daily_char_limit = 50000
        self.last_reset = time.time()  # Track when daily counter was last reset

        logger.info(f"TTS rate limiter initialized with {max_requests_per_minute} requests/min, "
                    f"{max_chars_per_request} chars/request, {self.daily_char_limit} daily char limit")

    def _reset_daily_counter_if_needed(self) -> None:
        """Reset daily character counter if it's a new day."""
        current_time = time.time()  # Get current timestamp
        if current_time - self.last_reset > 24 * 60 * 60:  # Check if 24 hours have passed
            self.total_chars_today = 0  # Reset daily character count
            self.last_reset = current_time  # Update reset timestamp
            logger.info("Daily TTS character count reset")  # Log daily reset

    def can_process_tts(self, text: str) -> Tuple[bool, str]:
        """
        Check if TTS request should be processed based on rate limits.

        Args:
            text: Text to be converted to speech

        Returns:
            Tuple[bool, str]: (can_process, reason_if_rejected)
        """
        self._reset_daily_counter_if_needed()  # Check if daily reset needed
        now = time.time()  # Get current timestamp

        # Remove old requests (older than 1 minute) from tracking deque
        while self.requests and now - self.requests[0] > 60:
            self.requests.popleft()  # Remove oldest request

        # Check per-minute rate limit
        if len(self.requests) >= self.max_requests:
            return False, "Audio rate limit exceeded. Please wait before requesting more audio."

        # Check per-request character limit
        if len(text) > self.max_chars:
            return False, f"Text too long for audio ({len(text)} chars). Maximum {self.max_chars} characters."

        # Check daily character limit
        if self.total_chars_today + len(text) > self.daily_char_limit:
            return False, "Daily audio limit reached. Audio will resume tomorrow."

        # Record this request for rate limiting
        self.requests.append(now)  # Add current timestamp to request tracking
        self.total_chars_today += len(text)  # Add characters to daily count

        logger.info(f"TTS rate limiter: {len(self.requests)}/{self.max_requests} requests, "
                    f"{self.total_chars_today}/{self.daily_char_limit} daily chars")

        return True, ""  # Request approved

    def get_status(self) -> dict:
        """
        Get current rate limiter status for monitoring.

        Returns:
            dict: Current rate limiting status and usage statistics
        """
        return {
            # Current request count
            "requests_in_last_minute": len(self.requests),
            "max_requests_per_minute": self.max_requests,  # Maximum allowed requests
            "chars_used_today": self.total_chars_today,  # Characters used today
            "daily_char_limit": self.daily_char_limit,  # Daily character limit
            # Time until daily reset
            "time_until_reset": 24*60*60 - (time.time() - self.last_reset)
        }


class VoiceConsentManager:
    """Manager for user consent to voice narration."""

    def __init__(self):
        """Initialize the voice consent manager with default settings."""
        self.voice_consent_given = False  # Track if user has consented to voice
        # Update the consent message to be more concise for integration with the main consent flow
        self.voice_consent_message = """
        **Audio Feature Option**
        
        Would you like to enable AI voice narration for this story?
        - Type 'enable audio' to activate voice narration
        - Type 'disable audio' or 'no audio' to continue with text only
        - You can change this setting at any time
        """

        logger.info("Voice consent manager initialized")  # Log initialization

    def check_voice_consent(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Check if user has given or is giving voice consent.

        Args:
            message: User message to check for consent commands

        Returns:
            Tuple[bool, Optional[str]]: (consent_status_changed, response_message)
        """
        message_lower = message.lower().strip()  # Normalize message for comparison

        # Check for audio enable command
        if message_lower == 'enable audio':
            if not self.voice_consent_given:  # Only change if not already enabled
                self.voice_consent_given = True  # Enable voice consent
                # Log consent given
                logger.info("User enabled audio narration")
                return True, "✅ Audio narration enabled! The story will now be read aloud."
            else:
                return False, "Audio narration is already enabled."  # Already enabled message

        # Check for audio disable command
        elif message_lower == 'disable audio':
            if self.voice_consent_given:  # Only change if currently enabled
                self.voice_consent_given = False  # Disable voice consent
                # Log consent revoked
                logger.info("User disabled audio narration")
                return True, "🔇 Audio narration disabled. You'll continue with text only."
            else:
                return False, "Audio narration is already disabled."  # Already disabled message

        # Check if this is the first time and user hasn't given consent
        elif not self.voice_consent_given and message_lower not in ['i agree', 'start game']:
            return True, self.voice_consent_message  # Show consent message

        return False, None  # No consent status change

    def is_consent_given(self) -> bool:
        """
        Check if voice consent has been given.

        Returns:
            bool: True if consent is given, False otherwise
        """
        return self.voice_consent_given

    def give_consent(self) -> None:
        """Mark voice consent as given."""
        self.voice_consent_given = True  # Enable voice consent
        logger.info("Voice consent explicitly given")  # Log consent granted

    def revoke_consent(self) -> None:
        """Revoke voice consent."""
        self.voice_consent_given = False  # Disable voice consent
        logger.info("Voice consent revoked")  # Log consent revoked


class TTSHandler:
    """Handler for text-to-speech functionality with rate limiting and audit trail."""

    def __init__(self, elevenlabs_client=None):
        """
        Initialize the TTS handler with optional ElevenLabs client.

        Args:
            elevenlabs_client: Optional ElevenLabs client instance for TTS
        """
        self.elevenlabs_client = elevenlabs_client  # Store ElevenLabs client reference
        self.rate_limiter = TTSRateLimiter()  # Initialize rate limiting
        self.consent_manager = VoiceConsentManager()  # Initialize consent management
        self.tts_session_started = False  # Track if TTS session has started
        # Default female voice ID for ElevenLabs
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"
        self.model_id = "eleven_flash_v2_5"  # Fast model for real-time synthesis

        # Get the audit trail instance for usage tracking
        self.audit_trail = get_audit_trail()

        logger.info("TTS handler initialized")  # Log successful initialization
        if not elevenlabs_client:
            logger.warning(
                "ElevenLabs client not provided, TTS will be disabled")  # Log missing client

    def add_voice_disclaimer(self, text: str) -> str:
        """
        Add AI voice disclaimer to the beginning of narration for transparency.

        Args:
            text: Text to be processed

        Returns:
            str: Text with disclaimer added if needed
        """
        # Check if this is the beginning of a new narration session
        if not self.tts_session_started:
            # Mark that TTS session has started
            self.tts_session_started = True
            # Add transparency disclaimer
            disclaimer = "This story is narrated by an AI-generated voice. "
            return disclaimer + text  # Prepend disclaimer to original text
        else:
            return text  # Return original text if session already started

    def mark_tts_session_started(self) -> None:
        """Mark TTS session as started for tracking purposes."""
        self.tts_session_started = True  # Set session started flag
        logger.info("TTS session marked as started")  # Log session start

    def detect_content_category(self, text: str) -> str:
        """
        Detect the category of content for audit purposes and analytics.

        Args:
            text: The text to categorize

        Returns:
            str: Content category for audit logging
        """
        # Check for dialogue (text in quotation marks with speaker attribution)
        if re.search(r'"[^"]+"\s*(?:said|asked|replied)', text):
            return "dialogue"

        # Check for inner thoughts (second person perspective)
        if re.search(r'\byou (think|feel|wonder|worry|consider)\b', text, re.IGNORECASE):
            return "inner_thoughts"

        # Check for options/choices presented to user
        if re.search(r'\d+\.\s+', text) or "what do you want to do?" in text.lower():
            return "options"

        # Default to narrative content
        return "narrative"

    def speak_text(self, text: str, category: str = "narrative") -> None:
        """
        Stream text to speech using ElevenLabs API and play with ffmpeg.

        Args:
            text: Text to convert to speech
            category: Category of speech content for audit logging
        """
        if not self.elevenlabs_client:  # Check if TTS client is available
            # Log disabled TTS
            logger.warning("TTS disabled: ElevenLabs client not initialized")
            self.audit_trail.log_synthesis_error(
                # Truncate long text for logging
                text=text[:100] + "..." if len(text) > 100 else text,
                error_message="TTS disabled: ElevenLabs client not initialized",
                category=category
            )
            return

        try:
            # Log TTS start
            logger.info("[DEBUG] Starting TTS stream with ffmpeg pipe...")
            stream_start = time.time()  # Record start time for performance monitoring

            # Log the synthesis start in audit trail
            synthesis_entry = self.audit_trail.log_synthesis(
                text=text,  # Full text being synthesized
                category=category,  # Content category
                metadata={
                    "voice_id": self.voice_id,  # Voice model used
                    "model_id": self.model_id  # TTS model used
                }
            )

            # Start ffplay process for audio playback
            process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-"],
                stdin=subprocess.PIPE,  # Accept audio data via stdin
                stdout=subprocess.DEVNULL,  # Suppress stdout
                stderr=subprocess.DEVNULL  # Suppress stderr
            )

            # Use the correct ElevenLabs streaming method
            audio_stream = self.elevenlabs_client.text_to_speech.stream(
                voice_id=self.voice_id,  # Voice to use
                output_format="mp3_44100_128",  # Audio format specification
                text=text,  # Text to synthesize
                model_id=self.model_id  # Model to use
            )

            # Stream audio data to ffplay
            for chunk in audio_stream:
                if process.stdin:  # Ensure stdin is available
                    process.stdin.write(chunk)  # Write audio chunk to ffplay
            
            if process.stdin:
                process.stdin.close()  # Close stdin when done

            process.wait()  # Wait for ffplay to finish
            stream_elapsed = time.time() - stream_start  # Calculate processing time
            logger.info(f"[DEBUG] TTS streaming duration: {stream_elapsed:.2f} seconds")

        except Exception as tts_error:
            logger.error(f"TTS Error: {tts_error}")  # Log TTS error
            # Log the synthesis error in audit trail
            self.audit_trail.log_synthesis_error(
                # Truncate long text for logging
                text=text[:100] + "..." if len(text) > 100 else text,
                error_message=str(tts_error),  # Convert exception to string
                category=category  # Include content category
            )

    def delayed_tts(self, text: str, category: str = "narrative") -> None:
        """
        Delay TTS by a short time to allow UI to update first.

        Args:
            text: Text to speak
            category: Category of speech content for audit logging
        """
        time.sleep(0.1)  # Short delay to allow UI to update before audio starts
        self.speak_text(text, category)  # Call main TTS function

    def cleanup(self):
        """Perform cleanup operations when shutting down."""
        try:
            # Log end of session with statistics
            if hasattr(self, 'audit_trail'):  # Ensure audit trail exists
                stats = self.audit_trail.get_session_statistics()  # Get session statistics
                # Log final statistics
                logger.info(f"TTS session stats: {stats}")
                self.audit_trail.log_session_end()  # Log session end event
        except Exception as e:
            # Log cleanup errors
            logger.error(f"Error during TTS cleanup: {e}")

    def run_tts_with_consent_and_limiting(self, text: str) -> None:
        """
        Run TTS with voice consent and rate limiting checks.

        Args:
            text: Text to convert to speech
        """
        # Check if TTS is disabled at the client level
        if not self.elevenlabs_client:
            # Log disabled state
            logger.debug("TTS is disabled: ElevenLabs client not initialized")
            return

        # Check voice consent - but don't interrupt narrative flow by asking for consent
        if not self.consent_manager.is_consent_given():
            # Log consent not given
            logger.debug("TTS skipped: Voice consent not given")
            return

        # Check rate limiting to prevent API abuse
        can_process, limit_message = self.rate_limiter.can_process_tts(text)
        if not can_process:
            # Log rate limiting
            logger.warning(f"TTS rate limited: {limit_message}")
            # Log the rate limiting in audit trail
            self.audit_trail.log_synthesis_error(
                # Truncate for logging
                text=text[:100] + "..." if len(text) > 100 else text,
                # Include rate limit reason
                error_message=f"Rate limiting: {limit_message}",
                category="rate_limited"  # Special category for rate limited events
            )
            return

        # Detect content category for analytics
        category = self.detect_content_category(text)

        # Add voice disclaimer if needed for transparency
        text_with_disclaimer = self.add_voice_disclaimer(text)

        # Run TTS in thread to avoid blocking the main UI thread
        threading.Thread(target=self.delayed_tts, args=(
            text_with_disclaimer, category), daemon=True).start()  # Start as daemon thread
        # Log thread start
        logger.info(f"Started TTS thread for text: {text[:50]}...")

    def process_command(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Process potential TTS-related commands from user input.

        Args:
            message: User message to check for TTS commands

        Returns:
            Tuple[bool, Optional[str]]: (is_tts_command, response_message)
        """
        # Check for voice consent commands
        message_lower = message.lower().strip()  # Normalize message for comparison

        # Handle audio enable command
        if message_lower == 'enable audio':
            if not self.consent_manager.is_consent_given():  # Check current consent status
                self.consent_manager.give_consent()  # Grant voice consent
                # Log consent granted
                logger.info("User enabled audio narration")
                return True, "✅ Audio narration enabled! The story will now be read aloud."
            else:
                return True, "Audio narration is already enabled."  # Already enabled response

        # Handle audio disable commands
        elif message_lower == 'disable audio' or message_lower == 'no audio':
            if self.consent_manager.is_consent_given():  # Check current consent status
                self.consent_manager.revoke_consent()  # Revoke voice consent
                # Log consent revoked
                logger.info("User disabled audio narration")
                return True, "🔇 Audio narration disabled. You'll continue with text only."
            else:
                return True, "Audio narration is already disabled."  # Already disabled response

        # Handle the combined consent command from initial consent flow
        elif message_lower == 'i agree with audio':
            self.consent_manager.give_consent()  # Grant voice consent
            logger.info(
                "User enabled audio narration through combined consent")  # Log consent via combined command
            return False, None  # Return False so the main flow continues

        # Handle combined consent without audio
        elif message_lower == 'i agree without audio':
            self.consent_manager.revoke_consent()  # Ensure audio is disabled
            logger.info(
                "User disabled audio narration through combined consent")  # Log audio disabled via combined command
            return False, None  # Return False so the main flow continues

        # Check for TTS status command for debugging/monitoring
        if message_lower == 'tts status':
            status = self.rate_limiter.get_status()  # Get rate limiter status
            audit_stats = self.audit_trail.get_session_statistics()  # Get audit statistics

            # Format comprehensive status message
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

        # Check for TTS report command for detailed analytics
        elif message_lower == 'tts report':
            # Generate a simple report from the audit trail
            try:
                report = self.audit_trail.extract_audit_report(
                    days=1)  # Get last 24 hours
                report_msg = (
                    f"TTS Audit Report (Last 24 hours):\n"
                    f"- Total sessions: {report.get('total_sessions', 0)}\n"
                    f"- Total synthesis events: {report.get('total_synthesis_events', 0)}\n"
                    f"- Characters synthesized: {report.get('total_chars_synthesized', 0)}\n"
                    f"- Categories: {', '.join(report.get('synthesis_by_category', {}).keys())}"
                )
                return True, report_msg
            except Exception as e:
                # Log report generation error
                logger.error(f"Error generating TTS report: {e}")
                return True, "Error generating TTS report. Please check logs."

        return False, None  # Not a TTS command


# Singleton instance for application-wide access
_tts_handler = None


def get_tts_handler(elevenlabs_client=None):
    """
    Get a singleton TTS handler instance for consistent state management.

    Args:
        elevenlabs_client: ElevenLabs client instance

    Returns:
        TTSHandler: Singleton TTS handler instance
    """
    global _tts_handler
    if _tts_handler is None:  # Create instance if not exists
        _tts_handler = TTSHandler(elevenlabs_client)
    return _tts_handler


# Register the cleanup function to run at exit
def cleanup_on_exit():
    """Perform cleanup when the application exits."""
    global _tts_handler

    if _tts_handler is not None:  # Only cleanup if handler exists
        try:
            _tts_handler.cleanup()  # Call cleanup method
            # Log successful cleanup
            logger.info("TTS handler cleanup completed")
        except Exception as e:
            # Log cleanup errors
            logger.error(f"Error during TTS handler cleanup: {e}")


# Register cleanup function for application exit
atexit.register(cleanup_on_exit)
