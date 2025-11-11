#!/usr/bin/env python3
"""
Helper script to extract information from convention-compliant agent definitions.
Reads agent markdown files from .github/agents/ and provides various utilities.
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path

AGENTS_DIR = Path(".github/agents")

def parse_agent_file(filepath):
    """Parse an agent markdown file and extract frontmatter and content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not frontmatter_match:
        return None
    
    frontmatter_str = frontmatter_match.group(1)
    body = frontmatter_match.group(2).strip()
    
    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError:
        return None
    
    # Extract emoji from body if present
    emoji_match = re.search(r'^#\s*([^\s]+)\s+', body)
    emoji = emoji_match.group(1) if emoji_match else ""
    
    # Extract mission statement (first paragraph or section after Core Responsibilities)
    mission_match = re.search(r'##\s+Core Responsibilities\s*\n\n1\.\s+\*\*([^:]+):\*\*\s+([^\n]+)', body)
    if mission_match:
        mission = mission_match.group(2)
    else:
        # Fallback: use description
        mission = frontmatter.get('description', '')
    
    return {
        'name': frontmatter.get('name', ''),
        'description': frontmatter.get('description', ''),
        'tools': frontmatter.get('tools', []),
        'emoji': emoji,
        'mission': mission,
        'body': body
    }

def list_agents():
    """List all agent names from .github/agents/."""
    agents = []
    if not AGENTS_DIR.exists():
        return agents
    
    for filepath in AGENTS_DIR.glob("*.md"):
        if filepath.name == "README.md":
            continue
        agent_info = parse_agent_file(filepath)
        if agent_info and agent_info['name']:
            agents.append(agent_info['name'])
    
    return sorted(agents)

def get_agent_info(agent_name):
    """Get full information about a specific agent."""
    filepath = AGENTS_DIR / f"{agent_name}.md"
    if not filepath.exists():
        return None
    
    return parse_agent_file(filepath)

def get_agent_emoji(agent_name):
    """Get the emoji for a specific agent."""
    info = get_agent_info(agent_name)
    return info['emoji'] if info else ""

def get_agent_mission(agent_name):
    """Get the mission statement for a specific agent."""
    info = get_agent_info(agent_name)
    return info['mission'] if info else ""

def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: get-agent-info.py <command> [args]", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  list                  - List all agent names", file=sys.stderr)
        print("  info <agent>          - Get full info as JSON", file=sys.stderr)
        print("  emoji <agent>         - Get agent emoji", file=sys.stderr)
        print("  mission <agent>       - Get agent mission", file=sys.stderr)
        print("  description <agent>   - Get agent description", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        agents = list_agents()
        print(" ".join(agents))
    
    elif command == "info":
        if len(sys.argv) < 3:
            print("Usage: get-agent-info.py info <agent-name>", file=sys.stderr)
            sys.exit(1)
        agent_name = sys.argv[2]
        info = get_agent_info(agent_name)
        if info:
            print(json.dumps(info, indent=2))
        else:
            print(f"Agent '{agent_name}' not found", file=sys.stderr)
            sys.exit(1)
    
    elif command == "emoji":
        if len(sys.argv) < 3:
            print("Usage: get-agent-info.py emoji <agent-name>", file=sys.stderr)
            sys.exit(1)
        agent_name = sys.argv[2]
        emoji = get_agent_emoji(agent_name)
        if emoji:
            print(emoji)
        else:
            print(f"Agent '{agent_name}' not found", file=sys.stderr)
            sys.exit(1)
    
    elif command == "mission":
        if len(sys.argv) < 3:
            print("Usage: get-agent-info.py mission <agent-name>", file=sys.stderr)
            sys.exit(1)
        agent_name = sys.argv[2]
        mission = get_agent_mission(agent_name)
        if mission:
            print(mission)
        else:
            print(f"Agent '{agent_name}' not found", file=sys.stderr)
            sys.exit(1)
    
    elif command == "description":
        if len(sys.argv) < 3:
            print("Usage: get-agent-info.py description <agent-name>", file=sys.stderr)
            sys.exit(1)
        agent_name = sys.argv[2]
        info = get_agent_info(agent_name)
        if info:
            print(info['description'])
        else:
            print(f"Agent '{agent_name}' not found", file=sys.stderr)
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
