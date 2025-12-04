#!/usr/bin/env python3
"""
Git Commit Strategy Learning System for Chained

A visionary, self-improving system for learning optimal git commit strategies
from successful merges. This system analyzes commit patterns, correlates them
with merge success, and generates actionable recommendations that evolve over time.

Inspired by Tesla's approach: innovative, elegant, and forward-thinking.
Enhanced by @create-botter with autonomous learning capabilities.

Architecture:
- CommitStrategyAnalyzer: Core analysis engine with trend detection
- CommitPatternDatabase: Structured pattern storage with history
- StrategyRecommender: Context-aware recommendation generation
- TrendAnalyzer: Identifies improving/declining patterns over time
- Integration with Chained's autonomous learning systems

Features:
- Analyzes commit size, message quality, file organization, timing
- Tracks correlation between commit attributes and merge success
- Learns repository-specific optimal strategies continuously
- Generates confidence-scored, context-aware recommendations
- Supports incremental learning from new merges
- Tracks strategy effectiveness over time
- Identifies emerging patterns and best practices
- Provides trend analysis and predictive insights

Usage:
    python commit-strategy-learner.py --analyze [--since DAYS]
    python commit-strategy-learner.py --recommend --context "feature" 
    python commit-strategy-learner.py --report [--output FILE]
    python commit-strategy-learner.py --trends [--period DAYS]
"""

import json
import os
import sys
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
from statistics import mean, median, stdev
import argparse


# Constants
LEARNINGS_DIR = Path("learnings")
COMMIT_STRATEGIES_FILE = LEARNINGS_DIR / "commit_strategies.json"
ANALYSIS_DIR = Path("analysis")
COMMIT_PATTERNS_FILE = ANALYSIS_DIR / "commit_patterns.json"

# Trend constants
TREND_IMPROVING = "improving"
TREND_STABLE = "stable"
TREND_DECLINING = "declining"
TREND_UNKNOWN = "unknown"

# Commit quality thresholds
MIN_MESSAGE_LENGTH = 10
MAX_MESSAGE_LENGTH = 72  # First line
IDEAL_FILES_PER_COMMIT = 5
MAX_FILES_PER_COMMIT = 15
IDEAL_LINES_CHANGED = 100
MAX_LINES_CHANGED = 500


@dataclass
class CommitMetrics:
    """Structured representation of commit metrics"""
    commit_hash: str
    author: str
    timestamp: str
    message: str
    message_length: int
    has_body: bool
    follows_conventional: bool
    conventional_type: Optional[str] = None
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    total_lines_changed: int = 0
    file_types: List[str] = field(default_factory=list)
    merge_status: str = "unknown"  # success, failed, pending
    merge_pr_number: Optional[int] = None
    merge_time_hours: Optional[float] = None
    ci_pass: bool = False
    review_comments: int = 0
    changes_requested: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CommitPattern:
    """Identified pattern in successful commits"""
    pattern_name: str
    pattern_type: str  # message, size, organization, timing
    description: str
    success_rate: float
    occurrence_count: int
    average_merge_time_hours: float
    common_attributes: Dict[str, Any]
    examples: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass  
class StrategyRecommendation:
    """Actionable commit strategy recommendation"""
    recommendation_id: str
    title: str
    description: str
    rationale: str
    expected_improvement: str
    confidence_score: float
    applicable_contexts: List[str]
    supporting_patterns: List[str]
    example_commits: List[str] = field(default_factory=list)
    trend: str = TREND_STABLE  # Use constant instead of magic string
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TrendData:
    """Historical trend analysis for patterns"""
    pattern_name: str
    measurements: List[Dict[str, Any]] = field(default_factory=list)
    trend_direction: str = TREND_UNKNOWN
    trend_confidence: float = 0.0
    velocity: float = 0.0  # Rate of change
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class CommitStrategyLearner:
    """
    Main class for git commit strategy learning system.
    
    Implements a systematic, rigorous approach to analyzing git commit
    patterns and learning optimal strategies from successful merges.
    """
    
    def __init__(self, repo_path: str = ".", verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.verbose = verbose
        self.strategies_data = self._load_strategies()
        self.patterns_data = self._load_patterns()
        
    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode enabled"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)
    
    def _load_strategies(self) -> Dict:
        """Load existing strategies database"""
        if COMMIT_STRATEGIES_FILE.exists():
            with open(COMMIT_STRATEGIES_FILE, 'r') as f:
                return json.load(f)
        return self._initialize_strategies()
    
    def _initialize_strategies(self) -> Dict:
        """Initialize strategies database with structure"""
        return {
            "version": "1.0.0",
            "last_updated": None,
            "repository": self.repo_path.name,
            "total_commits_analyzed": 0,
            "successful_merges": 0,
            "failed_merges": 0,
            "patterns_identified": [],
            "recommendations": [],
            "learning_history": []
        }
    
    def _load_patterns(self) -> Dict:
        """Load patterns database"""
        if COMMIT_PATTERNS_FILE.exists():
            with open(COMMIT_PATTERNS_FILE, 'r') as f:
                return json.load(f)
        return self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict:
        """Initialize patterns database"""
        return {
            "version": "1.0.0",
            "last_updated": None,
            "message_patterns": {},
            "size_patterns": {},
            "organization_patterns": {},
            "timing_patterns": {},
            "success_metrics": {
                "total_commits": 0,
                "successful_commits": 0,
                "failed_commits": 0
            }
        }
    
    def _save_strategies(self):
        """Save strategies database with proper error handling"""
        try:
            self.strategies_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
            
            # Write to temp file first, then rename (atomic operation)
            temp_file = COMMIT_STRATEGIES_FILE.with_suffix('.json.tmp')
            with open(temp_file, 'w') as f:
                json.dump(self.strategies_data, f, indent=2)
            temp_file.replace(COMMIT_STRATEGIES_FILE)
            
            self._log(f"Saved strategies to {COMMIT_STRATEGIES_FILE}")
        except Exception as e:
            self._log(f"Error saving strategies: {e}", "ERROR")
            raise
    
    def _save_patterns(self):
        """Save patterns database"""
        try:
            self.patterns_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
            
            temp_file = COMMIT_PATTERNS_FILE.with_suffix('.json.tmp')
            with open(temp_file, 'w') as f:
                json.dump(self.patterns_data, f, indent=2)
            temp_file.replace(COMMIT_PATTERNS_FILE)
            
            self._log(f"Saved patterns to {COMMIT_PATTERNS_FILE}")
        except Exception as e:
            self._log(f"Error saving patterns: {e}", "ERROR")
            raise
    
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
            self._log(f"Git command failed: {e}", "ERROR")
            return ""
    
    def _is_conventional_commit(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Check if commit follows conventional commit format.
        
        Returns (is_conventional, type)
        """
        conventional_pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9\-]+\))?: .+'
        match = re.match(conventional_pattern, message, re.IGNORECASE)
        if match:
            commit_type = match.group(1).lower()
            return True, commit_type
        return False, None
    
    def _analyze_commit_message(self, message: str) -> Dict[str, Any]:
        """Analyze commit message quality"""
        lines = message.split('\n')
        first_line = lines[0] if lines else ""
        has_body = len(lines) > 1 and any(line.strip() for line in lines[1:])
        
        is_conventional, conv_type = self._is_conventional_commit(first_line)
        
        return {
            "length": len(first_line),
            "has_body": has_body,
            "follows_conventional": is_conventional,
            "conventional_type": conv_type,
            "is_descriptive": len(first_line) >= MIN_MESSAGE_LENGTH,
            "is_concise": len(first_line) <= MAX_MESSAGE_LENGTH,
            "starts_with_verb": bool(re.match(r'^[A-Z][a-z]+', first_line))
        }
    
    def _get_commit_metrics(self, commit_hash: str) -> Optional[CommitMetrics]:
        """Extract comprehensive metrics from a commit"""
        try:
            # Get commit info
            commit_info = self._run_git_command([
                'show', '--format=%H%n%an%n%at%n%s%n%b', '--no-patch', commit_hash
            ])
            
            if not commit_info:
                return None
            
            lines = commit_info.split('\n')
            if len(lines) < 4:
                return None
            
            commit_hash = lines[0]
            author = lines[1]
            timestamp = datetime.fromtimestamp(int(lines[2]), tz=timezone.utc).isoformat()
            subject = lines[3]
            body = '\n'.join(lines[4:]).strip() if len(lines) > 4 else ""
            message = f"{subject}\n{body}".strip()
            
            # Analyze message
            msg_analysis = self._analyze_commit_message(message)
            
            # Get file changes
            stats = self._run_git_command([
                'show', '--stat', '--format=', commit_hash
            ])
            
            files_changed = 0
            lines_added = 0
            lines_deleted = 0
            file_types = set()
            
            if stats:
                for line in stats.split('\n'):
                    if '|' in line:
                        files_changed += 1
                        # Extract file extension
                        filename = line.split('|')[0].strip()
                        if '.' in filename:
                            ext = filename.split('.')[-1]
                            file_types.add(ext)
                    
                    # Parse summary line (e.g., "3 files changed, 100 insertions(+), 50 deletions(-)")
                    if 'changed' in line:
                        match = re.search(r'(\d+) insertion', line)
                        if match:
                            lines_added = int(match.group(1))
                        match = re.search(r'(\d+) deletion', line)
                        if match:
                            lines_deleted = int(match.group(1))
            
            return CommitMetrics(
                commit_hash=commit_hash,
                author=author,
                timestamp=timestamp,
                message=message,
                message_length=msg_analysis["length"],
                has_body=msg_analysis["has_body"],
                follows_conventional=msg_analysis["follows_conventional"],
                conventional_type=msg_analysis["conventional_type"],
                files_changed=files_changed,
                lines_added=lines_added,
                lines_deleted=lines_deleted,
                total_lines_changed=lines_added + lines_deleted,
                file_types=list(file_types)
            )
            
        except Exception as e:
            self._log(f"Error analyzing commit {commit_hash}: {e}", "ERROR")
            return None
    
    def _get_merge_info(self, commit_hash: str) -> Tuple[str, Optional[int], Optional[float]]:
        """
        Get merge status for a commit.
        
        Returns (status, pr_number, merge_time_hours)
        """
        # Check if commit is in a merged PR by looking at commit message
        commit_msg = self._run_git_command(['log', '-1', '--format=%B', commit_hash])
        
        # Look for PR merge patterns
        pr_match = re.search(r'#(\d+)', commit_msg)
        pr_number = int(pr_match.group(1)) if pr_match else None
        
        # Check if this is a merge commit
        parents = self._run_git_command(['log', '-1', '--format=%P', commit_hash])
        is_merge = len(parents.split()) > 1
        
        # For now, assume commits in main branch are successful
        branches = self._run_git_command(['branch', '--contains', commit_hash])
        if 'main' in branches or 'master' in branches:
            status = "success"
        else:
            status = "pending"
        
        # TODO: Calculate actual merge time by analyzing PR data
        merge_time_hours = None
        
        return status, pr_number, merge_time_hours
    
    def analyze_commits(self, since_days: int = 30, max_commits: int = 500) -> Dict[str, Any]:
        """
        Analyze recent commits to learn patterns.
        
        Args:
            since_days: Number of days of history to analyze
            max_commits: Maximum number of commits to analyze
            
        Returns:
            Analysis summary dictionary
        """
        self._log(f"Starting commit analysis (last {since_days} days, max {max_commits} commits)")
        
        # Get recent commits
        since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')
        commit_hashes = self._run_git_command([
            'log', '--format=%H', f'--since={since_date}', '--no-merges', f'-{max_commits}'
        ]).split('\n')
        
        commit_hashes = [h for h in commit_hashes if h.strip()]
        self._log(f"Found {len(commit_hashes)} commits to analyze")
        
        # Analyze each commit
        analyzed_commits = []
        successful_commits = []
        failed_commits = []
        
        for i, commit_hash in enumerate(commit_hashes):
            if i % 10 == 0:
                self._log(f"Progress: {i}/{len(commit_hashes)} commits analyzed")
            
            metrics = self._get_commit_metrics(commit_hash)
            if not metrics:
                continue
            
            # Get merge info
            status, pr_number, merge_time = self._get_merge_info(commit_hash)
            metrics.merge_status = status
            metrics.merge_pr_number = pr_number
            metrics.merge_time_hours = merge_time
            
            analyzed_commits.append(metrics)
            
            if status == "success":
                successful_commits.append(metrics)
            elif status == "failed":
                failed_commits.append(metrics)
        
        self._log(f"Analysis complete: {len(analyzed_commits)} commits analyzed")
        self._log(f"Successful: {len(successful_commits)}, Failed: {len(failed_commits)}")
        
        # Identify patterns
        patterns = self._identify_patterns(successful_commits, failed_commits)
        
        # Update databases
        self.strategies_data["total_commits_analyzed"] = len(analyzed_commits)
        self.strategies_data["successful_merges"] = len(successful_commits)
        self.strategies_data["failed_merges"] = len(failed_commits)
        self.strategies_data["patterns_identified"] = [p.to_dict() for p in patterns]
        
        # Record this analysis in learning history
        history_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commits_analyzed": len(analyzed_commits),
            "successful": len(successful_commits),
            "failed": len(failed_commits),
            "patterns_count": len(patterns),
            "since_days": since_days
        }
        
        if "learning_history" not in self.strategies_data:
            self.strategies_data["learning_history"] = []
        
        self.strategies_data["learning_history"].append(history_entry)
        
        # Keep only last 30 history entries
        if len(self.strategies_data["learning_history"]) > 30:
            self.strategies_data["learning_history"] = self.strategies_data["learning_history"][-30:]
        
        # Update patterns data
        self._update_pattern_database(analyzed_commits, patterns)
        
        # Save data
        self._save_strategies()
        self._save_patterns()
        
        return {
            "total_analyzed": len(analyzed_commits),
            "successful": len(successful_commits),
            "failed": len(failed_commits),
            "patterns_found": len(patterns),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _identify_patterns(
        self, 
        successful: List[CommitMetrics], 
        failed: List[CommitMetrics]
    ) -> List[CommitPattern]:
        """
        Identify patterns that correlate with successful merges.
        
        Uses statistical analysis to find meaningful patterns.
        """
        patterns = []
        
        if not successful:
            return patterns
        
        # Pattern 1: Conventional commit messages
        conv_success = sum(1 for c in successful if c.follows_conventional)
        conv_rate = conv_success / len(successful) if successful else 0
        
        if conv_rate > 0.5:  # More than 50% use conventional commits
            merge_times = [c.merge_time_hours for c in successful 
                          if c.follows_conventional and c.merge_time_hours is not None]
            avg_merge_time = mean(merge_times) if merge_times else 0.0
            
            patterns.append(CommitPattern(
                pattern_name="conventional_commits",
                pattern_type="message",
                description="Commits following conventional commit format",
                success_rate=conv_rate,
                occurrence_count=conv_success,
                average_merge_time_hours=avg_merge_time,
                common_attributes={
                    "format": "type(scope): description",
                    "most_common_types": self._get_common_types(successful)
                },
                examples=[c.commit_hash[:8] for c in successful 
                         if c.follows_conventional][:3],
                confidence_score=min(conv_rate * 1.2, 1.0)
            ))
        
        # Pattern 2: Optimal commit size
        ideal_size_commits = [c for c in successful 
                             if c.files_changed <= IDEAL_FILES_PER_COMMIT
                             and c.total_lines_changed <= IDEAL_LINES_CHANGED]
        
        if ideal_size_commits:
            size_rate = len(ideal_size_commits) / len(successful)
            merge_times = [c.merge_time_hours for c in ideal_size_commits 
                          if c.merge_time_hours is not None]
            avg_merge_time = mean(merge_times) if merge_times else 0.0
            
            patterns.append(CommitPattern(
                pattern_name="optimal_commit_size",
                pattern_type="size",
                description="Commits with focused changes (few files, moderate lines)",
                success_rate=size_rate,
                occurrence_count=len(ideal_size_commits),
                average_merge_time_hours=avg_merge_time,
                common_attributes={
                    "avg_files": mean([c.files_changed for c in ideal_size_commits]),
                    "avg_lines": mean([c.total_lines_changed for c in ideal_size_commits])
                },
                examples=[c.commit_hash[:8] for c in ideal_size_commits][:3],
                confidence_score=size_rate * 0.9
            ))
        
        # Pattern 3: Descriptive messages with body
        body_commits = [c for c in successful if c.has_body]
        if body_commits:
            body_rate = len(body_commits) / len(successful)
            merge_times = [c.merge_time_hours for c in body_commits 
                          if c.merge_time_hours is not None]
            avg_merge_time = mean(merge_times) if merge_times else 0.0
            
            patterns.append(CommitPattern(
                pattern_name="detailed_messages",
                pattern_type="message",
                description="Commits with detailed message body",
                success_rate=body_rate,
                occurrence_count=len(body_commits),
                average_merge_time_hours=avg_merge_time,
                common_attributes={
                    "has_explanation": True,
                    "avg_message_length": mean([c.message_length for c in body_commits])
                },
                examples=[c.commit_hash[:8] for c in body_commits][:3],
                confidence_score=body_rate * 0.85
            ))
        
        # Pattern 4: Single file type focus
        focused_commits = [c for c in successful if len(c.file_types) <= 2]
        if focused_commits:
            focus_rate = len(focused_commits) / len(successful)
            merge_times = [c.merge_time_hours for c in focused_commits 
                          if c.merge_time_hours is not None]
            avg_merge_time = mean(merge_times) if merge_times else 0.0
            
            patterns.append(CommitPattern(
                pattern_name="focused_changes",
                pattern_type="organization",
                description="Commits focused on single file type or related files",
                success_rate=focus_rate,
                occurrence_count=len(focused_commits),
                average_merge_time_hours=avg_merge_time,
                common_attributes={
                    "avg_file_types": mean([len(c.file_types) for c in focused_commits])
                },
                examples=[c.commit_hash[:8] for c in focused_commits][:3],
                confidence_score=focus_rate * 0.8
            ))
        
        return patterns
    
    def _get_common_types(self, commits: List[CommitMetrics]) -> List[str]:
        """Get most common conventional commit types"""
        types = [c.conventional_type for c in commits 
                if c.conventional_type]
        if not types:
            return []
        counter = Counter(types)
        return [t for t, _ in counter.most_common(5)]
    
    def _update_pattern_database(
        self, 
        commits: List[CommitMetrics], 
        patterns: List[CommitPattern]
    ):
        """Update the pattern database with new findings"""
        # Update success metrics
        self.patterns_data["success_metrics"]["total_commits"] = len(commits)
        self.patterns_data["success_metrics"]["successful_commits"] = sum(
            1 for c in commits if c.merge_status == "success"
        )
        self.patterns_data["success_metrics"]["failed_commits"] = sum(
            1 for c in commits if c.merge_status == "failed"
        )
        
        # Store patterns by type
        for pattern in patterns:
            pattern_dict = pattern.to_dict()
            pattern_type = pattern.pattern_type
            
            if pattern_type not in self.patterns_data:
                self.patterns_data[pattern_type] = {}
            
            self.patterns_data[pattern_type][pattern.pattern_name] = pattern_dict
    
    def generate_recommendations(
        self, 
        context: str = "general",
        min_confidence: float = 0.7
    ) -> List[StrategyRecommendation]:
        """
        Generate actionable commit strategy recommendations.
        
        Args:
            context: Context for recommendations (feature, bugfix, refactor, docs, general)
            min_confidence: Minimum confidence score for recommendations
            
        Returns:
            List of recommendations sorted by confidence
        """
        self._log(f"Generating recommendations for context: {context}")
        
        recommendations = []
        patterns = [CommitPattern(**p) for p in self.strategies_data.get("patterns_identified", [])]
        
        # Filter patterns by confidence
        high_confidence_patterns = [p for p in patterns if p.confidence_score >= min_confidence]
        
        self._log(f"Found {len(high_confidence_patterns)} high-confidence patterns")
        
        # Generate recommendations based on patterns
        for pattern in high_confidence_patterns:
            rec = self._pattern_to_recommendation(pattern, context)
            if rec:
                recommendations.append(rec)
        
        # Sort by confidence
        recommendations.sort(key=lambda r: r.confidence_score, reverse=True)
        
        # Store recommendations
        self.strategies_data["recommendations"] = [r.to_dict() for r in recommendations]
        self._save_strategies()
        
        return recommendations
    
    def _pattern_to_recommendation(
        self, 
        pattern: CommitPattern, 
        context: str
    ) -> Optional[StrategyRecommendation]:
        """Convert a pattern into an actionable recommendation"""
        
        # Map patterns to recommendations
        if pattern.pattern_name == "conventional_commits":
            return StrategyRecommendation(
                recommendation_id=f"rec_{pattern.pattern_name}_{context}",
                title="Use Conventional Commit Format",
                description=(
                    "Follow the conventional commit format: type(scope): description. "
                    f"This pattern shows {pattern.success_rate:.1%} success rate."
                ),
                rationale=(
                    f"Analysis of {pattern.occurrence_count} successful commits shows that "
                    "conventional commit format correlates with faster merges and fewer issues."
                ),
                expected_improvement=f"{pattern.success_rate:.1%} success rate",
                confidence_score=pattern.confidence_score,
                applicable_contexts=["general", "feature", "bugfix", "refactor", "docs"],
                supporting_patterns=[pattern.pattern_name],
                example_commits=pattern.examples
            )
        
        elif pattern.pattern_name == "optimal_commit_size":
            avg_files = pattern.common_attributes.get("avg_files", 5)
            avg_lines = pattern.common_attributes.get("avg_lines", 100)
            
            return StrategyRecommendation(
                recommendation_id=f"rec_{pattern.pattern_name}_{context}",
                title="Keep Commits Focused and Sized Appropriately",
                description=(
                    f"Aim for ~{avg_files:.0f} files and ~{avg_lines:.0f} lines per commit. "
                    f"This pattern shows {pattern.success_rate:.1%} success rate."
                ),
                rationale=(
                    "Smaller, focused commits are easier to review, test, and merge. "
                    f"They have {pattern.success_rate:.1%} success rate in this repository."
                ),
                expected_improvement=f"{pattern.success_rate:.1%} success rate",
                confidence_score=pattern.confidence_score,
                applicable_contexts=["general", "feature", "bugfix", "refactor"],
                supporting_patterns=[pattern.pattern_name],
                example_commits=pattern.examples
            )
        
        elif pattern.pattern_name == "detailed_messages":
            return StrategyRecommendation(
                recommendation_id=f"rec_{pattern.pattern_name}_{context}",
                title="Write Detailed Commit Messages",
                description=(
                    "Include a message body explaining why changes were made. "
                    f"This pattern shows {pattern.success_rate:.1%} success rate."
                ),
                rationale=(
                    "Detailed messages help reviewers understand context and intent. "
                    f"{pattern.occurrence_count} successful commits used this approach."
                ),
                expected_improvement=f"{pattern.success_rate:.1%} success rate",
                confidence_score=pattern.confidence_score,
                applicable_contexts=["general", "feature", "bugfix", "refactor"],
                supporting_patterns=[pattern.pattern_name],
                example_commits=pattern.examples
            )
        
        elif pattern.pattern_name == "focused_changes":
            return StrategyRecommendation(
                recommendation_id=f"rec_{pattern.pattern_name}_{context}",
                title="Focus Commits on Related Files",
                description=(
                    "Keep commits focused on a single concern or file type. "
                    f"This pattern shows {pattern.success_rate:.1%} success rate."
                ),
                rationale=(
                    "Focused commits are easier to understand and review. "
                    "Mixing unrelated changes increases complexity and review time."
                ),
                expected_improvement=f"{pattern.success_rate:.1%} success rate",
                confidence_score=pattern.confidence_score,
                applicable_contexts=["general", "feature", "refactor"],
                supporting_patterns=[pattern.pattern_name],
                example_commits=pattern.examples
            )
        
        return None
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a comprehensive report of learned strategies.
        
        Args:
            output_file: Optional file path to save report
            
        Returns:
            Report text
        """
        self._log("Generating comprehensive report")
        
        report_lines = [
            "# Git Commit Strategy Learning Report",
            "",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Repository: {self.strategies_data['repository']}",
            "",
            "## Summary",
            "",
            f"- Total commits analyzed: {self.strategies_data['total_commits_analyzed']}",
            f"- Successful merges: {self.strategies_data['successful_merges']}",
            f"- Failed merges: {self.strategies_data['failed_merges']}",
            f"- Patterns identified: {len(self.strategies_data['patterns_identified'])}",
            "",
            "## Identified Patterns",
            ""
        ]
        
        # Add patterns
        for pattern_dict in self.strategies_data['patterns_identified']:
            pattern = CommitPattern(**pattern_dict)
            report_lines.extend([
                f"### {pattern.pattern_name.replace('_', ' ').title()}",
                "",
                f"**Type:** {pattern.pattern_type}",
                f"**Success Rate:** {pattern.success_rate:.1%}",
                f"**Occurrences:** {pattern.occurrence_count}",
                f"**Confidence:** {pattern.confidence_score:.1%}",
                "",
                f"**Description:** {pattern.description}",
                "",
                "**Common Attributes:**",
                ""
            ])
            
            for key, value in pattern.common_attributes.items():
                report_lines.append(f"- {key}: {value}")
            
            report_lines.extend(["", "---", ""])
        
        # Add recommendations
        report_lines.extend([
            "## Recommendations",
            ""
        ])
        
        recommendations = self.generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report_lines.extend([
                f"### {i}. {rec.title}",
                "",
                f"**Confidence:** {rec.confidence_score:.1%}",
                f"**Context:** {', '.join(rec.applicable_contexts)}",
                f"**Trend:** {rec.trend}",
                "",
                rec.description,
                "",
                f"**Rationale:** {rec.rationale}",
                "",
                f"**Expected Improvement:** {rec.expected_improvement}",
                "",
                "---",
                ""
            ])
        
        report_text = '\n'.join(report_lines)
        
        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_text)
            self._log(f"Report saved to {output_file}")
        
        return report_text
    
    def validate_commit(
        self, 
        message: str, 
        files_changed: int = 0, 
        lines_changed: int = 0,
        file_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a commit against learned optimal strategies.
        
        This method enables pre-commit hooks or CI validation to check
        if a commit follows the learned patterns for successful merges.
        
        Args:
            message: The commit message to validate
            files_changed: Number of files in the commit
            lines_changed: Total lines added/deleted
            file_types: List of file extensions being changed
            
        Returns:
            Dictionary with validation result and suggestions
        """
        # Sanitize message for logging (remove control characters)
        safe_msg = ''.join(c if c.isprintable() or c.isspace() else '?' for c in message[:50])
        self._log(f"Validating commit message: {safe_msg}...")
        
        file_types = file_types or []
        issues: List[Dict[str, Any]] = []
        suggestions: List[str] = []
        score = 100  # Start with perfect score
        
        # Analyze the message
        msg_analysis = self._analyze_commit_message(message)
        
        # Check conventional commit format
        if not msg_analysis["follows_conventional"]:
            issues.append({
                "type": "message_format",
                "severity": "warning",
                "message": "Commit message doesn't follow conventional format (type: description)",
                "suggestion": "Use format like: feat: add feature, fix: correct bug, docs: update readme"
            })
            score -= 15
            suggestions.append("Consider using conventional commit format: type(scope): description")
        
        # Check message length
        if not msg_analysis["is_descriptive"]:
            issues.append({
                "type": "message_length",
                "severity": "warning",
                "message": f"Commit message is too short ({msg_analysis['length']} chars)",
                "suggestion": f"Aim for at least {MIN_MESSAGE_LENGTH} characters for clarity"
            })
            score -= 10
            suggestions.append(f"Add more detail to your commit message (current: {msg_analysis['length']} chars)")
        
        if not msg_analysis["is_concise"]:
            issues.append({
                "type": "message_length", 
                "severity": "info",
                "message": f"First line is long ({msg_analysis['length']} chars)",
                "suggestion": f"Keep first line under {MAX_MESSAGE_LENGTH} characters"
            })
            score -= 5
        
        # Check for body in complex commits
        if files_changed > 5 and not msg_analysis["has_body"]:
            issues.append({
                "type": "missing_body",
                "severity": "suggestion",
                "message": "Large commit lacks detailed explanation",
                "suggestion": "Add a body explaining the changes when modifying many files"
            })
            score -= 10
            suggestions.append("Add a commit body explaining why these changes were made")
        
        # Check commit size
        if files_changed > MAX_FILES_PER_COMMIT:
            issues.append({
                "type": "commit_size",
                "severity": "warning",
                "message": f"Commit changes {files_changed} files (recommended: <{MAX_FILES_PER_COMMIT})",
                "suggestion": "Consider breaking into smaller, focused commits"
            })
            score -= 20
            suggestions.append(f"Consider splitting into smaller commits (~{IDEAL_FILES_PER_COMMIT} files each)")
        elif files_changed > IDEAL_FILES_PER_COMMIT:
            issues.append({
                "type": "commit_size",
                "severity": "info",
                "message": f"Commit changes {files_changed} files (optimal: ~{IDEAL_FILES_PER_COMMIT})",
                "suggestion": "Smaller commits are easier to review"
            })
            score -= 5
        
        # Check lines changed
        if lines_changed > MAX_LINES_CHANGED:
            issues.append({
                "type": "lines_changed",
                "severity": "warning",
                "message": f"Commit changes {lines_changed} lines (recommended: <{MAX_LINES_CHANGED})",
                "suggestion": "Large changes are harder to review"
            })
            score -= 15
        elif lines_changed > IDEAL_LINES_CHANGED:
            issues.append({
                "type": "lines_changed",
                "severity": "info",
                "message": f"Commit changes {lines_changed} lines (optimal: ~{IDEAL_LINES_CHANGED})",
                "suggestion": "Consider if this can be broken down"
            })
            score -= 5
        
        # Check file type focus
        if file_types and len(file_types) > 3:
            issues.append({
                "type": "file_focus",
                "severity": "info",
                "message": f"Commit touches {len(file_types)} different file types",
                "suggestion": "Keep commits focused on related changes"
            })
            score -= 5
            suggestions.append("Consider separating unrelated changes into different commits")
        
        # Determine overall status (ensure score is within 0-100 range)
        score = min(100, max(0, score))
        
        if score >= 90:
            status = "excellent"
            status_emoji = "✅"
        elif score >= 70:
            status = "good"
            status_emoji = "👍"
        elif score >= 50:
            status = "acceptable"
            status_emoji = "⚠️"
        else:
            status = "needs_improvement"
            status_emoji = "❌"
        
        # Get patterns for context
        patterns = self.strategies_data.get("patterns_identified", [])
        applicable_patterns = []
        for pattern in patterns:
            if isinstance(pattern, dict):
                applicable_patterns.append({
                    "name": pattern.get("pattern_name", "unknown"),
                    "success_rate": pattern.get("success_rate", 0),
                    "confidence": pattern.get("confidence_score", 0)
                })
        
        return {
            "status": status,
            "status_emoji": status_emoji,
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
            "message_analysis": msg_analysis,
            "commit_metrics": {
                "files_changed": files_changed,
                "lines_changed": lines_changed,
                "file_types": file_types
            },
            "applicable_patterns": applicable_patterns,
            "validated_at": datetime.now(timezone.utc).isoformat()
        }

    def analyze_trends(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Analyze trends in commit patterns over time.
        
        Args:
            period_days: Number of days to analyze for trends
            
        Returns:
            Dictionary containing trend analysis
        """
        self._log(f"Analyzing trends over last {period_days} days")
        
        history = self.strategies_data.get("learning_history", [])
        
        if len(history) < 2:
            self._log("Not enough history for trend analysis")
            return {
                "status": "insufficient_data",
                "message": "Need at least 2 historical data points",
                "history_count": len(history)
            }
        
        # Calculate trends
        trends = {
            "success_rate": self._calculate_trend([
                h["successful"] / max(h["commits_analyzed"], 1) 
                for h in history if h["commits_analyzed"] > 0
            ]),
            "patterns_discovered": self._calculate_trend([
                h["patterns_count"] for h in history
            ]),
            "commit_quality": self._calculate_trend([
                1.0 - (h["failed"] / max(h["commits_analyzed"], 1))
                for h in history if h["commits_analyzed"] > 0
            ])
        }
        
        # Determine overall trend using constants
        improving_count = sum(1 for t in trends.values() if t["direction"] == TREND_IMPROVING)
        declining_count = sum(1 for t in trends.values() if t["direction"] == TREND_DECLINING)
        
        if improving_count > declining_count:
            overall = TREND_IMPROVING
        elif declining_count > improving_count:
            overall = TREND_DECLINING
        else:
            overall = TREND_STABLE
        
        return {
            "status": "success",
            "overall_trend": overall,
            "trends": trends,
            "history_analyzed": len(history),
            "period_days": period_days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """
        Calculate trend direction from a series of values.
        
        Returns:
            Dictionary with direction, velocity, and confidence
        """
        if len(values) < 2:
            return {"direction": TREND_UNKNOWN, "velocity": 0.0, "confidence": 0.0}
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        
        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        # Calculate slope (velocity)
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            velocity = 0.0
        else:
            velocity = numerator / denominator
        
        # Determine direction using constants
        if abs(velocity) < 0.01:
            direction = TREND_STABLE
        elif velocity > 0:
            direction = TREND_IMPROVING
        else:
            direction = TREND_DECLINING
        
        # Calculate confidence based on variance
        if len(values) > 2:
            try:
                variance = stdev(values)
                confidence = min(abs(velocity) / max(variance, 0.01), 1.0)
            except Exception:
                # Handle case where all values are identical
                confidence = 0.5
        else:
            confidence = 0.5
        
        return {
            "direction": direction,
            "velocity": velocity,
            "confidence": confidence,
            "sample_size": n
        }


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Git Commit Strategy Learning System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze recent commits
  python commit-strategy-learner.py --analyze
  
  # Analyze last 60 days
  python commit-strategy-learner.py --analyze --since 60
  
  # Generate recommendations for feature development
  python commit-strategy-learner.py --recommend --context feature
  
  # Generate full report
  python commit-strategy-learner.py --report --output analysis/commit_report.md
  
  # Analyze trends over time
  python commit-strategy-learner.py --trends --period 30
  
  # Validate a commit message
  python commit-strategy-learner.py --validate "feat: add new feature"
  
  # Validate with file info
  python commit-strategy-learner.py --validate "fix: bug fix" --files 3 --lines 50
        """
    )
    
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze commits and learn patterns')
    parser.add_argument('--since', type=int, default=30,
                       help='Days of history to analyze (default: 30)')
    parser.add_argument('--max-commits', type=int, default=500,
                       help='Maximum commits to analyze (default: 500)')
    
    parser.add_argument('--recommend', action='store_true',
                       help='Generate recommendations')
    parser.add_argument('--context', type=str, default='general',
                       choices=['general', 'feature', 'bugfix', 'refactor', 'docs'],
                       help='Context for recommendations')
    parser.add_argument('--min-confidence', type=float, default=0.7,
                       help='Minimum confidence for recommendations (default: 0.7)')
    
    parser.add_argument('--report', action='store_true',
                       help='Generate comprehensive report')
    parser.add_argument('--output', type=str,
                       help='Output file for report')
    
    parser.add_argument('--trends', action='store_true',
                       help='Analyze trends in learning history')
    parser.add_argument('--period', type=int, default=30,
                       help='Period in days for trend analysis (default: 30)')
    
    parser.add_argument('--validate', type=str, metavar='MESSAGE',
                       help='Validate a commit message against learned strategies')
    parser.add_argument('--files', type=int, default=0,
                       help='Number of files changed (for validation)')
    parser.add_argument('--lines', type=int, default=0,
                       help='Number of lines changed (for validation)')
    parser.add_argument('--json', action='store_true',
                       help='Output validation result as JSON')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Create learner instance
    learner = CommitStrategyLearner(verbose=args.verbose)
    
    try:
        if args.analyze:
            print("🔍 Analyzing commit patterns...")
            result = learner.analyze_commits(
                since_days=args.since,
                max_commits=args.max_commits
            )
            print(f"✅ Analysis complete!")
            print(f"   Commits analyzed: {result['total_analyzed']}")
            print(f"   Successful: {result['successful']}")
            print(f"   Failed: {result['failed']}")
            print(f"   Patterns found: {result['patterns_found']}")
        
        elif args.recommend:
            print(f"💡 Generating recommendations for context: {args.context}")
            recommendations = learner.generate_recommendations(
                context=args.context,
                min_confidence=args.min_confidence
            )
            
            if not recommendations:
                print("⚠️  No high-confidence recommendations available.")
                print("   Try running --analyze first to learn patterns.")
                return 1
            
            print(f"✅ Generated {len(recommendations)} recommendations:")
            print()
            
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec.title}")
                print(f"   Confidence: {rec.confidence_score:.1%}")
                print(f"   Trend: {rec.trend}")
                print(f"   {rec.description}")
                print()
        
        elif args.report:
            print("📊 Generating comprehensive report...")
            report = learner.generate_report(output_file=args.output)
            
            if args.output:
                print(f"✅ Report saved to {args.output}")
            else:
                print(report)
        
        elif args.trends:
            print(f"📈 Analyzing trends over {args.period} days...")
            trends = learner.analyze_trends(period_days=args.period)
            
            if trends["status"] == "insufficient_data":
                print(f"⚠️  {trends['message']}")
                print(f"   History count: {trends['history_count']}")
                print("   Run --analyze multiple times to build history")
                return 1
            
            print(f"✅ Trend Analysis Complete!")
            print(f"   Overall Trend: {trends['overall_trend'].upper()}")
            print(f"   History Points: {trends['history_analyzed']}")
            print()
            print("📊 Detailed Trends:")
            
            for metric, data in trends["trends"].items():
                direction = data["direction"]
                emoji = "📈" if direction == "improving" else "📉" if direction == "declining" else "➡️"
                print(f"   {emoji} {metric.replace('_', ' ').title()}: {direction}")
                print(f"      Velocity: {data['velocity']:.4f}")
                print(f"      Confidence: {data['confidence']:.1%}")
                print()
        
        elif args.validate:
            result = learner.validate_commit(
                message=args.validate,
                files_changed=args.files,
                lines_changed=args.lines
            )
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"{result['status_emoji']} Commit Validation: {result['status'].upper()}")
                print(f"   Score: {result['score']}/100")
                print()
                
                if result['issues']:
                    print("📋 Issues Found:")
                    for issue in result['issues']:
                        severity_emoji = "⚠️" if issue['severity'] == 'warning' else "ℹ️" if issue['severity'] == 'info' else "💡"
                        print(f"   {severity_emoji} [{issue['severity'].upper()}] {issue['message']}")
                        print(f"      → {issue['suggestion']}")
                    print()
                
                if result['suggestions']:
                    print("💡 Suggestions:")
                    for suggestion in result['suggestions']:
                        print(f"   • {suggestion}")
                    print()
                
                if result['applicable_patterns']:
                    print("📊 Based on Learned Patterns:")
                    for pattern in result['applicable_patterns']:
                        print(f"   • {pattern['name']}: {pattern['success_rate']:.1%} success rate")
            
            # Return exit code based on validation status
            return 0 if result['status'] in ['excellent', 'good'] else 1
        
        else:
            parser.print_help()
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
