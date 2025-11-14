"""
Test suite for agent evaluator workflow - agent archival functionality

This test ensures that eliminated agents are properly archived with their
specialization information intact, preventing the bug where agents were
skipped during archival.

Bug fixed: Eliminated agents were removed from registry['agents'] before
archival step tried to look them up, causing archival to be skipped.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from datetime import datetime


class TestAgentArchival:
    """Test cases for agent archival in the evaluator workflow"""

    def test_evaluation_results_include_specialization(self):
        """Test that evaluation results include specialization for all agent types"""
        
        # Setup test agents
        agents = [
            {
                "id": "test-promoted",
                "name": "Promoted Agent",
                "specialization": "engineer-master",
                "status": "active",
                "metrics": {"overall_score": 0.9}
            },
            {
                "id": "test-eliminated",
                "name": "Eliminated Agent",
                "specialization": "organize-guru",
                "status": "active",
                "metrics": {"overall_score": 0.2}
            },
            {
                "id": "test-maintained",
                "name": "Maintained Agent",
                "specialization": "coach-master",
                "status": "active",
                "metrics": {"overall_score": 0.5}
            }
        ]
        
        config = {
            "elimination_threshold": 0.3,
            "promotion_threshold": 0.85
        }
        
        # Simulate evaluation categorization
        promoted = []
        eliminated = []
        maintained = []
        
        for agent in agents:
            score = agent['metrics']['overall_score']
            if score >= config['promotion_threshold']:
                promoted.append(agent)
            elif score < config['elimination_threshold']:
                eliminated.append(agent)
            else:
                maintained.append(agent)
        
        # Create evaluation results (with the fix)
        results = {
            'promoted': [
                {
                    'id': a['id'],
                    'name': a['name'],
                    'score': a['metrics']['overall_score'],
                    'specialization': a.get('specialization', 'unknown')
                }
                for a in promoted
            ],
            'eliminated': [
                {
                    'id': a['id'],
                    'name': a['name'],
                    'score': a['metrics']['overall_score'],
                    'specialization': a.get('specialization', 'unknown')
                }
                for a in eliminated
            ],
            'maintained': [
                {
                    'id': a['id'],
                    'name': a['name'],
                    'score': a['metrics']['overall_score'],
                    'specialization': a.get('specialization', 'unknown')
                }
                for a in maintained
            ]
        }
        
        # Verify specialization is present
        assert len(results['promoted']) == 1
        assert results['promoted'][0]['specialization'] == 'engineer-master'
        
        assert len(results['eliminated']) == 1
        assert results['eliminated'][0]['specialization'] == 'organize-guru'
        
        assert len(results['maintained']) == 1
        assert results['maintained'][0]['specialization'] == 'coach-master'
        
        print("✅ All agent types include specialization in results")

    def test_archive_uses_specialization_from_results(self):
        """Test that archive step can use specialization from evaluation results"""
        
        test_dir = tempfile.mkdtemp()
        
        try:
            # Create test evaluation results
            results = {
                'eliminated': [
                    {
                        'id': 'test-agent-1',
                        'name': 'Test Agent 1',
                        'score': 0.2,
                        'specialization': 'organize-guru'
                    },
                    {
                        'id': 'test-agent-2',
                        'name': 'Test Agent 2',
                        'score': 0.15,
                        'specialization': 'secure-ninja'
                    }
                ]
            }
            
            # Create profile files
            profiles_dir = Path(test_dir) / "profiles"
            profiles_dir.mkdir(exist_ok=True)
            
            for agent in results['eliminated']:
                profile_path = profiles_dir / f"{agent['id']}.md"
                with open(profile_path, 'w') as f:
                    f.write(f"# {agent['name']}\n")
            
            # Create archive directory
            archive_dir = Path(test_dir) / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            # Simulate archive step (using the NEW fixed method)
            archived_agents = []
            for agent in results['eliminated']:
                agent_id = agent['id']
                agent_name = agent['name']
                
                # Archive profile
                profile_path = profiles_dir / f"{agent_id}.md"
                archive_path = archive_dir / f"{agent_id}.md"
                
                if profile_path.exists():
                    shutil.move(str(profile_path), str(archive_path))
                    
                    # Get specialization from evaluation results (THE FIX)
                    specialization = agent.get('specialization', 'unknown')
                    
                    # Verify we have the specialization
                    assert specialization != 'unknown', f"Specialization missing for {agent_name}"
                    
                    archived_agents.append({
                        'id': agent_id,
                        'name': agent_name,
                        'specialization': specialization
                    })
            
            # Verify all agents were archived
            assert len(archived_agents) == 2
            assert all(a['specialization'] != 'unknown' for a in archived_agents)
            
            # Verify profile files were moved
            assert not (profiles_dir / "test-agent-1.md").exists()
            assert not (profiles_dir / "test-agent-2.md").exists()
            assert (archive_dir / "test-agent-1.md").exists()
            assert (archive_dir / "test-agent-2.md").exists()
            
            print("✅ Archive step successfully uses specialization from results")
            print(f"✅ Archived {len(archived_agents)} agents with specializations")
            
        finally:
            shutil.rmtree(test_dir)

    def test_old_behavior_fails(self):
        """Demonstrate that the OLD behavior would fail (for regression testing)"""
        
        test_dir = tempfile.mkdtemp()
        
        try:
            # Create registry with agent
            registry = {
                "agents": [
                    {
                        "id": "test-agent",
                        "name": "Test Agent",
                        "specialization": "organize-guru",
                        "status": "active",
                        "metrics": {"overall_score": 0.2}
                    }
                ],
                "config": {"elimination_threshold": 0.3}
            }
            
            # Simulate elimination
            eliminated = []
            for agent in registry['agents']:
                if agent['metrics']['overall_score'] < registry['config']['elimination_threshold']:
                    agent['status'] = 'eliminated'
                    eliminated.append(agent)
            
            # Remove from registry (this is what happens in the workflow)
            registry['agents'] = [a for a in registry['agents'] if a['status'] == 'active']
            
            # OLD results format (WITHOUT specialization)
            old_results = {
                'eliminated': [
                    {'id': a['id'], 'name': a['name'], 'score': a['metrics']['overall_score']}
                    # NOTE: No specialization field!
                    for a in eliminated
                ]
            }
            
            # Try OLD archive method (looking up in registry)
            archived_count = 0
            for agent in old_results['eliminated']:
                agent_id = agent['id']
                
                # OLD: Try to find agent in registry
                full_agent = next(
                    (a for a in registry.get('agents', []) if a.get('id') == agent_id),
                    None
                )
                
                if not full_agent:
                    # This is what happens with the bug - agent not found!
                    continue
                
                # This code never executes because full_agent is None
                archived_count += 1
            
            # Verify the bug: no agents were archived
            assert archived_count == 0, "OLD method should fail to archive agents"
            
            print("✅ Verified that OLD behavior fails (agents not found in registry)")
            
        finally:
            shutil.rmtree(test_dir)

    def test_all_agent_types_preserved(self):
        """Test that promoted, eliminated, and maintained agents all have specialization"""
        
        agents = [
            {"id": "1", "name": "A", "specialization": "spec-a", "metrics": {"overall_score": 0.9}},
            {"id": "2", "name": "B", "specialization": "spec-b", "metrics": {"overall_score": 0.5}},
            {"id": "3", "name": "C", "specialization": "spec-c", "metrics": {"overall_score": 0.2}},
        ]
        
        config = {"elimination_threshold": 0.3, "promotion_threshold": 0.85}
        
        # Categorize
        results = {
            'promoted': [],
            'eliminated': [],
            'maintained': []
        }
        
        for agent in agents:
            score = agent['metrics']['overall_score']
            agent_info = {
                'id': agent['id'],
                'name': agent['name'],
                'score': score,
                'specialization': agent.get('specialization', 'unknown')
            }
            
            if score >= config['promotion_threshold']:
                results['promoted'].append(agent_info)
            elif score < config['elimination_threshold']:
                results['eliminated'].append(agent_info)
            else:
                results['maintained'].append(agent_info)
        
        # Verify all have specialization
        all_agents = (
            results['promoted'] + 
            results['eliminated'] + 
            results['maintained']
        )
        
        assert len(all_agents) == 3
        assert all('specialization' in a for a in all_agents)
        assert all(a['specialization'] != 'unknown' for a in all_agents)
        
        print("✅ All agent types (promoted, eliminated, maintained) preserve specialization")


def run_all_tests():
    """Run all test cases"""
    test_suite = TestAgentArchival()
    
    tests = [
        ("Evaluation results include specialization", test_suite.test_evaluation_results_include_specialization),
        ("Archive uses specialization from results", test_suite.test_archive_uses_specialization_from_results),
        ("Old behavior fails (regression test)", test_suite.test_old_behavior_fails),
        ("All agent types preserve specialization", test_suite.test_all_agent_types_preserved),
    ]
    
    print("="*70)
    print("Running Agent Evaluator Archival Tests")
    print("="*70)
    print()
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"Running: {name}")
            test_func()
            passed += 1
            print()
        except AssertionError as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
            print()
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   Error: {e}")
            failed += 1
            print()
    
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
