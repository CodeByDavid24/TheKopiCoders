# SootheAI Code Overview

This document provides a simplified overview of the SootheAI application architecture, focusing on core concepts for AI Application students.

## Introduction

SootheAI is an interactive application that uses AI to create personalized narratives about anxiety awareness. The experience follows a character named Serena, a JC student in Singapore, as she navigates academic pressure and undiagnosed anxiety.

## Key Components

### 1. Interface Options

SootheAI offers two user interfaces:

- **Streamlit Interface** (`soothe_interface_dev/stream.py`): A simple, user-friendly interface
- **Gradio Interface** (`soothe_app/main.py`): A chatbot-style interface with conversation history
- **HTML/CSS Prototype** (`soothe_interface_dev/digital_prototype/`): A static demo version

### 2. Character Data System

Characters are defined using JSON files (`soothe_app/characters/`):

```python
# Example of loading character data
def load_json(filename: str) -> dict:
    """Load and parse a JSON file with error handling"""
    try:
        with open(f'{filename}.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Load character data
character = load_json('characters/serena')
```

The character data includes:

- Personality traits and background
- Academic environment
- Behaviors related to anxiety
- Relationships and coping mechanisms

### 3. AI Integration

The application connects to Anthropic's Claude API to generate narrative responses:

```python
# Simplified Claude API integration
def get_response(message: str, history: list) -> str:
    """Get a response from Claude API"""
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=history + [{"role": "user", "content": message}],
        system=system_prompt
    )
    return response.content[0].text
```

The AI is guided by a detailed system prompt that defines:

- Character details and personality
- Narrative structure and flow
- Content safety guidelines
- Rules for depicting anxiety without clinical labels

### 4. Content Safety System

The application includes a comprehensive safety system:

```python
# Content filtering example
def check_input_safety(message: str) -> tuple[bool, str]:
    """Check if user input contains harmful content"""
    has_blacklisted, matched_phrases = contains_blacklisted_content(
        message, blacklisted_phrases)
    
    if has_blacklisted:
        return False, "This content may be sensitive. Let's focus on healthy coping strategies."
    return True, message
```

Key safety features:

- Blacklist of harmful phrases (`blacklist.py`)
- Input and output content filtering
- Safety disclaimers and helpline information
- Redirection for potentially harmful topics

### 5. Consent Flow

The application implements a mandatory consent process:

```python
# Simplified consent flow
if not game_state['consent_given']:
    if message.lower() == 'i agree':
        game_state['consent_given'] = True
        return "Thank you for agreeing. Type 'start game' to begin."
    else:
        return consent_message
```

Users must explicitly agree to terms before starting the experience, acknowledging:

- The fictional nature of the content
- Potential for sensitive topics
- Warning against harmful actions
- Data handling practices

### 6. Game State Management

The application tracks user progress and contextual information:

```python
# Game state initialization
game_state = {
    'seed': np.random.randint(0, 1000000),  # For reproducibility
    'character': character,                  # Character data
    'history': [],                           # Conversation history
    'consent_given': False,                  # Consent tracking
    'start': None                            # Initial narrative
}
```

This allows the application to:

- Remember previous interactions
- Maintain narrative continuity
- Track consent status
- Store character data

### 7. Error Handling and Logging

The application includes comprehensive error handling:

```python
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'soothe_app.log',
            maxBytes=1024*1024,  # 1MB per file
            backupCount=5        # Keep 5 backup files
        ),
        logging.StreamHandler(sys.stdout)  # Also log to console
    ]
)
```

This enables:

- Tracking API interactions
- Monitoring for errors
- Debugging issues
- Performance analysis

## Data Flow

Here's the typical flow of data through the application:

1. User sends a message through the interface
2. Message is checked against the blacklist for safety
3. If safe, message is sent to Claude API with conversation history
4. Claude generates a response based on the system prompt
5. Response is filtered for safety
6. Safe response is displayed to the user
7. User interaction and AI response are added to conversation history

## Testing Framework

The application includes several testing components:

- **Unit Tests** (`soothe_app/tests/test_blacklist.py`): Test content filtering
- **System Prompt Tester** (`soothe_app/tests/system_prompt_tester.py`): Test AI prompts
- **Consent Flow Tests** (`soothe_app/tests/consent_flow_tests.json`): Test user flow

## Key Takeaways for AI Application Students

1. **Prompt Engineering**: System prompts are crucial for guiding AI behavior.
2. **Safety First**: Content moderation is essential for mental health applications.
3. **Ethical Considerations**: Consent flow and proper disclaimers are necessary.
4. **Conversation Management**: Tracking history provides context for AI responses.
5. **Error Handling**: Robust error handling prevents application failures.
6. **Testing**: Comprehensive testing ensures application reliability.

## Simple Execution Flow

1. Initialize application and load character data
2. Present consent message
3. Wait for user to agree to terms
4. Start narrative once user types "start game"
5. Process user inputs and generate narrative responses
6. Filter all content for safety
7. Maintain conversation history for context

This architecture allows for an interactive, educational experience while maintaining strict safety standards for sensitive topics like mental health.
