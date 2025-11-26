#!/usr/bin/env python3
"""
Copilot Coordination Summary - Posts final summary to parent issue
"""

import os
import json
from github import Github

def main():
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    issue = repo.get_issue(issue_number)
    
    # Load sub-issue info
    sub_issues_file = f'/tmp/a2a_copilot_sub_issues_{issue_number}.json'
    try:
        with open(sub_issues_file, 'r') as f:
            sub_issues = json.load(f)
    except FileNotFoundError:
        sub_issues = []
    
    print(f"📊 Creating coordination summary for issue #{issue_number}")
    
    # Create summary
    summary = f"""## 🔗 Copilot A2A Coordination Summary

**Parent Issue**: #{issue_number}
**Total Agents**: {len(sub_issues)}
**Communication Method**: Branch-based message bus

### Agent Assignments

"""
    
    for sub_issue in sub_issues:
        assigned_status = "✅" if sub_issue.get('assigned') else "⏸️"
        summary += f"{assigned_status} **@{sub_issue['agent_name']}** - Issue #{sub_issue['sub_issue_number']} (Task: {sub_issue['task_id']})\n"
    
    summary += f"\n### Next Steps\n\n"
    summary += "The assigned Copilot agents will work on their respective sub-issues. "
    summary += "They will communicate via branch-based A2A protocol. "
    summary += "Check the sub-issues for progress updates.\n\n"
    summary += "---\n*A2A coordination completed by Copilot A2A Coordinator*"
    
    # Post summary
    issue.create_comment(summary)
    
    print(f"\n✨ Coordination summary posted to issue")

if __name__ == '__main__':
    main()
