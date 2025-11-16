#!/usr/bin/env python3
"""
Sync mission_created flags with missions_history.json hashes

This script ensures that ideas with hashes in missions_history.json
also have their mission_created flag set to True, preventing
duplicate mission creation attempts.
"""

import json
import hashlib
from datetime import datetime, timezone


def main():
    print("🔄 Synchronizing mission_created flags with missions_history.json")
    print("="*70)
    
    # Load knowledge
    with open('world/knowledge.json', 'r') as f:
        knowledge = json.load(f)
    
    # Load missions history
    try:
        with open('.github/agent-system/missions_history.json', 'r') as f:
            missions_history = json.load(f)
            previous_hashes = set(missions_history.get('mission_hashes', []))
    except FileNotFoundError:
        print("⚠️  missions_history.json not found")
        previous_hashes = set()
    
    ideas = knowledge.get('ideas', [])
    print(f"\nTotal ideas: {len(ideas)}")
    print(f"Hashes in history: {len(previous_hashes)}")
    
    # Find and fix inconsistencies
    fixed_count = 0
    already_synced = 0
    
    for idea in ideas:
        if idea.get('source') != 'learning_analysis':
            continue
        
        # Generate hash
        idea_id = idea.get('id', 'unknown')
        idea_title = idea.get('title', 'Unknown')
        idea_patterns = idea.get('patterns', [])
        mission_content = f"{idea_id}:{idea_title}:{':'.join(sorted(idea_patterns))}"
        mission_hash = hashlib.md5(mission_content.encode()).hexdigest()
        
        # Check if hash exists in history
        if mission_hash in previous_hashes:
            # Hash exists - flag should be True
            if not idea.get('mission_created', False):
                print(f"  🔧 Fixing: {idea_title[:50]}")
                print(f"     ID: {idea_id}")
                print(f"     Hash exists but flag=False → setting flag=True")
                idea['mission_created'] = True
                idea['mission_created_at'] = datetime.now(timezone.utc).isoformat()
                fixed_count += 1
            else:
                already_synced += 1
        else:
            # Hash doesn't exist - flag should be False
            if idea.get('mission_created', False):
                print(f"  ⚠️  Warning: {idea_title[:50]}")
                print(f"     ID: {idea_id}")
                print(f"     Flag=True but hash not in history")
                print(f"     This may indicate a missing hash - keeping flag as is")
    
    print(f"\n📊 Summary:")
    print(f"  Fixed inconsistencies: {fixed_count}")
    print(f"  Already synchronized: {already_synced}")
    
    if fixed_count > 0:
        # Save updated knowledge
        with open('world/knowledge.json', 'w') as f:
            json.dump(knowledge, f, indent=2)
        print(f"\n✅ Saved updated knowledge.json with {fixed_count} fixes")
    else:
        print(f"\n✅ All flags already synchronized, no changes needed")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
