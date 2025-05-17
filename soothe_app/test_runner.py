#!/usr/bin/env python3
"""
Test runner for SootheAI tests
Provides an easy way to run unit and integration tests
"""

import unittest
import sys
import os
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_runner')

# Add the parent directory to the path to allow importing from soothe_app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def discover_and_run_tests(test_type="all", verbosity=2, pattern="test_*.py", failfast=False):
    """
    Discover and run tests of the specified type
    
    Args:
        test_type: Type of tests to run ('unit', 'integration', 'all')
        verbosity: Level of detail in test output (1-3)
        pattern: File pattern to match for test files
        failfast: Stop at first failure if True
        
    Returns:
        unittest.TestResult: The test result object
    """
    start_time = datetime.now()
    logger.info(f"Starting {test_type} tests at {start_time}")
    
    # Initialize test loader
    loader = unittest.TestLoader()
    
    # Discover tests based on type
    if test_type == "unit":
        start_dir = os.path.join(os.path.dirname(__file__), "tests/unit")
        suite = loader.discover(start_dir, pattern=pattern)
    elif test_type == "integration":
        start_dir = os.path.join(os.path.dirname(__file__), "tests/integration")
        suite = loader.discover(start_dir, pattern=pattern)
    else:  # "all" or any other value
        start_dir = os.path.join(os.path.dirname(__file__), "tests")
        suite = loader.discover(start_dir, pattern=pattern)
    
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    
    # Run tests
    result = runner.run(suite)
    
    # Log test results
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Completed {test_type} tests in {duration}")
    logger.info(f"Tests run: {result.testsRun}, Errors: {len(result.errors)}, Failures: {len(result.failures)}, Skipped: {len(result.skipped)}")
    
    return result


def run_specific_test(test_path, verbosity=2, failfast=False):
    """
    Run a specific test module, class, or method
    
    Args:
        test_path: Path to the test in format 'module.class.method'
        verbosity: Level of detail in test output (1-3)
        failfast: Stop at first failure if True
        
    Returns:
        unittest.TestResult: The test result object
    """
    start_time = datetime.now()
    logger.info(f"Starting specific test {test_path} at {start_time}")
    
    try:
        # Try to load the specified test
        if '.' in test_path:
            # If it's a module.class or module.class.method format
            suite = unittest.defaultTestLoader.loadTestsFromName(test_path)
        else:
            # If it's just a module name
            suite = unittest.defaultTestLoader.loadTestsFromName(f"tests.{test_path}")
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to load test {test_path}: {str(e)}")
        return None
    
    # Create test runner
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    
    # Run tests
    result = runner.run(suite)
    
    # Log test results
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Completed specific test in {duration}")
    logger.info(f"Tests run: {result.testsRun}, Errors: {len(result.errors)}, Failures: {len(result.failures)}, Skipped: {len(result.skipped)}")
    
    return result


def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(description="Run SootheAI tests")
    parser.add_argument("--type", choices=["unit", "integration", "all"], 
                        default="all", help="Type of tests to run")
    parser.add_argument("--verbosity", type=int, choices=[1, 2, 3], 
                        default=2, help="Verbosity level (1-3)")
    parser.add_argument("--pattern", type=str, default="test_*.py", 
                        help="Pattern for test file discovery")
    parser.add_argument("--failfast", action="store_true", 
                        help="Stop on first test failure")
    parser.add_argument("--specific", type=str, 
                        help="Run a specific test module, class, or method")
    
    args = parser.parse_args()
    
    # Run tests based on arguments
    if args.specific:
        result = run_specific_test(args.specific, args.verbosity, args.failfast)
    else:
        result = discover_and_run_tests(args.type, args.verbosity, args.pattern, args.failfast)
    
    # Return appropriate exit code
    return 0 if result and result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
