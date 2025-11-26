#!/usr/bin/env python3
"""
Copilot Task Analyzer - Analyzes issues and maps to custom agents

Analyzes GitHub issues and determines which Copilot custom agents
should be assigned for branch-based A2A coordination.
"""

import os
import sys
import json
import re
from github import Github

# Mapping of task types to custom agent names
AGENT_MAPPING = {
    'api': 'engineer-master',
    'design': 'engineer-master',
    'implement': 'engineer-master',
    'refactor': 'organize-guru',
    'test': 'assert-specialist',
    'docs': 'support-master',
    'documentation': 'support-master',
    'security': 'secure-specialist',
    'performance': 'accelerate-master',
    'optimize': 'accelerate-master',
    'review': 'coach-master',
    'fix': 'engineer-master',
    'bug': 'engineer-master'
}

def analyze_task_type(text):
    """Determine task types from issue title and body"""
    text_lower = text.lower()
    detected_types = []
    
    for task_type, agent in AGENT_MAPPING.items():
        if task_type in text_lower:
            detected_types.append((task_type, agent))
    
    return detected_types

def main():
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    issue = repo.get_issue(issue_number)
    
    print(f"📋 Analyzing issue #{issue_number} for Copilot agent assignment")
    print(f"   Title: {issue.title}")
    
    # Analyze issue content
    full_text = f"{issue.title} {issue.body or ''}"
    detected_types = analyze_task_type(full_text)
    
    if not detected_types:
        # Default to engineer-master for general tasks
        detected_types = [('implement', 'engineer-master')]
    
    # Create agent assignments
    agent_assignments = []
    seen_agents = set()
    
    for i, (task_type, agent_name) in enumerate(detected_types):
        if agent_name in seen_agents:
            continue  # Avoid duplicate agents
        
        seen_agents.add(agent_name)
        
        assignment = {
            'task_id': f'copilot-task-{i+1}',
            'agent_name': agent_name,
            'task_type': task_type,
            'description': f'Handle {task_type} aspects of the issue'
        }
        agent_assignments.append(assignment)
    
    # Ensure at least one assignment
    if not agent_assignments:
        agent_assignments.append({
            'task_id': 'copilot-task-1',
            'agent_name': 'engineer-master',
            'task_type': 'implement',
            'description': 'Implement the requested changes'
        })
    
    print(f"\n✅ Agent analysis complete:")
    print(f"   Agents: {len(agent_assignments)}")
    for assignment in agent_assignments:
        print(f"   - {assignment['agent_name']} ({assignment['task_type']})")
    
    # Save assignments
    assignments_file = f'/tmp/a2a_copilot_assignments_{issue_number}.json'
    with open(assignments_file, 'w') as f:
        json.dump(agent_assignments, f, indent=2)
    
    print(f"\n📄 Assignments saved to: {assignments_file}")
    
    # Set GitHub Actions output
    with open(os.getenv('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f"agent_assignments={json.dumps(agent_assignments)}\n")
        f.write(f"assignments_file={assignments_file}\n")
        f.write(f"agent_count={len(agent_assignments)}\n")
    
    print("\n✨ Task analysis successful!")

if __name__ == '__main__':
    main()
