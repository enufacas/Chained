#!/usr/bin/env python3
"""
Claude Tier 2 Orchestrator - Parallel execution

Executes independent subtasks in parallel using asyncio, while respecting
task dependencies.

Note: This is a simple in-process parallel execution. For true cross-runner
parallelism, you would create sub-issues and use GitHub-mediated communication
(like the Gemini approach with gemini-dispatch).
"""

import asyncio
import os
import sys
import json
import time
from typing import Dict, List, Any
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


async def execute_subtask_async(client, model_name, subtask, parent_context):
    """Execute a single subtask using Claude (async wrapper)."""
    
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

    # Run synchronous API call in thread pool
    def sync_call():
        return client.messages.create(
            model=model_name,
            max_tokens=4096,
            temperature=0.5,
            system=system_prompt,
            messages=[{"role": "user", "content": task_prompt}],
        )
    
    response = await asyncio.to_thread(sync_call)
    return response.content[0].text


def build_dependency_graph(subtasks: List[Dict]) -> Dict[str, List[str]]:
    """Build a graph showing which tasks each task depends on."""
    graph = {}
    for task in subtasks:
        task_id = task['id']
        dependencies = task.get('dependencies', [])
        graph[task_id] = dependencies
    return graph


def get_ready_tasks(
    graph: Dict[str, List[str]],
    completed: set,
    running: set
) -> List[str]:
    """Get tasks that are ready to run (dependencies met)."""
    ready = []
    for task_id, deps in graph.items():
        if task_id in completed or task_id in running:
            continue
        if all(dep in completed for dep in deps):
            ready.append(task_id)
    return ready


async def main_async():
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    execution_plan_json = os.getenv('EXECUTION_PLAN')
    
    # Load execution plan
    try:
        execution_plan = json.loads(execution_plan_json)
    except (json.JSONDecodeError, TypeError):
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
    
    subtasks = execution_plan['subtasks']
    
    print(f"🔄 Starting Tier 2 (Parallel) Orchestration with Claude")
    print(f"   Subtasks: {len(subtasks)}")
    
    # Build dependency graph
    dep_graph = build_dependency_graph(subtasks)
    subtask_map = {t['id']: t for t in subtasks}
    
    # Track state
    completed: set = set()
    running: set = set()
    results: List[Dict[str, Any]] = []
    task_results: Dict[str, str] = {}  # For passing results to dependent tasks
    
    # Maximum concurrent tasks
    max_concurrent = 3
    
    while len(completed) < len(subtasks):
        # Get tasks ready to run
        ready = get_ready_tasks(dep_graph, completed, running)
        
        if not ready and not running:
            # Deadlock or all done
            break
        
        # Start ready tasks (up to max concurrent)
        tasks_to_start = ready[:max_concurrent - len(running)]
        
        if tasks_to_start:
            print(f"\n▶️ Starting {len(tasks_to_start)} task(s) in parallel: {tasks_to_start}")
            
            async def run_task(task_id):
                subtask = subtask_map[task_id]
                print(f"   🏃 {task_id}: {subtask['name']}")
                
                # Build context including results from dependencies
                context = parent_context
                for dep in subtask.get('dependencies', []):
                    if dep in task_results:
                        context += f"\n\n---\n**Result from {dep}**:\n{task_results[dep][:1000]}"
                
                start_time = time.time()
                try:
                    result = await execute_subtask_async(
                        client, model_name, subtask, context
                    )
                    elapsed = time.time() - start_time
                    return {
                        'task_id': task_id,
                        'name': subtask['name'],
                        'agent_type': subtask['agent_type'],
                        'completed': True,
                        'result': result,
                        'elapsed_seconds': elapsed
                    }
                except Exception as e:
                    return {
                        'task_id': task_id,
                        'name': subtask['name'],
                        'agent_type': subtask['agent_type'],
                        'completed': False,
                        'error': str(e)
                    }
            
            # Mark tasks as running
            for task_id in tasks_to_start:
                running.add(task_id)
            
            # Execute tasks concurrently
            task_futures = [run_task(tid) for tid in tasks_to_start]
            batch_results = await asyncio.gather(*task_futures)
            
            # Process results
            for result in batch_results:
                task_id = result['task_id']
                running.discard(task_id)
                completed.add(task_id)
                results.append(result)
                
                if result.get('completed'):
                    print(f"   ✅ {task_id}: completed in {result['elapsed_seconds']:.1f}s")
                    task_results[task_id] = result.get('result', '')
                else:
                    print(f"   ❌ {task_id}: failed - {result.get('error')}")
        
        # Small delay between batches
        await asyncio.sleep(1)
    
    # Save results
    results_file = f'/tmp/a2a_tier2_results_{issue_number}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    completed_count = sum(1 for r in results if r.get('completed'))
    print(f"\n✨ Tier 2 orchestration complete!")
    print(f"   Completed: {completed_count}/{len(results)}")
    print(f"   Results saved to: {results_file}")
    
    # Set output for next step
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"results_file={results_file}\n")
            f.write(f"completed_count={completed_count}\n")


def main():
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
