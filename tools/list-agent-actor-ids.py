#!/usr/bin/env python3
"""
List Custom Agent Actor IDs.

An elegant tool that bridges the gap between custom agent definitions and
GitHub's actor system. It reveals which agents have assignable actor IDs,
enabling direct programmatic assignment through the GitHub API.

Features:
    • Query repository actors via GraphQL
    • Scan custom agent definitions
    • Map agents to actor IDs
    • Provide actionable API examples

Usage:
    export GH_TOKEN="your_github_token"
    python3 list-agent-actor-ids.py <owner> <repo>
    
Example:
    python3 list-agent-actor-ids.py enufacas Chained
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any


def execute_github_cli(args: List[str], env: Optional[Dict] = None) -> Optional[str]:
    """
    Execute a GitHub CLI command with elegant error handling.
    
    This function wraps the gh CLI, providing a clean interface for
    running commands while gracefully handling failures.
    
    Args:
        args: List of command arguments (excluding 'gh' itself)
        env: Optional environment dictionary (defaults to os.environ)
        
    Returns:
        Command output as string, or None if execution fails
    """
    if env is None:
        env = os.environ.copy()
    
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return result.stdout
    except subprocess.CalledProcessError as error:
        print(f"❌ GitHub CLI command failed: {error.stderr}", file=sys.stderr)
        return None


def fetch_assignable_actors(owner: str, repo: str) -> List[Dict[str, Any]]:
    """
    Retrieve all actors assignable to repository issues.
    
    Queries GitHub's GraphQL API to discover which actors (users and bots)
    possess the CAN_BE_ASSIGNED capability for the specified repository.
    
    Args:
        owner: Repository owner username
        repo: Repository name
        
    Returns:
        List of actor dictionaries containing login, type, and ID details
    """
    query = '''
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
          nodes {
            login
            __typename
            ... on Bot { 
              id
              databaseId
              url
            }
            ... on User { 
              id
              databaseId
              url
            }
          }
        }
      }
    }
    '''
    
    output = execute_github_cli([
        'api', 'graphql',
        '-f', f'query={query}',
        '-f', f'owner={owner}',
        '-f', f'repo={repo}'
    ])
    
    if output:
        try:
            result = json.loads(output)
            return result.get('data', {}).get('repository', {}).get('suggestedActors', {}).get('nodes', [])
        except json.JSONDecodeError as error:
            print(f"❌ JSON parsing failed: {error}", file=sys.stderr)
    
    return []


def discover_custom_agents() -> List[Dict[str, str]]:
    """
    Discover custom agent definition files.
    
    Scans the .github/agents/ directory for markdown files that define
    custom agent personas, each with unique capabilities and specializations.
    
    Returns:
        List of dictionaries containing agent name and file path,
        sorted alphabetically by name
    """
    agents_directory = Path('.github/agents')
    if not agents_directory.exists():
        return []
    
    agents = [
        {'name': agent_file.stem, 'path': str(agent_file)}
        for agent_file in agents_directory.glob('*.md')
        if agent_file.name != 'README.md'
    ]
    
    return sorted(agents, key=lambda agent: agent['name'])


def main() -> int:
    """
    Main orchestration function for the actor ID listing tool.
    
    Coordinates the discovery of custom agents and their corresponding
    GitHub actor IDs, presenting findings in a clear and actionable format.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if len(sys.argv) != 3:
        print("Usage: python3 list-agent-actor-ids.py <owner> <repo>")
        print("Example: python3 list-agent-actor-ids.py enufacas Chained")
        sys.exit(1)
    
    owner = sys.argv[1]
    repo = sys.argv[2]
    
    if not os.environ.get('GH_TOKEN') and not os.environ.get('GITHUB_TOKEN'):
        print("⚠️  WARNING: No GH_TOKEN or GITHUB_TOKEN environment variable set")
        print("Set a token to query the GitHub API:")
        print("  export GH_TOKEN='your_token_here'")
        print()
    
    print("="*70)
    print("📋 Custom Agent Actor ID List")
    print("="*70)
    print(f"Repository: {owner}/{repo}")
    print()
    
    # Get all suggested actors
    print("🔍 Querying GitHub API for available actors...")
    actors = fetch_assignable_actors(owner, repo)
    
    if not actors:
        print("❌ Failed to retrieve actors (check token permissions)")
        return 1
    
    print(f"✅ Found {len(actors)} total actors")
    print()
    
    # Get custom agents from files
    print("📁 Scanning .github/agents/ directory...")
    custom_agents = discover_custom_agents()
    
    if not custom_agents:
        print("❌ No custom agent files found in .github/agents/")
        return 1
    
    print(f"✅ Found {len(custom_agents)} custom agent files")
    print()
    
    # Match custom agents to actors
    print("="*70)
    print("🎯 Custom Agent to Actor ID Mapping")
    print("="*70)
    print()
    
    found_count = 0
    not_found_count = 0
    
    # Build actor lookup
    actor_lookup = {actor['login']: actor for actor in actors}
    
    for agent in custom_agents:
        agent_name = agent['name']
        agent_path = agent['path']
        
        if agent_name in actor_lookup:
            actor = actor_lookup[agent_name]
            print(f"✅ {agent_name}")
            print(f"   Path: {agent_path}")
            print(f"   Actor ID: {actor.get('id')}")
            print(f"   Type: {actor.get('__typename')}")
            if 'url' in actor:
                print(f"   URL: {actor['url']}")
            print()
            found_count += 1
        else:
            print(f"❌ {agent_name}")
            print(f"   Path: {agent_path}")
            print(f"   Actor ID: None (not found as actor)")
            print()
            not_found_count += 1
    
    # Summary
    print("="*70)
    print("📊 Summary")
    print("="*70)
    print()
    print(f"Total custom agents: {len(custom_agents)}")
    print(f"Agents with actor IDs: {found_count}")
    print(f"Agents without actor IDs: {not_found_count}")
    print()
    
    if found_count > 0:
        print("✅ SUCCESS: Custom agents have actor IDs!")
        print()
        print("   This means you can assign directly to custom agents via API.")
        print("   The workflow will automatically use direct assignment when available.")
        print()
        print("   Example GraphQL mutation:")
        print("   ```")
        print("   mutation {")
        print("     replaceActorsForAssignable(input: {")
        print("       assignableId: \"<ISSUE_ID>\",")
        print("       actorIds: [\"<CUSTOM_AGENT_ACTOR_ID>\"]")
        print("     }) { ... }")
        print("   }")
        print("   ```")
    else:
        print("ℹ️  INFO: Custom agents do not have separate actor IDs")
        print()
        print("   This means custom agents are configuration profiles, not actors.")
        print("   The workflow will assign to generic Copilot and use directives")
        print("   to communicate which agent profile should be used.")
    
    print()
    print("="*70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
