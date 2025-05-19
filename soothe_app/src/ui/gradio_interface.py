"""
Gradio interface module for SootheAI.
Manages UI interactions and the web interface.
"""

import logging
import gradio as gr
from typing import Optional, Tuple, List, Dict, Any

from ..core.narrative_engine import create_narrative_engine
from ..models.game_state import GameState
from ..ui.tts_handler import get_tts_handler

# Set up logger
logger = logging.getLogger(__name__)


class GradioInterface:
    """Class for managing the Gradio interface for SootheAI."""

    def __init__(self, character_data: Dict[str, Any], elevenlabs_client=None):
        """
        Initialize the Gradio interface.

        Args:
            character_data: Character data dictionary
            elevenlabs_client: ElevenLabs client instance, if any
        """
        self.narrative_engine = create_narrative_engine(character_data)
        self.tts_handler = get_tts_handler(elevenlabs_client)
        self.interface = None
        self.consent_message = """
        **Welcome to SootheAI - Serena's Story**

        **Important Information:**
        This is a fictional story designed to help you understand anxiety. Please be aware that some of the content may depict distressing situations. **Do not replicate or engage in any harmful actions shown in the game.** If you're feeling distressed, we encourage you to seek professional help.

        Your choices and input will directly shape the direction of the story. Your decisions may influence the narrative, and some of your inputs might be used within the system to enhance your experience.

        **Audio Feature Option:**
        SootheAI can narrate the story using AI-generated speech. The audio is processed in real-time and not stored.

        **To begin:**
        Type 'I agree with audio' to enable voice narration
        OR
        Type 'I agree without audio' to continue with text only

        You can change audio settings at any time by typing 'enable audio' or 'disable audio'.
        """

    logger.info("GradioInterface initialized")

    def main_loop(self, message: Optional[str], history: List[Tuple[str, str]]) -> str:
        """
        Main game loop that processes player input and returns AI responses.

        Args:
            message: Player's input message
            history: Conversation history

        Returns:
            AI's response or error message
        """
        # Handle None message
        if message is None:
            logger.info("Processing empty message in main loop")
            return self.consent_message

        # Log message processing
        logger.info(
            f"Processing message in main loop: {message[:50] if message else ''}...")

        # Process the message using narrative engine
        response, success = self.narrative_engine.process_message(message)

        # Process TTS if appropriate - only do this for game content, not consent messages
        if success and self.narrative_engine.game_state.is_consent_given() and message.lower() not in ['i agree', 'enable audio', 'disable audio', 'start game']:
            self.tts_handler.run_tts_with_consent_and_limiting(response)

        return response

    def create_interface(self) -> gr.ChatInterface:
        """
        Create the Gradio chat interface.

        Returns:
            Gradio ChatInterface instance
        """
        logger.info("Creating Gradio interface")

        # Create interface
        chat_interface = gr.ChatInterface(
            self.main_loop,  # Main processing function
            chatbot=gr.Chatbot(
                height=500,  # Set chat window height
                placeholder="Type 'I agree' to begin",  # Initial placeholder text
                show_copy_button=True,  # Enable message copying
                render_markdown=True,  # Enable markdown rendering
                # Start with consent message
                value=[[None, self.consent_message]]
            ),
            textbox=gr.Textbox(
                placeholder="Type 'I agree' to continue...",  # Input placeholder
                container=False,  # No container styling
                scale=7  # Input field width
            ),
            title="SootheAI",  # Application title
            theme="soft",  # Use soft theme for better readability
            examples=[  # Example actions for users
                "Listen to music",
                "Journal",
                "Continue the story"
            ],
            cache_examples=False,  # Don't cache examples
        )

        self.interface = chat_interface
        return chat_interface

    def launch(self, share: bool = True, server_name: str = "0.0.0.0", server_port: int = 7861) -> None:
        """
        Launch the web interface.

        Args:
            share: Whether to create a shareable link
            server_name: Server name to listen on
            server_port: Port to serve on
        """
        if self.interface is None:
            self.create_interface()

        logger.info("Launching Gradio interface")

        try:
            self.interface.launch(
                share=share,
                server_name=server_name,
                server_port=server_port
            )
            logger.info("Gradio interface launched successfully")
        except Exception as e:
            logger.error(f"Failed to launch Gradio interface: {str(e)}")
            raise

    def close(self) -> None:
        """Close the Gradio interface."""
        if self.interface is not None:
            try:
                self.interface.close()
                logger.info("Closed Gradio interface")
            except Exception as e:
                logger.error(f"Error closing Gradio interface: {str(e)}")


def create_gradio_interface(character_data: Dict[str, Any], elevenlabs_client=None) -> GradioInterface:
    """
    Create a Gradio interface instance.

    Args:
        character_data: Character data dictionary
        elevenlabs_client: ElevenLabs client instance, if any

    Returns:
        GradioInterface instance
    """
    return GradioInterface(character_data, elevenlabs_client)
