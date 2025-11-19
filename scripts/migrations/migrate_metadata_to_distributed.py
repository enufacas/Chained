#!/usr/bin/env python3
"""
Migrate Metadata to Distributed Format

This script migrates the metadata.json file to a distributed format where each
field is stored in a separate file, preventing merge conflicts from concurrent updates.

Usage:
    python3 migrate_metadata_to_distributed.py
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from registry_manager import RegistryManager


def main():
    """Migrate metadata from single file to distributed format"""
    print("=" * 60)
    print("🔄 METADATA MIGRATION TO DISTRIBUTED FORMAT")
    print("=" * 60)
    print()
    
    registry = RegistryManager()
    
    print(f"Current metadata mode: {registry._metadata_mode}")
    print()
    
    if registry._metadata_mode == "distributed":
        print("✅ Metadata is already in distributed format!")
        print()
        print("Current metadata:")
        metadata = registry.get_metadata()
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        return 0
    
    print("Starting migration...")
    print()
    
    success = registry.migrate_metadata_to_distributed()
    
    if success:
        print()
        print("=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Metadata has been distributed into individual files:")
        print(f"  {registry.metadata_dir}/")
        
        # List created files
        for field_file in sorted(registry.metadata_dir.glob("*.txt")):
            with open(field_file, 'r') as f:
                value = f.read().strip()
            print(f"    {field_file.name}: {value}")
        
        print()
        print("Benefits:")
        print("  ✓ No more merge conflicts from concurrent metadata updates")
        print("  ✓ Atomic updates per field")
        print("  ✓ Each workflow can update its own field independently")
        print()
        print("Next steps:")
        print("  1. Verify the migration worked correctly")
        print("  2. Test workflows that update metadata")
        print(f"  3. After verification, you can delete {registry.metadata_file}")
        print()
        return 0
    else:
        print()
        print("=" * 60)
        print("❌ MIGRATION FAILED")
        print("=" * 60)
        print()
        print("Please check the error messages above and try again.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
