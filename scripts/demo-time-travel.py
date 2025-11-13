#!/usr/bin/env python3
"""
Demo script for Repository Time-Travel Debugger

This script demonstrates the key features of the time-travel debugger
by showing example usage and expected output.
"""

import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

# Import the module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "repo_time_travel",
    os.path.join(os.path.dirname(__file__), "tools", "repo-time-travel.py")
)
repo_time_travel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repo_time_travel)

RepoTimeTraveler = repo_time_travel.RepoTimeTraveler
format_commit_summary = repo_time_travel.format_commit_summary


def demo():
    """Run a demonstration of the time-travel debugger"""
    print("🕰️  Repository Time-Travel Debugger Demo")
    print("=" * 60)
    print()
    
    # Initialize traveler
    print("1. Initializing time traveler...")
    traveler = RepoTimeTraveler(".")
    print(f"   ✓ Current position: {traveler.current_commit[:7]}")
    print()
    
    # List recent commits
    print("2. Listing recent commits:")
    commits = traveler.list_commits(0, 5)
    for i, commit in enumerate(commits):
        marker = "→" if i == 0 else " "
        print(f"   {marker} {format_commit_summary(commit)}")
    print()
    
    # Navigate back
    print("3. Navigating back 2 commits...")
    if len(commits) >= 3:
        traveler.go_back(2)
        print(f"   ✓ Now at: {traveler.current_commit[:7]}")
        print()
    
    # Search for commits
    print("4. Searching for commits with 'time-travel':")
    results = traveler.search_commits('time-travel', 'message')
    for result in results[:3]:
        print(f"   • {format_commit_summary(result)}")
    print(f"   Found {len(results)} total results")
    print()
    
    # Get file history
    print("5. Getting history for README.md:")
    history = traveler.get_file_history('README.md', max_commits=3)
    for commit in history:
        print(f"   • {format_commit_summary(commit)}")
    print()
    
    # Show commit details
    print("6. Showing details for current commit:")
    commit = traveler.get_commit_details(traveler.current_commit)
    if commit:
        print(f"   Commit: {commit['short_hash']}")
        print(f"   Author: {commit['author']}")
        print(f"   Date:   {commit['date'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Subject: {commit['subject']}")
        if commit['files_changed']:
            print(f"   Files changed: {len(commit['files_changed'])}")
    print()
    
    # Demonstrate search by author
    print("7. Searching commits by author 'Copilot':")
    results = traveler.search_commits('Copilot', 'author')
    print(f"   Found {len(results)} commits by Copilot")
    for result in results[:3]:
        print(f"   • {format_commit_summary(result)}")
    print()
    
    print("=" * 60)
    print("Demo complete! Try the interactive mode with:")
    print("  python3 tools/repo-time-travel.py")
    print()


if __name__ == '__main__':
    try:
        demo()
    except Exception as e:
        print(f"Error during demo: {e}", file=sys.stderr)
        sys.exit(1)
