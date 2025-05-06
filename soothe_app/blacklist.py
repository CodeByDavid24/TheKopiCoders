# blacklist.py
# Module for content filtering and guardrails

import re
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Define sensitive phrases to be blacklisted
# These are phrases that could potentially lead to harmful content
BLACKLISTED_PHRASES = [
    # Self-harm related
    "commit suicide", "kill myself", "end my life", "take my own life",
    "self-harm", "hurt myself", "cutting myself", "suicide methods",

    # Extreme mental distress
    "i want to die", "i hate myself", "better off dead", "no reason to live",

    # Dangerous coping mechanisms
    "stop eating", "purge", "starve myself", "take pills", "overdose",
    "substance abuse", "get drunk", "get high",

    # Academic distress specific to student context
    "drop out", "run away", "give up on school", "academic failure",

    # Harmful advice
    "don't seek help", "hide your feelings", "isolation", "avoid therapy",

    # Other harmful content
    "self-diagnose", "ignore symptoms", "stop medication"
]


def load_blacklist_from_file(filename="blacklist.txt"):
    """
    Load additional blacklisted phrases from a file.

    Args:
        filename (str): Name of the blacklist file

    Returns:
        list: Combined list of blacklisted phrases
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            # Read lines, strip whitespace, and filter out empty lines and comments
            additional_phrases = [
                line.strip() for line in file
                if line.strip() and not line.strip().startswith('#')
            ]
            logger.info(
                f"Loaded {len(additional_phrases)} additional blacklisted phrases from {filename}")
            return BLACKLISTED_PHRASES + additional_phrases
    except FileNotFoundError:
        logger.warning(
            f"Blacklist file {filename} not found, using default blacklist")
        return BLACKLISTED_PHRASES
    except Exception as e:
        logger.error(f"Error loading blacklist file {filename}: {str(e)}")
        return BLACKLISTED_PHRASES


def contains_blacklisted_content(text, blacklist=None):
    """
    Check if text contains any blacklisted phrases.

    Args:
        text (str): Text to check
        blacklist (list, optional): List of blacklisted phrases to check against

    Returns:
        tuple: (contains_blacklisted_content, matched_phrases)
            - contains_blacklisted_content: Boolean indicating if blacklisted content was found
            - matched_phrases: List of matched blacklisted phrases
    """
    if blacklist is None:
        blacklist = BLACKLISTED_PHRASES

    if not text:
        return False, []

    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()

    # Find all matches
    matched_phrases = [
        phrase for phrase in blacklist if phrase.lower() in text_lower]

    return bool(matched_phrases), matched_phrases


def filter_content(text, replacement_text="[Content filtered for safety reasons]", blacklist=None):
    """
    Filter out blacklisted phrases from text.

    Args:
        text (str): Original text to filter
        replacement_text (str): Text to replace blacklisted phrases with
        blacklist (list, optional): List of blacklisted phrases to filter

    Returns:
        str: Filtered text with blacklisted phrases replaced
    """
    if blacklist is None:
        blacklist = BLACKLISTED_PHRASES

    if not text:
        return text

    filtered_text = text
    has_replacements = False

    # Compile all phrases into a single regex pattern for efficiency
    # Using word boundaries to match whole words/phrases
    pattern = r'\b(' + '|'.join(re.escape(phrase)
                                for phrase in blacklist) + r')\b'
    compiled_pattern = re.compile(pattern, re.IGNORECASE)

    # Check if any blacklisted phrases are in the text
    matches = compiled_pattern.findall(text)

    if matches:
        # Replace matched phrases with the replacement text
        filtered_text = compiled_pattern.sub(replacement_text, text)
        has_replacements = True
        logger.warning(
            f"Filtered {len(matches)} instances of blacklisted content: {', '.join(set(matches))}")

    return filtered_text


def get_safety_disclaimer():
    """
    Return a safety disclaimer for sensitive topics.

    Returns:
        str: Safety disclaimer text
    """
    return (
        "\n\n**Safety Notice:** If you're experiencing distress or having thoughts of self-harm, "
        "please reach out to a trusted adult, school counselor, or contact a mental health helpline:\n"
        "- National Care Hotline (Singapore): 1800-202-6868\n"
        "- Samaritans of Singapore (SOS): 1-767\n"
        "- IMH Mental Health Helpline: 6389-2222\n\n"
        "Remember that seeking help is a sign of strength, not weakness."
    )


def get_safe_response_alternative():
    """
    Return a safe response for when potentially harmful content is detected.

    Returns:
        str: Safe alternative response
    """
    return (
        "I notice this conversation is headed in a potentially sensitive direction. "
        "As Serena's story explores academic pressure and stress, it's important to focus on "
        "healthy coping strategies and seeking support when needed.\n\n"
        "Let's explore more constructive approaches to handling the challenges Serena faces. "
        "Would you like to:\n\n"
        "1. Learn about healthy stress management techniques\n"
        "2. Explore how Serena might talk to a trusted friend or teacher\n"
        "3. Consider how Serena could balance academic goals with self-care\n"
        "4. Continue the story in a different direction"
    ) + get_safety_disclaimer()
