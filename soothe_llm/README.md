# SootheAI: Interactive Mental Health Narrative Game

An AI-driven interactive narrative experience that explores themes of teenage anxiety through the character of Serena, a high school student in Singapore navigating academic pressures while managing her mental health.

## About the Project

SootheAI creates an immersive, choice-based narrative that:

- Educates players about teenage anxiety in a relatable context
- Presents realistic scenarios based on everyday high school situations
- Offers meaningful choices that demonstrate different coping strategies
- Provides a safe space to explore mental health challenges

## Features

- Text-based interactive storytelling powered by Ollama's large language models
- Character-driven narrative focusing on mental health themes
- Clean web interface built with Gradio
- Persistent game state and conversation history
- Detailed character framework defined via JSON configuration

## Setup Instructions

### 1. Install Ollama

First, make sure you have [Ollama](https://ollama.ai/) installed on your system.

### 2. Pull the Required Model

```bash
ollama pull llama3
```

### 3. Set Up Virtual Environment

```bash
conda create --prefix=venv python=3.11 -y
conda activate ./venv
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the Application

```bash
python main.py
```

## Gameplay

In SootheAI, you interact with a narrative centered around Serena, a quiet but determined high school student dealing with anxiety in a competitive academic environment. The game presents scenarios where Serena faces various anxiety triggers, and you choose how she responds.

Each scenario presents multiple options representing:

- Healthy coping mechanisms
- Avoidance behaviors
- Unhealthy coping strategies
- Neutral actions

Your choices influence Serena's journey and teach valuable lessons about managing anxiety.

## Character Customization

The character attributes are defined in `serena.json`. You can modify this file to adjust character traits, behavior patterns, anxiety triggers, and coping mechanisms.

## Project Structure

- `main.py`: Core application with game logic and Gradio interface
- `serena.json`: Character definition and attributes
- `requirements.txt`: Required Python packages
