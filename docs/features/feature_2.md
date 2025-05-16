# Feature 2: LLM Text Generation with Guardrails

## Overview

This document details the implementation of LLM (Large Language Model) text generation with safety guardrails in SootheAI, including the blacklisting system for harmful or sensitive phrases, integration with Claude's API, and the asynchronous handling of model responses.

## Ethics Requirements

### Content Safety Guardrails

The ethics requirements for this feature are centered around protecting vulnerable youth users from potentially harmful content:

1. **Blacklist Implementation**: The system implements guardrails by maintaining a comprehensive blacklist of harmful or sensitive phrases that could potentially trigger or exacerbate mental health issues among users.

2. **Content Categories Restricted**:
   - Self-harm related phrases (e.g., "commit suicide", "hurt myself")
   - Extreme mental distress expressions (e.g., "want to die", "better off dead")
   - Dangerous coping mechanisms (e.g., "stop eating", "substance abuse")
   - Academic-specific harmful content (e.g., "drop out", "academic failure")
   - Harmful advice (e.g., "don't seek help", "hide your feelings")

3. **Two-way Protection**:
   - Prevents harmful user inputs from being processed by the LLM
   - Filters LLM-generated content that might contain sensitive phrases

4. **Safety Notices**: Provides appropriate safety disclaimers and alternative responses when potentially harmful content is detected.

5. **Helpline Information**: Automatically includes mental health helpline contact information when sensitive topics are discussed.

## Software Requirements

### LLM Integration

1. **Claude API Integration**:
   - Integration with Anthropic's Claude API for generating narrative responses
   - Proper error handling for API communication
   - Support for different SDK versions

2. **Asynchronous API Handling**:
   - Asynchronous processing of API calls to prevent UI blocking
   - Proper response handling with timeout management
   - Error recovery mechanisms

### Content Filtering System

1. **Detection Mechanism**:
   - Case-insensitive pattern matching for blacklisted phrases
   - Support for partial and exact matches
   - Performance optimized for real-time filtering

2. **Filtering Implementation**:
   - Replacement of blacklisted content with appropriate alternative text
   - Configurable replacement text
   - Logging of filtered content for monitoring

3. **Blacklist Management**:
   - External file-based configuration (blacklist.txt)
   - Support for comments and structured organization
   - Runtime loading and updating capabilities

4. **Safe Response Generation**:
   - Alternative response templates for redirecting harmful conversations
   - Safety disclaimer inclusion mechanism
   - Context-appropriate redirection options

### User Experience Considerations

1. **Transparency**:
   - Clear indication when content has been filtered
   - Appropriate explanations without revealing specific blocked content
   - Educational approach to content restrictions

2. **Performance**:
   - Minimal latency added by the filtering process
   - Efficient pattern matching for real-time interactions
   - Optimized API calls to reduce response time

## Implementation Details

The content filtering system is implemented in `blacklist.py` with these key components:

```python
# Core filtering functions
def contains_blacklisted_content(text, blacklist):
    """Check if text contains any blacklisted phrases."""
    # Implementation details...

def filter_content(text, replacement_text, blacklist):
    """Filter out blacklisted phrases from text."""
    # Implementation details...

def get_safety_disclaimer():
    """Return a safety disclaimer for sensitive topics."""
    # Implementation details...

def get_safe_response_alternative():
    """Return a safe response for potentially harmful content."""
    # Implementation details...
```

The integration with the LLM is handled in `main.py`:

```python
def check_input_safety(message):
    """Check user input for potentially harmful content."""
    # Implementation details...

def filter_response_safety(response):
    """Filter LLM response for safety."""
    # Implementation details...
```

## Testing Strategy

The guardrails feature is tested with unit tests that verify:

1. Detection of blacklisted content in various contexts
2. Proper filtering and replacement of harmful phrases
3. Loading of blacklist entries from configuration files
4. Generation of appropriate safety disclaimers and alternative responses
5. Integration with the main application flow

## Future Enhancements

1. **Machine Learning-based Detection**:
   - Move beyond simple pattern matching to context-aware detection
   - Train models to understand nuanced harmful content

2. **Personalized Filtering Levels**:
   - Age-appropriate filtering based on user profiles
   - Adjustable sensitivity settings for educational contexts

3. **Continuous Improvement**:
   - Regular updates to the blacklist based on user interactions
   - Feedback mechanism for false positives/negatives
