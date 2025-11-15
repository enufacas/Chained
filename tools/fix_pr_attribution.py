#!/usr/bin/env python3
"""
Update issue_history.json with PR numbers from git log - @assert-specialist

This script repairs missing PR attribution by:
1. Reading issue_history.json
2. Finding PRs for issues via git log
3. Updating pr_number fields that are null

This is the actual fix for the PR attribution problem.
"""

import json
import subprocess
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

ISSUE_HISTORY_PATH = Path('.github/agent-system/issue_history.json')

def find_prs_from_git_log() -> Dict[int, List[int]]:
    """
    Parse git log to find PR numbers that closed issues.
    
    Returns:
        Dict mapping issue_number -> [pr_numbers]
    """
    print("🔍 Scanning git log for PR → Issue mappings...")
    
    issue_to_prs: Dict[int, List[int]] = {}
    
    try:
        # Get all merge commits (these are PRs)
        result = subprocess.run(
            ['git', 'log', '--merges', '--oneline', '-n', '1000'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ Git log failed: {result.stderr}", file=sys.stderr)
            return issue_to_prs
        
        # Patterns to find PRs and issues
        # Merge commit format: "Merge pull request #123 from..."
        # Issue references: "Fixes #456", "Closes #789", etc.
        merge_pr_pattern = re.compile(r'Merge pull request #(\d+)')
        issue_patterns = [
            re.compile(r'(?:Fix|Fixes|Close|Closes|Resolve|Resolves)\s+#(\d+)', re.IGNORECASE),
            re.compile(r'\(#(\d+)\)'),  # Often in merge commits: "(#123)"
        ]
        
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            # Find PR number from merge commit
            merge_match = merge_pr_pattern.search(line)
            if merge_match:
                pr_number = int(merge_match.group(1))
                
                # Find issue references in the same commit message
                issues_found: Set[int] = set()
                for pattern in issue_patterns:
                    for match in pattern.finditer(line):
                        issue_num = int(match.group(1))
                        # Filter out PR numbers being mistaken for issues
                        if issue_num != pr_number:
                            issues_found.add(issue_num)
                
                # Map each issue to this PR
                for issue_num in issues_found:
                    if issue_num not in issue_to_prs:
                        issue_to_prs[issue_num] = []
                    if pr_number not in issue_to_prs[issue_num]:
                        issue_to_prs[issue_num].append(pr_number)
                        print(f"  📎 Issue #{issue_num} → PR #{pr_number}")
    
    except subprocess.TimeoutExpired:
        print(f"❌ Git log timeout", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error parsing git log: {e}", file=sys.stderr)
    
    return issue_to_prs

def update_issue_history(dry_run: bool = False) -> int:
    """
    Update issue_history.json with PR numbers from git log.
    
    Args:
        dry_run: If True, don't actually write changes
        
    Returns:
        Number of records updated
    """
    print(f"\n{'=' * 70}")
    print("Update Issue History with PR Numbers - @assert-specialist")
    print(f"{'=' * 70}")
    
    if not ISSUE_HISTORY_PATH.exists():
        print(f"❌ Issue history not found: {ISSUE_HISTORY_PATH}")
        return 0
    
    # Load issue history
    with open(ISSUE_HISTORY_PATH, 'r') as f:
        history = json.load(f)
    
    issues = history.get('issues', [])
    print(f"\n📂 Loaded {len(issues)} issue records")
    
    # Count nulls before
    null_count_before = sum(1 for issue in issues if issue.get('pr_number') is None)
    print(f"   Issues with pr_number=null: {null_count_before} ({null_count_before/len(issues)*100:.1f}%)")
    
    # Get PR mappings from git
    issue_to_prs = find_prs_from_git_log()
    print(f"\n✅ Found {len(issue_to_prs)} issues with PR references in git log")
    
    # Update issue records
    updated_count = 0
    for issue_record in issues:
        issue_num = issue_record.get('issue_number')
        current_pr = issue_record.get('pr_number')
        
        # Only update if pr_number is null and we found a PR
        if current_pr is None and issue_num in issue_to_prs:
            prs = issue_to_prs[issue_num]
            # Use the most recent (highest numbered) PR
            pr_to_use = max(prs)
            
            issue_record['pr_number'] = pr_to_use
            updated_count += 1
            print(f"  🔧 Updated issue #{issue_num}: pr_number = {pr_to_use}")
    
    # Count nulls after
    null_count_after = sum(1 for issue in issues if issue.get('pr_number') is None)
    
    print(f"\n📊 Summary:")
    print(f"   Records updated: {updated_count}")
    print(f"   Null before: {null_count_before}")
    print(f"   Null after: {null_count_after}")
    print(f"   Fixed: {null_count_before - null_count_after} records")
    
    # Save if not dry run
    if dry_run:
        print(f"\n🚫 DRY RUN: Changes not saved")
    else:
        if updated_count > 0:
            # Backup original
            backup_path = ISSUE_HISTORY_PATH.with_suffix('.json.backup')
            import shutil
            shutil.copy2(ISSUE_HISTORY_PATH, backup_path)
            print(f"\n💾 Backup created: {backup_path}")
            
            # Save updated history
            with open(ISSUE_HISTORY_PATH, 'w') as f:
                json.dump(history, f, indent=2)
            
            print(f"✅ Updated issue_history.json with {updated_count} PR numbers")
        else:
            print(f"\n📝 No changes needed")
    
    return updated_count

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix PR attribution in issue_history.json - @assert-specialist'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without actually changing it'
    )
    
    args = parser.parse_args()
    
    updated = update_issue_history(dry_run=args.dry_run)
    
    if updated > 0:
        print(f"\n✨ Success! Fixed PR attribution for {updated} issues")
        print(f"\n📝 Next steps:")
        print(f"   1. Review the changes in issue_history.json")
        print(f"   2. Run: python tools/agent-metrics-collector.py")
        print(f"   3. Verify agent scores now show proper PR attribution")
    else:
        print(f"\n📝 No updates needed - all issues already have PR numbers")
        print(f"   or no PR references found in git log")

if __name__ == '__main__':
    main()
