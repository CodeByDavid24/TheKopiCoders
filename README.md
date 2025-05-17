# SootheAI: Interactive Mental Health Narrative Application

An AI-powered interactive narrative experience designed to help Singaporean youths understand, manage, and overcome anxiety through engaging storytelling set in culturally relevant contexts.

## About The Project

SootheAI creates an immersive, choice-based narrative that:

- Educates users about anxiety in a relatable context of Singaporean student life
- Presents realistic scenarios based on everyday situations faced by JC students
- Offers meaningful choices that demonstrate different coping strategies
- Provides a safe space to explore mental health challenges through fictional characters

## Features

- **Interactive storytelling experience** powered by Claude AI (using Anthropic's Claude 3.7 Sonnet model)
- **Text-to-speech integration** via ElevenLabs for immersive audio narration
- **Multiple interface options**:
  - Gradio-based chat interface for primary interaction
  - Streamlit interface with enhanced visual elements
  - HTML/CSS/JS prototype for static demonstrations
- **Character-driven narrative** focusing on mental health themes
- **Content safety filtering** to protect vulnerable users
- **Culturally relevant storytelling** set in Singapore educational context
- **Consent flow** that emphasizes ethical usage
- **Comprehensive security measures** and content moderation

## Project Structure

```
soothe_app/                   # Core Python application
├── src/                      # Source code
│   ├── core/                 # Core functionality
│   │   ├── api_client.py     # Claude API integration
│   │   ├── content_filter.py # Content safety system
│   │   └── narrative_engine.py # Story generation engine
│   ├── models/               # Data models
│   │   ├── character.py      # Character definition
│   │   └── game_state.py     # Game state tracking
│   ├── ui/                   # User interfaces
│   │   ├── gradio_interface.py # Primary Gradio interface
│   │   └── tts_handler.py    # Text-to-speech functionality
│   └── utils/                # Utility functions
│       ├── file_loader.py    # File handling utilities
│       ├── logger.py         # Logging configuration
│       └── safety.py         # Safety utilities
├── tests/                    # Test suite
│   ├── fixtures/             # Test data
│   │   ├── test_blacklist.py
│   │   └── test_character.json
│   ├── integration/          # Integration tests
│   │   ├── test_api_integration.py
│   │   └── test_full_flow.py
│   ├── tools/                # Testing tools
│   │   ├── consent_flow_tests.json
│   │   └── system_prompt_tester.py
│   ├── unit/                 # Unit tests
│   │   ├── test_character_loader.py
│   │   ├── test_content_filter.py
│   │   ├── test_integration.py
│   │   └── test_narrative_engine.py
│   └── __init__.py
├── characters/               # Character definition files
│   └── serena.json           # Main protagonist character

soothe_interface_dev/        # Web interface components
├── digital_prototype/       # HTML/CSS implementation
│   ├── images/              # Image assets
│   ├── about.html           # About page
│   ├── anxiety-education.html # Educational content
│   ├── game.html            # Interactive game screen
│   ├── helpline.html        # Support resources
│   ├── index.html           # Landing page
│   ├── script.js            # JavaScript functionality
│   └── styles.css           # CSS styling
└── stream.py                # Streamlit interface implementation

docs/                        # Documentation files
├── api/                     # API documentation
│   └── content_filter.md
├── development/             # Development documentation
│   ├── architecture.md
│   └── contributing.md
├── features/                # Feature documentation
│   ├── feature_1.md         # User input functionality
│   └── feature_2.md         # LLM text generation
├── setup/                   # Setup documentation
│   ├── configuration.md
│   └── installation.md
├── anthropic-prompt-cheatsheet.md # Prompt engineering guide
└── code-overview.md         # Application architecture overview
```

## Key Components

### 1. Narrative Engine

The heart of SootheAI is its narrative engine powered by Claude 3.7 Sonnet. The engine:

- Generates contextually relevant responses based on user inputs
- Maintains narrative consistency throughout the experience
- Portrays subtle anxiety symptoms without explicitly labeling them
- Adapts to user choices and preferences
- Provides educational insights through storytelling

### 2. Content Safety System

SootheAI implements comprehensive content safety measures:

- Multi-tier content filtering with severity levels
- Pattern-based detection using regex for complex harmful content identification
- Context-aware analysis for better understanding of user intent
- Configurable response strategies based on content severity
- Dynamic content replacement with contextually appropriate alternatives
- Comprehensive logging for monitoring and improvement

### 3. Character Framework

Characters are defined through detailed JSON files that specify:

- Personality traits and background
- Academic environment and pressures
- Behavioral patterns related to anxiety
- Relationships with family, friends, and teachers
- Coping mechanisms and triggers

### 4. Interface Options

SootheAI offers multiple user interface options:

#### Gradio Interface
- Primary chat-based interface
- Conversation history tracking
- Audio narration integration
- Pre-populated consent message

#### Streamlit Interface
- Visual character status dashboard
- Progress tracking and visualization
- Emotion state indicators
- Quick-action buttons for common choices

#### HTML/CSS Prototype
- Static demonstration of the application concept
- Visual design elements and layout
- Educational content pages
- Support resource information

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

Create a `.env` file in the project root with your API keys:

```
CLAUDE_API_KEY=your_anthropic_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### 3. Run the Application

For the Gradio interface:

```bash
python -m soothe_app.src.ui.gradio_interface
```

For the Streamlit interface:

```bash
streamlit run soothe_interface_dev/stream.py
```

To view the HTML prototype, open the HTML files in the `soothe_interface_dev/digital_prototype/` directory in a web browser.

## Usage

1. When you launch the application, you'll first see a consent message. Type "I agree" to continue.
2. Type "start game" to begin the narrative.
3. Read the story descriptions and make choices to navigate Serena's journey.
4. Type custom responses or select from available options to shape the narrative.
5. Listen to the narration through the text-to-speech feature (if enabled).
6. The story will conclude with an educational summary about anxiety and coping strategies.

## Testing

Run unit tests with:

```bash
python -m unittest discover -s soothe_app/tests
```

For system prompt testing:

```bash
python soothe_app/tests/tools/system_prompt_tester.py --prompt path/to/prompt --consent-flow
```

For enhanced filter integration testing:

```bash
python soothe_app/tests/unit/test_integration.py
```

## Development Notes

See `docs/anthropic-prompt-cheatsheet.md` for guidance on structuring prompts for the Claude API, and `docs/code-overview.md` for a detailed explanation of the application's architecture.

## License

This project is intended for educational purposes only. All character data and scenarios are fictional.

## Helpline Resources

If you're experiencing anxiety or mental health challenges, please contact:

- National Care Hotline (Singapore): 1800-202-6868
- Samaritans of Singapore (SOS): 1-767
- IMH Mental Health Helpline: 6389-2222
