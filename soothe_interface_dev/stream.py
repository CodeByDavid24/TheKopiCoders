import streamlit as st
import anthropic
import json
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
"""

# Define the consent message
consent_message = """
This is a fictional story designed to help you understand anxiety. Please be aware that some content may depict distressing situations. Do not replicate or engage in any harmful actions shown in the game. If you're feeling distressed, we encourage you to seek professional help.

Your choices will directly shape the story. By starting the game, you agree to these terms.
"""

# Initialize Claude API client
try:
    print(f"Anthropic SDK version: {anthropic.__version__}")
except AttributeError:
    print("Could not determine Anthropic SDK version")

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "REPLACE_WITH_YOUR_API_KEY_BEFORE_RUNNING")

# Initialize Claude client
try:
    claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
except Exception as e:
    print(f"Error initializing Claude client: {e}")
    claude_client = None


def get_initial_response():
    """Get the initial game narrative from Claude"""
    global claude_client

    if not claude_client:
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    try:
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            system=system_prompt,
            messages=[
                {"role": "user", "content": "Start the game with a brief introduction to Serena and her current situation. Please format your response to naturally fit in a visual storytelling interface."}
            ],
            temperature=0,
            max_tokens=1000
        )
        return response.content[0].text
    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"


def run_action(message: str, conversation_history: List[Tuple[str, str]]) -> str:
    """Process player actions and generate appropriate responses"""
    global claude_client

    if not claude_client:
        return "Claude API key is invalid. Please check the CLAUDE_API_KEY in the code."

    # Check if consent has been given
    if not st.session_state.consent_given:
        if message.lower() == 'i agree':
            st.session_state.consent_given = True
            return "Welcome to Serena's story. Let's begin..."
        else:
            return consent_message

    # Check if this is the start of the game
    if message.lower() == 'start game':
        if not st.session_state.start:
            st.session_state.start = get_initial_response()
        return st.session_state.start

    try:
        # Prepare message history for Claude
        claude_messages = []

        # Add conversation history
        for user_msg, assistant_msg in conversation_history:
            claude_messages.append({"role": "user", "content": user_msg})
            claude_messages.append({"role": "assistant", "content": assistant_msg})

        # Add current message to conversation
        claude_messages.append({"role": "user", "content": message})

        # Get response from Claude API
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            system=system_prompt,
            messages=claude_messages,
            temperature=0,
            max_tokens=1000
        )

        result = response.content[0].text
        
        # Update game state
        update_game_state(message, result)
        
        return result

    except Exception as e:
        return f"Error communicating with Claude API: {str(e)}"


def update_game_state(user_choice: str, story_response: str):
    """Update the game state based on user choices and story progression"""
    # Update progress
    if 'progress' not in st.session_state:
        st.session_state.progress = 0.1
    else:
        st.session_state.progress = min(1.0, st.session_state.progress + 0.08)
    
    # Update stage based on progress
    if st.session_state.progress < 0.33:
        st.session_state.stage = "Introduction"
    elif st.session_state.progress < 0.66:
        st.session_state.stage = "Middle Game"
    else:
        st.session_state.stage = "Climax"
    
    # Track choices
    if 'choices_made' not in st.session_state:
        st.session_state.choices_made = []
    
    if len(st.session_state.choices_made) >= 5:
        st.session_state.choices_made.pop(0)
    
    st.session_state.choices_made.append(user_choice)
    
    # Update Serena's emotional state (simple example)
    if 'serena_mood' not in st.session_state:
        st.session_state.serena_mood = 50  # 0-100 scale
    
    # Adjust mood based on choice type
    positive_keywords = ['music', 'journal', 'talk', 'help', 'relax', 'breathe']
    negative_keywords = ['ignore', 'stress', 'worry', 'panic', 'avoid']
    
    if any(keyword in user_choice.lower() for keyword in positive_keywords):
        st.session_state.serena_mood = min(100, st.session_state.serena_mood + 5)
    elif any(keyword in user_choice.lower() for keyword in negative_keywords):
        st.session_state.serena_mood = max(0, st.session_state.serena_mood - 5)


def apply_css():
    """Apply CSS styling with fixed syntax"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Override Streamlit default styles */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            background-color: #f8f9fa;
        }
        
        /* Hide Streamlit default menu items */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom theme */
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Inter', sans-serif;
        }
        
        /* Main title */
        .game-title {
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 1rem 0;
        }
        
        .game-subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #6c757d;
            margin-bottom: 2rem;
        }
        
        /* Story panel */
        .story-panel {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
        }
        
        .story-text {
            font-size: 1.1rem;
            line-height: 1.8;
            color: #333;
        }
        
        /* Character panel */
        .character-panel {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 15px;
            padding: 1.5rem;
            color: white;
            margin-bottom: 1rem;
        }
        
        .character-avatar {
            font-size: 3rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .character-name {
            font-size: 1.5rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .character-description {
            font-size: 0.9rem;
            text-align: center;
            margin-bottom: 1rem;
            opacity: 0.9;
        }
        
        /* Status bars */
        .status-bar {
            margin: 1rem 0;
        }
        
        .status-label {
            font-size: 0.85rem;
            color: white;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .status-bar-bg {
            background-color: rgba(255,255,255,0.2);
            border-radius: 10px;
            height: 10px;
            overflow: hidden;
        }
        
        .status-bar-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, #28a745, #34ce57);
        }
        
        .mood-fill {
            background: linear-gradient(90deg, #ffc107, #ffed4e);
        }
        
        /* Action buttons */
        .action-button {
            background: white;
            border: 2px solid #667eea;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem;
            color: #667eea;
            font-weight: 600;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .action-button:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        }
        
        /* Stats container */
        .stats-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .stat-item {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            color: #333;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #667eea;
            display: block;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Choice history */
        .choice-history {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
        }
        
        .choice-item {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            margin: 0.25rem 0;
            font-size: 0.85rem;
            color: #333;
            border-left: 3px solid #667eea;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #5a6fd8;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 0.75rem;
            font-size: 1rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .game-title {
                font-size: 2rem;
            }
            
            .stats-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def create_character_panel():
    """Create the character status panel"""
    with st.sidebar:
        st.markdown("""
        <div class="character-panel">
            <div class="character-avatar">👩‍🎓</div>
            <div class="character-name">Serena</div>
            <div class="character-description">
                17-year-old JC1 Student<br>
                Aspiring to study Medicine at NUS
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress = st.session_state.get('progress', 0)
        stage = st.session_state.get('stage', 'Not Started')
        
        st.markdown(f"""
        <div class="character-panel">
            <div class="status-bar">
                <div class="status-label">Story Progress - {stage}</div>
                <div class="status-bar-bg">
                    <div class="status-bar-fill progress-fill" style="width: {progress * 100}%"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mood indicator
        mood = st.session_state.get('serena_mood', 50)
        mood_text = "Anxious" if mood < 30 else "Okay" if mood < 70 else "Good"
        
        st.markdown(f"""
        <div class="character-panel">
            <div class="status-bar">
                <div class="status-label">Emotional State - {mood_text}</div>
                <div class="status-bar-bg">
                    <div class="status-bar-fill mood-fill" style="width: {mood}%"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats
        choices_count = len(st.session_state.get('choices_made', []))
        messages_count = len(st.session_state.get('messages', []))
        
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-item">
                <span class="stat-value">{choices_count}</span>
                <span class="stat-label">Choices Made</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{messages_count}</span>
                <span class="stat-label">Interactions</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recent choices
        if st.session_state.get('choices_made'):
            st.markdown("""
            <div class="choice-history">
                <h4 style="color: #333; margin-bottom: 0.5rem;">Recent Choices</h4>
            """, unsafe_allow_html=True)
            
            for choice in st.session_state.choices_made[-3:]:
                st.markdown(f'<div class="choice-item">{choice}</div>', unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)


def create_action_buttons():
    """Create interactive action buttons"""
    st.markdown("### Choose your action:")
    
    if not st.session_state.consent_given:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("I Agree to the Terms", key="agree_btn", use_container_width=True):
                user_input = "I agree"
                process_action(user_input)
    elif not st.session_state.get('start'):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start Game", key="start_btn", use_container_width=True):
                user_input = "Start game"
                process_action(user_input)
    else:
        actions = [
            ("🎵 Listen to Music", "Listen to music"),
            ("📓 Write in Journal", "Journal"),
            ("👥 Talk to Someone", "Talk to a friend"),
            ("🧘 Take Deep Breaths", "Take deep breaths"),
            ("📚 Continue Studying", "Continue studying"),
            ("🚶 Take a Walk", "Take a walk")
        ]
        
        cols = st.columns(2)
        for i, (label, action) in enumerate(actions):
            col = cols[i % 2]
            with col:
                if st.button(label, key=f"action_{i}", use_container_width=True):
                    process_action(action)


def process_action(action: str):
    """Process user action and update the game state"""
    # Add to conversation history
    conversation_history = st.session_state.get('messages', [])
    
    with st.spinner("Processing..."):
        ai_response = run_action(action, conversation_history)
    
    # Update messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    st.session_state.messages.append((action, ai_response))
    
    # Store current story text for display
    st.session_state.current_story = ai_response
    
    # Rerun to update UI
    st.rerun()


def display_story():
    """Display the current story text in a game-like format"""
    if not st.session_state.consent_given:
        st.markdown(f"""
        <div class="story-panel">
            <div class="story-text">
                <h3 style="color: #333; margin-bottom: 1rem;">⚠️ Important Information</h3>
                {consent_message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.get('current_story'):
        st.markdown(f"""
        <div class="story-panel">
            <div class="story-text">
                {st.session_state.current_story}
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.consent_given and not st.session_state.get('start'):
        st.markdown("""
        <div class="story-panel">
            <div class="story-text">
                <h3 style="color: #333; margin-bottom: 1rem;">Welcome to SootheAI</h3>
                <p>You're about to experience Serena's journey - a story about anxiety, choices, and growth.</p>
                <p>Click "Start Game" when you're ready to begin...</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main game interface"""
    # Set page config
    st.set_page_config(
        page_title="SootheAI Experience",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply CSS
    apply_css()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'consent_given' not in st.session_state:
        st.session_state.consent_given = False
    if 'start' not in st.session_state:
        st.session_state.start = None
    if 'current_story' not in st.session_state:
        st.session_state.current_story = None
    
    # Main title
    st.markdown("""
    <div class="game-title">SootheAI</div>
    <div class="game-subtitle">Navigate Anxiety Through Interactive Storytelling</div>
    """, unsafe_allow_html=True)
    
    # Create two-column layout
    left_col, right_col = st.columns([3, 1])
    
    with left_col:
        # Display current story
        display_story()
        
        # Action buttons
        create_action_buttons()
        
        # Custom text input for free-form responses
        if st.session_state.consent_given and st.session_state.get('start'):
            st.markdown("---")
            st.markdown("### 💬 Or type your own response:")
            user_input = st.text_input("", placeholder="Type your response here...", key="custom_input")
            
            if user_input and st.button("Submit", key="submit_custom"):
                process_action(user_input)
    
    with right_col:
        # This column will be empty since sidebar is used for character panel
        pass
    
    # Character panel (in sidebar)
    create_character_panel()


if __name__ == "__main__":
    main()