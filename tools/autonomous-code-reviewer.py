#!/usr/bin/env python3
"""
Autonomous Code Reviewer - Self-Improving Review System

An intelligent code review system that evolves its criteria based on outcomes.
Learns from successful merges, failed reviews, and manual feedback to continuously
improve review quality.

Architecture:
- Dynamic criteria storage with versioning
- Learning from PR outcomes (merge success/failure)
- Pattern recognition for common code issues
- Adaptive thresholds based on historical data
- Integration with existing agent system

Features:
- Multi-dimensional code quality assessment
- Self-improving review criteria
- Pattern-based issue detection
- Feedback incorporation mechanism
- Performance metrics tracking

Usage:
    python autonomous-code-reviewer.py --review PR_NUMBER
    python autonomous-code-reviewer.py --learn-from-outcome PR_NUMBER --outcome merged
    python autonomous-code-reviewer.py --update-criteria
    python autonomous-code-reviewer.py --show-stats

Author: @create-botter (Infrastructure creation specialist)
"""

import json
import os
import sys
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import argparse

# Constants
LEARNINGS_DIR = Path("learnings")
REVIEW_CRITERIA_FILE = LEARNINGS_DIR / "review_criteria.json"
REVIEW_HISTORY_DIR = LEARNINGS_DIR / "review_history"
REPO_OWNER = os.environ.get('GITHUB_REPOSITORY_OWNER', 'enufacas')
REPO_NAME = os.environ.get('GITHUB_REPOSITORY', 'enufacas/Chained').split('/')[-1]


@dataclass
class ReviewCriteria:
    """Review criteria that evolve over time"""
    name: str
    description: str
    weight: float  # 0.0 to 1.0
    threshold: float  # Minimum score to pass
    patterns: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)
    success_rate: float = 0.0  # Track how predictive this criterion is
    total_evaluations: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewResult:
    """Result of a code review"""
    pr_number: int
    timestamp: str
    overall_score: float
    criteria_scores: Dict[str, float]
    issues_found: List[Dict[str, Any]]
    suggestions: List[str]
    pass_threshold: float
    passed: bool
    reviewer_version: str
    confidence: float = 0.5  # Confidence in the prediction (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewOutcome:
    """Outcome of a reviewed PR (for learning)"""
    pr_number: int
    review_score: float
    outcome: str  # merged, rejected, revised, abandoned
    outcome_timestamp: str
    manual_feedback: Optional[Dict[str, Any]] = None
    criteria_accuracy: Dict[str, bool] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutonomousCodeReviewer:
    """Main autonomous code reviewer with self-improving capabilities"""
    
    VERSION = "1.0.0"
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.criteria: List[ReviewCriteria] = []
        self.history: List[ReviewOutcome] = []
        
        # Ensure directories exist
        LEARNINGS_DIR.mkdir(exist_ok=True)
        REVIEW_HISTORY_DIR.mkdir(exist_ok=True)
        
        # Load or initialize criteria
        self._load_or_initialize_criteria()
        self._load_history()
    
    def _log(self, message: str):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(f"[AutonomousReviewer] {message}", file=sys.stderr)
    
    def _load_or_initialize_criteria(self):
        """Load existing criteria or initialize with defaults"""
        if REVIEW_CRITERIA_FILE.exists():
            try:
                with open(REVIEW_CRITERIA_FILE, 'r') as f:
                    data = json.load(f)
                    self.criteria = [
                        ReviewCriteria(**c) for c in data.get('criteria', [])
                    ]
                self._log(f"Loaded {len(self.criteria)} review criteria")
            except Exception as e:
                self._log(f"Error loading criteria: {e}")
                self._initialize_default_criteria()
        else:
            self._initialize_default_criteria()
    
    def _initialize_default_criteria(self):
        """Initialize with sensible default criteria"""
        self.criteria = [
            ReviewCriteria(
                name="code_complexity",
                description="Measures code complexity and maintainability",
                weight=0.25,
                threshold=0.6,
                patterns=[
                    r"def \w+\([^)]*\):",  # Function definitions
                    r"class \w+",  # Class definitions
                ],
                anti_patterns=[
                    r"def \w+\([^)]{100,}\):",  # Very long parameter lists
                    r"if.*if.*if.*if",  # Deep nesting
                    r"for.*for.*for.*for",  # Deep loop nesting
                ],
                success_rate=0.7,
                total_evaluations=0
            ),
            ReviewCriteria(
                name="code_style",
                description="Checks for consistent code style and formatting",
                weight=0.15,
                threshold=0.7,
                patterns=[
                    r"^import \w+$",  # Clean imports
                    r"^from \w+ import",
                ],
                anti_patterns=[
                    r"import \*",  # Wildcard imports
                    r"^\+\t",  # Tab characters (prefer spaces)
                ],
                success_rate=0.8,
                total_evaluations=0
            ),
            ReviewCriteria(
                name="documentation",
                description="Ensures adequate documentation and comments",
                weight=0.20,
                threshold=0.5,
                patterns=[
                    r'""".*?"""',  # Docstrings
                    r"#\s+\w+",  # Comments
                    r"^def \w+\([^)]*\):\s*\n\s*\"\"\"",  # Documented functions
                ],
                anti_patterns=[
                    r"TODO|FIXME|XXX",  # Unresolved todos
                    r"#\s*noqa",  # Excessive linting disables
                ],
                success_rate=0.75,
                total_evaluations=0
            ),
            ReviewCriteria(
                name="test_coverage",
                description="Checks for adequate test coverage",
                weight=0.20,
                threshold=0.6,
                patterns=[
                    r"def test_\w+",  # Test functions
                    r"class Test\w+",  # Test classes
                    r"assert\s+",  # Assertions
                    r"@pytest\.mark",  # Pytest markers
                ],
                anti_patterns=[
                    r"pass\s*#.*test",  # Empty test placeholders
                    r"assert True",  # Meaningless assertions
                ],
                success_rate=0.85,
                total_evaluations=0
            ),
            ReviewCriteria(
                name="security",
                description="Identifies potential security issues",
                weight=0.20,
                threshold=0.8,
                patterns=[
                    r"os\.environ\.get\(",  # Safe env var access
                    r"secrets\.",  # Use of secrets module
                ],
                anti_patterns=[
                    r"eval\(",  # Dangerous eval
                    r"exec\(",  # Dangerous exec
                    r"os\.system\(",  # Dangerous system calls
                    r"subprocess\.call\(.+shell=True",  # Shell injection risk
                    r"pickle\.loads?\(",  # Unsafe pickle
                    r"yaml\.load\([^)]*(?!Loader=yaml\.SafeLoader)",  # Unsafe YAML
                ],
                success_rate=0.9,
                total_evaluations=0
            ),
        ]
        self._save_criteria()
        self._log(f"Initialized {len(self.criteria)} default criteria")
    
    def _save_criteria(self):
        """Save current criteria to disk"""
        try:
            data = {
                'version': self.VERSION,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'criteria': [c.to_dict() for c in self.criteria]
            }
            with open(REVIEW_CRITERIA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            self._log("Criteria saved successfully")
        except Exception as e:
            self._log(f"Error saving criteria: {e}")
    
    def _load_history(self):
        """Load review history for learning"""
        self.history = []
        if REVIEW_HISTORY_DIR.exists():
            for history_file in REVIEW_HISTORY_DIR.glob("outcome_*.json"):
                try:
                    with open(history_file, 'r') as f:
                        data = json.load(f)
                        self.history.append(ReviewOutcome(**data))
                except Exception as e:
                    self._log(f"Error loading history from {history_file}: {e}")
        self._log(f"Loaded {len(self.history)} historical outcomes")
    
    def review_pr(self, pr_number: int, pr_data: Optional[Dict[str, Any]] = None) -> ReviewResult:
        """
        Perform autonomous code review on a PR
        
        Args:
            pr_number: PR number to review
            pr_data: Optional PR data (if not provided, will fetch from GitHub)
        
        Returns:
            ReviewResult with scores and recommendations
        """
        self._log(f"Reviewing PR #{pr_number}")
        
        # In a full implementation, would fetch PR data from GitHub API
        # For now, simulate with basic analysis
        if pr_data is None:
            pr_data = self._fetch_pr_data(pr_number)
        
        # Evaluate against each criterion
        criteria_scores = {}
        all_issues = []
        all_suggestions = []
        
        for criterion in self.criteria:
            score, issues, suggestions = self._evaluate_criterion(
                criterion, pr_data
            )
            criteria_scores[criterion.name] = score
            all_issues.extend(issues)
            all_suggestions.extend(suggestions)
        
        # Calculate overall weighted score
        overall_score = sum(
            criteria_scores.get(c.name, 0) * c.weight 
            for c in self.criteria
        )
        
        # Calculate confidence based on historical accuracy and data amount
        confidence = self._calculate_confidence()
        
        # Determine pass/fail (can be adaptive based on confidence)
        pass_threshold = 0.7
        # Adjust threshold based on confidence (if low confidence, be more conservative)
        if confidence < 0.5:
            pass_threshold = 0.75  # Stricter when uncertain
        
        passed = overall_score >= pass_threshold
        
        result = ReviewResult(
            pr_number=pr_number,
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            issues_found=all_issues,
            suggestions=all_suggestions,
            pass_threshold=pass_threshold,
            passed=passed,
            reviewer_version=self.VERSION,
            confidence=confidence
        )
        
        # Save review result
        self._save_review_result(result)
        
        return result
    
    def _calculate_confidence(self) -> float:
        """
        Calculate confidence in review predictions based on:
        1. Amount of historical data
        2. Accuracy of past predictions
        3. Consistency of criteria
        """
        # Base confidence increases with more data
        data_confidence = min(1.0, len(self.history) / 50)  # Max confidence at 50+ reviews
        
        # Average accuracy of criteria
        if len(self.criteria) > 0:
            avg_accuracy = sum(c.success_rate for c in self.criteria) / len(self.criteria)
            accuracy_confidence = avg_accuracy
        else:
            accuracy_confidence = 0.5
        
        # Check consistency (variance in success rates)
        if len(self.criteria) > 1:
            success_rates = [c.success_rate for c in self.criteria]
            variance = sum((sr - avg_accuracy) ** 2 for sr in success_rates) / len(success_rates)
            consistency_confidence = 1.0 - min(1.0, variance * 2)  # Lower variance = higher confidence
        else:
            consistency_confidence = 0.5
        
        # Weighted combination
        confidence = (
            data_confidence * 0.4 +
            accuracy_confidence * 0.4 +
            consistency_confidence * 0.2
        )
        
        return confidence
    
    def _fetch_pr_data(self, pr_number: int) -> Dict[str, Any]:
        """Fetch PR data from GitHub using gh CLI"""
        self._log(f"Fetching PR data for #{pr_number}")
        
        try:
            # Use gh CLI to fetch PR data (more reliable than API in GitHub Actions)
            # Get PR details
            pr_info_cmd = [
                'gh', 'pr', 'view', str(pr_number),
                '--json', 'title,body,files,additions,deletions,changedFiles'
            ]
            pr_info_result = subprocess.run(
                pr_info_cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            pr_info = json.loads(pr_info_result.stdout)
            
            # Get PR diff
            diff_cmd = ['gh', 'pr', 'diff', str(pr_number)]
            diff_result = subprocess.run(
                diff_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'number': pr_number,
                'title': pr_info.get('title', ''),
                'body': pr_info.get('body', ''),
                'files': pr_info.get('files', []),
                'additions': pr_info.get('additions', 0),
                'deletions': pr_info.get('deletions', 0),
                'changed_files': pr_info.get('changedFiles', 0),
                'diff': diff_result.stdout
            }
        except subprocess.CalledProcessError as e:
            self._log(f"Error fetching PR data: {e}")
            self._log(f"stderr: {e.stderr}")
            # Return minimal data if fetch fails
            return {
                'number': pr_number,
                'title': f'PR #{pr_number}',
                'body': '',
                'files': [],
                'additions': 0,
                'deletions': 0,
                'changed_files': 0,
                'diff': ''
            }
        except Exception as e:
            self._log(f"Unexpected error fetching PR data: {e}")
            return {
                'number': pr_number,
                'title': f'PR #{pr_number}',
                'body': '',
                'files': [],
                'additions': 0,
                'deletions': 0,
                'changed_files': 0,
                'diff': ''
            }
    
    def _evaluate_criterion(
        self, 
        criterion: ReviewCriteria, 
        pr_data: Dict[str, Any]
    ) -> Tuple[float, List[Dict[str, Any]], List[str]]:
        """
        Evaluate PR against a single criterion
        
        Returns:
            (score, issues, suggestions)
        """
        issues = []
        suggestions = []
        
        # Extract PR content for analysis
        pr_diff = pr_data.get('diff', '')
        pr_title = pr_data.get('title', '')
        pr_body = pr_data.get('body', '')
        files = pr_data.get('files', [])
        
        # Pattern matching on actual diff
        pattern_matches = 0
        anti_pattern_matches = 0
        
        # Count pattern occurrences
        for pattern in criterion.patterns:
            try:
                matches = re.findall(pattern, pr_diff, re.MULTILINE)
                pattern_matches += len(matches)
            except re.error as e:
                self._log(f"Invalid pattern {pattern}: {e}")
        
        # Detect anti-patterns and create issues
        for anti_pattern in criterion.anti_patterns:
            try:
                matches = re.finditer(anti_pattern, pr_diff, re.MULTILINE)
                for match in matches:
                    anti_pattern_matches += 1
                    # Extract context around match
                    start = max(0, match.start() - 50)
                    end = min(len(pr_diff), match.end() + 50)
                    context = pr_diff[start:end]
                    
                    issues.append({
                        'criterion': criterion.name,
                        'severity': 'warning',
                        'message': f'Anti-pattern detected in diff',
                        'pattern': anti_pattern,
                        'context': context[:100]  # Limit context size
                    })
            except re.error as e:
                self._log(f"Invalid anti-pattern {anti_pattern}: {e}")
        
        # Enhanced scoring based on criterion type
        if criterion.name == 'code_complexity':
            score = self._evaluate_complexity(pr_data, pattern_matches, anti_pattern_matches)
        elif criterion.name == 'code_style':
            score = self._evaluate_style(pr_data, pattern_matches, anti_pattern_matches)
        elif criterion.name == 'documentation':
            score = self._evaluate_documentation(pr_data, pattern_matches, anti_pattern_matches)
        elif criterion.name == 'test_coverage':
            score = self._evaluate_test_coverage(pr_data, pattern_matches, anti_pattern_matches)
        elif criterion.name == 'security':
            score = self._evaluate_security(pr_data, pattern_matches, anti_pattern_matches)
        else:
            # Default scoring
            if len(criterion.patterns) > 0:
                base_score = min(1.0, pattern_matches / (len(criterion.patterns) * 2))
            else:
                base_score = 0.8
            
            penalty = min(0.5, anti_pattern_matches * 0.15)
            score = max(0.0, min(1.0, base_score - penalty))
        
        # Generate suggestions if score is low
        if score < criterion.threshold:
            suggestions.append(
                f"Improve {criterion.name}: {criterion.description} (score: {score:.2f}, threshold: {criterion.threshold:.2f})"
            )
        
        return score, issues, suggestions
    
    def _evaluate_complexity(self, pr_data: Dict[str, Any], good_patterns: int, bad_patterns: int) -> float:
        """Evaluate code complexity"""
        diff = pr_data.get('diff', '')
        
        # Check for deep nesting
        max_indent = 0
        for line in diff.split('\n'):
            if line.startswith('+'):
                indent = len(line) - len(line.lstrip(' '))
                max_indent = max(max_indent, indent)
        
        # Penalize deep nesting (>6 levels)
        nesting_penalty = max(0, (max_indent - 24) / 100)  # 4 spaces per level
        
        # Check for long functions (simple heuristic)
        function_lengths = []
        current_function = []
        in_function = False
        
        for line in diff.split('\n'):
            if line.startswith('+'):
                if re.match(r'\+\s*(def |async def )', line):
                    if in_function:
                        function_lengths.append(len(current_function))
                    current_function = [line]
                    in_function = True
                elif in_function:
                    current_function.append(line)
                    # End function at unindent
                    if line.strip() and not line.startswith('+    '):
                        function_lengths.append(len(current_function))
                        current_function = []
                        in_function = False
        
        # Penalize long functions (>50 lines)
        long_functions = sum(1 for length in function_lengths if length > 50)
        function_penalty = min(0.3, long_functions * 0.1)
        
        # Base score
        base_score = 0.9 - nesting_penalty - function_penalty
        
        # Apply pattern-based adjustment
        anti_pattern_penalty = min(0.4, bad_patterns * 0.1)
        
        return max(0.0, min(1.0, base_score - anti_pattern_penalty))
    
    def _evaluate_style(self, pr_data: Dict[str, Any], good_patterns: int, bad_patterns: int) -> float:
        """Evaluate code style"""
        diff = pr_data.get('diff', '')
        
        # Check for consistent indentation
        indent_types = {'spaces': 0, 'tabs': 0}
        for line in diff.split('\n'):
            if line.startswith('+'):
                if line.startswith('+\t'):
                    indent_types['tabs'] += 1
                elif line.startswith('+    '):
                    indent_types['spaces'] += 1
        
        # Penalize mixed indentation
        mixed_indent_penalty = 0.2 if indent_types['spaces'] > 0 and indent_types['tabs'] > 0 else 0
        
        # Base score from patterns
        base_score = 0.8 - mixed_indent_penalty
        anti_pattern_penalty = min(0.4, bad_patterns * 0.15)
        
        return max(0.0, min(1.0, base_score - anti_pattern_penalty))
    
    def _evaluate_documentation(self, pr_data: Dict[str, Any], good_patterns: int, bad_patterns: int) -> float:
        """Evaluate documentation quality"""
        diff = pr_data.get('diff', '')
        pr_body = pr_data.get('body', '')
        
        # Check for PR description
        has_description = len(pr_body.strip()) > 50
        description_score = 0.3 if has_description else 0.0
        
        # Check for docstrings in added functions
        added_functions = len(re.findall(r'^\+\s*(def |async def )', diff, re.MULTILINE))
        documented_functions = len(re.findall(r'^\+\s*(def |async def ).*:\s*\n\+\s*"""', diff, re.MULTILINE))
        
        if added_functions > 0:
            docstring_score = documented_functions / added_functions
        else:
            docstring_score = 0.8  # No functions added, not penalized
        
        # Check for comments
        comment_lines = len(re.findall(r'^\+\s*#', diff, re.MULTILINE))
        code_lines = len(re.findall(r'^\+\s*\w', diff, re.MULTILINE))
        
        if code_lines > 0:
            comment_ratio = comment_lines / code_lines
            comment_score = min(0.3, comment_ratio * 3)  # Cap at 0.3
        else:
            comment_score = 0.2
        
        # Combine scores
        base_score = description_score + (docstring_score * 0.4) + comment_score
        anti_pattern_penalty = min(0.3, bad_patterns * 0.1)  # TODO/FIXME penalty
        
        return max(0.0, min(1.0, base_score - anti_pattern_penalty))
    
    def _evaluate_test_coverage(self, pr_data: Dict[str, Any], good_patterns: int, bad_patterns: int) -> float:
        """Evaluate test coverage"""
        files = pr_data.get('files', [])
        diff = pr_data.get('diff', '')
        
        # Check if test files are included
        test_files = [f for f in files if 'test' in f.get('path', '').lower()]
        has_tests = len(test_files) > 0
        
        # Count test functions
        test_functions = len(re.findall(r'^\+\s*def test_\w+', diff, re.MULTILINE))
        test_classes = len(re.findall(r'^\+\s*class Test\w+', diff, re.MULTILINE))
        assertions = len(re.findall(r'^\+.*assert', diff, re.MULTILINE))
        
        # Count code changes outside tests
        code_files = [f for f in files if 'test' not in f.get('path', '').lower() and f.get('path', '').endswith('.py')]
        
        if len(code_files) == 0:
            # Only test changes, good
            return 0.9
        elif has_tests and (test_functions > 0 or test_classes > 0):
            # Has tests and code changes
            test_quality = min(1.0, (test_functions + test_classes * 3 + assertions * 0.1) / 10)
            return 0.6 + (test_quality * 0.3)
        elif has_tests:
            # Has test files but no new tests
            return 0.5
        else:
            # No test coverage
            return 0.3
    
    def _evaluate_security(self, pr_data: Dict[str, Any], good_patterns: int, bad_patterns: int) -> float:
        """Evaluate security practices"""
        diff = pr_data.get('diff', '')
        
        # Start with high score
        score = 0.95
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r'eval\(', 0.3, 'Use of eval()'),
            (r'exec\(', 0.3, 'Use of exec()'),
            (r'os\.system\(', 0.2, 'Use of os.system()'),
            (r'subprocess\.call\([^)]*shell=True', 0.25, 'Shell injection risk'),
            (r'pickle\.loads?\(', 0.15, 'Unsafe pickle usage'),
            (r'yaml\.load\([^)]*Loader', 0.15, 'Unsafe YAML loading'),
            (r'__import__\(', 0.2, 'Dynamic imports'),
        ]
        
        for pattern, penalty, description in dangerous_patterns:
            if re.search(pattern, diff, re.MULTILINE):
                score -= penalty
                self._log(f"Security concern: {description}")
        
        # Check for safe practices (bonus points)
        safe_patterns = [
            (r'os\.environ\.get\(', 0.02, 'Safe env var access'),
            (r'secrets\.', 0.03, 'Use of secrets module'),
            (r'hashlib\.', 0.02, 'Use of hashlib'),
        ]
        
        for pattern, bonus, description in safe_patterns:
            if re.search(pattern, diff, re.MULTILINE):
                score = min(1.0, score + bonus)
        
        return max(0.0, min(1.0, score))
    
    def _save_review_result(self, result: ReviewResult):
        """Save review result to history"""
        result_file = REVIEW_HISTORY_DIR / f"review_{result.pr_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(result_file, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            self._log(f"Review result saved: {result_file}")
        except Exception as e:
            self._log(f"Error saving review result: {e}")
    
    def learn_from_outcome(
        self, 
        pr_number: int, 
        outcome: str,
        manual_feedback: Optional[Dict[str, Any]] = None
    ):
        """
        Learn from PR outcome to improve criteria
        
        Args:
            pr_number: PR number
            outcome: 'merged', 'rejected', 'revised', 'abandoned'
            manual_feedback: Optional manual review feedback
        """
        self._log(f"Learning from PR #{pr_number} outcome: {outcome}")
        
        # Find review result for this PR
        review_files = list(REVIEW_HISTORY_DIR.glob(f"review_{pr_number}_*.json"))
        if not review_files:
            self._log(f"No review found for PR #{pr_number}")
            return
        
        # Load most recent review
        latest_review_file = max(review_files, key=lambda p: p.stat().st_mtime)
        with open(latest_review_file, 'r') as f:
            review_data = json.load(f)
        
        # Create outcome record
        outcome_record = ReviewOutcome(
            pr_number=pr_number,
            review_score=review_data['overall_score'],
            outcome=outcome,
            outcome_timestamp=datetime.now(timezone.utc).isoformat(),
            manual_feedback=manual_feedback
        )
        
        # Analyze prediction accuracy
        self._analyze_prediction_accuracy(review_data, outcome_record)
        
        # Update criteria based on outcome
        self._update_criteria_from_outcome(review_data, outcome_record)
        
        # Save outcome
        outcome_file = REVIEW_HISTORY_DIR / f"outcome_{pr_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(outcome_file, 'w') as f:
            json.dump(outcome_record.to_dict(), f, indent=2)
        
        self.history.append(outcome_record)
        self._log(f"Learned from outcome, total history: {len(self.history)}")
    
    def _analyze_prediction_accuracy(
        self, 
        review_data: Dict[str, Any],
        outcome: ReviewOutcome
    ):
        """Analyze how accurate the review was"""
        review_passed = review_data['passed']
        outcome_positive = outcome.outcome in ['merged', 'revised']
        
        # Update accuracy for each criterion
        for criterion in self.criteria:
            criterion_score = review_data['criteria_scores'].get(criterion.name, 0)
            criterion_passed = criterion_score >= criterion.threshold
            
            # Was the criterion prediction accurate?
            accurate = (criterion_passed == outcome_positive)
            outcome.criteria_accuracy[criterion.name] = accurate
            
            # Update criterion success rate
            criterion.total_evaluations += 1
            if accurate:
                # Increase success rate
                criterion.success_rate = (
                    criterion.success_rate * 0.9 + 0.1
                )
            else:
                # Decrease success rate
                criterion.success_rate = (
                    criterion.success_rate * 0.9
                )
        
        self._save_criteria()
    
    def _update_criteria_from_outcome(
        self,
        review_data: Dict[str, Any],
        outcome: ReviewOutcome
    ):
        """
        Update criteria weights and thresholds based on outcome using improved learning
        
        Uses adaptive learning rate based on:
        - Confidence in the prediction
        - Number of historical outcomes
        - Magnitude of prediction error
        """
        outcome_positive = outcome.outcome in ['merged', 'revised']
        review_score = review_data['overall_score']
        review_passed = review_data['passed']
        
        # Calculate prediction error
        prediction_correct = (review_passed == outcome_positive)
        error_magnitude = abs(review_score - (1.0 if outcome_positive else 0.3))
        
        # Adaptive learning rate (higher error = faster learning)
        base_learning_rate = 0.02
        adaptive_rate = base_learning_rate * (1 + error_magnitude)
        
        # Reduce learning rate as we get more data (converge)
        stability_factor = 1.0 / (1.0 + len(self.history) / 20)
        learning_rate = adaptive_rate * stability_factor
        
        self._log(f"Learning rate: {learning_rate:.4f} (error: {error_magnitude:.3f}, data: {len(self.history)})")
        
        for criterion in self.criteria:
            criterion_score = review_data['criteria_scores'].get(criterion.name, 0)
            criterion_passed = criterion_score >= criterion.threshold
            
            # Check if this criterion was predictive
            was_predictive = (criterion_passed == outcome_positive)
            
            # Update weight based on predictive power
            if was_predictive:
                # Increase weight for predictive criteria
                criterion.weight = criterion.weight * (1 + learning_rate)
            else:
                # Decrease weight for non-predictive criteria
                criterion.weight = criterion.weight * (1 - learning_rate)
            
            # Ensure minimum weight
            criterion.weight = max(0.05, criterion.weight)
        
        # Normalize weights to sum to 1.0
        total_weight = sum(c.weight for c in self.criteria)
        for c in self.criteria:
            c.weight = c.weight / total_weight
        
        # Adjust thresholds with adaptive learning
        for criterion in self.criteria:
            criterion_score = review_data['criteria_scores'].get(criterion.name, 0)
            
            if not prediction_correct:
                # Adjust threshold to correct the error
                if not outcome_positive and criterion_score >= criterion.threshold:
                    # False positive - increase threshold (be more strict)
                    adjustment = learning_rate * 0.5
                    criterion.threshold = min(0.95, criterion.threshold * (1 + adjustment))
                elif outcome_positive and criterion_score < criterion.threshold:
                    # False negative - decrease threshold (be more lenient)
                    adjustment = learning_rate * 0.5
                    criterion.threshold = max(0.3, criterion.threshold * (1 - adjustment))
        
        self._save_criteria()
        self._log(f"Criteria updated (prediction_correct: {prediction_correct})")
    
    def update_criteria_batch(self):
        """Batch update criteria based on all historical outcomes"""
        self._log(f"Batch updating criteria from {len(self.history)} outcomes")
        
        if len(self.history) < 5:
            self._log("Not enough history for batch update")
            return
        
        # Analyze overall success rates
        for criterion in self.criteria:
            correct_predictions = sum(
                1 for outcome in self.history
                if outcome.criteria_accuracy.get(criterion.name, False)
            )
            total = len(self.history)
            
            if total > 0:
                accuracy = correct_predictions / total
                self._log(f"  {criterion.name}: {accuracy:.2%} accuracy")
                
                # Update success rate with historical data
                criterion.success_rate = accuracy
        
        self._save_criteria()
        self._log("Batch criteria update complete")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reviewer statistics"""
        total_reviews = len(list(REVIEW_HISTORY_DIR.glob("review_*.json")))
        total_outcomes = len(self.history)
        
        outcome_counts = Counter(o.outcome for o in self.history)
        
        avg_accuracy = sum(c.success_rate for c in self.criteria) / len(self.criteria) if self.criteria else 0
        
        return {
            'version': self.VERSION,
            'total_reviews': total_reviews,
            'total_outcomes': total_outcomes,
            'outcome_distribution': dict(outcome_counts),
            'average_criterion_accuracy': avg_accuracy,
            'criteria_count': len(self.criteria),
            'criteria': [
                {
                    'name': c.name,
                    'weight': c.weight,
                    'threshold': c.threshold,
                    'success_rate': c.success_rate,
                    'evaluations': c.total_evaluations
                }
                for c in self.criteria
            ]
        }


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Autonomous Code Reviewer - Self-improving code review system"
    )
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    # Command group
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument('--review', type=int, metavar='PR_NUMBER',
                          help='Review a pull request')
    commands.add_argument('--learn-from-outcome', type=int, metavar='PR_NUMBER',
                          help='Learn from PR outcome')
    commands.add_argument('--update-criteria', action='store_true',
                          help='Batch update criteria from history')
    commands.add_argument('--show-stats', action='store_true',
                          help='Show reviewer statistics')
    
    # Additional arguments
    parser.add_argument('--outcome', choices=['merged', 'rejected', 'revised', 'abandoned'],
                        help='Outcome for learning (used with --learn-from-outcome)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file for results')
    
    args = parser.parse_args()
    
    # Create reviewer instance
    reviewer = AutonomousCodeReviewer(verbose=args.verbose)
    
    try:
        if args.review:
            # Perform review
            result = reviewer.review_pr(args.review)
            
            # Output result
            output = {
                'pr_number': result.pr_number,
                'overall_score': result.overall_score,
                'passed': result.passed,
                'criteria_scores': result.criteria_scores,
                'issues_count': len(result.issues_found),
                'suggestions': result.suggestions,
            }
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result.to_dict(), f, indent=2)
                print(f"Review result saved to: {args.output}")
            else:
                print(json.dumps(output, indent=2))
        
        elif args.learn_from_outcome:
            if not args.outcome:
                print("Error: --outcome is required with --learn-from-outcome", file=sys.stderr)
                sys.exit(1)
            
            reviewer.learn_from_outcome(args.learn_from_outcome, args.outcome)
            print(f"Learned from PR #{args.learn_from_outcome} outcome: {args.outcome}")
        
        elif args.update_criteria:
            reviewer.update_criteria_batch()
            print("Criteria batch update complete")
        
        elif args.show_stats:
            stats = reviewer.get_stats()
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(stats, f, indent=2)
                print(f"Statistics saved to: {args.output}")
            else:
                print(json.dumps(stats, indent=2))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
