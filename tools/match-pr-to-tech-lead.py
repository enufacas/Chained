#!/usr/bin/env python3
"""
Tech Lead Matching System for Pull Requests

This script analyzes PR file changes and determines which Tech Lead agents
should review the PR based on their defined path responsibilities.

Usage:
    python3 match-pr-to-tech-lead.py <pr_number>
    python3 match-pr-to-tech-lead.py <pr_number> --all-tech-leads
    python3 match-pr-to-tech-lead.py <pr_number> --check-complexity

Environment Variables:
    GITHUB_REPOSITORY: The repository (owner/repo)
    GH_TOKEN: GitHub token for API access
"""

import sys
import json
import os
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from fnmatch import fnmatch

# Constants
AGENTS_DIR = Path(".github/agents")
TECH_LEAD_THRESHOLDS = {
    "protected_paths": [
        ".github/workflows/**",
        ".github/actions/**", 
        ".github/agents/**",
        ".github/agent-system/**",
        ".github/CODEOWNERS",
    ],
    "max_files_for_optional": 5,  # Small PRs might not need Tech Lead
    "max_lines_for_optional": 100,  # Small changes might not need Tech Lead
    "always_require_for_patterns": [
        r"secret",
        r"password",
        r"token",
        r"auth",
        r"permission",
        r"security",
    ]
}


def run_gh_command(args: List[str]) -> Tuple[bool, str]:
    """Run a gh CLI command and return (success, output)."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def get_pr_files(pr_number: str) -> Optional[List[Dict]]:
    """Get list of files changed in a PR using gh CLI."""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        print("Error: GITHUB_REPOSITORY environment variable not set", file=sys.stderr)
        return None
    
    success, output = run_gh_command([
        "pr", "view", pr_number,
        "--repo", repo,
        "--json", "files"
    ])
    
    if not success:
        print(f"Error getting PR files: {output}", file=sys.stderr)
        return None
    
    try:
        data = json.loads(output)
        return data.get("files", [])
    except json.JSONDecodeError as e:
        print(f"Error parsing PR data: {e}", file=sys.stderr)
        return None


def get_pr_metadata(pr_number: str) -> Optional[Dict]:
    """Get PR metadata including title, body, labels, and stats."""
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        return None
    
    success, output = run_gh_command([
        "pr", "view", pr_number,
        "--repo", repo,
        "--json", "title,body,labels,additions,deletions"
    ])
    
    if not success:
        return None
    
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


def parse_tech_lead_agent(filepath: Path) -> Optional[Dict]:
    """Parse a Tech Lead agent file and extract path responsibilities."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not frontmatter_match:
            return None
        
        frontmatter_str = frontmatter_match.group(1)
        
        # Parse YAML (simple parser for our needs)
        agent_data = {}
        current_list = None
        for line in frontmatter_str.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('- '):
                # List item
                if current_list:
                    agent_data[current_list].append(line[2:].strip())
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'tech_lead_for_paths':
                    current_list = key
                    agent_data[key] = []
                elif value:
                    agent_data[key] = value
                    current_list = None
        
        # Must have tech_lead_for_paths to be a Tech Lead
        if 'tech_lead_for_paths' not in agent_data:
            return None
        
        return {
            'name': agent_data.get('name', ''),
            'description': agent_data.get('description', ''),
            'paths': agent_data.get('tech_lead_for_paths', []),
            'specialization': agent_data.get('specialization', ''),
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
        return None


def load_tech_leads() -> List[Dict]:
    """Load all Tech Lead agents from the agents directory."""
    tech_leads = []
    
    if not AGENTS_DIR.exists():
        return tech_leads
    
    for filepath in AGENTS_DIR.glob("*tech-lead.md"):
        agent_data = parse_tech_lead_agent(filepath)
        if agent_data:
            tech_leads.append(agent_data)
    
    return tech_leads


def match_file_to_tech_leads(filepath: str, tech_leads: List[Dict]) -> List[Dict]:
    """Match a file path to Tech Lead agents based on their responsibilities."""
    matched = []
    
    for tech_lead in tech_leads:
        for pattern in tech_lead['paths']:
            # Convert glob pattern to fnmatch
            if fnmatch(filepath, pattern):
                matched.append(tech_lead)
                break
    
    return matched


def analyze_pr_complexity(pr_files: List[Dict], pr_metadata: Dict) -> Dict:
    """Analyze PR complexity to determine if Tech Lead review is needed."""
    total_files = len(pr_files)
    total_additions = pr_metadata.get('additions', 0)
    total_deletions = pr_metadata.get('deletions', 0)
    total_changes = total_additions + total_deletions
    
    # Check for sensitive patterns in title/body
    pr_text = (pr_metadata.get('title', '') + ' ' + pr_metadata.get('body', '')).lower()
    has_sensitive_keywords = any(
        re.search(pattern, pr_text, re.IGNORECASE)
        for pattern in TECH_LEAD_THRESHOLDS['always_require_for_patterns']
    )
    
    # Check if any files are in protected paths
    touches_protected = False
    for pr_file in pr_files:
        filepath = pr_file.get('path', '')
        for pattern in TECH_LEAD_THRESHOLDS['protected_paths']:
            if fnmatch(filepath, pattern):
                touches_protected = True
                break
        if touches_protected:
            break
    
    # Determine if review is required
    requires_review = (
        touches_protected or
        has_sensitive_keywords or
        total_files > TECH_LEAD_THRESHOLDS['max_files_for_optional'] or
        total_changes > TECH_LEAD_THRESHOLDS['max_lines_for_optional']
    )
    
    return {
        'total_files': total_files,
        'total_additions': total_additions,
        'total_deletions': total_deletions,
        'total_changes': total_changes,
        'touches_protected': touches_protected,
        'has_sensitive_keywords': has_sensitive_keywords,
        'requires_review': requires_review,
        'recommendation': 'required' if requires_review else 'optional'
    }


def match_pr_to_tech_leads(pr_number: str, check_complexity: bool = False) -> Dict:
    """Main function to match a PR to Tech Lead agents."""
    # Get PR files
    pr_files = get_pr_files(pr_number)
    if pr_files is None:
        return {'error': 'Failed to get PR files'}
    
    # Get PR metadata
    pr_metadata = get_pr_metadata(pr_number)
    if pr_metadata is None:
        pr_metadata = {}
    
    # Load Tech Lead agents
    tech_leads = load_tech_leads()
    if not tech_leads:
        return {
            'pr_number': pr_number,
            'tech_leads': [],
            'message': 'No Tech Lead agents found'
        }
    
    # Match files to Tech Leads
    tech_lead_matches = {}
    file_coverage = {}
    
    for pr_file in pr_files:
        filepath = pr_file.get('path', '')
        file_coverage[filepath] = []
        
        matched = match_file_to_tech_leads(filepath, tech_leads)
        for tech_lead in matched:
            name = tech_lead['name']
            if name not in tech_lead_matches:
                tech_lead_matches[name] = {
                    'agent': tech_lead,
                    'files': [],
                    'file_count': 0
                }
            tech_lead_matches[name]['files'].append(filepath)
            tech_lead_matches[name]['file_count'] += 1
            file_coverage[filepath].append(name)
    
    # Sort Tech Leads by number of files they cover (most relevant first)
    sorted_matches = sorted(
        tech_lead_matches.values(),
        key=lambda x: x['file_count'],
        reverse=True
    )
    
    result = {
        'pr_number': pr_number,
        'total_files': len(pr_files),
        'tech_leads': [
            {
                'name': match['agent']['name'],
                'specialization': match['agent']['specialization'],
                'description': match['agent']['description'],
                'file_count': match['file_count'],
                'files': match['files']
            }
            for match in sorted_matches
        ],
        'file_coverage': file_coverage
    }
    
    # Add complexity analysis if requested
    if check_complexity:
        result['complexity'] = analyze_pr_complexity(pr_files, pr_metadata)
    
    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 match-pr-to-tech-lead.py <pr_number> [--check-complexity]")
        print("\nExample:")
        print("  python3 match-pr-to-tech-lead.py 123")
        print("  python3 match-pr-to-tech-lead.py 123 --check-complexity")
        sys.exit(1)
    
    pr_number = sys.argv[1]
    check_complexity = '--check-complexity' in sys.argv
    
    result = match_pr_to_tech_leads(pr_number, check_complexity)
    
    # Pretty print the result
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    if 'error' in result:
        sys.exit(1)
    elif result.get('tech_leads'):
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
