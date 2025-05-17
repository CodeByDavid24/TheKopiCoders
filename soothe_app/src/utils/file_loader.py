"""
File loader utilities for SootheAI.
Handles JSON and other file loading operations.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

# Set up logger
logger = logging.getLogger(__name__)


def load_json(filename: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file, returning an empty dict if file not found.

    Args:
        filename: Name of the JSON file, with or without extension

    Returns:
        Parsed JSON data or empty dict if file not found
    """
    # Add .json extension if not present
    if not filename.endswith('.json'):
        filename = f"{filename}.json"

    # Try different possible file locations
    possible_paths = [
        filename,
        os.path.join('soothe_app', filename),
        os.path.join('..', filename)
    ]

    for file_path in possible_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                logger.info(f"Loading JSON file: {file_path}")
                data = json.load(file)
                logger.debug(f"Successfully loaded JSON data from {file_path}")
                return data
        except FileNotFoundError:
            continue
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error loading {file_path}: {str(e)}")
            return {}

    logger.warning(f"JSON file not found in any location: {filename}")
    return {}


def save_json(data: Dict[str, Any], filename: str, indent: int = 2) -> bool:
    """
    Save data to a JSON file.

    Args:
        data: Data to save
        filename: Name of the file to save to, with or without extension
        indent: Indentation level for JSON formatting

    Returns:
        True if successful, False otherwise
    """
    # Add .json extension if not present
    if not filename.endswith('.json'):
        filename = f"{filename}.json"

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=indent)
            logger.info(f"Successfully saved JSON data to {filename}")
            return True
    except Exception as e:
        logger.error(f"Error saving JSON data to {filename}: {str(e)}")
        return False


def load_text_file(filename: str) -> Optional[str]:
    """
    Load text content from a file.

    Args:
        filename: Name of the text file to load

    Returns:
        File content as string, or None if file not found
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.info(f"Successfully loaded text from {filename}")
            return content
    except FileNotFoundError:
        logger.warning(f"Text file not found: {filename}")
        return None
    except Exception as e:
        logger.error(f"Error loading text from {filename}: {str(e)}")
        return None

# In file_loader.py, modify load_character_data function


def load_character_data(character_name: str = "serena") -> Dict[str, Any]:
    # Add more paths to look for character data
    character_paths = [
        os.path.join('characters', character_name),
        os.path.join('soothe_app', 'characters', character_name),
        os.path.join('soothe_app', 'config', 'characters', character_name),
        os.path.join('config', 'characters', character_name)
    ]

    # Try each path
    for character_path in character_paths:
        character_data = load_json(character_path)
        if character_data:
            return character_data


def find_file_in_directories(filename: str, directories: list) -> Optional[str]:
    """
    Search for a file in multiple directories.

    Args:
        filename: Name of the file to find
        directories: List of directories to search

    Returns:
        Full path to the file if found, None otherwise
    """
    for directory in directories:
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            logger.info(f"Found file {filename} in {directory}")
            return file_path

    logger.warning(
        f"File {filename} not found in any of the specified directories")
    return None


def load_config_file(config_name: str) -> Dict[str, Any]:
    """
    Load a configuration file from the config directory.

    Args:
        config_name: Name of the configuration file

    Returns:
        Configuration data as dictionary
    """
    # Look in standard config locations
    config_paths = [
        os.path.join('config', config_name),
        os.path.join('soothe_app', 'config', config_name),
        os.path.join('..', 'config', config_name)
    ]

    for path in config_paths:
        config_data = load_json(path)
        if config_data:
            return config_data

    logger.warning(
        f"Configuration file {config_name} not found, using empty config")
    return {}
