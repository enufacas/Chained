#!/usr/bin/env python3
"""
Generate and update CHANGELOG.md from git commit history.

This script:
1. Parses git commits with conventional commit prefixes (feat, fix, chore, etc.)
2. Categorizes changes by type
3. Differentiates between user-prompted and bot-only changes
4. Excludes auto-churn commits (data syncs, automated updates)
5. Links to PRs when available
6. Maintains chronological order by date
"""

import subprocess
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import argparse


# Commit types and their display names
COMMIT_TYPES = {
    'feat': '✨ Features',
    'fix': '🐛 Bug Fixes',
    'docs': '📚 Documentation',
    'chore': '🧹 Chores',
    'refactor': '♻️ Refactors',
    'test': '✅ Tests',
    'perf': '⚡ Performance',
    'ci': '👷 CI/CD',
    'build': '🔨 Build',
    'style': '💎 Style',
    'revert': '⏪ Reverts',
}

# Patterns to identify auto-churn commits that should be excluded
AUTO_CHURN_PATTERNS = [
    r'^🔄\s+(AgentOps|data)\s+sync',
    r'^🧠\s+Daily\s+Learning\s+Reflection',
    r'^🏗️\s+Update\s+architecture\s+evolution\s+tracking',
    r'^Update\s+AI\s+ideas\s+history',
    r'^\[auto\]',
    r'^chore:\s+update\s+reviewer\s+dashboard',
    r'^Auto-merge',
]

# Actors that indicate user-initiated vs bot-only
USER_ACTORS = ['enufacas']  # Add more user names as needed
BOT_ACTORS = ['github-actions[bot]', 'copilot-swe-agent[bot]']


class Commit:
    """Represents a git commit with parsed metadata."""
    
    def __init__(self, sha: str, subject: str, author_name: str, author_email: str, date: str, body: str = ''):
        self.sha = sha
        self.subject = subject
        self.author_name = author_name
        self.author_email = author_email
        self.date = datetime.fromisoformat(date.replace('+0000', '+00:00').replace(' ', 'T', 1))
        self.body = body
        self.pr_number = self._extract_pr_number()
        self.commit_type = self._extract_commit_type()
        self.is_user_initiated = self._determine_user_initiated()
        self.file_types = self._detect_file_types()
        
    def _extract_pr_number(self) -> Optional[int]:
        """Extract PR number from commit subject like (#1234) or from commit body."""
        # Try subject first
        match = re.search(r'\(#(\d+)\)', self.subject)
        if match:
            return int(match.group(1))
        
        # Try subject without parens
        match = re.search(r'#(\d+)', self.subject)
        if match:
            return int(match.group(1))
        
        # Try commit body
        if self.body:
            # Look for PR references in body
            match = re.search(r'#(\d+)', self.body)
            if match:
                return int(match.group(1))
        
        return None
    
    def _detect_file_types(self) -> set:
        """Detect special file types from commit subject."""
        types = set()
        subject_lower = self.subject.lower()
        
        # Check for workflow changes
        if '.github/workflows' in subject_lower or 'workflow' in subject_lower:
            types.add('workflow')
        
        # Check for agent changes
        if '.github/agents' in subject_lower or 'agent' in subject_lower or '@' in self.subject:
            types.add('agent')
        
        # Check for instruction changes
        if '.github/instructions' in subject_lower or 'instruction' in subject_lower or 'copilot-instructions' in subject_lower:
            types.add('instruction')
        
        return types
    
    def get_special_decorations(self) -> str:
        """Get special decoration emojis for file types."""
        decorations = []
        if 'workflow' in self.file_types:
            decorations.append('⚙️')
        if 'agent' in self.file_types:
            decorations.append('🔧')
        if 'instruction' in self.file_types:
            decorations.append('📋')
        
        return ' '.join(decorations) if decorations else ''
    
    def _extract_commit_type(self) -> Optional[str]:
        """Extract commit type from conventional commit prefix."""
        match = re.match(r'^(feat|fix|docs|chore|refactor|test|perf|ci|build|style|revert):', self.subject)
        return match.group(1) if match else None
    
    def _determine_user_initiated(self) -> bool:
        """Determine if this was user-initiated or bot-only."""
        # Check if author is a known user
        if any(user in self.author_email for user in USER_ACTORS):
            return True
        
        # Check if it's a PR merge with Copilot author (user prompted through issue)
        if self.pr_number and 'Copilot' in self.author_email and 'copilot-swe-agent' not in self.author_email:
            # PRs merged by main Copilot account are usually user-initiated
            return True
        
        return False
    
    def should_exclude(self) -> bool:
        """Check if this commit should be excluded from changelog."""
        # Check auto-churn patterns
        for pattern in AUTO_CHURN_PATTERNS:
            if re.search(pattern, self.subject, re.IGNORECASE):
                return True
        
        # Exclude "Initial plan" commits
        if self.subject.strip() == 'Initial plan':
            return True
        
        return False
    
    def get_clean_subject(self) -> str:
        """Get subject without PR number and prefix."""
        # Remove PR number
        subject = re.sub(r'\s*\(#\d+\)', '', self.subject)
        
        # Remove commit type prefix if present
        if self.commit_type:
            subject = re.sub(rf'^{self.commit_type}:\s*', '', subject)
        
        return subject.strip()
    
    def get_actor_badge(self) -> str:
        """Get a badge indicating the actor type."""
        if self.is_user_initiated:
            return '👤'
        return '🤖'


def get_git_commits(since_date: Optional[str] = None) -> List[Commit]:
    """Fetch commits from git history."""
    # Use a unique separator less likely to appear in commit messages
    separator = '|||COMMIT_SEP|||'
    cmd = ['git', 'log', '--all', f'--format=%H{separator}%s{separator}%an{separator}%ae{separator}%ad{separator}%b{separator}END', '--date=iso']
    
    if since_date:
        cmd.extend(['--since', since_date])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = []
        
        # Split by END marker to get individual commits
        commit_blocks = result.stdout.strip().split(f'{separator}END')
        
        for block in commit_blocks:
            if not block.strip():
                continue
            
            parts = block.split(separator)
            if len(parts) >= 5:
                sha = parts[0].strip()
                subject = parts[1].strip()
                author_name = parts[2].strip()
                author_email = parts[3].strip()
                date = parts[4].strip()
                body = parts[5].strip() if len(parts) > 5 else ''
                
                if not sha:
                    continue
                
                commit = Commit(sha, subject, author_name, author_email, date, body)
                
                # Only include commits with conventional commit types
                if commit.commit_type and not commit.should_exclude():
                    commits.append(commit)
        
        # Second pass: enhance PR numbers by looking at merge commits
        enhance_pr_numbers_from_merges(commits)
        
        return commits
    
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}", file=sys.stderr)
        return []


def enhance_pr_numbers_from_merges(commits: List[Commit]):
    """Enhance PR numbers by looking at merge commits in git history."""
    try:
        # Get all merge commits with PR numbers
        result = subprocess.run(
            ['git', 'log', '--all', '--merges', '--format=%H|%s'],
            capture_output=True, text=True, check=True
        )
        
        # Build a mapping of commit SHA to PR number from merge commits
        pr_map = {}
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 1)
            if len(parts) == 2:
                merge_sha, merge_subject = parts
                # Look for PR number in merge commit
                match = re.search(r'#(\d+)', merge_subject)
                if match:
                    pr_number = int(match.group(1))
                    # Get the commits included in this merge
                    try:
                        merge_commits = subprocess.run(
                            ['git', 'log', '--format=%H', f'{merge_sha}^..{merge_sha}'],
                            capture_output=True, text=True, check=True
                        )
                        for commit_sha in merge_commits.stdout.strip().split('\n'):
                            if commit_sha:
                                pr_map[commit_sha] = pr_number
                    except:
                        pass
        
        # Apply PR numbers to commits
        for commit in commits:
            if not commit.pr_number and commit.sha in pr_map:
                commit.pr_number = pr_map[commit.sha]
    
    except Exception as e:
        # Non-fatal, just skip enhancement
        pass


def group_commits_by_date_and_type(commits: List[Commit]) -> Dict[str, Dict[str, List[Commit]]]:
    """Group commits by date and type."""
    grouped = defaultdict(lambda: defaultdict(list))
    
    for commit in commits:
        date_key = commit.date.strftime('%Y-%m-%d')
        grouped[date_key][commit.commit_type].append(commit)
    
    return grouped


def collapse_similar_commits(commits: List[Commit], aggressive_docs: bool = True) -> List[Tuple[Commit, int]]:
    """Collapse similar commits and return (commit, count) tuples.
    
    Args:
        commits: List of commits to collapse
        aggressive_docs: If True, collapse documentation commits more aggressively
    """
    from collections import Counter
    
    # Group by clean subject
    subject_groups = defaultdict(list)
    for commit in commits:
        clean_subject = commit.get_clean_subject()
        
        # For documentation commits, further simplify by removing details
        if aggressive_docs and ('documentation' in clean_subject.lower() or 'doc:' in commit.subject.lower()):
            # Normalize common documentation patterns
            lower_subject = clean_subject.lower()
            
            # Collapse all variations of "add" documentation
            if any(pattern in lower_subject for pattern in ['add comprehensive', 'add implementation', 'add troubleshooting', 'add issue resolution', 'add final summary', 'add examples', 'add comment', 'add investigation', 'add quick-start']):
                clean_subject = 'Add documentation'
            # Collapse all variations of "update" documentation
            elif any(pattern in lower_subject for pattern in ['update documentation', 'update changelog', 'update guide', 'update readme']):
                clean_subject = 'Update documentation'
            # Collapse "complete" or "comprehensive" documentation
            elif 'complete' in lower_subject or 'comprehensive' in lower_subject:
                clean_subject = 'Add documentation'
        
        subject_groups[clean_subject].append(commit)
    
    # Return collapsed list with counts
    collapsed = []
    for subject, group in subject_groups.items():
        # Use the first commit as the representative
        representative = sorted(group, key=lambda c: c.date, reverse=True)[0]
        count = len(group)
        collapsed.append((representative, count))
    
    return collapsed


def generate_changelog_content(grouped_commits: Dict[str, Dict[str, List[Commit]]], 
                               include_header: bool = True) -> str:
    """Generate changelog markdown content."""
    lines = []
    
    if include_header:
        lines.extend([
            '# Changelog',
            '',
            'All notable changes to the Chained project are documented in this file.',
            '',
            'The format captures:',
            '- **Features** (feat): New capabilities and enhancements',
            '- **Bug Fixes** (fix): Corrections and fixes',
            '- **Major Improvements**: Significant changes that improve the system',
            '- **Chores & Maintenance**: Routine updates and housekeeping',
            '',
            'Actor indicators:',
            '- 👤 User-initiated (from issues or direct commits)',
            '- 🤖 Bot-generated (autonomous system)',
            '',
            'Special decorations:',
            '- ⚙️ Workflow changes (.github/workflows)',
            '- 🔧 Agent changes (.github/agents)',
            '- 📋 Instruction changes (.github/instructions)',
            '',
            'Note: Repeated similar tasks are collapsed with count (e.g., x12 means 12 occurrences).',
            '',
            'This changelog excludes automated data syncs and routine maintenance commits.',
            '',
            '---',
            '',
        ])
    
    # Sort dates in reverse chronological order
    sorted_dates = sorted(grouped_commits.keys(), reverse=True)
    
    for date in sorted_dates:
        commits_by_type = grouped_commits[date]
        
        # Count features and major improvements
        features = commits_by_type.get('feat', [])
        major_improvements = [c for c in features if c.is_user_initiated]
        
        # Only create section if there are relevant commits
        if not any(commits_by_type.values()):
            continue
        
        lines.append(f'## {date}')
        lines.append('')
        
        # Major Improvements section (user-initiated features)
        if major_improvements:
            lines.append('### ✨ Major Improvements')
            lines.append('')
            collapsed = collapse_similar_commits(major_improvements, aggressive_docs=False)
            for commit, count in sorted(collapsed, key=lambda x: x[0].date, reverse=True):
                pr_link = f' [#{commit.pr_number}](https://github.com/enufacas/Chained/pull/{commit.pr_number})' if commit.pr_number else ''
                count_suffix = f' (x{count})' if count > 1 else ''
                decorations = commit.get_special_decorations()
                decoration_prefix = f'{decorations} ' if decorations else ''
                lines.append(f'- {commit.get_actor_badge()} {decoration_prefix}{commit.get_clean_subject()}{count_suffix}{pr_link}')
            lines.append('')
        
        # Features section (all features including bot-generated)
        if features:
            lines.append('### ✨ Features')
            lines.append('')
            collapsed = collapse_similar_commits(features, aggressive_docs=False)
            for commit, count in sorted(collapsed, key=lambda x: x[0].date, reverse=True):
                pr_link = f' [#{commit.pr_number}](https://github.com/enufacas/Chained/pull/{commit.pr_number})' if commit.pr_number else ''
                count_suffix = f' (x{count})' if count > 1 else ''
                decorations = commit.get_special_decorations()
                decoration_prefix = f'{decorations} ' if decorations else ''
                lines.append(f'- {commit.get_actor_badge()} {decoration_prefix}{commit.get_clean_subject()}{count_suffix}{pr_link}')
            lines.append('')
        
        # Bug Fixes section
        fixes = commits_by_type.get('fix', [])
        if fixes:
            lines.append('### 🐛 Bug Fixes')
            lines.append('')
            collapsed = collapse_similar_commits(fixes, aggressive_docs=False)
            for commit, count in sorted(collapsed, key=lambda x: x[0].date, reverse=True):
                pr_link = f' [#{commit.pr_number}](https://github.com/enufacas/Chained/pull/{commit.pr_number})' if commit.pr_number else ''
                count_suffix = f' (x{count})' if count > 1 else ''
                decorations = commit.get_special_decorations()
                decoration_prefix = f'{decorations} ' if decorations else ''
                lines.append(f'- {commit.get_actor_badge()} {decoration_prefix}{commit.get_clean_subject()}{count_suffix}{pr_link}')
            lines.append('')
        
        # Other types grouped together
        other_types = [t for t in COMMIT_TYPES.keys() if t not in ['feat', 'fix'] and t in commits_by_type]
        if other_types:
            lines.append('### 🧹 Chores & Maintenance')
            lines.append('')
            for commit_type in other_types:
                # Use aggressive collapsing for documentation
                collapsed = collapse_similar_commits(commits_by_type[commit_type], aggressive_docs=True)
                for commit, count in sorted(collapsed, key=lambda x: x[0].date, reverse=True):
                    pr_link = f' [#{commit.pr_number}](https://github.com/enufacas/Chained/pull/{commit.pr_number})' if commit.pr_number else ''
                    type_label = COMMIT_TYPES[commit_type].split(' ', 1)[1].rstrip('s')  # Remove emoji and plural
                    count_suffix = f' (x{count})' if count > 1 else ''
                    decorations = commit.get_special_decorations()
                    decoration_prefix = f'{decorations} ' if decorations else ''
                    lines.append(f'- {commit.get_actor_badge()} {decoration_prefix}**{type_label}**: {commit.get_clean_subject()}{count_suffix}{pr_link}')
            lines.append('')
        
        lines.append('---')
        lines.append('')
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate CHANGELOG.md from git history')
    parser.add_argument('--since', help='Only include commits since this date (YYYY-MM-DD). Default: repository inception (2025-11-08)')
    parser.add_argument('--output', default='CHANGELOG.md', help='Output file path')
    parser.add_argument('--append', action='store_true', help='Append to existing changelog')
    parser.add_argument('--backfill', action='store_true', help='Generate complete history from inception')
    
    args = parser.parse_args()
    
    # Default to repository inception if no date specified
    since_date = args.since if args.since else '2025-11-08'
    
    # Get commits
    print(f"Fetching commits since {since_date}...")
    commits = get_git_commits(since_date=since_date)
    print(f"Found {len(commits)} relevant commits")
    
    if not commits:
        print("No commits to process")
        return
    
    # Group commits
    grouped = group_commits_by_date_and_type(commits)
    
    # Generate content
    include_header = not args.append
    content = generate_changelog_content(grouped, include_header=include_header)
    
    # Write to file
    mode = 'a' if args.append else 'w'
    with open(args.output, mode) as f:
        f.write(content)
    
    print(f"Changelog written to {args.output}")
    
    # Print summary
    print("\nSummary:")
    print(f"  Total commits: {len(commits)}")
    user_initiated = sum(1 for c in commits if c.is_user_initiated)
    bot_generated = len(commits) - user_initiated
    print(f"  User-initiated: {user_initiated}")
    print(f"  Bot-generated: {bot_generated}")
    
    # Count commits with PR links
    with_pr = sum(1 for c in commits if c.pr_number)
    print(f"  With PR links: {with_pr} ({with_pr*100//len(commits)}%)")
    
    print(f"  Date range: {min(c.date for c in commits).date()} to {max(c.date for c in commits).date()}")


if __name__ == '__main__':
    main()
