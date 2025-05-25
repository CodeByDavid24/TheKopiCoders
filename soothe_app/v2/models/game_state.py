"""
Game state model for SootheAI.
Manages the state of the narrative experience without character data dependency.
"""

import time
import logging
from typing import Dict, List, Tuple, Any, Optional

logger = logging.getLogger(__name__)


class GameState:
    """Class for managing the state of the SootheAI narrative experience."""

    def __init__(self):
        """Initialize the game state without character data dependency."""
        self.history: List[Tuple[str, str]] = []
        self.consent_given: bool = False
        self.start_narrative: Optional[str] = None
        self.interaction_count: int = 0
        self.audio_enabled: bool = False
        self.tts_session_started: bool = False
        self.story_ended: bool = False
        self.start_time = time.time()

        # Add a dedicated field for audio consent
        self.audio_consent_asked = False

        # Initialize with timestamp for debugging
        logger.info(
            f"Game state initialized at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    def mark_audio_consent_asked(self) -> None:
        """Mark that audio consent has been explicitly asked."""
        self.audio_consent_asked = True
        logger.info("Audio consent marked as explicitly asked")

    def is_audio_consent_asked(self) -> bool:
        """
        Check if audio consent has been explicitly asked.

        Returns:
            True if audio consent has been asked, False otherwise
        """
        return self.audio_consent_asked

    def give_consent(self) -> None:
        """Mark user consent as given."""
        self.consent_given = True
        logger.info("User consent recorded")

    def is_consent_given(self) -> bool:
        """Check if user has given consent."""
        return self.consent_given

    def set_starting_narrative(self, narrative: str) -> None:
        """
        Set the starting narrative.

        Args:
            narrative: Initial narrative text
        """
        self.start_narrative = narrative
        logger.info("Starting narrative set")

    def get_starting_narrative(self) -> Optional[str]:
        """
        Get the starting narrative.

        Returns:
            Starting narrative text or None if not set
        """
        return self.start_narrative

    def add_to_history(self, user_message: str, assistant_response: str) -> None:
        """
        Add a message pair to the conversation history.

        Args:
            user_message: User's message
            assistant_response: Assistant's response
        """
        self.history.append((user_message, assistant_response))
        logger.debug(
            f"Added message pair to history (now {len(self.history)} pairs)")

    def get_history(self) -> List[Tuple[str, str]]:
        """
        Get the conversation history.

        Returns:
            List of (user_message, assistant_response) tuples
        """
        return self.history

    def increment_interaction_count(self) -> int:
        """
        Increment the interaction count.

        Returns:
            New interaction count
        """
        self.interaction_count += 1
        logger.info(
            f"Interaction count incremented to {self.interaction_count}")
        return self.interaction_count

    def get_interaction_count(self) -> int:
        """
        Get the current interaction count.

        Returns:
            Current interaction count
        """
        return self.interaction_count

    def should_trigger_ending(self) -> bool:
        """
        Check if the story ending should be triggered.

        Returns:
            True if ending should be triggered, False otherwise
        """
        # Current simple implementation: trigger after 12 interactions
        return self.interaction_count >= 12

    def set_audio_enabled(self, enabled: bool) -> None:
        """
        Set whether audio narration is enabled.

        Args:
            enabled: Whether audio should be enabled
        """
        self.audio_enabled = enabled
        logger.info(f"Audio narration {'enabled' if enabled else 'disabled'}")

    def is_audio_enabled(self) -> bool:
        """
        Check if audio narration is enabled.

        Returns:
            True if audio is enabled, False otherwise
        """
        return self.audio_enabled

    def mark_tts_session_started(self) -> None:
        """Mark TTS session as started for tracking."""
        self.tts_session_started = True

    def is_tts_session_started(self) -> bool:
        """
        Check if TTS session has started.

        Returns:
            True if TTS session has started, False otherwise
        """
        return self.tts_session_started

    def mark_story_ended(self) -> None:
        """Mark the story as ended."""
        self.story_ended = True
        logger.info("Story marked as ended")

    def is_story_ended(self) -> bool:
        """
        Check if the story has ended.

        Returns:
            True if story has ended, False otherwise
        """
        return self.story_ended

    def get_session_duration(self) -> float:
        """
        Get the duration of the current session in seconds.

        Returns:
            Session duration in seconds
        """
        return time.time() - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the game state to a dictionary for serialization.

        Returns:
            Dictionary representation of the game state
        """
        return {
            "consent_given": self.consent_given,
            "interaction_count": self.interaction_count,
            "audio_enabled": self.audio_enabled,
            "tts_session_started": self.tts_session_started,
            "story_ended": self.story_ended,
            "session_duration": self.get_session_duration()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """
        Create a GameState instance from a dictionary.

        Args:
            data: Dictionary containing game state data

        Returns:
            GameState instance
        """
        state = cls()  # No character data needed

        state.consent_given = data.get("consent_given", False)
        state.interaction_count = data.get("interaction_count", 0)
        state.audio_enabled = data.get("audio_enabled", False)
        state.tts_session_started = data.get("tts_session_started", False)
        state.story_ended = data.get("story_ended", False)

        return state