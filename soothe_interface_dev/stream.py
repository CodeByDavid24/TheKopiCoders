import streamlit as st  # Import Streamlit for creating web interfaces
import anthropic  # Import Anthropic for Claude API interactions
import json  # Import JSON for handling configuration files
import numpy as np
import os
from typing import List, Tuple


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


def get_initial_response():
    """Get the initial game narrative from Claude"""
    global claude_client

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
            return response.content[0].text
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
            return response.completion

    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"


def run_action(message: str, conversation_history: List[Tuple[str, str]]) -> str:
    """
    Process player actions and generate appropriate responses
    Args:
        message: Player's input message
        conversation_history: Conversation history as a list of (user_msg, assistant_msg) tuples
    Returns:
        String containing AI's response to player action
    """
    global claude_client

    # Check if Claude client is configured
    if not claude_client:
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    # Check if consent has been given
    if not st.session_state.consent_given:
        if message.lower() == 'i agree':
            st.session_state.consent_given = True
            return "Thank you for agreeing to the terms. Type 'start game' to begin."
        else:
            return consent_message

    # Check if this is the start of the game
    if message.lower() == 'start game':
        # If we haven't generated the start yet, do it now
        if not st.session_state.start:
            st.session_state.start = get_initial_response()
        return st.session_state.start

    try:
        # Handle different SDK versions
        if isinstance(claude_client, anthropic.Anthropic):
            # New SDK version
            # Prepare message history for Claude
            claude_messages = []

            # Add conversation history
            for user_msg, assistant_msg in conversation_history:
                claude_messages.append(
                    {"role": "user", "content": user_msg})
                claude_messages.append(
                    {"role": "assistant", "content": assistant_msg})

            # Add current message to conversation
            claude_messages.append({"role": "user", "content": message})

            # Get response from Claude API
            response = claude_client.messages.create(
                model="claude-3.5-sonnet-20240620",  # Use an appropriate Claude model
                system=system_prompt,
                messages=claude_messages,
                temperature=0,
                max_tokens=1000
            )

            # Process result
            result = response.content[0].text
        else:
            # Older SDK version
            # Convert history to the older Claude format
            prompt = "\n\nHuman: " + message + "\n\nAssistant:"

            response = claude_client.completion(
                prompt=prompt,
                model="claude-3.5-sonnet-20240620",
                temperature=0,
                max_tokens_to_sample=1000,
                stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
            )

            result = response.completion

        return result

    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"


def display_message(message, is_user=False):
    """Display a message in the chat interface with improved visibility"""
    if is_user:
        message_container = st.chat_message("user", avatar="👤")
        # Add a light background for user messages
        with message_container:
            st.markdown(f"""
            <div style="background-color: #e6f7ff; padding: 10px; border-radius: 10px; color: #000000;">
                {message}
            </div>
            """, unsafe_allow_html=True)
    else:
        message_container = st.chat_message("assistant", avatar="🤖")
        # Add a light background for assistant messages
        with message_container:
            st.markdown(f"""
            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px; color: #000000;">
                {message}
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main Streamlit App"""
    # Set page config at the very beginning
    st.set_page_config(
        page_title="SootheAI Game",
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS for a more appealing interface with better visibility
    st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
        }
        .stTextInput > div > div > input {
            border-radius: 20px;
            color: #000000;
        }
        .main-header {
            font-family: 'Trebuchet MS', sans-serif;
            color: #1e3a5f;
            font-size: 2.2rem;
            font-weight: bold;
        }
        .message-container {
            border-radius: 15px;
            padding: 10px;
            margin: 5px 0;
        }
        .stButton button {
            border-radius: 20px;
            background-color: #6c5ce7;
            color: white;
            font-weight: bold;
        }
        /* Improve text visibility throughout the app */
        p, span, div {
            color: #000000 !important;
        }
        .stMarkdown a {
            color: #1e88e5 !important;
        }
        /* Make chat messages more visible */
        .stChatMessage {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 5px;
            margin-bottom: 10px;
        }
        .stChatMessage [data-testid="stChatMessageContent"] {
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # App title and description with improved visibility
    st.markdown("<h1 class='main-header'>SootheAI Game</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; color: #000000; margin-bottom: 20px;'>An interactive story experience about anxiety awareness.</p>", unsafe_allow_html=True)
    
    # Initialize session state variables
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'consent_given' not in st.session_state:
        st.session_state.consent_given = False
    if 'start' not in st.session_state:
        st.session_state.start = None
    if 'seed' not in st.session_state:
        st.session_state.seed = np.random.randint(0, 1000000)

    # Display conversation history
    for user_msg, ai_msg in st.session_state.messages:
        display_message(user_msg, is_user=True)
        display_message(ai_msg, is_user=False)

    # Show initial consent message if no messages yet
    if not st.session_state.messages:
        display_message(consent_message, is_user=False)

    # Create a sidebar with example actions - improved styling
    st.sidebar.markdown("<h2 style='color: #000000; font-weight: bold; margin-bottom: 15px;'>Suggested Actions</h2>", unsafe_allow_html=True)
    
    # Add a description
    st.sidebar.markdown("<p style='color: #000000; margin-bottom: 20px;'>Click any action below to quickly respond in the story:</p>", unsafe_allow_html=True)
    
    # Create custom styled buttons
    example_actions = ["Listen to music", "Journal", "Continue the story"]
    for i, action in enumerate(example_actions):
        button_key = f"action_button_{i}"
        if st.sidebar.button(action, key=button_key, use_container_width=True):
            # Use the action as user input
            user_input = action
            display_message(user_input, is_user=True)
            
            # Get AI response
            conversation_history = st.session_state.messages.copy()
            ai_response = run_action(user_input, conversation_history)
            
            # Display AI response
            display_message(ai_response, is_user=False)
            
            # Save to conversation history
            st.session_state.messages.append((user_input, ai_response))
            
            # Force a rerun to update the UI
            st.experimental_rerun()
    
    # Add separator and instructions
    st.sidebar.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='color: #000000;'>You can also type your own responses in the chat box below.</p>", unsafe_allow_html=True)

    # Input field for user messages
    placeholder_text = "Type 'I agree' to continue..." if not st.session_state.consent_given else "Type your message..."
    user_input = st.chat_input(placeholder_text)

    # Process user input when submitted
    if user_input:
        display_message(user_input, is_user=True)
        
        # Get AI response
        conversation_history = st.session_state.messages.copy()
        ai_response = run_action(user_input, conversation_history)
        
        # Display AI response
        display_message(ai_response, is_user=False)
        
        # Save to conversation history
        st.session_state.messages.append((user_input, ai_response))


# Start the application when script is run
if __name__ == "__main__":
    main()