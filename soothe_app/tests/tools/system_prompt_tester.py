import os
import json
import anthropic
import argparse
from dotenv import load_dotenv
import time
import sys
from typing import List, Dict, Any, Optional, Tuple

# Add parent directory to import path to enable importing from main app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables for API key
load_dotenv()


class SootheAIPromptTester:
    """
    A testing utility for validating SootheAI system prompts before deployment.

    This tester follows the consent flow of the SootheAI application:
    1. User must agree to terms (type "I agree")
    2. User must start the game (type "start game")
    3. Then gameplay interactions begin
    """

    def __init__(self, system_prompt=None, prompt_file=None, character_file=None, api_key=None):
        """
        Initialize the tester with a system prompt and API connection.

        Args:
            system_prompt (str, optional): The system prompt to test.
            prompt_file (str, optional): Path to a file containing the system prompt.
            character_file (str, optional): Path to character JSON file to load.
            api_key (str, optional): Claude API key. If None, loads from environment.
        """
        # Set up API key
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key provided. Set CLAUDE_API_KEY environment variable or pass api_key parameter.")

        # Initialize client
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Track consent flow state
        self.consent_given = False
        self.game_started = False

        # Load character data if provided
        self.character = None
        if character_file:
            try:
                with open(character_file, 'r', encoding='utf-8') as f:
                    self.character = json.load(f)
                print(f"Loaded character data from {character_file}")
            except Exception as e:
                print(f"Error loading character file: {e}")

        # Set system prompt
        if system_prompt:
            self.system_prompt = system_prompt
        elif prompt_file:
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.system_prompt = f.read()
                print(f"Loaded system prompt from {prompt_file}")
            except Exception as e:
                print(f"Error loading prompt file: {e}")
                self.system_prompt = None
        else:
            self.system_prompt = None

        # If character data was loaded and system prompt has format placeholders
        if self.character and self.system_prompt and '{character' in self.system_prompt:
            # Format the system prompt with character data
            try:
                self.system_prompt = self.system_prompt.format(
                    character=self.character)
                print("Formatted system prompt with character data")
            except KeyError as e:
                print(f"Warning: Character data missing key {e}")
            except Exception as e:
                print(f"Error formatting system prompt: {e}")

        self.test_cases = []
        self.test_results = []
        self.conversation_history = []

    def load_test_cases(self, test_file):
        """
        Load test cases from a JSON file.

        Args:
            test_file (str): Path to JSON file with test cases.

        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                self.test_cases = json.load(f)
            print(f"Loaded {len(self.test_cases)} test cases from {test_file}")
            return True
        except Exception as e:
            print(f"Error loading test cases: {e}")
            return False

    def add_test_case(self, user_input, description=None, check_terms=None, avoid_terms=None):
        """
        Add a test case to the suite.

        Args:
            user_input (str): The user message to test.
            description (str, optional): Description of what this test is checking.
            check_terms (list, optional): Terms that SHOULD appear in the response.
            avoid_terms (list, optional): Terms that should NOT appear in the response.
        """
        self.test_cases.append({
            "user_input": user_input,
            "description": description or f"Testing response to: {user_input[:30]}...",
            "check_terms": check_terms or [],
            "avoid_terms": avoid_terms or []
        })
        print(f"Added test case: {description or user_input[:30]}")

    def add_sootheai_consent_test_cases(self):
        """Add test cases specifically for SootheAI's consent flow and gameplay."""
        self.test_cases = [
            {
                "user_input": "I agree",
                "description": "Step 1: Consent acceptance - should confirm without revealing mechanics",
                "check_terms": ["Thank you", "start game"],
                "avoid_terms": ["anxiety", "overwhelm level", "mechanics", "system", "instructions"]
            },
            {
                "user_input": "start game",
                "description": "Step 2: Game start - should show introduction without revealing mechanics",
                "check_terms": ["Serena", "JC", "student"],
                "avoid_terms": ["anxiety", "overwhelm level", "wellbeing level", "game mechanics", "system", "narrative mechanics"]
            },
            {
                "user_input": "I want to raise my hand and ask a question in class",
                "description": "Step 3: First interaction - should show physical symptoms without labeling",
                "check_terms": ["hand", "question", "feel"],
                "avoid_terms": ["anxiety", "trigger", "level", "overwhelm level", "score", "+"]
            },
            {
                "user_input": "What's Serena's anxiety level right now?",
                "description": "Direct question about mechanics - should not reveal",
                "check_terms": ["feel", "experience"],
                "avoid_terms": ["anxiety level", "score", "overwhelm level", "scale", "system", "mechanics", "1-10"]
            },
            {
                "user_input": "I want to take a break and breathe deeply for a few minutes",
                "description": "Testing coping mechanism - should show effects without mentioning system",
                "check_terms": ["breathe", "calmer", "better"],
                "avoid_terms": ["anxiety reduction", "overwhelm reduction", "level", "decreased by", "coping mechanism", "-1", "-2"]
            }
        ]
        print(f"Added {len(self.test_cases)} SootheAI consent flow test cases")

    def run_tests(self, save_results=True, result_file="test_results.json"):
        """
        Run all test cases in sequence, respecting the consent flow.

        Args:
            save_results (bool): Whether to save results to a file.
            result_file (str): Filename to save results.

        Returns:
            dict: Summary of test results.
        """
        if not self.system_prompt:
            raise ValueError(
                "No system prompt set. Set a prompt before running tests.")

        if not self.test_cases:
            raise ValueError(
                "No test cases defined. Add test cases before running tests.")

        self.test_results = []

        print(f"\n{'='*50}")
        print(f"RUNNING {len(self.test_cases)} TEST CASES")
        print(f"{'='*50}\n")

        # Clear conversation history to start fresh
        self.conversation_history = []

        # Run each test case
        for i, test_case in enumerate(self.test_cases):
            print(f"\nTEST CASE {i+1}: {test_case['description']}")
            print(f"User input: {test_case['user_input']}")

            # Check consent flow state
            user_input = test_case['user_input'].lower()
            if user_input == "i agree":
                self.consent_given = True
            elif user_input == "start game" and self.consent_given:
                self.game_started = True

            try:
                # Create messages array with conversation history
                messages = self.conversation_history.copy()

                # Add the current test case to messages
                messages.append(
                    {"role": "user", "content": test_case['user_input']})

                # Make API call
                print("Calling Claude API...")
                start_time = time.time()
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    system=self.system_prompt,
                    messages=messages,
                    max_tokens=1000
                )
                end_time = time.time()

                # Extract response content
                response_text = response.content[0].text
                print(f"\nResponse (preview): {response_text[:100]}...\n")

                # Update conversation history for the next test
                self.conversation_history.append(
                    {"role": "user", "content": test_case['user_input']})
                self.conversation_history.append(
                    {"role": "assistant", "content": response_text})

                # Check for presence of required terms
                check_results = []
                for term in test_case.get('check_terms', []):
                    term_present = term.lower() in response_text.lower()
                    check_results.append({
                        "term": term,
                        "present": term_present,
                        "required": True
                    })
                    if not term_present:
                        print(
                            f"FAIL: Required term '{term}' not found in response")

                # Check for absence of forbidden terms
                avoid_results = []
                for term in test_case.get('avoid_terms', []):
                    term_present = term.lower() in response_text.lower()
                    avoid_results.append({
                        "term": term,
                        "present": term_present,
                        "required": False
                    })
                    if term_present:
                        print(
                            f"FAIL: Forbidden term '{term}' found in response")

                # Calculate test result
                check_pass = all(result["present"] for result in check_results)
                avoid_pass = all(not result["present"]
                                 for result in avoid_results)
                test_pass = check_pass and avoid_pass

                # Store test result
                result = {
                    "test_case": test_case,
                    "response": response_text,
                    "term_checks": check_results + avoid_results,
                    "passed": test_pass,
                    "response_time": end_time - start_time
                }
                self.test_results.append(result)

                # Display result
                print(f"Test {'PASSED' if test_pass else 'FAILED'}")
                print(f"Response time: {result['response_time']:.2f}s")

            except Exception as e:
                print(f"ERROR: {str(e)}")
                self.test_results.append({
                    "test_case": test_case,
                    "error": str(e),
                    "passed": False
                })

        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results if result.get("passed", False))
        failed_tests = total_tests - passed_tests

        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0
        }

        # Display summary
        print(f"\n{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Pass rate: {summary['pass_rate']*100:.1f}%")

        # Save results if requested
        if save_results:
            try:
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "summary": summary,
                        "results": self.test_results
                    }, f, indent=2)
                print(f"\nSaved test results to {result_file}")
            except Exception as e:
                print(f"\nError saving test results: {e}")

        return summary

    def interactive_test(self):
        """
        Start an interactive testing session that respects SootheAI's consent flow.
        """
        if not self.system_prompt:
            raise ValueError(
                "No system prompt set. Set a prompt before starting interactive test.")

        print(f"\n{'='*50}")
        print(f"INTERACTIVE TESTING SESSION")
        print(f"{'='*50}")
        print("SootheAI requires consent flow: First type 'I agree', then 'start game'")
        print("Type your messages to test the system prompt.")
        print("Type 'quit', 'exit', or 'q' to end the session.")
        print("Type 'save' to save the conversation history.")

        conversation = []

        while True:
            # Get user input
            user_input = input("\nYou: ")

            # Check for exit command
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Ending interactive testing session.")
                break

            # Check for save command
            if user_input.lower() == 'save':
                filename = input(
                    "Enter filename to save conversation (default: conversation.json): ") or "conversation.json"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(conversation, f, indent=2)
                    print(f"Saved conversation to {filename}")
                except Exception as e:
                    print(f"Error saving conversation: {e}")
                continue

            # Track consent flow
            if user_input.lower() == "i agree":
                self.consent_given = True
                print("(Tester note: Consent recorded)")
            elif user_input.lower() == "start game" and self.consent_given:
                self.game_started = True
                print("(Tester note: Game started)")

            try:
                # Add user message to conversation
                conversation.append({"role": "user", "content": user_input})

                # Make API call
                print("Claude is thinking...")
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    system=self.system_prompt,
                    messages=conversation,
                    max_tokens=1000
                )

                # Extract and display response
                response_text = response.content[0].text
                print(f"\nClaude: {response_text}")

                # Add assistant response to conversation
                conversation.append(
                    {"role": "assistant", "content": response_text})

            except Exception as e:
                print(f"Error: {str(e)}")

    def test_with_blacklist(self, blacklist_file=None):
        """
        Special test function that tests interaction with the blacklist functionality.

        Args:
            blacklist_file (str, optional): Path to blacklist file to test against.
        """
        try:
            # Try to import from parent directory
            from soothe_app.src.core.content_filter import contains_blacklisted_content, load_blacklist_from_file

            # Load blacklist
            if blacklist_file:
                blacklist = load_blacklist_from_file(blacklist_file)
            else:
                blacklist = load_blacklist_from_file()

            print(f"Loaded blacklist with {len(blacklist)} phrases")

            # Create test cases with blacklisted content
            blacklist_test_cases = [
                {
                    "user_input": "I want to commit suicide",
                    "description": "Testing blacklisted phrase - should be detected"
                },
                {
                    "user_input": "I'm feeling so overwhelmed that sometimes I think about how to end my life",
                    "description": "Testing blacklisted phrase in context - should be detected"
                },
                {
                    "user_input": "I Want To DIE",
                    "description": "Testing case insensitivity - should be detected"
                }
            ]

            print(f"\n{'='*50}")
            print(f"RUNNING BLACKLIST INTEGRATION TESTS")
            print(f"{'='*50}\n")

            for test_case in blacklist_test_cases:
                print(f"\nTesting: {test_case['description']}")
                print(f"Input: {test_case['user_input']}")

                # Check against blacklist
                contains, matched = contains_blacklisted_content(
                    test_case['user_input'], blacklist)

                print(f"Contains blacklisted content: {contains}")
                if contains:
                    print(f"Matched phrases: {matched}")

        except ImportError:
            print(
                "Could not import blacklist module. Make sure it's in the parent directory.")
        except Exception as e:
            print(f"Error testing blacklist integration: {e}")


def main():
    """Command-line interface for the SootheAI system prompt tester."""
    parser = argparse.ArgumentParser(
        description="Test your SootheAI system prompt")

    # Input arguments
    parser.add_argument("--prompt", type=str,
                        help="Path to system prompt file")
    parser.add_argument("--character", type=str,
                        help="Path to character JSON file")
    parser.add_argument("--api-key", type=str,
                        help="Claude API key (will use CLAUDE_API_KEY env var if not provided)")
    parser.add_argument("--tests", type=str,
                        help="Path to test cases JSON file")

    # Mode arguments
    parser.add_argument("--consent-flow", action="store_true",
                        help="Run consent flow test suite")
    parser.add_argument("--interactive", action="store_true",
                        help="Start interactive testing session")
    parser.add_argument("--blacklist", type=str,
                        help="Test blacklist integration with optional path to blacklist file")
    parser.add_argument(
        "--save", type=str, default="test_results.json", help="Path to save test results")

    args = parser.parse_args()

    try:
        # Initialize tester
        tester = SootheAIPromptTester(
            prompt_file=args.prompt,
            character_file=args.character,
            api_key=args.api_key
        )

        # Run requested test mode
        if args.interactive:
            tester.interactive_test()
        elif args.blacklist is not None:
            tester.test_with_blacklist(
                args.blacklist if args.blacklist != "True" else None)
        else:
            # Add test cases
            if args.tests:
                tester.load_test_cases(args.tests)

            if args.consent_flow or not args.tests:
                tester.add_sootheai_consent_test_cases()

            # Run tests
            tester.run_tests(
                save_results=bool(args.save),
                result_file=args.save
            )

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    main()
