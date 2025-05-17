"""
SootheAI Main Application Entry Point

This module serves as the entry point for the SootheAI application,
an interactive narrative experience about a character named Serena
to help users understand anxiety.
"""

import os
import sys
import logging
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

# Add the project root to the Python path to enable relative imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import our module components
from src.utils.logger import configure_logging
from src.utils.file_loader import load_character_data
from src.utils.safety import initialize_content_filter
from src.ui.gradio_interface import create_gradio_interface
from src.core.api_client import get_claude_client

# Load environment variables from .env file
load_dotenv()

def main():
    """Main entry point for the application."""
    # Configure logging
    configure_logging(log_file='soothe_app.log', console_level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting SootheAI application")
    
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
        logger.warning("ELEVENLABS_API_KEY environment variable not set, TTS will be disabled")
    
    # Initialize Claude client
    claude_client = get_claude_client()
    if not claude_client.is_ready():
        logger.error(f"Failed to initialize Claude client: {claude_client.get_error()}")
        print(f"Error: {claude_client.get_error()}")
        return 1
    
    # Load character data
    character_data = load_character_data()
    logger.info(f"Loaded character data for {character_data.get('name', 'unknown')}")
    
    try:
        # Create and launch the UI
        logger.info("Creating Gradio interface")
        interface = create_gradio_interface(character_data, elevenlabs_client)
        
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
