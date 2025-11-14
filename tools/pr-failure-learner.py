#!/usr/bin/env python3
"""
PR Failure Learning System

A systematic approach to learning from failed pull requests to improve future
code generation. Tracks PR failures, analyzes patterns, and generates actionable
insights for AI agents.

Architecture:
- Data collection from GitHub API (PR status, checks, reviews)
- Pattern analysis of failure causes
- Learning storage in structured format
- Integration with agent metrics system

Features:
- Comprehensive PR failure tracking (CI, tests, reviews, conflicts)
- Root cause analysis with categorization
- Temporal pattern detection
- Actionable improvement suggestions
- Integration with existing learning system

Usage:
    python pr-failure-learner.py --collect [--since DAYS]
    python pr-failure-learner.py --analyze [--output FILE]
    python pr-failure-learner.py --suggest --agent AGENT_ID
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import argparse

# Import GitHub integration utilities
try:
    from github_integration import GitHubAPIClient, GitHubAPIException
    GITHUB_INTEGRATION_AVAILABLE = True
except ImportError:
    GITHUB_INTEGRATION_AVAILABLE = False
    print("Warning: github_integration module not found. Using fallback.", file=sys.stderr)


# Constants
LEARNINGS_DIR = Path("learnings")
PR_FAILURES_FILE = LEARNINGS_DIR / "pr_failures.json"
AGENT_SYSTEM_DIR = Path(".github/agent-system")
REGISTRY_FILE = AGENT_SYSTEM_DIR / "registry.json"
REPO_OWNER = os.environ.get('GITHUB_REPOSITORY_OWNER', 'enufacas')
REPO_NAME = os.environ.get('GITHUB_REPOSITORY', 'enufacas/Chained').split('/')[-1]


@dataclass
class PRFailure:
    """Structured representation of a PR failure"""
    pr_number: int
    title: str
    author: str
    agent_id: Optional[str] = None
    agent_specialization: Optional[str] = None
    created_at: str = ""
    closed_at: Optional[str] = None
    failure_type: str = ""  # ci_failure, review_rejection, merge_conflict, test_failure
    failure_details: Dict[str, Any] = field(default_factory=dict)
    check_runs: List[Dict[str, Any]] = field(default_factory=list)
    review_comments: List[Dict[str, Any]] = field(default_factory=list)
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    labels: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class FailurePattern:
    """Identified pattern in PR failures"""
    pattern_type: str
    occurrences: int
    affected_agents: List[str]
    common_issues: List[str]
    suggested_improvements: List[str]
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class PRFailureLearner:
    """Main class for PR failure learning system"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.client = None
        if GITHUB_INTEGRATION_AVAILABLE:
            token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
            if token:
                self.client = GitHubAPIClient(token)
        
        # Ensure directories exist
        LEARNINGS_DIR.mkdir(exist_ok=True)
    
    def log(self, message: str):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(f"[PR-Learner] {message}", file=sys.stderr)
    
    def collect_pr_failures(self, since_days: int = 30) -> List[PRFailure]:
        """
        Collect PR failure data from GitHub.
        
        Args:
            since_days: Number of days to look back
            
        Returns:
            List of PR failures
        """
        self.log(f"Collecting PR failures from last {since_days} days...")
        
        if not self.client:
            self.log("GitHub client not available, returning empty list")
            return []
        
        failures = []
        since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
        
        try:
            # Get closed PRs
            params = {
                'state': 'closed',
                'sort': 'updated',
                'direction': 'desc',
                'per_page': 100
            }
            prs = self.client.get(f'/repos/{REPO_OWNER}/{REPO_NAME}/pulls', params)
            
            if not prs:
                self.log("No PRs found")
                return []
            
            for pr in prs:
                # Skip merged PRs - we only want failures
                if pr.get('merged_at'):
                    continue
                
                # Check if closed recently
                closed_at = pr.get('closed_at')
                if not closed_at:
                    continue
                
                pr_date = datetime.fromisoformat(closed_at.replace('Z', '+00:00'))
                since_dt = datetime.fromisoformat(since_date.replace('Z', '+00:00'))
                
                if pr_date < since_dt:
                    continue
                
                self.log(f"Processing failed PR #{pr['number']}: {pr['title']}")
                
                # Extract agent information from title or labels
                agent_id = None
                agent_spec = None
                for label in pr.get('labels', []):
                    label_name = label.get('name', '')
                    if label_name.startswith('agent:'):
                        agent_spec = label_name.replace('agent:', '')
                    elif label_name.startswith('agent-'):
                        agent_id = label_name
                
                # Detect failure type
                failure_type = self._detect_failure_type(pr)
                
                # Get check runs for CI failures
                check_runs = []
                if failure_type in ['ci_failure', 'test_failure']:
                    check_runs = self._get_check_runs(pr['number'])
                
                # Get review comments
                review_comments = self._get_review_comments(pr['number'])
                
                # Create failure record
                failure = PRFailure(
                    pr_number=pr['number'],
                    title=pr['title'],
                    author=pr['user']['login'],
                    agent_id=agent_id,
                    agent_specialization=agent_spec,
                    created_at=pr['created_at'],
                    closed_at=closed_at,
                    failure_type=failure_type,
                    failure_details={
                        'state_reason': pr.get('state_reason'),
                        'draft': pr.get('draft', False)
                    },
                    check_runs=check_runs,
                    review_comments=review_comments,
                    files_changed=pr.get('changed_files', 0),
                    additions=pr.get('additions', 0),
                    deletions=pr.get('deletions', 0),
                    labels=[l['name'] for l in pr.get('labels', [])]
                )
                failures.append(failure)
        
        except Exception as e:
            self.log(f"Error collecting PR failures: {e}")
        
        self.log(f"Collected {len(failures)} PR failures")
        return failures
    
    def _detect_failure_type(self, pr: Dict[str, Any]) -> str:
        """Detect the type of PR failure"""
        # Check labels first
        labels = [l['name'] for l in pr.get('labels', [])]
        if 'merge-conflict' in labels or 'conflicts' in labels:
            return 'merge_conflict'
        
        # Check title
        title_lower = pr['title'].lower()
        if 'conflict' in title_lower:
            return 'merge_conflict'
        if 'test' in title_lower and 'fail' in title_lower:
            return 'test_failure'
        
        # Default to review rejection if closed without merge
        return 'review_rejection'
    
    def _get_check_runs(self, pr_number: int) -> List[Dict[str, Any]]:
        """Get check runs for a PR"""
        if not self.client:
            return []
        
        try:
            # Get commits for this PR
            commits = self.client.get(f'/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/commits')
            if not commits:
                return []
            
            # Get check runs for the latest commit
            latest_commit_sha = commits[-1]['sha']
            check_runs_data = self.client.get(
                f'/repos/{REPO_OWNER}/{REPO_NAME}/commits/{latest_commit_sha}/check-runs'
            )
            
            if not check_runs_data or 'check_runs' not in check_runs_data:
                return []
            
            # Extract relevant info from failed checks
            failed_checks = []
            for check in check_runs_data['check_runs']:
                if check.get('conclusion') in ['failure', 'cancelled', 'timed_out']:
                    failed_checks.append({
                        'name': check['name'],
                        'conclusion': check['conclusion'],
                        'started_at': check.get('started_at'),
                        'completed_at': check.get('completed_at'),
                        'output': {
                            'title': check.get('output', {}).get('title'),
                            'summary': check.get('output', {}).get('summary', '')[:500]  # Truncate
                        }
                    })
            
            return failed_checks
        
        except Exception as e:
            self.log(f"Error getting check runs for PR #{pr_number}: {e}")
            return []
    
    def _get_review_comments(self, pr_number: int) -> List[Dict[str, Any]]:
        """Get review comments for a PR"""
        if not self.client:
            return []
        
        try:
            reviews = self.client.get(f'/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/reviews')
            if not reviews:
                return []
            
            # Extract comments from negative reviews
            comments = []
            for review in reviews:
                if review.get('state') in ['CHANGES_REQUESTED', 'COMMENTED']:
                    if review.get('body'):
                        comments.append({
                            'author': review['user']['login'],
                            'state': review['state'],
                            'body': review['body'][:500],  # Truncate
                            'submitted_at': review.get('submitted_at')
                        })
            
            return comments
        
        except Exception as e:
            self.log(f"Error getting reviews for PR #{pr_number}: {e}")
            return []
    
    def save_failures(self, failures: List[PRFailure]):
        """Save PR failures to storage"""
        self.log(f"Saving {len(failures)} failures to {PR_FAILURES_FILE}")
        
        # Load existing failures
        existing_data = {'failures': [], 'last_updated': None}
        if PR_FAILURES_FILE.exists():
            with open(PR_FAILURES_FILE, 'r') as f:
                existing_data = json.load(f)
        
        # Merge with new failures (avoid duplicates)
        existing_prs = {f['pr_number'] for f in existing_data['failures']}
        new_failures = [f for f in failures if f.pr_number not in existing_prs]
        
        # Combine and save
        all_failures = existing_data['failures'] + [f.to_dict() for f in new_failures]
        
        data = {
            'failures': all_failures,
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'total_count': len(all_failures)
        }
        
        with open(PR_FAILURES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.log(f"Saved {len(new_failures)} new failures")
    
    def load_failures(self) -> List[PRFailure]:
        """Load PR failures from storage"""
        if not PR_FAILURES_FILE.exists():
            return []
        
        with open(PR_FAILURES_FILE, 'r') as f:
            data = json.load(f)
        
        failures = []
        for f_dict in data.get('failures', []):
            failure = PRFailure(**f_dict)
            failures.append(failure)
        
        return failures
    
    def analyze_patterns(self, failures: List[PRFailure]) -> List[FailurePattern]:
        """
        Analyze PR failures to identify patterns.
        
        Args:
            failures: List of PR failures to analyze
            
        Returns:
            List of identified patterns
        """
        self.log(f"Analyzing patterns from {len(failures)} failures...")
        
        patterns = []
        
        # Group by failure type
        by_type = defaultdict(list)
        for f in failures:
            by_type[f.failure_type].append(f)
        
        # Analyze each failure type
        for failure_type, type_failures in by_type.items():
            # Common issues per type
            common_issues = self._extract_common_issues(type_failures)
            
            # Affected agents
            affected_agents = [f.agent_specialization for f in type_failures if f.agent_specialization]
            agent_counter = Counter(affected_agents)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(failure_type, common_issues, type_failures)
            
            # Calculate confidence based on sample size
            confidence = min(1.0, len(type_failures) / 10.0)
            
            pattern = FailurePattern(
                pattern_type=failure_type,
                occurrences=len(type_failures),
                affected_agents=list(agent_counter.keys()),
                common_issues=common_issues,
                suggested_improvements=suggestions,
                confidence_score=confidence
            )
            patterns.append(pattern)
        
        self.log(f"Identified {len(patterns)} patterns")
        return patterns
    
    def _extract_common_issues(self, failures: List[PRFailure]) -> List[str]:
        """Extract common issues from failures"""
        issues = []
        
        # Analyze check run failures
        check_names = []
        for f in failures:
            for check in f.check_runs:
                check_names.append(check['name'])
        
        if check_names:
            most_common_checks = Counter(check_names).most_common(3)
            for check_name, count in most_common_checks:
                if count > 1:
                    issues.append(f"Repeated check failure: {check_name} ({count} times)")
        
        # Analyze file change sizes
        large_changes = [f for f in failures if f.files_changed > 20]
        if len(large_changes) > len(failures) * 0.3:
            issues.append(f"Large changesets (>20 files): {len(large_changes)}/{len(failures)} PRs")
        
        # Analyze review comments for common themes
        review_keywords = []
        for f in failures:
            for comment in f.review_comments:
                body_lower = comment['body'].lower()
                if 'test' in body_lower:
                    review_keywords.append('missing_tests')
                if 'security' in body_lower:
                    review_keywords.append('security_concern')
                if 'documentation' in body_lower or 'doc' in body_lower:
                    review_keywords.append('missing_docs')
                if 'typo' in body_lower or 'style' in body_lower:
                    review_keywords.append('code_style')
        
        if review_keywords:
            common_keywords = Counter(review_keywords).most_common(3)
            for keyword, count in common_keywords:
                if count > 1:
                    issues.append(f"Review concern - {keyword}: {count} mentions")
        
        return issues[:10]  # Top 10 issues
    
    def _generate_suggestions(self, failure_type: str, issues: List[str], 
                             failures: List[PRFailure]) -> List[str]:
        """Generate improvement suggestions based on failure patterns"""
        suggestions = []
        
        if failure_type == 'ci_failure' or failure_type == 'test_failure':
            suggestions.append("Run tests locally before creating PR")
            suggestions.append("Ensure CI environment matches local development setup")
            if any('test' in issue.lower() for issue in issues):
                suggestions.append("Add or update tests to cover new functionality")
        
        elif failure_type == 'review_rejection':
            if any('missing_tests' in issue for issue in issues):
                suggestions.append("Include comprehensive tests with all PRs")
            if any('missing_docs' in issue for issue in issues):
                suggestions.append("Update documentation for code changes")
            if any('code_style' in issue for issue in issues):
                suggestions.append("Run linter before submitting PR")
            if any('security' in issue.lower() for issue in issues):
                suggestions.append("Review security implications of changes")
        
        elif failure_type == 'merge_conflict':
            suggestions.append("Sync with main branch before creating PR")
            suggestions.append("Keep PR scope small to reduce conflict likelihood")
            suggestions.append("Rebase regularly for long-lived PRs")
        
        # Size-based suggestions
        large_prs = [f for f in failures if f.files_changed > 20]
        if len(large_prs) > len(failures) * 0.3:
            suggestions.append("Break large changes into smaller, focused PRs")
        
        return suggestions[:5]  # Top 5 suggestions
    
    def generate_agent_suggestions(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate improvement suggestions for a specific agent or all agents.
        
        Args:
            agent_id: Optional agent ID to get specific suggestions
            
        Returns:
            Dictionary with suggestions per agent
        """
        self.log(f"Generating suggestions for agent: {agent_id or 'all'}")
        
        failures = self.load_failures()
        if not failures:
            self.log("No failures to analyze")
            return {}
        
        # Filter by agent if specified
        if agent_id:
            failures = [f for f in failures if f.agent_id == agent_id]
        
        # Analyze patterns
        patterns = self.analyze_patterns(failures)
        
        # Organize suggestions by agent
        agent_suggestions = defaultdict(lambda: {
            'total_failures': 0,
            'failure_types': Counter(),
            'improvements': []
        })
        
        for failure in failures:
            agent_key = failure.agent_specialization or 'unknown'
            agent_suggestions[agent_key]['total_failures'] += 1
            agent_suggestions[agent_key]['failure_types'][failure.failure_type] += 1
        
        # Add pattern-based suggestions
        for pattern in patterns:
            for agent in pattern.affected_agents:
                agent_suggestions[agent]['improvements'].extend(pattern.suggested_improvements)
        
        # Deduplicate suggestions
        for agent in agent_suggestions:
            improvements = agent_suggestions[agent]['improvements']
            agent_suggestions[agent]['improvements'] = list(set(improvements))
            agent_suggestions[agent]['failure_types'] = dict(agent_suggestions[agent]['failure_types'])
        
        return dict(agent_suggestions)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='PR Failure Learning System')
    parser.add_argument('--collect', action='store_true', 
                       help='Collect PR failures from GitHub')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze collected failures')
    parser.add_argument('--suggest', action='store_true',
                       help='Generate improvement suggestions')
    parser.add_argument('--agent', type=str,
                       help='Specific agent ID for suggestions')
    parser.add_argument('--since', type=int, default=30,
                       help='Days to look back (default: 30)')
    parser.add_argument('--output', type=str,
                       help='Output file for analysis results')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    learner = PRFailureLearner(verbose=args.verbose)
    
    if args.collect:
        failures = learner.collect_pr_failures(since_days=args.since)
        learner.save_failures(failures)
        print(f"✅ Collected {len(failures)} PR failures")
    
    if args.analyze:
        failures = learner.load_failures()
        if not failures:
            print("⚠️  No failures to analyze. Run with --collect first.")
            sys.exit(1)
        
        patterns = learner.analyze_patterns(failures)
        
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_failures': len(failures),
            'patterns': [p.to_dict() for p in patterns],
            'failure_type_distribution': dict(Counter(f.failure_type for f in failures))
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Analysis saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    
    if args.suggest:
        suggestions = learner.generate_agent_suggestions(agent_id=args.agent)
        print(json.dumps(suggestions, indent=2))
    
    if not (args.collect or args.analyze or args.suggest):
        parser.print_help()


if __name__ == '__main__':
    main()
