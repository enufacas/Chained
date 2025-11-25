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

Author: @create-guru (Infrastructure creation specialist)
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
                    r"\s{4,}\w",  # Inconsistent indentation
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
                ],
                anti_patterns=[
                    r"pass\s*#.*test",  # Empty test placeholders
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
                    r"input\(.*\)",  # Safe input handling checks
                    r"os\.environ\.get\(",  # Safe env var access
                ],
                anti_patterns=[
                    r"eval\(",  # Dangerous eval
                    r"exec\(",  # Dangerous exec
                    r"os\.system\(",  # Dangerous system calls
                    r"subprocess\.call\(.+shell=True",  # Shell injection risk
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
        
        # Determine pass/fail
        pass_threshold = 0.7  # Can be made adaptive
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
            reviewer_version=self.VERSION
        )
        
        # Save review result
        self._save_review_result(result)
        
        return result
    
    def _fetch_pr_data(self, pr_number: int) -> Dict[str, Any]:
        """Fetch PR data from GitHub (stub for now)"""
        # In full implementation, would use GitHub API
        return {
            'number': pr_number,
            'title': f'PR #{pr_number}',
            'files': [],
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
        # Simplified evaluation logic
        # In full implementation, would analyze actual code
        
        issues = []
        suggestions = []
        
        # Pattern matching (simplified)
        pattern_matches = 0
        anti_pattern_matches = 0
        
        # Would analyze actual PR diff here
        pr_content = str(pr_data.get('diff', ''))
        
        for pattern in criterion.patterns:
            if re.search(pattern, pr_content, re.MULTILINE):
                pattern_matches += 1
        
        for anti_pattern in criterion.anti_patterns:
            match = re.search(anti_pattern, pr_content, re.MULTILINE)
            if match:
                anti_pattern_matches += 1
                issues.append({
                    'criterion': criterion.name,
                    'severity': 'warning',
                    'message': f'Anti-pattern detected: {anti_pattern}',
                    'location': 'code'
                })
        
        # Calculate score
        if len(criterion.patterns) > 0:
            base_score = pattern_matches / len(criterion.patterns)
        else:
            base_score = 0.8  # Default if no patterns
        
        # Penalize for anti-patterns
        penalty = min(0.5, anti_pattern_matches * 0.1)
        score = max(0.0, min(1.0, base_score - penalty))
        
        # Generate suggestions if score is low
        if score < criterion.threshold:
            suggestions.append(
                f"Consider improving {criterion.name}: {criterion.description}"
            )
        
        return score, issues, suggestions
    
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
        """Update criteria weights and thresholds based on outcome"""
        outcome_positive = outcome.outcome in ['merged', 'revised']
        
        for criterion in self.criteria:
            criterion_score = review_data['criteria_scores'].get(criterion.name, 0)
            
            # Adjust weight based on predictive power
            if outcome.criteria_accuracy.get(criterion.name, False):
                # This criterion was predictive, slightly increase weight
                criterion.weight = min(1.0, criterion.weight * 1.02)
            else:
                # This criterion was not predictive, slightly decrease weight
                criterion.weight = max(0.05, criterion.weight * 0.98)
            
            # Normalize weights to sum to 1.0
            total_weight = sum(c.weight for c in self.criteria)
            for c in self.criteria:
                c.weight = c.weight / total_weight
            
            # Adjust threshold based on false positives/negatives
            if not outcome_positive and criterion_score >= criterion.threshold:
                # False positive - tighten threshold
                criterion.threshold = min(1.0, criterion.threshold * 1.05)
            elif outcome_positive and criterion_score < criterion.threshold:
                # False negative - loosen threshold
                criterion.threshold = max(0.3, criterion.threshold * 0.95)
        
        self._save_criteria()
        self._log("Criteria updated based on outcome")
    
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
