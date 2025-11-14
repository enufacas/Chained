#!/usr/bin/env python3
"""
Extended test suite for Enhanced Archaeology Learner

Tests the new predictive and knowledge base features.
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


def test_risk_assessment():
    """Test risk assessment functionality"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        # Test low risk change
        low_risk_chars = {
            "is_refactor": True,
            "has_tests": True,
            "large_change": False,
            "has_documentation": True
        }
        
        risk = learner.assess_risk(low_risk_chars)
        
        assert "risk_level" in risk
        assert "risk_score" in risk
        assert "risk_factors" in risk
        assert "success_probability" in risk
        assert "recommendation" in risk
        assert risk["risk_level"] in ["low", "medium", "high"]
        
        # Test high risk change
        high_risk_chars = {
            "is_feature": True,
            "has_tests": False,
            "large_change": True,
            "has_documentation": False
        }
        
        high_risk = learner.assess_risk(high_risk_chars)
        assert high_risk["risk_score"] >= risk["risk_score"]
        
        print(f"✓ Risk assessment test passed (low risk: {risk['risk_level']}, high risk: {high_risk['risk_level']})")
    finally:
        shutil.rmtree(test_repo)


def test_timeline_estimation():
    """Test timeline estimation functionality"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        # Test different change types
        for change_type in ['feature', 'refactor', 'bugfix']:
            timeline = learner.estimate_timeline(change_type, files_count=3)
            
            assert "estimated_days" in timeline
            assert "confidence" in timeline
            assert "reasoning" in timeline
            assert "range" in timeline
            assert timeline["confidence"] in ["low", "medium", "high"]
        
        print("✓ Timeline estimation test passed")
    finally:
        shutil.rmtree(test_repo)


def test_find_similar_changes():
    """Test finding similar historical changes"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        characteristics = {
            "is_refactor": True,
            "has_tests": True,
            "large_change": False
        }
        
        similar = learner.find_similar_changes(characteristics, max_results=5)
        
        assert isinstance(similar, list)
        
        for change in similar:
            assert "commit_hash" in change
            assert "subject" in change
            assert "outcome" in change
            assert "similarity" in change
            assert "characteristics" in change
            assert "lessons_learned" in change
            assert change["outcome"] in ["success", "failure"]
            assert 0 <= change["similarity"] <= 1
        
        print(f"✓ Find similar changes test passed (found {len(similar)} similar changes)")
    finally:
        shutil.rmtree(test_repo)


def test_knowledge_base_building():
    """Test knowledge base construction"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        kb = learner.patterns_data.get("knowledge_base", {})
        
        assert "best_practices" in kb
        assert "common_pitfalls" in kb
        assert "success_examples" in kb
        assert "failure_examples" in kb
        
        assert isinstance(kb["best_practices"], list)
        assert isinstance(kb["common_pitfalls"], list)
        assert isinstance(kb["success_examples"], list)
        assert isinstance(kb["failure_examples"], list)
        
        # Check structure of best practices
        if kb["best_practices"]:
            practice = kb["best_practices"][0]
            assert "practice" in practice
            assert "evidence_count" in practice
        
        # Check structure of pitfalls
        if kb["common_pitfalls"]:
            pitfall = kb["common_pitfalls"][0]
            assert "pitfall" in pitfall
            assert "occurrences" in pitfall
        
        print(f"✓ Knowledge base building test passed (practices: {len(kb['best_practices'])}, pitfalls: {len(kb['common_pitfalls'])})")
    finally:
        shutil.rmtree(test_repo)


def test_knowledge_base_search():
    """Test searching the knowledge base"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        # Search for test-related information
        results = learner.search_knowledge_base("test")
        
        assert isinstance(results, list)
        
        for result in results:
            assert "type" in result
            assert "content" in result
        
        # Search with specific category
        practice_results = learner.search_knowledge_base("test", category="best_practices")
        assert isinstance(practice_results, list)
        
        print(f"✓ Knowledge base search test passed (found {len(results)} results)")
    finally:
        shutil.rmtree(test_repo)


def test_timeline_data_extraction():
    """Test extraction of timeline data from patterns"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        timeline_data = learner.patterns_data.get("timeline_data", {})
        
        assert "feature_completion_times" in timeline_data
        assert "refactor_completion_times" in timeline_data
        assert "bugfix_completion_times" in timeline_data
        
        assert isinstance(timeline_data["feature_completion_times"], list)
        assert isinstance(timeline_data["refactor_completion_times"], list)
        assert isinstance(timeline_data["bugfix_completion_times"], list)
        
        print(f"✓ Timeline data extraction test passed")
    finally:
        shutil.rmtree(test_repo)


def test_enhanced_statistics():
    """Test enhanced statistics tracking"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        stats = learner.patterns_data.get("statistics", {})
        
        assert "total_patterns" in stats
        assert "prediction_accuracy" in stats
        assert "recommendations_generated" in stats
        assert "predictions_made" in stats
        assert "predictions_validated" in stats
        
        assert isinstance(stats["total_patterns"], int)
        assert isinstance(stats["prediction_accuracy"], float)
        assert stats["prediction_accuracy"] >= 0.0
        
        print("✓ Enhanced statistics test passed")
    finally:
        shutil.rmtree(test_repo)


def test_enhanced_report_generation():
    """Test enhanced report generation with new sections"""
    test_repo = create_test_repo_with_patterns()
    
    try:
        learner = ArchaeologyLearner(repo_path=test_repo)
        learner.analyze_and_learn(max_commits=20)
        
        report = learner.generate_report()
        
        # Check for new sections in report (case insensitive)
        report_lower = report.lower()
        assert "knowledge base" in report_lower
        assert "best practices" in report_lower or "knowledge base entries:" in report_lower
        assert "predictive capabilities" in report_lower
        assert "usage examples" in report_lower
        assert "assess_risk" in report
        assert "estimate_timeline" in report
        assert "find_similar_changes" in report
        
        print("✓ Enhanced report generation test passed")
    finally:
        shutil.rmtree(test_repo)


def test_integration_with_existing_data():
    """Test that enhanced features work with existing archaeology data"""
    test_repo = create_test_repo_with_patterns()
    temp_dir = tempfile.mkdtemp()
    patterns_file = os.path.join(temp_dir, "patterns.json")
    
    try:
        # First run to create data
        learner1 = ArchaeologyLearner(repo_path=test_repo, patterns_file=patterns_file)
        learner1.analyze_and_learn(max_commits=20)
        
        # Load existing data and test features
        learner2 = ArchaeologyLearner(repo_path=test_repo, patterns_file=patterns_file)
        
        # Test that we can use predictive features with loaded data
        risk = learner2.assess_risk({"is_feature": True, "has_tests": True, "large_change": False})
        assert "risk_level" in risk
        
        timeline = learner2.estimate_timeline("feature", 3)
        assert "estimated_days" in timeline
        
        search_results = learner2.search_knowledge_base("test")
        assert isinstance(search_results, list)
        
        print("✓ Integration with existing data test passed")
    finally:
        shutil.rmtree(test_repo)
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all enhanced tests"""
    print("Running Enhanced Archaeology Learner Tests...")
    print("=" * 50)
    
    tests = [
        test_risk_assessment,
        test_timeline_estimation,
        test_find_similar_changes,
        test_knowledge_base_building,
        test_knowledge_base_search,
        test_timeline_data_extraction,
        test_enhanced_statistics,
        test_enhanced_report_generation,
        test_integration_with_existing_data,
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
