# Feature 1: User Input Functionality

## Overview

This document details the implementation of the user input functionality in SootheAI, including the consent message system, front-end interface, and input processing logic.

## Front-End Implementation (Software Requirement)

SootheAI utilizes Gradio to create an intuitive chat-based interface for user interaction. The front-end components are defined in the `start_game()` function:

```python
chat_interface = gr.ChatInterface(
    main_loop,
    chatbot=gr.Chatbot(
        height=500,
        placeholder="Type 'I agree' to begin",
        show_copy_button=True,
        render_markdown=True,
        value=[[None, consent_message]]  # Pre-populated with consent message
    ),
    textbox=gr.Textbox(placeholder="Type 'I agree' to continue...",
                       container=False, scale=7),
    title="SootheAI",
    theme="soft",
    examples=["Listen to music", "Journal", "Continue the story"],
    cache_examples=False,
)
```

Key front-end features:

- Chat window with 500px height for message display
- Pre-loaded consent message when the application starts
- Text input field with a prompt to guide initial interaction
- Example inputs as quick-access buttons
- Markdown rendering support for rich text formatting
- Copy button to allow users to save responses

## Consent Message (Ethics Requirement)

The application includes a mandatory consent message that users must acknowledge before proceeding:

```python
consent_message = """
**Start Game - Important Information**

**Warning & Consent:**
This is a fictional story designed to help you understand anxiety. Please be aware that some of the content may depict distressing situations. **Do not replicate or engage in any harmful actions shown in the game.** If you're feeling distressed, we encourage you to seek professional help.

Your choices and input will directly shape the direction of the story. Your decisions may influence the narrative, and some of your inputs might be used within the system to enhance your experience. By starting the game, you agree to these terms.

Type 'I agree' then 'Start game' to continue.
"""
```

This message addresses several ethical considerations:

1. Warning about potentially distressing content
2. Advising against replicating harmful actions
3. Encouraging professional help for those experiencing distress
4. Informing users about how their inputs will be used
5. Requiring explicit consent through user action

## Consent Tracking System

The application tracks user consent through the `game_state` dictionary:

```python
game_state = {
    'seed': np.random.randint(0, 1000000),
    'character': character,
    'history': [],
    'consent_given': False,  # Initially set to False
    'start': None
}
```

The `consent_given` flag is initially set to `False` and is only changed when the user explicitly types "I agree".

## User Input Processing Logic

The core input processing occurs in the `run_action()` function:

```python
def run_action(message: str, history: list, game_state: dict) -> str:
    # [API client verification code omitted]

    # Check if consent has been given
    if not game_state['consent_given']:
        if message.lower() == 'i agree':
            game_state['consent_given'] = True
            return "Thank you for agreeing to the terms. Type 'start game' to begin."
        else:
            return consent_message
            
    # [Rest of the function for handling game inputs]
```

The user input flow works as follows:

1. All user inputs are processed through the `main_loop()` function, which calls `run_action()`
2. If consent hasn't been given, the system checks if the user typed "i agree" (case-insensitive)
3. When "i agree" is detected, `game_state['consent_given']` is set to `True`
4. The system then prompts the user to type "start game" to begin
5. Any other input before consent is given results in the consent message being repeated
6. After consent, the system processes game-specific commands and forwards user inputs to the AI

## Game Start Handling

Once consent is given, the system processes the "start game" command:

```python
# Check if this is the start of the game
if message.lower() == 'start game':
    # If we haven't generated the start yet, do it now
    if game_state['start'] is None:
        game_state['start'] = get_initial_response()
    return game_state['start']
```

This triggers the initial game narrative to be loaded or generated using the Claude API.

## Complete User Input Flow

The complete user input flow is:

1. User sees the consent message upon application launch
2. User must type "I agree" to proceed (consent tracking)
3. After consent, user types "start game" to begin the actual game
4. All subsequent inputs are processed through the AI
5. User inputs and AI responses are tracked in `game_state['history']`

This implementation ensures ethical compliance by requiring explicit consent while providing an intuitive user interface.
