#!/usr/bin/env python3
"""
A2A Demo Script - Real Multi-Agent Communication via Gemini AI

This script demonstrates real A2A (Agent-to-Agent) protocol communication by:
1. Registering agents in a discovery service
2. Using Gemini AI to process tasks from each agent's perspective
3. Coordinating real inter-agent communication
4. Aggregating results and posting to the GitHub issue

This is NOT a simulation - it uses actual Gemini API calls to process tasks
from each agent's specialized perspective.

Usage:
    Set environment variables:
    - ISSUE_NUMBER: GitHub issue number
    - ISSUE_TITLE: Issue title
    - AGENTS: Comma-separated list of agents
    - GEMINI_API_KEY or GOOGLE_API_KEY: API key for Gemini
    
    Then run: python3 tools/a2a/demo_a2a_issue.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from tools.a2a import (
    get_discovery_service,
    generate_agent_card,
    get_agent_port
)
from tools.a2a.agent_card import parse_agent_definition


def configure_gemini() -> bool:
    """Configure Gemini API. Returns True if successful."""
    if not GEMINI_AVAILABLE:
        print("ERROR: google-generativeai package not installed")
        return False
    
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        return True
    elif google_api_key:
        genai.configure(api_key=google_api_key)
        return True
    else:
        print("ERROR: No Gemini API key configured (GEMINI_API_KEY or GOOGLE_API_KEY)")
        return False


async def call_agent_with_gemini(
    agent_name: str,
    agent_metadata: Dict[str, Any],
    task: str,
    issue_context: str
) -> Dict[str, Any]:
    """
    Call Gemini AI to process a task from a specific agent's perspective.
    
    This is the core of real A2A communication - each agent uses Gemini
    to analyze and respond to tasks based on their specialization.
    """
    specialization = agent_metadata.get('specialization', 'general assistance')
    description = agent_metadata.get('description', f'{agent_name} agent')
    personality = agent_metadata.get('personality', 'professional and helpful')
    
    # Build agent-specific prompt
    prompt = f"""You are @{agent_name}, a specialized AI agent in the Chained autonomous AI ecosystem.

**Your Specialization**: {specialization}
**Your Description**: {description}
**Your Personality**: {personality}

**Context - GitHub Issue**:
{issue_context}

**Your Task**:
{task}

**Instructions**:
1. Analyze this task from YOUR specialized perspective as @{agent_name}
2. Provide actionable recommendations based on your expertise
3. Be specific and practical
4. Format your response as JSON with the following structure:

{{
    "agent": "{agent_name}",
    "analysis": "Your analysis of the task (2-3 sentences)",
    "recommendations": [
        "Specific recommendation 1",
        "Specific recommendation 2",
        "Specific recommendation 3"
    ],
    "confidence": "high|medium|low",
    "next_steps": ["Suggested next step 1", "Suggested next step 2"]
}}

Respond with ONLY the JSON, no markdown formatting or extra text.
"""

    response_text = ''
    try:
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response if wrapped in markdown
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
        if response_text.startswith('json'):
            response_text = response_text[4:].strip()
        
        result = json.loads(response_text)
        result['status'] = 'success'
        return result
        
    except json.JSONDecodeError as e:
        return {
            'agent': agent_name,
            'status': 'error',
            'error': f'Failed to parse Gemini response as JSON: {e}',
            'raw_response': response_text[:500] if response_text else 'No response'
        }
    except Exception as e:
        return {
            'agent': agent_name,
            'status': 'error',
            'error': str(e)
        }


async def run_a2a_demo():
    """Run the real A2A demonstration using Gemini AI."""
    
    issue_number = os.environ.get('ISSUE_NUMBER', 'unknown')
    issue_title = os.environ.get('ISSUE_TITLE', 'Demo Task')
    agents_str = os.environ.get('AGENTS', 'engineer-master,secure-specialist,organize-guru')
    
    # Read issue body
    try:
        with open('/tmp/issue_body.txt', 'r') as f:
            issue_body = f.read()
    except (FileNotFoundError, IOError, PermissionError):
        issue_body = "Task description unavailable"
    
    agents = [a.strip() for a in agents_str.split(',') if a.strip()]
    
    print("=" * 70)
    print("A2A (Agent-to-Agent) Communication Demo - LIVE")
    print("=" * 70)
    print()
    print(f"Issue #{issue_number}: {issue_title}")
    print(f"Agents: {', '.join(agents)}")
    print(f"Mode: LIVE (Real Gemini API calls)")
    print()
    
    # Configure Gemini
    print("=" * 70)
    print("Phase 0: Configuring Gemini AI")
    print("=" * 70)
    print()
    
    if not configure_gemini():
        print("FATAL: Cannot proceed without Gemini API access")
        return 1
    
    print("Gemini AI configured successfully")
    print()
    
    # Initialize discovery service and register agents
    print("=" * 70)
    print("Phase 1: Agent Discovery & Registration")
    print("=" * 70)
    print()
    
    discovery = get_discovery_service()
    registered_agents = []
    
    for agent_name in agents:
        try:
            # Get agent metadata from definition file
            metadata = parse_agent_definition(agent_name)
            card = generate_agent_card(agent_name)
            port = get_agent_port(agent_name)
            skills = [s.id for s in card.skills] if card.skills else []
            
            # Register in discovery
            discovery.registry.register_agent(agent_name, port, skills)
            registered_agents.append({
                'name': agent_name,
                'port': port,
                'skills': skills,
                'url': f"http://localhost:{port}",
                'metadata': metadata
            })
            
            print(f"Registered: @{agent_name}")
            print(f"   URL: http://localhost:{port}")
            print(f"   Specialization: {metadata.get('specialization', 'N/A')}")
            if skills:
                print(f"   Skills: {', '.join(skills[:3])}")
            print()
            
        except Exception as e:
            print(f"Failed to register {agent_name}: {e}")
            print()
    
    print(f"Registered {len(registered_agents)} agents in discovery service")
    print()
    
    # Build issue context
    issue_context = f"""
Issue #{issue_number}: {issue_title}

Description:
{issue_body}
    """.strip()
    
    # Execute real A2A communication via Gemini
    print("=" * 70)
    print("Phase 2: A2A Communication (Real Gemini API Calls)")
    print("=" * 70)
    print()
    
    results = {}
    
    for i, agent_info in enumerate(registered_agents, 1):
        agent_name = agent_info['name']
        metadata = agent_info['metadata']
        port = agent_info['port']
        
        print(f"[{i}/{len(registered_agents)}] Calling @{agent_name} via Gemini AI")
        print(f"   Simulated A2A Endpoint: http://localhost:{port}/tasks")
        print(f"   Real Processing: Gemini API with agent persona")
        print()
        
        # Define task for this agent based on their specialization
        specialization = metadata.get('specialization', 'general')
        task = f"Analyze this GitHub issue from your {specialization} perspective. Provide specific, actionable recommendations."
        
        # Make real Gemini API call
        response = await call_agent_with_gemini(
            agent_name=agent_name,
            agent_metadata=metadata,
            task=task,
            issue_context=issue_context
        )
        
        results[agent_name] = response
        
        if response.get('status') == 'success':
            print(f"   Response from @{agent_name}:")
            print(f"      Analysis: {response.get('analysis', 'N/A')}")
            print(f"      Confidence: {response.get('confidence', 'N/A')}")
            recommendations = response.get('recommendations', [])
            if recommendations:
                print(f"      Recommendations:")
                for rec in recommendations:
                    print(f"         - {rec}")
            print()
        else:
            print(f"   ERROR from @{agent_name}: {response.get('error', 'Unknown error')}")
            print()
    
    # Aggregate results
    print("=" * 70)
    print("Phase 3: Result Aggregation")
    print("=" * 70)
    print()
    
    all_recommendations = []
    all_next_steps = []
    
    for agent_name, response in results.items():
        if response.get('status') == 'success':
            recs = response.get('recommendations', [])
            for rec in recs:
                all_recommendations.append(f"@{agent_name}: {rec}")
            
            steps = response.get('next_steps', [])
            for step in steps:
                all_next_steps.append(f"@{agent_name}: {step}")
    
    print("Aggregated Recommendations from all agents:")
    for i, rec in enumerate(all_recommendations, 1):
        print(f"   {i}. {rec}")
    print()
    
    if all_next_steps:
        print("Suggested Next Steps:")
        for i, step in enumerate(all_next_steps, 1):
            print(f"   {i}. {step}")
        print()
    
    # Generate summary
    print("=" * 70)
    print("Phase 4: Demo Summary")
    print("=" * 70)
    print()
    
    successful_agents = sum(1 for r in results.values() if r.get('status') == 'success')
    
    print("A2A Demo completed!")
    print()
    print("Statistics:")
    print(f"   Agents coordinated: {len(registered_agents)}")
    print(f"   Successful responses: {successful_agents}")
    print(f"   Recommendations collected: {len(all_recommendations)}")
    print(f"   Communication: Real Gemini API calls with agent personas")
    print(f"   A2A Pattern: Tier 1 (Same-Runner, Simulated HTTP Endpoints)")
    print()
    
    # Save results for GitHub comment
    with open('/tmp/demo_results.md', 'w') as f:
        f.write(f"## A2A Demo Results - LIVE\n\n")
        f.write(f"**Issue:** #{issue_number} - {issue_title}\n\n")
        f.write(f"**Mode:** Real Gemini AI calls with agent personas\n\n")
        f.write(f"### Agents Coordinated\n\n")
        for agent_info in registered_agents:
            metadata = agent_info['metadata']
            f.write(f"- **@{agent_info['name']}** - {metadata.get('specialization', 'N/A')}\n")
            f.write(f"  - Endpoint: `{agent_info['url']}`\n")
        
        f.write(f"\n### Agent Analysis & Recommendations\n\n")
        for agent_name, response in results.items():
            f.write(f"#### @{agent_name}\n\n")
            if response.get('status') == 'success':
                f.write(f"**Analysis:** {response.get('analysis', 'N/A')}\n\n")
                f.write(f"**Confidence:** {response.get('confidence', 'N/A')}\n\n")
                recommendations = response.get('recommendations', [])
                if recommendations:
                    f.write("**Recommendations:**\n")
                    for rec in recommendations:
                        f.write(f"- {rec}\n")
                next_steps = response.get('next_steps', [])
                if next_steps:
                    f.write("\n**Next Steps:**\n")
                    for step in next_steps:
                        f.write(f"- {step}\n")
            else:
                f.write(f"**Error:** {response.get('error', 'Unknown error')}\n")
            f.write("\n")
        
        f.write(f"### Aggregated Recommendations\n\n")
        for rec in all_recommendations:
            f.write(f"- {rec}\n")
        
        if all_next_steps:
            f.write(f"\n### Combined Next Steps\n\n")
            for step in all_next_steps:
                f.write(f"- {step}\n")
        
        f.write(f"\n### Demo Statistics\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Agents Coordinated | {len(registered_agents)} |\n")
        f.write(f"| Successful Responses | {successful_agents} |\n")
        f.write(f"| Recommendations | {len(all_recommendations)} |\n")
        f.write(f"| Mode | Live Gemini AI |\n")
        f.write(f"| A2A Tier | Tier 1 (Same-Runner) |\n")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_a2a_demo())
    sys.exit(exit_code)
