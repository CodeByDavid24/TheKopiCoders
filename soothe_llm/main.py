import gradio as gr  # Import Gradio for creating web interfaces
import ollama  # Import Ollama for AI model interactions
import json  # Import JSON for handling configuration files
import numpy as np


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
You are an AI gamemaster. Your job is to create an adventure for {character['name']} who is trying to achieve {character['backstory']['goals']}, {character['name']} is {character['backstory']['description']}.
The user is playing as {character['name']}, a {character['physical']['race']['name']} {character['class']['name']} living in {character['location']}.
{character['name']} has anxiety, her anxiety triggers are {character['anxiety_triggers']}, she copes by {character['coping_mechanism']}

{character['name']} character profile
Race: {character['physical']['race']['name']} 
Class: {character['class']['name']}

Instructions:

- Write in first person. For example: "{character['name']}, a {character['physical']['race']['name']} {character['class']['name']}" 
- Write in present tense. For example "You stand at..."
- Limit to only 1 paragraph 
- Include sensory details that convey Serena's anxiety state
- Incorporate the character's {character['behaviour']} in every response
- Always end by presenting 4 clear options for what the player can do next.

Format choices as numbered options:
1. Suggest Serena take a moment to practice deep breathing before entering the classroom
2. Encourage Serena to tell the teacher she forgot her homework and needs an extension
3. Recommend Serena skip lunch to keep studying for the afternoon test
4. Ask Serena about her favorite class this semester
"""

# Define the consent message
consent_message = """
**Start Game - Important Information**

**Warning & Consent:**
This is a fictional story designed to help you understand anxiety. Please be aware that some of the content may depict distressing situations. **Do not replicate or engage in any harmful actions shown in the game.** If you're feeling distressed, we encourage you to seek professional help.

Your choices and input will directly shape the direction of the story. Your decisions may influence the narrative, and some of your inputs might be used within the system to enhance your experience. By starting the game, you agree to these terms.

Type 'I agree' to continue.
"""

# Initialize conversation with system prompt
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f'Your Start:'}
]

# Initialize game state first
game_state = {
    'seed': np.random.randint(0, 1000000),  # Initial seed
    'character': character,  # Store character data
    'history': [],  # Track conversation history
    'consent_given': False  # Track whether user has given consent
}

# Get initial response from the AI model
model_output = ollama.chat(
    model='mistral',
    messages=messages,
    options={'temperature': 0, 'seed': game_state['seed']},
    stream=False,
)

# Store the starting narrative
game_state['start'] = model_output['message']['content']

demo = None  # Global variable to store Gradio interface instance for restart capability


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
    # Check if consent has been given
    if not game_state['consent_given']:
        if message.lower() == 'i agree':
            game_state['consent_given'] = True
            return "Thank you for agreeing to the terms. Type 'start game' to begin."
        else:
            return consent_message

    # Check if this is the start of the game
    if message.lower() == 'start game':
        return game_state['start']

    # Initialize new messages list with the gameplay system prompt
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add the game's start message and appropriate history
    if len(game_state['history']) > 0 or len(history) > 0:
        # First add the game start message
        messages.append({"role": "assistant", "content": game_state['start']})

        # Then add conversation history from game_state
        for user_msg, assistant_msg in game_state['history']:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})

    # Add current message to conversation
    messages.append({"role": "user", "content": message})

    # Get response from AI model
    model_output = ollama.chat(
        model='mistral',
        messages=messages,
        # Use seed from game_state
        options={'temperature': 0, 'seed': game_state['seed']},
        stream=False,
    )

    # Process and store result
    result = model_output['message']['content']
    game_state['history'].append((message, result))
    return result


def main_loop(message: str, history: list) -> str:
    """
    Main game loop that processes player input and returns AI responses
    Args:
        message: Player's input message
        history: Conversation history
    Returns:
        String containing AI's response
    """
    if not history:
        # First message in conversation, show consent message
        return consent_message
    return run_action(message, history, game_state)


def start_game(main_loop: callable, share: bool = False) -> None:
    """
    Initialize and launch the Gradio interface for the game
    Args:
        main_loop: Function handling the main game logic
        share: Boolean indicating whether to create a shareable link
    """
    # Access global demo variable for restart functionality
    global demo
    # Close existing demo if it exists
    if demo is not None:
        demo.close()

    # Create new Gradio interface with specified configuration
    demo = gr.ChatInterface(
        main_loop,
        chatbot=gr.Chatbot(
            height=500,
            placeholder="Type 'I agree' and then 'start game' to begin",
            bubble_full_width=False,
            show_copy_button=True,
            render_markdown=True
        ),
        textbox=gr.Textbox(placeholder="Type 'I agree' to continue...",
                           container=False, scale=7),
        title="SootheAI",
        theme="soft",
        examples=["I agree", "Start game",
                  "Look around", "Continue the story"],
        cache_examples=False,
        retry_btn="Retry",
        undo_btn="Undo",
        clear_btn="Clear",
    )
    # Launch the interface
    demo.launch(share=True, server_name="0.0.0.0", server_port=7861)


# Start the game when script is run
start_game(main_loop)
