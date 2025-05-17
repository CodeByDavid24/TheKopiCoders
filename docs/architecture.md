# Architecture Overview

This document describes the architecture of the SootheAI application, explaining its components, interactions, and design principles.

## High-Level Architecture

SootheAI follows a modular architecture with clear separation of concerns:

![Architecture Diagram](architecture_diagram.png)

### Core Components

1. **User Interface Layer**: Gradio-based web interface
2. **Application Logic Layer**: Narrative engine and game state management
3. **Integration Layer**: API clients for Claude and ElevenLabs
4. **Data Layer**: Character definitions, system prompts, and game content
5. **Safety Layer**: Content filtering and safety mechanisms

## Component Interactions

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  User (Gradio) │────▶│ Narrative      │────▶│ Claude API     │
│  Interface     │◀────│ Engine         │◀────│ Client         │
└────────────────┘     └────────────────┘     └────────────────┘
                              │ ▲
                              ▼ │
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Safety Filter  │◀───▶│ Game State    │◀───▶│ ElevenLabs API │
│  System         │     │ Manager       │     │ (TTS)          │
└────────────────┘     └────────────────┘     └────────────────┘
                              │ ▲
                              ▼ │
                       ┌────────────────┐
                       │ Character &    │
                       │ Story Data     │
                       └────────────────┘
```

## Key Classes and Responsibilities

### UI Layer

- **GradioInterface** (`src/ui/gradio_interface.py`)
  - Creates and manages the web interface
  - Handles user input/output
  - Maintains chat history display
  - Coordinates with narrative engine

- **TTSHandler** (`src/ui/tts_handler.py`)
  - Manages text-to-speech functionality
  - Handles rate limiting and consent
  - Streams audio via ffmpeg

### Application Logic Layer

- **NarrativeEngine** (`src/core/narrative_engine.py`)
  - Core application logic
  - Processes user input and generates responses
  - Manages system prompts and messaging
  - Handles game progression and endings
  - Coordinates with safety systems

- **GameState** (`src/models/game_state.py`)
  - Tracks narrative state and progress
  - Manages character state and relationships
  - Records conversation history
  - Tracks user consent and preferences

### Integration Layer

- **ClaudeClient** (`src/core/api_client.py`)
  - Communicates with Anthropic's Claude API
  - Handles authentication and error management
  - Formats prompts and parses responses
  - Provides a singleton instance pattern

- **ElevenLabs Integration** (via `tts_handler.py`)
  - Optional text-to-speech capability
  - Handles streaming and playback
  - Manages API usage and rate limits

### Data Layer

- **Character** (`src/models/character.py`)
  - Defines character attributes and properties
  - Provides serialization/deserialization
  - Supports default values and inheritance

- **File Loaders** (`src/utils/file_loader.py`)
  - Load character definitions
  - Load configuration
  - Load game content and milestones

### Safety Layer

- **ContentFilter** (`src/core/content_filter.py`)
  - Multi-level safety filtering system
  - Pattern matching for harmful content
  - Context analysis for concerning combinations
  - Replacement strategies for unsafe content

- **Safety Utilities** (`src/utils/safety.py`)
  - Input/output safety checks
  - Alternative responses for unsafe inputs
  - Safety disclaimers and messaging

## Data Flow

### Startup Flow

1. Main application initializes
2. Environment variables and configuration loaded
3. API clients created and validated
4. Character data loaded
5. Game state initialized
6. Gradio interface created and launched

### User Interaction Flow

1. User enters text in Gradio interface
2. Input passed to narrative engine
3. Input checked for safety concerns
4. If safe, input processed by game state
5. Claude API generates response using system prompt
6. Response filtered for safety
7. Response returned to user interface
8. (Optional) Response converted to speech
9. Conversation history updated

### Content Safety Flow

```
User Input → Safety Check → Response Generation → Safety Filter → User
              ↓                                       ↓
        Unsafe Detected                         Unsafe Detected
              ↓                                       ↓
      Safety Response                          Safety Response
```

## Design Principles

### 1. Safety First

- All input and output is filtered for safety
- Multi-layered approach to content filtering
- Explicit consent required for participation
- Educational focus in sensitive areas

### 2. Modularity

- Clear separation of concerns
- Loose coupling between components
- Interface-based design for extensibility
- Single-responsibility principle adherence

### 3. Stateful Narrative

- Persistent game state across interactions
- Character state modeling
- Decision-based narrative progression
- Multiple ending pathways

### 4. API Abstraction

- Clean API client interfaces
- Error handling and recovery
- Configurable via environment
- Singleton patterns for shared resources

## Configuration

### System Prompts

- Located in `config/system_prompts/`
- Defines the narrative framework and rules
- Includes character attributes and state tracking
- Controls narrative style and safety boundaries

### Character Definitions

- Located in `config/characters/`
- JSON-based character definitions
- Extensible attribute system
- Support for multiple characters and relationships

### Safety Configuration

- Located in `config/blacklist/`
- Pattern-based content filtering
- Severity levels and categories
- Replacements and safe alternatives

## Extensibility Points

The architecture provides several extensibility points:

1. **New Characters**: Add new JSON definitions
2. **Additional Safety Rules**: Extend blacklists and patterns
3. **Alternative UIs**: Replace Gradio with other frameworks
4. **Custom Endings**: Create new ending narratives
5. **Enhanced State Tracking**: Add new state variables and triggers

## Performance Considerations

- **API Latency**: Claude API calls introduce latency
- **TTS Processing**: Text-to-speech adds additional latency
- **Memory Usage**: Game state grows with conversation history
- **Gradio Resource Usage**: Web interface can be resource-intensive

## Security Considerations

- **API Keys**: Stored in environment variables, not code
- **User Input**: All input filtered for safety concerns
- **Output Filtering**: All AI responses checked before display
- **Data Usage**: No permanent storage of conversation data
