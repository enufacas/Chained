#!/usr/bin/env python3
"""
Example: Autonomous Issue Prioritizer Demo
Author: @create-botter (Nikola Tesla)

Demonstrates the multi-armed bandit issue prioritizer with realistic scenarios.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_issue_prioritizer import (
    AutonomousIssuePrioritizer,
    Issue
)


def create_sample_issues():
    """Create a diverse set of sample issues"""
    base_time = datetime.now(timezone.utc)
    
    issues = [
        # Old urgent bug
        Issue(
            number=1,
            title="Critical security vulnerability in authentication",
            body="Users' passwords are being logged in plaintext. This is a critical security issue that needs immediate attention.",
            labels=["security", "bug", "urgent"],
            state="open",
            created_at=(base_time - timedelta(days=45)).isoformat(),
            author="security-team",
            comments=12
        ),
        
        # Simple quick fix
        Issue(
            number=2,
            title="Fix typo in README",
            body="Small typo in installation instructions.",
            labels=["documentation"],
            state="open",
            created_at=(base_time - timedelta(days=2)).isoformat(),
            author="contributor",
            comments=1
        ),
        
        # Complex feature request
        Issue(
            number=3,
            title="Implement advanced machine learning pipeline with real-time data processing",
            body="We need to build a comprehensive ML pipeline that can handle real-time data streams, " +
                 "perform feature engineering, train models dynamically, and deploy them automatically. " +
                 "This involves integrating with multiple cloud services, setting up monitoring, " +
                 "implementing A/B testing capabilities, and creating a robust data versioning system. " * 3,
            labels=["feature", "enhancement"],
            state="open",
            created_at=(base_time - timedelta(days=10)).isoformat(),
            author="product-manager",
            comments=25
        ),
        
        # High-impact bug
        Issue(
            number=4,
            title="Application crashes on startup for 30% of users",
            body="Multiple users reporting that the app crashes immediately on startup. Affects iOS 15+ devices.",
            labels=["bug", "high-priority"],
            state="open",
            created_at=(base_time - timedelta(days=7)).isoformat(),
            author="support-team",
            comments=45
        ),
        
        # Medium priority enhancement
        Issue(
            number=5,
            title="Add dark mode support",
            body="Users have requested dark mode for better usability at night.",
            labels=["enhancement", "ui"],
            state="open",
            created_at=(base_time - timedelta(days=20)).isoformat(),
            author="designer",
            comments=8
        ),
        
        # Old low-priority issue
        Issue(
            number=6,
            title="Optimize image loading performance",
            body="Images could load faster with better caching strategies.",
            labels=["performance", "enhancement"],
            state="open",
            created_at=(base_time - timedelta(days=60)).isoformat(),
            author="developer",
            comments=3
        ),
        
        # Recent blocker
        Issue(
            number=7,
            title="Production deployment failing",
            body="CI/CD pipeline is broken. Cannot deploy to production.",
            labels=["blocker", "urgent", "infrastructure"],
            state="open",
            created_at=(base_time - timedelta(hours=6)).isoformat(),
            author="devops",
            comments=15
        ),
        
        # Feature with moderate complexity
        Issue(
            number=8,
            title="Add export to CSV functionality",
            body="Users want to export their data as CSV files for analysis.",
            labels=["feature"],
            state="open",
            created_at=(base_time - timedelta(days=14)).isoformat(),
            author="user-request",
            comments=5
        )
    ]
    
    return issues


def demo_basic_prioritization():
    """Demonstrate basic prioritization"""
    print("=" * 80)
    print("🎯 DEMO 1: Basic Prioritization")
    print("=" * 80)
    print()
    
    # Initialize prioritizer
    prioritizer = AutonomousIssuePrioritizer()
    
    # Create sample issues
    issues = create_sample_issues()
    
    print(f"Prioritizing {len(issues)} issues...")
    print()
    
    # Prioritize
    recommendations = prioritizer.prioritize_issues(issues)
    
    # Display top 5
    print("🏆 Top 5 Priority Issues:")
    print()
    for i, rec in enumerate(recommendations[:5], 1):
        issue = next(iss for iss in issues if iss.number == rec.issue_number)
        print(f"{i}. Issue #{issue.number}: {issue.title[:50]}...")
        print(f"   Priority Score: {rec.priority_score:.3f}")
        print(f"   Strategy: {rec.selected_arm}")
        print(f"   Confidence: {rec.confidence:.3f}")
        print(f"   Age: {issue.age_days:.1f} days")
        print(f"   Labels: {', '.join(issue.labels)}")
        print()
    
    return prioritizer, issues, recommendations


def demo_learning_from_outcomes(prioritizer, issues, recommendations):
    """Demonstrate learning from outcomes"""
    print("=" * 80)
    print("🧠 DEMO 2: Learning from Outcomes")
    print("=" * 80)
    print()
    
    print("Recording outcomes for resolved issues...")
    print()
    
    # Simulate resolving issues
    # High-priority issues resolve successfully
    outcomes = {
        1: True,   # Critical security - SUCCESS
        7: True,   # Production blocker - SUCCESS
        4: True,   # Crash bug - SUCCESS
        2: True,   # Simple typo - SUCCESS
        3: False,  # Complex ML - FAILURE (too complex)
        5: True,   # Dark mode - SUCCESS
        6: False,  # Old optimization - FAILURE (low priority)
    }
    
    for issue_number, success in outcomes.items():
        prioritizer.record_outcome(issue_number, success)
        status = "✅ SUCCESS" if success else "❌ FAILURE"
        issue = next(iss for iss in issues if iss.number == issue_number)
        print(f"{status}: Issue #{issue_number} - {issue.title[:50]}...")
    
    print()
    print("Learning complete! Updated arm statistics.")
    print()


def demo_statistics(prioritizer):
    """Demonstrate statistics"""
    print("=" * 80)
    print("📊 DEMO 3: Prioritizer Statistics")
    print("=" * 80)
    print()
    
    stats = prioritizer.get_statistics()
    
    print(f"Total Recommendations: {stats['total_recommendations']}")
    print(f"Total Outcomes Recorded: {stats['total_outcomes']}")
    print(f"Overall Success Rate: {stats['success_rate']:.1%}")
    print()
    
    print("Arm Performance:")
    print("-" * 80)
    print(f"{'Arm':<15} {'Pulls':<8} {'Success':<10} {'Failure':<10} {'Expected':<12} {'95% CI'}")
    print("-" * 80)
    
    for arm_name, arm_stats in stats['arms'].items():
        ci = arm_stats['confidence_interval']
        ci_str = f"[{ci[0]:.2f}, {ci[1]:.2f}]"
        
        print(f"{arm_name:<15} {arm_stats['pulls']:<8} "
              f"{arm_stats['successes']:<10} {arm_stats['failures']:<10} "
              f"{arm_stats['expected_value']:.3f}       {ci_str}")
    
    print()


def demo_adapted_prioritization(prioritizer):
    """Demonstrate how priorities change after learning"""
    print("=" * 80)
    print("🔄 DEMO 4: Adapted Prioritization (After Learning)")
    print("=" * 80)
    print()
    
    # Create new batch of similar issues
    base_time = datetime.now(timezone.utc)
    
    new_issues = [
        Issue(
            number=10,
            title="Another security issue in API",
            body="Potential SQL injection vulnerability.",
            labels=["security", "bug"],
            state="open",
            created_at=(base_time - timedelta(days=5)).isoformat(),
            author="security",
            comments=8
        ),
        Issue(
            number=11,
            title="Implement new advanced analytics dashboard with real-time updates",
            body="Complex feature requiring significant architecture changes " * 20,
            labels=["feature"],
            state="open",
            created_at=(base_time - timedelta(days=3)).isoformat(),
            author="product",
            comments=10
        ),
        Issue(
            number=12,
            title="Update copyright year",
            body="Simple one-line change.",
            labels=["documentation"],
            state="open",
            created_at=(base_time - timedelta(days=1)).isoformat(),
            author="contributor",
            comments=0
        )
    ]
    
    print("Prioritizing new issues with learned preferences...")
    print()
    
    recommendations = prioritizer.prioritize_issues(new_issues)
    
    for rec in recommendations:
        issue = next(iss for iss in new_issues if iss.number == rec.issue_number)
        print(f"Issue #{issue.number}: {issue.title[:60]}...")
        print(f"  Priority Score: {rec.priority_score:.3f}")
        print(f"  Strategy: {rec.selected_arm} (confidence: {rec.confidence:.3f})")
        print(f"  Reasoning: {rec.reasoning}")
        print()
    
    print("Note: The prioritizer has learned to prefer strategies that worked well!")
    print()


def demo_arm_comparison():
    """Compare different arm strategies"""
    print("=" * 80)
    print("⚔️  DEMO 5: Strategy Comparison")
    print("=" * 80)
    print()
    
    # Create a single issue
    issue = Issue(
        number=100,
        title="Important feature request with moderate complexity",
        body="This feature would benefit many users and is moderately complex to implement.",
        labels=["feature", "enhancement"],
        state="open",
        created_at=(datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
        author="user",
        comments=10
    )
    
    prioritizer = AutonomousIssuePrioritizer()
    
    print(f"Issue: {issue.title}")
    print()
    print("How each strategy would score this issue:")
    print("-" * 80)
    
    for arm_name in prioritizer.arms.keys():
        score = prioritizer.compute_priority_score(issue, arm_name)
        description = prioritizer.arms[arm_name].description
        print(f"{arm_name:<15} Score: {score:.3f}  |  {description}")
    
    print()
    print("Different strategies emphasize different aspects of the issue!")
    print()


def main():
    """Run all demos"""
    print()
    print("🚀 Autonomous Issue Prioritizer - Interactive Demo")
    print("Using Multi-Armed Bandits with Thompson Sampling")
    print()
    
    # Demo 1: Basic prioritization
    prioritizer, issues, recommendations = demo_basic_prioritization()
    
    input("Press Enter to continue to Demo 2...")
    print()
    
    # Demo 2: Learning from outcomes
    demo_learning_from_outcomes(prioritizer, issues, recommendations)
    
    input("Press Enter to continue to Demo 3...")
    print()
    
    # Demo 3: Statistics
    demo_statistics(prioritizer)
    
    input("Press Enter to continue to Demo 4...")
    print()
    
    # Demo 4: Adapted prioritization
    demo_adapted_prioritization(prioritizer)
    
    input("Press Enter to continue to Demo 5...")
    print()
    
    # Demo 5: Strategy comparison
    demo_arm_comparison()
    
    print("=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print()
    print("The prioritizer has learned from outcomes and adapted its strategy.")
    print("In production, this learning continues indefinitely, constantly improving.")
    print()
    print("Try it yourself:")
    print("  python3 tools/autonomous_issue_prioritizer.py --help")
    print()


if __name__ == '__main__':
    main()
