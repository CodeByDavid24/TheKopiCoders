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


# Initialize conversation with system prompt
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f'Your Start:'}
]

# Initialize game state first
game_state = {
    'seed': np.random.randint(0, 1000000),  # Initial seed
    'character': character,  # Store character data
    'history': []  # Track conversation history
}

# Get initial response from the AI model
model_output = ollama.chat(
    model='mattw/llama2-13b-tiefighter',
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
        model='llama3',
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
            placeholder="Type 'start game' to begin",
            bubble_full_width=False,
            show_copy_button=True,
            render_markdown=True
        ),
        textbox=gr.Textbox(placeholder="What do you do next?",
                           container=False, scale=7),
        title="SootheAI",
        # description=f"You are playing as {character['name']}. {character['backstory']['description']}",
        theme="soft",
        examples=["Look around", "Continue the story"],
        cache_examples=False,
        retry_btn="Retry",
        undo_btn="Undo",
        clear_btn="Clear",
    )
    # Launch the interface
    demo.launch(share=True, server_name="0.0.0.0", server_port=7861)


# Start the game when script is run
start_game(main_loop)
