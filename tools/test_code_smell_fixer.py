#!/usr/bin/env python3
"""
Comprehensive Tests for Code Smell Fixer
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
import importlib.util

# Load the fixer module
spec = importlib.util.spec_from_file_location(
    "code_smell_fixer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "code-smell-fixer.py")
)
code_smell_fixer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_smell_fixer)

CodeSmellFixer = code_smell_fixer.CodeSmellFixer


def test_initialization():
    """Test that CodeSmellFixer initializes correctly"""
    fixer = CodeSmellFixer()
    assert not fixer.dry_run
    assert not fixer.interactive
    assert fixer.backup
    assert fixer.analyzer is not None
    print("✓ Initialization test passed")


def test_unused_imports_detection_and_fix():
    """Test detection and removal of unused imports"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''import os
import sys
import json
import tempfile

def main():
    print(os.path.exists("."))
    return sys.exit(0)
''')
        
        fixer = CodeSmellFixer(dry_run=False, backup=False)
        result = fixer.fix_unused_imports(test_file)
        
        assert result["success"]
        assert result["changes"] == 2  # json and tempfile are unused
        assert "json" in result["unused_imports"]
        assert "tempfile" in result["unused_imports"]
        
        # Verify the file was modified
        with open(test_file, 'r') as f:
            content = f.read()
            assert "import json" not in content
            assert "import tempfile" not in content
            assert "import os" in content
            assert "import sys" in content
        
        print("✓ Unused imports detection and fix test passed")


def test_unused_imports_dry_run():
    """Test that dry-run mode doesn't modify files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        original_content = '''import os
import json

def main():
    print(os.path.exists("."))
'''
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        fixer = CodeSmellFixer(dry_run=True)
        result = fixer.fix_unused_imports(test_file)
        
        # Verify the file was NOT modified
        with open(test_file, 'r') as f:
            content = f.read()
            assert content == original_content
        
        print("✓ Unused imports dry-run test passed")


def test_magic_numbers_detection_and_fix():
    """Test detection and extraction of magic numbers"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''def calculate():
    x = 42
    y = 42
    return x + y + 123
''')
        
        fixer = CodeSmellFixer(dry_run=False, backup=False)
        result = fixer.fix_magic_numbers(test_file)
        
        assert result["success"]
        assert result["changes"] > 0
        
        # Verify constants were added
        with open(test_file, 'r') as f:
            content = f.read()
            assert "CONSTANT_" in content
            assert "# Constants extracted" in content
        
        print("✓ Magic numbers detection and fix test passed")


def test_missing_docstrings_fix():
    """Test adding skeleton docstrings"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''def function_without_docstring():
    return 42

class ClassWithoutDocstring:
    def method(self):
        return 1
''')
        
        fixer = CodeSmellFixer(dry_run=False, backup=False)
        result = fixer.fix_missing_docstrings(test_file)
        
        assert result["success"]
        assert result["changes"] >= 2  # At least function and class
        assert "function_without_docstring" in result["docstrings_added"]
        assert "ClassWithoutDocstring" in result["docstrings_added"]
        
        # Verify docstrings were added
        with open(test_file, 'r') as f:
            content = f.read()
            assert '"""TODO: Add function docstring."""' in content
            assert '"""TODO: Add class docstring."""' in content
        
        print("✓ Missing docstrings fix test passed")


def test_poor_variable_names_detection():
    """Test detection of poor variable names"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''def process():
    a = 1
    temp = 2
    data = 3
    return a + temp + data
''')
        
        fixer = CodeSmellFixer()
        result = fixer.fix_poor_variable_names(test_file)
        
        assert result["success"]
        assert len(result["poor_names_detected"]) > 0
        
        # Check that we detected poor names
        poor_names = [name for name, _, _ in result["poor_names_detected"]]
        assert any(name in ['a', 'temp', 'data'] for name in poor_names)
        
        print("✓ Poor variable names detection test passed")


def test_missing_type_hints_detection():
    """Test detection of missing type hints"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''def add(a, b):
    return a + b

def multiply(x: int, y: int) -> int:
    return x * y
''')
        
        fixer = CodeSmellFixer()
        result = fixer.fix_missing_type_hints(test_file)
        
        assert result["success"]
        assert "add" in result["functions_without_hints"]
        assert "multiply" not in result["functions_without_hints"]
        
        print("✓ Missing type hints detection test passed")


def test_long_functions_detection():
    """Test detection of long functions"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        # Create a function with more than 50 lines
        lines = ["def long_function():"]
        lines.append('    """A very long function"""')
        for i in range(60):
            lines.append(f"    x{i} = {i}")
        lines.append("    return x0")
        
        with open(test_file, 'w') as f:
            f.write('\n'.join(lines))
        
        fixer = CodeSmellFixer()
        result = fixer.detect_long_functions(test_file)
        
        assert result["success"]
        assert len(result["long_functions"]) > 0
        assert result["long_functions"][0][0] == "long_function"
        assert result["long_functions"][0][2] > 50  # More than 50 lines
        
        print("✓ Long functions detection test passed")


def test_deep_nesting_detection():
    """Test detection of deep nesting"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''def deeply_nested():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        print("Too deep!")
''')
        
        fixer = CodeSmellFixer()
        result = fixer.detect_deep_nesting(test_file)
        
        assert result["success"]
        assert len(result["deep_nesting_functions"]) > 0
        assert result["deep_nesting_functions"][0][0] == "deeply_nested"
        assert result["deep_nesting_functions"][0][2] > 4  # Depth > 4
        
        print("✓ Deep nesting detection test passed")


def test_backup_creation():
    """Test that backups are created before modifications"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        original_content = '''import os
import json

def main():
    print(os.path.exists("."))
'''
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        fixer = CodeSmellFixer(dry_run=False, backup=True)
        result = fixer.fix_unused_imports(test_file)
        
        # Verify backup was created
        assert result.get("backup") is not None
        assert os.path.exists(result["backup"])
        
        # Verify backup contains original content
        with open(result["backup"], 'r') as f:
            backup_content = f.read()
            assert backup_content == original_content
        
        print("✓ Backup creation test passed")


def test_no_backup_mode():
    """Test that no backups are created when backup=False"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''import os
import json

def main():
    print(os.path.exists("."))
''')
        
        fixer = CodeSmellFixer(dry_run=False, backup=False)
        result = fixer.fix_unused_imports(test_file)
        
        # Verify no backup was created
        assert result.get("backup") is None
        backup_dir = os.path.join(tmpdir, '.smell_fixer_backups')
        assert not os.path.exists(backup_dir)
        
        print("✓ No backup mode test passed")


def test_fix_file_comprehensive():
    """Test fixing a single file with multiple issues"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''import os
import sys
import json

def process():
    x = 42
    y = 42
    return x + y
''')
        
        fixer = CodeSmellFixer(dry_run=False, backup=False)
        result = fixer.fix_file(test_file)
        
        assert "file" in result
        assert "fixes" in result
        assert "unused_imports" in result["fixes"]
        assert "magic_numbers" in result["fixes"]
        assert "missing_docstrings" in result["fixes"]
        
        print("✓ Comprehensive file fix test passed")


def test_fix_directory():
    """Test fixing multiple files in a directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple test files
        for i in range(3):
            test_file = os.path.join(tmpdir, f"test{i}.py")
            with open(test_file, 'w') as f:
                f.write(f'''import os
import json

def function{i}():
    return {i}
''')
        
        fixer = CodeSmellFixer(dry_run=False, backup=False)
        result = fixer.fix_directory(tmpdir)
        
        assert "directory" in result
        assert "files" in result
        assert result["summary"]["total_files"] == 3
        assert len(result["files"]) == 3
        
        print("✓ Directory fix test passed")


def test_report_generation():
    """Test report generation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''import os
import json

def main():
    print(os.path.exists("."))
''')
        
        fixer = CodeSmellFixer(dry_run=False, backup=False)
        result = fixer.fix_file(test_file)
        report = fixer.generate_report(result)
        
        assert "Code Smell Fixer Report" in report
        assert "Generated:" in report
        assert "File:" in report
        
        print("✓ Report generation test passed")


def test_syntax_error_handling():
    """Test handling of files with syntax errors"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''def broken(
    # Missing closing parenthesis and body
''')
        
        fixer = CodeSmellFixer()
        result = fixer.fix_unused_imports(test_file)
        
        assert not result["success"]
        assert "error" in result
        assert "Syntax error" in result["error"]
        
        print("✓ Syntax error handling test passed")


def test_file_not_found_handling():
    """Test handling of non-existent files"""
    fixer = CodeSmellFixer()
    result = fixer.fix_file("/nonexistent/file.py")
    
    assert "error" in result
    assert "not found" in result["error"].lower()
    
    print("✓ File not found handling test passed")


def test_non_python_file_handling():
    """Test handling of non-Python files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("This is not a Python file")
        
        fixer = CodeSmellFixer()
        result = fixer.fix_file(test_file)
        
        assert "error" in result
        assert "Python files" in result["error"]
        
        print("✓ Non-Python file handling test passed")


def test_directory_exclusions():
    """Test that certain directories are excluded from processing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files in excluded directories
        for excluded_dir in ['.git', '__pycache__', 'node_modules', 'venv']:
            dir_path = os.path.join(tmpdir, excluded_dir)
            os.makedirs(dir_path, exist_ok=True)
            test_file = os.path.join(dir_path, "test.py")
            with open(test_file, 'w') as f:
                f.write("import os\n")
        
        # Create a valid file in the main directory
        main_file = os.path.join(tmpdir, "main.py")
        with open(main_file, 'w') as f:
            f.write("import os\n")
        
        fixer = CodeSmellFixer(dry_run=True)
        result = fixer.fix_directory(tmpdir)
        
        # Should only process the main file
        assert result["summary"]["total_files"] == 1
        
        print("✓ Directory exclusions test passed")


def test_preserves_working_code():
    """Test that fixer doesn't break working code"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        working_code = '''def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y

if __name__ == "__main__":
    result = add(2, 3)
    print(f"Result: {result}")
'''
        with open(test_file, 'w') as f:
            f.write(working_code)
        
        fixer = CodeSmellFixer(dry_run=False, backup=False)
        result = fixer.fix_file(test_file)
        
        # Code should still be valid Python
        with open(test_file, 'r') as f:
            new_content = f.read()
        
        import ast
        try:
            ast.parse(new_content)
            print("✓ Preserves working code test passed")
        except SyntaxError:
            raise AssertionError("Fixer broke valid Python code")


def test_edge_case_empty_file():
    """Test handling of empty files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "empty.py")
        with open(test_file, 'w') as f:
            f.write("")
        
        fixer = CodeSmellFixer()
        result = fixer.fix_file(test_file)
        
        # Should handle empty file gracefully
        assert "file" in result
        assert "fixes" in result
        
        print("✓ Edge case empty file test passed")


def test_edge_case_only_comments():
    """Test handling of files with only comments"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "comments.py")
        with open(test_file, 'w') as f:
            f.write("# This is a comment\n# Another comment\n")
        
        fixer = CodeSmellFixer()
        result = fixer.fix_file(test_file)
        
        # Should handle comments-only file gracefully
        assert "file" in result
        assert "fixes" in result
        
        print("✓ Edge case only comments test passed")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_initialization,
        test_unused_imports_detection_and_fix,
        test_unused_imports_dry_run,
        test_magic_numbers_detection_and_fix,
        test_missing_docstrings_fix,
        test_poor_variable_names_detection,
        test_missing_type_hints_detection,
        test_long_functions_detection,
        test_deep_nesting_detection,
        test_backup_creation,
        test_no_backup_mode,
        test_fix_file_comprehensive,
        test_fix_directory,
        test_report_generation,
        test_syntax_error_handling,
        test_file_not_found_handling,
        test_non_python_file_handling,
        test_directory_exclusions,
        test_preserves_working_code,
        test_edge_case_empty_file,
        test_edge_case_only_comments,
    ]
    
    print("Running Code Smell Fixer Tests...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
