#!/usr/bin/env python3
"""
List custom agent actor IDs from GitHub API.

This tool queries the GitHub GraphQL API to discover if custom agents
have their own actor IDs that can be used for direct assignment.

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


def run_gh_command(args, env=None):
    """Execute a gh CLI command."""
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
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e.stderr}", file=sys.stderr)
        return None


def get_suggested_actors(owner, repo):
    """Get all suggested actors for a repository."""
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
    
    output = run_gh_command([
        'api', 'graphql',
        '-f', f'query={query}',
        '-f', f'owner={owner}',
        '-f', f'repo={repo}'
    ])
    
    if output:
        try:
            result = json.loads(output)
            return result.get('data', {}).get('repository', {}).get('suggestedActors', {}).get('nodes', [])
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
    
    return []


def get_custom_agents():
    """Get list of custom agent files from .github/agents/."""
    agents_dir = Path('.github/agents')
    if not agents_dir.exists():
        return []
    
    agents = []
    for agent_file in agents_dir.glob('*.md'):
        if agent_file.name != 'README.md':
            agents.append({
                'name': agent_file.stem,
                'path': str(agent_file)
            })
    
    return sorted(agents, key=lambda x: x['name'])


def main():
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
    actors = get_suggested_actors(owner, repo)
    
    if not actors:
        print("❌ Failed to retrieve actors (check token permissions)")
        return 1
    
    print(f"✅ Found {len(actors)} total actors")
    print()
    
    # Get custom agents from files
    print("📁 Scanning .github/agents/ directory...")
    custom_agents = get_custom_agents()
    
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
