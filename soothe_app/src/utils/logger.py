"""
Logging utilities for SootheAI.
Configures application-wide logging.
"""

import logging  # Python's built-in logging module
import logging.handlers  # For advanced logging handlers like rotation
import os  # For file system operations
import sys  # For system-specific parameters and functions
from typing import Optional  # Type hints for better code documentation


def configure_logging(log_file: str = 'soothe_app.log',
                      console_level: int = logging.INFO,
                      file_level: int = logging.INFO,
                      max_bytes: int = 1024*1024,  # 1MB default max file size
                      backup_count: int = 5) -> logging.Logger:
    """
    Configure logging for the application with both console and file output.

    Args:
        log_file: Path to log file for persistent logging
        console_level: Logging level for console output (default: INFO)
        file_level: Logging level for file output (default: INFO)
        max_bytes: Maximum size of log file before rotation (default: 1MB)
        backup_count: Number of backup files to keep during rotation (default: 5)

    Returns:
        logging.Logger: Configured root logger instance

    Example:
        >>> logger = configure_logging('app.log', logging.DEBUG)
        >>> logger.info("Application started")
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)  # Extract directory from log file path
    # Check if directory needs to be created
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)  # Create directory recursively

    # Configure root logger with the most permissive level
    root_logger = logging.getLogger()  # Get root logger instance
    # Set to minimum level to capture all messages
    root_logger.setLevel(min(console_level, file_level))

    # Remove existing handlers to avoid duplication during reconfiguration
    # Iterate over copy of handlers list
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)  # Remove each existing handler

    # Create formatter for consistent log message format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler for real-time log viewing
    console_handler = logging.StreamHandler(sys.stdout)  # Output to stdout
    # Set console-specific logging level
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)  # Apply consistent formatting
    # Add console handler to root logger
    root_logger.addHandler(console_handler)

    # Create file handler with rotation for persistent logging
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,  # Log file path
        maxBytes=max_bytes,  # Maximum file size before rotation
        backupCount=backup_count,  # Number of backup files to maintain
        encoding='utf-8'  # Use UTF-8 encoding for international characters
    )
    file_handler.setLevel(file_level)  # Set file-specific logging level
    file_handler.setFormatter(formatter)  # Apply consistent formatting
    root_logger.addHandler(file_handler)  # Add file handler to root logger

    # Create logger for this module and log configuration success
    logger = logging.getLogger(__name__)  # Get logger for this specific module
    logger.info(f"Logging configured: console={logging.getLevelName(console_level)}, "
                f"file={logging.getLevelName(file_level)}, log_file={log_file}")  # Log configuration details

    return root_logger  # Return configured root logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        logging.Logger: Logger instance for the specified name

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    return logging.getLogger(name)  # Return named logger instance


def set_module_level(module_name: str, level: int) -> None:
    """
    Set logging level for a specific module to control verbosity.

    Args:
        module_name: Name of the module to configure
        level: Logging level (e.g., logging.DEBUG, logging.INFO)

    Example:
        >>> set_module_level('soothe_app.ui', logging.DEBUG)
        >>> # Now UI module will log debug messages
    """
    logging.getLogger(module_name).setLevel(
        level)  # Set level for specified module
    logger = logging.getLogger(__name__)  # Get logger for this module
    # Log level change
    logger.info(
        f"Set logging level for {module_name} to {logging.getLevelName(level)}")


def create_named_logger(name: str,
                        level: int = logging.INFO,
                        log_file: Optional[str] = None) -> logging.Logger:
    """
    Create a named logger with optional separate log file.

    Args:
        name: Logger name for identification
        level: Logging level for this specific logger (default: INFO)
        log_file: Optional separate log file for this logger

    Returns:
        logging.Logger: Configured logger instance with optional file output

    Example:
        >>> audit_logger = create_named_logger('audit', logging.INFO, 'audit.log')
        >>> audit_logger.info("User action logged")
    """
    logger = logging.getLogger(name)  # Get or create named logger
    logger.setLevel(level)  # Set logging level for this logger

    # Create formatter for consistent message format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add file handler if specified for separate log file
    if log_file:
        # Create directory if needed
        # Extract directory from log file path
        log_dir = os.path.dirname(log_file)
        # Check if directory needs creation
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)  # Create directory recursively

        # Create rotating file handler for this specific logger
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,  # Specific log file path
            maxBytes=1024*1024,  # 1MB max file size
            backupCount=3,  # Keep 3 backup files
            encoding='utf-8'  # UTF-8 encoding for international characters
        )
        file_handler.setFormatter(formatter)  # Apply consistent formatting
        file_handler.setLevel(level)  # Set handler logging level

        # Remove any existing handlers of the same type to avoid duplication
        # Iterate over copy of handlers list
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.handlers.RotatingFileHandler):  # Check handler type
                # Remove existing rotating file handler
                logger.removeHandler(handler)

        logger.addHandler(file_handler)  # Add new file handler

    return logger  # Return configured named logger
