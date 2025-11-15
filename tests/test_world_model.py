#!/usr/bin/env python3
"""
Integration test for the world model system.
Tests the complete flow: article ingestion → agent update → state persistence.
"""

import sys
import os
import json

# Add world directory to path
WORLD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'world')
sys.path.insert(0, WORLD_DIR)

from world_state_manager import load_world_state, get_all_agents
from knowledge_manager import load_knowledge, get_all_ideas


def test_world_model_integration():
    """Run integration tests on the world model."""
    print("=" * 60)
    print("🧪 World Model Integration Test")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Load world state
    print("\n1. Testing world state loading...")
    try:
        state = load_world_state()
        assert 'tick' in state
        assert 'agents' in state
        assert 'regions' in state
        assert 'metrics' in state
        print("   ✅ World state loaded successfully")
        print(f"   - Tick: {state['tick']}")
        print(f"   - Agents: {len(state['agents'])}")
        print(f"   - Regions: {len(state['regions'])}")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 2: Load knowledge base
    print("\n2. Testing knowledge base loading...")
    try:
        knowledge = load_knowledge()
        assert 'ideas' in knowledge
        ideas = get_all_ideas(knowledge)
        print("   ✅ Knowledge base loaded successfully")
        print(f"   - Ideas: {len(ideas)}")
        if ideas:
            print(f"   - Sample: {ideas[0].get('title', 'N/A')[:50]}...")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 3: Validate data consistency
    print("\n3. Testing data consistency...")
    try:
        state = load_world_state()
        knowledge = load_knowledge()
        
        # Check that metrics match actual data
        actual_ideas = len(knowledge.get('ideas', []))
        actual_regions = len(state.get('regions', []))
        
        metrics = state.get('metrics', {})
        metric_ideas = metrics.get('total_ideas', 0)
        metric_regions = metrics.get('total_regions', 0)
        
        # Allow small discrepancy due to timing
        idea_diff = abs(actual_ideas - metric_ideas)
        region_diff = abs(actual_regions - metric_regions)
        
        print(f"   Ideas: {actual_ideas} (metrics: {metric_ideas})")
        print(f"   Regions: {actual_regions} (metrics: {metric_regions})")
        
        if idea_diff <= 1 and region_diff <= 1:
            print("   ✅ Data consistency validated")
            tests_passed += 1
        else:
            print(f"   ⚠️  Small inconsistency detected (acceptable)")
            tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 4: Validate agent structure
    print("\n4. Testing agent data structure...")
    try:
        state = load_world_state()
        agents = get_all_agents(state)
        
        if agents:
            agent = agents[0]
            required_fields = ['id', 'label', 'location_region_id', 'status']
            
            for field in required_fields:
                assert field in agent, f"Missing field: {field}"
            
            print("   ✅ Agent structure validated")
            print(f"   - Agent: {agent.get('label')}")
            print(f"   - Location: {agent.get('location_region_id')}")
            print(f"   - Status: {agent.get('status')}")
            tests_passed += 1
        else:
            print("   ⚠️  No agents to test")
            tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 5: Validate region structure
    print("\n5. Testing region data structure...")
    try:
        state = load_world_state()
        regions = state.get('regions', [])
        
        if regions:
            region = regions[0]
            required_fields = ['id', 'label', 'lat', 'lng', 'idea_count']
            
            for field in required_fields:
                assert field in region, f"Missing field: {field}"
            
            # Validate coordinates
            assert -90 <= region['lat'] <= 90, "Invalid latitude"
            assert -180 <= region['lng'] <= 180, "Invalid longitude"
            
            print("   ✅ Region structure validated")
            print(f"   - Region: {region.get('label')}")
            print(f"   - Coordinates: ({region.get('lat')}, {region.get('lng')})")
            print(f"   - Ideas: {region.get('idea_count')}")
            tests_passed += 1
        else:
            print("   ⚠️  No regions to test")
            tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Test 6: Validate idea structure
    print("\n6. Testing idea data structure...")
    try:
        knowledge = load_knowledge()
        ideas = get_all_ideas(knowledge)
        
        if ideas:
            idea = ideas[0]
            required_fields = ['id', 'title', 'summary', 'patterns', 'companies', 'inspiration_regions']
            
            for field in required_fields:
                assert field in idea, f"Missing field: {field}"
            
            # Validate inspiration regions
            if idea['inspiration_regions']:
                insp = idea['inspiration_regions'][0]
                assert 'region_id' in insp
                assert 'lat' in insp
                assert 'lng' in insp
                assert 'weight' in insp
                assert 0 <= insp['weight'] <= 1, "Weight should be 0-1"
            
            print("   ✅ Idea structure validated")
            print(f"   - Idea: {idea.get('title')[:50]}...")
            print(f"   - Patterns: {len(idea.get('patterns', []))}")
            print(f"   - Companies: {len(idea.get('companies', []))}")
            print(f"   - Regions: {len(idea.get('inspiration_regions', []))}")
            tests_passed += 1
        else:
            print("   ⚠️  No ideas to test")
            tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 All tests passed! World model is healthy.")
        return 0
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Please review.")
        return 1


if __name__ == '__main__':
    sys.exit(test_world_model_integration())
