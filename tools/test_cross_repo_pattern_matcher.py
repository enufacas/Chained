#!/usr/bin/env python3
"""
Tests for Cross-Repository Pattern Matcher

Tests pattern detection, scoring, and reporting functionality.
Created by @investigate-champion
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import with correct module path
if os.path.dirname(__file__):
    sys.path.insert(0, os.path.dirname(__file__))

# Import the pattern matcher module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cross_repo_pattern_matcher",
    os.path.join(os.path.dirname(__file__), "cross-repo-pattern-matcher.py")
)
cross_repo_pattern_matcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cross_repo_pattern_matcher)

Pattern = cross_repo_pattern_matcher.Pattern
PatternMatch = cross_repo_pattern_matcher.PatternMatch
CodePatternDetector = cross_repo_pattern_matcher.CodePatternDetector
WorkflowPatternDetector = cross_repo_pattern_matcher.WorkflowPatternDetector
SecurityPatternDetector = cross_repo_pattern_matcher.SecurityPatternDetector
CrossRepoPatternMatcher = cross_repo_pattern_matcher.CrossRepoPatternMatcher


def test_code_pattern_detection():
    """Test that code patterns are properly detected"""
    print("Testing code pattern detection...")
    
    detector = CodePatternDetector()
    
    # Test type hints detection
    code_with_types = '''
def process_data(data: dict[str, int]) -> bool:
    """Process the data and return success status"""
    return True
'''
    
    file_path = Path("test.py")
    matches = detector.detect(file_path, code_with_types)
    
    # Should find type hints
    type_hint_matches = [m for m in matches if m.pattern_id == 'CP001']
    assert len(type_hint_matches) > 0, "Should detect type hints"
    print("  ✅ Type hints detected correctly")
    
    # Test docstring detection
    docstring_matches = [m for m in matches if m.pattern_id == 'CP002']
    assert len(docstring_matches) > 0, "Should detect docstrings"
    print("  ✅ Docstrings detected correctly")
    
    # Test long function detection
    long_code = 'def long_func():\n' + '    pass\n' * 60
    matches = detector.detect(file_path, long_code)
    long_func_matches = [m for m in matches if m.pattern_id == 'CP004']
    assert len(long_func_matches) > 0, "Should detect long functions"
    print("  ✅ Long functions detected correctly")


def test_workflow_pattern_detection():
    """Test workflow pattern detection"""
    print("\nTesting workflow pattern detection...")
    
    detector = WorkflowPatternDetector()
    
    # Test workflow with good practices
    workflow_yaml = '''
name: Test Workflow
on:
  workflow_dispatch:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest
        env:
          API_KEY: ${{ secrets.API_KEY }}
'''
    
    file_path = Path(".github/workflows/test.yml")
    matches = detector.detect(file_path, workflow_yaml)
    
    # Should find multiple patterns
    assert len(matches) > 0, "Should detect workflow patterns"
    
    # Check for pinned version
    pinned_matches = [m for m in matches if m.pattern_id == 'WF003']
    assert len(pinned_matches) > 0, "Should detect pinned action versions"
    print("  ✅ Pinned versions detected correctly")
    
    # Check for timeout
    timeout_matches = [m for m in matches if m.pattern_id == 'WF005']
    assert len(timeout_matches) > 0, "Should detect timeout configuration"
    print("  ✅ Timeout configuration detected correctly")
    
    # Check for secrets usage
    secrets_matches = [m for m in matches if m.pattern_id == 'WF002']
    assert len(secrets_matches) > 0, "Should detect secrets usage"
    print("  ✅ Secrets management detected correctly")


def test_security_pattern_detection():
    """Test security pattern detection"""
    print("\nTesting security pattern detection...")
    
    detector = SecurityPatternDetector()
    
    # Test hardcoded secret detection
    code_with_secret = '''
API_KEY = "sk-1234567890abcdefghijklmnop"
PASSWORD = "secretpassword123"
'''
    
    file_path = Path("config.py")
    matches = detector.detect(file_path, code_with_secret)
    
    # Should find hardcoded secrets
    secret_matches = [m for m in matches if m.pattern_id == 'SEC003']
    assert len(secret_matches) > 0, "Should detect hardcoded secrets"
    print("  ✅ Hardcoded secrets detected correctly")
    
    # Test secure random detection
    secure_code = '''
import secrets

token = secrets.token_hex(16)
'''
    
    matches = detector.detect(file_path, secure_code)
    secure_matches = [m for m in matches if m.pattern_id == 'SEC004']
    assert len(secure_matches) > 0, "Should detect secure random usage"
    print("  ✅ Secure random usage detected correctly")


def test_pattern_matcher_integration():
    """Test full pattern matcher on a temporary repository"""
    print("\nTesting pattern matcher integration...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        
        # Create some test files
        (repo_path / "code.py").write_text('''
def calculate(x: int, y: int) -> int:
    """Calculate sum of two numbers"""
    try:
        return x + y
    except Exception as e:
        print(f"Error: {e}")
        return 0
''')
        
        # Create workflow directory
        workflow_dir = repo_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        (workflow_dir / "test.yml").write_text('''
name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
''')
        
        # Run matcher
        matcher = CrossRepoPatternMatcher(str(repo_path))
        analysis = matcher.analyze_repository()
        
        # Verify results
        assert analysis.repository_name == tmpdir.split('/')[-1], "Should have correct repo name"
        assert len(analysis.patterns_matched) > 0, "Should find patterns"
        assert analysis.score >= 0, "Should have valid score"
        assert analysis.score <= 100, "Score should be in valid range"
        assert len(analysis.recommendations) > 0, "Should have recommendations"
        
        print("  ✅ Pattern matcher integration working correctly")
        print(f"     Found {len(analysis.patterns_matched)} patterns")
        print(f"     Score: {analysis.score:.1f}/100")


def test_scoring_algorithm():
    """Test scoring calculation"""
    print("\nTesting scoring algorithm...")
    
    # Create a mock repository with known patterns
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        
        # Create file with only good practices
        (repo_path / "good.py").write_text('''
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration class"""
    name: str
    value: int

def process(data: dict) -> bool:
    """Process data with error handling"""
    try:
        with open("file.txt") as f:
            content = f.read()
        return True
    except Exception:
        return False
''')
        
        matcher = CrossRepoPatternMatcher(str(repo_path))
        analysis = matcher.analyze_repository()
        
        # Should have a good score
        assert analysis.score > 50, "Score should be above baseline for good practices"
        print(f"  ✅ Scoring algorithm working (score: {analysis.score:.1f})")


def test_pattern_listing():
    """Test that all patterns are properly defined"""
    print("\nTesting pattern definitions...")
    
    matcher = CrossRepoPatternMatcher()
    
    all_patterns = []
    for detector in matcher.detectors:
        patterns = detector.get_patterns()
        all_patterns.extend(patterns)
        
        # Verify each pattern has required fields
        for pattern in patterns:
            assert pattern.id, "Pattern must have ID"
            assert pattern.name, "Pattern must have name"
            assert pattern.category, "Pattern must have category"
            assert pattern.description, "Pattern must have description"
            assert pattern.severity in ['critical', 'high', 'medium', 'low', 'info'], \
                f"Pattern {pattern.id} has invalid severity: {pattern.severity}"
            assert pattern.type in ['good_practice', 'anti_pattern', 'improvement_opportunity'], \
                f"Pattern {pattern.id} has invalid type: {pattern.type}"
    
    print(f"  ✅ All {len(all_patterns)} patterns properly defined")
    
    # Check for unique IDs
    pattern_ids = [p.id for p in all_patterns]
    assert len(pattern_ids) == len(set(pattern_ids)), "Pattern IDs must be unique"
    print(f"  ✅ All pattern IDs are unique")


def test_report_export():
    """Test report export functionality"""
    print("\nTesting report export...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        
        # Create a simple test file
        (repo_path / "test.py").write_text('def test(): pass')
        
        # Run analysis
        matcher = CrossRepoPatternMatcher(str(repo_path))
        analysis = matcher.analyze_repository()
        
        # Export report
        output_path = os.path.join(tmpdir, "report.json")
        matcher.export_report(analysis, output_path)
        
        # Verify file exists and is valid JSON
        assert os.path.exists(output_path), "Report file should exist"
        
        with open(output_path, 'r') as f:
            report_data = json.load(f)
        
        # Verify structure
        assert 'repository_name' in report_data
        assert 'timestamp' in report_data
        assert 'patterns_matched' in report_data
        assert 'summary' in report_data
        assert 'recommendations' in report_data
        assert 'score' in report_data
        
        print("  ✅ Report export working correctly")


def test_confidence_calculation():
    """Test that confidence scores are reasonable"""
    print("\nTesting confidence calculation...")
    
    detector = CodePatternDetector()
    
    code = '''
def example(x: int) -> str:
    """Example function with type hints"""
    return str(x)
'''
    
    matches = detector.detect(Path("test.py"), code)
    
    for match in matches:
        assert 0.0 <= match.confidence <= 1.0, \
            f"Confidence must be between 0 and 1, got {match.confidence}"
        # Most code patterns should have high confidence
        assert match.confidence >= 0.7, \
            f"Code pattern confidence should be >= 0.7, got {match.confidence}"
    
    print("  ✅ Confidence scores are reasonable")


def test_category_grouping():
    """Test that patterns are properly categorized"""
    print("\nTesting category grouping...")
    
    matcher = CrossRepoPatternMatcher()
    
    categories = set()
    for detector in matcher.detectors:
        for pattern in detector.get_patterns():
            categories.add(pattern.category)
    
    expected_categories = {'code', 'workflow', 'security'}
    assert categories == expected_categories, \
        f"Expected categories {expected_categories}, got {categories}"
    
    print(f"  ✅ All patterns properly categorized into {len(categories)} categories")


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("🧪 RUNNING PATTERN MATCHER TESTS")
    print("=" * 80)
    
    tests = [
        test_code_pattern_detection,
        test_workflow_pattern_detection,
        test_security_pattern_detection,
        test_pattern_matcher_integration,
        test_scoring_algorithm,
        test_pattern_listing,
        test_report_export,
        test_confidence_calculation,
        test_category_grouping,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
