#!/usr/bin/env python3
"""
Autonomous Issue Prioritizer using Multi-Armed Bandit Algorithms

This module implements an intelligent issue prioritization system using
multi-armed bandit (MAB) algorithms to balance exploration and exploitation
when deciding which issues to prioritize.

Design Philosophy (@accelerate-master):
- Efficient: Minimize computational overhead
- Simple: Clear algorithm that's easy to understand and maintain
- Adaptive: Learns from historical data to improve over time
- Performance-focused: Fast priority calculations

Algorithm: Upper Confidence Bound (UCB1)
The UCB1 algorithm balances exploration (trying untested issue types) with
exploitation (prioritizing issue types that have historically performed well).

UCB1 Score = Average Reward + c * sqrt(ln(total_trials) / type_trials)

Where:
- Average Reward: Historical success rate for this issue type
- c: Exploration parameter (typically sqrt(2))
- total_trials: Total number of resolved issues
- type_trials: Number of issues resolved of this type
"""

import json
import os
import sys
import math
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class IssueMetrics:
    """Metrics for evaluating issue outcomes"""
    resolution_time_hours: Optional[float] = None
    pr_success: bool = False
    code_quality: float = 0.0
    agent_score: float = 0.0
    
    def calculate_reward(self) -> float:
        """Calculate reward signal (0.0 to 1.0)"""
        reward = 0.0
        
        # PR success (40% weight)
        if self.pr_success:
            reward += 0.4
        
        # Code quality (30% weight)
        reward += 0.3 * self.code_quality
        
        # Resolution speed bonus (20% weight)
        if self.resolution_time_hours:
            # Faster is better, normalized to 48 hours
            speed_factor = max(0, 1 - (self.resolution_time_hours / 48))
            reward += 0.2 * speed_factor
        
        # Agent performance (10% weight)
        reward += 0.1 * self.agent_score
        
        return min(1.0, max(0.0, reward))


@dataclass
class IssueType:
    """Represents an issue category (arm in the bandit)"""
    name: str
    keywords: List[str]
    total_attempts: int = 0
    total_reward: float = 0.0
    
    def average_reward(self) -> float:
        """Calculate average reward for this issue type"""
        if self.total_attempts == 0:
            return 0.0
        return self.total_reward / self.total_attempts
    
    def ucb1_score(self, total_attempts: int, c: float = 1.414) -> float:
        """Calculate UCB1 score for this issue type
        
        Args:
            total_attempts: Total attempts across all issue types
            c: Exploration parameter (default: sqrt(2) ≈ 1.414)
        
        Returns:
            UCB1 score (higher = higher priority)
        """
        if self.total_attempts == 0:
            # Unexplored arms get infinite priority
            return float('inf')
        
        avg_reward = self.average_reward()
        exploration_bonus = c * math.sqrt(math.log(total_attempts) / self.total_attempts)
        
        return avg_reward + exploration_bonus


class IssuePrioritizer:
    """Multi-Armed Bandit Issue Prioritizer"""
    
    def __init__(self, history_file: Optional[Path] = None):
        """Initialize prioritizer with optional history file"""
        self.history_file = history_file or Path(".github/agent-system/issue_history.json")
        self.priority_state_file = Path(".github/agent-system/priority_state.json")
        
        # Define issue types (arms in the bandit)
        self.issue_types = {
            'performance': IssueType(
                name='performance',
                keywords=['performance', 'slow', 'optimize', 'speed', 'efficiency', 'latency']
            ),
            'bug': IssueType(
                name='bug',
                keywords=['bug', 'error', 'crash', 'fail', 'broken', 'exception']
            ),
            'feature': IssueType(
                name='feature',
                keywords=['feature', 'enhancement', 'add', 'implement', 'new']
            ),
            'testing': IssueType(
                name='testing',
                keywords=['test', 'coverage', 'qa', 'quality']
            ),
            'security': IssueType(
                name='security',
                keywords=['security', 'vulnerability', 'auth', 'permission', 'cve']
            ),
            'documentation': IssueType(
                name='documentation',
                keywords=['doc', 'documentation', 'readme', 'guide', 'tutorial']
            ),
            'refactor': IssueType(
                name='refactor',
                keywords=['refactor', 'cleanup', 'technical debt', 'code smell']
            ),
            'infrastructure': IssueType(
                name='infrastructure',
                keywords=['infra', 'ci/cd', 'deployment', 'workflow', 'automation']
            )
        }
        
        self.load_state()
    
    def load_state(self):
        """Load historical state from file"""
        if self.priority_state_file.exists():
            try:
                with open(self.priority_state_file, 'r') as f:
                    state = json.load(f)
                    
                # Restore issue type statistics
                for type_name, type_data in state.get('issue_types', {}).items():
                    if type_name in self.issue_types:
                        self.issue_types[type_name].total_attempts = type_data.get('total_attempts', 0)
                        self.issue_types[type_name].total_reward = type_data.get('total_reward', 0.0)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load priority state: {e}", file=sys.stderr)
    
    def save_state(self):
        """Save current state to file"""
        state = {
            'version': '1.0',
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'issue_types': {
                name: {
                    'total_attempts': itype.total_attempts,
                    'total_reward': itype.total_reward,
                    'average_reward': itype.average_reward()
                }
                for name, itype in self.issue_types.items()
            }
        }
        
        self.priority_state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.priority_state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def classify_issue(self, title: str, body: str, labels: List[str]) -> str:
        """Classify an issue into an issue type
        
        Args:
            title: Issue title
            body: Issue body
            labels: Issue labels
        
        Returns:
            Issue type name
        """
        text = f"{title} {body} {' '.join(labels)}".lower()
        
        # Count keyword matches for each type
        scores = {}
        for type_name, issue_type in self.issue_types.items():
            score = sum(1 for keyword in issue_type.keywords if keyword in text)
            scores[type_name] = score
        
        # Return type with highest score, or 'feature' as default
        if max(scores.values()) == 0:
            return 'feature'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def calculate_priority(self, issue_type: str) -> float:
        """Calculate priority score for an issue type using UCB1
        
        Args:
            issue_type: Issue type name
        
        Returns:
            Priority score (0.0 to 1.0+)
        """
        if issue_type not in self.issue_types:
            return 0.5  # Default priority
        
        total_attempts = sum(t.total_attempts for t in self.issue_types.values())
        if total_attempts == 0:
            return 1.0  # All types equally prioritized initially
        
        ucb1_score = self.issue_types[issue_type].ucb1_score(total_attempts)
        
        # Normalize to 0-1 range (approximately)
        # UCB1 scores are typically 0-2, so we divide by 2
        if ucb1_score == float('inf'):
            return 1.0
        
        return min(1.0, ucb1_score / 2.0)
    
    def prioritize_issue(self, issue_number: int, title: str, body: str, 
                        labels: List[str]) -> Dict:
        """Prioritize a single issue
        
        Args:
            issue_number: Issue number
            title: Issue title
            body: Issue body
            labels: Issue labels
        
        Returns:
            Dictionary with priority information
        """
        issue_type = self.classify_issue(title, body, labels)
        priority_score = self.calculate_priority(issue_type)
        
        # Calculate priority tier
        if priority_score >= 0.85:
            tier = "P0-Critical"
            action = "Implement immediately"
        elif priority_score >= 0.70:
            tier = "P1-High"
            action = "Plan for next sprint"
        elif priority_score >= 0.50:
            tier = "P2-Medium"
            action = "Add to backlog"
        else:
            tier = "P3-Low"
            action = "Monitor"
        
        return {
            'issue_number': issue_number,
            'title': title,
            'issue_type': issue_type,
            'priority_score': round(priority_score, 3),
            'priority_tier': tier,
            'recommended_action': action,
            'ucb1_stats': {
                'attempts': self.issue_types[issue_type].total_attempts,
                'avg_reward': round(self.issue_types[issue_type].average_reward(), 3)
            }
        }
    
    def update_from_history(self):
        """Update bandit state from historical issue data"""
        if not self.history_file.exists():
            print("Warning: No history file found", file=sys.stderr)
            return
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading history: {e}", file=sys.stderr)
            return
        
        # Process each resolved issue
        for issue in history.get('issues', []):
            issue_type = self.classify_issue(
                issue.get('title', ''),
                issue.get('body', ''),
                issue.get('labels', [])
            )
            
            # Calculate reward
            metrics = IssueMetrics(
                pr_success=(issue.get('pr_number') is not None),
                code_quality=0.7,  # Default assuming good quality
                agent_score=0.7    # Default
            )
            reward = metrics.calculate_reward()
            
            # Update statistics
            if issue_type in self.issue_types:
                self.issue_types[issue_type].total_attempts += 1
                self.issue_types[issue_type].total_reward += reward
        
        self.save_state()
        print(f"Updated state from {len(history.get('issues', []))} historical issues")
    
    def generate_priority_report(self, issues: List[Dict]) -> str:
        """Generate a markdown report of prioritized issues
        
        Args:
            issues: List of issue dictionaries with priority info
        
        Returns:
            Markdown formatted report
        """
        # Sort by priority score
        sorted_issues = sorted(issues, key=lambda x: x['priority_score'], reverse=True)
        
        report = [
            "# 🎯 Issue Priority Report",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Total Issues:** {len(issues)}",
            "",
            "## Multi-Armed Bandit Statistics",
            "",
            "Issue type performance (learning from history):",
            ""
        ]
        
        # Add type statistics
        for type_name, issue_type in sorted(
            self.issue_types.items(), 
            key=lambda x: x[1].average_reward(), 
            reverse=True
        ):
            avg_reward = issue_type.average_reward()
            attempts = issue_type.total_attempts
            report.append(
                f"- **{type_name}**: {avg_reward:.2f} avg reward "
                f"({attempts} attempts)"
            )
        
        report.extend([
            "",
            "## 🔥 Priority Tiers",
            ""
        ])
        
        # Group by tier
        tiers = defaultdict(list)
        for issue in sorted_issues:
            tiers[issue['priority_tier']].append(issue)
        
        for tier_name in ["P0-Critical", "P1-High", "P2-Medium", "P3-Low"]:
            if tier_name in tiers:
                report.append(f"### {tier_name}")
                report.append("")
                for issue in tiers[tier_name]:
                    report.append(
                        f"- **#{issue['issue_number']}**: {issue['title']} "
                        f"(Type: {issue['issue_type']}, Score: {issue['priority_score']})"
                    )
                    report.append(f"  - Action: {issue['recommended_action']}")
                report.append("")
        
        return "\n".join(report)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Autonomous Issue Prioritizer using Multi-Armed Bandits'
    )
    parser.add_argument(
        'command',
        choices=['update', 'prioritize', 'report', 'stats'],
        help='Command to execute'
    )
    parser.add_argument(
        '--issue-number',
        type=int,
        help='Issue number to prioritize'
    )
    parser.add_argument(
        '--title',
        help='Issue title'
    )
    parser.add_argument(
        '--body',
        default='',
        help='Issue body'
    )
    parser.add_argument(
        '--labels',
        nargs='*',
        default=[],
        help='Issue labels'
    )
    
    args = parser.parse_args()
    
    prioritizer = IssuePrioritizer()
    
    if args.command == 'update':
        # Update from historical data
        prioritizer.update_from_history()
        print("✅ Updated bandit state from history")
    
    elif args.command == 'prioritize':
        # Prioritize a single issue
        if not args.issue_number or not args.title:
            print("Error: --issue-number and --title required", file=sys.stderr)
            sys.exit(1)
        
        result = prioritizer.prioritize_issue(
            args.issue_number,
            args.title,
            args.body,
            args.labels
        )
        
        print(json.dumps(result, indent=2))
    
    elif args.command == 'report':
        # Generate report for all active issues
        # For now, just show statistics
        print(prioritizer.generate_priority_report([]))
    
    elif args.command == 'stats':
        # Show current statistics
        print("📊 Multi-Armed Bandit Statistics\n")
        total = sum(t.total_attempts for t in prioritizer.issue_types.values())
        print(f"Total trials: {total}\n")
        
        for name, itype in sorted(
            prioritizer.issue_types.items(),
            key=lambda x: x[1].average_reward(),
            reverse=True
        ):
            avg = itype.average_reward()
            ucb1 = itype.ucb1_score(total) if total > 0 else 0
            print(f"{name:15} | Attempts: {itype.total_attempts:3} | "
                  f"Avg Reward: {avg:.3f} | UCB1: {ucb1:.3f}")


if __name__ == '__main__':
    main()
