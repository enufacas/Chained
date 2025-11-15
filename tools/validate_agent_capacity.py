#!/usr/bin/env python3
"""
Agent Capacity Validator
Ensures no more than 10 agents are assigned to any mission
"""

import sys
import json
from typing import List, Dict, Any, Tuple

MAX_AGENTS = 10

def validate_agent_list(agents: List[str], context: str = "") -> Tuple[bool, str]:
    """
    Validate that an agent list doesn't exceed capacity
    
    Args:
        agents: List of agent IDs/names
        context: Context description for error messages
    
    Returns:
        Tuple of (is_valid, message)
    """
    count = len(agents)
    
    if count > MAX_AGENTS:
        msg = f"❌ CAPACITY VIOLATION: {count} agents exceeds limit of {MAX_AGENTS}"
        if context:
            msg += f" (Context: {context})"
        return False, msg
    elif count == MAX_AGENTS:
        msg = f"⚠️  AT CAPACITY: {count}/{MAX_AGENTS} agents assigned"
        if context:
            msg += f" ({context})"
        return True, msg
    else:
        msg = f"✅ WITHIN CAPACITY: {count}/{MAX_AGENTS} agents assigned"
        if context:
            msg += f" ({context})"
        return True, msg

def select_top_agents(
    agents: List[Dict[str, Any]], 
    max_count: int = MAX_AGENTS,
    score_key: str = 'score'
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Select top agents up to capacity limit
    
    Args:
        agents: List of agent dictionaries with scores
        max_count: Maximum agents to select
        score_key: Key to use for scoring
    
    Returns:
        Tuple of (selected_agents, overflow_agents)
    """
    # Sort by score (highest first)
    sorted_agents = sorted(
        agents,
        key=lambda a: a.get(score_key, 0),
        reverse=True
    )
    
    # Split at capacity limit
    selected = sorted_agents[:max_count]
    overflow = sorted_agents[max_count:]
    
    return selected, overflow

def create_overflow_summary(overflow_agents: List[Dict[str, Any]]) -> str:
    """
    Create a summary of overflow agents for backlog issue
    
    Args:
        overflow_agents: List of agents that exceeded capacity
    
    Returns:
        Markdown formatted summary
    """
    if not overflow_agents:
        return ""
    
    summary = f"## 📋 Overflow Agents ({len(overflow_agents)} agents)\n\n"
    summary += "These agents were considered but not selected due to 10-agent capacity limit:\n\n"
    
    for agent in overflow_agents:
        agent_id = agent.get('id', agent.get('name', 'unknown'))
        score = agent.get('score', 0)
        reason = agent.get('reason', 'No reason provided')
        summary += f"- **@{agent_id}** (score: {score:.2f})\n"
        summary += f"  - {reason}\n"
    
    summary += "\n"
    summary += "### Next Steps\n\n"
    summary += "- Monitor capacity of current assignment\n"
    summary += "- Consider these agents for future related tasks\n"
    summary += "- Review if task scope should be split\n"
    
    return summary

def validate_assignment_file(filepath: str) -> bool:
    """
    Validate an assignment JSON file for capacity compliance
    
    Args:
        filepath: Path to assignment JSON file
    
    Returns:
        True if valid, False otherwise
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Check different possible structures
        agents = []
        if isinstance(data, list):
            agents = data
        elif isinstance(data, dict):
            agents = data.get('agents', data.get('assigned_agents', []))
        
        is_valid, message = validate_agent_list(agents, f"File: {filepath}")
        print(message)
        
        return is_valid
    
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in file: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error validating file: {e}")
        return False

def main():
    """Main validation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate agent capacity limits (max 10 agents)'
    )
    parser.add_argument(
        'agents',
        nargs='*',
        help='Agent IDs to validate (space-separated)'
    )
    parser.add_argument(
        '--file',
        help='JSON file containing agent assignment'
    )
    parser.add_argument(
        '--context',
        default='',
        help='Context description for error messages'
    )
    
    args = parser.parse_args()
    
    print("🤖 Agent Capacity Validator")
    print("=" * 60)
    print(f"Maximum allowed agents: {MAX_AGENTS}")
    print("=" * 60)
    
    # Validate from file
    if args.file:
        is_valid = validate_assignment_file(args.file)
        sys.exit(0 if is_valid else 1)
    
    # Validate from command line
    if args.agents:
        is_valid, message = validate_agent_list(args.agents, args.context)
        print(message)
        
        if len(args.agents) > MAX_AGENTS:
            print()
            print("💡 Suggestion: Create backlog issue for overflow agents")
            overflow = args.agents[MAX_AGENTS:]
            print(f"   Overflow agents: {', '.join(overflow)}")
        
        sys.exit(0 if is_valid else 1)
    
    # No input provided
    print("❌ No agents or file provided")
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    main()
