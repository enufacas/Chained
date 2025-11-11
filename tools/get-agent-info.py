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

# Import validation utilities
try:
    from validation_utils import (
        ValidationError,
        validate_agent_name,
        validate_file_path,
        safe_file_read
    )
except ImportError:
    # Fallback if validation_utils is not available
    class ValidationError(Exception):
        pass
    def validate_agent_name(name):
        return name
    def validate_file_path(path, base=None):
        return Path(path)
    def safe_file_read(path, encoding='utf-8'):
        with open(path, 'r', encoding=encoding) as f:
            return f.read()

AGENTS_DIR = Path(".github/agents")

def parse_agent_file(filepath):
    """
    Parse an agent markdown file and extract frontmatter and content.
    
    Args:
        filepath: Path to the agent markdown file
        
    Returns:
        Dict with agent information, or None if parsing fails
    """
    try:
        # Validate filepath to prevent path traversal
        filepath = validate_file_path(filepath, AGENTS_DIR.resolve())
        
        # Read file safely
        content = safe_file_read(filepath)
        
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
        
        # Validate that frontmatter is a dict
        if not isinstance(frontmatter, dict):
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
    except (ValidationError, IOError, OSError, UnicodeDecodeError) as e:
        # Handle file reading errors gracefully
        return None
    except Exception as e:
        # Catch any other unexpected errors
        return None

def list_agents():
    """
    List all agent names from .github/agents/.
    
    Returns:
        Sorted list of agent names
    """
    agents = []
    if not AGENTS_DIR.exists():
        return agents
    
    try:
        for filepath in AGENTS_DIR.glob("*.md"):
            if filepath.name == "README.md":
                continue
            agent_info = parse_agent_file(filepath)
            if agent_info and agent_info['name']:
                agents.append(agent_info['name'])
    except Exception:
        # Handle any errors gracefully
        pass
    
    return sorted(agents)

def get_agent_info(agent_name):
    """
    Get full information about a specific agent.
    
    Args:
        agent_name: Name of the agent (validated for security)
        
    Returns:
        Dict with agent information, or None if not found
    """
    try:
        # Validate agent_name to prevent path traversal
        agent_name = validate_agent_name(agent_name)
        
        filepath = AGENTS_DIR / f"{agent_name}.md"
        if not filepath.exists():
            return None
        
        return parse_agent_file(filepath)
    except ValidationError:
        # Invalid agent name
        return None

def get_agent_emoji(agent_name):
    """
    Get the emoji for a specific agent.
    
    Args:
        agent_name: Name of the agent (validated for security)
        
    Returns:
        Agent emoji string, or empty string if not found
    """
    info = get_agent_info(agent_name)
    return info['emoji'] if info else ""

def get_agent_mission(agent_name):
    """
    Get the mission statement for a specific agent.
    
    Args:
        agent_name: Name of the agent (validated for security)
        
    Returns:
        Agent mission string, or empty string if not found
    """
    info = get_agent_info(agent_name)
    return info['mission'] if info else ""

def main():
    """Command-line interface with elegant command dispatch."""
    commands = {
        'list': handle_list_command,
        'info': handle_info_command,
        'emoji': handle_emoji_command,
        'mission': handle_mission_command,
        'description': handle_description_command,
    }
    
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command not in commands:
        print(f"Unknown command: {command}", file=sys.stderr)
        print_usage()
        sys.exit(1)
    
    commands[command]()


def print_usage():
    """Display usage information."""
    print("Usage: get-agent-info.py <command> [args]", file=sys.stderr)
    print("\nCommands:", file=sys.stderr)
    print("  list                  - List all agent names", file=sys.stderr)
    print("  info <agent>          - Get full info as JSON", file=sys.stderr)
    print("  emoji <agent>         - Get agent emoji", file=sys.stderr)
    print("  mission <agent>       - Get agent mission", file=sys.stderr)
    print("  description <agent>   - Get agent description", file=sys.stderr)


def require_agent_argument() -> str:
    """
    Ensure an agent name was provided as an argument.
    
    Returns:
        The agent name from command line arguments
        
    Exits:
        If no agent name is provided
    """
    if len(sys.argv) < 3:
        print(f"Usage: get-agent-info.py {sys.argv[1]} <agent-name>", file=sys.stderr)
        sys.exit(1)
    return sys.argv[2]


def handle_list_command():
    """List all available agents."""
    agents = list_agents()
    print(" ".join(agents))


def handle_info_command():
    """Display full agent information as JSON."""
    agent_name = require_agent_argument()
    info = get_agent_info(agent_name)
    
    if info:
        print(json.dumps(info, indent=2))
    else:
        print(f"Agent '{agent_name}' not found", file=sys.stderr)
        sys.exit(1)


def handle_emoji_command():
    """Display agent emoji."""
    agent_name = require_agent_argument()
    emoji = get_agent_emoji(agent_name)
    
    if emoji:
        print(emoji)
    else:
        print(f"Agent '{agent_name}' not found", file=sys.stderr)
        sys.exit(1)


def handle_mission_command():
    """Display agent mission statement."""
    agent_name = require_agent_argument()
    mission = get_agent_mission(agent_name)
    
    if mission:
        print(mission)
    else:
        print(f"Agent '{agent_name}' not found", file=sys.stderr)
        sys.exit(1)


def handle_description_command():
    """Display agent description."""
    agent_name = require_agent_argument()
    info = get_agent_info(agent_name)
    
    if info:
        print(info['description'])
    else:
        print(f"Agent '{agent_name}' not found", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
