# SootheAI Code Overview

This document provides a high-level overview of the SootheAI application architecture, code structure, and key components.

## Project Structure

```
soothe_app/
├── config/                 # Configuration files
│   ├── blacklist/          # Content safety blacklists
│   ├── characters/         # Character definitions
│   └── system_prompts/     # Claude system prompts
├── docs/                   # Documentation
├── game_data/              # Game narrative content
│   ├── endings/            # Story ending definitions
│   └── milestones/         # Narrative milestone events
├── src/                    # Source code
│   ├── core/               # Core functionality
│   ├── models/             # Data models
│   ├── ui/                 # User interface components
│   └── utils/              # Utility functions
└── tests/                  # Test suites
    ├── fixtures/           # Test fixtures
    ├── integration/        # Integration tests
    ├── tools/              # Testing utilities
    └── unit/               # Unit tests
```

## Core Components

### Narrative Engine

The narrative engine (`src/core/narrative_engine.py`) is the heart of SootheAI. It manages:

- Story generation through Claude API
- Game state tracking and transitions
- User input processing
- Content safety filtering
- Response formatting

```python
# Key classes
class NarrativeEngine:
    """Engine that drives the SootheAI narrative experience."""
    
    def process_message(self, message: str) -> Tuple[str, bool]:
        """Process a player message and generate a response."""
```

### Game State

The game state model (`src/models/game_state.py`) tracks:

- Character wellbeing
- Conversation history
- Player consent status
- Relationship scores
- Interaction count

```python
class GameState:
    """Class for managing the state of the SootheAI narrative experience."""
    
    def update_wellbeing_level(self, change: int) -> int:
        """Update the character's wellbeing level."""
```

### API Client

The API client (`src/core/api_client.py`) handles communication with the Claude API:

- Manages authentication
- Handles request/response formatting
- Implements error handling
- Provides a singleton instance for application-wide use

```python
class ClaudeClient:
    """Client for interacting with Claude API."""
    
    def generate_response(self, messages: List[Dict[str, str]], 
                          system_prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate a response from Claude."""
```

### Content Filter

The content filter (`src/core/content_filter.py`) provides safety features:

- Detects harmful content in user input
- Filters unsafe content from AI responses
- Implements multi-level severity detection
- Provides alternative safe responses

```python
class EnhancedContentFilter:
    """Enhanced content filtering system with multiple detection methods"""
    
    def analyze_content(self, text: str) -> ContentFilterResult:
        """Analyze content for harmful material with comprehensive filtering"""
```

### Gradio Interface

The UI interface (`src/ui/gradio_interface.py`) creates the web experience:

- Implements chat interface
- Manages consent flow
- Integrates optional text-to-speech
- Handles user interactions

```python
class GradioInterface:
    """Class for managing the Gradio interface for SootheAI."""
    
    def main_loop(self, message: Optional[str], history: List[Tuple[str, str]]) -> str:
        """Main game loop that processes player input and returns AI responses."""
```

## Key Workflows

### Application Startup

1. Environment variables loaded
2. Logging configured
3. API clients initialized
4. Character data loaded
5. Content filter initialized
6. Gradio interface created and launched

### Consent Flow

1. User presented with consent message
2. User must explicitly agree ("I agree")
3. User starts game ("start game")
4. Initial narrative displayed

### Gameplay Loop

1. User sends input message
2. Input checked for safety
3. Game state updated
4. Claude API generates response
5. Response filtered for safety
6. Response displayed to user (with optional TTS)
7. Conversation history updated

## Development Guidelines

### Testing

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Run with `python test_runner.py`

### Safety Features

- Never bypass content filter checks
- Always filter both input and output
- Use appropriately sanitized prompts
- Follow consent flow requirements

### Adding Features

1. Create unit tests first
2. Implement changes
3. Update documentation
4. Create pull request

## Integration Points

- **Claude API**: Main narrative generation
- **ElevenLabs API**: Optional text-to-speech
- **Gradio**: Web interface framework
- **Content Filter**: Safety system
