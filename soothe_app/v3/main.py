"""
SootheAI Main Application Entry Point

This module serves as the entry point for the SootheAI application,
an interactive narrative experience with autonomous character generation.
"""

from soothe_app.v3.core.api_client import get_claude_client
from soothe_app.v3.ui.gradio_interface import create_gradio_interface
from soothe_app.v3.utils.safety import initialize_content_filter
from soothe_app.v3.utils.logger import configure_logging

import os
import sys
import logging
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv()


def main():
    """Main entry point for the application."""
    # Configure logging
    configure_logging(log_file='soothe_app.log', console_level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting SootheAI application with autonomous character generation")

    # Initialize content filter
    initialize_content_filter()

    # Set up ElevenLabs client for TTS
    elevenlabs_client = None
    elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
    if elevenlabs_api_key:
        logger.info("Setting up ElevenLabs client")
        try:
            elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
            logger.info("ElevenLabs client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs client: {str(e)}")
    else:
        logger.warning(
            "ELEVENLABS_API_KEY environment variable not set, TTS will be disabled")

    # Initialize Claude client
    claude_client = get_claude_client()
    if not claude_client.is_ready():
        logger.error(
            f"Failed to initialize Claude client: {claude_client.get_error()}")
        print(f"Error: {claude_client.get_error()}")
        return 1

    try:
        # Create and launch the UI without character data
        logger.info("Creating autonomous Gradio interface")
        interface = create_gradio_interface(elevenlabs_client)  # Remove character_data parameter

        # Launch the web interface
        interface.launch(share=True, server_name="0.0.0.0", server_port=7861)

        return 0
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        return 0
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())