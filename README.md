# SootheAI

An interactive mental health education platform that helps Singaporean youths understand anxiety through immersive narrative experiences.

## Problem Statement

Youths (15-35) often lack knowledge about anxiety and mental health issues, leading to:

- Difficulty recognizing symptoms in themselves and others
- Inadequate support for peers experiencing anxiety
- Stigma surrounding mental health challenges
- Limited awareness of healthy coping strategies

## Solution

SootheAI is an AI-powered interactive fiction platform that educates through simulation and storytelling:

- **Interactive Scenarios**: Users navigate situations where they make choices on how to help someone experiencing anxiety, learning effective communication and support strategies.
- **Empathy Training**: Users can experience scenarios from the perspective of someone with anxiety, gaining insight into the challenges and emotions associated with the condition.
- **Educational Content**: Through engaging storytelling and realistic scenarios, users learn about anxiety symptoms, triggers, and healthy coping mechanisms.

## Features

- Text-based interactive storytelling powered by Claude 3.5 Sonnet
- Character-driven narrative focusing on mental health themes in a Singaporean context
- Clean, accessible web interface built with Gradio
- Persistent conversation history to track progress
- Detailed character framework with realistic anxiety behaviors and triggers
- API key configuration interface for Claude access

## Project Structure

```
soothe_llm/
├── main.py              # Core application logic
├── serena.json          # Character definition file
├── requirements.txt     # Python dependencies for the project
└── README.md            # Technical documentation
```

## Technical Implementation

SootheAI uses:

- **Anthropic's Claude API**: Cloud-based LLM for generating responsive, contextual narrative
- **Gradio**: Web interface for user interaction
- **JSON Configuration**: Character attributes and behaviors defined in structured format

## Setup Instructions

### 1. Claude API Key

You'll need an API key from Anthropic. Sign up at [Anthropic's website](https://www.anthropic.com/) to obtain one.

### 2. Set Up Virtual Environment

```bash
conda create --prefix=venv python=3.11 -y
conda activate ./venv
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the Application

```bash
cd soothe_llm
python main.py
```

### 5. Configure API Key

Once the application is running, go to the "API Key" tab and enter your Claude API key before starting the game.

## Gameplay

In SootheAI, users interact with a narrative centered around Serena, a Chinese high school student in Singapore dealing with anxiety in a competitive academic environment. The game presents authentic scenarios where Serena faces various anxiety triggers, and users choose how she responds.

Each scenario offers multiple options representing:

- Healthy coping mechanisms
- Avoidance behaviors
- Unhealthy coping strategies
- Neutral actions

User choices influence Serena's journey while teaching valuable lessons about managing anxiety.

## Character Customization

The character attributes are defined in `serena.json`. This file can be modified to adjust character traits, behavior patterns, anxiety triggers, and coping mechanisms to create different scenarios or characters.

## Contributing

Contributions to SootheAI are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
