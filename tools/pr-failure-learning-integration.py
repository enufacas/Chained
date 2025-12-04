#!/usr/bin/env python3
"""
PR Failure Learning Integration - Enhanced Code Generation Guidance

Built by @create-botter to integrate PR failure learning directly into the
code generation workflow. This module enables AI agents to learn from
historical PR failures and improve future code generation.

This integration provides:
- Pre-task learning context for agents before they start work
- Real-time failure pattern checks during code generation
- Agent-specific improvement tracking over time
- Actionable checklist generation based on historical failures

Architecture:
- Integrates with existing pr-failure-learner.py data
- Integrates with agent-learning-api.py for guidance queries
- Provides structured output for issue assignment workflows
- Tracks learning effectiveness through improvement metrics

Usage:
    # Generate pre-task learning context for an agent
    python pr-failure-learning-integration.py --agent AGENT_ID --issue-number 123

    # Generate improvement checklist based on agent's history
    python pr-failure-learning-integration.py --checklist --agent AGENT_ID

    # Track learning improvement for an agent
    python pr-failure-learning-integration.py --track-improvement --agent AGENT_ID --pr-number 456

Examples:
    python pr-failure-learning-integration.py --agent create-botter --issue-number 2946
    python pr-failure-learning-integration.py --checklist --agent engineer-master
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from collections import Counter
import argparse

# Path Constants
LEARNINGS_DIR = Path("learnings")
PR_FAILURES_FILE = LEARNINGS_DIR / "pr_failures.json"
INTELLIGENCE_DIR = LEARNINGS_DIR / "pr_intelligence"
AGENT_PROFILES_DIR = INTELLIGENCE_DIR / "agent_profiles"
PATTERNS_FILE = INTELLIGENCE_DIR / "code_patterns.json"
AGENT_LEARNING_TRACKER_FILE = INTELLIGENCE_DIR / "agent_learning_tracker.json"

# Threshold Constants - Configurable values for failure analysis
SMALL_PR_FILE_THRESHOLD = 10  # PRs with <= this many files are considered "small"
LARGE_PR_FILE_THRESHOLD = 20  # PRs with > this many files are considered "large"
LARGE_PR_RATIO_THRESHOLD = 0.3  # If > 30% of failures are large PRs, warn about it
HIGH_SUCCESS_RATE_THRESHOLD = 0.8  # Patterns with >= 80% success are recommended
HISTORY_LIMIT = 50  # Maximum entries to keep in learning history per agent


@dataclass
class LearningContext:
    """Learning context for an agent before starting a task"""
    agent_id: str
    issue_number: Optional[int] = None
    proactive_warnings: List[str] = field(default_factory=list)
    recommended_approach: List[str] = field(default_factory=list)
    success_patterns: List[str] = field(default_factory=list)
    past_failures_count: int = 0
    past_rejections_count: int = 0
    improvement_trajectory: str = "unknown"  # improving, stable, declining
    confidence_score: float = 0.5
    generated_at: str = ""
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def to_markdown(self) -> str:
        """Generate markdown formatted context for issue injection"""
        lines = []
        
        # Proactive Warnings Section
        if self.proactive_warnings:
            lines.append("### ⚠️ Proactive Warnings\n")
            lines.append(f"Based on historical PR failures, **@{self.agent_id}** should be aware of:\n")
            for warning in self.proactive_warnings:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")
        
        # Recommended Approach Section
        if self.recommended_approach:
            lines.append("\n### ✅ Recommended Approach\n")
            for rec in self.recommended_approach:
                lines.append(f"- ✅ {rec}")
            lines.append("")
        
        # Success Patterns Section
        if self.success_patterns:
            lines.append("\n### 🎯 Success Patterns\n")
            lines.append("PRs that follow these patterns have high success rates:\n")
            for pattern in self.success_patterns:
                lines.append(f"- {pattern}")
            lines.append("")
        
        return "\n".join(lines)


@dataclass
class ImprovementChecklist:
    """Checklist for agents to improve code quality based on past failures"""
    agent_id: str
    checklist_items: List[Dict[str, Any]] = field(default_factory=list)
    priority_focus: List[str] = field(default_factory=list)
    generated_at: str = ""
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_markdown(self) -> str:
        """Generate markdown formatted checklist"""
        lines = ["## 📋 Pre-Submission Checklist", ""]
        
        if self.priority_focus:
            lines.append("**Priority Focus Areas:**")
            for focus in self.priority_focus:
                lines.append(f"- 🎯 {focus}")
            lines.append("")
        
        lines.append("**Checklist:**")
        for item in self.checklist_items:
            priority = item.get('priority', 'medium')
            emoji = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢"
            lines.append(f"- [ ] {emoji} {item['text']}")
        
        return "\n".join(lines)


class PRFailureLearningIntegration:
    """
    Integration service for PR failure learning in code generation.
    
    Built by @create-botter to help AI agents learn from historical
    PR failures and improve their code generation.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._ensure_directories()
        self._load_data()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        INTELLIGENCE_DIR.mkdir(parents=True, exist_ok=True)
        AGENT_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """Load failure and pattern data"""
        self.failures = self._load_failures()
        self.patterns = self._load_patterns()
        self.learning_tracker = self._load_learning_tracker()
    
    def _load_failures(self) -> List[Dict[str, Any]]:
        """Load PR failure data"""
        if not PR_FAILURES_FILE.exists():
            return []
        with open(PR_FAILURES_FILE, 'r') as f:
            data = json.load(f)
        return data.get('failures', [])
    
    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load code patterns data"""
        if not PATTERNS_FILE.exists():
            return []
        with open(PATTERNS_FILE, 'r') as f:
            data = json.load(f)
        return data.get('patterns', [])
    
    def _load_learning_tracker(self) -> Dict[str, Any]:
        """Load agent learning tracker"""
        if not AGENT_LEARNING_TRACKER_FILE.exists():
            return {'agents': {}, 'last_updated': None}
        with open(AGENT_LEARNING_TRACKER_FILE, 'r') as f:
            return json.load(f)
    
    def _save_learning_tracker(self):
        """Save agent learning tracker"""
        self.learning_tracker['last_updated'] = datetime.now(timezone.utc).isoformat()
        with open(AGENT_LEARNING_TRACKER_FILE, 'w') as f:
            json.dump(self.learning_tracker, f, indent=2)
    
    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[PR-Learning-Integration] {message}", file=sys.stderr)
    
    def get_agent_failures(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get failures associated with a specific agent"""
        agent_failures = []
        for failure in self.failures:
            if failure.get('agent_specialization') == agent_id:
                agent_failures.append(failure)
            elif agent_id in str(failure.get('labels', [])):
                agent_failures.append(failure)
            elif agent_id in failure.get('title', ''):
                agent_failures.append(failure)
        return agent_failures
    
    def generate_learning_context(
        self, 
        agent_id: str, 
        issue_number: Optional[int] = None,
        issue_title: Optional[str] = None,
        issue_body: Optional[str] = None
    ) -> LearningContext:
        """
        Generate learning context for an agent before starting a task.
        
        Args:
            agent_id: The agent's identifier
            issue_number: Optional issue number for context
            issue_title: Optional issue title for matching
            issue_body: Optional issue body for matching
            
        Returns:
            LearningContext with proactive warnings and recommendations
        """
        self.log(f"Generating learning context for agent: {agent_id}")
        
        # Get agent-specific failures
        agent_failures = self.get_agent_failures(agent_id)
        
        # Analyze failure types
        failure_types = Counter(f.get('failure_type', 'unknown') for f in agent_failures)
        
        # Count rejections specifically
        rejection_count = failure_types.get('review_rejection', 0)
        
        # Generate proactive warnings
        warnings = self._generate_proactive_warnings(agent_id, agent_failures, failure_types)
        
        # Generate recommended approach
        recommendations = self._generate_recommendations(agent_failures, failure_types)
        
        # Generate success patterns from pattern data
        success_patterns = self._generate_success_patterns()
        
        # Determine improvement trajectory
        trajectory = self._calculate_improvement_trajectory(agent_id)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(len(agent_failures), len(self.patterns))
        
        return LearningContext(
            agent_id=agent_id,
            issue_number=issue_number,
            proactive_warnings=warnings,
            recommended_approach=recommendations,
            success_patterns=success_patterns,
            past_failures_count=len(agent_failures),
            past_rejections_count=rejection_count,
            improvement_trajectory=trajectory,
            confidence_score=confidence
        )
    
    def _generate_proactive_warnings(
        self, 
        agent_id: str,
        failures: List[Dict[str, Any]], 
        failure_types: Counter
    ) -> List[str]:
        """Generate proactive warnings based on agent's failure history"""
        warnings = []
        
        # Warning for review rejections
        rejections = failure_types.get('review_rejection', 0)
        if rejections > 0:
            warnings.append(
                f"You have {rejections} past review rejections. "
                "Follow code review guidelines carefully."
            )
        
        # Warning for test failures
        test_failures = failure_types.get('test_failure', 0)
        if test_failures > 0:
            warnings.append(
                f"You have {test_failures} past test failures. "
                "Ensure all tests pass before submitting."
            )
        
        # Warning for CI failures
        ci_failures = failure_types.get('ci_failure', 0)
        if ci_failures > 0:
            warnings.append(
                f"You have {ci_failures} past CI failures. "
                "Run lint and build locally before submitting."
            )
        
        # Warning for merge conflicts
        merge_conflicts = failure_types.get('merge_conflict', 0)
        if merge_conflicts > 0:
            warnings.append(
                f"You have {merge_conflicts} past merge conflicts. "
                "Keep PRs small and sync frequently with main."
            )
        
        # Warning for large PRs
        large_prs = [f for f in failures if f.get('files_changed', 0) > LARGE_PR_FILE_THRESHOLD]
        if len(large_prs) > len(failures) * LARGE_PR_RATIO_THRESHOLD and len(large_prs) > 0:
            warnings.append(
                "Large PRs tend to fail more often. "
                "Consider breaking changes into smaller, focused PRs."
            )
        
        return warnings
    
    def _generate_recommendations(
        self,
        failures: List[Dict[str, Any]],
        failure_types: Counter
    ) -> List[str]:
        """Generate recommended approach based on failure analysis"""
        recommendations = []
        
        # Always recommend following conventions
        recommendations.append("Follow repository conventions")
        
        # Always recommend clear code
        recommendations.append("Write clear, maintainable code")
        
        # Test-related recommendations
        if failure_types.get('test_failure', 0) > 0 or failure_types.get('review_rejection', 0) > 0:
            recommendations.append("Include tests for new functionality")
        
        # Review comments analysis
        review_issues = []
        for failure in failures:
            for comment in failure.get('review_comments', []):
                body = comment.get('body', '').lower()
                if 'test' in body:
                    review_issues.append('tests')
                if 'document' in body or 'doc' in body:
                    review_issues.append('documentation')
                if 'security' in body:
                    review_issues.append('security')
        
        if 'documentation' in review_issues:
            recommendations.append("Update documentation for changes")
        if 'security' in review_issues:
            recommendations.append("Review security implications")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _generate_success_patterns(self) -> List[str]:
        """Generate success patterns from pattern data"""
        success_patterns = []
        
        for pattern in self.patterns:
            success_rate = pattern.get('success_rate', 0)
            if success_rate >= HIGH_SUCCESS_RATE_THRESHOLD:  # Only high-success patterns
                description = pattern.get('description', '')
                if description:
                    success_patterns.append(description)
        
        # Add default patterns if none found
        if not success_patterns:
            success_patterns = [
                f"Small PRs (≤{SMALL_PR_FILE_THRESHOLD} files) have higher success rates",
                "PRs including test files succeed more often",
                "PRs with conventional commit format have better outcomes"
            ]
        
        return success_patterns[:5]  # Top 5 patterns
    
    def _calculate_improvement_trajectory(self, agent_id: str) -> str:
        """Calculate agent's improvement trajectory over time"""
        tracker_data = self.learning_tracker.get('agents', {}).get(agent_id, {})
        history = tracker_data.get('success_history', [])
        
        if len(history) < 3:
            return "unknown"
        
        # Calculate recent vs historical success rate
        recent = history[-3:]
        historical = history[:-3] if len(history) > 3 else []
        
        recent_rate = sum(1 for x in recent if x) / len(recent)
        hist_rate = sum(1 for x in historical if x) / len(historical) if historical else 0.5
        
        if recent_rate > hist_rate + 0.1:
            return "improving"
        elif recent_rate < hist_rate - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_confidence(self, failure_count: int, pattern_count: int) -> float:
        """Calculate confidence score based on available data"""
        # Base confidence on data availability
        data_score = min(1.0, (failure_count + pattern_count * 2) / 20)
        return round(data_score, 2)
    
    def generate_improvement_checklist(self, agent_id: str) -> ImprovementChecklist:
        """
        Generate a pre-submission checklist for an agent based on their history.
        
        Args:
            agent_id: The agent's identifier
            
        Returns:
            ImprovementChecklist with items and priority focus areas
        """
        self.log(f"Generating improvement checklist for agent: {agent_id}")
        
        agent_failures = self.get_agent_failures(agent_id)
        failure_types = Counter(f.get('failure_type', 'unknown') for f in agent_failures)
        
        checklist_items = []
        priority_focus = []
        
        # Base checklist items
        checklist_items.append({
            'text': 'Run all tests locally before submitting',
            'priority': 'high' if failure_types.get('test_failure', 0) > 0 else 'medium',
            'category': 'testing'
        })
        
        checklist_items.append({
            'text': 'Run linter and fix all issues',
            'priority': 'high' if failure_types.get('ci_failure', 0) > 0 else 'medium',
            'category': 'code_quality'
        })
        
        checklist_items.append({
            'text': f'Check PR size (aim for ≤{SMALL_PR_FILE_THRESHOLD} files)',
            'priority': 'high' if any(f.get('files_changed', 0) > LARGE_PR_FILE_THRESHOLD for f in agent_failures) else 'low',
            'category': 'pr_size'
        })
        
        checklist_items.append({
            'text': 'Sync branch with main to avoid conflicts',
            'priority': 'high' if failure_types.get('merge_conflict', 0) > 0 else 'low',
            'category': 'version_control'
        })
        
        checklist_items.append({
            'text': 'Include tests for new functionality',
            'priority': 'high',
            'category': 'testing'
        })
        
        checklist_items.append({
            'text': 'Update documentation if needed',
            'priority': 'medium',
            'category': 'documentation'
        })
        
        checklist_items.append({
            'text': 'Use conventional commit format in PR title',
            'priority': 'medium',
            'category': 'conventions'
        })
        
        checklist_items.append({
            'text': 'Review code for security implications',
            'priority': 'medium',
            'category': 'security'
        })
        
        # Determine priority focus based on failure history
        if failure_types.get('test_failure', 0) > 1:
            priority_focus.append("Focus on comprehensive testing")
        if failure_types.get('review_rejection', 0) > 1:
            priority_focus.append("Carefully follow code review guidelines")
        if failure_types.get('ci_failure', 0) > 1:
            priority_focus.append("Ensure CI passes before review")
        if failure_types.get('merge_conflict', 0) > 1:
            priority_focus.append("Keep PRs small and sync frequently")
        
        if not priority_focus:
            priority_focus.append("Maintain current quality standards")
        
        return ImprovementChecklist(
            agent_id=agent_id,
            checklist_items=checklist_items,
            priority_focus=priority_focus
        )
    
    def track_pr_outcome(
        self, 
        agent_id: str, 
        pr_number: int, 
        success: bool,
        failure_type: Optional[str] = None
    ):
        """
        Track a PR outcome for learning improvement analysis.
        
        Args:
            agent_id: The agent's identifier
            pr_number: The PR number
            success: Whether the PR was successful (merged)
            failure_type: Type of failure if unsuccessful
        """
        self.log(f"Tracking PR outcome: agent={agent_id}, pr={pr_number}, success={success}")
        
        if agent_id not in self.learning_tracker['agents']:
            self.learning_tracker['agents'][agent_id] = {
                'success_history': [],
                'failure_types': [],
                'pr_history': [],
                'first_tracked': datetime.now(timezone.utc).isoformat()
            }
        
        agent_data = self.learning_tracker['agents'][agent_id]
        agent_data['success_history'].append(success)
        agent_data['pr_history'].append({
            'pr_number': pr_number,
            'success': success,
            'failure_type': failure_type,
            'tracked_at': datetime.now(timezone.utc).isoformat()
        })
        
        if not success and failure_type:
            agent_data['failure_types'].append(failure_type)
        
        # Keep only the most recent entries based on configured limit
        if len(agent_data['success_history']) > HISTORY_LIMIT:
            agent_data['success_history'] = agent_data['success_history'][-HISTORY_LIMIT:]
        if len(agent_data['pr_history']) > HISTORY_LIMIT:
            agent_data['pr_history'] = agent_data['pr_history'][-HISTORY_LIMIT:]
        
        self._save_learning_tracker()
    
    def get_agent_learning_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get learning statistics for an agent.
        
        Args:
            agent_id: The agent's identifier
            
        Returns:
            Dictionary with learning statistics
        """
        agent_data = self.learning_tracker.get('agents', {}).get(agent_id, {})
        history = agent_data.get('success_history', [])
        
        if not history:
            return {
                'agent_id': agent_id,
                'total_tracked': 0,
                'success_rate': 0.0,
                'trajectory': 'unknown',
                'message': 'No tracked history available'
            }
        
        success_count = sum(1 for x in history if x)
        total = len(history)
        
        return {
            'agent_id': agent_id,
            'total_tracked': total,
            'success_rate': round(success_count / total, 2),
            'trajectory': self._calculate_improvement_trajectory(agent_id),
            'recent_successes': sum(1 for x in history[-5:] if x),
            'recent_total': min(5, len(history)),
            'first_tracked': agent_data.get('first_tracked', 'unknown'),
            'failure_types': Counter(agent_data.get('failure_types', []))
        }


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description='PR Failure Learning Integration - Enhanced Code Generation Guidance'
    )
    
    parser.add_argument('--agent', type=str, required=True,
                       help='Agent ID for the learning context')
    parser.add_argument('--issue-number', type=int,
                       help='Optional issue number for context')
    parser.add_argument('--checklist', action='store_true',
                       help='Generate improvement checklist instead of learning context')
    parser.add_argument('--track-improvement', action='store_true',
                       help='Track PR outcome for improvement analysis')
    parser.add_argument('--pr-number', type=int,
                       help='PR number for tracking (required with --track-improvement)')
    parser.add_argument('--success', action='store_true',
                       help='Mark PR as successful (for tracking)')
    parser.add_argument('--failure-type', type=str,
                       help='Failure type if PR failed (for tracking)')
    parser.add_argument('--stats', action='store_true',
                       help='Get learning statistics for agent')
    parser.add_argument('--markdown', action='store_true',
                       help='Output in markdown format')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    integration = PRFailureLearningIntegration(verbose=args.verbose)
    
    if args.track_improvement:
        if not args.pr_number:
            print("Error: --pr-number required with --track-improvement", file=sys.stderr)
            sys.exit(1)
        
        integration.track_pr_outcome(
            agent_id=args.agent,
            pr_number=args.pr_number,
            success=args.success,
            failure_type=args.failure_type
        )
        print(f"✅ Tracked PR #{args.pr_number} outcome for {args.agent}")
    
    elif args.stats:
        stats = integration.get_agent_learning_stats(args.agent)
        print(json.dumps(stats, indent=2))
    
    elif args.checklist:
        checklist = integration.generate_improvement_checklist(args.agent)
        if args.markdown:
            print(checklist.to_markdown())
        else:
            print(json.dumps(checklist.to_dict(), indent=2))
    
    else:
        context = integration.generate_learning_context(
            agent_id=args.agent,
            issue_number=args.issue_number
        )
        if args.markdown:
            print(context.to_markdown())
        else:
            print(context.to_json())


if __name__ == '__main__':
    main()
