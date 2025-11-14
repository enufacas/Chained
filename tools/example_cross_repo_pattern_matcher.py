#!/usr/bin/env python3
"""
Example Usage: Cross-Repository Pattern Matcher

Demonstrates how to use the pattern matcher for various scenarios.
Created by @investigate-champion
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add tools to path
sys.path.insert(0, os.path.dirname(__file__))

# Import pattern matcher
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cross_repo_pattern_matcher",
    os.path.join(os.path.dirname(__file__), "cross-repo-pattern-matcher.py")
)
matcher_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(matcher_module)

CrossRepoPatternMatcher = matcher_module.CrossRepoPatternMatcher


def example_basic_analysis():
    """Example 1: Basic repository analysis"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Repository Analysis")
    print("=" * 80)
    print()
    
    # Analyze current repository
    matcher = CrossRepoPatternMatcher('.')
    analysis = matcher.analyze_repository()
    
    # Print report
    matcher.print_report(analysis, verbose=False)
    
    print()


def example_focused_analysis():
    """Example 2: Analyze specific directory"""
    print("=" * 80)
    print("EXAMPLE 2: Focused Analysis (tools directory)")
    print("=" * 80)
    print()
    
    # Create a temporary matcher for just the tools directory
    # Note: This creates a matcher for the subdirectory
    tools_path = Path('.') / 'tools'
    if tools_path.exists():
        matcher = CrossRepoPatternMatcher(str(tools_path))
        analysis = matcher.analyze_repository()
        
        print(f"📊 Tools Directory Score: {analysis.score:.1f}/100")
        print(f"📈 Good Practices: {analysis.summary['good_practices']}")
        print(f"⚠️  Anti-Patterns: {analysis.summary['anti_patterns']}")
    else:
        print("Tools directory not found")
    
    print()


def example_json_export():
    """Example 3: Export and parse JSON report"""
    print("=" * 80)
    print("EXAMPLE 3: JSON Export and Analysis")
    print("=" * 80)
    print()
    
    # Analyze and export
    matcher = CrossRepoPatternMatcher('.')
    analysis = matcher.analyze_repository()
    
    output_file = '/tmp/pattern-report.json'
    matcher.export_report(analysis, output_file)
    
    # Read back and analyze
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    print(f"📄 Report exported to: {output_file}")
    print(f"📊 Total patterns: {data['summary']['total_patterns']}")
    print()
    
    # Find top issues by severity
    print("Top Issues by Severity:")
    for severity in ['critical', 'high', 'medium']:
        count = data['summary']['by_severity'].get(severity, 0)
        if count > 0:
            print(f"  {severity.upper()}: {count} issues")
    
    print()


def example_filter_patterns():
    """Example 4: Filter specific pattern types"""
    print("=" * 80)
    print("EXAMPLE 4: Filter Security Patterns")
    print("=" * 80)
    print()
    
    matcher = CrossRepoPatternMatcher('.')
    analysis = matcher.analyze_repository()
    
    # Filter security patterns
    security_patterns = [
        m for m in analysis.patterns_matched
        if m.category == 'security'
    ]
    
    print(f"🔒 Found {len(security_patterns)} security-related patterns")
    print()
    
    if security_patterns:
        # Group by pattern type
        from collections import defaultdict
        by_pattern = defaultdict(list)
        for match in security_patterns:
            by_pattern[match.pattern_name].append(match)
        
        for pattern_name, matches in sorted(by_pattern.items()):
            print(f"  {pattern_name}: {len(matches)} occurrences")
            # Show first example
            if matches:
                first = matches[0]
                print(f"    Example: {first.file_path}:{first.line_number}")
    
    print()


def example_score_tracking():
    """Example 5: Track scores over time"""
    print("=" * 80)
    print("EXAMPLE 5: Score Tracking Simulation")
    print("=" * 80)
    print()
    
    # Simulate tracking scores over time
    scores = []
    
    # Current score
    matcher = CrossRepoPatternMatcher('.')
    analysis = matcher.analyze_repository()
    
    score_entry = {
        'timestamp': datetime.now().isoformat(),
        'score': analysis.score,
        'good_practices': analysis.summary['good_practices'],
        'anti_patterns': analysis.summary['anti_patterns']
    }
    scores.append(score_entry)
    
    print("📈 Score History:")
    for entry in scores:
        print(f"  {entry['timestamp'][:19]}: {entry['score']:.1f}/100")
        print(f"    Good: {entry['good_practices']}, Anti-patterns: {entry['anti_patterns']}")
    
    print()
    print("💡 To track over time, run analysis regularly and store results")
    print()


def example_cross_repo_comparison():
    """Example 6: Compare multiple repositories (simulated)"""
    print("=" * 80)
    print("EXAMPLE 6: Cross-Repository Comparison")
    print("=" * 80)
    print()
    
    print("🔄 Simulated cross-repo comparison")
    print()
    
    # This would normally analyze multiple repos
    # For demo, we'll show the pattern
    
    repos = ['Chained', 'Project-A', 'Project-B', 'Project-C']
    
    # Simulate different scores
    import random
    random.seed(42)
    
    print("Repository Comparison:")
    print(f"{'Repository':20s} {'Score':>10s} {'Good':>8s} {'Bad':>8s}")
    print("-" * 50)
    
    for repo in repos:
        if repo == 'Chained':
            # Real score for Chained
            matcher = CrossRepoPatternMatcher('.')
            analysis = matcher.analyze_repository()
            score = analysis.score
            good = analysis.summary['good_practices']
            bad = analysis.summary['anti_patterns']
        else:
            # Simulated scores for demo
            score = random.uniform(60, 95)
            good = random.randint(100, 500)
            bad = random.randint(10, 100)
        
        print(f"{repo:20s} {score:>9.1f} {good:>8d} {bad:>8d}")
    
    print()
    print("💡 Best: Focus on repositories with scores < 70")
    print()


def example_pattern_recommendations():
    """Example 7: Get actionable recommendations"""
    print("=" * 80)
    print("EXAMPLE 7: Actionable Recommendations")
    print("=" * 80)
    print()
    
    matcher = CrossRepoPatternMatcher('.')
    analysis = matcher.analyze_repository()
    
    print("📋 Top Recommendations:")
    print()
    
    for i, rec in enumerate(analysis.recommendations[:5], 1):
        print(f"{i}. {rec}")
        print()
    
    # Find most common anti-patterns
    from collections import Counter
    anti_patterns = [
        m for m in analysis.patterns_matched
        if m.pattern_name in ['Long Functions', 'Deep Nesting', 'Hardcoded Secrets']
    ]
    
    if anti_patterns:
        top_anti = Counter(m.pattern_name for m in anti_patterns).most_common(3)
        
        print("🎯 Priority Actions:")
        for pattern_name, count in top_anti:
            print(f"  - Address {count} instances of '{pattern_name}'")
    
    print()


def example_confidence_analysis():
    """Example 8: Analyze pattern confidence"""
    print("=" * 80)
    print("EXAMPLE 8: Pattern Confidence Analysis")
    print("=" * 80)
    print()
    
    matcher = CrossRepoPatternMatcher('.')
    analysis = matcher.analyze_repository()
    
    # Group by confidence ranges
    high_conf = [m for m in analysis.patterns_matched if m.confidence >= 0.9]
    med_conf = [m for m in analysis.patterns_matched if 0.7 <= m.confidence < 0.9]
    low_conf = [m for m in analysis.patterns_matched if m.confidence < 0.7]
    
    print("📊 Confidence Distribution:")
    print(f"  High (≥90%):   {len(high_conf)} patterns")
    print(f"  Medium (70-89%): {len(med_conf)} patterns")
    print(f"  Low (<70%):      {len(low_conf)} patterns")
    print()
    
    print("💡 Focus on high-confidence patterns for quick wins")
    print()


def example_integration_with_ci():
    """Example 9: CI/CD Integration Pattern"""
    print("=" * 80)
    print("EXAMPLE 9: CI/CD Integration Pattern")
    print("=" * 80)
    print()
    
    print("GitHub Actions Workflow Example:")
    print()
    print("""
    name: Pattern Analysis
    on: [push, pull_request]
    
    jobs:
      analyze:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          
          - name: Run Pattern Analysis
            run: |
              python3 tools/cross-repo-pattern-matcher.py \\
                --repo . \\
                -o pattern-report.json
          
          - name: Check Score
            run: |
              SCORE=$(python3 -c "import json; print(json.load(open('pattern-report.json'))['score'])")
              echo "Best Practices Score: $SCORE/100"
              
              # Fail if score is too low
              if (( $(echo "$SCORE < 70" | bc -l) )); then
                echo "::error::Score $SCORE is below threshold of 70"
                exit 1
              fi
          
          - name: Upload Report
            uses: actions/upload-artifact@v4
            with:
              name: pattern-analysis
              path: pattern-report.json
    """)
    print()


def main():
    """Run all examples"""
    examples = [
        ("Basic Analysis", example_basic_analysis),
        ("Focused Analysis", example_focused_analysis),
        ("JSON Export", example_json_export),
        ("Filter Patterns", example_filter_patterns),
        ("Score Tracking", example_score_tracking),
        ("Cross-Repo Comparison", example_cross_repo_comparison),
        ("Recommendations", example_pattern_recommendations),
        ("Confidence Analysis", example_confidence_analysis),
        ("CI/CD Integration", example_integration_with_ci),
    ]
    
    print("\n" + "=" * 80)
    print("🎯 CROSS-REPOSITORY PATTERN MATCHER EXAMPLES")
    print("=" * 80)
    print()
    print("Choose an example to run:")
    print()
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print(f"  {len(examples) + 1}. Run All Examples")
    print("  0. Exit")
    print()
    
    try:
        choice = input("Enter choice (0-{}): ".format(len(examples) + 1))
        choice = int(choice)
        
        if choice == 0:
            print("Goodbye!")
            return
        elif choice == len(examples) + 1:
            print("\nRunning all examples...\n")
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"Error in {name}: {e}")
                    import traceback
                    traceback.print_exc()
        elif 1 <= choice <= len(examples):
            examples[choice - 1][1]()
        else:
            print("Invalid choice")
    
    except (ValueError, KeyboardInterrupt):
        print("\nGoodbye!")


if __name__ == '__main__':
    main()
