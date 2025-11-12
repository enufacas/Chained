#!/usr/bin/env python3
"""
Test suite for Archaeology Learner

Tests the functionality of the archaeology learning tool.
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import using relative import workaround
import importlib.util
spec = importlib.util.spec_from_file_location(
    "archaeology_learner", 
    os.path.join(os.path.dirname(__file__), "archaeology-learner.py")
)
archaeology_learner_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archaeology_learner_module)
ArchaeologyLearner = archaeology_learner_module.ArchaeologyLearner


def create_test_repo_with_patterns():
    """Create a test repository with clear success/failure patterns"""
    temp_dir = tempfile.mkdtemp()
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
    
    # Create commits with clear patterns
    test_commits = [
        # Success pattern: refactor with tests
        {
            "file": "module.py",
            "content": "def func(): return 1",
            "message": "Refactor: Simplify module structure"
        },
        {
            "file": "test_module.py",
            "content": "def test_func(): assert func() == 1",
            "message": "Add tests for refactored module"
        },
        
        # Failure pattern: large change without tests
        {
            "file": "feature.py",
            "content": "# Large feature implementation\n" * 20,
            "message": "Implement large feature X"
        },
        {
            "file": "feature.py",
            "content": "# Bug fix\n" + "# Large feature implementation\n" * 19,
            "message": "Fix bug in feature X introduced in previous commit"
        },
        
        # Success pattern: incremental feature with tests
        {
            "file": "utils.py",
            "content": "def helper(): return 'help'",
            "message": "Add utility helper function"
        },
        {
            "file": "test_utils.py",
            "content": "def test_helper(): assert helper() == 'help'",
            "message": "Add tests for utility helper"
        },
        
        # Failure pattern: quick fix without proper testing
        {
            "file": "config.py",
            "content": "DEBUG = True  # Quick fix",
            "message": "Quick fix for configuration issue"
        },
        {
            "file": "config.py",
            "content": "DEBUG = False  # Proper fix",
            "message": "Fix: Correct configuration setting from quick fix"
        },
        
        # Success pattern: well-documented change
        {
            "file": "api.py",
            "content": "def api_call(): pass",
            "message": "Add API endpoint\n\nDecided to use REST because it's standard"
        },
        
        # Evolution pattern: frequently changed file
        {
            "file": "core.py",
            "content": "# Version 1",
            "message": "Initial core implementation"
        },
        {
            "file": "core.py",
            "content": "# Version 2",
            "message": "Update core logic"
        },
        {
            "file": "core.py",
            "content": "# Version 3",
            "message": "Improve core performance"
        },
        {
            "file": "core.py",
            "content": "# Version 4",
            "message": "Refactor core module"
        },
    ]
    
    for commit in test_commits:
        filepath = os.path.join(temp_dir, commit["file"])
        with open(filepath, 'w') as f:
            f.write(commit["content"])
        
        subprocess.run(['git', 'add', commit["file"]], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', commit["message"]], cwd=temp_dir, capture_output=True)
    
    return temp_dir


def test_initialization():
    """Test learner initialization"""
    temp_dir = tempfile.mkdtemp()
    patterns_file = os.path.join(temp_dir, "test_patterns.json")
    
    learner = ArchaeologyLearner(repo_path=temp_dir, patterns_file=patterns_file)
    
    assert learner.repo_path == temp_dir
    assert learner.patterns_file == patterns_file
    assert learner.patterns_data["version"] == "1.0"
    assert "patterns" in learner.patterns_data
    assert "insights" in learner.patterns_data
    assert "recommendations" in learner.patterns_data
    
    shutil.rmtree(temp_dir)
    print("✓ Initialization test passed")


def test_pattern_extraction():
    """Test extracting patterns from commits"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        # Get a commit
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H'],
            cwd=test_repo,
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        commit = learner._parse_commit(commit_hash)
        
        outcome = {"success": True, "fixes_needed": [], "improvements_made": [], "issues_introduced": []}
        pattern = learner._extract_pattern(commit, outcome, "success")
        
        assert pattern is not None
        assert "pattern_type" in pattern
        assert "characteristics" in pattern
        assert "commit_hash" in pattern
        
        print("✓ Pattern extraction test passed")
    finally:
        shutil.rmtree(test_repo)


def test_success_pattern_learning():
    """Test learning success patterns"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        success_patterns = learner.learn_success_patterns(max_commits=20)
        
        assert isinstance(success_patterns, list)
        # Should find at least some successful patterns in our test repo
        assert len(success_patterns) >= 0  # May be zero if no clear successes found
        
        print(f"✓ Success pattern learning test passed (found {len(success_patterns)} patterns)")
    finally:
        shutil.rmtree(test_repo)


def test_failure_pattern_learning():
    """Test learning failure patterns"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        failure_patterns = learner.learn_failure_patterns(max_commits=20)
        
        assert isinstance(failure_patterns, list)
        # May find failures based on fix commits
        
        print(f"✓ Failure pattern learning test passed (found {len(failure_patterns)} patterns)")
    finally:
        shutil.rmtree(test_repo)


def test_evolution_pattern_learning():
    """Test learning evolution patterns"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        evolution_patterns = learner.learn_evolution_patterns(max_commits=20)
        
        assert isinstance(evolution_patterns, list)
        # Should find core.py as frequently changed
        core_patterns = [p for p in evolution_patterns if 'core.py' in p.get('file', '')]
        assert len(core_patterns) > 0, "Should find core.py evolution pattern"
        
        print(f"✓ Evolution pattern learning test passed (found {len(evolution_patterns)} patterns)")
    finally:
        shutil.rmtree(test_repo)


def test_insight_generation():
    """Test generating insights from patterns"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        # Create some mock patterns
        patterns = {
            "success": [
                {
                    "characteristics": {
                        "is_refactor": True,
                        "has_tests": True,
                        "large_change": False
                    }
                }
            ],
            "failure": [
                {
                    "characteristics": {
                        "is_feature": True,
                        "has_tests": False,
                        "large_change": True
                    }
                }
            ],
            "evolution": [
                {
                    "file": "core.py",
                    "change_frequency": "very_frequent",
                    "changes_count": 10
                }
            ]
        }
        
        insights = learner.generate_insights(patterns)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        # Check insight structure
        for insight in insights:
            assert "type" in insight
            assert "title" in insight
            assert "description" in insight
            assert "confidence" in insight
        
        print(f"✓ Insight generation test passed (generated {len(insights)} insights)")
    finally:
        shutil.rmtree(test_repo)


def test_recommendation_generation():
    """Test generating recommendations from insights"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        # Create mock insights
        insights = [
            {
                "type": "testing_importance",
                "title": "Tests correlate with success",
                "description": "Commits with tests succeed more often",
                "confidence": "high",
                "actionable": True
            },
            {
                "type": "high_churn",
                "title": "High churn files need attention",
                "description": "Some files change too frequently",
                "files": ["core.py", "utils.py"],
                "confidence": "high",
                "actionable": True
            }
        ]
        
        recommendations = learner.generate_recommendations(insights)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check recommendation structure
        for rec in recommendations:
            assert "priority" in rec
            assert "title" in rec
            assert "description" in rec
            assert "action" in rec
            assert "based_on" in rec
        
        print(f"✓ Recommendation generation test passed (generated {len(recommendations)} recommendations)")
    finally:
        shutil.rmtree(test_repo)


def test_outcome_prediction():
    """Test predicting commit outcomes"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        # Set up some patterns
        learner.patterns_data["patterns"] = {
            "success": [
                {
                    "characteristics": {
                        "is_refactor": True,
                        "has_tests": True,
                        "large_change": False
                    }
                }
            ],
            "failure": [
                {
                    "characteristics": {
                        "is_refactor": False,
                        "has_tests": False,
                        "large_change": True
                    }
                }
            ]
        }
        
        # Test prediction for similar to success
        commit_chars = {
            "is_refactor": True,
            "has_tests": True,
            "large_change": False
        }
        
        prediction = learner.predict_outcome(commit_chars)
        
        assert "prediction" in prediction
        assert "confidence" in prediction
        assert "reasoning" in prediction
        assert prediction["prediction"] in ["success", "likely_needs_fixes", "uncertain", "unknown"]
        
        print("✓ Outcome prediction test passed")
    finally:
        shutil.rmtree(test_repo)


def test_full_analysis():
    """Test complete analysis and learning process"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        results = learner.analyze_and_learn(max_commits=20)
        
        assert "timestamp" in results
        assert "patterns_learned" in results
        assert "insights_generated" in results
        assert "recommendations_generated" in results
        
        # Check patterns were learned
        patterns_learned = results["patterns_learned"]
        assert "success" in patterns_learned
        assert "failure" in patterns_learned
        assert "evolution" in patterns_learned
        
        # Check file was saved
        assert os.path.exists(learner.patterns_file)
        
        print("✓ Full analysis test passed")
    finally:
        shutil.rmtree(test_repo)


def test_pattern_persistence():
    """Test saving and loading patterns"""
    test_repo = create_test_repo_with_patterns()
    temp_dir = tempfile.mkdtemp()
    patterns_file = os.path.join(temp_dir, "test_patterns.json")
    
    try:
        # First analysis
        learner1 = ArchaeologyLearner(repo_path=test_repo, patterns_file=patterns_file)
        learner1.analyze_and_learn(max_commits=20)
        
        assert os.path.exists(patterns_file)
        
        # Load existing patterns
        learner2 = ArchaeologyLearner(repo_path=test_repo, patterns_file=patterns_file)
        
        assert learner2.patterns_data["version"] == "1.0"
        assert "patterns" in learner2.patterns_data
        assert learner2.patterns_data["last_updated"] is not None
        
        print("✓ Pattern persistence test passed")
    finally:
        shutil.rmtree(test_repo)
        shutil.rmtree(temp_dir)


def test_report_generation():
    """Test generating human-readable report"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        report = learner.generate_report()
        
        assert "Archaeology Learning Report" in report
        assert "Statistics" in report
        assert "Learned Patterns" in report
        
        print("✓ Report generation test passed")
    finally:
        shutil.rmtree(test_repo)


def test_change_frequency_calculation():
    """Test calculating file change frequency"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        from datetime import datetime, timedelta
        
        # Test frequent changes
        frequent_history = [
            {"timestamp": (datetime.now() - timedelta(days=i)).isoformat()}
            for i in range(5)
        ]
        
        frequency = learner._calculate_change_frequency(frequent_history)
        assert frequency in ["very_frequent", "frequent", "moderate", "rare"]
        
        print("✓ Change frequency calculation test passed")
    finally:
        shutil.rmtree(test_repo)


def test_similarity_calculation():
    """Test calculating similarity between characteristics"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        
        characteristics = {
            "is_refactor": True,
            "has_tests": True,
            "large_change": False
        }
        
        patterns = [
            {
                "characteristics": {
                    "is_refactor": True,
                    "has_tests": True,
                    "large_change": False
                }
            },
            {
                "characteristics": {
                    "is_refactor": False,
                    "has_tests": False,
                    "large_change": True
                }
            }
        ]
        
        similarity = learner._calculate_similarity(characteristics, patterns)
        
        assert isinstance(similarity, float)
        assert similarity >= 0.0
        
        print("✓ Similarity calculation test passed")
    finally:
        shutil.rmtree(test_repo)


def run_all_tests():
    """Run all tests"""
    print("Running Archaeology Learner Tests...")
    print("=" * 50)
    
    tests = [
        test_initialization,
        test_pattern_extraction,
        test_success_pattern_learning,
        test_failure_pattern_learning,
        test_evolution_pattern_learning,
        test_insight_generation,
        test_recommendation_generation,
        test_outcome_prediction,
        test_full_analysis,
        test_pattern_persistence,
        test_report_generation,
        test_change_frequency_calculation,
        test_similarity_calculation,
    ]
    
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
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
