# SootheAI: Understanding the Code Behind an Anxiety Awareness Game

## 1. Introduction

SootheAI is an interactive narrative game designed to help users understand anxiety through a character-driven story. The application uses the Claude LLM (Large Language Model) to create an immersive experience where players take on the role of "Serena," a 17-year-old Singaporean student dealing with unacknowledged anxiety while pursuing academic excellence.

This document provides a comprehensive breakdown of the code structure, explaining how it works and the key components that power this psychological awareness tool.

## 2. Technical Overview

The application is built using:

- **Gradio**: For the web interface
- **Anthropic's Claude API**: For the AI-driven conversation
- **JSON**: For storing character data and configurations
- **NumPy**: For random seed generation

## 3. Code Structure Analysis

### 3.1 Imports and Dependencies

```python
import gradio as gr  # Web interface creation
import anthropic  # Claude API interactions
import json  # Configuration handling
import numpy as np  # For random seed generation
import os  # Environment variable access
```

### 3.2 Configuration and Setup Functions

#### Character Data Loading

```python
def load_json(filename: str) -> dict:
    """
    Load and parse a JSON file, returning an empty dict if file not found
    Args:
        filename: Name of the JSON file without extension
    Returns:
        Dict containing parsed JSON data or empty dict if file not found
    """
    try:
        with open(f'{filename}.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Load character data from JSON file
character = load_json('characters/serena')
```

This function loads character data from a JSON file, which contains information about Serena's background, personality traits, relationships, and daily routines.

### 3.3 System Prompt Configuration

The system prompt is a crucial component that sets the behavior of the AI. It contains detailed instructions for the Claude model on how to act as a gamemaster:

```python
system_prompt = f"""
You are an AI gamemaster. Your job is to create an immersive adventure for the user playing as Serena, a 17-year-old Chinese Singaporean JC1 student working toward her goal of securing a place in NUS Medicine.

Serena's character profile:
- Name: {character['name']}
- Race: {character['physical']['race']['name']}
- Class: {character['class']['name']}
- Location: {character['location']['school']} in Singapore

Instructions:
[... detailed instructions for the AI about how to present scenarios, handle the character's anxiety, etc.]
"""
```

This prompt:

1. Defines the character's basic information
2. Provides instructions on how to present the narrative
3. Sets rules for incorporating anxiety elements without explicit labeling
4. Outlines how to present choices to the player

### 3.4 API Authentication and Client Initialization

```python
# Get API key from environment variable
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "REPLACE_WITH_YOUR_API_KEY_BEFORE_RUNNING")

# Initialize Claude client with error handling for different SDK versions
try:
    # First attempt with standard initialization
    claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
except TypeError as e:
    if "unexpected keyword argument 'proxies'" in str(e):
        # Handle proxy issues with alternative initialization methods
        # ...
    else:
        # Different type error
        print(f"Error initializing Claude client: {e}")
        claude_client = None
except Exception as e:
    print(f"Error initializing Claude client: {e}")
    claude_client = None
```

The code carefully handles the initialization of the Claude client with robust error handling for different versions of the Anthropic SDK.

### 3.5 Game State Management

```python
# Initialize game state
game_state = {
    'seed': np.random.randint(0, 1000000),  # Initial seed
    'character': character,  # Store character data
    'history': [],  # Track conversation history
    'consent_given': False,  # Track whether user has given consent
    'start': None  # Will store the starting narrative
}
```

The game state dictionary keeps track of:

- A random seed for potential randomization
- The character data
- Conversation history
- Whether the user has consented to playing
- The initial narrative from Claude

### 3.6 Initial Response Generation

```python
def get_initial_response():
    """Get the initial game narrative from Claude"""
    global game_state, claude_client

    if not claude_client:
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    try:
        # Create the initial message for Claude
        # Check which version of the SDK we're using based on the client type
        if isinstance(claude_client, anthropic.Anthropic):
            # New SDK version API call
            # ...
        else:
            # Older SDK version API call
            # ...

        return game_state['start']
    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"
```

This function generates the initial narrative by making an API call to Claude, handling both new and older SDK versions.

### 3.7 Action Processing

```python
def run_action(message: str, history: list, game_state: dict) -> str:
    """
    Process player actions and generate appropriate responses
    """
    # Check Claude client configuration
    # Check consent status
    # Check for game start command
    
    try:
        # Handle different SDK versions for API calls
        # ...
        
        game_state['history'].append((message, result))
        return result
    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"
```

This function:

1. Checks if the Claude client is configured correctly
2. Verifies that the user has consented to playing
3. Handles the "start game" command
4. Makes API calls to Claude with the user's input
5. Updates the conversation history

### 3.8 Main Game Loop

```python
def main_loop(message: str, history: list) -> str:
    """
    Main game loop that processes player input and returns AI responses
    """
    if not history:
        # First message in conversation, show consent message
        return consent_message
    return run_action(message, history, game_state)
```

The main_loop function serves as the entry point for the Gradio chat interface, showing the consent message first and then processing actions.

### 3.9 Gradio Interface Setup

```python
def start_game() -> None:
    """
    Initialize and launch the Gradio interface for the game
    """
    global demo

    # Close existing demo if it exists
    if demo is not None:
        demo.close()

    # Create game interface
    chat_interface = gr.ChatInterface(
        main_loop,
        chatbot=gr.Chatbot(
            height=500,
            placeholder="Type 'I agree' to begin",
            show_copy_button=True,
            render_markdown=True
        ),
        textbox=gr.Textbox(placeholder="Type 'I agree' to continue...",
                           container=False, scale=7),
        title="SootheAI",
        theme="soft",
        examples=["Listen to music", "Journal", "Continue the story"],
        cache_examples=False,
    )

    # Set the interface
    demo = chat_interface

    # Launch the interface
    demo.launch(share=True, server_name="0.0.0.0", server_port=7861)
```

This function creates and launches the Gradio web interface for the game, configuring:

- The chat interface appearance
- Example messages
- The server configuration

## 4. Flow of Execution

1. When the script is run, `start_game()` is called
2. Gradio interface is initialized and launched
3. User sees consent message and must type "I agree"
4. After agreement, user types "start game" to begin
5. Initial narrative is generated from Claude API
6. User interacts with the game by typing messages
7. Claude responds with narrative and 4 choices for the player
8. Game continues as a conversation, with history maintained

## 5. Mental Health Design Elements

### Character Design

- Serena is designed as a high-achieving student with unacknowledged anxiety
- Her behaviors (sitting at the back, studying alone) subtly indicate anxiety without labeling
- The game avoids explicitly mentioning mental health issues until the player discovers them

### Educational Purpose

- The game helps users understand how anxiety manifests in everyday situations
- Players learn to recognize anxiety patterns by making choices for Serena
- The narrative presents realistic anxiety triggers in an academic setting

## 6. Technical Implementation Considerations

### API Compatibility

- The code handles both new and old versions of the Anthropic SDK
- Error handling for API initialization is robust
- Response formatting accounts for API version differences

### State Management

- Game state tracks conversation history, consent status, and character data
- Conversation flow is maintained between interactions
- Character information is injected into the system prompt for consistency

## 7. Deployment Information

The application is configured to run on:

- Server address: 0.0.0.0 (all network interfaces)
- Port: 7861
- With sharing enabled for remote access

## 8. Conclusion

SootheAI demonstrates how LLMs can be used for mental health education through interactive storytelling. The code combines web technologies, AI, and careful prompt engineering to create an experience that helps users understand anxiety in a simulated but realistic context.
