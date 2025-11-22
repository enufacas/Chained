#!/usr/bin/env python3
"""
Deduplicate Idea IDs in knowledge.json

**@APIs-architect** Fix: Remove duplicate idea IDs by keeping the first
occurrence and reassigning IDs to duplicates.
"""

import json
import sys
from collections import defaultdict


def main():
    print("🔧 Deduplicating idea IDs in knowledge.json")
    print("=" * 70)
    
    # Load knowledge
    with open('world/knowledge.json', 'r') as f:
        knowledge = json.load(f)
    
    ideas = knowledge.get('ideas', [])
    print(f"Total ideas before: {len(ideas)}")
    
    # Find max ID
    max_id = 0
    for idea in ideas:
        idea_id = idea.get('id', 'idea:0')
        if idea_id.startswith('idea:'):
            try:
                num = int(idea_id.split(':')[1])
                max_id = max(max_id, num)
            except (ValueError, IndexError):
                pass
    
    print(f"Max ID found: {max_id}")
    
    # Track seen IDs and reassign duplicates
    seen_ids = {}
    next_id = max_id + 1
    fixed_count = 0
    
    for i, idea in enumerate(ideas):
        idea_id = idea.get('id', f'idea:{i+1}')
        
        if idea_id in seen_ids:
            # Duplicate found - reassign
            old_id = idea_id
            new_id = f'idea:{next_id}'
            idea['id'] = new_id
            seen_ids[new_id] = i
            next_id += 1
            fixed_count += 1
            print(f"  ✓ Reassigned duplicate {old_id} → {new_id}: {idea.get('title', 'No title')[:50]}")
        else:
            seen_ids[idea_id] = i
    
    print(f"\n📊 Summary:")
    print(f"  Duplicates fixed: {fixed_count}")
    print(f"  Unique ideas: {len(seen_ids)}")
    
    # Save updated knowledge
    with open('world/knowledge.json', 'w') as f:
        json.dump(knowledge, f, indent=2)
    
    print(f"\n✅ Saved updated knowledge.json")
    return 0


if __name__ == '__main__':
    sys.exit(main())
