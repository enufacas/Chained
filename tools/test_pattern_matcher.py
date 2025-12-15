#!/usr/bin/env python3
"""
Tests for pattern-matcher.py
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the module - use direct import since we're in tools/
import importlib.util
spec = importlib.util.spec_from_file_location("pattern_matcher", 
                                               os.path.join(os.path.dirname(__file__), "pattern-matcher.py"))
pattern_matcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pattern_matcher)

PatternMatcher = pattern_matcher.PatternMatcher
PatternMatch = pattern_matcher.PatternMatch


class TestPatternMatcher(unittest.TestCase):
    """Test cases for PatternMatcher"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.matcher = PatternMatcher()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove temp files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_detect_language(self):
        """Test language detection from file extensions"""
        self.assertEqual(self.matcher.detect_language('test.py'), 'python')
        self.assertEqual(self.matcher.detect_language('test.js'), 'javascript')
        self.assertEqual(self.matcher.detect_language('test.sh'), 'bash')
        self.assertEqual(self.matcher.detect_language('test.yml'), 'yaml')
        self.assertEqual(self.matcher.detect_language('test.yaml'), 'yaml')
        self.assertIsNone(self.matcher.detect_language('test.txt'))
    
    def test_python_bare_except(self):
        """Test detection of bare except clauses in Python"""
        test_file = os.path.join(self.temp_dir, 'sample.py')
        with open(test_file, 'w') as f:
            f.write("try:\n    pass\nexcept:\n    pass\n")
        
        matches = self.matcher.scan_file(test_file)
        bare_except_matches = [m for m in matches if m.pattern_id == 'py-no-bare-except']
        self.assertGreater(len(bare_except_matches), 0)
        self.assertEqual(bare_except_matches[0].severity, 'warning')
    
    def test_python_hardcoded_secret(self):
        """Test detection of hardcoded secrets in Python"""
        test_file = os.path.join(self.temp_dir, 'config.py')
        with open(test_file, 'w') as f:
            f.write('api_key = "sk_prod_1234567890abcdefghijklmnop"\n')
        
        matches = self.matcher.scan_file(test_file)
        secret_matches = [m for m in matches if m.pattern_id == 'py-hardcoded-secrets']
        self.assertGreater(len(secret_matches), 0)
        self.assertEqual(secret_matches[0].severity, 'error')
    
    def test_javascript_console_log(self):
        """Test detection of console.log in JavaScript"""
        test_file = os.path.join(self.temp_dir, 'test.js')
        with open(test_file, 'w') as f:
            f.write('console.log("test");\n')
        
        matches = self.matcher.scan_file(test_file)
        console_matches = [m for m in matches if m.pattern_id == 'js-console-log']
        self.assertGreater(len(console_matches), 0)
        self.assertEqual(console_matches[0].severity, 'info')
    
    def test_javascript_var_keyword(self):
        """Test detection of var keyword in JavaScript"""
        test_file = os.path.join(self.temp_dir, 'test.js')
        with open(test_file, 'w') as f:
            f.write('var x = 10;\n')
        
        matches = self.matcher.scan_file(test_file)
        var_matches = [m for m in matches if m.pattern_id == 'js-var-keyword']
        self.assertGreater(len(var_matches), 0)
        self.assertEqual(var_matches[0].severity, 'warning')
    
    def test_javascript_eval(self):
        """Test detection of eval() in JavaScript"""
        test_file = os.path.join(self.temp_dir, 'test.js')
        with open(test_file, 'w') as f:
            f.write('eval("1+1");\n')
        
        matches = self.matcher.scan_file(test_file)
        eval_matches = [m for m in matches if m.pattern_id == 'js-eval-usage']
        self.assertGreater(len(eval_matches), 0)
        self.assertEqual(eval_matches[0].severity, 'error')
    
    def test_todo_comments(self):
        """Test detection of TODO comments"""
        # Python TODO
        py_file = os.path.join(self.temp_dir, 'test.py')
        with open(py_file, 'w') as f:
            f.write('# TODO: Fix this\n')
        
        matches = self.matcher.scan_file(py_file)
        todo_matches = [m for m in matches if 'todo' in m.pattern_id.lower()]
        self.assertGreater(len(todo_matches), 0)
        
        # JavaScript TODO
        js_file = os.path.join(self.temp_dir, 'test.js')
        with open(js_file, 'w') as f:
            f.write('// TODO: Fix this\n')
        
        matches = self.matcher.scan_file(js_file)
        todo_matches = [m for m in matches if 'todo' in m.pattern_id.lower()]
        self.assertGreater(len(todo_matches), 0)
    
    def test_scan_directory(self):
        """Test scanning a directory"""
        # Create test files
        py_file = os.path.join(self.temp_dir, 'test.py')
        with open(py_file, 'w') as f:
            f.write('# TODO: test\n')
        
        js_file = os.path.join(self.temp_dir, 'test.js')
        with open(js_file, 'w') as f:
            f.write('// TODO: test\n')
        
        matches = self.matcher.scan_directory(self.temp_dir, recursive=False)
        self.assertGreater(len(matches), 0)
    
    def test_statistics(self):
        """Test statistics generation"""
        test_file = os.path.join(self.temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write('try:\n    pass\nexcept:\n    pass\n')
            f.write('api_key = "sk_test_1234567890abcdefghijklmnop"\n')
        
        matches = self.matcher.scan_file(test_file)
        stats = self.matcher.get_statistics(matches)
        
        self.assertIn('total_issues', stats)
        self.assertIn('by_severity', stats)
        self.assertIn('by_category', stats)
        self.assertGreater(stats['total_issues'], 0)
    
    def test_report_generation_text(self):
        """Test text report generation"""
        test_file = os.path.join(self.temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write('# TODO: test\n')
        
        matches = self.matcher.scan_file(test_file)
        report = self.matcher.generate_report(matches, 'text')
        
        self.assertIn('Cross-Repository Pattern Matcher Report', report)
        self.assertIn('Total Issues Found', report)
    
    def test_report_generation_json(self):
        """Test JSON report generation"""
        test_file = os.path.join(self.temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write('# TODO: test\n')
        
        matches = self.matcher.scan_file(test_file)
        report = self.matcher.generate_report(matches, 'json')
        
        import json
        data = json.loads(report)
        self.assertIsInstance(data, list)
        if data:
            self.assertIn('pattern_id', data[0])
    
    def test_empty_file(self):
        """Test scanning an empty file"""
        test_file = os.path.join(self.temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write('')
        
        matches = self.matcher.scan_file(test_file)
        self.assertEqual(len(matches), 0)
    
    def test_unsupported_language(self):
        """Test scanning file with unsupported extension"""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('some text\n')
        
        matches = self.matcher.scan_file(test_file)
        self.assertEqual(len(matches), 0)

    def test_bash_quoted_variables_no_warnings(self):
        """Test that properly quoted bash variables don't trigger warnings"""
        code = '''#!/bin/bash
set -e

# These should NOT trigger warnings
echo "Processing issue #$issue_number"
result="$value"
if [ "$var" = "test" ]; then
  echo "quoted"
fi
for item in "$list"; do
  echo "item"
done
'''
        temp_file = os.path.join(self.temp_dir, 'test_quoted.sh')
        with open(temp_file, 'w') as f:
            f.write(code)
        
        matches = self.matcher.scan_file(temp_file)
        # Should have no warnings about unquoted variables
        var_warnings = [m for m in matches if 'unquoted' in m.pattern_id.lower()]
        self.assertEqual(len(var_warnings), 0, 
                        f"Found unexpected unquoted variable warnings: {[m.matched_text for m in var_warnings]}")
    
    def test_bash_unquoted_in_test(self):
        """Test detection of unquoted variables in test conditions"""
        code = '''#!/bin/bash
if [ $var = "test" ]; then
  echo "bad"
fi
'''
        temp_file = os.path.join(self.temp_dir, 'check_unquoted.sh')
        with open(temp_file, 'w') as f:
            f.write(code)
        
        matches = self.matcher.scan_file(temp_file)
        test_warnings = [m for m in matches if m.pattern_id == 'bash-unquoted-in-single-bracket-test']
        self.assertGreater(len(test_warnings), 0, "Should detect unquoted variable in test")
    
    def test_bash_shebang_first_line_only(self):
        """Test that shebang check only applies to first line"""
        code = '''#!/bin/bash
set -e
echo "line 2"
echo "line 3"
'''
        temp_file = os.path.join(self.temp_dir, 'test_shebang.sh')
        with open(temp_file, 'w') as f:
            f.write(code)
        
        matches = self.matcher.scan_file(temp_file)
        shebang_matches = [m for m in matches if m.pattern_id == 'bash-missing-shebang']
        # Should have 0 matches since shebang is present on line 1
        self.assertEqual(len(shebang_matches), 0, "Should not flag missing shebang when present")
    
    def test_bash_missing_shebang(self):
        """Test detection of missing shebang"""
        code = '''echo "no shebang"
set -e
'''
        temp_file = os.path.join(self.temp_dir, 'script_no_shebang.sh')
        with open(temp_file, 'w') as f:
            f.write(code)
        
        matches = self.matcher.scan_file(temp_file)
        shebang_matches = [m for m in matches if m.pattern_id == 'bash-missing-shebang']
        self.assertGreater(len(shebang_matches), 0, "Should detect missing shebang")
    
    def test_bash_set_e_file_level(self):
        """Test that set -e check is file-level, not per-line"""
        code = '''#!/bin/bash
set -e
echo "line 1"
echo "line 2"
echo "line 3"
'''
        temp_file = os.path.join(self.temp_dir, 'test_set_e.sh')
        with open(temp_file, 'w') as f:
            f.write(code)
        
        matches = self.matcher.scan_file(temp_file)
        set_e_matches = [m for m in matches if m.pattern_id == 'bash-no-set-e']
        # Should have 0 matches since set -e is present
        self.assertEqual(len(set_e_matches), 0, "Should not flag missing set -e when present")
    
    def test_bash_no_set_e(self):
        """Test detection of missing set -e"""
        code = '''#!/bin/bash
echo "no set -e"
'''
        temp_file = os.path.join(self.temp_dir, 'script_no_set_e.sh')
        with open(temp_file, 'w') as f:
            f.write(code)
        
        matches = self.matcher.scan_file(temp_file)
        set_e_matches = [m for m in matches if m.pattern_id == 'bash-no-set-e']
        self.assertGreater(len(set_e_matches), 0, "Should detect missing set -e")
        # Should only be reported once (file-level check)
        self.assertEqual(len(set_e_matches), 1, "Should report missing set -e only once")
    
    def test_python_type_hints_removed(self):
        """Test that type hints pattern was removed (was too noisy)"""
        code = '''def function_without_hints(arg):
    return arg
'''
        temp_file = os.path.join(self.temp_dir, 'test_hints.py')
        with open(temp_file, 'w') as f:
            f.write(code)
        
        matches = self.matcher.scan_file(temp_file)
        hint_matches = [m for m in matches if 'type-hint' in m.pattern_id.lower()]
        # Type hints pattern should be removed
        self.assertEqual(len(hint_matches), 0, "Type hints pattern should be removed")


if __name__ == '__main__':
    unittest.main()
