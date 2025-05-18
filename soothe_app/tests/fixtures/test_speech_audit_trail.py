"""
Integration Tests for Speech Synthesis Audit Trail
"""

from soothe_app.src.utils.tts_audit_utils import log_tts_event, log_tts_error, create_tts_report
from soothe_app.src.ui.tts_handler import TTSHandler
from soothe_app.src.ui.speech_audit_trail import SpeechSynthesisAuditTrail, get_audit_trail

import unittest
import os
import sys
import time
import json
import tempfile
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the modules to test


class TestSpeechAuditTrail(unittest.TestCase):
    """Test the speech synthesis audit trail functionality."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary log file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(
            self.temp_dir.name, "test_audit_log.jsonl")

        # Create the audit trail with the test log file
        self.audit_trail = SpeechSynthesisAuditTrail(
            log_file_path=self.log_path)

    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()

    def test_log_session_start(self):
        """Test that session start is logged correctly."""
        # Session start is already logged in setUp

        # Check that the log file exists and contains the session start entry
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)

            # Parse the session start entry
            entry = json.loads(lines[0])
            self.assertEqual(entry['event_type'], 'session_start')
            self.assertEqual(entry['session_id'], self.audit_trail.session_id)

    def test_log_synthesis(self):
        """Test logging a successful synthesis event."""
        # Log a synthesis event
        text = "This is a test synthesis."
        category = "test_category"
        metadata = {"voice_id": "test_voice", "model_id": "test_model"}

        entry = self.audit_trail.log_synthesis(
            text=text,
            category=category,
            was_successful=True,
            metadata=metadata
        )

        # Verify the entry
        self.assertEqual(entry['session_id'], self.audit_trail.session_id)
        self.assertEqual(entry['event_type'], 'synthesis')
        self.assertEqual(entry['content_length'], len(text))
        self.assertEqual(entry['category'], category)
        self.assertTrue(entry['successful'])
        self.assertEqual(entry['metadata'], metadata)

        # Check that the entry was written to the log file
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)  # Session start + synthesis

            synthesis_entry = json.loads(lines[1])
            self.assertEqual(synthesis_entry['event_type'], 'synthesis')
            self.assertEqual(synthesis_entry['content_preview'], text)

    def test_log_synthesis_error(self):
        """Test logging a failed synthesis event."""
        # Log a synthesis error
        text = "This synthesis failed."
        error_message = "Test error message"

        entry = self.audit_trail.log_synthesis_error(
            text=text,
            error_message=error_message,
            category="error_category"
        )

        # Verify the entry
        self.assertEqual(entry['session_id'], self.audit_trail.session_id)
        self.assertEqual(entry['event_type'], 'synthesis')
        self.assertFalse(entry['successful'])
        self.assertEqual(entry['metadata']['error_message'], error_message)

        # Check that the entry was written to the log file
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)  # Session start + error

            error_entry = json.loads(lines[1])
            self.assertEqual(error_entry['event_type'], 'synthesis')
            self.assertFalse(error_entry['successful'])

    def test_log_session_end(self):
        """Test ending a session and logging statistics."""
        # Log some synthesis events
        self.audit_trail.log_synthesis(
            text="First synthesis",
            category="category1"
        )
        self.audit_trail.log_synthesis(
            text="Second synthesis",
            category="category2"
        )

        # End the session
        end_entry = self.audit_trail.log_session_end()

        # Verify the entry
        self.assertEqual(end_entry['session_id'], self.audit_trail.session_id)
        self.assertEqual(end_entry['event_type'], 'session_end')

        # Check the session summary
        summary = end_entry['session_summary']
        self.assertEqual(summary['total_synthesis_count'], 2)
        self.assertEqual(summary['total_chars_synthesized'], len(
            "First synthesis") + len("Second synthesis"))
        self.assertEqual(summary['synthesis_categories'], {
                         "category1": 1, "category2": 1})

        # Check that the entry was written to the log file
        with open(self.log_path, 'r') as f:
            lines = f.readlines()
            # Session start + 2 synthesis + session end
            self.assertEqual(len(lines), 4)

            end_entry = json.loads(lines[3])
            self.assertEqual(end_entry['event_type'], 'session_end')

    def test_extract_audit_report(self):
        """Test extracting an audit report from the log file."""
        # Log various events
        self.audit_trail.log_synthesis(text="Text 1", category="narrative")
        self.audit_trail.log_synthesis(text="Text 2", category="dialogue")
        self.audit_trail.log_synthesis(text="Text 3", category="narrative")
        self.audit_trail.log_session_end()

        # Extract the report
        report = SpeechSynthesisAuditTrail.extract_audit_report(
            log_file_path=self.log_path,
            days=7
        )

        # Verify the report
        self.assertEqual(report['total_sessions'], 1)
        self.assertEqual(report['total_synthesis_events'], 3)
        self.assertEqual(report['total_chars_synthesized'], len(
            "Text 1") + len("Text 2") + len("Text 3"))
        self.assertEqual(report['synthesis_by_category'], {
                         "narrative": 2, "dialogue": 1})


class TestTTSHandlerIntegration(unittest.TestCase):
    """Test the integration of TTS handler with audit trail."""

    def setUp(self):
        """Set up the test environment."""
        # Create a mock ElevenLabs client
        self.mock_elevenlabs = MagicMock()

        # Create a temporary log file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_path = os.path.join(
            self.temp_dir.name, "test_integration_log.jsonl")

        # Patch the audit trail to use our test log file
        self.audit_trail_patcher = patch(
            'soothe_app.src.ui.speech_audit_trail._audit_trail', None)
        self.audit_trail_patcher.start()

        # Create a new audit trail with our test log file
        with patch('soothe_app.src.ui.speech_audit_trail.SpeechSynthesisAuditTrail.__init__',
                   return_value=None):
            from soothe_app.src.ui.speech_audit_trail import SpeechSynthesisAuditTrail
            audit_trail = SpeechSynthesisAuditTrail()
            audit_trail.log_file_path = self.log_path
            audit_trail.session_id = "test_session"
            audit_trail.synthesis_count = 0
            audit_trail.session_start_time = time.time()
            audit_trail.total_chars_synthesized = 0
            audit_trail.synthesis_categories = {}
            audit_trail._write_log_entry = MagicMock()
            audit_trail.log_synthesis = MagicMock(return_value={})
            audit_trail.log_synthesis_error = MagicMock(return_value={})

            # Patch the global instance
            from soothe_app.src.ui.speech_audit_trail import _audit_trail
            import soothe_app.src.ui.speech_audit_trail
            soothe_app.src.ui.speech_audit_trail._audit_trail = audit_trail

        # Create the TTS handler
        from soothe_app.src.ui.tts_handler import _tts_handler
        import soothe_app.src.ui.tts_handler
        soothe_app.src.ui.tts_handler._tts_handler = None

        with patch('subprocess.Popen'):
            self.tts_handler = TTSHandler(
                elevenlabs_client=self.mock_elevenlabs)
            self.tts_handler.consent_manager.give_consent()

    def tearDown(self):
        """Clean up the test environment."""
        self.audit_trail_patcher.stop()
        self.temp_dir.cleanup()

    def test_tts_handler_with_audit_trail(self):
        """Test that TTS handler uses the audit trail correctly."""
        # Setup the mock stream method
        self.mock_elevenlabs.text_to_speech.convert_as_stream = MagicMock(return_value=[
                                                                          b'test'])

        # Run TTS
        text = "This is a test of the TTS handler."
        with patch('subprocess.Popen'):
            with patch('threading.Thread') as mock_thread:
                self.tts_handler.run_tts_with_consent_and_limiting(text)

                # Verify thread was started to run TTS
                self.assertTrue(mock_thread.called)

                # Call the thread target directly (since it's mocked)
                args, kwargs = mock_thread.call_args
                thread_target = args[0]
                thread_args = kwargs.get('args', ())

                # Run the thread target
                with patch('time.sleep'):
                    thread_target(*thread_args)

        # Verify that audit_trail.log_synthesis was called
        audit_trail = get_audit_trail()
        self.assertTrue(audit_trail.log_synthesis.called)

        # Check the arguments to log_synthesis
        args, kwargs = audit_trail.log_synthesis.call_args
        self.assertEqual(kwargs['category'], 'narrative')  # Default category
        self.assertTrue(kwargs['was_successful'])
        self.assertIn('voice_id', kwargs['metadata'])
        self.assertIn('model_id', kwargs['metadata'])

    def test_tts_error_logging(self):
        """Test that TTS errors are logged correctly."""
        # Setup the mock to raise an exception
        self.mock_elevenlabs.text_to_speech.convert_as_stream = MagicMock(
            side_effect=Exception("Test TTS error"))

        # Run TTS
        text = "This should cause an error."
        with patch('subprocess.Popen'):
            with patch('threading.Thread') as mock_thread:
                self.tts_handler.run_tts_with_consent_and_limiting(text)

                # Call the thread target directly
                args, kwargs = mock_thread.call_args
                thread_target = args[0]
                thread_args = kwargs.get('args', ())

                # Run the thread target
                with patch('time.sleep'):
                    thread_target(*thread_args)

        # Verify that audit_trail.log_synthesis_error was called
        audit_trail = get_audit_trail()
        self.assertTrue(audit_trail.log_synthesis_error.called)

        # Check the arguments to log_synthesis_error
        args, kwargs = audit_trail.log_synthesis_error.call_args
        self.assertIn('Test TTS error', kwargs['error_message'])


if __name__ == '__main__':
    unittest.main()
