# Anthropic Prompt Cheatsheet for SootheAI

This guide provides best practices for crafting effective prompts for the Anthropic Claude API when working with the SootheAI application.

## Basic Prompt Structure

When creating prompts for narrative generation in SootheAI, follow this basic structure:

```
[INSTRUCTIONS: Specific guidance for Claude]

Context about Serena and her current situation...

[REQUEST: What you want Claude to generate]
```

## System Prompt Structure

The SootheAI system prompt follows a specific structure:

1. **Character Profile** - Details about Serena and her life context
2. **Hidden Game Mechanics** - State tracking, triggers, and thresholds
3. **Response Requirements** - Dos and don'ts for narrative generation
4. **Examples** - Model examples of correct/incorrect responses
5. **Safety Guidelines** - Content restrictions and redirections

## Effective Techniques

### Do's:
- **Be specific**: "Describe Serena's physical sensations when she's called on in class" (better than "Describe Serena in class")
- **Use second-person perspective**: "You notice your heart racing as you approach the front of the classroom..."
- **Include sensory details**: Request physical sensations, environmental details, and internal thoughts
- **Request options**: "End with 3-4 choices for how Serena might respond to this situation"
- **Maintain continuity**: Reference previous interactions and choices

### Don'ts:
- **Avoid clinical terminology**: Don't use "anxiety", "panic attack", "trigger", etc.
- **Don't reference mechanics**: Never mention wellbeing levels, relationship scores, etc.
- **Don't break immersion**: Don't reference the system or simulation nature
- **Don't use tags**: Avoid XML-style tags in your visible requests

## Examples

### Effective Prompt:
```
Create a scene where Serena is preparing for her Chemistry practical exam. 
Show her physical sensations, racing thoughts, and the classroom environment.
End with 3-4 choices for how she might approach the first experiment.
```

### Ineffective Prompt:
```
Increase Serena's anxiety level by 2 points as she prepares for her exam.
Show her having a minor panic attack and then give the player some coping mechanism options.
```

## Testing Prompts

Use the `system_prompt_tester.py` utility to test your prompts before integrating them:

```bash
python tests/tools/system_prompt_tester.py --prompt your_prompt.txt --interactive
```

## Content Safety Guidelines

- Never generate content that encourages self-harm or dangerous behaviors
- Don't provide information about harmful coping mechanisms
- Always promote healthy strategies and appropriate support
- Balance realism with hope and guidance
- Redirect concerning user content toward constructive alternatives

## Further Resources

- [Claude API Documentation](https://docs.anthropic.com/)
- [Effective Prompting Guide](https://www.anthropic.com/news/claude-prompt-engineering)
- [Content Safety Guidelines](https://www.anthropic.com/safety)
