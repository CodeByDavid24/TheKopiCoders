# Usage Guide

This document provides instructions for using the SootheAI application.

## Starting the Application

1. **Activate your virtual environment** (if not already activated):
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Launch the application**:
   ```bash
   python -m soothe_app.src.main
   ```

3. The application will start and open a Gradio web interface in your browser. If it doesn't open automatically, navigate to:
   ```
   http://localhost:7861
   ```

## Consent Flow

1. **Read the consent message**:  
   The application starts with a consent message explaining the purpose, content warnings, and data usage.

2. **Agree to terms**:  
   Type `I agree` in the chat box and press Enter.

3. **Start the game**:  
   Type `start game` and press Enter to begin Serena's story.

## Interacting with the Narrative

### Basic Interaction

- **Text input**: Type your desired actions or responses in the chat box.
- **Reading responses**: The system will respond with narrative text, Serena's thoughts, and possible options.
- **Making choices**: You can select from suggested options or type your own actions.

### Example Interactions

- `I want to raise my hand and ask a question` - Actions Serena might take
- `Let me take deep breaths to calm down` - Trying coping techniques
- `Talk to my friend Wei Ming about the exam` - Social interactions
- `How am I feeling right now?` - Self-reflection prompts
- `What do I think about this situation?` - Exploring Serena's thoughts

### Audio Narration (Optional)

If you've configured the ElevenLabs API:

- **Enable audio**: Type `enable audio` to turn on voice narration.
- **Disable audio**: Type `disable audio` to return to text-only mode.
- **Audio status**: Type `tts status` to check audio usage and limits.

## Story Progression

### Narrative Structure

The story follows Serena's experiences as a JC student in Singapore, focusing on:
- Academic pressures and expectations
- Social interactions with peers and teachers
- Internal experiences and physical sensations
- Choices and their consequences

### Story Length

- The narrative typically runs for **12-15 interactions** before reaching an ending.
- Three possible ending paths exist based on your choices:
  - **Successful Path**: Serena develops healthy coping skills
  - **Resilient Recovery**: Serena experiences difficulties but finds support
  - **Depression Spiral**: Serena's struggles intensify without adequate support

### Key Story Milestones

1. **Introduction**: Meet Serena and understand her context
2. **First Challenge**: Academic or social situation that creates pressure
3. **Coping Choices**: Options for handling challenges
4. **Character Interactions**: Encounters with family, friends, and teachers
5. **Turning Point**: Critical decision that influences the story path
6. **Resolution**: Outcome based on accumulated choices

## Tips for Meaningful Engagement

- **Be specific** in your responses for more tailored narrative progression.
- **Experiment with different approaches** to see how they affect Serena's experience.
- **Pay attention to physical sensations** described in the narrative as they provide clues about Serena's wellbeing.
- **Try various coping strategies** to see their effects on the story.
- **Engage with supporting characters** to develop different aspects of the narrative.

## Educational Elements

SootheAI is designed as an educational experience to help understand:
- How stress and anxiety can manifest physically
- The impact of academic pressure on wellbeing
- Effective and ineffective coping strategies
- The importance of social support and professional help when needed

At the end of your experience, you'll receive an educational summary highlighting key insights.

## Safety Features

If you encounter distressing content or want to stop:
- Type `pause` to take a break without ending the story.
- Close the browser tab to end the session completely.
- The application filters unsafe content both in your inputs and the AI responses.

## Getting Help

For technical issues:
- Check the [Installation Guide](installation.md) for setup problems
- Visit our GitHub repository for known issues
- Contact support at support@sootheai.example.com

For mental health support:
- National Care Hotline (Singapore): 1800-202-6868
- Samaritans of Singapore (SOS): 1-767
- IMH Mental Health Helpline: 6389-2222
