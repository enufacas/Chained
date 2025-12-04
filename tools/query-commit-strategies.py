#!/usr/bin/env python3
"""
Query Learned Commit Strategies

A utility for agents to access learned git commit strategies and get
context-aware recommendations for their work.

Created by @create-botter - Infrastructure for agent integration

Usage:
    python query-commit-strategies.py --context feature
    python query-commit-strategies.py --priority CRITICAL
    python query-commit-strategies.py --list-patterns
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import argparse


# Configuration constants
VALID_CONTEXTS = ['general', 'feature', 'bugfix', 'refactor', 'docs']
VALID_PRIORITIES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']


def load_latest_strategies() -> Optional[Dict[str, Any]]:
    """Load the most recent commit strategies file."""
    learnings_dir = Path("learnings")
    
    if not learnings_dir.exists():
        return None
    
    # Find all commit strategy files
    strategy_files = sorted(
        learnings_dir.glob("commit_strategies_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not strategy_files:
        # Try the base file
        base_file = learnings_dir / "commit_strategies.json"
        if base_file.exists():
            strategy_files = [base_file]
        else:
            return None
    
    # Load the most recent
    with open(strategy_files[0], 'r') as f:
        return json.load(f)


def get_recommendations(
    strategies: Dict[str, Any],
    context: Optional[str] = None,
    priority: Optional[str] = None,
    min_confidence: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Get filtered recommendations based on criteria.
    
    Args:
        strategies: Loaded strategies data
        context: Optional context filter (feature, bugfix, refactor, docs)
        priority: Optional priority filter (CRITICAL, HIGH, MEDIUM, LOW)
        min_confidence: Minimum confidence score
    
    Returns:
        List of matching recommendations
    """
    recommendations = strategies.get('recommendations', [])
    
    # Filter by priority
    if priority:
        recommendations = [
            r for r in recommendations
            if r.get('priority') == priority.upper()
        ]
    
    # Filter by confidence (if available)
    if min_confidence > 0:
        recommendations = [
            r for r in recommendations
            if r.get('confidence_score', 1.0) >= min_confidence
        ]
    
    return recommendations


def format_recommendation(rec: Dict[str, Any], index: int) -> str:
    """Format a recommendation for display."""
    lines = []
    
    priority_emoji = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢'
    }
    
    priority = rec.get('priority', 'MEDIUM')
    emoji = priority_emoji.get(priority, '⚪')
    
    lines.append(f"\n{index}. {emoji} [{priority}] {rec.get('title', 'No title')}")
    lines.append(f"   {rec.get('description', '')}")
    
    action_items = rec.get('action_items', [])
    if action_items:
        lines.append("\n   Action Items:")
        for item in action_items:
            lines.append(f"   • {item}")
    
    based_on = rec.get('based_on', '')
    if based_on:
        lines.append(f"\n   Based on: {based_on}")
    
    return "\n".join(lines)


def list_patterns(strategies: Dict[str, Any]) -> None:
    """List identified patterns."""
    patterns = strategies.get('patterns', {})
    
    print("\n📊 Identified Commit Patterns\n")
    
    # Message patterns
    msg_patterns = patterns.get('message', {})
    if msg_patterns:
        print("🔤 Message Patterns:")
        for name, data in msg_patterns.items():
            success_rate = data.get('success_rate', 0)
            occurrence = data.get('occurrence_count', 0)
            description = data.get('description', 'No description')
            print(f"  • {name}: {description}")
            print(f"    Success rate: {success_rate:.1%}, Occurrences: {occurrence}")
    
    # Size patterns
    size_patterns = patterns.get('size', {})
    if size_patterns:
        print("\n📏 Size Patterns:")
        for name, data in size_patterns.items():
            success_rate = data.get('success_rate', 0)
            occurrence = data.get('occurrence_count', 0)
            description = data.get('description', 'No description')
            print(f"  • {name}: {description}")
            print(f"    Success rate: {success_rate:.1%}, Occurrences: {occurrence}")
            
            attrs = data.get('common_attributes', {})
            if attrs:
                print(f"    Attributes: {', '.join(f'{k}={v}' for k, v in attrs.items())}")
    
    # Organization patterns
    org_patterns = patterns.get('organization', {})
    if org_patterns:
        print("\n📁 Organization Patterns:")
        for name, data in org_patterns.items():
            success_rate = data.get('success_rate', 0)
            occurrence = data.get('occurrence_count', 0)
            description = data.get('description', 'No description')
            print(f"  • {name}: {description}")
            print(f"    Success rate: {success_rate:.1%}, Occurrences: {occurrence}")


def show_summary(strategies: Dict[str, Any]) -> None:
    """Show summary of learning data."""
    summary = strategies.get('summary', {})
    
    print("\n📈 Learning Summary\n")
    print(f"Total Commits Analyzed: {summary.get('total_analyzed', 0)}")
    print(f"Successful Commits: {summary.get('successful', 0)}")
    print(f"Failed Commits: {summary.get('failed', 0)}")
    print(f"Patterns Found: {summary.get('patterns_found', 0)}")
    
    timestamp = strategies.get('timestamp', '')
    if timestamp:
        print(f"Last Updated: {timestamp}")
    
    metadata = strategies.get('_metadata', {})
    if metadata:
        created_by = metadata.get('created_by', '')
        if created_by:
            print(f"Created by: {created_by}")


def get_quick_tip(strategies: Dict[str, Any]) -> str:
    """Get a quick tip for immediate use."""
    recommendations = strategies.get('recommendations', [])
    
    if not recommendations:
        return "No recommendations available yet. More data needed."
    
    # Get highest priority recommendation
    critical = [r for r in recommendations if r.get('priority') == 'CRITICAL']
    if critical:
        rec = critical[0]
        return f"💡 Quick Tip: {rec.get('title', '')} - {rec.get('description', '')}"
    
    high = [r for r in recommendations if r.get('priority') == 'HIGH']
    if high:
        rec = high[0]
        return f"💡 Quick Tip: {rec.get('title', '')} - {rec.get('description', '')}"
    
    # Just return first
    rec = recommendations[0]
    return f"💡 Quick Tip: {rec.get('title', '')} - {rec.get('description', '')}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Query learned git commit strategies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get all recommendations
  python query-commit-strategies.py
  
  # Get critical recommendations only
  python query-commit-strategies.py --priority CRITICAL
  
  # Get recommendations for feature development
  python query-commit-strategies.py --context feature
  
  # List all identified patterns
  python query-commit-strategies.py --list-patterns
  
  # Show learning summary
  python query-commit-strategies.py --summary
  
  # Get a quick tip
  python query-commit-strategies.py --quick-tip
        """
    )
    
    parser.add_argument(
        '--context',
        type=str,
        choices=VALID_CONTEXTS,
        help='Context for recommendations'
    )
    
    parser.add_argument(
        '--priority',
        type=str,
        choices=VALID_PRIORITIES,
        help='Filter by priority level'
    )
    
    parser.add_argument(
        '--min-confidence',
        type=float,
        default=0.0,
        help='Minimum confidence score (0.0-1.0)'
    )
    
    parser.add_argument(
        '--list-patterns',
        action='store_true',
        help='List all identified patterns'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show learning summary'
    )
    
    parser.add_argument(
        '--quick-tip',
        action='store_true',
        help='Get a quick tip for immediate use'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    # Load strategies
    strategies = load_latest_strategies()
    
    if not strategies:
        print("❌ No commit strategies found. Run the learning workflow first.", file=sys.stderr)
        return 1
    
    # Handle special modes
    if args.summary:
        show_summary(strategies)
        return 0
    
    if args.list_patterns:
        list_patterns(strategies)
        return 0
    
    if args.quick_tip:
        tip = get_quick_tip(strategies)
        print(tip)
        return 0
    
    # Get recommendations
    recommendations = get_recommendations(
        strategies,
        context=args.context,
        priority=args.priority,
        min_confidence=args.min_confidence
    )
    
    if not recommendations:
        print("No recommendations match your criteria.")
        return 0
    
    # Output
    if args.json:
        print(json.dumps(recommendations, indent=2))
    else:
        print("\n🎯 Commit Strategy Recommendations\n")
        for i, rec in enumerate(recommendations, 1):
            print(format_recommendation(rec, i))
        
        print(f"\n\n📊 Total: {len(recommendations)} recommendations")
        print("💡 Use these insights to improve commit quality and merge success rate")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
