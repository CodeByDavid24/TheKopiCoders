import gradio as gr  # Import Gradio for creating web interfaces
import anthropic  # Import Anthropic for Claude API interactions
import json  # Import JSON for handling configuration files
import numpy as np
import os


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
character = load_json('serena')

# Define the system prompt that sets up the initial game state and rules
system_prompt = f"""
### Core Role
You are an AI game master generating an interactive fiction game about Serena, a quiet but determined high school student living with anxiety. 
She navigates academic pressures while battling insecurities and dreams of a better future, not just for her career, but for her self-worth. 
The narrative educates players about teenage anxiety while providing meaningful choices that impact Serena's journey.

### Player Character Framework
You are playing as {character['name']}, a {character['physical']['race']['name']} {character['class']['name']}.

### Character Data
Race: {character['physical']['race']['name']}
Class: {character['class']['name']}
Behaviors: {character['behaviour']} (MUST be incorporated into every response)

Instructions:

### Narrative Structure

#### Anxiety Scenarios
Frame scenarios around everyday high school situations where anxiety commonly manifests:

- Academic pressures (tests, presentations, college applications)
- Social interactions (classroom dynamics, lunch periods, school events)
- Extracurricular activities (clubs, sports, competitions)
- Family expectations (parent-teacher conferences, report cards)
- Identity development (self-image, future planning, peer comparison)

#### Difficulty Progression
Begin with manageable situations and gradually introduce more complex challenges:

- Early game: Routine class participation, casual friend interactions
- Mid game: Important exams, school social events, conflict with friends
- Late game: College decisions, confronting root causes of anxiety, setting boundaries

#### Interaction Mechanics
Response Format

Always write in second person present tense: "You, {character['name']} the {character['physical']['race']['name']} {character['class']['name']}, notice Serena's shoulders tense as she approaches the classroom door."
Limit each response to one concise, vivid paragraph (3-5 sentences maximum)
Include sensory details that convey Serena's anxiety state
Incorporate the character's defined behaviors in every response

#### Choice Structure
After each narrative paragraph, present 3-4 distinct options that represent:

- A healthy coping mechanism (deep breathing, positive self-talk, seeking support from counselor)
- An avoidance behavior (faking illness to skip class, procrastinating on assignments)
- An unhealthy coping strategy (pulling all-nighters, isolating from friends, negative self-talk)
- A neutral action (neither helpful nor harmful to anxiety management)

Format choices as numbered options:
1. Suggest Serena take a moment to practice deep breathing before entering the classroom
2. Encourage Serena to tell the teacher she forgot her homework and needs an extension
3. Recommend Serena skip lunch to keep studying for the afternoon test
4. Ask Serena about her favorite class this semester
"""

# Define the API key (replace with your actual API key or use environment variables)
CLAUDE_API_KEY = "your-api-key-here"

# Initialize Claude client - using a simpler initialization to avoid the proxies error
claude_client = None

# Initialize game state
game_state = {
    'seed': np.random.randint(0, 1000000),  # Initial seed
    'character': character,  # Store character data
    'history': [],  # Track conversation history
    'start': None  # Will store the starting narrative
}

demo = None  # Global variable to store Gradio interface instance for restart capability


def initialize_claude_client(api_key):
    """Initialize or update the Claude client with the given API key"""
    global claude_client
    try:
        # Simple initialization without extra parameters
        claude_client = anthropic.Anthropic(api_key=api_key)
        return "Claude API key configured successfully!"
    except Exception as e:
        return f"Error initializing Claude client: {str(e)}"


def get_initial_response():
    """Get the initial game narrative from Claude"""
    global game_state, claude_client

    if not claude_client:
        return "Claude API key not configured. Please set it in the API Key tab."

    try:
        # Create the initial message for Claude
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",  # Use Claude 3.5 Sonnet
            system=system_prompt,
            messages=[
                {"role": "user", "content": "Your Start:"}
            ],
            temperature=0,
            max_tokens=1000
        )

        # Store the starting narrative
        game_state['start'] = response.content[0].text
        return game_state['start']
    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"


def run_action(message: str, history: list, game_state: dict) -> str:
    """
    Process player actions and generate appropriate responses
    Args:
        message: Player's input message
        history: Conversation history from Gradio (list of [user_msg, assistant_msg] pairs)
        game_state: Current state of the game
    Returns:
        String containing AI's response to player action
    """
    global claude_client

    # Check if Claude client is configured
    if not claude_client:
        return "Claude API key not configured. Please set it up first."

    # Check if this is the start of the game
    if message.lower() == 'start game':
        # If we haven't generated the start yet, do it now
        if game_state['start'] is None:
            return get_initial_response()
        return game_state['start']

    try:
        # Prepare message history for Claude
        claude_messages = []

        # Add the game start message and appropriate history
        if len(game_state['history']) > 0 or len(history) > 0:
            # First add the game start message if we have it
            if game_state['start']:
                claude_messages.append(
                    {"role": "assistant", "content": game_state['start']})

            # Add conversation history from game_state
            for user_msg, assistant_msg in game_state['history']:
                claude_messages.append({"role": "user", "content": user_msg})
                claude_messages.append(
                    {"role": "assistant", "content": assistant_msg})

        # Add current message to conversation
        claude_messages.append({"role": "user", "content": message})

        # Get response from Claude API
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",  # Use Claude 3.5 Sonnet
            system=system_prompt,
            messages=claude_messages,
            temperature=0,
            max_tokens=1000
        )

        # Process and store result
        result = response.content[0].text
        game_state['history'].append((message, result))
        return result

    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"


def set_api_key(api_key: str):
    """
    Set the Claude API key and initialize the client
    Args:
        api_key: The API key to use for Claude
    Returns:
        Success or error message
    """
    global CLAUDE_API_KEY

    if not api_key.strip():
        return "API key cannot be empty"

    try:
        # Store the API key
        CLAUDE_API_KEY = api_key.strip()
        # Initialize the client
        result = initialize_claude_client(CLAUDE_API_KEY)
        return result
    except Exception as e:
        return f"Error setting API key: {str(e)}"


def main_loop(message: str, history: list) -> str:
    """
    Main game loop that processes player input and returns AI responses
    Args:
        message: Player's input message
        history: Conversation history
    Returns:
        String containing AI's response
    """
    return run_action(message, history, game_state)


def start_game() -> None:
    """
    Initialize and launch the Gradio interface for the game
    """
    global demo

    # Close existing demo if it exists
    if demo is not None:
        demo.close()

    # Create API key configuration tab
    with gr.Blocks(theme="soft") as api_block:
        gr.Markdown("# Claude API Configuration")
        with gr.Row():
            api_key_input = gr.Textbox(
                placeholder="Enter your Claude API Key",
                type="password",
                label="Claude API Key"
            )
            api_submit = gr.Button("Set API Key")
        api_result = gr.Textbox(label="Status", interactive=False)

        api_submit.click(
            fn=set_api_key,
            inputs=api_key_input,
            outputs=api_result
        )

    # Create game interface
    chat_interface = gr.ChatInterface(
        main_loop,
        chatbot=gr.Chatbot(
            height=500,
            placeholder="Type 'start game' to begin",
            bubble_full_width=False,
            show_copy_button=True,
            render_markdown=True
        ),
        textbox=gr.Textbox(placeholder="What do you do next?",
                           container=False, scale=7),
        title="SootheAI",
        theme="soft",
        examples=["Look around", "Continue the story"],
        cache_examples=False,
        retry_btn="Retry",
        undo_btn="Undo",
        clear_btn="Clear",
    )

    # Combine everything into tabs
    demo = gr.TabbedInterface(
        [api_block, chat_interface],
        ["API Key", "Game"],
        title="SootheAI"
    )

    # Launch the interface
    demo.launch(share=True, server_name="0.0.0.0", server_port=7861)


# Start the application when script is run
if __name__ == "__main__":
    # We don't initialize claude_client here anymore - it will be initialized when the API key is provided
    start_game()
