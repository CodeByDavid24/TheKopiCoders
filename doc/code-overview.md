# SootheAI Application - Lecture Notes

## Introduction

SootheAI is an interactive, conversational application that leverages the Claude AI API to create an immersive narrative experience focused on mental health awareness. The application simulates interactions with a character named Serena, a 17-year-old Chinese Singaporean JC1 student who is experiencing anxiety but doesn't recognize it as such. The game aims to help users understand anxiety through interactive storytelling.

## Application Architecture

The application is built with:

- **Python** - Core programming language
- **Gradio** - Web interface framework
- **Anthropic Claude API** - AI model for generating narrative responses
- **Logging** - For application monitoring and debugging

## Code Structure and Key Components

### 1. Imports and Dependencies

```python
import gradio as gr  # Web interface
import anthropic  # Claude API client
import json  # For configuration files
import numpy as np  # For random number generation
import os  # For environment variables
import logging  # Application monitoring
import logging.handlers  # For log file rotation
import httpx  # HTTP client
import sys  # System parameters
from dotenv import load_dotenv  # Environment variables
```

### 2. Logging Configuration

The application uses Python's built-in logging module with a rotating file handler:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'soothe_app.log',
            maxBytes=1024*1024,  # 1MB per file
            backupCount=5  # Keep 5 backup files
        ),
        logging.StreamHandler(sys.stdout)  # Also log to console
    ]
)
```

### 3. Character Data Management

Character data is loaded from JSON files:

```python
def load_json(filename: str) -> dict:
    """Load and parse a JSON file, returning an empty dict if file not found."""
    try:
        with open(f'{filename}.json', 'r', encoding='utf-8') as file:
            logger.info(f"Loading JSON file: {filename}.json")
            return json.load(file)
    except FileNotFoundError:
        logger.warning(f"JSON file not found: {filename}.json")
        return {}
    # Additional error handling...

# Load character data
character = load_json('characters/serena')
```

### 4. Claude API Integration

The application connects to the Claude API for AI-powered responses:

```python
def initialize_claude_client() -> tuple[anthropic.Anthropic | None, str]:
    """Initialize the Claude API client with proper error handling."""
    # Get API key from environment variable
    api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        logger.error("CLAUDE_API_KEY environment variable not set")
        return None, "CLAUDE_API_KEY environment variable not set"

    try:
        # Standard initialization
        return anthropic.Anthropic(api_key=api_key), ""
    except TypeError as e:
        # Handle proxy configuration issues
        if "unexpected keyword argument 'proxies'" in str(e):
            try:
                # Try with custom http client
                http_client = httpx.Client()
                return anthropic.Anthropic(api_key=api_key, http_client=http_client), ""
            except Exception as e:
                return None, f"Failed to initialize Claude client: {str(e)}"
        else:
            return None, f"TypeError: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"
```

### 5. System Prompt Configuration

The system prompt defines the game's rules and character details:

```python
system_prompt = f"""
You are an AI gamemaster. Your job is to create an immersive adventure for the user playing as Serena, a 17-year-old Chinese Singaporean JC1 student working toward her goal of securing a place in NUS Medicine.

Serena's character profile:
- Name: {character.get('name', 'Serena')}
- Race: {character.get('physical', {}).get('race', {}).get('name', 'Chinese')}
- Class: {character.get('class', {}).get('name', 'JC1')}
- Location: {character.get('location', {}).get('school', 'Unknown')} in Singapore

# Additional instructions...
"""
```

### 6. Game State Management

The application maintains a game state to track conversation history and user preferences:

```python
GameState = dict[str, int | dict | list | bool | None]  # Type alias

game_state: GameState = {
    'seed': np.random.randint(0, 1000000),  # For reproducibility
    'character': character,  # Store character data
    'history': [],  # Track conversation history
    'consent_given': False,  # Track user consent
    'start': None  # Will store the starting narrative
}
```

### 7. Initial Response Generation

The application gets the initial game narrative from Claude:

```python
def get_initial_response() -> str:
    """Get the initial game narrative from Claude."""
    global game_state, claude_client

    if not claude_client:
        logger.error("Claude client not initialized")
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    try:
        # Create the initial message for Claude
        logger.info("Requesting initial narrative from Claude API")
        
        # Check which version of the SDK we're using
        if hasattr(claude_client, 'messages'):
            # New SDK version (>=0.18.1)
            response = claude_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": "Start the game with a brief introduction to Serena."
                }],
                system=system_prompt
            )
            game_state['start'] = response.content[0].text
        else:
            # Older SDK version
            response = claude_client.completion(
                prompt=f"\n\nHuman: Start the game with a brief introduction to Serena.\n\nAssistant:",
                model="claude-2.1",
                temperature=0,
                max_tokens_to_sample=1000,
                stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
            )
            game_state['start'] = response.completion

        return game_state['start']
    except Exception as e:
        error_msg = f"Error communicating with Claude API: {str(e)}"
        logger.error(error_msg)
        return error_msg
```

### 8. Action Processing

The application processes user actions and generates appropriate responses:

```python
def run_action(message: str, history: list[tuple[str, str]], game_state: GameState) -> str:
    """Process player actions and generate appropriate responses."""
    global claude_client

    # Check if Claude client is configured
    if not claude_client:
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    # Check if consent has been given
    if not game_state['consent_given']:
        if message.lower() == 'i agree':
            game_state['consent_given'] = True
            return "Thank you for agreeing to the terms. Type 'start game' to begin."
        else:
            return consent_message

    # Check if this is the start of the game
    if message.lower() == 'start game':
        # If we haven't generated the start yet, do it now
        if game_state['start'] is None:
            game_state['start'] = get_initial_response()
        return game_state['start']

    try:
        # Handle different SDK versions
        if hasattr(claude_client, 'messages'):
            # New SDK version - prepare message history and get response
            # ...
        else:
            # Older SDK version
            # ...

        # Update game state and return result
        game_state['history'].append((message, result))
        return result

    except Exception as e:
        error_msg = f"Error communicating with Claude API: {str(e)}"
        logger.error(error_msg)
        return error_msg
```

### 9. Main Game Loop

The main game loop processes player input and returns AI responses:

```python
def main_loop(message: str | None, history: list[tuple[str, str]]) -> str:
    """Main game loop that processes player input and returns AI responses."""
    global game_state

    # Handle None message
    if message is None:
        return consent_message

    # Process the action using the game state
    return run_action(message, history, game_state)
```

### 10. Gradio Web Interface

The application uses Gradio to create a user-friendly web interface:

```python
def start_game() -> None:
    """Initialize and launch the Gradio interface for the game."""
    global demo, game_state

    # Create game interface
    chat_interface = gr.ChatInterface(
        main_loop,  # Main processing function
        chatbot=gr.Chatbot(
            height=500,
            placeholder="Type 'I agree' to begin",
            show_copy_button=True,
            render_markdown=True,
            value=[[None, consent_message]]  # Start with consent message
        ),
        textbox=gr.Textbox(
            placeholder="Type 'I agree' to continue...",
            container=False,
            scale=7
        ),
        title="SootheAI",
        theme="soft",
        examples=[
            "Listen to music",
            "Journal",
            "Continue the story"
        ],
        cache_examples=False,
    )

    # Set the interface
    demo = chat_interface

    # Launch the interface
    try:
        demo.launch(
            share=True,
            server_name="0.0.0.0",
            server_port=7861
        )
    except Exception as e:
        logger.error(f"Failed to launch game interface: {str(e)}")
        raise
```

### 11. Application Startup

The application starts when the script is run:

```python
if __name__ == "__main__":
    logger.info("Starting SootheAI application")
    try:
        start_game()  # Launch the game interface
    except Exception as e:
        logger.critical(f"Critical error in main application: {str(e)}")
        raise
```

## Log Analysis

The application logs reveal several important insights:

1. **Environment Variable Issues**: Initially, the application had issues with the CLAUDE_API_KEY environment variable not being set.
2. **Client Initialization**: There were some attempts with proxy configuration problems.
3. **SDK Version Compatibility**: The logs indicate issues with different versions of the Anthropic SDK.
4. **Successful API Calls**: Eventually, after fixing configuration issues, the application successfully communicated with the Claude API.

## Key Concepts

### Error Handling

The application implements comprehensive error handling with:

- Try-except blocks for all API calls
- Detailed logging of errors
- Graceful fallbacks when operations fail
- User-friendly error messages

### API Version Compatibility

The code handles different versions of the Anthropic SDK:

- It checks for the presence of the `messages` attribute to determine SDK version
- It provides alternate code paths for older versions using `completion` API
- It includes fallbacks for proxy configuration issues

### State Management

The application maintains game state to track:

- Conversation history
- User consent status
- Character data
- Initial narrative

### User Consent Flow

The application implements a consent flow:

1. Display consent message
2. Require user to type "I agree"
3. Prompt user to type "start game"
4. Begin the narrative

## Execution Flow

1. Load environment variables and configure logging
2. Load character data from JSON files
3. Initialize Claude API client
4. Set up game state
5. Start Gradio web interface
6. Wait for user to provide consent
7. Generate initial narrative
8. Process user actions and generate responses
9. Update game state with conversation history

## Conclusion

SootheAI demonstrates a well-structured application that:

- Combines web technologies with AI capabilities
- Implements proper error handling and logging
- Provides a user-friendly interface for interactive storytelling
- Addresses sensitive topics (mental health) in an educational format
- Uses external configuration for character data and system prompts

The application shows good software engineering practices including:

- Type hints for better code readability
- Comprehensive error handling
- Detailed logging
- Clear documentation
- Modular design
