"""
SootheAI Main Application Entry Point

This module serves as the entry point for the SootheAI application,
an interactive narrative experience about a character named Serena
to help users understand anxiety.
"""

# Import core API client for Claude integration
from soothe_app.v1.core.api_client import get_claude_client
# Import Gradio interface creation function
from soothe_app.v1.ui.gradio_interface import create_gradio_interface
# Import content filtering initialization for safety
from soothe_app.v1.utils.safety import initialize_content_filter
# Import character data loading utility
from soothe_app.v1.utils.file_loader import load_character_data
# Import logging configuration utility
from soothe_app.v1.utils.logger import configure_logging

# Standard library imports for system operations
import os
import sys
import logging
# Import ElevenLabs for text-to-speech functionality
from elevenlabs import ElevenLabs
# Import environment variable loading
from dotenv import load_dotenv

# Add the project root to the Python path for module imports
project_root = os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))  # Get project root directory
sys.path.insert(0, project_root)  # Insert at beginning of path for priority

# Then use imports from soothe_app

# Load environment variables from .env file in project root
load_dotenv()


def main():
    """
    Main entry point for the application.

    Initializes all necessary components and launches the web interface.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Configure logging with file output and console output at INFO level
    configure_logging(log_file='soothe_app.log', console_level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get logger for this module
    logger.info("Starting SootheAI application")  # Log application startup

    # Initialize content filter for safety checking user inputs and responses
    initialize_content_filter()

    # Set up ElevenLabs client for TTS (Text-to-Speech) functionality
    elevenlabs_client = None  # Initialize as None in case API key not available
    elevenlabs_api_key = os.environ.get(
        "ELEVENLABS_API_KEY")  # Get API key from environment
    if elevenlabs_api_key:  # Only initialize if API key is available
        logger.info("Setting up ElevenLabs client")  # Log setup attempt
        try:
            # Initialize client with API key
            elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
            # Log successful initialization
            logger.info("ElevenLabs client initialized successfully")
        except Exception as e:
            # Log initialization failure
            logger.error(f"Failed to initialize ElevenLabs client: {str(e)}")
    else:
        logger.warning(
            "ELEVENLABS_API_KEY environment variable not set, TTS will be disabled")  # Log missing API key

    # Initialize Claude client for AI conversation functionality
    claude_client = get_claude_client()
    if not claude_client.is_ready():  # Check if client initialization was successful
        logger.error(
            f"Failed to initialize Claude client: {claude_client.get_error()}")  # Log initialization failure
        # Print error to console for user
        print(f"Error: {claude_client.get_error()}")
        return 1  # Return error exit code

    # Load character data (Serena's personality, background, etc.)
    character_data = load_character_data()
    logger.info(
        f"Loaded character data for {character_data.get('name', 'unknown')}")  # Log character data loading

    try:
        # Create and launch the UI
        logger.info("Creating Gradio interface")  # Log interface creation
        interface = create_gradio_interface(
            character_data, elevenlabs_client)  # Create web interface

        # Launch the web interface with sharing enabled on all network interfaces
        interface.launch(share=True, server_name="0.0.0.0", server_port=7861)

        return 0  # Return success exit code
    except KeyboardInterrupt:
        logger.info("Application terminated by user")  # Log user termination
        return 0  # Return success exit code (graceful shutdown)
    except Exception as e:
        # Log critical error with traceback
        logger.critical(f"Unhandled exception: {str(e)}", exc_info=True)
        return 1  # Return error exit code


if __name__ == "__main__":
    sys.exit(main())  # Exit with the return code from main function
