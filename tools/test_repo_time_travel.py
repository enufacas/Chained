#!/usr/bin/env python3
"""
Test suite for Repository Time-Travel Debugger

Tests the functionality of the repository time-travel debugger tool.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import using relative import workaround
import importlib.util
spec = importlib.util.spec_from_file_location(
    "repo_time_travel",
    os.path.join(os.path.dirname(__file__), "repo-time-travel.py")
)
repo_time_travel_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repo_time_travel_module)
RepoTimeTraveler = repo_time_travel_module.RepoTimeTraveler


def create_test_repo():
    """Create a temporary git repository for testing"""
    temp_dir = tempfile.mkdtemp()
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
    
    # Create some test commits
    test_commits = [
        {
            "file": "main.py",
            "content": "# Initial version\nprint('hello')",
            "message": "Initial commit: Add main.py"
        },
        {
            "file": "config.py",
            "content": "# Config\nDEBUG = True",
            "message": "Add configuration file"
        },
        {
            "file": "main.py",
            "content": "# Updated version\nprint('hello world')",
            "message": "Update main.py to print hello world"
        },
        {
            "file": "utils.py",
            "content": "# Utilities\ndef helper():\n    return 42",
            "message": "Add utility functions"
        },
        {
            "file": "main.py",
            "content": "# Final version\nimport utils\nprint('hello world', utils.helper())",
            "message": "Integrate utils in main"
        }
    ]
    
    for commit_info in test_commits:
        filepath = os.path.join(temp_dir, commit_info["file"])
        with open(filepath, 'w') as f:
            f.write(commit_info["content"])
        subprocess.run(['git', 'add', commit_info["file"]], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', commit_info["message"]], cwd=temp_dir, capture_output=True)
    
    return temp_dir


def test_initialization():
    """Test initialization of RepoTimeTraveler"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        assert traveler.current_commit is not None, "Current commit should be set"
        assert len(traveler.commit_history) > 0, "Commit history should be loaded"
        assert traveler.history_index == 0, "History index should start at 0"
        
        print("✓ Initialization test passed")
    finally:
        shutil.rmtree(test_repo)


def test_commit_details():
    """Test getting commit details"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Get details for HEAD
        commit = traveler.get_commit_details(traveler.current_commit)
        
        assert commit is not None, "Commit details should be returned"
        assert 'hash' in commit, "Commit should have hash"
        assert 'author' in commit, "Commit should have author"
        assert 'subject' in commit, "Commit should have subject"
        assert 'files_changed' in commit, "Commit should have files_changed"
        
        # Check that files_changed has correct structure
        if commit['files_changed']:
            file_info = commit['files_changed'][0]
            assert 'status' in file_info, "File info should have status"
            assert 'filename' in file_info, "File info should have filename"
        
        print("✓ Commit details test passed")
    finally:
        shutil.rmtree(test_repo)


def test_navigation():
    """Test navigation through history"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        initial_commit = traveler.current_commit
        initial_index = traveler.history_index
        
        # Go back one commit
        prev_commit = traveler.go_back(1)
        assert prev_commit is not None, "Should be able to go back"
        assert traveler.history_index == initial_index + 1, "Index should increase when going back"
        assert traveler.current_commit != initial_commit, "Commit should change"
        
        # Go forward one commit
        next_commit = traveler.go_forward(1)
        assert next_commit is not None, "Should be able to go forward"
        assert traveler.history_index == initial_index, "Index should return to initial"
        assert traveler.current_commit == initial_commit, "Should return to initial commit"
        
        # Try to go forward when already at HEAD (should fail)
        result = traveler.go_forward(1)
        assert result is None, "Should not be able to go forward past HEAD"
        
        print("✓ Navigation test passed")
    finally:
        shutil.rmtree(test_repo)


def test_file_at_commit():
    """Test getting file content at specific commits"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Get current main.py
        current_content = traveler.get_file_at_commit(traveler.current_commit, 'main.py')
        assert current_content is not None, "Should get file content"
        assert 'Final version' in current_content, "Should have latest content"
        
        # Go back to first commit and check main.py
        traveler.go_back(4)  # Go to first commit
        old_content = traveler.get_file_at_commit(traveler.current_commit, 'main.py')
        assert old_content is not None, "Should get old file content"
        assert 'Initial version' in old_content, "Should have initial content"
        assert 'Final version' not in old_content, "Should not have final content"
        
        print("✓ File at commit test passed")
    finally:
        shutil.rmtree(test_repo)


def test_diff():
    """Test diff between commits"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Get last two commits
        if len(traveler.commit_history) >= 2:
            commit1 = traveler.commit_history[1]['hash']
            commit2 = traveler.commit_history[0]['hash']
            
            # Get diff
            diff = traveler.diff_commits(commit1, commit2)
            assert diff is not None, "Diff should be returned"
            # Diff may be empty if no changes between commits
            
            # Get diff for specific file
            diff_file = traveler.diff_commits(commit1, commit2, 'main.py')
            # Just verify it doesn't crash
            
        print("✓ Diff test passed")
    finally:
        shutil.rmtree(test_repo)


def test_search_commits():
    """Test searching commits"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Search by message
        results = traveler.search_commits('main', 'message')
        assert len(results) > 0, "Should find commits with 'main' in message"
        
        # Search by author
        results = traveler.search_commits('Test User', 'author')
        assert len(results) > 0, "Should find commits by Test User"
        
        # Search for file
        results = traveler.search_commits('main.py', 'file')
        assert len(results) > 0, "Should find commits that changed main.py"
        
        # Search by content
        results = traveler.search_commits('hello', 'content')
        assert len(results) > 0, "Should find commits with 'hello' in content"
        
        print("✓ Search commits test passed")
    finally:
        shutil.rmtree(test_repo)


def test_file_history():
    """Test getting file history"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Get history for main.py
        history = traveler.get_file_history('main.py')
        assert len(history) > 0, "Should find history for main.py"
        
        # main.py was modified 3 times in our test repo
        assert len(history) >= 3, "Should have at least 3 commits for main.py"
        
        # Get history for non-existent file
        history = traveler.get_file_history('nonexistent.py')
        assert len(history) == 0, "Should have no history for non-existent file"
        
        print("✓ File history test passed")
    finally:
        shutil.rmtree(test_repo)


def test_list_commits():
    """Test listing commits"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # List all commits
        commits = traveler.list_commits(0, 100)
        assert len(commits) > 0, "Should have commits"
        assert len(commits) == len(traveler.commit_history), "Should return all commits"
        
        # List first 2 commits
        commits = traveler.list_commits(0, 2)
        assert len(commits) == 2, "Should return exactly 2 commits"
        
        # List commits starting from index 1
        commits = traveler.list_commits(1, 2)
        assert len(commits) <= 2, "Should return at most 2 commits"
        
        print("✓ List commits test passed")
    finally:
        shutil.rmtree(test_repo)


def test_navigate_to_commit():
    """Test navigating to a specific commit"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Get a commit from history
        if len(traveler.commit_history) >= 2:
            target_commit = traveler.commit_history[2]['hash']
            
            # Navigate to it
            success = traveler.navigate_to_commit(target_commit)
            assert success, "Should successfully navigate to commit"
            assert traveler.current_commit == target_commit, "Current commit should be updated"
            assert traveler.history_index == 2, "History index should be updated"
            
            # Try to navigate to invalid commit
            success = traveler.navigate_to_commit('invalid_hash_12345')
            assert not success, "Should fail to navigate to invalid commit"
        
        print("✓ Navigate to commit test passed")
    finally:
        shutil.rmtree(test_repo)


def test_branches_and_tags():
    """Test getting branches and tags"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Get branches for current commit
        branches = traveler.get_branches_at_commit(traveler.current_commit)
        assert isinstance(branches, list), "Should return a list of branches"
        # Should have at least the default branch
        assert len(branches) > 0, "Should have at least one branch"
        
        # Create a tag
        subprocess.run(['git', 'tag', 'v1.0.0'], cwd=test_repo, capture_output=True)
        
        # Get tags for current commit
        tags = traveler.get_tags_at_commit(traveler.current_commit)
        assert isinstance(tags, list), "Should return a list of tags"
        assert 'v1.0.0' in tags, "Should include the tag we just created"
        
        print("✓ Branches and tags test passed")
    finally:
        shutil.rmtree(test_repo)


def test_blame():
    """Test blame functionality"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Get blame for main.py
        blame_info = traveler.blame_file('main.py')
        assert len(blame_info) > 0, "Should have blame information"
        
        # Check structure of blame info
        if blame_info:
            info = blame_info[0]
            assert 'hash' in info, "Blame info should have hash"
            assert 'author' in info, "Blame info should have author"
            assert 'timestamp' in info, "Blame info should have timestamp"
            assert 'line' in info, "Blame info should have line content"
        
        print("✓ Blame test passed")
    finally:
        shutil.rmtree(test_repo)


def test_empty_operations():
    """Test operations that should handle edge cases gracefully"""
    test_repo = create_test_repo()
    
    try:
        traveler = RepoTimeTraveler(test_repo)
        
        # Try to get non-existent file
        content = traveler.get_file_at_commit(traveler.current_commit, 'nonexistent.txt')
        assert content is None or content == "", "Should return None or empty for non-existent file"
        
        # Search with no results
        results = traveler.search_commits('xyznonexistent123', 'message')
        assert len(results) == 0, "Should return empty list for no matches"
        
        # Get history for non-existent file
        history = traveler.get_file_history('nonexistent.txt')
        assert len(history) == 0, "Should return empty list for non-existent file"
        
        # Try to navigate past the beginning
        for _ in range(100):  # Try to go way back
            result = traveler.go_back(1)
            if result is None:
                break
        assert result is None, "Should eventually reach the end of history"
        
        print("✓ Empty operations test passed")
    finally:
        shutil.rmtree(test_repo)


def run_all_tests():
    """Run all tests"""
    print("Running Repository Time-Travel Debugger Tests...")
    print("=" * 60)
    
    tests = [
        test_initialization,
        test_commit_details,
        test_navigation,
        test_file_at_commit,
        test_diff,
        test_search_commits,
        test_file_history,
        test_list_commits,
        test_navigate_to_commit,
        test_branches_and_tags,
        test_blame,
        test_empty_operations
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"✗ {test.__name__} failed: {e}")
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} failed with error: {e}")
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
