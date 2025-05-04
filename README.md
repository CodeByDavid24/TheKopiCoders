# SootheAI: Interactive Mental Health Narrative Game

An AI-driven interactive narrative experience that explores themes of teenage anxiety through the character of Serena, a JC student in Singapore navigating academic pressures while managing her mental health.

## About the Project

SootheAI creates an immersive, choice-based narrative that:

- Educates players about teenage anxiety in a relatable context
- Presents realistic scenarios based on everyday JC student situations
- Offers meaningful choices that demonstrate different coping strategies
- Provides a safe space to explore mental health challenges

## Features

- Text-based interactive storytelling powered by large language models
- Character-driven narrative focusing on mental health themes
- Clean web interface built with Gradio
- Persistent game state and conversation history
- Detailed character framework defined via JSON configuration

## Project Structure

- `soothe_app/`: Core application directory
  - `main.py`: Core application with game logic and Gradio interface
  - `characters/`: Directory containing character definitions
    - `serena.json`: Primary character definition and attributes
    - `chloe.json`: Supporting character definition
    - `mother.json`: Family member character definition
    - `therapist.json`: Supporting character for mental health guidance
- `doc/`: Documentation files
  - `features/`: Detailed documentation for each feature in my requirements gathering
    - `feature_1.md`: User input function with ethics and software requirements
  - `anthropic-prompt-cheatsheet.md`: Guide for structuring Claude API prompts
  - `code-breakdown.md`: Detailed explanation of application code
- `requirements.txt`: Required Python packages

## Setup Instructions

### 1. Install Dependencies

```bash
conda create --prefix=venv python=3.11 -y
conda activate ./venv
python -m pip install -r requirements.txt
```

### 2. API Configuration

Create a `.env` file with your API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Run the Application

```bash
cd soothe_app
python main.py
```

## Gameplay

In SootheAI, you interact with a narrative centered around Serena, a dedicated JC1 student at Raffles Junior College dealing with unacknowledged anxiety in Singapore's competitive academic environment. The game presents scenarios where Serena faces various anxiety triggers, and you choose how she responds.

Each scenario presents multiple options representing:

- Healthy coping mechanisms
- Avoidance behaviors
- Unhealthy coping strategies
- Neutral actions

Your choices influence Serena's journey and teach valuable lessons about managing anxiety, even when the character doesn't recognize her experiences as anxiety.

## Character Customization

The character attributes are defined in the JSON files located in the `soothe_app/characters/` directory. You can modify these files to adjust character traits, behavior patterns, anxiety triggers, and coping mechanisms.

## Development Notes

See `doc/anthropic-prompt-cheatsheet.md` for guidance on structuring prompts for the Claude API, and `doc/code-breakdown.md` for a detailed explanation of the application's architecture.
