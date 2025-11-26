#!/usr/bin/env python3
"""
Gemini Task Analyzer - Analyzes issues and creates A2A execution plans

This script uses Gemini AI to analyze a GitHub issue and decompose it into
subtasks that can be executed by specialized Gemini agents.
"""

import os
import sys
import json
import google.generativeai as genai
from github import Github

def main():
    # Get environment variables
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    use_vertex_ai = os.getenv('USE_VERTEX_AI', 'false').lower() == 'true'
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    orchestration_tier = os.getenv('ORCHESTRATION_TIER', 'tier1')
    
    # Configure Gemini
    if use_vertex_ai and google_api_key:
        genai.configure(api_key=google_api_key)
    elif gemini_api_key:
        genai.configure(api_key=gemini_api_key)
    else:
        print("ERROR: No API key configured for Gemini")
        sys.exit(1)
    
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
    }},
    ...
  ],
  "execution_order": ["task-1", "task-2", ...],
  "estimated_duration_minutes": 25
}}

**Guidelines**:
- Keep subtasks focused and manageable
- Ensure clear dependency chains
- Choose appropriate agent types
- Be realistic about complexity
- {orchestration_tier} execution: {"sequential (one after another)" if orchestration_tier == "tier1" else "parallel (simultaneous when possible)"}
"""
    
    # Call Gemini to analyze
    model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest')
    response = model.generate_content(analysis_prompt)
    
    # Extract JSON from response
    response_text = response.text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith('```'):
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
    if response_text.startswith('json'):
        response_text = response_text[4:].strip()
    
    try:
        execution_plan = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse Gemini response as JSON: {e}")
        print(f"Response was: {response_text[:500]}")
        sys.exit(1)
    
    # Validate plan
    required_fields = ['analysis', 'complexity', 'subtasks', 'execution_order']
    if not all(field in execution_plan for field in required_fields):
        print(f"ERROR: Missing required fields in execution plan")
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
    with open(os.getenv('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
        f.write(f"execution_plan={json.dumps(execution_plan)}\n")
        f.write(f"plan_file={plan_file}\n")
        f.write(f"subtask_count={len(execution_plan['subtasks'])}\n")
    
    print("\n✨ Task decomposition successful!")

if __name__ == '__main__':
    main()
