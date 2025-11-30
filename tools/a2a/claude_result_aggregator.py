#!/usr/bin/env python3
"""
Claude Result Aggregator - Collects and summarizes multi-agent results

Uses Claude to synthesize results from all subtasks into a cohesive summary.
"""

import os
import sys
import json
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


def main():
    github_token = os.getenv('GITHUB_TOKEN')
    issue_number = int(os.getenv('ISSUE_NUMBER'))
    
    g = Github(github_token)
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    issue = repo.get_issue(issue_number)
    
    # Try both tier1 and tier2 results files
    results = []
    for tier in ['tier1', 'tier2']:
        results_file = f'/tmp/a2a_{tier}_results_{issue_number}.json'
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
            print(f"✓ Loaded results from {tier}")
            break
        except FileNotFoundError:
            continue
    
    if not results:
        print("⚠️ No results file found")
        results = []
    
    print(f"📊 Aggregating results for issue #{issue_number}")
    print(f"   Subtasks: {len(results)}")
    
    completed_count = sum(1 for r in results if r.get('completed', False))
    
    # Build results summary for Claude synthesis
    results_text = ""
    for result in results:
        status = "✅" if result.get('completed') else "❌"
        results_text += f"\n### {status} Task: {result.get('name', result['task_id'])} ({result['agent_type']})\n"
        
        if result.get('completed'):
            result_content = result.get('result', 'No result captured')
            # Truncate long results
            if len(result_content) > 2000:
                result_content = result_content[:2000] + "... [truncated]"
            results_text += f"{result_content}\n"
        else:
            results_text += f"Failed: {result.get('error', 'Unknown error')}\n"
    
    # Use Claude to synthesize results into a cohesive summary
    synthesis = ""
    if results and completed_count > 0:
        try:
            client, model_name = get_claude_client()
            
            synthesis_prompt = f"""Synthesize these multi-agent task results into a cohesive summary.

**Original Issue**: {issue.title}

**Task Results**:
{results_text}

**Instructions**:
1. Summarize what was accomplished
2. Highlight key findings or outputs
3. Note any issues or failures
4. Provide recommended next steps

Keep the summary concise (under 500 words)."""

            response = client.messages.create(
                model=model_name,
                max_tokens=1024,
                temperature=0.3,
                messages=[{"role": "user", "content": synthesis_prompt}],
            )
            
            synthesis = response.content[0].text
            print("✓ Generated synthesis summary")
            
        except Exception as e:
            print(f"⚠️ Could not generate synthesis: {e}")
            synthesis = "Synthesis not available."
    
    # Create summary comment
    summary = f"""## 🎯 Claude A2A Coordination Summary

**Parent Issue**: #{issue_number}
**Total Subtasks**: {len(results)}
**Completed**: {completed_count}/{len(results)}

### Task Status

"""
    
    for result in results:
        status = "✅" if result.get('completed') else "❌"
        elapsed = result.get('elapsed_seconds', 0)
        time_str = f" ({elapsed:.1f}s)" if elapsed else ""
        summary += f"- {status} **{result.get('name', result['task_id'])}** ({result['agent_type']}){time_str}\n"
    
    if synthesis:
        summary += f"""
### Synthesis

{synthesis}
"""
    
    summary += f"""
---
*Claude A2A Coordinator | [View workflow run]({os.getenv('GITHUB_SERVER_URL', 'https://github.com')}/{os.getenv('GITHUB_REPOSITORY', '')}/actions/runs/{os.getenv('GITHUB_RUN_ID', 'unknown')})*"""
    
    # Post summary
    issue.create_comment(summary)
    
    print(f"\n✨ Results aggregated and posted to issue #{issue_number}")


if __name__ == '__main__':
    main()
