#!/usr/bin/env python3
"""
Tests for ask_gemini tool.

Tests authentication mode detection, error handling, and basic functionality.
Uses mocking to avoid actual API calls during testing.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from ask_gemini import get_auth_mode, ask_gemini


class TestAuthMode(unittest.TestCase):
    """Test authentication mode detection."""
    
    def setUp(self):
        """Save original environment variables."""
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Restore original environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_no_auth_configured(self):
        """Test error when no authentication is configured."""
        # Clear all auth-related env vars
        for key in ['GEMINI_API_KEY', 'GOOGLE_API_KEY', 'USE_VERTEX_AI', 
                    'GOOGLE_CLOUD_PROJECT', 'GCP_PROJECT_ID']:
            os.environ.pop(key, None)
        
        mode, error = get_auth_mode()
        
        self.assertIsNone(mode)
        self.assertIn("No Gemini authentication configured", error)
    
    def test_genai_mode_with_gemini_key(self):
        """Test Google AI Studio mode with GEMINI_API_KEY."""
        os.environ['GEMINI_API_KEY'] = 'test-key'
        
        with patch('ask_gemini.GENAI_AVAILABLE', True):
            mode, error = get_auth_mode()
            
            self.assertEqual(mode, 'genai')
            self.assertIsNone(error)
    
    def test_genai_mode_with_google_key(self):
        """Test Google AI Studio mode with GOOGLE_API_KEY."""
        os.environ['GOOGLE_API_KEY'] = 'test-key'
        
        with patch('ask_gemini.GENAI_AVAILABLE', True):
            mode, error = get_auth_mode()
            
            self.assertEqual(mode, 'genai')
            self.assertIsNone(error)
    
    def test_vertex_mode_explicit(self):
        """Test Vertex AI mode when USE_VERTEX_AI is true."""
        os.environ['USE_VERTEX_AI'] = 'true'
        os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
        
        with patch('ask_gemini.VERTEX_AVAILABLE', True):
            mode, error = get_auth_mode()
            
            self.assertEqual(mode, 'vertex')
            self.assertIsNone(error)
    
    def test_vertex_mode_missing_project(self):
        """Test error when Vertex AI requested but project missing."""
        os.environ['USE_VERTEX_AI'] = 'true'
        os.environ.pop('GOOGLE_CLOUD_PROJECT', None)
        os.environ.pop('GCP_PROJECT_ID', None)
        
        with patch('ask_gemini.VERTEX_AVAILABLE', True):
            mode, error = get_auth_mode()
            
            self.assertIsNone(mode)
            self.assertIn("GOOGLE_CLOUD_PROJECT", error)
    
    def test_genai_not_installed(self):
        """Test error when google-generativeai not installed."""
        os.environ['GEMINI_API_KEY'] = 'test-key'
        
        with patch('ask_gemini.GENAI_AVAILABLE', False):
            mode, error = get_auth_mode()
            
            self.assertIsNone(mode)
            self.assertIn("google-generativeai", error)


class TestAskGemini(unittest.TestCase):
    """Test ask_gemini function."""
    
    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ['GEMINI_API_KEY'] = 'test-key'
    
    def tearDown(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch('ask_gemini.GENAI_AVAILABLE', True)
    @patch('ask_gemini.genai')
    def test_basic_query(self, mock_genai):
        """Test basic query to Gemini."""
        # Mock the Gemini API response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is Gemini's response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        response = ask_gemini("What is Python?")
        
        self.assertEqual(response, "This is Gemini's response")
        mock_genai.configure.assert_called_once_with(api_key='test-key')
        mock_model.generate_content.assert_called_once()
    
    @patch('ask_gemini.GENAI_AVAILABLE', True)
    @patch('ask_gemini.genai')
    def test_query_with_context(self, mock_genai):
        """Test query with additional context."""
        # Mock the Gemini API response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Response with context"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        response = ask_gemini(
            question="How to optimize?",
            context="Python code with O(n^2) complexity"
        )
        
        self.assertEqual(response, "Response with context")
        
        # Verify context was included in prompt
        call_args = mock_model.generate_content.call_args[0][0]
        self.assertIn("Python code with O(n^2) complexity", call_args)
    
    def test_no_auth_error(self):
        """Test error when no authentication configured."""
        # Clear auth
        os.environ.pop('GEMINI_API_KEY', None)
        
        with self.assertRaises(RuntimeError) as ctx:
            ask_gemini("Test question")
        
        self.assertIn("No Gemini authentication configured", str(ctx.exception))
    
    @patch('ask_gemini.GENAI_AVAILABLE', True)
    @patch('ask_gemini.genai')
    def test_api_error_handling(self, mock_genai):
        """Test handling of API errors."""
        # Mock API error
        mock_genai.GenerativeModel.side_effect = Exception("API Error")
        
        with self.assertRaises(RuntimeError) as ctx:
            ask_gemini("Test question")
        
        self.assertIn("Error consulting Gemini", str(ctx.exception))


class TestCLI(unittest.TestCase):
    """Test command-line interface."""
    
    @patch('ask_gemini.ask_gemini')
    @patch('sys.argv', ['ask_gemini.py', 'Test question'])
    def test_cli_basic(self, mock_ask):
        """Test basic CLI usage."""
        mock_ask.return_value = "Test response"
        
        from ask_gemini import main
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_called_once_with(0)
    
    @patch('ask_gemini.ask_gemini')
    @patch('sys.argv', ['ask_gemini.py', 'Question', '--context', 'Context info'])
    def test_cli_with_context(self, mock_ask):
        """Test CLI with context argument."""
        mock_ask.return_value = "Test response"
        
        from ask_gemini import main
        
        with patch('sys.exit') as mock_exit:
            main()
            
            # Verify context was passed
            mock_ask.assert_called_once()
            call_kwargs = mock_ask.call_args[1]
            self.assertEqual(call_kwargs['context'], 'Context info')
    
    @patch('ask_gemini.ask_gemini')
    @patch('sys.argv', ['ask_gemini.py', 'Question', '--model', 'gemini-1.5-flash'])
    def test_cli_custom_model(self, mock_ask):
        """Test CLI with custom model."""
        mock_ask.return_value = "Test response"
        
        from ask_gemini import main
        
        with patch('sys.exit') as mock_exit:
            main()
            
            # Verify model was passed
            call_kwargs = mock_ask.call_args[1]
            self.assertEqual(call_kwargs['model'], 'gemini-1.5-flash')


if __name__ == '__main__':
    unittest.main()
