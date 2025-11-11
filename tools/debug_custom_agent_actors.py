#!/usr/bin/env python3
"""
Debug tool for GitHub Custom Agent Actor IDs.

This elegant diagnostic script explores the GitHub GraphQL API to discover
how custom agents are represented in the actor system. It reveals the
relationship between agent definition files and assignable actors.

Features:
    • Query all assignable actors for a repository
    • Discover custom agent actor IDs
    • Match agent files to GitHub actors
    • Provide actionable insights for automation

Usage:
    export GH_TOKEN="your_github_token"
    python3 debug_custom_agent_actors.py <owner> <repo>
    
Example:
    python3 debug_custom_agent_actors.py enufacas Chained
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

def execute_graphql_query(query: str, variables: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Execute a GraphQL query using GitHub CLI.
    
    This function orchestrates the communication with GitHub's GraphQL API,
    handling the complexities of subprocess execution and JSON parsing with
    grace and proper error handling.
    
    Args:
        query: GraphQL query string
        variables: Dictionary of query variables
        
    Returns:
        Parsed JSON response, or None if the query fails
    """
    command = ['gh', 'api', 'graphql', '-f', f'query={query}']
    
    for key, value in variables.items():
        command.extend(['-f', f'{key}={value}'])
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as error:
        print(f"❌ GraphQL query failed: {error.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError as error:
        print(f"❌ JSON parsing failed: {error}", file=sys.stderr)
        return None

def fetch_assignable_actors(owner: str, repo: str) -> List[Dict[str, Any]]:
    """
    Retrieve all actors that can be assigned to issues.
    
    This function queries GitHub's GraphQL API to discover which actors
    (users and bots) have the ability to be assigned to issues in the
    specified repository.
    
    Args:
        owner: Repository owner username
        repo: Repository name
        
    Returns:
        List of actor dictionaries with login, type, and ID information
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
    
    result = execute_graphql_query(query, {'owner': owner, 'repo': repo})
    if result and 'data' in result:
        return result['data']['repository']['suggestedActors']['nodes']
    return []

def discover_custom_agents() -> List[str]:
    """
    Discover custom agent definitions in the repository.
    
    Scans the .github/agents/ directory for agent definition files,
    each representing a specialized AI persona configured for specific
    types of tasks.
    
    Returns:
        Sorted list of agent names (without .md extension)
    """
    agents_directory = Path('.github/agents')
    if not agents_directory.exists():
        return []
    
    agent_names = [
        agent_file.stem 
        for agent_file in agents_directory.glob('*.md')
        if agent_file.name != 'README.md'
    ]
    
    return sorted(agent_names)

def display_header(owner: str, repo: str) -> None:
    """Display the tool's header banner."""
    print("="*60)
    print("🔍 GitHub Custom Agent Actor ID Debug Tool")
    print("="*60)
    print(f"Repository: {owner}/{repo}")
    print()


def check_authentication() -> None:
    """Verify GitHub authentication is configured."""
    if not os.environ.get('GH_TOKEN') and not os.environ.get('GITHUB_TOKEN'):
        print("⚠️  WARNING: No GH_TOKEN or GITHUB_TOKEN environment variable set")
        print("Set a token to query the GitHub API:")
        print("  export GH_TOKEN='your_token_here'")
        print()


def main() -> int:
    """
    Main entry point for the debug tool.
    
    Orchestrates the discovery process, displaying findings about custom
    agent actors in an organized and informative manner.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if len(sys.argv) != 3:
        print("Usage: python3 debug_custom_agent_actors.py <owner> <repo>")
        print("Example: python3 debug_custom_agent_actors.py enufacas Chained")
        sys.exit(1)
    
    owner = sys.argv[1]
    repo = sys.argv[2]
    
    check_authentication()
    display_header(owner, repo)
    
    # Step 1: Get all suggested actors
    print("━"*60)
    print("📋 Step 1: Querying Suggested Actors")
    print("━"*60)
    actors = fetch_assignable_actors(owner, repo)
    
    if not actors:
        print("❌ Failed to retrieve actors (check token permissions)")
        return 1
    
    print(f"Found {len(actors)} actors that can be assigned:")
    print()
    for actor in actors:
        print(f"  {actor['login']:30s} ({actor['__typename']:8s}) ID: {actor.get('id', 'N/A')}")
    print()
    
    # Step 2: Filter for Copilot-related actors
    print("━"*60)
    print("🤖 Step 2: Copilot-Related Actors")
    print("━"*60)
    copilot_actors = [a for a in actors if 'copilot' in a['login'].lower()]
    
    if copilot_actors:
        print(f"Found {len(copilot_actors)} Copilot-related actor(s):")
        print()
        for actor in copilot_actors:
            print(f"  ✅ {actor['login']}")
            print(f"     Type: {actor['__typename']}")
            print(f"     ID: {actor.get('id')}")
            if 'url' in actor:
                print(f"     URL: {actor['url']}")
            print()
    else:
        print("❌ No Copilot actors found")
        print("   This might mean Copilot is not enabled for this repository")
        print()
    
    # Step 3: Get custom agents from files
    print("━"*60)
    print("📁 Step 3: Custom Agent Files")
    print("━"*60)
    custom_agents = discover_custom_agents()
    
    if custom_agents:
        print(f"Found {len(custom_agents)} custom agent file(s):")
        print()
        for agent in custom_agents:
            print(f"  ✓ {agent}")
        print()
    else:
        print("❌ No custom agent files found in .github/agents/")
        print()
    
    # Step 4: Check if custom agents have actor IDs
    print("━"*60)
    print("🔎 Step 4: Matching Custom Agents to Actors")
    print("━"*60)
    
    if not custom_agents:
        print("No custom agents to match")
        print()
    else:
        found_count = 0
        not_found_count = 0
        
        for agent_name in custom_agents:
            matching_actor = next((a for a in actors if a['login'] == agent_name), None)
            
            if matching_actor:
                print(f"  ✅ {agent_name:30s} → Actor ID: {matching_actor.get('id')}")
                found_count += 1
            else:
                print(f"  ❌ {agent_name:30s} → Not found as actor")
                not_found_count += 1
        
        print()
        print(f"Summary: {found_count} found, {not_found_count} not found")
        print()
    
    # Step 5: Search for patterns
    print("━"*60)
    print("🔬 Step 5: Pattern Analysis")
    print("━"*60)
    
    agent_actors = [a for a in actors if 'agent' in a['login'].lower()]
    if agent_actors:
        print(f"Actors with 'agent' in name: {len(agent_actors)}")
        for actor in agent_actors:
            print(f"  - {actor['login']} ({actor['__typename']})")
        print()
    else:
        print("No actors with 'agent' in their name")
        print()
    
    # Step 6: Analysis and conclusion
    print("━"*60)
    print("📊 Step 6: Analysis & Conclusions")
    print("━"*60)
    print()
    
    if custom_agents:
        matched_agents = [a for a in custom_agents if any(actor['login'] == a for actor in actors)]
        match_rate = len(matched_agents) / len(custom_agents) * 100 if custom_agents else 0
        
        print(f"Match Rate: {len(matched_agents)}/{len(custom_agents)} ({match_rate:.1f}%)")
        print()
        
        if len(matched_agents) > 0:
            print("✅ BREAKTHROUGH: Some custom agents have actor IDs!")
            print()
            print("   This means we CAN assign to specific agents via API!")
            print()
            print("   Matched agents:")
            for agent in matched_agents:
                actor = next((a for a in actors if a['login'] == agent), None)
                print(f"     - {agent}: {actor['id']}")
            print()
            print("   Next steps:")
            print("   1. Update workflow to use custom agent actor IDs")
            print("   2. Assign directly to matched agent's actor ID")
            print("   3. Remove workaround directives (no longer needed)")
        else:
            print("❌ CONFIRMED: Custom agents do NOT have separate actor IDs")
            print()
            print("   This means:")
            print("   - Custom agents are configuration files, not actors")
            print("   - We can only assign to the generic Copilot bot")
            print("   - Agent selection must happen through other mechanisms")
            print()
            print("   Current approach (directives in issue) is the best option.")
    else:
        print("⚠️  No custom agents found to analyze")
        print()
    
    print("="*60)
    print("Debug complete!")
    print("="*60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
