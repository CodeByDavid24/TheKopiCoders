"""
API client module for SootheAI.
Provides abstraction layer for communication with Claude API.
"""

import anthropic
import httpx
import logging
import os
from typing import Tuple, List, Dict, Any, Optional

# Set up logger
logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude API client.

        Args:
            api_key: API key for Claude. If None, tries to load from environment.
        """
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        if not self.api_key:
            logger.error("CLAUDE_API_KEY environment variable not set")
            self.client = None
            self.error_message = "CLAUDE_API_KEY environment variable not set"
        else:
            self.client, self.error_message = self._initialize_client()

    def _initialize_client(self) -> Tuple[Optional[anthropic.Anthropic], str]:
        """
        Initialize the Claude client with error handling.

        Returns:
            Tuple of (client, error_message)
        """
        try:
            # Log API client initialization
            logger.info(
                "Attempting to initialize Claude client with standard configuration")

            # Try standard initialization first
            try:
                return anthropic.Anthropic(api_key=self.api_key), ""
            except TypeError as e:
                # Handle proxy configuration errors in some SDK versions
                if "unexpected keyword argument 'proxies'" in str(e):
                    logger.warning(
                        "Proxy configuration error, attempting alternative initialization")
                    http_client = httpx.Client()
                    return anthropic.Anthropic(api_key=self.api_key, http_client=http_client), ""
                else:
                    raise e

        except Exception as e:
            error_msg = f"Unexpected error during Claude client initialization: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    def is_ready(self) -> bool:
        """Check if client is initialized and ready to use."""
        return self.client is not None

    def get_error(self) -> str:
        """Get error message if initialization failed."""
        return self.error_message

    def generate_response(self,
                          messages: List[Dict[str, str]],
                          system_prompt: str,
                          model: str = "claude-3-7-sonnet-20250219",
                          max_tokens: int = 1000,
                          temperature: float = 0) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a response from Claude.

        Args:
            messages: List of message objects with role and content keys
            system_prompt: System prompt to guide Claude's behavior
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Randomness parameter (0 = deterministic)

        Returns:
            Tuple of (response_text, error_message)
        """
        if not self.is_ready():
            return None, f"Claude client not initialized: {self.error_message}"

        try:
            logger.info(
                f"Sending request to Claude API with {len(messages)} messages")

            # Check which version of the SDK we're using
            if hasattr(self.client, 'messages'):
                # New SDK version
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages,
                    system=system_prompt
                )
                result = response.content[0].text
                return result, None
            else:
                # Older SDK version
                logger.warning(
                    "Using older Anthropic SDK version with completion API")

                # Convert messages to older format
                prompt = ""
                for msg in messages:
                    if msg["role"] == "user":
                        prompt += f"\n\nHuman: {msg['content']}"
                    elif msg["role"] == "assistant":
                        prompt += f"\n\nAssistant: {msg['content']}"

                # Add final assistant prompt for completion
                prompt += "\n\nAssistant:"

                response = self.client.completion(
                    prompt=prompt,
                    model="claude-2.1",  # Older model for compatibility
                    temperature=temperature,
                    max_tokens_to_sample=max_tokens,
                    stop_sequences=["\n\nHuman:", "\n\nAssistant:"]
                )
                return response.completion, None

        except Exception as e:
            error_msg = f"Error communicating with Claude API: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    def get_narrative(self, prompt: str, system_prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a narrative response for the SootheAI experience.

        Args:
            prompt: Prompt to send to Claude
            system_prompt: System prompt with game mechanics

        Returns:
            Tuple of (narrative_text, error_message)
        """
        messages = [{"role": "user", "content": prompt}]
        return self.generate_response(messages, system_prompt)


# Singleton instance for global use
_claude_client = None


def get_claude_client(api_key: Optional[str] = None) -> ClaudeClient:
    """
    Get a singleton Claude client instance.

    Args:
        api_key: API key for Claude. If None, tries to load from environment.

    Returns:
        ClaudeClient instance
    """
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient(api_key)
    return _claude_client
