#!/usr/bin/env python3
"""
Inspect issue assignment history to understand custom agent assignments.

This tool queries the GitHub API to examine how custom agents are assigned
when done through the UI, helping us understand the assignment patterns.

Usage:
    export GH_TOKEN="your_github_token"
    python3 inspect-issue-assignment.py <owner> <repo> <issue_number>
    
Example:
    python3 inspect-issue-assignment.py enufacas Chained 42
"""

import os
import sys
import json
import subprocess
from datetime import datetime


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


def get_issue_details(owner, repo, issue_number):
    """Get detailed issue information including assignees."""
    query = '''
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          id
          number
          title
          body
          createdAt
          updatedAt
          assignees(first: 10) {
            nodes {
              login
              __typename
              id
              url
            }
          }
          timelineItems(first: 100, itemTypes: [ASSIGNED_EVENT, UNASSIGNED_EVENT]) {
            nodes {
              __typename
              ... on AssignedEvent {
                id
                createdAt
                assignee {
                  __typename
                  ... on Bot {
                    login
                    id
                    url
                  }
                  ... on User {
                    login
                    id
                    url
                  }
                }
                actor {
                  login
                }
              }
              ... on UnassignedEvent {
                id
                createdAt
                assignee {
                  __typename
                  ... on Bot {
                    login
                    id
                  }
                  ... on User {
                    login
                    id
                  }
                }
                actor {
                  login
                }
              }
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
        '-f', f'repo={repo}',
        '-F', f'number={issue_number}'
    ])
    
    if output:
        try:
            result = json.loads(output)
            return result.get('data', {}).get('repository', {}).get('issue')
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
    
    return None


def format_timestamp(timestamp):
    """Format ISO timestamp to readable format."""
    if not timestamp:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except Exception:
        return timestamp


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 inspect-issue-assignment.py <owner> <repo> <issue_number>")
        print("Example: python3 inspect-issue-assignment.py enufacas Chained 42")
        sys.exit(1)
    
    owner = sys.argv[1]
    repo = sys.argv[2]
    issue_number = int(sys.argv[3])
    
    if not os.environ.get('GH_TOKEN') and not os.environ.get('GITHUB_TOKEN'):
        print("⚠️  WARNING: No GH_TOKEN or GITHUB_TOKEN environment variable set")
        print("Set a token to query the GitHub API:")
        print("  export GH_TOKEN='your_token_here'")
        print()
    
    print("="*80)
    print("🔍 Issue Assignment History Inspector")
    print("="*80)
    print(f"Repository: {owner}/{repo}")
    print(f"Issue: #{issue_number}")
    print()
    
    # Get issue details
    print("📡 Querying GitHub API...")
    issue = get_issue_details(owner, repo, issue_number)
    
    if not issue:
        print("❌ Failed to retrieve issue details")
        return 1
    
    print("✅ Issue data retrieved")
    print()
    
    # Display issue info
    print("="*80)
    print("📋 Issue Information")
    print("="*80)
    print(f"Title: {issue['title']}")
    print(f"Issue ID: {issue['id']}")
    print(f"Created: {format_timestamp(issue['createdAt'])}")
    print(f"Updated: {format_timestamp(issue['updatedAt'])}")
    print()
    
    # Display current assignees
    print("="*80)
    print("👥 Current Assignees")
    print("="*80)
    
    assignees = issue.get('assignees', {}).get('nodes', [])
    if not assignees:
        print("❌ No assignees")
    else:
        for assignee in assignees:
            print(f"\n✅ {assignee['login']}")
            print(f"   Type: {assignee['__typename']}")
            print(f"   Actor ID: {assignee['id']}")
            print(f"   URL: {assignee.get('url', 'N/A')}")
            
            # Check if this looks like a custom agent
            if 'copilot' not in assignee['login'].lower() and assignee['__typename'] == 'Bot':
                print(f"   🎯 POSSIBLE CUSTOM AGENT DETECTED!")
                print(f"   Login '{assignee['login']}' might be a custom agent name")
            elif '-' in assignee['login'] and assignee['__typename'] == 'Bot':
                print(f"   🎯 CUSTOM AGENT FORMAT DETECTED!")
                print(f"   Login pattern matches custom agent naming (contains hyphen)")
    
    print()
    
    # Display assignment history
    print("="*80)
    print("📜 Assignment History (Timeline)")
    print("="*80)
    
    timeline = issue.get('timelineItems', {}).get('nodes', [])
    if not timeline:
        print("ℹ️  No assignment events found")
    else:
        print(f"Found {len(timeline)} assignment event(s)\n")
        
        for idx, event in enumerate(timeline, 1):
            event_type = event['__typename']
            timestamp = format_timestamp(event.get('createdAt'))
            assignee = event.get('assignee', {})
            actor = event.get('actor', {})
            
            if event_type == 'AssignedEvent':
                print(f"#{idx} ✅ ASSIGNED")
            else:
                print(f"#{idx} ❌ UNASSIGNED")
            
            print(f"   When: {timestamp}")
            print(f"   By: {actor.get('login', 'Unknown')}")
            
            if assignee:
                print(f"   Assignee: {assignee.get('login', 'Unknown')}")
                print(f"   Assignee Type: {assignee.get('__typename', 'Unknown')}")
                print(f"   Assignee ID: {assignee.get('id', 'N/A')}")
                
                # Detect custom agent patterns
                assignee_login = assignee.get('login', '')
                if assignee_login and assignee_login not in ['github-copilot', 'copilot']:
                    print(f"   🎯 CUSTOM AGENT INDICATOR!")
                    print(f"      This might be a custom agent: '{assignee_login}'")
                    print(f"      Check if .github/agents/{assignee_login}.md exists")
            
            print()
    
    # Analysis and recommendations
    print("="*80)
    print("📊 Analysis & Recommendations")
    print("="*80)
    print()
    
    # Check for custom agent patterns
    custom_agent_logins = []
    for assignee in assignees:
        login = assignee.get('login', '')
        if login and login not in ['github-copilot', 'copilot'] and assignee['__typename'] == 'Bot':
            custom_agent_logins.append({
                'login': login,
                'id': assignee['id'],
                'url': assignee.get('url', '')
            })
    
    if custom_agent_logins:
        print("🎉 CUSTOM AGENT ASSIGNMENT DETECTED!")
        print()
        print("Custom agent(s) found as assignees:")
        for agent in custom_agent_logins:
            print(f"\n  Agent: {agent['login']}")
            print(f"  Actor ID: {agent['id']}")
            print(f"  URL: {agent['url']}")
        
        print()
        print("💡 KEY INSIGHTS:")
        print()
        print("1. Custom agents HAVE separate actor IDs in the GitHub API")
        print("2. When assigned via UI, they appear as Bot type assignees")
        print("3. Their login matches the agent name (e.g., 'bug-hunter')")
        print("4. We CAN use these actor IDs for programmatic assignment!")
        print()
        print("📋 To use this for API assignment:")
        print()
        print("   ```graphql")
        print("   mutation {")
        print("     replaceActorsForAssignable(input: {")
        print("       assignableId: \"<ISSUE_ID>\",")
        for agent in custom_agent_logins:
            print(f"       actorIds: [\"{agent['id']}\"]  # {agent['login']}")
        print("     }) { ... }")
        print("   }")
        print("   ```")
        print()
        print("✅ The workflow can now use this information to assign directly!")
    else:
        print("ℹ️  No custom agent assignments detected")
        print()
        print("   If you assigned a custom agent via the UI, it should appear here.")
        print("   The assignee's login would match the agent name (e.g., 'bug-hunter').")
        print()
        print("   Possible reasons:")
        print("   - Custom agents don't have separate actor IDs in this repository")
        print("   - The agent was assigned but appears as 'github-copilot'")
        print("   - Custom agent feature may not be fully enabled")
    
    print()
    print("="*80)
    print("🔧 Next Steps")
    print("="*80)
    print()
    
    if custom_agent_logins:
        print("1. ✅ Update the workflow to use custom agent actor IDs")
        print("2. ✅ Store agent name → actor ID mappings")
        print("3. ✅ Use direct assignment when custom agent actor IDs are available")
        print("4. ✅ Test with new issues to verify it works programmatically")
    else:
        print("1. Verify custom agents are properly configured in .github/agents/")
        print("2. Try assigning different custom agents via UI")
        print("3. Run this tool again to see if patterns emerge")
        print("4. Check GitHub Copilot settings for the repository")
    
    print()
    print("="*80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
