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

The character attributes are defined in `characters/serena.json`. You can modify this file to adjust character traits, behavior patterns, anxiety triggers, and coping mechanisms.

## Project Structure

- `main.py`: Core application with game logic and Gradio interface
- `characters/`: Directory containing character definitions
  - `serena.json`: Primary character definition and attributes
- `requirements.txt`: Required Python packages
