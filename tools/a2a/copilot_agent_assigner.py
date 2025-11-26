#!/usr/bin/env python3
"""
Copilot Agent Assigner - Creates sub-issues and assigns custom agents via GraphQL

Creates sub-issues for each subtask and uses GraphQL to assign custom Copilot agents.
"""

import os
import sys
import json
import subprocess
from github import Github

def get_custom_agent_actor_id(repo_owner, repo_name, agent_name):
    """Query GitHub GraphQL API for custom agent actor ID"""
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
          nodes {
            login
            __typename
            ... on Bot { id }
            ... on User { id }
          }
        }
      }
    }
    """
    
    # Execute GraphQL query via gh CLI
    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={query}', 
         '-f', f'owner={repo_owner}', '-f', f'repo={repo_name}'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"ERROR querying GraphQL: {result.stderr}")
        return None
    
    try:
        data = json.loads(result.stdout)
        actors = data['data']['repository']['suggestedActors']['nodes']
        
        # Find agent by name
        for actor in actors:
            if actor['login'] == agent_name:
                return actor['id']
    except (json.JSONDecodeError, KeyError) as e:
        print(f"ERROR parsing GraphQL response: {e}")
    
    return None

def assign_agent_to_issue(issue_id, actor_id):
    """Assign agent to issue via GraphQL mutation"""
    mutation = """
    mutation($issueId: ID!, $actorId: ID!) {
      addAssigneesToAssignable(input: {assignableId: $issueId, assigneeIds: [$actorId]}) {
        assignable {
          assignees(first: 10) {
            nodes {
              login
            }
          }
        }
      }
    }
    """
    
    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={mutation}',
         '-f', f'issueId={issue_id}', '-f', f'actorId={actor_id}'],
        capture_output=True,
        text=True
    )
    
    return result.returncode == 0

def main():
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    assignments_json = os.getenv('AGENT_ASSIGNMENTS')
    
    # Load assignments
    try:
        agent_assignments = json.loads(assignments_json)
    except json.JSONDecodeError:
        assignments_file = f'/tmp/a2a_copilot_assignments_{issue_number}.json'
        with open(assignments_file, 'r') as f:
            agent_assignments = json.load(f)
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    parent_issue = repo.get_issue(issue_number)
    
    repo_owner = os.getenv('GITHUB_REPOSITORY_OWNER')
    repo_name = os.getenv('GITHUB_REPOSITORY').split('/')[-1]
    
    print(f"🔗 Creating sub-issues and assigning Copilot agents")
    print(f"   Parent issue: #{issue_number}")
    print(f"   Agents to assign: {len(agent_assignments)}")
    
    sub_issues = []
    
    for assignment in agent_assignments:
        task_id = assignment['task_id']
        agent_name = assignment['agent_name']
        task_type = assignment['task_type']
        description = assignment['description']
        
        print(f"\n▶️ Creating sub-issue for: {agent_name}")
        
        # Create sub-issue
        sub_issue_title = f"[A2A-{task_id}] {task_type.title()} - {parent_issue.title[:50]}"
        sub_issue_body = f"""## 🤖 Copilot A2A Subtask

**Parent Issue**: #{issue_number}
**Task ID**: {task_id}
**Assigned Agent**: @{agent_name}
**Task Type**: {task_type}

### Description
{description}

### Context from Parent Issue
{parent_issue.body[:1000] if parent_issue.body else 'No description provided'}

### A2A Communication
This task is part of branch-based A2A coordination. 

**A2A-TASK-BRANCH**: `a2a-tasks/{task_id}-{{{{timestamp}}}}`

When you complete your work, push results to the A2A task branch as `result.json`.

---
*This is an automated sub-task created by Copilot A2A Coordinator*
*Parent Issue: #{issue_number}*
*Agent: @{agent_name}*"""
        
        sub_issue = repo.create_issue(
            title=sub_issue_title,
            body=sub_issue_body,
            labels=['a2a-subtask', f'a2a-parent-{issue_number}', 'copilot', task_type]
        )
        
        print(f"   ✅ Created sub-issue #{sub_issue.number}")
        
        # Try to assign custom agent via GraphQL
        print(f"   🔍 Looking up custom agent actor ID for: {agent_name}")
        actor_id = get_custom_agent_actor_id(repo_owner, repo_name, agent_name)
        
        if actor_id:
            print(f"   ✅ Found actor ID: {actor_id}")
            print(f"   📌 Assigning @{agent_name} to sub-issue...")
            
            # Get issue node ID for GraphQL
            issue_node_id = sub_issue.raw_data['node_id']
            
            if assign_agent_to_issue(issue_node_id, actor_id):
                print(f"   ✅ Successfully assigned @{agent_name}")
            else:
                print(f"   ⚠️ Failed to assign via GraphQL, will use fallback")
        else:
            print(f"   ⚠️ Custom agent @{agent_name} not found, using generic Copilot")
        
        sub_issues.append({
            'task_id': task_id,
            'sub_issue_number': sub_issue.number,
            'agent_name': agent_name,
            'assigned': actor_id is not None
        })
    
    # Save sub-issue info
    sub_issues_file = f'/tmp/a2a_copilot_sub_issues_{issue_number}.json'
    with open(sub_issues_file, 'w') as f:
        json.dump(sub_issues, f, indent=2)
    
    print(f"\n✨ Sub-issues created and agents assigned!")
    print(f"   Total: {len(sub_issues)}")
    print(f"   Assigned: {sum(1 for s in sub_issues if s['assigned'])}")
    print(f"   Saved to: {sub_issues_file}")
    
    # Set output
    with open(os.getenv('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f"sub_issues_file={sub_issues_file}\n")

if __name__ == '__main__':
    main()
