#!/usr/bin/env python3
"""
Integration Example: Pattern Matcher + Code Analyzer + Dependency Analyzer

Shows how to combine insights from multiple analysis tools.
Created by @investigate-champion
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Import all analyzers
sys.path.insert(0, os.path.dirname(__file__))

import importlib.util

def load_module(name, path):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load modules
pattern_matcher = load_module(
    "cross_repo_pattern_matcher",
    os.path.join(os.path.dirname(__file__), "cross-repo-pattern-matcher.py")
)
code_analyzer = load_module(
    "code_analyzer",
    os.path.join(os.path.dirname(__file__), "code-analyzer.py")
)


def run_comprehensive_analysis(repo_path='.'):
    """
    Run comprehensive analysis combining all tools.
    
    Returns a unified report with insights from:
    - Pattern Matcher: Best practices and anti-patterns
    - Code Analyzer: Code quality metrics
    """
    print("=" * 80)
    print("🔬 COMPREHENSIVE REPOSITORY ANALYSIS")
    print("=" * 80)
    print(f"Repository: {Path(repo_path).resolve().name}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'repository': str(Path(repo_path).resolve()),
        'analyses': {}
    }
    
    # 1. Pattern Matcher Analysis
    print("📊 Running Pattern Matcher...")
    try:
        matcher = pattern_matcher.CrossRepoPatternMatcher(repo_path)
        pattern_analysis = matcher.analyze_repository()
        
        results['analyses']['patterns'] = {
            'score': pattern_analysis.score,
            'good_practices': pattern_analysis.summary['good_practices'],
            'anti_patterns': pattern_analysis.summary['anti_patterns'],
            'by_category': pattern_analysis.summary['by_category'],
            'recommendations': pattern_analysis.recommendations
        }
        
        print(f"   ✅ Score: {pattern_analysis.score:.1f}/100")
        print(f"   📈 Good Practices: {pattern_analysis.summary['good_practices']}")
        print(f"   ⚠️  Anti-Patterns: {pattern_analysis.summary['anti_patterns']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['analyses']['patterns'] = {'error': str(e)}
    
    print()
    
    # 2. Code Analyzer
    print("🔍 Running Code Analyzer...")
    try:
        analyzer = code_analyzer.CodeAnalyzer()
        
        # Analyze Python files in tools directory
        tools_path = os.path.join(repo_path, 'tools')
        if os.path.exists(tools_path):
            code_analysis = analyzer.analyze_directory(tools_path)
            
            results['analyses']['code_quality'] = {
                'files_analyzed': code_analysis['summary']['total_files'],
                'good_patterns': code_analysis['summary']['total_good_patterns'],
                'bad_patterns': code_analysis['summary']['total_bad_patterns']
            }
            
            print(f"   ✅ Files Analyzed: {code_analysis['summary']['total_files']}")
            print(f"   📊 Pattern Breakdown:")
            for pattern, count in sorted(
                code_analysis['summary']['pattern_breakdown'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]:
                print(f"      {pattern}: {count}")
        else:
            print(f"   ⚠️  Tools directory not found")
            results['analyses']['code_quality'] = {'error': 'Directory not found'}
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['analyses']['code_quality'] = {'error': str(e)}
    
    print()
    
    # Generate unified insights
    print("=" * 80)
    print("💡 UNIFIED INSIGHTS")
    print("=" * 80)
    print()
    
    generate_unified_insights(results)
    
    # Export combined report
    output_file = 'comprehensive-analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"📄 Comprehensive report saved to: {output_file}")
    print()
    
    return results


def generate_unified_insights(results):
    """Generate insights by combining multiple analysis results"""
    
    insights = []
    
    # Pattern analysis insights
    if 'patterns' in results['analyses'] and 'score' in results['analyses']['patterns']:
        score = results['analyses']['patterns']['score']
        good = results['analyses']['patterns']['good_practices']
        bad = results['analyses']['patterns']['anti_patterns']
        
        if score >= 85:
            insights.append(
                f"✅ **Excellent Code Quality**: Score of {score:.1f}/100 indicates "
                "strong adherence to best practices."
            )
        elif score >= 70:
            insights.append(
                f"👍 **Good Code Quality**: Score of {score:.1f}/100 with room for "
                "improvement in specific areas."
            )
        else:
            insights.append(
                f"⚠️  **Needs Improvement**: Score of {score:.1f}/100 suggests "
                "systematic issues that should be addressed."
            )
        
        if bad > good * 0.2:  # More than 20% anti-patterns
            insights.append(
                f"🔧 **High Anti-Pattern Ratio**: {bad} anti-patterns vs {good} good "
                "practices. Consider refactoring."
            )
    
    # Code quality insights
    if 'code_quality' in results['analyses'] and 'files_analyzed' in results['analyses']['code_quality']:
        files = results['analyses']['code_quality']['files_analyzed']
        good_patterns = results['analyses']['code_quality']['good_patterns']
        bad_patterns = results['analyses']['code_quality']['bad_patterns']
        
        avg_good = good_patterns / files if files > 0 else 0
        avg_bad = bad_patterns / files if files > 0 else 0
        
        if avg_good > avg_bad * 2:
            insights.append(
                f"📈 **Consistent Quality**: Average of {avg_good:.1f} good patterns "
                f"per file significantly exceeds bad patterns ({avg_bad:.1f})."
            )
        elif avg_bad > avg_good:
            insights.append(
                f"📉 **Quality Concerns**: Bad patterns ({avg_bad:.1f}/file) exceed "
                f"good patterns ({avg_good:.1f}/file)."
            )
    
    # Cross-tool insights
    if ('patterns' in results['analyses'] and 
        'code_quality' in results['analyses'] and
        'score' in results['analyses']['patterns'] and
        'files_analyzed' in results['analyses']['code_quality']):
        
        pattern_score = results['analyses']['patterns']['score']
        code_good = results['analyses']['code_quality']['good_patterns']
        code_bad = results['analyses']['code_quality']['bad_patterns']
        
        code_ratio = code_good / (code_bad + 1)  # Avoid division by zero
        
        if pattern_score > 80 and code_ratio > 2:
            insights.append(
                "🌟 **Highly Maintainable Codebase**: Both pattern analysis and "
                "code quality metrics indicate excellent maintainability."
            )
    
    # Print insights
    if insights:
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
            print()
    else:
        print("No specific insights generated. Run individual analyses for details.")
    
    # Recommendations
    print("🎯 **Recommended Actions**:")
    print()
    
    if 'patterns' in results['analyses'] and 'recommendations' in results['analyses']['patterns']:
        # Show top 3 recommendations from pattern matcher
        for i, rec in enumerate(results['analyses']['patterns']['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
    else:
        print("   - Run pattern analysis for specific recommendations")
    
    print()


def compare_with_baseline():
    """Compare current analysis with a baseline (if exists)"""
    print("=" * 80)
    print("📊 BASELINE COMPARISON")
    print("=" * 80)
    print()
    
    baseline_file = 'baseline-analysis.json'
    current_file = 'comprehensive-analysis.json'
    
    if not os.path.exists(current_file):
        print("⚠️  Run comprehensive analysis first")
        return
    
    if not os.path.exists(baseline_file):
        print("📝 No baseline found. Creating baseline from current analysis...")
        import shutil
        shutil.copy(current_file, baseline_file)
        print(f"   ✅ Baseline saved to: {baseline_file}")
        print()
        print("   Run this comparison again later to see changes over time.")
        return
    
    # Load both files
    with open(baseline_file, 'r') as f:
        baseline = json.load(f)
    
    with open(current_file, 'r') as f:
        current = json.load(f)
    
    # Compare scores
    print("Score Comparison:")
    print()
    
    if ('patterns' in baseline['analyses'] and 
        'patterns' in current['analyses'] and
        'score' in baseline['analyses']['patterns'] and
        'score' in current['analyses']['patterns']):
        
        baseline_score = baseline['analyses']['patterns']['score']
        current_score = current['analyses']['patterns']['score']
        diff = current_score - baseline_score
        
        print(f"   Baseline: {baseline_score:.1f}/100")
        print(f"   Current:  {current_score:.1f}/100")
        
        if diff > 0:
            print(f"   📈 Improvement: +{diff:.1f} points")
        elif diff < 0:
            print(f"   📉 Regression: {diff:.1f} points")
        else:
            print(f"   ➡️  No change")
    
    print()
    
    # Compare patterns
    print("Pattern Comparison:")
    print()
    
    if ('patterns' in baseline['analyses'] and 
        'patterns' in current['analyses']):
        
        baseline_good = baseline['analyses']['patterns'].get('good_practices', 0)
        current_good = current['analyses']['patterns'].get('good_practices', 0)
        baseline_bad = baseline['analyses']['patterns'].get('anti_patterns', 0)
        current_bad = current['analyses']['patterns'].get('anti_patterns', 0)
        
        print(f"   Good Practices: {baseline_good} → {current_good} ({current_good - baseline_good:+d})")
        print(f"   Anti-Patterns:  {baseline_bad} → {current_bad} ({current_bad - baseline_bad:+d})")
    
    print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Comprehensive Repository Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--repo',
        default='.',
        help='Repository path to analyze (default: current directory)'
    )
    parser.add_argument(
        '--baseline',
        action='store_true',
        help='Compare with baseline analysis'
    )
    
    args = parser.parse_args()
    
    # Run comprehensive analysis
    run_comprehensive_analysis(args.repo)
    
    # Compare with baseline if requested
    if args.baseline:
        print()
        compare_with_baseline()


if __name__ == '__main__':
    main()
