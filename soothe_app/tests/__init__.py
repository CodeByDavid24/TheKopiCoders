"""
SootheAI Tests Package
This package contains all the test suites for the SootheAI application.
"""

import sys
import os

# Add the parent directory to the path to allow importing from soothe_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test package structure information
__all__ = [
    'fixtures',
    'integration',
    'unit'
]
