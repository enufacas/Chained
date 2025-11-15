#!/usr/bin/env python3
"""
Get Available Human Names for Agent Spawning

This script checks the registry for active agents and returns
a list of human names that are not currently in use.

Usage:
    python3 tools/get-available-human-names.py [--format text|json]
    
Output:
    - text: One name per line (default)
    - json: JSON array of names
    - count: Number of available names

Created by @assert-specialist for agent spawner workflow
"""

import json
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from registry_manager import RegistryManager


# Full list of possible human names (from spawner workflows)
ALL_HUMAN_NAMES = [
    "Ada", "Tesla", "Einstein", "Curie", "Turing", "Lovelace",
    "Darwin", "Newton", "Feynman", "Hopper", "Hamilton", "Liskov",
    "Dijkstra", "Knuth", "Shannon"
]


def get_available_human_names():
    """
    Get list of human names not currently used by active agents.
    
    Returns:
        list: Human names that are available for new agents
    """
    registry = RegistryManager()
    agents = registry.list_agents(status='active')
    
    # Get all currently used names
    used_names = {agent.get('human_name', 'Unknown') for agent in agents}
    
    # Filter out used names
    available = [name for name in ALL_HUMAN_NAMES if name not in used_names]
    
    return available


def get_fallback_name(base_name, used_names):
    """
    Generate a fallback name when base name is taken.
    
    Args:
        base_name: Original name that's already used
        used_names: Set of all currently used names
        
    Returns:
        str: Unique name with suffix (e.g., "Ada-2")
    """
    counter = 2
    while True:
        fallback = f"{base_name}-{counter}"
        if fallback not in used_names:
            return fallback
        counter += 1
        if counter > 100:  # Safety limit
            # Use timestamp as ultimate fallback
            import time
            return f"{base_name}-{int(time.time())}"


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Get available human names for agent spawning"
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'count', 'random'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--with-fallback',
        action='store_true',
        help='If no names available, return a fallback name'
    )
    
    args = parser.parse_args()
    
    try:
        available = get_available_human_names()
        
        # Handle the case where all names are used
        if not available:
            if args.with_fallback:
                # Get used names for fallback generation
                registry = RegistryManager()
                agents = registry.list_agents(status='active')
                used_names = {agent.get('human_name', 'Unknown') for agent in agents}
                
                # Pick a base name and add suffix
                import random
                base_name = random.choice(ALL_HUMAN_NAMES)
                fallback = get_fallback_name(base_name, used_names)
                
                if args.format == 'json':
                    print(json.dumps([fallback]))
                elif args.format == 'count':
                    print(1)
                elif args.format == 'random':
                    print(fallback)
                else:
                    print(fallback)
                return 0
            else:
                # No names available and no fallback requested
                if args.format == 'count':
                    print(0)
                elif args.format == 'json':
                    print(json.dumps([]))
                else:
                    print("# No names available", file=sys.stderr)
                return 1
        
        # Output available names in requested format
        if args.format == 'text':
            for name in available:
                print(name)
        elif args.format == 'json':
            print(json.dumps(available))
        elif args.format == 'count':
            print(len(available))
        elif args.format == 'random':
            import random
            print(random.choice(available))
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
