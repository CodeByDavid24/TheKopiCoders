# Anthropic API Prompt Engineering Cheatsheet for SootheAI

## Core Concepts for Claude Prompting

### System vs. User vs. Assistant Messages

| Message Type | Purpose | Best Use in SootheAI |
|-------------|---------|----------------------|
| **System** | Sets context and instructions | Define game rules, character details, and response formats |
| **User** | Player's input | Capture player decisions and questions |
| **Assistant** | Claude's response | Deliver narrative, scenarios, and choices |

### System Prompt Structure for SootheAI

```python
system_prompt = f"""
# Role Definition
You are an AI gamemaster for SootheAI, an anxiety awareness interactive narrative.

# Character Details
- Name: {character['name']}
- Age: 17
- Background: {character['physical']['race']['name']} Singaporean JC1 student
- Goal: Securing a place in NUS Medicine

# Response Format
1. Narrate the scene (1-2 paragraphs)
2. Describe Serena's thoughts/feelings (without labeling as anxiety)
3. Present exactly 4 choices, numbered 1-4

# Tone Guidelines
- Realistic depiction of student life
- Subtle manifestation of anxiety symptoms
- Academically focused narrative
- Use Singaporean English where appropriate

# Constraints
- Never explicitly label behaviors as anxiety-related
- Keep responses under 250 words
- Always maintain the character's voice and perspective
"""
```

## Advanced Techniques from Anthropic Courses

### 1. Clear Task Instructions

**Before:**

```
Create scenarios that incorporate her behaviors.
```

**After:**

```
Create scenarios that naturally incorporate her behaviors (arriving early to sit at the back, taking meticulous notes but rarely asking questions, studying alone during breaks) without labeling them as anxiety-related.
```

### 2. Few-Shot Examples

Add examples directly in your system prompt:

```
# Example Exchange
User: "I want to talk to my teacher about my grade"
Assistant: "The thought of approaching Mrs. Tan about your B- in Chemistry makes your stomach tighten. You rehearse what to say in your head as you walk toward the staff room.

Your options:
1. Wait until after school when fewer people are around to approach her
2. Ask a direct question about how to improve your grade
3. Mention you're aiming for Medicine and need advice on improvement
4. Decide it's better to study harder next time instead of discussing this grade"
```

### 3. Chain-of-Thought Reasoning

Include structured thinking instructions:

```
When developing scenarios, follow this reasoning process:
1. Consider Serena's current emotional state based on previous interactions
2. Identify a relevant academic or social situation from her daily routine
3. Determine physical manifestations of her anxiety appropriate to the situation
4. Create realistic choices that include both avoidance and confrontation options
```

### 4. XML Tagging for Structure

```
For each response, structure your output as:
<narrative>
[Scene description and what's happening]
</narrative>

<internal>
[Serena's thoughts and physical sensations]
</internal>

<choices>
1. [First option]
2. [Second option]
3. [Third option]
4. [Fourth option]
</choices>
```

## Anthropic Messages API Implementation

### Modern SDK Implementation

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    system=system_prompt,
    messages=[
        {"role": "user", "content": user_message}
    ],
    temperature=0.7,  # Adjust for consistency vs. creativity
    max_tokens=1000
)
result = response.content[0].text
```

### Key Parameters to Consider

| Parameter | Recommended Value | Effect |
|-----------|------------------|--------|
| `temperature` | 0.3-0.7 | Lower for consistent responses, higher for variety |
| `max_tokens` | 800-1000 | Enough for narrative + 4 choices |
| `top_p` | 0.9 | Controls diversity of word choices |
| `top_k` | 40 | Limits token selection pool |

## Context Management for SootheAI

### Efficient History Handling

```python
# Only include the most relevant history
# For SootheAI, track anxiety triggers encountered and choices made
relevant_history = []

# Add markers for important game events
for msg in full_history[-10:]:  # Last 10 exchanges
    if any(trigger in msg for trigger in anxiety_triggers):
        relevant_history.append({"role": "system", "content": f"Note: Player has encountered the '{trigger}' anxiety trigger."})
    relevant_history.append(msg)
```

### Prompt Compression Techniques

For long-running games, implement summarization:

```python
def summarize_history(history, max_tokens=2000):
    """Compress history when it gets too long"""
    if len(history) > 10:  # arbitrary threshold
        summary_prompt = f"Summarize the key events and Serena's emotional state from this conversation history: {history[:5]}"
        summary_response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=300
        )
        compressed = summary_response.content[0].text
        return [{"role": "system", "content": f"Previous conversation summary: {compressed}"}] + history[-5:]
    return history
```

## Response Evaluation

### Quality Assessment Checklist

- Does the response include all required sections? (narrative, internal thoughts, 4 choices)
- Are anxiety symptoms subtly portrayed without explicit labeling?
- Do the choices represent realistic options for the character?
- Is the narrative consistent with Serena's character profile?
- Does the response maintain appropriate length (under 250 words)?

### Self-Evaluation Prompt Addition

```python
# Add to your system prompt
At the end of each response, evaluate whether your output:
1. Subtly incorporated anxiety symptoms
2. Presented realistic academic pressure
3. Gave balanced choices (some healthy, some unhealthy coping)
4. Maintained character consistency

If you notice an issue, revise before sending.
```

## Best Practices for SootheAI

### DO

- Keep character details consistent throughout interactions
- Maintain subtle portrayal of anxiety symptoms
- Use specific Singaporean educational context (JC system, CCA, etc.)
- Provide balanced choices that explore different coping mechanisms
- Include physical symptoms (racing heart, stomach tightness) without labeling

### DON'T

- Explicitly diagnose or label anxiety
- Provide unrealistic or overly dramatic scenarios
- Include harmful coping mechanisms as viable choices
- Break character voice or perspective
- Ignore previous player choices in subsequent scenarios

## Customization for Different Anxiety Types

Add specificity to your system prompt based on anxiety type:

```python
anxiety_type = "academic_performance"  # Options: social, academic_performance, future_uncertainty

anxiety_manifestations = {
    "academic_performance": [
        "Checking work repeatedly",
        "Avoiding asking questions despite confusion",
        "Physical symptoms before tests (headache, nausea)",
        "Catastrophizing about grade impact"
    ],
    "social": [
        "Avoiding eye contact in group settings",
        "Rehearsing conversations mentally",
        "Declining social invitations",
        "Hyperawareness of others' reactions"
    ],
    "future_uncertainty": [
        "Excessive research about university requirements",
        "Difficulty making decisions about subjects",
        "Insomnia thinking about career path",
        "Seeking constant reassurance about choices"
    ]
}

# Add to system prompt:
f"""
Focus on these specific anxiety manifestations:
{anxiety_manifestations[anxiety_type]}
"""
```

---

## Implementation Checklist for SootheAI

- [ ] Update system prompt with structured sections
- [ ] Add few-shot examples for desired response format
- [ ] Implement proper message history management
- [ ] Adjust temperature based on desired consistency
- [ ] Include character details from JSON in system prompt
- [ ] Add response format guidelines with XML tags
- [ ] Ensure prompt includes both constraints and goals
- [ ] Consider adding chain-of-thought instructions
