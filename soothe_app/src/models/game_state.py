"""
Game state model for SootheAI.
Manages the state of the narrative experience.
"""

import time
import logging
from typing import Dict, List, Tuple, Any, Optional

# Set up logger
logger = logging.getLogger(__name__)


class GameState:
    """Class for managing the state of the SootheAI narrative experience."""

    def __init__(self, character_data: Dict[str, Any]):
        """
        Initialize the game state.

        Args:
            character_data: Character configuration data
        """
        self.character = character_data
        self.history: List[Tuple[str, str]] = []
        self.consent_given: bool = False
        self.start_narrative: Optional[str] = None
        self.interaction_count: int = 0
        self.audio_enabled: bool = False
        self.tts_session_started: bool = False
        self.story_ended: bool = False
        self.start_time = time.time()

        # Internal game mechanics state
        # Scale: 1-10 (10=overwhelmed, 1=balanced)
        self.wellbeing_level: int = 5
        self.self_awareness: str = "Low"  # None, Low, Developing, Growing, High
        # Relaxed, Mild tension, Moderate tension, High tension, Physical distress
        self.physical_state: str = "Moderate tension"
        # Rare worries, Occasional worries, Frequent worries, Constant worries, Overwhelming thoughts
        self.mental_state: str = "Frequent worries"

        # Relationship scores (0-10)
        self.relationships = {
            "parents": 6,
            "friends": 7,
            "teachers": 7,
            "classmates": 5
        }

        # Trigger tracking
        # Tracks consecutive high overwhelm interactions
        self.high_overwhelm_count: int = 0

        # Initialize with timestamp for debugging
        logger.info(
            f"Game state initialized at {time.strftime('%Y-%m-%d %H:%M:%S')}")

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

    def update_wellbeing_level(self, change: int) -> int:
        """
        Update the character's wellbeing level.

        Args:
            change: Amount to change wellbeing level by (positive = more overwhelmed)

        Returns:
            New wellbeing level
        """
        # Update the wellbeing level, ensuring it stays within bounds
        old_level = self.wellbeing_level
        self.wellbeing_level = max(1, min(10, self.wellbeing_level + change))

        # Track consecutive high overwhelm states
        if self.wellbeing_level >= 8:
            self.high_overwhelm_count += 1
        else:
            self.high_overwhelm_count = 0

        logger.info(
            f"Wellbeing level changed from {old_level} to {self.wellbeing_level}")
        return self.wellbeing_level

    def get_wellbeing_level(self) -> int:
        """
        Get the current wellbeing level.

        Returns:
            Current wellbeing level
        """
        return self.wellbeing_level

    def is_in_crisis(self) -> bool:
        """
        Check if character is in crisis state.

        Returns:
            True if in crisis, False otherwise
        """
        return self.wellbeing_level >= 9 or self.high_overwhelm_count >= 3

    def update_relationship(self, relationship: str, change: int) -> int:
        """
        Update a relationship score.

        Args:
            relationship: Relationship type ('parents', 'friends', 'teachers', 'classmates')
            change: Amount to change relationship score by

        Returns:
            New relationship score
        """
        if relationship not in self.relationships:
            logger.warning(
                f"Attempted to update unknown relationship: {relationship}")
            return -1

        old_score = self.relationships[relationship]
        self.relationships[relationship] = max(
            0, min(10, self.relationships[relationship] + change))

        logger.info(
            f"Relationship '{relationship}' changed from {old_score} to {self.relationships[relationship]}")
        return self.relationships[relationship]

    def get_relationship_score(self, relationship: str) -> int:
        """
        Get a relationship score.

        Args:
            relationship: Relationship type

        Returns:
            Relationship score or -1 if relationship not found
        """
        return self.relationships.get(relationship, -1)

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
            "wellbeing_level": self.wellbeing_level,
            "self_awareness": self.self_awareness,
            "physical_state": self.physical_state,
            "mental_state": self.mental_state,
            "relationships": self.relationships,
            "high_overwhelm_count": self.high_overwhelm_count,
            "session_duration": self.get_session_duration()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], character_data: Dict[str, Any]) -> 'GameState':
        """
        Create a GameState instance from a dictionary.

        Args:
            data: Dictionary containing game state data
            character_data: Character configuration data

        Returns:
            GameState instance
        """
        state = cls(character_data)

        state.consent_given = data.get("consent_given", False)
        state.interaction_count = data.get("interaction_count", 0)
        state.audio_enabled = data.get("audio_enabled", False)
        state.tts_session_started = data.get("tts_session_started", False)
        state.story_ended = data.get("story_ended", False)
        state.wellbeing_level = data.get("wellbeing_level", 5)
        state.self_awareness = data.get("self_awareness", "Low")
        state.physical_state = data.get("physical_state", "Moderate tension")
        state.mental_state = data.get("mental_state", "Frequent worries")
        state.relationships = data.get("relationships", {
            "parents": 6,
            "friends": 7,
            "teachers": 7,
            "classmates": 5
        })
        state.high_overwhelm_count = data.get("high_overwhelm_count", 0)

        # History can't be easily serialized, so it starts empty

        return state
