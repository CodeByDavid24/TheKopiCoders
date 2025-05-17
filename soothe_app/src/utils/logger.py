"""
Logging utilities for SootheAI.
Configures application-wide logging.
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional

def configure_logging(log_file: str = 'soothe_app.log', 
                     console_level: int = logging.INFO, 
                     file_level: int = logging.INFO,
                     max_bytes: int = 1024*1024,  # 1MB
                     backup_count: int = 5) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to log file
        console_level: Logging level for console output
        file_level: Logging level for file output
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Root logger
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(min(console_level, file_level))
    
    # Remove existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: console={logging.getLevelName(console_level)}, "
               f"file={logging.getLevelName(file_level)}, log_file={log_file}")
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def set_module_level(module_name: str, level: int) -> None:
    """
    Set logging level for a specific module.
    
    Args:
        module_name: Module name
        level: Logging level
    """
    logging.getLogger(module_name).setLevel(level)
    logger = logging.getLogger(__name__)
    logger.info(f"Set logging level for {module_name} to {logging.getLevelName(level)}")

def create_named_logger(name: str, 
                       level: int = logging.INFO, 
                       log_file: Optional[str] = None) -> logging.Logger:
    """
    Create a named logger with optional separate log file.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional separate log file for this logger
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add file handler if specified
    if log_file:
        # Create directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=1024*1024,  # 1MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        
        # Remove any existing handlers of the same type
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                logger.removeHandler(handler)
                
        logger.addHandler(file_handler)
        
    return logger
