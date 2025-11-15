#!/usr/bin/env python3
"""
Tests for Hierarchical Agent System

Validates the role-based hierarchical coordination system.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from hierarchical_agent_system import (
    HierarchicalAgentSystem,
    AgentRole,
    AgentTier,
    DelegationChain,
    DelegationStatus
)


def create_test_registry(temp_dir):
    """Create a test agent registry"""
    registry = {
        'agents': [
            {
                'id': 'agent-coord-1',
                'name': '🎯 Alan Turing',
                'specialization': 'meta-coordinator',
                'status': 'active',
                'metrics': {'overall_score': 0.9}
            },
            {
                'id': 'agent-spec-1',
                'name': '⚙️ Margaret Hamilton',
                'specialization': 'engineer-master',
                'status': 'active',
                'metrics': {'overall_score': 0.85}
            },
            {
                'id': 'agent-spec-2',
                'name': '🔒 Bruce Schneier',
                'specialization': 'secure-specialist',
                'status': 'active',
                'metrics': {'overall_score': 0.8}
            },
            {
                'id': 'agent-worker-1',
                'name': '⚡ Rich Hickey',
                'specialization': 'accelerate-master',
                'status': 'active',
                'metrics': {'overall_score': 0.75}
            },
            {
                'id': 'agent-worker-2',
                'name': '🧪 Leslie Lamport',
                'specialization': 'assert-specialist',
                'status': 'active',
                'metrics': {'overall_score': 0.7}
            }
        ]
    }
    
    agent_system_dir = temp_dir / '.github' / 'agent-system'
    agent_system_dir.mkdir(parents=True, exist_ok=True)
    
    with open(agent_system_dir / 'registry.json', 'w') as f:
        json.dump(registry, f, indent=2)
    
    return temp_dir


class TestHierarchicalAgentSystem:
    """Test suite for hierarchical agent system"""
    
    def __init__(self):
        self.temp_dir = None
        self.system = None
    
    def setup(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        create_test_registry(self.temp_dir)
        self.system = HierarchicalAgentSystem(str(self.temp_dir))
    
    def teardown(self):
        """Clean up test environment"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_agent_tier_initialization(self):
        """Test that agents are assigned to correct tiers"""
        print("Testing agent tier initialization...")
        
        # Check coordinator tier
        coordinators = self.system.get_coordinator_agents()
        assert len(coordinators) == 1, f"Expected 1 coordinator, got {len(coordinators)}"
        assert 'agent-coord-1' in coordinators
        
        # Check specialist tier
        specialists = self.system.get_specialist_agents()
        assert len(specialists) == 2, f"Expected 2 specialists, got {len(specialists)}"
        assert 'agent-spec-1' in specialists
        assert 'agent-spec-2' in specialists
        
        # Check worker tier
        workers = self.system.get_worker_agents()
        assert len(workers) == 2, f"Expected 2 workers, got {len(workers)}"
        assert 'agent-worker-1' in workers
        assert 'agent-worker-2' in workers
        
        print("✓ Agent tier initialization test passed")
    
    def test_role_delegation_rules(self):
        """Test that delegation rules are correctly enforced"""
        print("Testing role delegation rules...")
        
        coord_tier = self.system.agent_tiers['agent-coord-1']
        spec_tier = self.system.agent_tiers['agent-spec-1']
        worker_tier = self.system.agent_tiers['agent-worker-1']
        
        # Coordinators can delegate to specialists and workers
        assert AgentRole.SPECIALIST in coord_tier.can_delegate_to
        assert AgentRole.WORKER in coord_tier.can_delegate_to
        
        # Specialists can delegate to workers
        assert AgentRole.WORKER in spec_tier.can_delegate_to
        assert AgentRole.COORDINATOR not in spec_tier.can_delegate_to
        
        # Workers cannot delegate
        assert len(worker_tier.can_delegate_to) == 0
        
        print("✓ Role delegation rules test passed")
    
    def test_hierarchical_plan_creation(self):
        """Test creation of hierarchical coordination plan"""
        print("Testing hierarchical plan creation...")
        
        plan, chain = self.system.create_hierarchical_plan(
            task_id="test-123",
            task_description="Build API with security audit and testing",
            task_context={'labels': ['api', 'security']}
        )
        
        # Verify plan was created
        assert plan is not None
        assert plan.task_id == "test-123"
        assert len(plan.sub_tasks) > 0
        
        # Verify delegation chain
        assert chain is not None
        assert chain.root_task_id == "test-123"
        assert chain.coordinator_id == 'agent-coord-1'
        
        # Verify hierarchy levels
        assert len(chain.hierarchy) >= 1
        assert chain.hierarchy[0]['level'] == 0
        assert chain.hierarchy[0]['role'] == 'coordinator'
        
        print("✓ Hierarchical plan creation test passed")
    
    def test_valid_delegation(self):
        """Test successful task delegation"""
        print("Testing valid delegation...")
        
        # Coordinator delegating to specialist
        delegation = self.system.delegate_task(
            from_agent='agent-coord-1',
            to_agent='agent-spec-1',
            task_description='Design API architecture'
        )
        
        assert delegation is not None
        assert delegation['from_agent'] == 'agent-coord-1'
        assert delegation['to_agent'] == 'agent-spec-1'
        assert delegation['from_role'] == 'coordinator'
        assert delegation['to_role'] == 'specialist'
        assert delegation['status'] == 'pending'
        
        print("✓ Valid delegation test passed")
    
    def test_invalid_delegation(self):
        """Test that invalid delegations are rejected"""
        print("Testing invalid delegation...")
        
        # Worker trying to delegate to specialist (not allowed)
        try:
            self.system.delegate_task(
                from_agent='agent-worker-1',
                to_agent='agent-spec-1',
                task_description='Some task'
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "cannot delegate to" in str(e)
        
        # Specialist trying to delegate to coordinator (not allowed)
        try:
            self.system.delegate_task(
                from_agent='agent-spec-1',
                to_agent='agent-coord-1',
                task_description='Some task'
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "cannot delegate to" in str(e)
        
        print("✓ Invalid delegation test passed")
    
    def test_task_escalation(self):
        """Test task escalation up the hierarchy"""
        print("Testing task escalation...")
        
        # Worker escalating to specialist
        escalation = self.system.escalate_task(
            from_agent='agent-worker-1',
            task_id='subtask-456',
            reason='Task complexity exceeds capability'
        )
        
        assert escalation is not None
        assert escalation['from_agent'] == 'agent-worker-1'
        assert escalation['from_role'] == 'worker'
        assert escalation['to_role'] == 'specialist'
        assert escalation['reason'] == 'Task complexity exceeds capability'
        
        # Verify escalated to a specialist
        assert escalation['to_agent'] in self.system.get_specialist_agents()
        
        print("✓ Task escalation test passed")
    
    def test_hierarchy_summary(self):
        """Test hierarchy summary generation"""
        print("Testing hierarchy summary...")
        
        summary = self.system.get_hierarchy_summary()
        
        assert summary['total_agents'] == 5
        assert summary['by_role']['coordinator'] == 1
        assert summary['by_role']['specialist'] == 2
        assert summary['by_role']['worker'] == 2
        
        assert len(summary['coordinator_agents']) == 1
        assert len(summary['specialist_agents']) == 2
        assert len(summary['worker_agents']) == 2
        
        print("✓ Hierarchy summary test passed")
    
    def test_specialist_filtering(self):
        """Test filtering specialists by specialization"""
        print("Testing specialist filtering...")
        
        # Get all specialists
        all_specialists = self.system.get_specialist_agents()
        assert len(all_specialists) == 2
        
        # Get engineer specialists
        engineer_specialists = self.system.get_specialist_agents('engineer-master')
        assert len(engineer_specialists) == 1
        assert 'agent-spec-1' in engineer_specialists
        
        # Get security specialists
        security_specialists = self.system.get_specialist_agents('secure-specialist')
        assert len(security_specialists) == 1
        assert 'agent-spec-2' in security_specialists
        
        print("✓ Specialist filtering test passed")
    
    def test_worker_filtering(self):
        """Test filtering workers by specialization"""
        print("Testing worker filtering...")
        
        # Get all workers
        all_workers = self.system.get_worker_agents()
        assert len(all_workers) == 2
        
        # Get performance workers
        perf_workers = self.system.get_worker_agents('accelerate-master')
        assert len(perf_workers) == 1
        assert 'agent-worker-1' in perf_workers
        
        # Get testing workers
        test_workers = self.system.get_worker_agents('assert-specialist')
        assert len(test_workers) == 1
        assert 'agent-worker-2' in test_workers
        
        print("✓ Worker filtering test passed")
    
    def test_delegation_logging(self):
        """Test that delegations are properly logged"""
        print("Testing delegation logging...")
        
        initial_count = self.system.delegation_log['statistics']['total_delegations']
        
        # Create a delegation
        self.system.delegate_task(
            from_agent='agent-coord-1',
            to_agent='agent-spec-1',
            task_description='Test task'
        )
        
        # Verify count increased
        new_count = self.system.delegation_log['statistics']['total_delegations']
        assert new_count == initial_count + 1
        
        # Verify delegation was logged
        assert len(self.system.delegation_log['delegation_chains']) > 0
        
        print("✓ Delegation logging test passed")
    
    def test_escalation_to_best_supervisor(self):
        """Test that escalation selects the best supervisor"""
        print("Testing escalation to best supervisor...")
        
        # Worker escalates - should go to best specialist
        escalation = self.system.escalate_task(
            from_agent='agent-worker-1',
            task_id='test-task',
            reason='Need help'
        )
        
        # Should escalate to agent-spec-1 (highest score: 0.85)
        assert escalation['to_agent'] == 'agent-spec-1'
        
        print("✓ Escalation to best supervisor test passed")
    
    def test_configuration_persistence(self):
        """Test that configuration is saved and loaded correctly"""
        print("Testing configuration persistence...")
        
        # Modify configuration
        self.system.hierarchy_config['oversight_enabled'] = False
        self.system._save_hierarchy_config()
        
        # Create new system instance
        new_system = HierarchicalAgentSystem(str(self.temp_dir))
        
        # Verify configuration was loaded
        assert new_system.hierarchy_config['oversight_enabled'] == False
        
        print("✓ Configuration persistence test passed")
    
    def run_all_tests(self):
        """Run all tests"""
        tests = [
            self.test_agent_tier_initialization,
            self.test_role_delegation_rules,
            self.test_hierarchical_plan_creation,
            self.test_valid_delegation,
            self.test_invalid_delegation,
            self.test_task_escalation,
            self.test_hierarchy_summary,
            self.test_specialist_filtering,
            self.test_worker_filtering,
            self.test_delegation_logging,
            self.test_escalation_to_best_supervisor,
            self.test_configuration_persistence,
        ]
        
        print("\n" + "="*60)
        print("Running Hierarchical Agent System Tests")
        print("="*60 + "\n")
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                self.setup()
                test()
                passed += 1
            except AssertionError as e:
                print(f"✗ {test.__name__} failed: {e}")
                failed += 1
            except Exception as e:
                print(f"✗ {test.__name__} error: {e}")
                failed += 1
            finally:
                self.teardown()
        
        print("\n" + "="*60)
        print(f"Test Results: {passed} passed, {failed} failed")
        print("="*60 + "\n")
        
        return failed == 0


def main():
    """Run tests"""
    test_suite = TestHierarchicalAgentSystem()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
