# SootheAI - Interactive Mental Health Support for Singapore's Youth

SootheAI is an AI-powered interactive storytelling platform designed to help Singaporean students understand and manage anxiety through engaging narrative experiences. The application uses Claude AI to generate dynamic, culturally-relevant stories that provide mental health education and coping strategies.

## 🌟 Features

- **Interactive AI Storytelling**: Dynamic narratives that adapt to user choices
- **Mental Health Education**: Evidence-based anxiety management techniques
- **Singapore Context**: Stories set in familiar educational and cultural environments
- **Text-to-Speech Support**: Optional AI-generated voice narration
- **Safety Systems**: Comprehensive content filtering and crisis support resources
- **Multiple Versions**: Three iterations with progressive improvements

## 📋 Project Structure

```
soothe_app/
├── v1/                     # Initial prototype version
├── v2/                     # Core stable version
│   ├── core/              # Core engine components
│   │   ├── api_client.py          # Claude API integration
│   │   ├── narrative_engine.py    # Story generation logic
│   │   ├── content_filter.py      # Safety filtering system
│   │   └── filter_compatibility.py
│   ├── models/            # Data models
│   │   ├── character.py           # Character data structures
│   │   └── game_state.py          # Session management
│   ├── ui/                # User interface components
│   │   ├── gradio_interface.py    # Web interface
│   │   ├── tts_handler.py         # Text-to-speech system
│   │   └── speech_audit_trail.py  # TTS usage tracking
│   ├── utils/             # Utility modules
│   │   ├── file_loader.py         # File handling
│   │   ├── logger.py              # Logging configuration
│   │   ├── safety.py              # Safety utilities
│   │   └── tts_audit_utils.py     # TTS audit functions
│   └── main.py            # Application entry point
├── v3/                     # Enhanced UI version
│   └── ui/                # Improved interface components
├── config/                # Configuration files
│   ├── characters/        # Character definitions
│   ├── system_prompts/    # AI prompts
│   └── blacklist/         # Content filtering rules
├── game_data/             # Game content
│   ├── milestones/        # Story milestones
│   └── endings/           # Story endings
└── logs/                  # Application logs
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Claude API key from Anthropic
- ElevenLabs API key (optional, for TTS)
- FFmpeg (for audio playback)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd soothe_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Install FFmpeg** (for audio support)
   - **Windows**: Download from https://ffmpeg.org/
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

### Running the Application

Choose your preferred version:

**V2 (Stable)**
```bash
python -m soothe_app.v2.main
```

**V3 (Enhanced UI)**
```bash
python -m soothe_app.v3.main
```

The application will launch a web interface accessible at `http://localhost:7861`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
CLAUDE_API_KEY=your_claude_api_key_here

# Optional (for text-to-speech)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional (logging level)
LOG_LEVEL=INFO
```

### Character Configuration

Characters are defined in JSON files under `config/characters/`:
- `serena.json` - Main protagonist
- `mother.json` - Family dynamics
- `therapist.json` - Professional support
- `chloe.json` - Academic rival
- `teacher.json` - Educational support

### Content Filtering

Safety systems are configured in `config/blacklist/`:
- `blacklist.txt` - Harmful phrases
- `harmful_patterns_file.json` - Pattern matching rules
- `enhance_filter_config.json` - Filter settings

## 🎮 Usage

### Basic Interaction

1. **Start the application** and navigate to the web interface
2. **Read the consent message** and agree to terms
3. **Choose audio preferences** (with/without TTS)
4. **Type "start game"** to begin the interactive story
5. **Make choices** by selecting options or typing responses

### Available Commands

- `start game` - Begin the interactive story
- `enable audio` / `disable audio` - Toggle text-to-speech
- `tts status` - Check TTS usage statistics
- `tts report` - Generate TTS audit report

### Story Features

- **Autonomous Character Generation**: AI creates unique characters for each playthrough
- **Multiple Endings**: Different story outcomes based on choices
- **Educational Milestones**: Key learning moments about anxiety management
- **Cultural Authenticity**: Singapore-specific contexts and scenarios

## 🛡️ Safety Features

### Content Filtering
- **Multi-layer filtering** for harmful content
- **Pattern matching** for complex detection
- **Severity scoring** for appropriate responses
- **Context analysis** for comprehensive safety

### Crisis Support
- **Emergency contacts** prominently displayed
- **Safety disclaimers** throughout the experience
- **Professional help** guidance when appropriate
- **Resource links** to local mental health services

### Privacy Protection
- **No data storage** of personal conversations
- **Audit trails** for TTS usage only (anonymized)
- **Session-based** state management
- **Local processing** where possible

## 📊 Monitoring and Auditing

### TTS Audit Trail
The system tracks text-to-speech usage for:
- **Usage statistics** and rate limiting
- **Content categorization** for analytics
- **Error tracking** and performance monitoring
- **Privacy-preserving** hashed content logging

### Logging
Comprehensive logging includes:
- **Application events** and errors
- **Safety filter** activations
- **User interactions** (anonymized)
- **System performance** metrics

## 🧪 Development

### Project Versions

**V1**: Initial prototype with basic functionality
**V2**: Stable version with full feature set
**V3**: Enhanced UI with improved design and accessibility

### Architecture

- **Modular design** with clear separation of concerns
- **Plugin architecture** for easy feature additions
- **Configuration-driven** character and content management
- **Async-compatible** for scalability

### Testing

Run tests with appropriate test frameworks (add specific commands based on your test setup):

```bash
# Example test commands
python -m pytest tests/
python -m unittest discover tests/
```

## 📚 Educational Content

### Mental Health Topics
- Anxiety recognition and symptoms
- Healthy coping strategies
- Academic pressure management
- Support system building
- Professional help seeking

### Singapore Context
- Local education system pressures
- Cultural family dynamics
- Available mental health resources
- Community support networks

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add comprehensive docstrings
- Include appropriate error handling
- Test safety features thoroughly
- Maintain cultural sensitivity

## 📄 License

This project is licensed under [Your License] - see the LICENSE file for details.

## 🆘 Support and Resources

### Mental Health Resources (Singapore)
- **Emergency**: 999
- **Samaritans of Singapore (SOS)**: 1-767
- **National Care Hotline**: 1800-202-6868
- **IMH Mental Health Helpline**: 6389-2222
- **CHAT (Youth 16-30)**: 6493-6500

### Technical Support
- Check the [Issues](link-to-issues) page for common problems
- Review the documentation in `/docs/`
- Contact the development team

## ⚠️ Important Disclaimers

- **Educational Tool Only**: SootheAI is for educational awareness and is not a substitute for professional medical advice
- **Emergency Situations**: For mental health emergencies, contact emergency services immediately
- **Professional Help**: The tool complements but does not replace professional mental health care
- **Content Warning**: Stories may depict distressing situations related to anxiety and academic pressure

## 🔮 Future Development

- Enhanced multilingual support
- Extended character interaction systems
- Advanced personalization features
- Mobile application development
- Integration with local mental health services

---

**Made with ❤️ for Singapore's youth mental health**