#!/usr/bin/env python3
"""
Autonomous Issue Prioritizer using Multi-Armed Bandits

This module implements an intelligent issue prioritization system using Thompson Sampling,
a Bayesian approach to the multi-armed bandit problem. It learns from historical data to 
optimize issue assignment and prioritization for faster resolution times.

The system tracks:
- Success rates for different issue types
- Agent performance on various issue categories
- Resolution times and quality metrics
- Exploration vs exploitation tradeoffs

Author: @APIs-architect
Inspired by: Margaret Hamilton - rigorous and innovative
"""

import json
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum


class PriorityLevel(Enum):
    """Priority levels for issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    
    def to_score(self) -> float:
        """Convert priority to numeric score."""
        scores = {
            PriorityLevel.CRITICAL: 1.0,
            PriorityLevel.HIGH: 0.75,
            PriorityLevel.MEDIUM: 0.5,
            PriorityLevel.LOW: 0.25
        }
        return scores[self]


@dataclass
class IssueArm:
    """Represents an 'arm' in the multi-armed bandit - a category of issues."""
    category: str
    successes: int = 0  # Beta distribution alpha parameter
    failures: int = 0   # Beta distribution beta parameter
    total_pulls: int = 0
    avg_resolution_time_hours: float = 0.0
    last_updated: str = ""
    
    def update(self, success: bool, resolution_time_hours: float) -> None:
        """Update arm statistics based on outcome."""
        if success:
            self.successes += 1
        else:
            self.failures += 1
        
        self.total_pulls += 1
        
        # Update running average of resolution time
        if self.avg_resolution_time_hours == 0.0:
            self.avg_resolution_time_hours = resolution_time_hours
        else:
            # Exponential moving average
            alpha = 0.3
            self.avg_resolution_time_hours = (
                alpha * resolution_time_hours + 
                (1 - alpha) * self.avg_resolution_time_hours
            )
        
        self.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    @property
    def success_rate(self) -> float:
        """Calculate empirical success rate."""
        if self.total_pulls == 0:
            return 0.5  # Prior
        return self.successes / self.total_pulls
    
    def sample_thompson(self) -> float:
        """Sample from Beta distribution for Thompson Sampling."""
        # Beta(1, 1) is uniform prior - no information
        alpha = self.successes + 1
        beta = self.failures + 1
        
        # Sample from Beta distribution
        return random.betavariate(alpha, beta)


@dataclass
class IssuePriority:
    """Priority decision for an issue."""
    issue_number: int
    category: str
    priority: PriorityLevel
    confidence: float
    estimated_resolution_hours: float
    recommended_agent: Optional[str] = None
    reasoning: str = ""


class IssuePrioritizer:
    """
    Multi-armed bandit issue prioritizer using Thompson Sampling.
    
    Thompson Sampling is a Bayesian approach that naturally balances exploration
    (trying issues we know less about) and exploitation (prioritizing issues we
    know work well). It's optimal in the sense of minimizing regret over time.
    """
    
    def __init__(self, registry_path: str = ".github/agent-system/issue_prioritizer.json"):
        """
        Initialize the issue prioritizer.
        
        Args:
            registry_path: Path to the prioritizer state file
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_registry_exists()
    
    def _ensure_registry_exists(self) -> None:
        """Ensure the registry file exists with proper structure."""
        if not self.registry_path.exists():
            initial_registry = {
                "version": "1.0.0",
                "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "config": {
                    "min_samples_for_exploitation": 10,
                    "exploration_bonus": 0.1,
                    "time_decay_factor": 0.95,
                    "categories": [
                        "bug",
                        "feature",
                        "documentation",
                        "refactoring",
                        "security",
                        "performance",
                        "testing",
                        "infrastructure",
                        "ai-idea",
                        "other"
                    ]
                },
                "arms": {},
                "history": [],
                "stats": {
                    "total_decisions": 0,
                    "total_successes": 0,
                    "total_failures": 0,
                    "avg_resolution_time_hours": 0.0
                }
            }
            
            # Initialize arms for each category
            for category in initial_registry["config"]["categories"]:
                initial_registry["arms"][category] = asdict(IssueArm(category=category))
            
            self._write_registry(initial_registry)
    
    def _read_registry(self) -> Dict[str, Any]:
        """Read the prioritizer registry."""
        try:
            with open(self.registry_path, 'r') as f:
                content = f.read()
                if not content.strip():
                    raise json.JSONDecodeError("Empty file", "", 0)
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            # Defensive: if registry is corrupted, reinitialize
            if self.registry_path.exists():
                # Backup corrupted file
                backup_path = self.registry_path.with_suffix('.corrupted')
                self.registry_path.rename(backup_path)
            self._ensure_registry_exists()
            with open(self.registry_path, 'r') as f:
                return json.load(f)
    
    def _write_registry(self, registry: Dict[str, Any]) -> None:
        """Write the prioritizer registry atomically."""
        temp_path = self.registry_path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(registry, f, indent=2)
        temp_path.replace(self.registry_path)
    
    def _categorize_issue(self, title: str, body: str = "", labels: List[str] = None) -> str:
        """
        Categorize an issue based on its content.
        
        Args:
            title: Issue title
            body: Issue body
            labels: Issue labels
            
        Returns:
            Category name
        """
        labels = labels or []
        combined_text = f"{title} {body}".lower()
        
        # Check labels first
        registry = self._read_registry()
        categories = registry["config"]["categories"]
        
        for label in labels:
            label_lower = label.lower()
            if label_lower in categories:
                return label_lower
        
        # Pattern matching for common categories
        patterns = {
            "bug": ["bug", "error", "fix", "broken", "issue", "crash", "fail"],
            "feature": ["feature", "enhancement", "add", "new", "implement", "create"],
            "documentation": ["doc", "documentation", "readme", "guide", "tutorial"],
            "refactoring": ["refactor", "cleanup", "reorganize", "simplify", "optimize"],
            "security": ["security", "vulnerability", "cve", "exploit", "auth", "permission"],
            "performance": ["performance", "slow", "optimize", "speed", "bottleneck"],
            "testing": ["test", "testing", "coverage", "unit test", "integration test"],
            "infrastructure": ["infrastructure", "ci", "cd", "workflow", "pipeline", "deploy"],
            "ai-idea": ["ai idea", "ai-generated", "autonomous", "agent", "learning"]
        }
        
        # Score each category
        scores = {}
        for category, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return "other"
    
    def prioritize_issue(
        self,
        issue_number: int,
        title: str,
        body: str = "",
        labels: List[str] = None,
        current_open_issues: int = 0
    ) -> IssuePriority:
        """
        Prioritize an issue using Thompson Sampling.
        
        Args:
            issue_number: Issue number
            title: Issue title
            body: Issue body
            labels: Issue labels
            current_open_issues: Number of currently open issues
            
        Returns:
            IssuePriority object with priority decision
        """
        registry = self._read_registry()
        
        # Categorize the issue
        category = self._categorize_issue(title, body, labels)
        
        # Get or create arm for this category
        if category not in registry["arms"]:
            registry["arms"][category] = asdict(IssueArm(category=category))
            self._write_registry(registry)
        
        arm_data = registry["arms"][category]
        arm = IssueArm(**arm_data)
        
        # Sample from Thompson Sampling
        sampled_value = arm.sample_thompson()
        
        # Adjust for current workload
        workload_factor = max(0.5, 1.0 - (current_open_issues / 100.0))
        adjusted_value = sampled_value * workload_factor
        
        # Determine priority level
        if adjusted_value >= 0.75:
            priority = PriorityLevel.CRITICAL
        elif adjusted_value >= 0.6:
            priority = PriorityLevel.HIGH
        elif adjusted_value >= 0.4:
            priority = PriorityLevel.MEDIUM
        else:
            priority = PriorityLevel.LOW
        
        # Estimate resolution time based on historical data
        if arm.total_pulls > 0 and arm.avg_resolution_time_hours > 0:
            estimated_hours = arm.avg_resolution_time_hours
        else:
            # Default estimates based on category
            default_estimates = {
                "bug": 8.0,
                "feature": 24.0,
                "documentation": 4.0,
                "refactoring": 16.0,
                "security": 12.0,
                "performance": 20.0,
                "testing": 6.0,
                "infrastructure": 16.0,
                "ai-idea": 12.0,
                "other": 10.0
            }
            estimated_hours = default_estimates.get(category, 10.0)
        
        # Calculate confidence (always at least 0.1 for new categories)
        confidence = max(0.1, min(1.0, arm.total_pulls / 20.0))  # Full confidence after 20 samples
        
        # Generate reasoning
        reasoning = self._generate_reasoning(arm, category, sampled_value, priority)
        
        result = IssuePriority(
            issue_number=issue_number,
            category=category,
            priority=priority,
            confidence=confidence,
            estimated_resolution_hours=estimated_hours,
            reasoning=reasoning
        )
        
        # Record the decision
        registry["history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "issue_number": issue_number,
            "category": category,
            "priority": priority.value,
            "sampled_value": sampled_value,
            "confidence": confidence
        })
        
        # Keep history to last 1000 entries
        if len(registry["history"]) > 1000:
            registry["history"] = registry["history"][-1000:]
        
        registry["stats"]["total_decisions"] += 1
        self._write_registry(registry)
        
        return result
    
    def _generate_reasoning(
        self,
        arm: IssueArm,
        category: str,
        sampled_value: float,
        priority: PriorityLevel
    ) -> str:
        """Generate human-readable reasoning for the priority decision."""
        if arm.total_pulls == 0:
            return f"New category '{category}' - exploring to gather data"
        
        success_rate = arm.success_rate
        
        reasoning_parts = [
            f"Category '{category}' has {success_rate:.1%} historical success rate",
            f"({arm.successes} successes, {arm.failures} failures)"
        ]
        
        if arm.avg_resolution_time_hours > 0:
            reasoning_parts.append(
                f"Average resolution time: {arm.avg_resolution_time_hours:.1f} hours"
            )
        
        if sampled_value > success_rate * 1.2:
            reasoning_parts.append("Optimistic sampling suggests prioritization")
        elif sampled_value < success_rate * 0.8:
            reasoning_parts.append("Conservative sampling suggests lower priority")
        
        return ". ".join(reasoning_parts)
    
    def record_outcome(
        self,
        issue_number: int,
        category: str,
        success: bool,
        resolution_time_hours: float
    ) -> None:
        """
        Record the outcome of handling an issue to update the bandit.
        
        Args:
            issue_number: Issue number
            category: Issue category
            success: Whether the issue was successfully resolved
            resolution_time_hours: Time taken to resolve in hours
        """
        registry = self._read_registry()
        
        if category not in registry["arms"]:
            # Category doesn't exist yet, create it
            registry["arms"][category] = asdict(IssueArm(category=category))
        
        arm_data = registry["arms"][category]
        arm = IssueArm(**arm_data)
        
        # Update the arm
        arm.update(success, resolution_time_hours)
        registry["arms"][category] = asdict(arm)
        
        # Update global stats (outcomes only, not decisions)
        stats = registry["stats"]
        if success:
            stats["total_successes"] += 1
        else:
            stats["total_failures"] += 1
        
        # Update average resolution time
        if stats["avg_resolution_time_hours"] == 0:
            stats["avg_resolution_time_hours"] = resolution_time_hours
        else:
            # Exponential moving average
            alpha = 0.2
            stats["avg_resolution_time_hours"] = (
                alpha * resolution_time_hours +
                (1 - alpha) * stats["avg_resolution_time_hours"]
            )
        
        self._write_registry(registry)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall prioritizer statistics."""
        registry = self._read_registry()
        
        stats = {
            "overall": registry["stats"],
            "categories": {}
        }
        
        for category, arm_data in registry["arms"].items():
            arm = IssueArm(**arm_data)
            stats["categories"][category] = {
                "success_rate": arm.success_rate,
                "total_pulls": arm.total_pulls,
                "avg_resolution_time_hours": arm.avg_resolution_time_hours,
                "last_updated": arm.last_updated
            }
        
        return stats
    
    def get_top_priorities(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top N priority categories based on Thompson Sampling.
        
        Args:
            n: Number of top categories to return
            
        Returns:
            List of category information sorted by sampled priority
        """
        registry = self._read_registry()
        
        categories = []
        for category, arm_data in registry["arms"].items():
            arm = IssueArm(**arm_data)
            sampled_value = arm.sample_thompson()
            
            categories.append({
                "category": category,
                "sampled_priority": sampled_value,
                "success_rate": arm.success_rate,
                "total_pulls": arm.total_pulls,
                "avg_resolution_time_hours": arm.avg_resolution_time_hours
            })
        
        # Sort by sampled priority
        categories.sort(key=lambda x: x["sampled_priority"], reverse=True)
        
        return categories[:n]


def main():
    """CLI interface for the issue prioritizer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous Issue Prioritizer using Multi-Armed Bandits"
    )
    parser.add_argument("command", choices=["prioritize", "record", "stats", "top"])
    parser.add_argument("--issue-number", type=int, help="Issue number")
    parser.add_argument("--title", help="Issue title")
    parser.add_argument("--body", default="", help="Issue body")
    parser.add_argument("--labels", nargs="*", default=[], help="Issue labels")
    parser.add_argument("--category", help="Issue category")
    parser.add_argument("--success", action="store_true", help="Issue was successful")
    parser.add_argument("--resolution-time", type=float, help="Resolution time in hours")
    parser.add_argument("--registry", default=".github/agent-system/issue_prioritizer.json",
                       help="Registry path")
    parser.add_argument("-n", type=int, default=10, help="Number of results for 'top' command")
    
    args = parser.parse_args()
    
    prioritizer = IssuePrioritizer(registry_path=args.registry)
    
    if args.command == "prioritize":
        if not args.title:
            print("Error: --title required for prioritize command")
            return 1
        
        result = prioritizer.prioritize_issue(
            issue_number=args.issue_number or 0,
            title=args.title,
            body=args.body,
            labels=args.labels
        )
        
        print(f"\n🎯 Issue Priority Decision")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Category:     {result.category}")
        print(f"Priority:     {result.priority.value.upper()}")
        print(f"Confidence:   {result.confidence:.1%}")
        print(f"Est. Time:    {result.estimated_resolution_hours:.1f} hours")
        print(f"\n💡 Reasoning:")
        print(f"   {result.reasoning}")
        
    elif args.command == "record":
        if not args.category or args.resolution_time is None:
            print("Error: --category and --resolution-time required for record command")
            return 1
        
        prioritizer.record_outcome(
            issue_number=args.issue_number or 0,
            category=args.category,
            success=args.success,
            resolution_time_hours=args.resolution_time
        )
        
        print(f"✅ Recorded outcome for {args.category}: " +
              f"{'success' if args.success else 'failure'} " +
              f"in {args.resolution_time:.1f} hours")
    
    elif args.command == "stats":
        stats = prioritizer.get_stats()
        
        print(f"\n📊 Issue Prioritizer Statistics")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\nOverall:")
        overall = stats["overall"]
        print(f"  Total Decisions:  {overall['total_decisions']}")
        print(f"  Successes:        {overall['total_successes']}")
        print(f"  Failures:         {overall['total_failures']}")
        if overall['total_decisions'] > 0:
            success_rate = overall['total_successes'] / overall['total_decisions']
            print(f"  Success Rate:     {success_rate:.1%}")
        print(f"  Avg Resolution:   {overall['avg_resolution_time_hours']:.1f} hours")
        
        print(f"\n📁 Categories:")
        for category, cat_stats in sorted(stats["categories"].items()):
            if cat_stats["total_pulls"] > 0:
                print(f"\n  {category}:")
                print(f"    Success Rate:     {cat_stats['success_rate']:.1%}")
                print(f"    Samples:          {cat_stats['total_pulls']}")
                print(f"    Avg Resolution:   {cat_stats['avg_resolution_time_hours']:.1f}h")
    
    elif args.command == "top":
        top_categories = prioritizer.get_top_priorities(n=args.n)
        
        print(f"\n🏆 Top {args.n} Priority Categories (Thompson Sampling)")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for i, cat in enumerate(top_categories, 1):
            print(f"\n{i}. {cat['category'].upper()}")
            print(f"   Sampled Priority:  {cat['sampled_priority']:.3f}")
            print(f"   Success Rate:      {cat['success_rate']:.1%}")
            print(f"   Total Samples:     {cat['total_pulls']}")
            print(f"   Avg Resolution:    {cat['avg_resolution_time_hours']:.1f}h")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
