#!/usr/bin/env python3
"""
Agent Commit Quality Validator

Validates agent commits against learned strategies and provides
real-time feedback for improvement.

Created by @create-guru - Infrastructure for agent quality assurance

Usage:
    python validate-commit-quality.py --commit-hash abc123
    python validate-commit-quality.py --message "feat: add feature"
"""

import json
import os
import sys
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import argparse


# Configuration constants
CONVENTIONAL_COMMIT_TYPES = [
    'feat', 'fix', 'docs', 'style', 'refactor', 
    'test', 'chore', 'perf', 'ci', 'build', 'revert'
]

# Default success rate for commits with message bodies
DEFAULT_BODY_SUCCESS_RATE = 90.4


def load_strategies() -> Dict[str, Any]:
    """Load learned commit strategies."""
    learnings_dir = Path("learnings")
    
    # Find most recent strategies file
    strategy_files = sorted(
        learnings_dir.glob("commit_strategies_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not strategy_files:
        base_file = learnings_dir / "commit_strategies.json"
        if base_file.exists():
            strategy_files = [base_file]
    
    if strategy_files:
        with open(strategy_files[0], 'r') as f:
            return json.load(f)
    
    return {}


def is_conventional_commit(message: str) -> Tuple[bool, Optional[str]]:
    """
    Check if commit message follows conventional commit format.
    
    Returns:
        (is_conventional, type)
    """
    # Build pattern from configured types
    types_pattern = '|'.join(CONVENTIONAL_COMMIT_TYPES)
    pattern = f'^({types_pattern})(\\(.+\\))?: .+'
    match = re.match(pattern, message, re.IGNORECASE)
    
    if match:
        return True, match.group(1).lower()
    
    return False, None


def validate_message_length(message: str) -> Dict[str, Any]:
    """Validate commit message length."""
    lines = message.split('\n')
    first_line = lines[0] if lines else ''
    
    issues = []
    
    # First line length check
    if len(first_line) < 10:
        issues.append({
            'severity': 'error',
            'message': f"First line too short ({len(first_line)} chars). Should be at least 10 characters."
        })
    elif len(first_line) > 72:
        issues.append({
            'severity': 'warning',
            'message': f"First line too long ({len(first_line)} chars). Recommended max: 72 characters."
        })
    
    # Body presence check
    has_body = len(lines) > 1 and any(line.strip() for line in lines[1:])
    
    return {
        'first_line_length': len(first_line),
        'has_body': has_body,
        'issues': issues
    }


def get_commit_stats(commit_hash: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get commit statistics."""
    if not commit_hash:
        # Use staged changes
        result = subprocess.run(
            ['git', 'diff', '--cached', '--numstat'],
            capture_output=True,
            text=True
        )
    else:
        result = subprocess.run(
            ['git', 'show', '--numstat', '--format=', commit_hash],
            capture_output=True,
            text=True
        )
    
    if result.returncode != 0:
        return None
    
    files_changed = 0
    lines_added = 0
    lines_deleted = 0
    file_types = set()
    
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) >= 3:
            try:
                added = int(parts[0]) if parts[0] != '-' else 0
                deleted = int(parts[1]) if parts[1] != '-' else 0
                filepath = parts[2]
                
                lines_added += added
                lines_deleted += deleted
                files_changed += 1
                
                # Get file extension
                ext = Path(filepath).suffix
                if ext:
                    file_types.add(ext)
            except ValueError:
                continue
    
    return {
        'files_changed': files_changed,
        'lines_added': lines_added,
        'lines_deleted': lines_deleted,
        'total_lines_changed': lines_added + lines_deleted,
        'file_types': list(file_types)
    }


def validate_commit_size(stats: Dict[str, Any], strategies: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate commit size against learned patterns."""
    issues = []
    
    # Get learned optimal size
    patterns = strategies.get('patterns', {})
    size_patterns = patterns.get('size', {})
    
    optimal_size = size_patterns.get('optimal_commit_size', {})
    if optimal_size:
        attrs = optimal_size.get('common_attributes', {})
        avg_files = attrs.get('avg_files', 5)
        avg_lines = attrs.get('avg_lines', 100)
        
        files = stats['files_changed']
        lines = stats['total_lines_changed']
        
        # Check files
        if files > avg_files * 2:
            issues.append({
                'severity': 'warning',
                'message': f"Large commit: {files} files changed. Learned optimal: ~{avg_files:.0f} files.",
                'suggestion': "Consider breaking into smaller, focused commits."
            })
        
        # Check lines
        if lines > avg_lines * 3:
            issues.append({
                'severity': 'warning',
                'message': f"Large commit: {lines} lines changed. Learned optimal: ~{avg_lines:.0f} lines.",
                'suggestion': "Consider breaking into smaller commits for easier review."
            })
    
    return issues


def validate_organization(stats: Dict[str, Any], strategies: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate commit organization."""
    issues = []
    
    file_types = stats.get('file_types', [])
    
    # Check for too many file types (might indicate unfocused commit)
    if len(file_types) > 3:
        issues.append({
            'severity': 'info',
            'message': f"Commit changes {len(file_types)} different file types: {', '.join(file_types)}",
            'suggestion': "Ensure all changes are logically related."
        })
    
    return issues


def generate_score(validation_results: Dict[str, Any]) -> float:
    """Generate a quality score for the commit."""
    score = 100.0
    
    # Deduct for errors
    for issue in validation_results.get('all_issues', []):
        if issue['severity'] == 'error':
            score -= 20
        elif issue['severity'] == 'warning':
            score -= 10
        elif issue['severity'] == 'info':
            score -= 5
    
    return max(0.0, score)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate commit quality against learned strategies'
    )
    
    parser.add_argument(
        '--commit-hash',
        type=str,
        help='Commit hash to validate (omit to check staged changes)'
    )
    
    parser.add_argument(
        '--message',
        type=str,
        help='Commit message to validate (alternative to --commit-hash)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    # Load strategies
    strategies = load_strategies()
    if not strategies:
        print("⚠️  No learned strategies available. Quality checks will be basic.", file=sys.stderr)
    
    # Get commit message
    if args.message:
        message = args.message
    elif args.commit_hash:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%B', args.commit_hash],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Could not get commit message for {args.commit_hash}", file=sys.stderr)
            return 1
        message = result.stdout.strip()
    else:
        print("❌ Either --commit-hash or --message must be provided", file=sys.stderr)
        return 1
    
    # Validate message
    is_conv, conv_type = is_conventional_commit(message)
    message_validation = validate_message_length(message)
    
    # Get commit stats if hash provided
    stats = None
    size_issues = []
    org_issues = []
    
    if args.commit_hash or not args.message:
        stats = get_commit_stats(args.commit_hash)
        if stats:
            size_issues = validate_commit_size(stats, strategies)
            org_issues = validate_organization(stats, strategies)
    
    # Compile results
    all_issues = []
    
    # Conventional commit check
    if not is_conv:
        all_issues.append({
            'severity': 'warning',
            'message': 'Not using conventional commit format',
            'suggestion': 'Use format: type(scope): description. E.g., feat: add feature'
        })
    
    # Message issues
    all_issues.extend(message_validation['issues'])
    
    # Recommend body if missing
    if not message_validation['has_body']:
        # Get success rate from strategies or use default
        body_success_rate = DEFAULT_BODY_SUCCESS_RATE
        patterns = strategies.get('patterns', {})
        msg_patterns = patterns.get('message', {})
        detailed_msg = msg_patterns.get('detailed_messages', {})
        if detailed_msg and 'success_rate' in detailed_msg:
            body_success_rate = detailed_msg['success_rate'] * 100
        
        all_issues.append({
            'severity': 'info',
            'message': 'No commit message body',
            'suggestion': f'Add a body explaining why changes were made ({body_success_rate:.1f}% of successful commits have bodies)'
        })
    
    # Size and organization issues
    all_issues.extend(size_issues)
    all_issues.extend(org_issues)
    
    # Generate results
    results = {
        'message': message,
        'is_conventional': is_conv,
        'conventional_type': conv_type,
        'message_validation': message_validation,
        'stats': stats,
        'issues': all_issues,
        'score': generate_score({'all_issues': all_issues})
    }
    
    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Pretty print
        score = results['score']
        score_emoji = '✅' if score >= 80 else '⚠️' if score >= 60 else '❌'
        
        print(f"\n{score_emoji} Commit Quality Score: {score:.0f}/100\n")
        
        if is_conv:
            print(f"✓ Conventional commit format: {conv_type}")
        else:
            print("✗ Not using conventional commit format")
        
        if message_validation['has_body']:
            print("✓ Has commit message body")
        else:
            print("✗ No commit message body")
        
        if stats:
            print(f"\n📊 Statistics:")
            print(f"  Files changed: {stats['files_changed']}")
            print(f"  Lines changed: {stats['total_lines_changed']} (+{stats['lines_added']}/-{stats['lines_deleted']})")
            if stats['file_types']:
                print(f"  File types: {', '.join(stats['file_types'])}")
        
        if all_issues:
            print(f"\n⚠️  Issues ({len(all_issues)}):")
            for issue in all_issues:
                severity_emoji = '🔴' if issue['severity'] == 'error' else '🟡' if issue['severity'] == 'warning' else 'ℹ️'
                print(f"\n  {severity_emoji} {issue['message']}")
                if 'suggestion' in issue:
                    print(f"     💡 {issue['suggestion']}")
        else:
            print("\n✅ No issues found - excellent commit quality!")
        
        print()
    
    # Exit code based on score
    if results['score'] >= 60:
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
