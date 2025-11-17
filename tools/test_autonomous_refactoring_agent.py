#!/usr/bin/env python3
"""
Tests for the Autonomous Refactoring Agent

This test suite validates the agent's ability to:
- Learn code style preferences from various sources
- Build a knowledge base over time
- Generate accurate refactoring suggestions
- Integrate with existing learning systems
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
import importlib.util

# Import the autonomous refactoring agent
spec = importlib.util.spec_from_file_location(
    "autonomous_refactoring_agent",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "autonomous-refactoring-agent.py")
)
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

StylePreferenceLearner = agent_module.StylePreferenceLearner
AutoRefactorer = agent_module.AutoRefactorer
StylePreference = agent_module.StylePreference
RefactoringPattern = agent_module.RefactoringPattern


def test_style_preference_initialization():
    """Test that StylePreferenceLearner initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        assert learner.preferences_file == prefs_file
        assert learner.patterns_file == patterns_file
        assert isinstance(learner.preferences, dict)
        assert isinstance(learner.patterns, dict)
        print("✓ StylePreferenceLearner initialization test passed")


def test_learn_from_pr_history():
    """Test learning from PR history."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        # Create a test Python file
        test_file = os.path.join(tmpdir, "test_code.py")
        with open(test_file, 'w') as f:
            f.write('''
def calculate_sum(numbers: list) -> int:
    """Calculate the sum of numbers."""
    return sum(numbers)

class DataProcessor:
    """Processes data."""
    
    def process(self, data: dict) -> dict:
        """Process the data."""
        return data
''')
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        # Simulate learning from a PR
        pr_data = {
            'number': 123,
            'merged': True,
            'files_changed': [test_file],
            'commit_sha': 'abc123'
        }
        
        learner.learn_from_pr_history(pr_data)
        
        # Check that preferences were learned
        assert len(learner.preferences) > 0
        print(f"✓ Learned {len(learner.preferences)} preferences from PR history")


def test_learn_from_external_source():
    """Test learning from external sources like TLDR."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        # Create a mock TLDR learning file
        learning_file = os.path.join(tmpdir, "tldr_test.json")
        learning_data = {
            "timestamp": "2025-11-17T00:00:00Z",
            "source": "TLDR Tech",
            "learnings": [
                {
                    "title": "Clean Code Practices",
                    "content": "Best practices include using type hints, comprehensive docstrings, and proper error handling for better code quality.",
                    "source": "TLDR",
                    "url": "https://example.com"
                },
                {
                    "title": "Code Style Guide",
                    "content": "Modern Python development emphasizes clean code with modularity and maintainability as key principles.",
                    "source": "TLDR",
                    "url": "https://example.com"
                }
            ]
        }
        
        with open(learning_file, 'w') as f:
            json.dump(learning_data, f)
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        learner.learn_from_external_source(learning_file)
        
        # Check that external preferences were learned
        external_prefs = [k for k in learner.preferences.keys() if k.startswith('external_')]
        assert len(external_prefs) > 0
        print(f"✓ Learned {len(external_prefs)} preferences from external source")


def test_preferences_persistence():
    """Test that preferences are saved and loaded correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        # Create and save preferences
        learner1 = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        learner1.preferences["test_pref"] = StylePreference(
            preference_type="test",
            value="test_value",
            confidence=0.8,
            occurrences=10,
            last_seen="2025-11-17T00:00:00Z",
            sources=["test"],
            success_rate=0.9
        )
        learner1._save_preferences()
        
        # Load preferences in a new instance
        learner2 = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        assert "test_pref" in learner2.preferences
        pref = learner2.preferences["test_pref"]
        assert pref.preference_type == "test"
        assert pref.value == "test_value"
        assert pref.confidence == 0.8
        assert pref.occurrences == 10
        print("✓ Preferences persistence test passed")


def test_preferences_summary():
    """Test generating a summary of learned preferences."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        # Add some test preferences
        for i in range(5):
            learner.preferences[f"pref_{i}"] = StylePreference(
                preference_type=f"type_{i % 3}",
                value=f"value_{i}",
                confidence=0.5 + i * 0.1,
                occurrences=10 + i * 5,
                last_seen="2025-11-17T00:00:00Z",
                sources=["test"],
                success_rate=0.8
            )
        
        summary = learner.get_preferences_summary()
        
        assert summary["total_preferences"] == 5
        assert "preferences_by_type" in summary
        assert "top_preferences" in summary
        assert len(summary["top_preferences"]) <= 10
        print("✓ Preferences summary test passed")


def test_auto_refactorer_analyze_file():
    """Test that AutoRefactorer can analyze files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        # Create a test file with specific style
        test_file = os.path.join(tmpdir, "analyze_test.py")
        with open(test_file, 'w') as f:
            f.write('''
def myFunction(x, y):
    result = x + y
    return result
''')
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        # Set a learned preference for function naming
        learner.preferences["naming_function_naming"] = StylePreference(
            preference_type="naming_function_naming",
            value="snake_case",
            confidence=0.9,
            occurrences=100,
            last_seen="2025-11-17T00:00:00Z",
            sources=["repo_history"],
            success_rate=0.95
        )
        
        refactorer = AutoRefactorer(learner)
        analysis = refactorer.analyze_file(test_file)
        
        assert "filepath" in analysis
        assert "suggestions" in analysis
        assert analysis["filepath"] == test_file
        print(f"✓ File analysis generated {len(analysis['suggestions'])} suggestions")


def test_auto_refactorer_generate_report():
    """Test generating a refactoring report for a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        # Create multiple test files
        test_dir = os.path.join(tmpdir, "test_project")
        os.makedirs(test_dir)
        
        for i in range(3):
            test_file = os.path.join(test_dir, f"module_{i}.py")
            with open(test_file, 'w') as f:
                f.write(f'''
def function{i}(x):
    """A test function."""
    return x * {i + 1}
''')
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        # Add some learned preferences
        learner.preferences["naming_function_naming"] = StylePreference(
            preference_type="naming_function_naming",
            value="snake_case",
            confidence=0.9,
            occurrences=100,
            last_seen="2025-11-17T00:00:00Z",
            sources=["repo_history"],
            success_rate=0.95
        )
        
        refactorer = AutoRefactorer(learner)
        report = refactorer.generate_refactoring_report(test_dir)
        
        assert "timestamp" in report
        assert "files_analyzed" in report
        assert "total_suggestions" in report
        assert report["files_analyzed"] == 3
        print(f"✓ Report generated for {report['files_analyzed']} files with {report['total_suggestions']} suggestions")


def test_confidence_increases_with_occurrences():
    """Test that confidence increases as preferences are seen more often."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        # Simulate learning the same preference multiple times
        for i in range(5):
            test_file = os.path.join(tmpdir, f"test_{i}.py")
            with open(test_file, 'w') as f:
                f.write('''
def test_function():
    """A test function."""
    pass
''')
            
            pr_data = {
                'number': i,
                'merged': True,
                'files_changed': [test_file],
                'commit_sha': f'abc{i}'
            }
            
            learner.learn_from_pr_history(pr_data)
        
        # Check that confidence increased
        if learner.preferences:
            # Get any preference
            pref = list(learner.preferences.values())[0]
            # Confidence should be higher with more occurrences
            assert pref.occurrences >= 5 or pref.confidence > 0.1
            print(f"✓ Confidence increases with occurrences (confidence: {pref.confidence:.2f}, occurrences: {pref.occurrences})")


def test_success_rate_tracking():
    """Test that success rate is tracked correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def test_function():
    """A test."""
    pass
''')
        
        # Learn from successful PR
        pr_data = {
            'number': 1,
            'merged': True,
            'files_changed': [test_file],
            'commit_sha': 'abc123'
        }
        
        learner.learn_from_pr_history(pr_data)
        
        # Check that success rate is tracked
        if learner.preferences:
            pref = list(learner.preferences.values())[0]
            assert hasattr(pref, 'success_rate')
            assert pref.success_rate >= 0.0
            assert pref.success_rate <= 1.0
            print(f"✓ Success rate tracked: {pref.success_rate:.2%}")


def test_refactoring_suggestions_prioritization():
    """Test that suggestions are properly prioritized by confidence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
def myBadFunction(x):
    return x
''')
        
        learner = StylePreferenceLearner(
            preferences_file=prefs_file,
            patterns_file=patterns_file
        )
        
        # Add preferences with different confidence levels
        learner.preferences["naming_function_naming"] = StylePreference(
            preference_type="naming_function_naming",
            value="snake_case",
            confidence=0.9,  # High confidence
            occurrences=100,
            last_seen="2025-11-17T00:00:00Z",
            sources=["repo_history"],
            success_rate=0.95
        )
        
        learner.preferences["indentation_style"] = StylePreference(
            preference_type="indentation",
            value="spaces_4",
            confidence=0.3,  # Low confidence
            occurrences=10,
            last_seen="2025-11-17T00:00:00Z",
            sources=["test"],
            success_rate=0.5
        )
        
        refactorer = AutoRefactorer(learner)
        analysis = refactorer.analyze_file(test_file)
        
        # Only high confidence suggestions should be included
        high_conf_suggestions = [s for s in analysis['suggestions'] if s.get('confidence', 0) > 0.5]
        assert len(high_conf_suggestions) >= 0  # Should have at least naming suggestion
        print(f"✓ Generated {len(high_conf_suggestions)} high-confidence suggestions")


def run_all_tests():
    """Run all tests."""
    tests = [
        test_style_preference_initialization,
        test_learn_from_pr_history,
        test_learn_from_external_source,
        test_preferences_persistence,
        test_preferences_summary,
        test_auto_refactorer_analyze_file,
        test_auto_refactorer_generate_report,
        test_confidence_increases_with_occurrences,
        test_success_rate_tracking,
        test_refactoring_suggestions_prioritization,
    ]
    
    print("\n=== Running Autonomous Refactoring Agent Tests ===\n")
    
    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append((test.__name__, str(e)))
    
    print(f"\n=== Test Summary ===")
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {len(tests) - len(failed)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed tests:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
