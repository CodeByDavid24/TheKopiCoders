import gradio as gr  # Import Gradio for creating web interfaces
import anthropic  # Import Anthropic for Claude API interactions
import json  # Import JSON for handling configuration files
import numpy as np  # Import NumPy for random number generation
import os  # Import OS for environment variables and file operations
import logging  # Import logging for application monitoring
import logging.handlers  # Import logging handlers for file rotation
import httpx  # Import httpx for HTTP client functionality
import sys  # Import sys for system-specific parameters and functions
from dotenv import load_dotenv  # Import dotenv for loading environment variables

# Import the blacklist module for content filtering
from blacklist import (
    load_blacklist_from_file,
    contains_blacklisted_content,
    filter_content,
    get_safety_disclaimer,
    get_safe_response_alternative
)

# Load environment variables from .env file
load_dotenv()  # Load environment variables from .env file
logger = logging.getLogger(__name__)  # Create logger instance before using it
# Log environment loading
logger.info("Loading environment variables from .env file")

# Configure logging with rotating file handler
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    # Define log format
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'soothe_app.log',  # Log file name
            maxBytes=1024*1024,  # Maximum size of 1MB per file
            backupCount=5  # Keep 5 backup files
        ),
        logging.StreamHandler(sys.stdout)  # Also log to console
    ]
)

# Create logger instance for this module
logger = logging.getLogger(__name__)

# Load blacklist from file at startup
try:
    blacklisted_phrases = load_blacklist_from_file()
    logger.info(f"Loaded {len(blacklisted_phrases)} blacklisted phrases")
except Exception as e:
    logger.error(f"Error loading blacklist: {str(e)}")
    blacklisted_phrases = []


def load_json(filename: str) -> dict:
    """
    Load and parse a JSON file, returning an empty dict if file not found.

    Args:
        filename (str): Name of the JSON file without extension

    Returns:
        dict: Parsed JSON data or empty dict if file not found

    Example:
        >>> character_data = load_json('characters/serena')
        >>> print(character_data['name'])
        'Serena'
    """
    try:
        with open(f'{filename}.json', 'r', encoding='utf-8') as file:  # Explicitly specify encoding
            # Log file loading attempt
            logger.info(f"Loading JSON file: {filename}.json")
            return json.load(file)
    except FileNotFoundError:
        # Log file not found warning
        logger.warning(f"JSON file not found: {filename}.json")
        return {}
    except json.JSONDecodeError as e:
        # Log JSON decode error
        logger.error(f"Error decoding JSON from {filename}.json: {str(e)}")
        return {}
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error loading {filename}.json: {str(e)}")
        return {}


# Load character data from JSON file with logging
# Log character data loading attempt
logger.info("Loading character data from JSON file")
character = load_json('characters/serena')  # Load character configuration

# Define the system prompt that sets up the initial game state and rules
system_prompt = f"""
You are an AI gamemaster. Your job is to create an immersive adventure for the user playing as Serena, a 17-year-old Chinese Singaporean JC1 student working toward her goal of securing a place in NUS Medicine.

Serena's character profile:
- Name: {character.get('name', 'Serena')}  # Use get() with default value for safety
- Race: {character.get('physical', {}).get('race', {}).get('name', 'Chinese')}
- Class: {character.get('class', {}).get('name', 'JC1')}
- Location: {character.get('location', {}).get('school', 'Unknown')} in Singapore

Instructions:
- Begin with a brief introduction about Serena's life as a dedicated JC1 student taking {character.get('class', {}).get('subjects', ['Unknown'])[0]}, {character.get('class', {}).get('subjects', ['Unknown'])[1]}, {character.get('class', {}).get('subjects', ['Unknown'])[2]}, and {character.get('class', {}).get('subjects', ['Unknown'])[3]}, while serving as {character.get('class', {}).get('cca', 'Unknown')}. Mention her academic standing and ambitions without revealing her internal struggles.
- Limit the introduction to one paragraph focusing on her academic environment, outward achievements, and goals.
- DO NOT explicitly mention anxiety, mental health issues, or her coping mechanisms - these should be subtly woven into the narrative for the player to discover.
- Create scenarios that naturally incorporate her behaviors (arriving early to sit at the back, taking meticulous notes but rarely asking questions, studying alone during breaks) without labeling them as anxiety-related.
- Occasionally introduce situations involving her triggers (being called on unexpectedly, group projects, receiving grades lower than expected, tight deadlines, social gatherings, comparisons with classmates) and observe how the player responds.
- Incorporate elements from her daily routine ({character.get('daily_routine', {}).get('morning', 'Unknown')}, {character.get('daily_routine', {}).get('school_hours', 'Unknown')}, {character.get('daily_routine', {}).get('after_school', 'Unknown')}) to create realistic scenarios.
- Include interactions with her parents who are {character.get('relationships', {}).get('parents', 'Unknown')}, her small circle of {character.get('relationships', {}).get('friends', 'Unknown')}, and her teachers who {character.get('relationships', {}).get('teachers', 'Unknown')}.
- Allow the user to respond freely to your scenarios and ask questions about Serena's life, background, and environment.
- After each significant interaction, present 4 clear options for what the player can do next that reflect realistic choices Serena might consider. Examples:
  1. Stay in the library until closing time to perfect your chemistry assignment
  2. Join your classmates who invited you for dinner, even though it means less study time
  3. Call it a day and go home to rest, knowing you have an early start tomorrow
  4. Find a quiet spot in the school garden to clear your mind before deciding

Remember: Serena doesn't view herself as having anxiety - she believes her reactions and feelings are normal parts of being a JC student in Singapore's competitive academic environment. She attributes her physical symptoms (headaches, stomach aches) to academic pressure rather than anxiety. The story should allow the player to gradually recognize these patterns through gameplay while making choices that either reinforce or help address her unacknowledged anxiety.

IMPORTANT: Avoid generating harmful, distressing, or unsafe content. Never suggest or describe self-harm or unsafe coping mechanisms. Focus on creating positive learning experiences about mental health awareness.
"""

# Add safety instructions to the system prompt to reinforce content guidelines
safety_instructions = """
CONTENT SAFETY GUIDELINES:
- Never generate content that describes or encourages self-harm, suicide, or dangerous behaviors
- Do not provide information about harmful coping mechanisms
- Always promote healthy coping strategies and seeking appropriate support
- Maintain an educational and supportive tone throughout the experience
- When discussing mental health challenges, balance realism with hope and guidance
- If the user introduces concerning content, redirect toward constructive alternatives
"""

# Append safety instructions to the system prompt
system_prompt += "\n\n" + safety_instructions

# Define the consent message with clear formatting
consent_message = """
**Start Game - Important Information**

**Warning & Consent:**
This is a fictional story designed to help you understand anxiety. Please be aware that some of the content may depict distressing situations. **Do not replicate or engage in any harmful actions shown in the game.** If you're feeling distressed, we encourage you to seek professional help.

Your choices and input will directly shape the direction of the story. Your decisions may influence the narrative, and some of your inputs might be used within the system to enhance your experience. By starting the game, you agree to these terms.

Type 'I agree' then 'Start game' to continue.
"""


def initialize_claude_client() -> tuple[anthropic.Anthropic | None, str]:
    """
    Initialize the Claude API client with proper error handling.

    Returns:
        tuple: (claude_client, error_message)
            - claude_client: Anthropic client instance or None if initialization fails
            - error_message: Error message string if initialization fails, empty string otherwise

    Example:
        >>> client, error = initialize_claude_client()
        >>> if client is None:
        ...     print(f"Failed to initialize client: {error}")
    """
    try:
        # Log version check attempt
        logger.info("Checking Anthropic SDK version")
        print(f"Anthropic SDK version: {anthropic.__version__}")
    except AttributeError:
        # Log version check failure
        logger.warning("Could not determine Anthropic SDK version")
        print("Could not determine Anthropic SDK version")

    # Get API key from environment variable
    api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        # Log missing API key
        logger.error("CLAUDE_API_KEY environment variable not set")
        return None, "CLAUDE_API_KEY environment variable not set"

    try:
        # First attempt with standard initialization
        # Log initialization attempt
        logger.info(
            "Attempting to initialize Claude client with standard configuration")
        return anthropic.Anthropic(api_key=api_key), ""
    except TypeError as e:
        if "unexpected keyword argument 'proxies'" in str(e):
            # Log proxy error
            logger.warning(
                "Proxy configuration error, attempting alternative initialization")
            try:
                # Try with custom http client
                http_client = httpx.Client()
                return anthropic.Anthropic(api_key=api_key, http_client=http_client), ""
            except Exception as e:
                # Log initialization failure
                logger.error(
                    f"Failed to initialize Claude client with custom HTTP client: {str(e)}")
                return None, f"Failed to initialize Claude client: {str(e)}"
        else:
            # Log type error
            logger.error(
                f"TypeError during Claude client initialization: {str(e)}")
            return None, f"TypeError: {str(e)}"
    except Exception as e:
        # Log unexpected error
        logger.error(
            f"Unexpected error during Claude client initialization: {str(e)}")
        return None, f"Unexpected error: {str(e)}"


# Initialize Claude client using the new function
claude_client, client_error = initialize_claude_client()
if client_error:
    # Log initialization failure
    logger.error(f"Failed to initialize Claude client: {client_error}")

# Initialize game state with type hints and documentation
GameState = dict[str, int | dict | list |
                 bool | None]  # Type alias for game state

game_state: GameState = {
    'seed': np.random.randint(0, 1000000),  # Initial seed for reproducibility
    'character': character,  # Store character data
    'history': [],  # Track conversation history
    'consent_given': False,  # Track whether user has given consent
    'start': None  # Will store the starting narrative
}

# Global variable to store Gradio interface instance for restart capability
demo: gr.Blocks | None = None


def check_input_safety(message: str) -> tuple[bool, str]:
    """
    Check user input for potentially harmful content.

    Args:
        message (str): User's input message

    Returns:
        tuple: (is_safe, safe_message)
            - is_safe: Boolean indicating if message is safe
            - safe_message: Original message or safety warning

    Example:
        >>> is_safe, message = check_input_safety("How can I help Serena cope with stress?")
        >>> print(is_safe, message)
        True "How can I help Serena cope with stress?"
    """
    # Check for blacklisted content
    has_blacklisted, matched_phrases = contains_blacklisted_content(
        message, blacklisted_phrases)

    if has_blacklisted:
        logger.warning(
            f"Detected harmful content in user input: {matched_phrases}")

        # Return a safety message
        safety_message = (
            "I notice your message contains content that might be sensitive or potentially harmful. "
            "In this experience, we focus on exploring healthy coping strategies and understanding anxiety. "
            "Please try rephrasing your message or exploring a different aspect of Serena's story."
        ) + get_safety_disclaimer()

        return False, safety_message

    return True, message


def filter_response_safety(response: str) -> str:
    """
    Filter LLM response for safety, replacing any harmful content.

    Args:
        response (str): LLM response to filter

    Returns:
        str: Filtered safe response

    Example:
        >>> safe_response = filter_response_safety("Serena considers studying all night.")
        >>> print(safe_response)
        "Serena considers studying all night."
    """
    # Check if response contains any blacklisted content
    has_blacklisted, matched_phrases = contains_blacklisted_content(
        response, blacklisted_phrases)

    if has_blacklisted:
        logger.warning(
            f"Detected harmful content in LLM response: {matched_phrases}")

        # For severe cases, replace the entire response
        if any(phrase in ["commit suicide", "kill myself", "end my life"] for phrase in matched_phrases):
            logger.error(
                f"Detected extremely harmful content in LLM response, replacing entirely")
            return get_safe_response_alternative()

        # For less severe cases, filter out the specific phrases
        filtered_response = filter_content(
            response, blacklist=blacklisted_phrases)

        # Add safety disclaimer
        filtered_response += get_safety_disclaimer()

        return filtered_response

    return response


def get_initial_response() -> str:
    """
    Get the initial game narrative from Claude.

    Returns:
        str: Initial narrative text or error message if request fails

    Example:
        >>> narrative = get_initial_response()
        >>> print(narrative)
        'Welcome to Serena's story...'
    """
    global game_state, claude_client

    if not claude_client:
        # Log missing client error
        logger.error("Claude client not initialized")
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    try:
        # Create the initial message for Claude
        # Log API request attempt
        logger.info("Requesting initial narrative from Claude API")

        # Check which version of the SDK we're using based on available methods
        if hasattr(claude_client, 'messages'):
            # New SDK version (>=0.18.1)
            response = claude_client.messages.create(
                model="claude-3-5-sonnet-20240620",  # Use latest stable model
                max_tokens=1000,  # Limit response length
                temperature=0,  # Use deterministic output
                messages=[{
                    "role": "user",
                    "content": "Start the game with a brief introduction to Serena."
                }],
                system=system_prompt  # Use predefined system prompt
            )
            # Store the starting narrative
            initial_narrative = response.content[0].text
        else:
            # Older SDK version
            # Log SDK version warning
            logger.warning(
                "Using older Anthropic SDK version with completion API")
            response = claude_client.completion(
                prompt=f"\n\nHuman: Start the game with a brief introduction to Serena.\n\nAssistant:",
                model="claude-2.1",  # Use older model for compatibility
                temperature=0,
                max_tokens_to_sample=1000,
                stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
            )
            # Store the starting narrative
            initial_narrative = response.completion

        # Filter the initial narrative for safety
        safe_narrative = filter_response_safety(initial_narrative)
        game_state['start'] = safe_narrative

        # Log successful response
        logger.info(
            "Successfully received and filtered initial narrative from Claude API")
        return safe_narrative
    except Exception as e:
        error_msg = f"Error communicating with Claude API: {str(e)}"
        logger.error(error_msg)  # Log API communication error
        return error_msg


def run_action(message: str, history: list[tuple[str, str]], game_state: GameState) -> str:
    """
    Process player actions and generate appropriate responses.

    Args:
        message (str): Player's input message
        history (list[tuple[str, str]]): Conversation history from Gradio
        game_state (GameState): Current state of the game

    Returns:
        str: AI's response to player action or error message

    Example:
        >>> response = run_action("I want to study in the library", [], game_state)
        >>> print(response)
        'Serena heads to the library...'
    """
    global claude_client

    # Check if Claude client is configured
    if not claude_client:
        # Log missing client error
        logger.error("Claude client not initialized")
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    # Check if consent has been given
    if not game_state['consent_given']:
        if message.lower() == 'i agree':
            logger.info("User consent received")  # Log consent given
            game_state['consent_given'] = True
            return "Thank you for agreeing to the terms. Type 'start game' to begin."
        else:
            # Log consent message display
            logger.info("Showing consent message to user")
            return consent_message

    # Check if this is the start of the game
    if message.lower() == 'start game':
        logger.info("Starting new game")  # Log game start
        # If we haven't generated the start yet, do it now
        if game_state['start'] is None:
            game_state['start'] = get_initial_response()
        return game_state['start']

    # Check user input for safety
    is_safe_input, safe_message = check_input_safety(message)
    if not is_safe_input:
        logger.warning("Blocked unsafe user input")
        return safe_message

    try:
        # Handle different SDK versions
        if hasattr(claude_client, 'messages'):
            # New SDK version
            # Prepare message history for Claude
            claude_messages = []

            # Add conversation history from game_state
            if len(game_state['history']) > 0 or len(history) > 0:
                for user_msg, assistant_msg in game_state['history']:
                    claude_messages.append({
                        "role": "user",
                        "content": user_msg
                    })
                    claude_messages.append({
                        "role": "assistant",
                        "content": assistant_msg
                    })

            # Add current message to conversation
            claude_messages.append({
                "role": "user",
                "content": message
            })

            # Log message being sent
            logger.info(f"Sending message to Claude API: {message[:50]}...")

            # Get response from Claude API
            response = claude_client.messages.create(
                model="claude-3-5-sonnet-20240620",  # Use latest stable model
                max_tokens=1000,  # Limit response length
                temperature=0,  # Use deterministic output
                messages=claude_messages,
                system=system_prompt  # Use predefined system prompt
            )

            # Process and store result
            result = response.content[0].text
        else:
            # Older SDK version
            # Log SDK version warning
            logger.warning(
                "Using older Anthropic SDK version with completion API")
            # Convert history to the older Claude format
            prompt = "\n\nHuman: " + message + "\n\nAssistant:"

            # Log message being sent
            logger.info(
                f"Sending message to Claude API (old SDK): {message[:50]}...")

            response = claude_client.completion(
                prompt=prompt,
                model="claude-2.1",  # Use older model for compatibility
                temperature=0,
                max_tokens_to_sample=1000,
                stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
            )

            result = response.completion

        # Filter the response for safety
        safe_result = filter_response_safety(result)

        # Log successful response and update game state
        # Log response received
        logger.info(
            f"Received and filtered response from Claude API: {safe_result[:50]}...")
        game_state['history'].append((message, safe_result))
        return safe_result

    except Exception as e:
        error_msg = f"Error communicating with Claude API: {str(e)}"
        logger.error(error_msg)  # Log API communication error
        return error_msg


def main_loop(message: str | None, history: list[tuple[str, str]]) -> str:
    """
    Main game loop that processes player input and returns AI responses.

    Args:
        message (str | None): Player's input message
        history (list[tuple[str, str]]): Conversation history

    Returns:
        str: AI's response or error message

    Example:
        >>> response = main_loop("Hello", [])
        >>> print(response)
        'Welcome to the game...'
    """
    global game_state

    # Handle None message
    if message is None:
        # Log empty message
        logger.info("Processing empty message in main loop")
        return consent_message

    # Log message processing safely
    logger.info(
        f"Processing message in main loop: {message[:50] if message else ''}...")
    # Process the action using the game state
    return run_action(message, history, game_state)


def start_game() -> None:
    """
    Initialize and launch the Gradio interface for the game.

    This function:
    1. Initializes the game state
    2. Creates the chat interface
    3. Configures the interface appearance
    4. Launches the web server

    Example:
        >>> start_game()  # Launches the web interface
    """
    global demo, game_state

    logger.info("Initializing game interface")  # Log game initialization

    # Ensure game state is initialized with consent_given as False
    if 'consent_given' not in game_state:
        game_state['consent_given'] = False

    # Close existing demo if it exists
    if demo is not None:
        logger.info("Closing existing game interface")  # Log interface closure
        demo.close()

    # Create game interface
    chat_interface = gr.ChatInterface(
        main_loop,  # Main processing function
        chatbot=gr.Chatbot(
            height=500,  # Set chat window height
            placeholder="Type 'I agree' to begin",  # Initial placeholder text
            show_copy_button=True,  # Enable message copying
            render_markdown=True,  # Enable markdown rendering
            value=[[None, consent_message]]  # Start with consent message
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

    # Set the interface
    demo = chat_interface

    logger.info("Launching game interface")  # Log interface launch
    # Launch the interface
    try:
        demo.launch(
            share=True,  # Enable sharing
            server_name="0.0.0.0",  # Listen on all interfaces
            server_port=7861  # Use port 7861
        )
        # Log successful launch
        logger.info("Game interface launched successfully")
    except Exception as e:
        # Log launch failure
        logger.error(f"Failed to launch game interface: {str(e)}")
        raise  # Re-raise the exception after logging


# Start the application when script is run
if __name__ == "__main__":
    logger.info("Starting SootheAI application")  # Log application start
    try:
        start_game()  # Launch the game interface
    except Exception as e:
        # Log critical errors
        logger.critical(f"Critical error in main application: {str(e)}")
        raise  # Re-raise the exception after logging
