# SootheAI: Interactive Mental Health Narrative Application

An AI-powered interactive narrative experience designed to help Singaporean youths understand, manage, and overcome anxiety through engaging storytelling set in culturally relevant contexts.

## About The Project

SootheAI creates an immersive, choice-based narrative that:

- Educates users about anxiety in a relatable context of Singaporean student life
- Presents realistic scenarios based on everyday situations faced by JC students
- Offers meaningful choices that demonstrate different coping strategies
- Provides a safe space to explore mental health challenges through fictional characters

## Features

### Current Version Features

- **Interactive story experience** powered by Claude AI (using Anthropic's latest Claude 3.5 Sonnet model)
- **Text-to-speech integration** via ElevenLabs for immersive audio narration
- **Two application versions** with different feature sets:
  - **main_v0.py**: Simple version with basic content filtering and adaptive ending system
  - **main_v1.py**: Advanced version with comprehensive guardrail system (ending integration planned)
- **Web interface** available in both Streamlit and HTML/CSS/JS versions with Gradio as the primary interface
- **Character-driven narrative** focusing on mental health themes
- **Content safety filtering** to protect vulnerable users
- **Culturally relevant storytelling** set in Singapore educational context
- **Consent flow** that emphasizes ethical usage
- **Comprehensive security measures** and content moderation

### Version Comparison

#### main_v0.py (Simple Version)

- Basic blacklist content filtering
- Adaptive ending system with 3 narrative branches
- Simple ending that triggers after 12 interactions
- Educational summary with key insights about anxiety
- TTS integration for immersive experience
- Less comprehensive content safety measures

#### main_v1.py (Advanced Version)

- **Enhanced content filtering system** with:
  - Multi-level severity classification (LOW, MEDIUM, HIGH, CRITICAL)
  - Context-aware pattern matching
  - Configurable replacement strategies
  - Comprehensive violation reporting
- **Advanced guardrails**:
  - Real-time content analysis
  - Contextual safety responses
  - Detailed logging of content filtering
- **Same core features** as v0 (TTS, Claude integration, consent flow)
- **Ending system integration** (planned for next release)

## Project Structure

```
soothe_app/                   # Core Python application
├── __init__.py 
├── main_v0.py               # Simple version with basic filtering and endings
├── main_v1.py               # Advanced version with enhanced guardrail system
├── blacklist.py             # Enhanced content filtering and safety module
├── stream.py                # Streamlit interface implementation
├── characters/              # Character definition files
│   ├── serena.json          # Main protagonist character
│   ├── chloe.json           # Supporting character
│   ├── mother.json          # Family member character
│   └── therapist.json       # Mental health professional character
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_blacklist.py    # Unit tests for blacklist module
│   ├── system_prompt_tester.py  # Tool for testing system prompts
│   └── consent_flow_tests.json  # Test cases for consent flow
├── enhance_filter_config.json   # Configuration for enhanced filtering
├── harmful_patterns_file.json   # Pattern definitions for content filtering
└── test_integration.py      # Integration tests for enhanced filter

soothe_interface_dev/        # Web interface components
├── digital_prototype/       # HTML/CSS implementation
│   ├── about.html
│   ├── anxiety-education.html
│   ├── game.html
│   ├── helpline.html
│   ├── index.html
│   ├── scripts.js
│   └── styles.css
└── stream.py               # Streamlit interface

doc/                        # Documentation files
├── anthropic-prompt-cheatsheet.md
├── code-overview.md
└── features/
    ├── feature_1.md         # User input functionality docs
    └── feature_2.md         # LLM text generation docs
```

## Key Components

### 1. Content Safety

SootheAI implements comprehensive content safety measures:

#### Basic Version (main_v0.py)

- Simple blacklist filtering for potentially harmful content
- Safety disclaimers for sensitive discussions
- Redirection to helpline resources when needed
- System prompts designed to avoid explicitly labeling anxiety

#### Enhanced Version (main_v1.py)

- **Multi-tier content filtering** with severity levels (LOW, MEDIUM, HIGH, CRITICAL)
- **Pattern-based detection** using regex for complex harmful content identification
- **Context-aware analysis** for better understanding of user intent
- **Configurable response strategies** based on content severity
- **Comprehensive logging** for monitoring and improvement
- **Dynamic content replacement** with contextually appropriate alternatives

### 2. Character Framework

Characters are defined through detailed JSON files that specify:

- Personality traits and background
- Academic environment and pressures
- Behavioral patterns related to anxiety
- Relationships with family, friends, and teachers
- Coping mechanisms and triggers

### 3. AI Integration

The application integrates with Anthropic's Claude API and ElevenLabs for TTS:

- Generate narrative responses based on user choices using Claude 3.5 Sonnet
- Text-to-speech conversion for an immersive audio experience
- Maintain conversation history and context
- Filter responses for safety compliance
- Present realistic character behaviors

### 4. Adaptive Ending System (main_v0.py)

- Triggers after 12 user interactions
- Three narrative branches based on user choices:
  - Acknowledgment of feelings and physical symptoms
  - Recognition of late study habits and balance
  - Importance of talking to others and sharing burdens
- Educational summary with key insights about anxiety
- Singapore helpline resources

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

For the Streamlit interface:

```bash
streamlit run soothe_interface_dev/stream.py
```

For the Gradio interface (choose version):

```bash
# Simple version with basic filtering and endings
python soothe_app/main_v0.py

# Advanced version with enhanced guardrails
python soothe_app/main_v1.py
```

## Usage

1. When you launch the application, you'll first see a consent message. Type "I agree" to continue.
2. Type "start game" to begin the narrative.
3. Read the story descriptions and make choices to navigate Serena's journey.
4. Type custom responses or select from available options to shape the narrative.
5. Listen to the narration through the text-to-speech feature (if enabled).
6. In main_v0.py, the story will conclude after 12 interactions with an educational summary.

## Testing

Run unit tests with:

```bash
python -m unittest discover -s soothe_app/tests
```

For system prompt testing:

```bash
python soothe_app/tests/system_prompt_tester.py --prompt path/to/prompt --consent-flow
```

For enhanced filter integration testing:

```bash
python soothe_app/test_integration.py
```

## Development Notes

See `doc/anthropic-prompt-cheatsheet.md` for guidance on structuring prompts for the Claude API, and `doc/code-overview.md` for a detailed explanation of the application's architecture.

## Current Development Status

- ✅ **main_v0.py**: Fully functional with basic filtering and adaptive ending system
- ✅ **main_v1.py**: Enhanced guardrail system implemented
- 🚧 **main_v2.py ending system**: Integration of adaptive endings (next milestone)
- 🚧 **main_v3.py NPC integration**: Integration of different characters in Serena's life that players can interact with
- ✅ **Enhanced content filtering**: Multi-tier safety system with pattern matching
- ✅ **Text-to-speech integration**: Full audio narration support
- ✅ **Comprehensive testing**: Unit tests and integration tests for core functionality

## License

This project is intended for educational purposes only. All character data and scenarios are fictional.

## Helpline Resources

If you're experiencing anxiety or mental health challenges, please contact:

- National Care Hotline (Singapore): 1800-202-6868
- Samaritans of Singapore (SOS): 1-767
- IMH Mental Health Helpline: 6389-2222
