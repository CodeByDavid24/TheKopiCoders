# Installation Guide

This guide provides instructions for setting up and installing the SootheAI application on your system.

## Prerequisites

Before installing SootheAI, ensure you have the following:

- Python 3.8 or higher
- pip (Python package installer)
- ffmpeg (for text-to-speech functionality)
- Git (for cloning the repository)

## Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/soothe_app.git
   cd soothe_app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## API Keys Setup

SootheAI requires API keys for its core functionality:

1. **Create a .env file**:
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys** to the `.env` file:
   ```
   # Required
   CLAUDE_API_KEY=your_claude_api_key_here
   
   # Optional (for text-to-speech)
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

   - Get a Claude API key from [Anthropic](https://www.anthropic.com/)
   - (Optional) Get an ElevenLabs API key from [ElevenLabs](https://elevenlabs.io/)

3. **Run the setup script**:
   ```bash
   python setup.py
   ```
   This will create necessary directories and configuration files.

## Content Filter Setup

SootheAI includes an enhanced content filter for safety:

1. **Verify blacklist files**:
   ```bash
   python -m soothe_app.tests.unit.test_content_filter
   ```

2. **Customize blacklist** (optional):
   - Edit files in the `soothe_app/config/blacklist/` directory
   - Add additional terms to `blacklist.txt`
   - Modify pattern matching in `harmful_patterns_file.json`

## Character Configuration

To customize the main character:

1. **Edit character files** in `soothe_app/config/characters/`:
   - `serena.json` - Main character
   - `mother.json` - Serena's mother
   - `therapist.json` - School counselor
   - `chloe.json` - Classmate/academic rival
   - `teacher.json` - Chemistry teacher

2. **Test your configuration**:
   ```bash
   python -m soothe_app.tests.tools.system_prompt_tester --character soothe_app/config/characters/serena.json --interactive
   ```

## Testing Your Installation

To verify your installation:

1. **Run the test suite**:
   ```bash
   python test_runner.py
   ```

2. **Run a quick integration test**:
   ```bash
   python -m soothe_app.tests.integration.test_full_flow
   ```

3. **Start the application in test mode**:
   ```bash
   python -m soothe_app.src.main --test
   ```

## Troubleshooting

### API Connection Issues

If you experience connection issues with Claude API:
- Verify your API key in the `.env` file
- Check your internet connection
- Ensure your API key has not expired

### Text-to-Speech Not Working

If TTS functionality isn't working:
- Verify ffmpeg is installed and in your PATH
- Check your ElevenLabs API key
- Ensure the ElevenLabs Python library is installed

### Content Filter Errors

If content filter issues occur:
- Check blacklist file formats
- Verify Python encoding settings
- Run the content filter tests

## Next Steps

After successful installation, refer to the following guides:
- [Usage Guide](usage.md) - How to use the application
- [Development Guide](development.md) - How to develop and extend features
- [Architecture](architecture.md) - Understanding the system design

## Getting Help

If you encounter issues not covered here:
- Check the [GitHub Issues](https://github.com/yourusername/soothe_app/issues)
- Open a new issue with detailed information about your problem
- Contact the development team
