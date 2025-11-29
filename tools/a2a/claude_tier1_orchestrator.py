#!/usr/bin/env python3
"""
Claude Tier 1 Orchestrator - Sequential execution

Executes subtasks sequentially, using Claude to process each subtask directly.
This is simpler than Gemini's approach of creating sub-issues - we just use
Claude to execute each task in sequence and aggregate results.
"""

import os
import sys
import json
import time
from github import Github


def get_claude_client():
    """Get the appropriate Claude client based on configuration."""
    use_vertex = os.getenv('CLAUDE_CODE_USE_VERTEX', 'false').lower() in ('true', '1')
    
    if use_vertex:
        from anthropic import AnthropicVertex
        
        project_id = os.getenv('ANTHROPIC_VERTEX_PROJECT_ID')
        region = os.getenv('CLOUD_ML_REGION', 'us-east5')
        
        if not project_id:
            print("ERROR: ANTHROPIC_VERTEX_PROJECT_ID not set for Vertex AI")
            sys.exit(1)
        
        client = AnthropicVertex(project_id=project_id, region=region)
        return client, "claude-sonnet-4@20250514"
    else:
        from anthropic import Anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("ERROR: ANTHROPIC_API_KEY not set")
            sys.exit(1)
        
        client = Anthropic(api_key=api_key)
        return client, "claude-sonnet-4-20250514"


def execute_subtask(client, model_name, subtask, parent_context):
    """Execute a single subtask using Claude."""
    
    # Create task prompt based on agent type
    agent_prompts = {
        'design': "You are a software architect. Design and plan a solution.",
        'implement': "You are a software engineer. Implement the solution.",
        'review': "You are a code reviewer. Review the code for issues.",
        'test': "You are a QA engineer. Create and describe test cases.",
        'docs': "You are a technical writer. Write clear documentation.",
        'security': "You are a security expert. Analyze for vulnerabilities.",
        'performance': "You are a performance engineer. Analyze and optimize."
    }
    
    system_prompt = agent_prompts.get(
        subtask['agent_type'],
        "You are a helpful AI assistant."
    )
    
    task_prompt = f"""## Task: {subtask['name']}

### Description
{subtask['description']}

### Context from Parent Issue
{parent_context[:2000] if parent_context else 'No additional context'}

### Instructions
Complete this task thoroughly. Provide:
1. Your analysis or approach
2. Your solution or output
3. Any recommendations or next steps

Be concise but comprehensive."""

    response = client.messages.create(
        model=model_name,
        max_tokens=4096,
        temperature=0.5,
        system=system_prompt,
        messages=[{"role": "user", "content": task_prompt}],
    )
    
    return response.content[0].text


def main():
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    execution_plan_json = os.getenv('EXECUTION_PLAN')
    
    # Load execution plan
    try:
        execution_plan = json.loads(execution_plan_json)
    except (json.JSONDecodeError, TypeError):
        # Try loading from file if JSON parsing fails
        plan_file = f'/tmp/a2a_execution_plan_{issue_number}.json'
        with open(plan_file, 'r') as f:
            execution_plan = json.load(f)
    
    # Get Claude client
    client, model_name = get_claude_client()
    
    # Get issue context
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    issue = repo.get_issue(issue_number)
    parent_context = f"**Issue**: {issue.title}\n\n{issue.body or 'No description'}"
    
    print(f"🔄 Starting Tier 1 (Sequential) Orchestration with Claude")
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
        
        start_time = time.time()
        
        try:
            # Execute subtask with Claude
            result_text = execute_subtask(client, model_name, subtask, parent_context)
            elapsed = time.time() - start_time
            
            print(f"   ✅ Completed in {elapsed:.1f}s")
            
            results.append({
                'task_id': task_id,
                'name': subtask['name'],
                'agent_type': subtask['agent_type'],
                'completed': True,
                'result': result_text,
                'elapsed_seconds': elapsed
            })
            
            # Add result to context for subsequent tasks
            parent_context += f"\n\n---\n**Completed Task**: {subtask['name']}\n{result_text[:1000]}"
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append({
                'task_id': task_id,
                'name': subtask['name'],
                'agent_type': subtask['agent_type'],
                'completed': False,
                'error': str(e)
            })
        
        # Brief pause between subtasks
        time.sleep(2)
    
    # Save results
    results_file = f'/tmp/a2a_tier1_results_{issue_number}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    completed_count = sum(1 for r in results if r.get('completed'))
    print(f"\n✨ Tier 1 orchestration complete!")
    print(f"   Completed: {completed_count}/{len(results)}")
    print(f"   Results saved to: {results_file}")
    
    # Set output for next step
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"results_file={results_file}\n")
            f.write(f"completed_count={completed_count}\n")


if __name__ == '__main__':
    main()
