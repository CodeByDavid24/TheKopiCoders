# SootheAI: Interactive Mental Health Narrative Application

An AI-powered interactive narrative experience designed to help Singaporean youths understand, manage, and overcome anxiety through engaging storytelling set in culturally relevant contexts.

## About The Project

SootheAI creates an immersive, choice-based narrative that:

- Educates users about anxiety in a relatable context of Singaporean student life
- Presents realistic scenarios based on everyday situations faced by JC students
- Offers meaningful choices that demonstrate different coping strategies
- Provides a safe space to explore mental health challenges through fictional characters

## Features

- Interactive story experience powered by Claude AI
- Web interface available in both Streamlit and HTML/CSS/JS versions
- Character-driven narrative focusing on mental health themes
- Content safety filtering to protect vulnerable users
- Culturally relevant storytelling set in Singapore educational context
- Consent flow that emphasizes ethical usage
- Comprehensive security measures and content moderation

## Project Structure

```
soothe_app/                   # Core Python application
├── __init__.py 
├── main.py                   # Gradio interface application entry point
├── blacklist.py              # Content filtering and safety module
├── stream.py                 # Streamlit interface implementation
├── characters/               # Character definition files
│   ├── serena.json           # Main protagonist character
│   ├── chloe.json            # Supporting character
│   ├── mother.json           # Family member character
│   └── therapist.json        # Mental health professional character
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_blacklist.py     # Unit tests for blacklist module
│   ├── system_prompt_tester.py  # Tool for testing system prompts
│   └── consent_flow_tests.json  # Test cases for consent flow

soothe_interface_dev/         # Web interface components
├── digital_prototype/        # HTML/CSS implementation
│   ├── about.html
│   ├── anxiety-education.html
│   ├── game.html
│   ├── helpline.html
│   ├── index.html
│   ├── script.js
│   └── styles.css
└── stream.py                 # Streamlit interface

doc/                         # Documentation files
├── anthropic-prompt-cheatsheet.md
├── code-overview.md
└── features/
    ├── feature_1.md          # User input functionality docs
    └── feature_2.md          # LLM text generation docs
```

## Key Components

### 1. Content Safety

SootheAI implements comprehensive content safety measures:

- Blacklist filtering for potentially harmful content
- Safety disclaimers for sensitive discussions
- Redirection to helpline resources when needed
- System prompts designed to avoid explicitly labeling anxiety

### 2. Character Framework

Characters are defined through detailed JSON files that specify:

- Personality traits and background
- Academic environment and pressures
- Behavioral patterns related to anxiety
- Relationships with family, friends, and teachers
- Coping mechanisms and triggers

### 3. AI Integration

The application integrates with Anthropic's Claude API to:

- Generate narrative responses based on user choices
- Maintain conversation history and context
- Filter responses for safety compliance
- Present realistic character behaviors

## Setup Instructions

### 1. Install Dependencies

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. API Configuration

Create a `.env` file in the project root with your API key:

```
CLAUDE_API_KEY=your_api_key_here
```

### 3. Run the Application

For the Streamlit interface:

```bash
streamlit run soothe_interface_dev/stream.py
```

For the Gradio interface:

```bash
python soothe_app/main.py
```

## Usage

1. When you launch the application, you'll first see a consent message. Type "I agree" to continue.
2. Type "start game" to begin the narrative.
3. Read the story descriptions and make choices to navigate Serena's journey.
4. Type custom responses or select from available options to shape the narrative.

## Testing

Run unit tests with:

```bash
python -m unittest discover -s soothe_app/tests
```

For system prompt testing:

```bash
python soothe_app/tests/system_prompt_tester.py --prompt path/to/prompt --consent-flow
```

## Development Notes

See `doc/anthropic-prompt-cheatsheet.md` for guidance on structuring prompts for the Claude API, and `doc/code-overview.md` for a detailed explanation of the application's architecture.

## License

This project is intended for educational purposes only. All character data and scenarios are fictional.

## Helpline Resources

If you're experiencing anxiety or mental health challenges, please contact:

- National Care Hotline (Singapore): 1800-202-6868
- Samaritans of Singapore (SOS): 1-767
- IMH Mental Health Helpline: 6389-2222
