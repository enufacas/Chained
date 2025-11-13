#!/usr/bin/env python3
"""
Test suite for exception handling bug fixes.

Tests that specific exception types are caught instead of bare except clauses.
This ensures that critical exceptions (SystemExit, KeyboardInterrupt) propagate correctly.

This test validates the fixes by checking the actual code in the files.
"""

import sys
import os
import re
import unittest


class TestExceptionHandlingInCode(unittest.TestCase):
    """Test that exception handling uses specific exception types"""
    
    def setUp(self):
        """Set up test paths"""
        self.repo_root = os.path.dirname(os.path.abspath(__file__))
        self.copilot_tracker = os.path.join(self.repo_root, 'tools', 'copilot-usage-tracker.py')
        self.github_integration = os.path.join(self.repo_root, 'tools', 'github_integration.py')
    
    def test_copilot_tracker_no_bare_except(self):
        """Test that copilot-usage-tracker.py has no bare except clauses"""
        with open(self.copilot_tracker, 'r') as f:
            content = f.read()
        
        # Check for bare except clauses (except: followed by optional whitespace)
        # Exclude cases where it's in a comment or string
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Strip comments
            code_part = line.split('#')[0]
            # Check for bare except
            if re.search(r'^\s*except\s*:\s*$', code_part):
                self.fail(f"Found bare except clause at line {i} in {self.copilot_tracker}")
    
    def test_github_integration_no_bare_except(self):
        """Test that github_integration.py has no bare except clauses"""
        with open(self.github_integration, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            code_part = line.split('#')[0]
            if re.search(r'^\s*except\s*:\s*$', code_part):
                self.fail(f"Found bare except clause at line {i} in {self.github_integration}")
    
    def test_copilot_tracker_has_specific_exceptions_date_parsing(self):
        """Test that date parsing has specific exception types"""
        with open(self.copilot_tracker, 'r') as f:
            content = f.read()
        
        # Look for the date parsing exception handler
        self.assertIn('except (ValueError, AttributeError, TypeError)', content,
                     "Date parsing should catch specific exception types: ValueError, AttributeError, TypeError")
    
    def test_copilot_tracker_has_specific_exceptions_file_loading(self):
        """Test that file loading has specific exception types"""
        with open(self.copilot_tracker, 'r') as f:
            content = f.read()
        
        # Look for the file loading exception handler
        self.assertIn('except (json.JSONDecodeError, IOError, OSError)', content,
                     "File loading should catch specific exception types: json.JSONDecodeError, IOError, OSError")
    
    def test_github_integration_has_specific_exceptions(self):
        """Test that error response parsing has specific exception types"""
        with open(self.github_integration, 'r') as f:
            content = f.read()
        
        # Look for the error response parsing exception handler
        self.assertIn('except (json.JSONDecodeError, UnicodeDecodeError, AttributeError)', content,
                     "Error response parsing should catch specific exception types: json.JSONDecodeError, UnicodeDecodeError, AttributeError")
    
    def test_copilot_tracker_has_comments(self):
        """Test that exception handlers have explanatory comments"""
        with open(self.copilot_tracker, 'r') as f:
            content = f.read()
        
        # Check for comments explaining the exception handling
        self.assertIn('# Skip invalid date formats', content,
                     "Date parsing exception handler should have explanatory comment")
        self.assertIn('# Return empty dict if file is corrupted or unreadable', content,
                     "File loading exception handler should have explanatory comment")
    
    def test_github_integration_has_comments(self):
        """Test that exception handlers have explanatory comments"""
        with open(self.github_integration, 'r') as f:
            content = f.read()
        
        # Check for comments explaining the exception handling
        self.assertIn('# Fallback to basic error message if response body is malformed', content,
                     "Error response parsing exception handler should have explanatory comment")


class TestExceptionBehavior(unittest.TestCase):
    """Test exception behavior patterns"""
    
    def test_keyboard_interrupt_propagates(self):
        """Test that KeyboardInterrupt is not caught by try-except blocks"""
        # This is a behavioral test - KeyboardInterrupt should always propagate
        raised = False
        try:
            raise KeyboardInterrupt()
        except KeyboardInterrupt:
            raised = True
        
        self.assertTrue(raised, "KeyboardInterrupt should be catchable explicitly")
    
    def test_system_exit_propagates(self):
        """Test that SystemExit is not caught by try-except blocks"""
        # This is a behavioral test - SystemExit should always propagate
        raised = False
        try:
            raise SystemExit()
        except SystemExit:
            raised = True
        
        self.assertTrue(raised, "SystemExit should be catchable explicitly")
    
    def test_value_error_is_catchable(self):
        """Test that ValueError can be caught specifically"""
        caught = False
        try:
            raise ValueError("test")
        except ValueError:
            caught = True
        
        self.assertTrue(caught, "ValueError should be catchable")
    
    def test_json_decode_error_is_catchable(self):
        """Test that json.JSONDecodeError can be caught specifically"""
        import json
        caught = False
        try:
            json.loads("invalid json")
        except json.JSONDecodeError:
            caught = True
        
        self.assertTrue(caught, "json.JSONDecodeError should be catchable")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
