#!/usr/bin/env python3
"""
Update Last Spawn Timestamp

Helper script to update the last_spawn timestamp in the registry metadata.
This should be called AFTER all agent spawning is complete to avoid
merge conflicts when multiple agents are spawned concurrently.

Usage:
    python3 tools/update_last_spawn.py
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from registry_manager import RegistryManager


def main():
    try:
        # Update metadata - last_spawn timestamp using atomic field update
        registry = RegistryManager()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if registry.update_metadata_field("last_spawn", timestamp):
            print(f"✓ Updated last_spawn timestamp to {timestamp}")
            sys.exit(0)
        else:
            print(f"✗ Failed to update last_spawn timestamp")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
