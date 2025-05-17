# Development Guide

This guide provides information for developers who want to extend, modify, or contribute to the SootheAI project.

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A code editor (VS Code recommended with Python extensions)
- Anthropic API key for Claude
- (Optional) ElevenLabs API key for TTS

### Setting Up

1. **Clone the repository and create a development branch**:
   ```bash
   git clone https://github.com/yourusername/soothe_app.git
   cd soothe_app
   git checkout -b feature/your-feature-name
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies with development extras**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## Project Structure

Understand the core components before making changes:

```
soothe_app/
├── config/                # Configuration files
│   ├── blacklist/         # Content safety blacklists
│   ├── characters/        # Character definitions
│   └── system_prompts/    # Claude system prompts
├── src/                   # Source code
│   ├── core/              # Core functionality
│   │   ├── api_client.py  # Claude API wrapper
│   │   ├── content_filter.py  # Safety filters
│   │   ├── narrative_engine.py  # Main game logic
│   │   └── filter_compatibility.py  # Safety compatibility layer
│   ├── models/            # Data models
│   │   ├── character.py   # Character data structures
│   │   └── game_state.py  # Game state tracking
│   ├── ui/                # User interface components
│   │   ├── gradio_interface.py  # Web UI
│   │   └── tts_handler.py  # Text-to-speech handling
│   └── utils/             # Utility functions
│       ├── file_loader.py  # File loading utilities
│       ├── logger.py      # Logging configuration
│       └── safety.py      # Safety utilities
└── tests/                 # Test suites
```

## Development Workflow

### 1. Local Development

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Run tests to confirm baseline functionality**:
   ```bash
   python test_runner.py
   ```

3. **Make your changes** following the coding standards

4. **Write tests** for your new functionality:
   ```bash
   # For unit tests
   python -m unittest tests.unit.test_your_feature
   
   # For integration tests
   python -m unittest tests.integration.test_your_feature
   ```

5. **Run all tests** to ensure nothing broke:
   ```bash
   python test_runner.py
   ```

### 2. Testing

SootheAI uses a comprehensive testing approach:

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **System Tests**: Test the full application flow

Special testing tools:

- **System Prompt Tester**: Test Claude prompts directly
  ```bash
  python tests/tools/system_prompt_tester.py --prompt your_prompt.txt --interactive
  ```

- **Content Filter Tests**: Test safety systems
  ```bash
  python -m unittest tests.unit.test_content_filter
  ```

### 3. Safety Considerations

When developing for SootheAI, always keep safety in mind:

1. **Content Filtering**: Never bypass content filters
2. **System Prompts**: Ensure prompts include safety guardrails
3. **User Input**: Always validate and sanitize user input
4. **Response Processing**: Always filter AI-generated responses

## Extending Key Components

### 1. Adding Character Attributes

To extend the character model:

1. Update the `Character` class in `src/models/character.py`
2. Add new fields to character JSON files in `config/characters/`
3. Update loading and serialization methods
4. Add tests for the new attributes

Example:
```python
# Add to Character class in character.py
@dataclass
class NewAttribute:
    field1: str = "default"
    field2: List[str] = field(default_factory=list)

# Add to Character class
new_attribute: NewAttribute = field(default_factory=NewAttribute)
```

### 2. Enhancing the Narrative Engine

To modify narrative generation:

1. Study the existing `NarrativeEngine` class
2. Identify the part you want to enhance
3. Make changes with thorough testing
4. Update system prompts if needed

Example - Adding a new state tracking variable:
```python
# In game_state.py
class GameState:
    def __init__(self, character_data):
        # Existing code...
        self.new_tracker: int = 0
    
    def update_new_tracker(self, value):
        self.new_tracker = value
        logger.info(f"Updated new tracker to {value}")
        return self.new_tracker
```

### 3. Adding Safety Rules

To enhance content filtering:

1. Add patterns to `config/blacklist/` files
2. Extend the `EnhancedContentFilter` class if needed
3. Test extensively with potentially problematic content

Example blacklist entry:
```
[CATEGORY_NAME]
SEVERITY: HIGH
REPLACEMENT: [Safer alternative text]

harmful_phrase_1
harmful_phrase_2
```

### 4. Adding a New API Integration

To integrate a new external service:

1. Create a new client class in `src/core/`
2. Add environment variables for API keys
3. Create appropriate interfaces and handlers
4. Add tests for the integration

Example:
```python
# New API client
class NewServiceClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("NEW_SERVICE_API_KEY")
        # Initialize client...
    
    def make_request(self, parameters):
        # Implementation...
        return result
```

### 5. Adding Story Milestones

To add new narrative elements:

1. Create or modify JSON files in `game_data/milestones/`
2. Update the narrative engine to recognize the milestone
3. Test the narrative flow extensively

Example milestone:
```json
{
    "milestone_type": "school_event",
    "title": "Science Fair Project",
    "description": "A critical academic event requiring preparation and presentation",
    "scenario": {
        "setting": "School hall, with all projects on display",
        "context": "Serena must present her chemistry project to judges"
    },
    "decision_points": [
        {
            "id": "preparation_approach",
            "situation": "How to prepare for the presentation",
            "choices": [
                {
                    "id": "methodical_practice",
                    "text": "Practice the presentation repeatedly until perfect",
                    "immediate_effect": "Feels prepared but exhausted",
                    "long_term_impact": "Confidence in presentation but high stress"
                },
                // More choices...
            ]
        }
    ]
}
```

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and returns
- Document classes and functions with docstrings
- Use descriptive variable and function names

Example:
```python
def process_input(message: str) -> Tuple[bool, str]:
    """
    Process user input for safety and relevance.
    
    Args:
        message: The user's input message
        
    Returns:
        Tuple of (is_safe, processed_message)
    """
    # Implementation...
```

### Error Handling

- Use appropriate exception types
- Log exceptions with sufficient context
- Provide user-friendly error messages
- Recover gracefully when possible

Example:
```python
try:
    result = api_client.make_request(params)
except ConnectionError as e:
    logger.error(f"API connection failed: {str(e)}")
    return "I'm having trouble connecting. Please try again in a moment."
except ValueError as e:
    logger.warning(f"Invalid parameter value: {str(e)}")
    return "I couldn't process that. Please try a different approach."
```

### Logging

- Use the configured logger for all logging
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include contextual information in log messages
- Avoid logging sensitive data

Example:
```python
logger.info(f"Processing message: {message[:20]}...")
logger.debug(f"Full message content: {message}")
logger.warning(f"Potentially concerning content detected: {categories}")
logger.error(f"Failed to process message: {error}")
```

## Documentation

When adding or modifying features:

1. **Update docstrings** for all new functions and classes
2. **Update README.md** if needed
3. **Add examples** for complex functionality
4. **Document configuration options** in relevant files

## Pull Request Process

1. **Create a feature branch** from `develop` branch
2. **Make your changes** with appropriate tests
3. **Run all tests** and fix any failures
4. **Submit a pull request** with detailed description
5. **Address review comments** as needed
6. **Rebase and squash** commits if requested
7. **Wait for approval** before merging

## Release Process

1. **Merge feature branches** into `develop`
2. **Create a release branch** (e.g., `release/v1.2.0`)
3. **Run full test suite** on release branch
4. **Update version numbers** in relevant files
5. **Create release notes** with changes and fixes
6. **Merge release branch** into `main` and tag the release
7. **Merge release branch** back into `develop`

## Resources

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Gradio Documentation](https://gradio.app/docs/)
- [ElevenLabs Documentation](https://docs.elevenlabs.io/)
