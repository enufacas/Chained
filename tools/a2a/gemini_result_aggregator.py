#!/usr/bin/env python3
"""
Gemini Result Aggregator - Collects and summarizes multi-agent results
"""

import os
import sys
import json
from github import Github

def main():
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    issue = repo.get_issue(issue_number)
    
    # Load results
    results_file = f'/tmp/a2a_tier1_results_{issue_number}.json'
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("⚠️ No results file found")
        results = []
    
    print(f"📊 Aggregating results for issue #{issue_number}")
    print(f"   Subtasks: {len(results)}")
    
    # Create summary
    summary = f"""## 🎯 A2A Coordination Summary

**Parent Issue**: #{issue_number}
**Total Subtasks**: {len(results)}
**Completed**: {sum(1 for r in results if r.get('completed', False))}

### Subtask Results

"""
    
    for result in results:
        status = "✅" if result.get('completed') else "⏸️"
        summary += f"{status} **Task {result['task_id']}** ({result['agent_type']}) - Issue #{result['sub_issue_number']}\n"
    
    summary += f"\n---\n*A2A coordination completed by Gemini Coordinator*"
    
    # Post summary
    issue.create_comment(summary)
    
    print(f"\n✨ Results aggregated and posted to issue")

if __name__ == '__main__':
    main()
