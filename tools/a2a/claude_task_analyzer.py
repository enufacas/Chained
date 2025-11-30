#!/usr/bin/env python3
"""
Claude Task Analyzer - Analyzes issues and creates A2A execution plans

This script uses Claude AI to analyze a GitHub issue and decompose it into
subtasks that can be executed by specialized agents.

Supports both direct Anthropic API and Google Vertex AI authentication.
"""

import os
import sys
import json

from github import Github


def get_claude_client():
    """Get the appropriate Claude client based on configuration."""
    use_vertex = os.getenv('CLAUDE_CODE_USE_VERTEX', 'false').lower() in ('true', '1')
    
    if use_vertex:
        # Use Vertex AI
        try:
            from anthropic import AnthropicVertex
            
            project_id = os.getenv('ANTHROPIC_VERTEX_PROJECT_ID')
            region = os.getenv('CLOUD_ML_REGION', 'us-east5')
            
            if not project_id:
                print("ERROR: ANTHROPIC_VERTEX_PROJECT_ID not set for Vertex AI")
                sys.exit(1)
            
            client = AnthropicVertex(project_id=project_id, region=region)
            print(f"✓ Using Claude via Vertex AI (region: {region})")
            return client, "claude-sonnet-4@20250514"
            
        except ImportError:
            print("ERROR: anthropic package not installed")
            sys.exit(1)
    else:
        # Use direct Anthropic API
        try:
            from anthropic import Anthropic
            
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                print("ERROR: ANTHROPIC_API_KEY not set")
                sys.exit(1)
            
            client = Anthropic(api_key=api_key)
            print("✓ Using Claude via direct Anthropic API")
            return client, "claude-sonnet-4-20250514"
            
        except ImportError:
            print("ERROR: anthropic package not installed")
            sys.exit(1)


def main():
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    orchestration_tier = os.getenv('ORCHESTRATION_TIER', 'tier1')
    
    # Get Claude client
    client, model_name = get_claude_client()
    
    # Get issue details
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    issue = repo.get_issue(issue_number)
    
    print(f"📋 Analyzing issue #{issue_number}: {issue.title}")
    print(f"🎯 Orchestration tier: {orchestration_tier}")
    
    # Create analysis prompt
    analysis_prompt = f"""You are an AI task coordinator. Analyze this GitHub issue and create an execution plan for multi-agent collaboration.

**Issue Title**: {issue.title}
**Issue Body**:
{issue.body or 'No description provided'}

**Your Task**:
1. Break down this issue into 2-5 discrete subtasks
2. For each subtask, specify:
   - Task name (concise, 3-5 words)
   - Agent type (design/implement/review/test/docs/security/performance)
   - Description (1-2 sentences)
   - Dependencies (which other subtasks must complete first)
   - Estimated complexity (low/medium/high)

**Output Format** (JSON only, no markdown):
{{
  "analysis": "Brief analysis of the task (2-3 sentences)",
  "complexity": "low|medium|high",
  "subtasks": [
    {{
      "id": "task-1",
      "name": "Design API schema",
      "agent_type": "design",
      "description": "Create OpenAPI specification for the REST API",
      "dependencies": [],
      "complexity": "medium"
    }}
  ],
  "execution_order": ["task-1", "task-2"],
  "estimated_duration_minutes": 25
}}

**Guidelines**:
- Keep subtasks focused and manageable
- Ensure clear dependency chains
- Choose appropriate agent types
- Be realistic about complexity
- {orchestration_tier} execution: {"sequential (one after another)" if orchestration_tier == "tier1" else "parallel (simultaneous when possible)"}

Output only valid JSON, no explanation text before or after."""
    
    # Call Claude to analyze
    response = client.messages.create(
        model=model_name,
        max_tokens=2048,
        temperature=0.3,
        messages=[{"role": "user", "content": analysis_prompt}],
    )
    
    # Extract response text
    response_text = response.content[0].text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
    if response_text.startswith('json'):
        response_text = response_text[4:].strip()
    
    try:
        execution_plan = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse Claude response as JSON: {e}")
        print(f"Response was: {response_text[:500]}")
        sys.exit(1)
    
    # Validate plan
    required_fields = ['analysis', 'complexity', 'subtasks', 'execution_order']
    if not all(field in execution_plan for field in required_fields):
        print("ERROR: Missing required fields in execution plan")
        sys.exit(1)
    
    print(f"\n✅ Task analysis complete:")
    print(f"   Complexity: {execution_plan['complexity']}")
    print(f"   Subtasks: {len(execution_plan['subtasks'])}")
    print(f"   Est. duration: {execution_plan.get('estimated_duration_minutes', 'unknown')} minutes")
    
    # Save plan to file and output
    plan_file = f'/tmp/a2a_execution_plan_{issue_number}.json'
    with open(plan_file, 'w') as f:
        json.dump(execution_plan, f, indent=2)
    
    print(f"\n📄 Execution plan saved to: {plan_file}")
    
    # Set GitHub Actions output
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"execution_plan={json.dumps(execution_plan)}\n")
            f.write(f"plan_file={plan_file}\n")
            f.write(f"subtask_count={len(execution_plan['subtasks'])}\n")
    
    print("\n✨ Task decomposition successful!")


if __name__ == '__main__':
    main()
