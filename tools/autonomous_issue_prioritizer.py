#!/usr/bin/env python3
"""
Autonomous Issue Prioritizer using Multi-Armed Bandits
Author: @create-botter (Nikola Tesla)

An intelligent system that learns optimal issue prioritization strategies using
Thompson Sampling (Bayesian Multi-Armed Bandit algorithm). The system balances
exploration of new strategies with exploitation of proven approaches, continuously
adapting based on issue resolution outcomes.

Key Features:
- Thompson Sampling for Bayesian optimization
- Multiple prioritization arms (urgency, complexity, impact, agent load)
- Persistent state tracking across sessions
- Integration with GitHub Issues API
- Real-time learning from resolution outcomes
- Adaptive confidence-based prioritization

Inspired by Nikola Tesla's vision of intelligent, self-optimizing systems.
"""

import json
import os
import sys
import time
import argparse
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import math


@dataclass
class BanditArm:
    """Represents a prioritization strategy (arm) in the multi-armed bandit"""
    name: str
    description: str
    successes: int = 0  # Beta distribution alpha parameter
    failures: int = 0   # Beta distribution beta parameter
    pulls: int = 0      # Total times this arm was selected
    total_reward: float = 0.0
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'BanditArm':
        return BanditArm(**data)
    
    def sample_theta(self) -> float:
        """Sample from Beta distribution for Thompson Sampling"""
        # Add 1 to avoid Beta(0,0)
        alpha = self.successes + 1
        beta = self.failures + 1
        
        # Simple Beta sampling using uniform random variables
        # This is a simplified implementation; for production, use numpy.random.beta
        return self._beta_sample(alpha, beta)
    
    def _beta_sample(self, alpha: float, beta: float) -> float:
        """
        Beta distribution sampling using Gamma-based method.
        
        Beta(α, β) can be sampled as: X ~ Gamma(α,1), Y ~ Gamma(β,1), then Beta = X/(X+Y)
        This is mathematically correct and doesn't require numpy.
        """
        # Simple Gamma(shape, scale=1) sampling using Marsaglia and Tsang method
        def gamma_sample(shape):
            """Sample from Gamma(shape, 1) using acceptance-rejection"""
            if shape < 1:
                # For shape < 1, use Ahrens-Dieter method
                shape_adj = shape + 1
                gamma_val = gamma_sample(shape_adj)
                u = random.random()
                return gamma_val * (u ** (1.0 / shape))
            
            # For shape >= 1, use Marsaglia-Tsang method (simplified)
            d = shape - 1.0 / 3.0
            c = 1.0 / math.sqrt(9.0 * d)
            
            while True:
                # Sample from standard normal (Box-Muller)
                u1 = random.random()
                u2 = random.random()
                z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
                
                v = (1.0 + c * z) ** 3
                
                if v <= 0:
                    continue
                
                u = random.random()
                
                if math.log(u) < 0.5 * z * z + d - d * v + d * math.log(v):
                    return d * v
        
        # Sample from Beta using Gamma ratio
        if alpha <= 0 or beta <= 0:
            return 0.5  # Fallback for invalid parameters
        
        x = gamma_sample(alpha)
        y = gamma_sample(beta)
        
        if x + y == 0:
            return 0.5
        
        return x / (x + y)
    
    def update(self, reward: float):
        """Update arm statistics based on reward (0.0 to 1.0)"""
        self.pulls += 1
        self.total_reward += reward
        
        # Binary reward: success if reward > 0.5, failure otherwise
        if reward > 0.5:
            self.successes += 1
        else:
            self.failures += 1
    
    def expected_value(self) -> float:
        """Calculate expected value (mean of Beta distribution)"""
        alpha = self.successes + 1
        beta = self.failures + 1
        return alpha / (alpha + beta)
    
    def confidence_interval(self) -> Tuple[float, float]:
        """Calculate 95% confidence interval"""
        alpha = self.successes + 1
        beta = self.failures + 1
        mean = alpha / (alpha + beta)
        
        # Approximate standard deviation for Beta distribution
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        std = math.sqrt(variance)
        
        # 95% CI (approximately 2 standard deviations)
        return (max(0.0, mean - 2 * std), min(1.0, mean + 2 * std))


@dataclass
class Issue:
    """Represents a GitHub issue for prioritization"""
    number: int
    title: str
    body: str
    labels: List[str]
    state: str
    created_at: str
    author: str
    comments: int = 0
    assigned_agent: Optional[str] = None
    
    # Computed features
    urgency_score: float = 0.0
    complexity_score: float = 0.0
    impact_score: float = 0.0
    age_days: float = 0.0
    
    def to_dict(self):
        data = asdict(self)
        return data


@dataclass
class PriorityRecommendation:
    """Recommendation from the prioritizer"""
    issue_number: int
    priority_score: float
    selected_arm: str
    confidence: float
    reasoning: str
    features: Dict[str, float]
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class AutonomousIssuePrioritizer:
    """
    Multi-Armed Bandit based issue prioritizer using Thompson Sampling.
    
    The system maintains multiple prioritization strategies (arms) and learns
    which strategies lead to successful issue resolutions. It uses Bayesian
    optimization to balance exploration and exploitation.
    
    Available Arms:
    - urgency: Prioritize based on age and urgency labels
    - complexity: Prioritize based on estimated complexity
    - impact: Prioritize based on potential impact
    - balanced: Weighted combination of all factors
    """
    
    def __init__(self, state_file: Optional[str] = None):
        """Initialize the prioritizer"""
        self.state_file = state_file or os.path.join(
            os.path.dirname(__file__), 
            'data', 
            'issue_prioritizer_state.json'
        )
        
        # Initialize bandit arms
        self.arms = {
            'urgency': BanditArm(
                name='urgency',
                description='Prioritize urgent and time-sensitive issues'
            ),
            'complexity': BanditArm(
                name='complexity',
                description='Prioritize simple issues for quick wins'
            ),
            'impact': BanditArm(
                name='impact',
                description='Prioritize high-impact issues'
            ),
            'balanced': BanditArm(
                name='balanced',
                description='Balanced approach considering all factors'
            ),
            'exploration': BanditArm(
                name='exploration',
                description='Try random prioritization to explore'
            )
        }
        
        # History tracking
        self.history: List[Dict[str, Any]] = []
        self.recommendations: List[PriorityRecommendation] = []
        
        # Load existing state
        self.load_state()
    
    def compute_features(self, issue: Issue) -> Dict[str, float]:
        """Compute feature scores for an issue"""
        features = {}
        
        # Age-based urgency (older = more urgent)
        # Handle both 'Z' suffix and timezone-aware formats
        created_str = issue.created_at.replace('Z', '+00:00')
        created = datetime.fromisoformat(created_str)
        age = (datetime.now(timezone.utc) - created).total_seconds() / 86400
        issue.age_days = age
        features['age_days'] = age
        features['age_urgency'] = min(1.0, age / 30.0)  # Normalize to 30 days
        
        # Label-based urgency
        urgency_labels = {'urgent', 'critical', 'high-priority', 'blocker'}
        has_urgent = any(label.lower() in urgency_labels for label in issue.labels)
        features['label_urgency'] = 1.0 if has_urgent else 0.0
        
        # Complexity estimation (simple heuristic based on title/body length)
        title_words = len(issue.title.split())
        body_words = len(issue.body.split()) if issue.body else 0
        features['title_length'] = min(1.0, title_words / 20.0)
        features['body_length'] = min(1.0, body_words / 500.0)
        features['complexity'] = (features['title_length'] + features['body_length']) / 2
        
        # Impact estimation (based on labels and keywords)
        impact_labels = {'feature', 'enhancement', 'bug', 'security'}
        impact_keywords = {'critical', 'important', 'major', 'significant'}
        
        label_impact = sum(1 for label in issue.labels if label.lower() in impact_labels)
        
        # Safely handle None body
        issue_text = (issue.title + ' ' + (issue.body or '')).lower()
        keyword_impact = sum(1 for keyword in impact_keywords if keyword in issue_text)
        
        features['label_impact'] = min(1.0, label_impact / 3.0)
        features['keyword_impact'] = min(1.0, keyword_impact / 2.0)
        features['impact'] = (features['label_impact'] + features['keyword_impact']) / 2
        
        # Engagement (comments indicate importance)
        features['engagement'] = min(1.0, issue.comments / 10.0)
        
        # Store computed scores
        issue.urgency_score = (features['age_urgency'] + features['label_urgency']) / 2
        issue.complexity_score = features['complexity']
        issue.impact_score = features['impact']
        
        return features
    
    def compute_priority_score(self, issue: Issue, arm_name: str) -> float:
        """Compute priority score based on selected arm strategy"""
        features = self.compute_features(issue)
        
        if arm_name == 'urgency':
            # High priority for urgent issues
            return features['age_urgency'] * 0.6 + features['label_urgency'] * 0.4
        
        elif arm_name == 'complexity':
            # Prefer simpler issues (inverse of complexity)
            return 1.0 - features['complexity']
        
        elif arm_name == 'impact':
            # High priority for high-impact issues
            return features['impact'] * 0.7 + features['engagement'] * 0.3
        
        elif arm_name == 'balanced':
            # Balanced weighted combination
            return (
                features['age_urgency'] * 0.25 +
                features['label_urgency'] * 0.15 +
                (1.0 - features['complexity']) * 0.20 +
                features['impact'] * 0.25 +
                features['engagement'] * 0.15
            )
        
        elif arm_name == 'exploration':
            # Random exploration
            return random.random()
        
        else:
            # Default to balanced
            return (features['age_urgency'] + features['impact']) / 2
    
    def select_arm(self) -> str:
        """Select arm using Thompson Sampling"""
        # Sample from each arm's posterior distribution
        samples = {name: arm.sample_theta() for name, arm in self.arms.items()}
        
        # Select arm with highest sample
        selected_arm = max(samples, key=samples.get)
        
        return selected_arm
    
    def prioritize_issue(self, issue: Issue) -> PriorityRecommendation:
        """Generate priority recommendation for an issue"""
        # Select arm using Thompson Sampling
        selected_arm = self.select_arm()
        
        # Compute priority score
        priority_score = self.compute_priority_score(issue, selected_arm)
        
        # Compute confidence
        arm = self.arms[selected_arm]
        confidence = arm.expected_value()
        ci_low, ci_high = arm.confidence_interval()
        
        # Generate reasoning
        reasoning = self._generate_reasoning(issue, selected_arm, priority_score)
        
        # Create recommendation
        features = self.compute_features(issue)
        recommendation = PriorityRecommendation(
            issue_number=issue.number,
            priority_score=priority_score,
            selected_arm=selected_arm,
            confidence=confidence,
            reasoning=reasoning,
            features=features,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.recommendations.append(recommendation)
        
        return recommendation
    
    def prioritize_issues(self, issues: List[Issue]) -> List[PriorityRecommendation]:
        """Prioritize a batch of issues"""
        recommendations = []
        
        for issue in issues:
            rec = self.prioritize_issue(issue)
            recommendations.append(rec)
        
        # Sort by priority score (descending)
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        
        return recommendations
    
    def _generate_reasoning(self, issue: Issue, arm: str, score: float) -> str:
        """Generate human-readable reasoning"""
        reasoning_parts = [
            f"Strategy: {arm}",
            f"Priority Score: {score:.2f}",
            f"Age: {issue.age_days:.1f} days",
            f"Urgency: {issue.urgency_score:.2f}",
            f"Complexity: {issue.complexity_score:.2f}",
            f"Impact: {issue.impact_score:.2f}"
        ]
        
        return " | ".join(reasoning_parts)
    
    def record_outcome(self, issue_number: int, success: bool):
        """Record the outcome of an issue prioritization"""
        # Find the recommendation for this issue
        rec = None
        for r in self.recommendations:
            if r.issue_number == issue_number:
                rec = r
                break
        
        if rec is None:
            print(f"Warning: No recommendation found for issue {issue_number}")
            return
        
        # Update the arm that was used
        reward = 1.0 if success else 0.0
        arm_name = rec.selected_arm
        self.arms[arm_name].update(reward)
        
        # Record in history
        self.history.append({
            'issue_number': issue_number,
            'arm': arm_name,
            'success': success,
            'reward': reward,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        # Save state
        self.save_state()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics for all arms"""
        stats = {
            'arms': {},
            'total_recommendations': len(self.recommendations),
            'total_outcomes': len(self.history),
            'success_rate': 0.0
        }
        
        for name, arm in self.arms.items():
            stats['arms'][name] = {
                'name': name,
                'description': arm.description,
                'pulls': arm.pulls,
                'successes': arm.successes,
                'failures': arm.failures,
                'expected_value': arm.expected_value(),
                'confidence_interval': arm.confidence_interval(),
                'total_reward': arm.total_reward
            }
        
        # Overall success rate
        if self.history:
            successes = sum(1 for h in self.history if h['success'])
            stats['success_rate'] = successes / len(self.history)
        
        return stats
    
    def save_state(self):
        """Save current state to disk"""
        state = {
            'arms': {name: arm.to_dict() for name, arm in self.arms.items()},
            'history': self.history,
            'recommendations': [r.to_dict() for r in self.recommendations],
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        # Write state
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        """Load state from disk"""
        if not os.path.exists(self.state_file):
            return
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            # Load arms
            for name, arm_data in state.get('arms', {}).items():
                self.arms[name] = BanditArm.from_dict(arm_data)
            
            # Load history
            self.history = state.get('history', [])
            
            # Load recommendations
            recs_data = state.get('recommendations', [])
            self.recommendations = [
                PriorityRecommendation(**r) for r in recs_data
            ]
            
        except Exception as e:
            print(f"Warning: Failed to load state: {e}")
    
    def reset(self):
        """Reset all arm statistics (use with caution)"""
        for arm in self.arms.values():
            arm.successes = 0
            arm.failures = 0
            arm.pulls = 0
            arm.total_reward = 0.0
        
        self.history = []
        self.recommendations = []
        self.save_state()


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Autonomous Issue Prioritizer using Multi-Armed Bandits'
    )
    parser.add_argument(
        '--state-file',
        help='Path to state file',
        default=None
    )
    parser.add_argument(
        '--action',
        choices=['prioritize', 'record', 'stats', 'reset'],
        required=True,
        help='Action to perform'
    )
    parser.add_argument(
        '--issue-data',
        help='JSON file containing issue data for prioritization'
    )
    parser.add_argument(
        '--issue-number',
        type=int,
        help='Issue number for recording outcome'
    )
    parser.add_argument(
        '--success',
        action='store_true',
        help='Issue was successfully resolved'
    )
    parser.add_argument(
        '--output',
        help='Output file for recommendations'
    )
    
    args = parser.parse_args()
    
    # Initialize prioritizer
    prioritizer = AutonomousIssuePrioritizer(state_file=args.state_file)
    
    if args.action == 'prioritize':
        # Load issues
        if not args.issue_data:
            print("Error: --issue-data required for prioritize action")
            return 1
        
        with open(args.issue_data, 'r') as f:
            issues_data = json.load(f)
        
        issues = [Issue(**issue_data) for issue_data in issues_data]
        
        # Prioritize
        recommendations = prioritizer.prioritize_issues(issues)
        
        # Output
        output_data = [r.to_dict() for r in recommendations]
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Wrote recommendations to {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
    
    elif args.action == 'record':
        # Record outcome
        if args.issue_number is None:
            print("Error: --issue-number required for record action")
            return 1
        
        prioritizer.record_outcome(args.issue_number, args.success)
        print(f"Recorded {'success' if args.success else 'failure'} for issue {args.issue_number}")
    
    elif args.action == 'stats':
        # Print statistics
        stats = prioritizer.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.action == 'reset':
        # Reset state
        confirm = input("Are you sure you want to reset all statistics? (yes/no): ")
        if confirm.lower() == 'yes':
            prioritizer.reset()
            print("State reset successfully")
        else:
            print("Reset cancelled")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
