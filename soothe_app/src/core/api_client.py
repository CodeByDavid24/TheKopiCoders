"""
API client module for SootheAI.
Provides abstraction layer for communication with Claude API.
This module handles all interactions with Anthropic's Claude API,
including initialization, error handling, and message processing.
"""

import anthropic  # Anthropic's official SDK for Claude API
import httpx      # HTTP client library for custom configurations
import logging    # Standard Python logging for debugging and monitoring
import os         # Operating system interface for environment variables
# Type hints for better code documentation
from typing import Tuple, List, Dict, Any, Optional

# Set up logger instance for this module
# Creates logger with module name for identification
logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Client for interacting with Claude API.

    This class provides a high-level interface for communicating with
    Anthropic's Claude API, handling authentication, error management,
    and response processing.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude API client with optional API key.

        Args:
            api_key: API key for Claude. If None, tries to load from environment.
                    This allows for flexible authentication methods.
        """
        # Try to use provided key or fall back to environment variable
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")

        # Check if API key was successfully obtained
        if not self.api_key:
            # Log critical error
            logger.error("CLAUDE_API_KEY environment variable not set")
            self.client = None  # Set client to None to indicate failure
            # Store error for later retrieval
            self.error_message = "CLAUDE_API_KEY environment variable not set"
        else:
            # Initialize client if API key is available
            self.client, self.error_message = self._initialize_client()

    def _initialize_client(self) -> Tuple[Optional[anthropic.Anthropic], str]:
        """
        Initialize the Claude client with comprehensive error handling.

        This method handles various initialization scenarios including
        proxy configuration issues and SDK version differences.

        Returns:
            Tuple of (client_instance, error_message)
            - client_instance: Anthropic client object or None if failed
            - error_message: Empty string if successful, error description if failed
        """
        try:
            # Log initialization attempt for debugging
            logger.info(
                "Attempting to initialize Claude client with standard configuration")

            # Try standard initialization first (most common case)
            try:
                # Return client and empty error string
                return anthropic.Anthropic(api_key=self.api_key), ""
            except TypeError as e:
                # Handle specific proxy configuration errors in some SDK versions
                if "unexpected keyword argument 'proxies'" in str(e):
                    logger.warning(
                        "Proxy configuration error, attempting alternative initialization")
                    # Create custom HTTP client to bypass proxy issues
                    http_client = httpx.Client()
                    return anthropic.Anthropic(api_key=self.api_key, http_client=http_client), ""
                else:
                    raise e  # Re-raise if it's a different TypeError

        except Exception as e:
            # Catch any other unexpected errors during initialization
            error_msg = f"Unexpected error during Claude client initialization: {str(e)}"
            logger.error(error_msg)  # Log the full error for debugging
            return None, error_msg  # Return None client and error message

    def is_ready(self) -> bool:
        """
        Check if client is initialized and ready to use.

        Returns:
            bool: True if client is ready, False otherwise
        """
        return self.client is not None  # Simple check for client existence

    def get_error(self) -> str:
        """
        Get error message if initialization failed.

        Returns:
            str: Error message from initialization, empty if no error
        """
        return self.error_message  # Return stored error message

    def generate_response(self,
                          # List of message objects with role/content
                          messages: List[Dict[str, str]],
                          system_prompt: str,              # System instructions for Claude
                          model: str = "claude-sonnet-4-20250514",  # Model version
                          max_tokens: int = 1000,          # Maximum response length
                          temperature: float = 0) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a response from Claude using the messages API.

        Args:
            messages: List of message objects with role and content keys
                     Format: [{"role": "user", "content": "message text"}]
            system_prompt: System prompt to guide Claude's behavior and context
            model: Claude model to use (defaults to claude-3-7-sonnet)
            max_tokens: Maximum tokens in response (controls response length)
            temperature: Randomness parameter (0 = deterministic, 1 = creative)

        Returns:
            Tuple of (response_text, error_message)
            - response_text: Claude's response or None if error
            - error_message: None if successful, error description if failed
        """
        # Check if client was properly initialized
        if not self.is_ready():
            return None, f"Claude client not initialized: {self.error_message}"

        try:
            # Log request details for debugging and monitoring
            logger.info(
                f"Sending request to Claude API with {len(messages)} messages")

            # Check which version of the Anthropic SDK we're using
            if hasattr(self.client, 'messages'):
                # New SDK version with messages API (preferred method)
                response = self.client.messages.create(
                    model=model,                    # Specify which Claude model to use
                    max_tokens=max_tokens,          # Limit response length
                    temperature=temperature,        # Control randomness
                    messages=messages,              # Conversation history
                    system=system_prompt           # System instructions
                )
                # Extract text from response object
                result = response.content[0].text
                return result, None  # Return response and no error
            else:
                # Older SDK version with completion API (fallback)
                logger.warning(
                    "Using older Anthropic SDK version with completion API")

                # Convert messages format to older prompt format
                prompt = ""
                for msg in messages:
                    if msg["role"] == "user":
                        # Format user messages
                        prompt += f"\n\nHuman: {msg['content']}"
                    elif msg["role"] == "assistant":
                        # Format assistant messages
                        prompt += f"\n\nAssistant: {msg['content']}"

                # Add final assistant prompt for completion
                prompt += "\n\nAssistant:"

                # Use older completion API
                response = self.client.completion(
                    prompt=prompt,                          # Formatted prompt string
                    model="claude-sonnet-4-20250514",       # Model version
                    temperature=temperature,                # Randomness setting
                    max_tokens_to_sample=max_tokens,       # Different parameter name in old API
                    # Stop at conversation markers
                    stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
                )
                return response.completion, None  # Return completion text and no error

        except Exception as e:
            # Handle any errors during API communication
            error_msg = f"Error communicating with Claude API: {str(e)}"
            logger.error(error_msg)  # Log error for debugging
            return None, error_msg   # Return no response and error message

    def get_narrative(self, prompt: str, system_prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a narrative response for the SootheAI experience.

        This is a convenience method that wraps generate_response for
        single-turn narrative generation.

        Args:
            prompt: User prompt to send to Claude
            system_prompt: System prompt with game mechanics and context

        Returns:
            Tuple of (narrative_text, error_message)
            - narrative_text: Generated narrative or None if error
            - error_message: None if successful, error description if failed
        """
        # Convert single prompt to messages format
        messages = [{"role": "user", "content": prompt}]
        # Use the main generate_response method
        return self.generate_response(messages, system_prompt)


# Singleton pattern implementation for global client access
_claude_client = None  # Module-level variable to store singleton instance


def get_claude_client(api_key: Optional[str] = None) -> ClaudeClient:
    """
    Get a singleton Claude client instance.

    This function implements the singleton pattern to ensure only one
    Claude client exists throughout the application lifecycle, improving
    resource management and consistency.

    Args:
        api_key: API key for Claude. If None, tries to load from environment.

    Returns:
        ClaudeClient: Singleton client instance
    """
    global _claude_client  # Access module-level singleton variable

    # Create client only if it doesn't exist yet
    if _claude_client is None:
        # Initialize with provided or environment key
        _claude_client = ClaudeClient(api_key)

    return _claude_client  # Return existing or newly created client
