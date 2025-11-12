#!/usr/bin/env python3
"""
Repository Time-Travel Debugger for Chained

This tool provides an interactive interface to navigate and debug git history,
allowing developers to view code state at any point in time, compare versions,
and understand how code evolved.
"""

import os
import sys
import subprocess
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class RepoTimeTraveler:
    """Navigate and debug git repository history"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.current_commit = None
        self.commit_history = []
        self.history_index = 0
        self._initialize()
    
    def _initialize(self):
        """Initialize the time traveler"""
        # Get current branch HEAD
        result = self._run_git_command(['rev-parse', 'HEAD'])
        if result:
            self.current_commit = result
            self._load_commit_history()
    
    def _run_git_command(self, args: List[str]) -> str:
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if e.stderr:
                print(f"Error: {e.stderr.strip()}", file=sys.stderr)
            return ""
    
    def _load_commit_history(self, max_commits: int = 1000):
        """Load commit history"""
        log_output = self._run_git_command([
            'log', '--format=%H|%an|%ae|%at|%s', f'-{max_commits}'
        ])
        
        if not log_output:
            return
        
        self.commit_history = []
        for line in log_output.split('\n'):
            if not line:
                continue
            parts = line.split('|', 4)
            if len(parts) == 5:
                commit_hash, author, email, timestamp, subject = parts
                self.commit_history.append({
                    'hash': commit_hash,
                    'short_hash': commit_hash[:7],
                    'author': author,
                    'email': email,
                    'timestamp': int(timestamp),
                    'date': datetime.fromtimestamp(int(timestamp), tz=timezone.utc),
                    'subject': subject
                })
    
    def get_commit_details(self, commit_hash: str) -> Optional[Dict]:
        """Get detailed information about a commit"""
        output = self._run_git_command([
            'show', '--format=%H|%an|%ae|%at|%s|%b', '--no-patch', commit_hash
        ])
        
        if not output:
            return None
        
        lines = output.split('\n')
        parts = lines[0].split('|', 5)
        
        if len(parts) < 5:
            return None
        
        commit_hash, author, email, timestamp, subject = parts[:5]
        body = parts[5] if len(parts) > 5 else ""
        
        # Get files changed
        files_output = self._run_git_command([
            'show', '--name-status', '--format=', commit_hash
        ])
        
        files_changed = []
        if files_output:
            for line in files_output.split('\n'):
                if line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        status, filename = parts
                        files_changed.append({
                            'status': status,
                            'filename': filename
                        })
        
        # Get diff stats
        stats_output = self._run_git_command([
            'show', '--stat', '--format=', commit_hash
        ])
        
        return {
            'hash': commit_hash,
            'short_hash': commit_hash[:7],
            'author': author,
            'email': email,
            'timestamp': int(timestamp),
            'date': datetime.fromtimestamp(int(timestamp), tz=timezone.utc),
            'subject': subject,
            'body': body,
            'files_changed': files_changed,
            'stats': stats_output
        }
    
    def get_file_at_commit(self, commit_hash: str, filepath: str) -> Optional[str]:
        """Get file content at a specific commit"""
        output = self._run_git_command(['show', f'{commit_hash}:{filepath}'])
        return output if output else None
    
    def diff_commits(self, commit1: str, commit2: str, filepath: Optional[str] = None) -> str:
        """Get diff between two commits"""
        args = ['diff', commit1, commit2]
        if filepath:
            args.append('--')
            args.append(filepath)
        
        return self._run_git_command(args)
    
    def search_commits(self, query: str, search_type: str = 'message') -> List[Dict]:
        """Search commits by various criteria"""
        results = []
        
        if search_type == 'message':
            # Search in commit messages
            output = self._run_git_command([
                'log', '--format=%H|%an|%at|%s', '--grep', query, '-i'
            ])
        elif search_type == 'author':
            # Search by author
            output = self._run_git_command([
                'log', '--format=%H|%an|%at|%s', '--author', query
            ])
        elif search_type == 'file':
            # Search commits that changed a file
            output = self._run_git_command([
                'log', '--format=%H|%an|%at|%s', '--', query
            ])
        elif search_type == 'content':
            # Search in code content
            output = self._run_git_command([
                'log', '--format=%H|%an|%at|%s', '-S', query
            ])
        else:
            return results
        
        if output:
            for line in output.split('\n'):
                if not line:
                    continue
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commit_hash, author, timestamp, subject = parts
                    results.append({
                        'hash': commit_hash,
                        'short_hash': commit_hash[:7],
                        'author': author,
                        'timestamp': int(timestamp),
                        'date': datetime.fromtimestamp(int(timestamp), tz=timezone.utc),
                        'subject': subject
                    })
        
        return results
    
    def get_file_history(self, filepath: str, max_commits: int = 50) -> List[Dict]:
        """Get commit history for a specific file"""
        output = self._run_git_command([
            'log', '--format=%H|%an|%at|%s', f'-{max_commits}', '--', filepath
        ])
        
        results = []
        if output:
            for line in output.split('\n'):
                if not line:
                    continue
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commit_hash, author, timestamp, subject = parts
                    results.append({
                        'hash': commit_hash,
                        'short_hash': commit_hash[:7],
                        'author': author,
                        'timestamp': int(timestamp),
                        'date': datetime.fromtimestamp(int(timestamp), tz=timezone.utc),
                        'subject': subject
                    })
        
        return results
    
    def navigate_to_commit(self, commit_hash: str) -> bool:
        """Navigate to a specific commit"""
        # Verify commit exists
        result = self._run_git_command(['rev-parse', '--verify', commit_hash])
        if result:
            self.current_commit = result
            # Update history index
            for i, commit in enumerate(self.commit_history):
                if commit['hash'].startswith(commit_hash):
                    self.history_index = i
                    break
            return True
        return False
    
    def go_back(self, steps: int = 1) -> Optional[str]:
        """Navigate backward in history"""
        new_index = self.history_index + steps
        if new_index < len(self.commit_history):
            self.history_index = new_index
            self.current_commit = self.commit_history[self.history_index]['hash']
            return self.current_commit
        return None
    
    def go_forward(self, steps: int = 1) -> Optional[str]:
        """Navigate forward in history"""
        new_index = self.history_index - steps
        if new_index >= 0:
            self.history_index = new_index
            self.current_commit = self.commit_history[self.history_index]['hash']
            return self.current_commit
        return None
    
    def list_commits(self, start: int = 0, count: int = 10) -> List[Dict]:
        """List commits in history"""
        end = min(start + count, len(self.commit_history))
        return self.commit_history[start:end]
    
    def get_branches_at_commit(self, commit_hash: str) -> List[str]:
        """Get branches that contain the commit"""
        output = self._run_git_command(['branch', '--contains', commit_hash])
        if output:
            branches = [branch.strip().replace('* ', '') for branch in output.split('\n')]
            return [b for b in branches if b]
        return []
    
    def get_tags_at_commit(self, commit_hash: str) -> List[str]:
        """Get tags that point to the commit"""
        output = self._run_git_command(['tag', '--points-at', commit_hash])
        if output:
            return [tag.strip() for tag in output.split('\n') if tag.strip()]
        return []
    
    def blame_file(self, filepath: str, commit_hash: Optional[str] = None) -> List[Dict]:
        """Get blame information for a file"""
        args = ['blame', '--line-porcelain']
        if commit_hash:
            args.append(commit_hash)
        args.append('--')
        args.append(filepath)
        
        output = self._run_git_command(args)
        if not output:
            return []
        
        blame_info = []
        current_entry = {}
        
        for line in output.split('\n'):
            if not line:
                continue
            
            if line.startswith('\t'):
                # This is the actual code line
                if current_entry:
                    current_entry['line'] = line[1:]
                    blame_info.append(current_entry.copy())
                    current_entry = {}
            elif ' ' in line:
                key, value = line.split(' ', 1)
                if len(key) == 40:  # Commit hash
                    current_entry['hash'] = key
                    current_entry['line_number'] = value
                elif key == 'author':
                    current_entry['author'] = value
                elif key == 'author-time':
                    current_entry['timestamp'] = int(value)
                    current_entry['date'] = datetime.fromtimestamp(int(value), tz=timezone.utc)
        
        return blame_info


def format_commit_summary(commit: Dict, show_index: bool = False, index: int = 0) -> str:
    """Format a commit for display"""
    date_str = commit['date'].strftime('%Y-%m-%d %H:%M:%S')
    prefix = f"[{index}] " if show_index else ""
    return f"{prefix}{commit['short_hash']} - {date_str} - {commit['author']}: {commit['subject']}"


def format_commit_details(commit: Dict) -> str:
    """Format detailed commit information"""
    output = []
    output.append(f"Commit: {commit['hash']}")
    output.append(f"Author: {commit['author']} <{commit['email']}>")
    output.append(f"Date:   {commit['date'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
    output.append("")
    output.append(f"    {commit['subject']}")
    if commit.get('body'):
        output.append("")
        for line in commit['body'].split('\n'):
            output.append(f"    {line}")
    output.append("")
    
    if commit.get('files_changed'):
        output.append("Files changed:")
        for file_info in commit['files_changed']:
            status_symbol = {
                'A': '(added)',
                'M': '(modified)',
                'D': '(deleted)',
                'R': '(renamed)',
                'C': '(copied)'
            }.get(file_info['status'], '')
            output.append(f"  {file_info['status']} {status_symbol} {file_info['filename']}")
        output.append("")
    
    if commit.get('stats'):
        output.append(commit['stats'])
    
    return '\n'.join(output)


class CommandHandler:
    """Handles interactive debugger commands"""
    
    def __init__(self, traveler: RepoTimeTraveler):
        self.traveler = traveler
    
    def handle_current(self, args):
        """Show current commit details"""
        if self.traveler.current_commit:
            commit = self.traveler.get_commit_details(self.traveler.current_commit)
            if commit:
                print(format_commit_details(commit))
        else:
            print("No current commit")
    
    def handle_go(self, args):
        """Navigate to a specific commit"""
        if not args:
            print("Error: commit hash required")
            return
        if self.traveler.navigate_to_commit(args[0]):
            commit = self.traveler.get_commit_details(self.traveler.current_commit)
            if commit:
                print(f"Navigated to: {format_commit_summary(commit)}")
        else:
            print(f"Error: commit '{args[0]}' not found")
    
    def handle_back(self, args):
        """Go back n commits"""
        steps = int(args[0]) if args else 1
        new_commit = self.traveler.go_back(steps)
        if new_commit:
            commit = self.traveler.get_commit_details(new_commit)
            if commit:
                print(f"Moved back to: {format_commit_summary(commit)}")
        else:
            print("Error: cannot go back further")
    
    def handle_forward(self, args):
        """Go forward n commits"""
        steps = int(args[0]) if args else 1
        new_commit = self.traveler.go_forward(steps)
        if new_commit:
            commit = self.traveler.get_commit_details(new_commit)
            if commit:
                print(f"Moved forward to: {format_commit_summary(commit)}")
        else:
            print("Error: cannot go forward further")
    
    def handle_show(self, args):
        """Show commit details"""
        commit_hash = args[0] if args else self.traveler.current_commit
        if commit_hash:
            commit = self.traveler.get_commit_details(commit_hash)
            if commit:
                print(format_commit_details(commit))
            else:
                print(f"Error: commit '{commit_hash}' not found")
        else:
            print("Error: no commit specified and no current commit")
    
    def handle_list(self, args):
        """List recent commits"""
        count = int(args[0]) if args else 10
        commits = self.traveler.list_commits(self.traveler.history_index, count)
        if commits:
            print(f"\nShowing {len(commits)} commits:")
            for i, commit in enumerate(commits):
                marker = "→ " if i == 0 else "  "
                print(f"{marker}{format_commit_summary(commit, show_index=True, index=i)}")
            print()
        else:
            print("No commits found")
    
    def handle_diff(self, args):
        """Show diff between commits"""
        if len(args) < 2:
            print("Error: requires two commit hashes")
            return
        filepath = args[2] if len(args) > 2 else None
        diff = self.traveler.diff_commits(args[0], args[1], filepath)
        if diff:
            print(diff)
        else:
            print("No differences found")
    
    def handle_file(self, args):
        """Show file at specific commit"""
        if len(args) < 2:
            print("Error: requires commit hash and filepath")
            return
        content = self.traveler.get_file_at_commit(args[0], args[1])
        if content:
            print(content)
        else:
            print(f"Error: file '{args[1]}' not found at commit '{args[0]}'")
    
    def handle_history(self, args):
        """Show file history"""
        if not args:
            print("Error: filepath required")
            return
        history = self.traveler.get_file_history(args[0])
        if history:
            print(f"\nHistory for {args[0]}:")
            for commit in history:
                print(format_commit_summary(commit))
            print()
        else:
            print(f"No history found for '{args[0]}'")
    
    def handle_search(self, args):
        """Search commits by message"""
        if not args:
            print("Error: search query required")
            return
        query = ' '.join(args)
        results = self.traveler.search_commits(query, 'message')
        self._print_search_results(results, query, "commits")
    
    def handle_search_author(self, args):
        """Search commits by author"""
        if not args:
            print("Error: author name required")
            return
        query = ' '.join(args)
        results = self.traveler.search_commits(query, 'author')
        self._print_search_results(results, query, f"commits by '{query}'")
    
    def handle_search_file(self, args):
        """Search commits by file"""
        if not args:
            print("Error: filepath required")
            return
        results = self.traveler.search_commits(args[0], 'file')
        self._print_search_results(results, args[0], f"commits for '{args[0]}'")
    
    def handle_search_code(self, args):
        """Search commits by code content"""
        if not args:
            print("Error: search text required")
            return
        query = ' '.join(args)
        results = self.traveler.search_commits(query, 'content')
        self._print_search_results(results, query, f"commits containing '{query}'")
    
    def handle_blame(self, args):
        """Show blame for file"""
        if not args:
            print("Error: filepath required")
            return
        blame_info = self.traveler.blame_file(args[0])
        if blame_info:
            print(f"\nBlame for {args[0]}:")
            current_commit = None
            for info in blame_info:
                if info['hash'] != current_commit:
                    current_commit = info['hash']
                    date_str = info['date'].strftime('%Y-%m-%d')
                    print(f"\n{info['hash'][:7]} ({info['author']}, {date_str}):")
                print(f"  {info.get('line', '')}")
            print()
        else:
            print(f"No blame information for '{args[0]}'")
    
    def handle_branches(self, args):
        """Show branches at commit"""
        commit_hash = args[0] if args else self.traveler.current_commit
        if commit_hash:
            branches = self.traveler.get_branches_at_commit(commit_hash)
            if branches:
                print(f"\nBranches containing {commit_hash[:7]}:")
                for branch in branches:
                    print(f"  {branch}")
                print()
            else:
                print(f"No branches found for commit {commit_hash[:7]}")
        else:
            print("Error: no commit specified")
    
    def handle_tags(self, args):
        """Show tags at commit"""
        commit_hash = args[0] if args else self.traveler.current_commit
        if commit_hash:
            tags = self.traveler.get_tags_at_commit(commit_hash)
            if tags:
                print(f"\nTags at {commit_hash[:7]}:")
                for tag in tags:
                    print(f"  {tag}")
                print()
            else:
                print(f"No tags found at commit {commit_hash[:7]}")
        else:
            print("Error: no commit specified")
    
    def _print_search_results(self, results, query, description):
        """Print search results in consistent format"""
        if results:
            print(f"\nFound {len(results)} {description}:")
            for commit in results:
                print(format_commit_summary(commit))
            print()
        else:
            print(f"No {description} found")


def _print_help():
    """Print help message"""
    print("🕰️  Repository Time-Travel Debugger")
    print("=" * 60)
    print("Commands:")
    print("  go <commit>     - Navigate to specific commit")
    print("  back [n]        - Go back n commits (default: 1)")
    print("  forward [n]     - Go forward n commits (default: 1)")
    print("  show [commit]   - Show commit details")
    print("  list [n]        - List n recent commits (default: 10)")
    print("  diff <c1> <c2> [file] - Show diff between commits")
    print("  file <commit> <path>  - Show file at commit")
    print("  history <path>  - Show file history")
    print("  search <query>  - Search commits by message")
    print("  search-author <name> - Search by author")
    print("  search-file <path>   - Search commits for file")
    print("  search-code <text>   - Search in code content")
    print("  blame <path>    - Show blame for file")
    print("  branches [commit] - Show branches at commit")
    print("  tags [commit]   - Show tags at commit")
    print("  current         - Show current commit")
    print("  help            - Show this help")
    print("  quit            - Exit")
    print("=" * 60)


def interactive_mode(traveler: RepoTimeTraveler):
    """Run interactive time-travel debugger"""
    _print_help()
    print()
    
    if traveler.current_commit:
        print(f"Current position: {traveler.current_commit[:7]}")
        print()
    
    handler = CommandHandler(traveler)
    
    command_map = {
        'current': handler.handle_current,
        'go': handler.handle_go,
        'back': handler.handle_back,
        'forward': handler.handle_forward,
        'show': handler.handle_show,
        'list': handler.handle_list,
        'diff': handler.handle_diff,
        'file': handler.handle_file,
        'history': handler.handle_history,
        'search': handler.handle_search,
        'search-author': handler.handle_search_author,
        'search-file': handler.handle_search_file,
        'search-code': handler.handle_search_code,
        'blame': handler.handle_blame,
        'branches': handler.handle_branches,
        'tags': handler.handle_tags,
    }
    
    while True:
        try:
            user_input = input("time-travel> ").strip()
            if not user_input:
                continue
            
            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:]
            
            if command in ['quit', 'exit', 'q']:
                print("Exiting time-travel debugger...")
                break
            elif command == 'help':
                print("\nAvailable commands:")
                print("  go, back, forward, show, list, diff, file, history")
                print("  search, search-author, search-file, search-code")
                print("  blame, branches, tags, current, help, quit")
                print()
            elif command in command_map:
                command_map[command](args)
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit")
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Repository Time-Travel Debugger - Navigate and debug git history interactively'
    )
    parser.add_argument(
        '-r', '--repo',
        default='.',
        help='Path to git repository (default: current directory)'
    )
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        default=True,
        help='Run in interactive mode (default)'
    )
    parser.add_argument(
        '--show',
        metavar='COMMIT',
        help='Show details for a specific commit'
    )
    parser.add_argument(
        '--list',
        metavar='N',
        type=int,
        help='List N recent commits'
    )
    parser.add_argument(
        '--search',
        metavar='QUERY',
        help='Search commits by message'
    )
    parser.add_argument(
        '--history',
        metavar='FILE',
        help='Show history for a specific file'
    )
    
    args = parser.parse_args()
    
    # Verify we're in a git repository
    if not os.path.exists(os.path.join(args.repo, '.git')):
        print(f"Error: '{args.repo}' is not a git repository", file=sys.stderr)
        sys.exit(1)
    
    traveler = RepoTimeTraveler(args.repo)
    
    if not traveler.current_commit:
        print("Error: Could not initialize time traveler (empty repository?)", file=sys.stderr)
        sys.exit(1)
    
    # Handle non-interactive commands
    if args.show:
        commit = traveler.get_commit_details(args.show)
        if commit:
            print(format_commit_details(commit))
        else:
            print(f"Error: commit '{args.show}' not found", file=sys.stderr)
            sys.exit(1)
        return
    
    if args.list:
        commits = traveler.list_commits(0, args.list)
        for commit in commits:
            print(format_commit_summary(commit))
        return
    
    if args.search:
        results = traveler.search_commits(args.search, 'message')
        if results:
            print(f"Found {len(results)} commits:")
            for commit in results:
                print(format_commit_summary(commit))
        else:
            print(f"No commits found matching '{args.search}'")
        return
    
    if args.history:
        history = traveler.get_file_history(args.history)
        if history:
            print(f"History for {args.history}:")
            for commit in history:
                print(format_commit_summary(commit))
        else:
            print(f"No history found for '{args.history}'")
        return
    
    # Default to interactive mode
    interactive_mode(traveler)


if __name__ == '__main__':
    main()
