"""
File loader utilities for SootheAI.
Handles JSON and other file loading operations.
"""

import json  # For JSON file parsing
import logging  # For application logging
import os  # For file system operations
# Type hints for better code documentation
from typing import Dict, Any, Optional

# Set up logger for this module
logger = logging.getLogger(__name__)


def load_json(filename: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file, returning an empty dict if file not found.

    Args:
        filename: Name of the JSON file, with or without extension

    Returns:
        Dict[str, Any]: Parsed JSON data or empty dict if file not found

    Example:
        >>> character_data = load_json('characters/serena')
        >>> print(character_data['name'])
        'Serena'
    """
    # Add .json extension if not present
    if not filename.endswith('.json'):  # Check if extension already exists
        filename = f"{filename}.json"  # Append .json extension

    # Try different possible file locations for flexible deployment
    possible_paths = [
        filename,  # Current directory
        os.path.join('soothe_app', filename),  # In soothe_app directory
        os.path.join('..', filename)  # Parent directory
    ]

    # Attempt to load from each possible path
    for file_path in possible_paths:
        try:
            # Open with explicit UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as file:
                # Log successful file location
                logger.info(f"Loading JSON file: {file_path}")
                data = json.load(file)  # Parse JSON content
                # Log successful parsing
                logger.debug(f"Successfully loaded JSON data from {file_path}")
                return data  # Return parsed data
        except FileNotFoundError:
            continue  # Try next path if file not found
        except json.JSONDecodeError as e:
            # Log JSON parsing error
            logger.error(f"Error decoding JSON from {file_path}: {str(e)}")
            return {}  # Return empty dict on parsing error
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error loading {file_path}: {str(e)}")
            return {}  # Return empty dict on unexpected error

    # Log file not found warning
    logger.warning(f"JSON file not found in any location: {filename}")
    return {}  # Return empty dict if file not found anywhere


def save_json(data: Dict[str, Any], filename: str, indent: int = 2) -> bool:
    """
    Save data to a JSON file with error handling.

    Args:
        data: Data to save as JSON
        filename: Name of the file to save to, with or without extension
        indent: Indentation level for JSON formatting (default: 2)

    Returns:
        bool: True if successful, False otherwise

    Example:
        >>> success = save_json({'name': 'Serena'}, 'characters/serena')
        >>> print(success)
        True
    """
    # Add .json extension if not present
    if not filename.endswith('.json'):  # Check if extension already exists
        filename = f"{filename}.json"  # Append .json extension

    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filename)  # Extract directory path
        if directory:  # Only create if directory path exists
            # Create directory recursively
            os.makedirs(directory, exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as file:  # Open for writing with UTF-8 encoding
            # Write JSON with formatting
            json.dump(data, file, indent=indent, ensure_ascii=False)
            # Log successful save
            logger.info(f"Successfully saved JSON data to {filename}")
            return True  # Return success
    except Exception as e:
        # Log save error
        logger.error(f"Error saving JSON data to {filename}: {str(e)}")
        return False  # Return failure


def load_text_file(filename: str) -> Optional[str]:
    """
    Load text content from a file.

    Args:
        filename: Name of the text file to load

    Returns:
        Optional[str]: File content as string, or None if file not found

    Example:
        >>> content = load_text_file('prompts/system_prompt.txt')
        >>> if content:
        ...     print(f"Loaded {len(content)} characters")
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:  # Open with UTF-8 encoding
            content = file.read()  # Read entire file content
            # Log successful load
            logger.info(f"Successfully loaded text from {filename}")
            return content  # Return file content
    except FileNotFoundError:
        # Log file not found
        logger.warning(f"Text file not found: {filename}")
        return None  # Return None if file not found
    except Exception as e:
        # Log loading error
        logger.error(f"Error loading text from {filename}: {str(e)}")
        return None  # Return None on error


def load_character_data(character_name: str = "serena") -> Dict[str, Any]:
    """
    Load character data from JSON file with multiple fallback locations.

    Args:
        character_name: Name of the character to load (default: "serena")

    Returns:
        Dict[str, Any]: Character data dictionary or empty dict if not found

    Example:
        >>> serena_data = load_character_data("serena")
        >>> print(serena_data.get('personality', 'Unknown'))
    """
    # Add more paths to look for character data
    character_paths = [
        os.path.join('characters', character_name),  # In characters directory
        # In soothe_app/characters
        os.path.join('soothe_app', 'characters', character_name),
        # In soothe_app/config/characters
        os.path.join('soothe_app', 'config', 'characters', character_name),
        # In config/characters
        os.path.join('config', 'characters', character_name)
    ]

    # Try each path until character data is found
    for character_path in character_paths:
        # Attempt to load JSON from path
        character_data = load_json(character_path)
        if character_data:  # Check if data was successfully loaded
            # Log successful load location
            logger.info(f"Loaded character data from: {character_path}")
            return character_data  # Return character data

    # Log warning if character data not found anywhere
    logger.warning(
        f"Character data for '{character_name}' not found in any location")
    return {}  # Return empty dict if character not found


def find_file_in_directories(filename: str, directories: list) -> Optional[str]:
    """
    Search for a file in multiple directories.

    Args:
        filename: Name of the file to find
        directories: List of directories to search

    Returns:
        Optional[str]: Full path to the file if found, None otherwise

    Example:
        >>> config_path = find_file_in_directories('app_config.json', 
        ...                                       ['config', 'soothe_app/config'])
        >>> if config_path:
        ...     print(f"Found config at: {config_path}")
    """
    # Search through each directory
    for directory in directories:
        # Construct full file path
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):  # Check if file exists at this path
            # Log successful find
            logger.info(f"Found file {filename} in {directory}")
            return file_path  # Return full path to found file

    logger.warning(
        f"File {filename} not found in any of the specified directories")  # Log file not found
    return None  # Return None if file not found anywhere


def load_config_file(config_name: str) -> Dict[str, Any]:
    """
    Load a configuration file from the config directory.

    Args:
        config_name: Name of the configuration file (with or without .json extension)

    Returns:
        Dict[str, Any]: Configuration data as dictionary

    Example:
        >>> app_config = load_config_file('app_settings')
        >>> debug_mode = app_config.get('debug', False)
    """
    # Look in standard config locations
    config_paths = [
        os.path.join('config', config_name),  # In config directory
        # In soothe_app/config
        os.path.join('soothe_app', 'config', config_name),
        os.path.join('..', 'config', config_name)  # In parent/config
    ]

    # Try each configuration path
    for path in config_paths:
        config_data = load_json(path)  # Attempt to load configuration JSON
        if config_data:  # Check if configuration was loaded successfully
            # Log successful config load
            logger.info(f"Loaded configuration from: {path}")
            return config_data  # Return configuration data

    logger.warning(
        f"Configuration file {config_name} not found, using empty config")  # Log config not found
    return {}  # Return empty dict as fallback configuration
