#!/usr/bin/env python3
"""
Test AI Idea Deduplication System

**@refactor-champion** Test: Verifies that the AI idea generation system
prevents duplicate ideas from being created across multiple workflow runs.

This test ensures:
1. Ideas are hashed consistently
2. Previously used ideas are skipped
3. History file is properly maintained
4. Cycle resets when all ideas are used
"""

import json
import hashlib
import sys
import os
from datetime import datetime, timezone


def generate_idea_hash(idea_text):
    """Generate hash for an AI idea"""
    return hashlib.md5(idea_text.encode()).hexdigest()


def test_hash_consistency():
    """Test that hashes are generated consistently"""
    print("🧪 Testing Hash Consistency")
    print("=" * 70)
    
    idea = "Self-evolving neural architecture adapting workflows based on success rates"
    
    # Generate hash multiple times
    hash1 = generate_idea_hash(idea)
    hash2 = generate_idea_hash(idea)
    hash3 = generate_idea_hash(idea)
    
    if hash1 == hash2 == hash3:
        print(f"✅ PASS: Hashes are consistent")
        print(f"   Hash: {hash1}")
        return True
    else:
        print(f"❌ FAIL: Hashes are inconsistent")
        print(f"   Hash 1: {hash1}")
        print(f"   Hash 2: {hash2}")
        print(f"   Hash 3: {hash3}")
        return False


def test_deduplication_logic():
    """Test the deduplication logic"""
    print("\n🧪 Testing Deduplication Logic")
    print("=" * 70)
    
    # Sample ideas pool (matching the workflow)
    ai_ideas = [
        "Self-evolving neural architecture adapting workflows based on success rates",
        "AI agent learning from failed PRs to improve code generation",
        "Meta-learning system optimizing workflow schedules",
        "Autonomous code reviewer improving criteria over time",
        "AI-powered workflow orchestrator predicting execution times"
    ]
    
    # Simulate history
    history = {
        'idea_hashes': [],
        'created_ideas': [],
        'last_updated': None
    }
    
    # First run: Select first 3 ideas
    print("\n📝 Simulating First 3 Runs:")
    for i in range(3):
        existing_hashes = set(history.get('idea_hashes', []))
        
        # Find available ideas
        available_ideas = []
        for idea_text in ai_ideas:
            idea_hash = generate_idea_hash(idea_text)
            if idea_hash not in existing_hashes:
                available_ideas.append((idea_text, idea_hash))
        
        if available_ideas:
            # Pick first available
            idea, idea_hash = available_ideas[0]
            
            # Record it
            history['idea_hashes'].append(idea_hash)
            history['created_ideas'].append({
                'idea': idea,
                'hash': idea_hash,
                'created_at': datetime.now(timezone.utc).isoformat()
            })
            
            print(f"  Run {i+1}: Selected idea (hash: {idea_hash[:8]}...)")
            print(f"         Available: {len(available_ideas)}/{len(ai_ideas)}")
    
    # Verify we have 3 unique ideas
    unique_hashes = set(history['idea_hashes'])
    if len(unique_hashes) == 3:
        print(f"✅ PASS: 3 unique ideas created")
    else:
        print(f"❌ FAIL: Expected 3 unique ideas, got {len(unique_hashes)}")
        return False
    
    # Simulate using all ideas
    print("\n📝 Simulating Using All Ideas:")
    while True:
        existing_hashes = set(history.get('idea_hashes', []))
        
        available_ideas = []
        for idea_text in ai_ideas:
            idea_hash = generate_idea_hash(idea_text)
            if idea_hash not in existing_hashes:
                available_ideas.append((idea_text, idea_hash))
        
        if not available_ideas:
            print(f"  ✅ All {len(ai_ideas)} ideas have been used")
            break
        
        # Use next idea
        idea, idea_hash = available_ideas[0]
        history['idea_hashes'].append(idea_hash)
    
    # Verify all ideas used
    if len(set(history['idea_hashes'])) == len(ai_ideas):
        print(f"✅ PASS: All ideas used exactly once")
    else:
        print(f"❌ FAIL: Not all ideas used")
        return False
    
    # Test cycle reset
    print("\n📝 Testing Cycle Reset:")
    existing_hashes = set(history.get('idea_hashes', []))
    
    available_ideas = []
    for idea_text in ai_ideas:
        idea_hash = generate_idea_hash(idea_text)
        if idea_hash not in existing_hashes:
            available_ideas.append((idea_text, idea_hash))
    
    if not available_ideas:
        print(f"  ✅ Detected all ideas used (should trigger reset)")
        # Reset would happen here in the workflow
        history['idea_hashes'] = []
        history['created_ideas'] = []
        print(f"  🔄 Cycle reset - ready for new round")
    else:
        print(f"❌ FAIL: Should have detected all ideas used")
        return False
    
    return True


def test_history_file_format():
    """Test that history file exists and has correct format"""
    print("\n🧪 Testing History File Format")
    print("=" * 70)
    
    history_file = '.github/agent-system/ai_ideas_history.json'
    
    if not os.path.exists(history_file):
        print(f"❌ FAIL: History file does not exist: {history_file}")
        return False
    
    print(f"✅ History file exists: {history_file}")
    
    try:
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        # Check required fields
        required_fields = ['idea_hashes', 'created_ideas', 'last_updated']
        for field in required_fields:
            if field not in history:
                print(f"❌ FAIL: Missing required field: {field}")
                return False
        
        print(f"✅ PASS: All required fields present")
        
        # Check types
        if not isinstance(history['idea_hashes'], list):
            print(f"❌ FAIL: idea_hashes should be a list")
            return False
        
        if not isinstance(history['created_ideas'], list):
            print(f"❌ FAIL: created_ideas should be a list")
            return False
        
        print(f"✅ PASS: Field types are correct")
        
        # Show current state
        print(f"\n📊 Current History State:")
        print(f"  Total ideas created: {len(history['idea_hashes'])}")
        print(f"  Last updated: {history['last_updated']}")
        
        if history['created_ideas']:
            print(f"\n  Recent ideas:")
            for i, item in enumerate(history['created_ideas'][-3:], 1):
                print(f"    {i}. {item['idea'][:60]}...")
                print(f"       Hash: {item['hash'][:16]}...")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: Invalid JSON in history file: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 AI Idea Deduplication Tests (@refactor-champion)")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Hash Consistency", test_hash_consistency()))
    results.append(("Deduplication Logic", test_deduplication_logic()))
    results.append(("History File Format", test_history_file_format()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 SUCCESS: All deduplication tests passed!")
        return 0
    else:
        print(f"\n❌ FAILURE: {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
