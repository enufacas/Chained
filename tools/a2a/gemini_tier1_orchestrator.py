#!/usr/bin/env python3
"""
Gemini Tier 1 Orchestrator - Sequential workflow_call execution

Executes subtasks sequentially using workflow_call to specialized Gemini workflows.
"""

import os
import sys
import json
import time
import subprocess
from github import Github

def main():
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    execution_plan_json = os.getenv('EXECUTION_PLAN')
    
    # Load execution plan
    try:
        execution_plan = json.loads(execution_plan_json)
    except json.JSONDecodeError:
        # Try loading from file if JSON parsing fails
        plan_file = f'/tmp/a2a_execution_plan_{issue_number}.json'
        with open(plan_file, 'r') as f:
            execution_plan = json.load(f)
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    issue = repo.get_issue(issue_number)
    
    print(f"🔄 Starting Tier 1 (Sequential) Orchestration")
    print(f"   Subtasks: {len(execution_plan['subtasks'])}")
    print(f"   Execution order: {execution_plan['execution_order']}")
    
    results = []
    
    # Execute subtasks in order
    for task_id in execution_plan['execution_order']:
        # Find subtask details
        subtask = next((t for t in execution_plan['subtasks'] if t['id'] == task_id), None)
        if not subtask:
            print(f"⚠️ Subtask {task_id} not found in plan")
            continue
        
        print(f"\n▶️ Executing: {subtask['name']} ({subtask['agent_type']})")
        print(f"   Description: {subtask['description']}")
        
        # Create sub-issue for this subtask
        sub_issue_title = f"[A2A-{task_id}] {subtask['name']}"
        sub_issue_body = f"""## 🤖 A2A Subtask

**Parent Issue**: #{issue_number}
**Task ID**: {task_id}
**Agent Type**: {subtask['agent_type']}

### Description
{subtask['description']}

### Context from Parent Issue
{issue.body[:500] if issue.body else 'No description'}...

---
*This is an automated sub-task created by Gemini A2A Coordinator*
*Workflow Run: ${{{{ github.server_url }}}}/${{{{ github.repository }}}}/actions/runs/${{{{ github.run_id }}}}*"""
        
        # Create the sub-issue
        sub_issue = repo.create_issue(
            title=sub_issue_title,
            body=sub_issue_body,
            labels=['a2a-subtask', f'a2a-parent-{issue_number}', subtask['agent_type']]
        )
        
        print(f"   ✅ Created sub-issue #{sub_issue.number}")
        
        # Trigger appropriate Gemini workflow via @gemini-cli command
        command_map = {
            'design': '/invoke Please design and plan the solution',
            'implement': '/invoke Please implement the solution',
            'review': '/review',
            'test': '/invoke Please create and run tests',
            'docs': '/invoke Please write documentation',
            'security': '/invoke Please perform security review',
            'performance': '/invoke Please analyze and optimize performance'
        }
        
        command = command_map.get(subtask['agent_type'], '/invoke Please complete this task')
        
        # Post command to trigger gemini-dispatch
        sub_issue.create_comment(f"@gemini-cli {command}\n\n{subtask['description']}")
        
        print(f"   📨 Posted @gemini-cli command to sub-issue")
        
        # Wait for completion (poll for Gemini response)
        print(f"   ⏳ Waiting for Gemini to complete (timeout: 10 minutes)...")
        
        completed = False
        timeout = 600  # 10 minutes
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            time.sleep(15)  # Check every 15 seconds
            
            # Refresh issue and check comments
            sub_issue = repo.get_issue(sub_issue.number)
            comments = list(sub_issue.get_comments())
            
            # Look for Gemini completion indicators
            for comment in reversed(comments[-5:]):  # Check last 5 comments
                if 'gemini' in comment.user.login.lower():
                    comment_body = comment.body.lower()
                    # Check for completion phrases
                    if any(phrase in comment_body for phrase in ['completed', 'done', 'finished', 'summary', 'results']):
                        completed = True
                        print(f"   ✅ Subtask completed by Gemini")
                        break
            
            if completed:
                break
        
        if not completed:
            print(f"   ⚠️ Subtask timed out after 10 minutes")
        
        # Store result
        results.append({
            'task_id': task_id,
            'sub_issue_number': sub_issue.number,
            'completed': completed,
            'agent_type': subtask['agent_type']
        })
        
        # Brief pause between subtasks
        time.sleep(5)
    
    # Save results
    results_file = f'/tmp/a2a_tier1_results_{issue_number}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✨ Tier 1 orchestration complete!")
    print(f"   Completed: {sum(1 for r in results if r['completed'])}/{len(results)}")
    print(f"   Results saved to: {results_file}")
    
    # Set output for next step
    with open(os.getenv('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f"results_file={results_file}\n")

if __name__ == '__main__':
    main()
