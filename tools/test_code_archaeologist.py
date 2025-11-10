#!/usr/bin/env python3
"""
Test suite for Code Archaeologist

Tests the functionality of the AI code archaeologist tool.
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
    "code_archaeologist", 
    os.path.join(os.path.dirname(__file__), "code-archaeologist.py")
)
code_archaeologist_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_archaeologist_module)
CodeArchaeologist = code_archaeologist_module.CodeArchaeologist


def create_test_repo():
    """Create a temporary git repository for testing"""
    temp_dir = tempfile.mkdtemp()
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
    
    # Create some files and commits
    test_commits = [
        {
            "file": "main.py",
            "content": "# Initial version\nprint('hello')",
            "message": "Add initial implementation of main module"
        },
        {
            "file": "config.py",
            "content": "# Config\nDEBUG = True",
            "message": "Refactor: Decided to move config to separate file because it improves modularity"
        },
        {
            "file": "utils.py",
            "content": "# Utils\n# TODO: Fix this workaround\ndef helper(): pass",
            "message": "Add utility functions with temporary workaround for issue #123"
        },
        {
            "file": "main.py",
            "content": "# Updated\nprint('world')",
            "message": "Fix bug in main module causing crash"
        },
        {
            "file": "feature.py",
            "content": "# New feature\ndef new_feature(): pass",
            "message": "Implement new feature: user authentication"
        }
    ]
    
    for commit in test_commits:
        filepath = os.path.join(temp_dir, commit["file"])
        with open(filepath, 'w') as f:
            f.write(commit["content"])
        
        subprocess.run(['git', 'add', commit["file"]], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', commit["message"]], cwd=temp_dir, capture_output=True)
    
    return temp_dir


def test_initialization():
    """Test archaeologist initialization"""
    temp_dir = tempfile.mkdtemp()
    archaeology_file = os.path.join(temp_dir, "test_archaeology.json")
    
    archaeologist = CodeArchaeologist(repo_path=temp_dir, archaeology_file=archaeology_file)
    
    assert archaeologist.repo_path == temp_dir
    assert archaeologist.archaeology_file == archaeology_file
    assert archaeologist.archaeology_data["version"] == "1.0.0"
    assert archaeologist.archaeology_data["total_commits_analyzed"] == 0
    
    shutil.rmtree(temp_dir)
    print("✓ Initialization test passed")


def test_commit_parsing():
    """Test parsing commit information"""
    test_repo = create_test_repo()
    
    try:
        archaeologist = CodeArchaeologist(repo_path=test_repo)
        
        # Get latest commit hash
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H'],
            cwd=test_repo,
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        
        commit = archaeologist._parse_commit(commit_hash)
        
        assert commit is not None
        assert "hash" in commit
        assert "author" in commit
        assert "subject" in commit
        assert "files_changed" in commit
        assert commit["author"] == "Test User"
        
        print("✓ Commit parsing test passed")
    finally:
        shutil.rmtree(test_repo)


def test_commit_categorization():
    """Test categorizing commits by type"""
    test_repo = create_test_repo()
    
    try:
        archaeologist = CodeArchaeologist(repo_path=test_repo)
        
        test_cases = [
            {
                "subject": "Refactor: Decided to move config to separate file",
                "body": "",
                "expected": "architectural"
            },
            {
                "subject": "Add utility functions",
                "body": "TODO: Fix this workaround",
                "expected": "technical_debt"
            },
            {
                "subject": "Fix bug in main module",
                "body": "",
                "expected": "bug_fix"
            },
            {
                "subject": "Implement new feature",
                "body": "",
                "expected": "feature"
            }
        ]
        
        for test_case in test_cases:
            commit = {
                "subject": test_case["subject"],
                "body": test_case["body"]
            }
            category = archaeologist._categorize_commit(commit)
            assert category == test_case["expected"], \
                f"Expected {test_case['expected']}, got {category} for '{test_case['subject']}'"
        
        print("✓ Commit categorization test passed")
    finally:
        shutil.rmtree(test_repo)


def test_decision_extraction():
    """Test extracting decisions from commits"""
    test_repo = create_test_repo()
    
    try:
        archaeologist = CodeArchaeologist(repo_path=test_repo)
        
        commit = {
            "hash": "abc123def456",
            "subject": "Refactor config",
            "body": "Decided to move config to separate file because it improves modularity",
            "timestamp": "2024-01-01T00:00:00+00:00"
        }
        
        decisions = archaeologist._extract_decisions(commit)
        
        assert len(decisions) > 0
        assert any("move config" in d["content"].lower() for d in decisions)
        
        print("✓ Decision extraction test passed")
    finally:
        shutil.rmtree(test_repo)


def test_technical_debt_extraction():
    """Test extracting technical debt from commits"""
    test_repo = create_test_repo()
    
    try:
        archaeologist = CodeArchaeologist(repo_path=test_repo)
        
        commit = {
            "hash": "abc123def456",
            "subject": "Add utilities",
            "body": "TODO: Fix this workaround for the database connection",
            "timestamp": "2024-01-01T00:00:00+00:00",
            "files_changed": ["utils.py"]
        }
        
        debt = archaeologist._extract_technical_debt(commit)
        
        assert len(debt) > 0
        assert any("workaround" in d["description"].lower() for d in debt)
        assert debt[0]["type"] == "technical_debt"
        
        print("✓ Technical debt extraction test passed")
    finally:
        shutil.rmtree(test_repo)


def test_repository_analysis():
    """Test analyzing entire repository"""
    test_repo = create_test_repo()
    
    try:
        archaeologist = CodeArchaeologist(repo_path=test_repo)
        
        results = archaeologist.analyze_repository(max_commits=10)
        
        assert "commits_analyzed" in results
        assert results["commits_analyzed"] > 0
        assert "architectural_decisions" in results
        assert "technical_debt" in results
        assert "code_evolution" in results
        assert "statistics" in results
        
        # Check that we found our test commits
        assert results["statistics"]["total_commits"] == 5
        assert len(results["code_evolution"]["feature_additions"]) > 0
        assert len(results["code_evolution"]["bug_fixes"]) > 0
        
        print("✓ Repository analysis test passed")
    finally:
        shutil.rmtree(test_repo)


def test_report_generation():
    """Test generating human-readable report"""
    test_repo = create_test_repo()
    
    try:
        archaeologist = CodeArchaeologist(repo_path=test_repo)
        results = archaeologist.analyze_repository(max_commits=10)
        
        report = archaeologist.generate_report(results)
        
        assert "Code Archaeology Report" in report
        assert "Summary" in report
        assert "Statistics" in report
        assert "commits analyzed" in report.lower()
        
        print("✓ Report generation test passed")
    finally:
        shutil.rmtree(test_repo)


def test_archaeology_persistence():
    """Test saving and loading archaeology data"""
    test_repo = create_test_repo()
    temp_dir = tempfile.mkdtemp()
    archaeology_file = os.path.join(temp_dir, "test_archaeology.json")
    
    try:
        # First analysis
        archaeologist1 = CodeArchaeologist(repo_path=test_repo, archaeology_file=archaeology_file)
        results1 = archaeologist1.analyze_repository(max_commits=10)
        
        assert os.path.exists(archaeology_file)
        
        # Load existing data
        archaeologist2 = CodeArchaeologist(repo_path=test_repo, archaeology_file=archaeology_file)
        
        assert archaeologist2.archaeology_data["total_commits_analyzed"] > 0
        assert len(archaeologist2.archaeology_data["decision_timeline"]) >= 0
        
        print("✓ Archaeology persistence test passed")
    finally:
        shutil.rmtree(test_repo)
        shutil.rmtree(temp_dir)


def test_statistics():
    """Test statistics collection"""
    test_repo = create_test_repo()
    
    try:
        archaeologist = CodeArchaeologist(repo_path=test_repo)
        results = archaeologist.analyze_repository(max_commits=10)
        
        stats = results["statistics"]
        
        assert "total_commits" in stats
        assert "by_category" in stats
        assert "by_author" in stats
        assert "files_most_changed" in stats
        
        assert stats["total_commits"] == 5
        assert "Test User" in stats["by_author"]
        assert stats["by_author"]["Test User"] == 5
        
        print("✓ Statistics test passed")
    finally:
        shutil.rmtree(test_repo)


def test_empty_repository():
    """Test handling empty repository"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize empty git repo
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
        
        archaeologist = CodeArchaeologist(repo_path=temp_dir)
        results = archaeologist.analyze_repository(max_commits=10)
        
        # Should handle gracefully
        assert "error" in results or results["commits_analyzed"] == 0
        
        print("✓ Empty repository test passed")
    finally:
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all tests"""
    print("Running Code Archaeologist Tests...")
    print("=" * 50)
    
    tests = [
        test_initialization,
        test_commit_parsing,
        test_commit_categorization,
        test_decision_extraction,
        test_technical_debt_extraction,
        test_repository_analysis,
        test_report_generation,
        test_archaeology_persistence,
        test_statistics,
        test_empty_repository
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
