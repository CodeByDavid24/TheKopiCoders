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
character = load_json('characters/serena')

# Define the system prompt that sets up the initial game state and rules
system_prompt = f"""
You are an AI gamemaster. Your job is to create an immersive adventure for the user playing as Serena, a 17-year-old Chinese Singaporean JC1 student working toward her goal of securing a place in NUS Medicine.

Serena's character profile:
- Name: {character['name']}
- Race: {character['physical']['race']['name']}
- Class: {character['class']['name']}
- Location: {character['location']['school']} in Singapore

Instructions:
- Begin with a brief introduction about Serena's life as a dedicated JC1 student taking {character['class']['subjects'][0]}, {character['class']['subjects'][1]}, {character['class']['subjects'][2]}, and {character['class']['subjects'][3]}, while serving as {character['class']['cca']}. Mention her academic standing and ambitions without revealing her internal struggles.
- Limit the introduction to one paragraph focusing on her academic environment, outward achievements, and goals.
- DO NOT explicitly mention anxiety, mental health issues, or her coping mechanisms - these should be subtly woven into the narrative for the player to discover.
- Create scenarios that naturally incorporate her behaviors (arriving early to sit at the back, taking meticulous notes but rarely asking questions, studying alone during breaks) without labeling them as anxiety-related.
- Occasionally introduce situations involving her triggers (being called on unexpectedly, group projects, receiving grades lower than expected, tight deadlines, social gatherings, comparisons with classmates) and observe how the player responds.
- Incorporate elements from her daily routine ({character['daily_routine']['morning']}, {character['daily_routine']['school_hours']}, {character['daily_routine']['after_school']}) to create realistic scenarios.
- Include interactions with her parents who are {character['relationships']['parents']}, her small circle of {character['relationships']['friends']}, and her teachers who {character['relationships']['teachers']}.
- Allow the user to respond freely to your scenarios and ask questions about Serena's life, background, and environment.
- After each significant interaction, present 4 clear options for what the player can do next that reflect realistic choices Serena might consider. Examples:
  1. Stay in the library until closing time to perfect your chemistry assignment
  2. Join your classmates who invited you for dinner, even though it means less study time
  3. Call it a day and go home to rest, knowing you have an early start tomorrow
  4. Find a quiet spot in the school garden to clear your mind before deciding

Remember: Serena doesn't view herself as having anxiety - she believes her reactions and feelings are normal parts of being a JC student in Singapore's competitive academic environment. She attributes her physical symptoms (headaches, stomach aches) to academic pressure rather than anxiety. The story should allow the player to gradually recognize these patterns through gameplay while making choices that either reinforce or help address her unacknowledged anxiety.
"""

# Define the consent message
consent_message = """
**Start Game - Important Information**

**Warning & Consent:**
This is a fictional story designed to help you understand anxiety. Please be aware that some of the content may depict distressing situations. **Do not replicate or engage in any harmful actions shown in the game.** If you're feeling distressed, we encourage you to seek professional help.

Your choices and input will directly shape the direction of the story. Your decisions may influence the narrative, and some of your inputs might be used within the system to enhance your experience. By starting the game, you agree to these terms.

Type 'I agree' then 'Start game' to continue.
"""

# Add this at the top of your file, after the imports
try:
    print(f"Anthropic SDK version: {anthropic.__version__}")
except AttributeError:
    print("Could not determine Anthropic SDK version")

# Get API key from environment variable or use a placeholder that won't trigger detection
# To use this in production, set the CLAUDE_API_KEY environment variable:
# export CLAUDE_API_KEY=your_actual_key_here  (for Linux/Mac)
# set CLAUDE_API_KEY=your_actual_key_here     (for Windows)
CLAUDE_API_KEY = os.environ.get(
    "CLAUDE_API_KEY", "REPLACE_WITH_YOUR_API_KEY_BEFORE_RUNNING")

# Initialize Claude client - handling proxy settings error
try:
    # First attempt with standard initialization
    claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
except TypeError as e:
    if "unexpected keyword argument 'proxies'" in str(e):
        # Try importing and using httpx directly to avoid the proxies issue
        import httpx
        http_client = httpx.Client()
        try:
            # Try with custom http client
            claude_client = anthropic.Anthropic(
                api_key=CLAUDE_API_KEY, http_client=http_client)
        except Exception:
            # Last resort - try older client style
            try:
                claude_client = anthropic.Client(api_key=CLAUDE_API_KEY)
            except Exception:
                print(
                    "Failed to initialize Claude client. Please check your Anthropic SDK version.")
                claude_client = None
    else:
        # Different type error
        print(f"Error initializing Claude client: {e}")
        claude_client = None
except Exception as e:
    print(f"Error initializing Claude client: {e}")
    claude_client = None

# Initialize game state
game_state = {
    'seed': np.random.randint(0, 1000000),  # Initial seed
    'character': character,  # Store character data
    'history': [],  # Track conversation history
    'consent_given': False,  # Track whether user has given consent
    'start': None  # Will store the starting narrative
}

demo = None  # Global variable to store Gradio interface instance for restart capability

# Remove the initialize_claude_client function since we're not using it anymore


def get_initial_response():
    """Get the initial game narrative from Claude"""
    global game_state, claude_client

    if not claude_client:
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    try:
        # Create the initial message for Claude
        # Check which version of the SDK we're using based on the client type
        if isinstance(claude_client, anthropic.Anthropic):
            # New SDK version
            response = claude_client.messages.create(
                model="claude-3-5-sonnet-20240620",  # Use an appropriate Claude model
                system=system_prompt,
                messages=[
                    {"role": "user", "content": "Start the game with a brief introduction to Serena."}
                ],
                temperature=0,
                max_tokens=1000
            )
            # Store the starting narrative
            game_state['start'] = response.content[0].text
        else:
            # Older SDK version
            response = claude_client.completion(
                prompt=f"\n\nHuman: Start the game with a brief introduction to Serena.\n\nAssistant:",
                model="claude-3-5-sonnet-20240620",
                temperature=0,
                max_tokens_to_sample=1000,
                stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
            )
            # Store the starting narrative
            game_state['start'] = response.completion

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
        if isinstance(claude_client, anthropic.Anthropic):
            # New SDK version
            # Prepare message history for Claude
            claude_messages = []

            # Add conversation history from game_state
            if len(game_state['history']) > 0 or len(history) > 0:
                for user_msg, assistant_msg in game_state['history']:
                    claude_messages.append(
                        {"role": "user", "content": user_msg})
                    claude_messages.append(
                        {"role": "assistant", "content": assistant_msg})

            # Add current message to conversation
            claude_messages.append({"role": "user", "content": message})

            # Get response from Claude API
            response = claude_client.messages.create(
                model="claude-3-5-sonnet-20240620",  # Use an appropriate Claude model
                system=system_prompt,
                messages=claude_messages,
                temperature=0,
                max_tokens=1000
            )

            # Process and store result
            result = response.content[0].text
        else:
            # Older SDK version
            # Convert history to the older Claude format
            prompt = "\n\nHuman: " + message + "\n\nAssistant:"

            response = claude_client.completion(
                prompt=prompt,
                model="claude-3-5-sonnet-20240620",
                temperature=0,
                max_tokens_to_sample=1000,
                stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
            )

            result = response.completion

        game_state['history'].append((message, result))
        return result

    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"


def main_loop(message: str, history: list) -> str:
    """
    Main game loop that processes player input and returns AI responses
    Args:
        message: Player's input message
        history: Conversation history
    Returns:
        String containing AI's response
    """
    global game_state

    # Process the action using the game state
    return run_action(message, history, game_state)


def start_game() -> None:
    """
    Initialize and launch the Gradio interface for the game
    """
    global demo, game_state

    # Ensure game state is initialized with consent_given as False
    if 'consent_given' not in game_state:
        game_state['consent_given'] = False

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
            render_markdown=True,
            # Start with consent message already shown
            value=[[None, consent_message]]
        ),
        textbox=gr.Textbox(placeholder="Type 'I agree' to continue...",
                           container=False, scale=7),
        title="SootheAI",
        theme="soft",
        examples=["Listen to music", "Journal", "Continue the story"],
        cache_examples=False,
    )

    # Set the interface directly without tabs since we removed the API key tab
    demo = chat_interface

    # Launch the interface
    demo.launch(share=True, server_name="0.0.0.0", server_port=7861)


# Start the application when script is run
if __name__ == "__main__":
    start_game()
