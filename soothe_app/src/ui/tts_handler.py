"""
Text-to-speech handler for SootheAI.
Manages audio narration using ElevenLabs API.
"""

import time
import logging
import threading
import subprocess
from collections import deque
from typing import Optional, Tuple

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
        self.voice_consent_message = """
        **Audio Feature Consent Required**
        
        SootheAI can narrate the story using AI-generated speech. Please note:
        - This uses synthetic voice generation, not a real person
        - Audio is processed in real-time and not stored
        - You can disable audio at any time by typing 'disable audio'
        
        Would you like to enable audio narration?
        - Type 'enable audio' to activate voice narration
        - Type 'disable audio' to continue with text only
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

    def speak_text(self, text: str) -> None:
        """
        Stream text to speech using ElevenLabs API and play with ffmpeg.

        Args:
            text: Text to convert to speech
        """
        if not self.elevenlabs_client:
            logger.warning("TTS disabled: ElevenLabs client not initialized")
            return

        try:
            logger.info("[DEBUG] Starting TTS stream with ffmpeg pipe...")
            stream_start = time.time()

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

    def delayed_tts(self, text: str) -> None:
        """
        Delay TTS by a short time to allow UI to update first.

        Args:
            text: Text to speak
        """
        time.sleep(0.1)  # Short delay to allow UI to update
        self.speak_text(text)

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

        # Check voice consent
        if not self.consent_manager.is_consent_given():
            logger.debug("TTS skipped: Voice consent not given")
            return

        # Check rate limiting
        can_process, limit_message = self.rate_limiter.can_process_tts(text)
        if not can_process:
            logger.warning(f"TTS rate limited: {limit_message}")
            return

        # Add voice disclaimer if needed
        text_with_disclaimer = self.add_voice_disclaimer(text)

        # Run TTS in thread to avoid blocking
        threading.Thread(target=self.delayed_tts, args=(
            text_with_disclaimer,), daemon=True).start()
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
        consent_changed, consent_response = self.consent_manager.check_voice_consent(
            message)
        if consent_changed:
            return True, consent_response

        # Check for other TTS commands
        message_lower = message.lower().strip()

        if message_lower == 'tts status':
            status = self.rate_limiter.get_status()
            status_msg = (
                f"TTS Status:\n"
                f"- Audio enabled: {'Yes' if self.consent_manager.is_consent_given() else 'No'}\n"
                f"- Rate limit: {status['requests_in_last_minute']}/{status['max_requests_per_minute']} requests/min\n"
                f"- Daily usage: {status['chars_used_today']}/{status['daily_char_limit']} characters\n"
                f"- Reset in: {status['time_until_reset']/3600:.1f} hours"
            )
            return True, status_msg

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
