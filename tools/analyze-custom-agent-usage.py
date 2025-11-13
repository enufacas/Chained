#!/usr/bin/env python3
"""
Tool to analyze custom agent usage in GitHub Copilot workflows.

This script examines:
1. Issue comments and bodies for custom agent mentions
2. PR descriptions for custom agent references
3. Workflow run logs (if available via API)
4. Agent assignment history

Usage:
    python tools/analyze-custom-agent-usage.py [--issue ISSUE_NUM] [--verbose]
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


def run_gh_command(command: List[str]) -> Optional[str]:
    """Run a gh CLI command and return output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}", file=sys.stderr)
        print(f"Error output: {e.stderr}", file=sys.stderr)
        return None


def get_copilot_assigned_issues(limit: int = 50) -> List[Dict]:
    """Get issues that have been assigned to Copilot."""
    output = run_gh_command([
        'gh', 'issue', 'list',
        '--label', 'copilot-assigned',
        '--state', 'all',
        '--limit', str(limit),
        '--json', 'number,title,labels,assignees,body,comments,closedAt,createdAt'
    ])
    
    if not output:
        return []
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def get_issue_details(issue_number: int) -> Optional[Dict]:
    """Get detailed information about a specific issue."""
    output = run_gh_command([
        'gh', 'issue', 'view', str(issue_number),
        '--json', 'number,title,body,comments,labels,assignees,createdAt,closedAt'
    ])
    
    if not output:
        return None
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


def get_prs_for_issue(issue_number: int) -> List[Dict]:
    """Get PRs linked to a specific issue."""
    # Search for PRs that reference the issue
    output = run_gh_command([
        'gh', 'pr', 'list',
        '--search', f'#{issue_number}',
        '--state', 'all',
        '--limit', '10',
        '--json', 'number,title,body,author,createdAt,mergedAt,closedAt'
    ])
    
    if not output:
        return []
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def extract_custom_agent_from_text(text: str) -> List[str]:
    """Extract custom agent mentions from text."""
    if not text:
        return []
    
    agents = []
    
    # Pattern 1: @agent-name mentions
    agent_mentions = re.findall(r'@([a-z-]+(?:master|specialist|guru|champion|wizard|expert))', text.lower())
    agents.extend(agent_mentions)
    
    # Pattern 2: COPILOT_AGENT: directive
    agent_directive = re.search(r'COPILOT_AGENT:([a-z-]+)', text, re.IGNORECASE)
    if agent_directive:
        agents.append(agent_directive.group(1))
    
    # Pattern 3: agent:label-name labels
    agent_labels = re.findall(r'agent:([a-z-]+)', text.lower())
    agents.extend(agent_labels)
    
    # Pattern 4: .github/agents/agent-name.md references
    agent_paths = re.findall(r'\.github/agents/([a-z-]+)\.md', text.lower())
    agents.extend(agent_paths)
    
    # Pattern 5: "**agent-name** custom agent" or similar
    agent_bold = re.findall(r'\*\*([a-z-]+(?:master|specialist|guru|champion|wizard|expert))\*\*', text.lower())
    agents.extend(agent_bold)
    
    return list(set(agents))  # Remove duplicates


def analyze_issue_custom_agent_usage(issue: Dict) -> Dict:
    """Analyze an issue for custom agent usage."""
    issue_num = issue['number']
    
    result = {
        'issue_number': issue_num,
        'title': issue['title'],
        'created_at': issue['createdAt'],
        'closed_at': issue.get('closedAt'),
        'assigned_to_copilot': False,
        'custom_agent_mentioned': False,
        'custom_agents': [],
        'evidence': []
    }
    
    # Check if assigned to Copilot
    assignees = [a['login'] for a in issue.get('assignees', [])]
    if any('copilot' in a.lower() for a in assignees):
        result['assigned_to_copilot'] = True
        result['evidence'].append(f"Assigned to: {', '.join(assignees)}")
    
    # Check labels
    labels = [label['name'] for label in issue.get('labels', [])]
    if 'copilot-assigned' in labels:
        result['assigned_to_copilot'] = True
        result['evidence'].append("Has 'copilot-assigned' label")
    
    # Check for agent-specific labels
    agent_labels = [l for l in labels if l.startswith('agent:')]
    if agent_labels:
        result['custom_agents'].extend([l.replace('agent:', '') for l in agent_labels])
        result['evidence'].append(f"Agent labels: {', '.join(agent_labels)}")
    
    # Analyze issue body
    body = issue.get('body', '')
    body_agents = extract_custom_agent_from_text(body)
    if body_agents:
        result['custom_agent_mentioned'] = True
        result['custom_agents'].extend(body_agents)
        result['evidence'].append(f"Custom agents in issue body: {', '.join(body_agents)}")
    
    # Analyze comments
    comments = issue.get('comments', [])
    for comment in comments:
        comment_body = comment.get('body', '')
        comment_agents = extract_custom_agent_from_text(comment_body)
        if comment_agents:
            result['custom_agent_mentioned'] = True
            result['custom_agents'].extend(comment_agents)
            author = comment.get('author', {}).get('login', 'unknown')
            result['evidence'].append(f"Custom agents in comment by {author}: {', '.join(comment_agents)}")
    
    # Remove duplicates from custom_agents list
    result['custom_agents'] = list(set(result['custom_agents']))
    
    return result


def analyze_pr_custom_agent_usage(pr: Dict, issue_number: int) -> Dict:
    """Analyze a PR for custom agent usage evidence."""
    result = {
        'pr_number': pr['number'],
        'title': pr['title'],
        'author': pr['author']['login'],
        'created_at': pr['createdAt'],
        'merged_at': pr.get('mergedAt'),
        'custom_agent_mentioned': False,
        'custom_agents': [],
        'evidence': []
    }
    
    # Check if author is Copilot
    if 'copilot' in result['author'].lower():
        result['evidence'].append(f"PR created by: {result['author']}")
    
    # Analyze PR body
    body = pr.get('body', '')
    body_agents = extract_custom_agent_from_text(body)
    if body_agents:
        result['custom_agent_mentioned'] = True
        result['custom_agents'].extend(body_agents)
        result['evidence'].append(f"Custom agents in PR body: {', '.join(body_agents)}")
    
    # Remove duplicates
    result['custom_agents'] = list(set(result['custom_agents']))
    
    return result


def generate_report(analyses: List[Tuple[Dict, List[Dict]]], verbose: bool = False):
    """Generate a report of custom agent usage."""
    print("=" * 80)
    print("CUSTOM AGENT USAGE ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    total_issues = len(analyses)
    copilot_assigned = sum(1 for a, _ in analyses if a['assigned_to_copilot'])
    custom_agent_mentioned = sum(1 for a, _ in analyses if a['custom_agent_mentioned'])
    
    print(f"Total issues analyzed: {total_issues}")
    print(f"Issues assigned to Copilot: {copilot_assigned}")
    print(f"Issues with custom agent mentions: {custom_agent_mentioned}")
    print()
    
    if copilot_assigned > 0:
        percentage = (custom_agent_mentioned / copilot_assigned) * 100
        print(f"Custom agent usage rate: {percentage:.1f}% ({custom_agent_mentioned}/{copilot_assigned})")
    else:
        print("No issues assigned to Copilot found.")
    
    print()
    print("-" * 80)
    print("CUSTOM AGENT FREQUENCY")
    print("-" * 80)
    
    # Count agent mentions
    agent_counts = {}
    for issue_analysis, pr_analyses in analyses:
        for agent in issue_analysis['custom_agents']:
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        for pr_analysis in pr_analyses:
            for agent in pr_analysis['custom_agents']:
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    if agent_counts:
        for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {agent}: {count} mentions")
    else:
        print("  No custom agent mentions found.")
    
    print()
    print("-" * 80)
    print("DETAILED ANALYSIS")
    print("-" * 80)
    print()
    
    for issue_analysis, pr_analyses in analyses:
        if not issue_analysis['assigned_to_copilot'] and not verbose:
            continue
        
        print(f"Issue #{issue_analysis['issue_number']}: {issue_analysis['title']}")
        print(f"  Created: {issue_analysis['created_at']}")
        if issue_analysis['closed_at']:
            print(f"  Closed: {issue_analysis['closed_at']}")
        
        if issue_analysis['assigned_to_copilot']:
            print(f"  ✅ Assigned to Copilot")
        else:
            print(f"  ❌ NOT assigned to Copilot")
        
        if issue_analysis['custom_agent_mentioned']:
            print(f"  ✅ Custom agent mentioned: {', '.join(issue_analysis['custom_agents'])}")
        else:
            print(f"  ❌ NO custom agent mentions")
        
        if issue_analysis['evidence']:
            print(f"  Evidence:")
            for evidence in issue_analysis['evidence']:
                print(f"    - {evidence}")
        
        # Show PR info
        if pr_analyses:
            print(f"  Related PRs ({len(pr_analyses)}):")
            for pr_analysis in pr_analyses:
                print(f"    PR #{pr_analysis['pr_number']}: {pr_analysis['title']}")
                print(f"      Author: {pr_analysis['author']}")
                if pr_analysis['custom_agent_mentioned']:
                    print(f"      Custom agents: {', '.join(pr_analysis['custom_agents'])}")
                if pr_analysis['evidence']:
                    for evidence in pr_analysis['evidence']:
                        print(f"      - {evidence}")
        
        print()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze custom agent usage in GitHub Copilot workflows'
    )
    parser.add_argument(
        '--issue',
        type=int,
        help='Analyze a specific issue number'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Number of issues to analyze (default: 50)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show all issues, not just Copilot-assigned ones'
    )
    
    args = parser.parse_args()
    
    # Check if gh CLI is available
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: GitHub CLI (gh) is not installed or not in PATH", file=sys.stderr)
        print("Install from: https://cli.github.com/", file=sys.stderr)
        sys.exit(1)
    
    if args.issue:
        # Analyze a specific issue
        print(f"Analyzing issue #{args.issue}...")
        issue = get_issue_details(args.issue)
        if not issue:
            print(f"Error: Could not fetch issue #{args.issue}", file=sys.stderr)
            sys.exit(1)
        
        issue_analysis = analyze_issue_custom_agent_usage(issue)
        prs = get_prs_for_issue(args.issue)
        pr_analyses = [analyze_pr_custom_agent_usage(pr, args.issue) for pr in prs]
        
        generate_report([(issue_analysis, pr_analyses)], verbose=True)
    else:
        # Analyze all copilot-assigned issues
        print(f"Fetching up to {args.limit} Copilot-assigned issues...")
        issues = get_copilot_assigned_issues(args.limit)
        
        if not issues:
            print("No Copilot-assigned issues found.", file=sys.stderr)
            print("\nThis could mean:", file=sys.stderr)
            print("  1. No issues have been assigned to Copilot yet", file=sys.stderr)
            print("  2. The 'copilot-assigned' label doesn't exist", file=sys.stderr)
            print("  3. The GitHub CLI is not properly authenticated", file=sys.stderr)
            sys.exit(1)
        
        print(f"Found {len(issues)} issues to analyze...")
        print()
        
        analyses = []
        for issue in issues:
            issue_analysis = analyze_issue_custom_agent_usage(issue)
            prs = get_prs_for_issue(issue['number'])
            pr_analyses = [analyze_pr_custom_agent_usage(pr, issue['number']) for pr in prs]
            analyses.append((issue_analysis, pr_analyses))
        
        generate_report(analyses, args.verbose)


if __name__ == '__main__':
    main()
