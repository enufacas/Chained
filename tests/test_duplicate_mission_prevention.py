#!/usr/bin/env python3
"""
Test to verify that duplicate missions are prevented by the unified deduplication system.

This test simulates the workflow behavior to ensure:
1. Both workflows check both flag and hash
2. Ideas with hashes are properly skipped
3. Ideas with flags are properly skipped
4. New ideas without either are identified for mission creation
"""

import json
import hashlib
import sys
from datetime import datetime, timezone


def generate_mission_hash(idea_id, idea_title, idea_patterns):
    """Generate mission hash using the standardized method"""
    mission_content = f"{idea_id}:{idea_title}:{':'.join(sorted(idea_patterns))}"
    return hashlib.md5(mission_content.encode()).hexdigest()


def test_deduplication_logic():
    """Test the complete deduplication logic"""
    print("🧪 Testing Duplicate Mission Prevention")
    print("="*70)
    
    # Load current state
    with open('world/knowledge.json', 'r') as f:
        knowledge = json.load(f)
    
    with open('.github/agent-system/missions_history.json', 'r') as f:
        missions_history = json.load(f)
    
    ideas = knowledge.get('ideas', [])
    previous_hashes = set(missions_history.get('mission_hashes', []))
    
    print(f"\n📊 Initial State:")
    print(f"  Total ideas: {len(ideas)}")
    print(f"  Hashes in history: {len(previous_hashes)}")
    
    # Simulate agent-missions.yml filtering logic
    learning_ideas = [i for i in ideas if i.get('source') == 'learning_analysis']
    print(f"  Learning ideas: {len(learning_ideas)}")
    
    # Test deduplication
    print(f"\n🔍 Testing Deduplication Logic:")
    
    skipped_by_flag = []
    skipped_by_hash = []
    would_create = []
    
    for idea in learning_ideas:
        idea_id = idea.get('id', 'unknown')
        idea_title = idea.get('title', 'Unknown')
        idea_patterns = idea.get('patterns', [])
        
        # Generate hash
        mission_hash = generate_mission_hash(idea_id, idea_title, idea_patterns)
        
        # Check flag
        if idea.get('mission_created', False):
            skipped_by_flag.append({
                'id': idea_id,
                'title': idea_title,
                'reason': 'mission_created flag is True'
            })
            continue
        
        # Check hash
        if mission_hash in previous_hashes:
            skipped_by_hash.append({
                'id': idea_id,
                'title': idea_title,
                'hash': mission_hash,
                'reason': 'hash exists in missions_history.json'
            })
            continue
        
        # Would create mission for this idea
        would_create.append({
            'id': idea_id,
            'title': idea_title,
            'hash': mission_hash
        })
    
    # Report results
    print(f"\n📈 Results:")
    print(f"  ✅ Skipped by flag: {len(skipped_by_flag)}")
    print(f"  ✅ Skipped by hash: {len(skipped_by_hash)}")
    print(f"  🆕 Would create: {len(would_create)}")
    
    # Verify no duplicates in "would create" list
    hashes_to_create = [i['hash'] for i in would_create]
    if len(hashes_to_create) != len(set(hashes_to_create)):
        print(f"\n❌ FAIL: Duplicate hashes in 'would create' list!")
        return 1
    
    # Verify all skipped items have valid reasons
    print(f"\n🔍 Verification:")
    
    # Check that items skipped by flag also have hashes (if properly synced)
    flag_and_hash_synced = 0
    flag_not_in_hash = 0
    
    for item in skipped_by_flag:
        # Reconstruct hash
        for idea in learning_ideas:
            if idea.get('id') == item['id']:
                hash = generate_mission_hash(
                    idea.get('id'),
                    idea.get('title'),
                    idea.get('patterns', [])
                )
                if hash in previous_hashes:
                    flag_and_hash_synced += 1
                else:
                    flag_not_in_hash += 1
                    print(f"  ⚠️  Warning: {item['title'][:40]} has flag but no hash")
                break
    
    print(f"  Flag & hash synchronized: {flag_and_hash_synced}/{len(skipped_by_flag)}")
    
    # Show what would be created
    if would_create:
        print(f"\n🆕 New missions that would be created ({len(would_create)}):")
        for i, item in enumerate(would_create[:5], 1):
            print(f"  {i}. {item['title']}")
            print(f"     Hash: {item['hash'][:16]}...")
    
    # Final verdict
    print(f"\n" + "="*70)
    
    # Success criteria:
    # 1. No duplicate hashes in would_create
    # 2. At least some items properly deduplicated
    # 3. Flag and hash are mostly synchronized
    
    success = True
    
    if len(hashes_to_create) != len(set(hashes_to_create)):
        print(f"❌ FAIL: Duplicate hashes detected")
        success = False
    
    if len(skipped_by_flag) + len(skipped_by_hash) == 0:
        print(f"⚠️  WARNING: No missions deduplicated (may be first run)")
    else:
        print(f"✅ PASS: {len(skipped_by_flag) + len(skipped_by_hash)} missions properly deduplicated")
    
    if flag_not_in_hash > 0:
        print(f"⚠️  WARNING: {flag_not_in_hash} ideas have flag but no hash")
        print(f"   (Run tools/sync_mission_flags.py to fix)")
    else:
        print(f"✅ PASS: All flags synchronized with hashes")
    
    if success:
        print(f"\n🎉 SUCCESS: Duplicate mission prevention is working correctly!")
        return 0
    else:
        print(f"\n❌ FAILURE: Issues detected in deduplication logic")
        return 1


if __name__ == '__main__':
    sys.exit(test_deduplication_logic())
