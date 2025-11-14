#!/usr/bin/env python3
"""
List Agents from Registry

Helper script for workflows to query agents from the distributed registry.

Usage:
    python3 tools/list_agents_from_registry.py [--status STATUS] [--format json|count]
"""

import json
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from registry_manager import RegistryManager


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="List agents from registry")
    parser.add_argument("--status", help="Filter by status (e.g., 'active')")
    parser.add_argument("--format", choices=["json", "count"], default="json",
                       help="Output format")
    
    args = parser.parse_args()
    
    try:
        registry = RegistryManager()
        agents = registry.list_agents(status=args.status)
        
        if args.format == "count":
            print(len(agents))
        else:
            print(json.dumps(agents, indent=2))
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
