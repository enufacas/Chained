#!/usr/bin/env python3
"""
Tests for Enhanced Refactoring Features
Part of the Chained autonomous AI ecosystem

Author: @create-guru
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import using importlib
import importlib.util
spec = importlib.util.spec_from_file_location(
    "enhanced_refactoring_features",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "enhanced-refactoring-features.py")
)
enhanced_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enhanced_module)

TeamStyleLearner = enhanced_module.TeamStyleLearner
StyleConflictResolver = enhanced_module.StyleConflictResolver
AdvancedPatternRecognizer = enhanced_module.AdvancedPatternRecognizer
TeamMember = enhanced_module.TeamMember
StyleConflict = enhanced_module.StyleConflict


def test_team_style_learner_initialization():
    """Test TeamStyleLearner initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        team_file = os.path.join(tmpdir, "team_data.json")
        learner = TeamStyleLearner(team_file)
        
        assert len(learner.team_members) == 0
        print("✓ TeamStyleLearner initialization test passed")


def test_team_member_learning():
    """Test learning from team member reviews."""
    with tempfile.TemporaryDirectory() as tmpdir:
        team_file = os.path.join(tmpdir, "team_data.json")
        learner = TeamStyleLearner(team_file)
        
        # Learn from reviews
        learner.learn_from_review("alice", "naming_convention", "snake_case", approved=True)
        learner.learn_from_review("alice", "naming_convention", "snake_case", approved=True)
        learner.learn_from_review("bob", "naming_convention", "snake_case", approved=True)
        
        assert "alice" in learner.team_members
        assert "bob" in learner.team_members
        assert learner.team_members["alice"].review_count == 2
        assert learner.team_members["bob"].review_count == 1
        
        print("✓ Team member learning test passed")


def test_team_consensus():
    """Test team consensus calculation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        team_file = os.path.join(tmpdir, "team_data.json")
        learner = TeamStyleLearner(team_file)
        
        # Create consensus
        learner.learn_from_review("alice", "naming", "snake_case", approved=True)
        learner.learn_from_review("bob", "naming", "snake_case", approved=True)
        learner.learn_from_review("charlie", "naming", "snake_case", approved=True)
        learner.learn_from_review("dave", "naming", "camelCase", approved=False)
        
        consensus = learner.get_team_consensus("naming")
        
        assert consensus is not None
        value, confidence = consensus
        assert value == "snake_case"
        assert confidence > 0.5
        
        print(f"✓ Team consensus test passed (consensus: {value}, confidence: {confidence:.2f})")


def test_style_champions():
    """Test identifying style champions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        team_file = os.path.join(tmpdir, "team_data.json")
        learner = TeamStyleLearner(team_file)
        
        # Create different levels of expertise
        for i in range(10):
            learner.learn_from_review("alice", "naming", "snake_case", approved=True)
        for i in range(5):
            learner.learn_from_review("bob", "naming", "snake_case", approved=True)
        for i in range(2):
            learner.learn_from_review("charlie", "naming", "snake_case", approved=True)
        
        champions = learner.identify_style_champions(2)
        
        assert len(champions) <= 2
        assert champions[0][0] == "alice"  # Alice should be top champion
        
        print(f"✓ Style champions test passed (top champion: {champions[0][0]})")


def test_conflict_detection():
    """Test style conflict detection."""
    from collections import namedtuple
    
    Pref = namedtuple('Pref', ['preference_type', 'value', 'confidence', 'sources'])
    
    with tempfile.TemporaryDirectory() as tmpdir:
        team_file = os.path.join(tmpdir, "team_data.json")
        team_learner = TeamStyleLearner(team_file)
        resolver = StyleConflictResolver(team_learner)
        
        # Create conflicting preferences
        prefs = {
            'pref1': Pref('naming', 'snake_case', 0.9, ['alice', 'bob']),
            'pref2': Pref('naming', 'camelCase', 0.7, ['charlie']),
            'pref3': Pref('indent', 'spaces_4', 0.95, ['alice']),
        }
        
        conflicts = resolver.detect_conflicts(prefs)
        
        assert len(conflicts) >= 1  # Should detect naming conflict
        assert any(c.preference_type == 'naming' for c in conflicts)
        
        print(f"✓ Conflict detection test passed ({len(conflicts)} conflicts detected)")


def test_conflict_resolution():
    """Test conflict resolution strategies."""
    from collections import namedtuple
    
    Pref = namedtuple('Pref', ['preference_type', 'value', 'confidence', 'sources'])
    
    with tempfile.TemporaryDirectory() as tmpdir:
        team_file = os.path.join(tmpdir, "team_data.json")
        team_learner = TeamStyleLearner(team_file)
        
        # Build team preferences
        team_learner.learn_from_review("alice", "naming", "snake_case", approved=True)
        team_learner.learn_from_review("bob", "naming", "snake_case", approved=True)
        team_learner.learn_from_review("charlie", "naming", "camelCase", approved=False)
        
        resolver = StyleConflictResolver(team_learner)
        
        # Create conflicting preferences
        prefs = {
            'pref1': Pref('naming', 'snake_case', 0.9, ['alice', 'bob']),
            'pref2': Pref('naming', 'camelCase', 0.6, ['charlie']),
        }
        
        result = resolver.resolve_all_conflicts(prefs)
        
        assert result['conflicts_detected'] >= 1
        assert result['conflicts_resolved'] >= 1
        assert len(result['conflict_details']) >= 1
        
        print(f"✓ Conflict resolution test passed ({result['conflicts_resolved']} resolved)")


def test_advanced_pattern_recognition():
    """Test advanced pattern extraction."""
    recognizer = AdvancedPatternRecognizer()
    
    sample_code = '''
def example_function(x: int, y: int) -> int:
    """Example function with type hints."""
    return x + y

class ExampleClass:
    """Example class."""
    pass
'''
    
    features = recognizer.extract_advanced_features(sample_code, "tools/example.py")
    
    assert "complexity_indicators" in features
    assert "style_fingerprint" in features
    assert features["complexity_indicators"]["function_count"] >= 1
    assert features["complexity_indicators"]["class_count"] >= 1
    assert features["style_fingerprint"]["uses_type_hints"] == True
    assert features["style_fingerprint"]["uses_docstrings"] == True
    
    print("✓ Advanced pattern recognition test passed")


def test_style_similarity():
    """Test style similarity calculation."""
    recognizer = AdvancedPatternRecognizer()
    
    code1 = '''
def func1(x: int) -> int:
    """Docstring."""
    return x * 2
'''
    
    code2 = '''
def func2(y: int) -> int:
    """Another docstring."""
    return y * 3
'''
    
    code3 = '''
def func3(z):
    return z * 4
'''
    
    features1 = recognizer.extract_advanced_features(code1, "file1.py")
    features2 = recognizer.extract_advanced_features(code2, "file2.py")
    features3 = recognizer.extract_advanced_features(code3, "file3.py")
    
    similarity_12 = recognizer.calculate_style_similarity(features1, features2)
    similarity_13 = recognizer.calculate_style_similarity(features1, features3)
    
    # Similar styles should have higher similarity
    assert similarity_12 > similarity_13
    
    print(f"✓ Style similarity test passed (sim12: {similarity_12:.2f}, sim13: {similarity_13:.2f})")


def test_anomaly_detection():
    """Test style anomaly detection."""
    recognizer = AdvancedPatternRecognizer()
    
    # Historical code with type hints and docstrings
    historical = []
    for i in range(5):
        code = f'''
def func{i}(x: int) -> int:
    """Docstring."""
    return x * {i+1}
'''
        historical.append(recognizer.extract_advanced_features(code, f"file{i}.py"))
    
    # Current code without type hints or docstrings
    current_code = '''
def bad_func(x):
    return x * 2
'''
    current_features = recognizer.extract_advanced_features(current_code, "current.py")
    
    anomalies = recognizer.detect_style_anomalies(current_features, historical)
    
    assert len(anomalies) > 0
    assert any("type hints" in a.lower() for a in anomalies)
    
    print(f"✓ Anomaly detection test passed ({len(anomalies)} anomalies detected)")


def test_refactoring_success_prediction():
    """Test refactoring success prediction."""
    recognizer = AdvancedPatternRecognizer()
    
    # Historical outcomes
    outcomes = [
        ("naming_convention", True),
        ("naming_convention", True),
        ("naming_convention", True),
        ("naming_convention", False),
        ("type_hints", True),
        ("type_hints", False),
    ]
    
    # Predict success for naming convention (3/4 = 75% success)
    success_prob = recognizer.predict_refactoring_success("naming_convention", outcomes)
    
    assert 0.0 <= success_prob <= 1.0
    assert success_prob > 0.5  # Should predict success based on history
    
    print(f"✓ Success prediction test passed (predicted: {success_prob:.1%})")


def test_pattern_history_recording():
    """Test pattern history recording."""
    recognizer = AdvancedPatternRecognizer()
    
    sample_code = '''
def test_func(x: int) -> int:
    return x * 2
'''
    
    features = recognizer.extract_advanced_features(sample_code, "test.py")
    
    # Record patterns
    recognizer.record_pattern(features, outcome=True)
    recognizer.record_pattern(features, outcome=False)
    recognizer.record_pattern(features, outcome=True)
    
    assert len(recognizer.pattern_history) == 3
    assert recognizer.pattern_history[0]["outcome"] == True
    assert recognizer.pattern_history[1]["outcome"] == False
    
    print(f"✓ Pattern history recording test passed ({len(recognizer.pattern_history)} patterns)")


def test_persistence():
    """Test data persistence across sessions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        team_file = os.path.join(tmpdir, "team_data.json")
        
        # Create first learner and add data
        learner1 = TeamStyleLearner(team_file)
        learner1.learn_from_review("alice", "naming", "snake_case", approved=True)
        learner1.learn_from_review("bob", "indent", "spaces_4", approved=True)
        
        # Create second learner and verify data persists
        learner2 = TeamStyleLearner(team_file)
        
        assert "alice" in learner2.team_members
        assert "bob" in learner2.team_members
        assert learner2.team_members["alice"].review_count == 1
        
        print("✓ Persistence test passed")


def run_all_tests():
    """Run all test functions."""
    print("\n" + "="*70)
    print("Running Enhanced Refactoring Features Tests")
    print("@create-guru")
    print("="*70 + "\n")
    
    tests = [
        test_team_style_learner_initialization,
        test_team_member_learning,
        test_team_consensus,
        test_style_champions,
        test_conflict_detection,
        test_conflict_resolution,
        test_advanced_pattern_recognition,
        test_style_similarity,
        test_anomaly_detection,
        test_refactoring_success_prediction,
        test_pattern_history_recording,
        test_persistence,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"Test Summary: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
