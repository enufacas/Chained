#!/usr/bin/env python3
"""
Test suite for agent coordination system.

Tests coordination, hibernation, and collaboration features.
Created by @accelerate-specialist.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from agent_coordinator import (
    AgentCoordinator,
    AgentWorkloadState,
    AgentState,
    MessageType
)


def test_agent_state_update():
    """Test updating agent workload state"""
    print("\n🧪 Test: Agent State Update")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_states = AgentCoordinator.STATES_FILE
        AgentCoordinator.STATES_FILE = f"{tmpdir}/agent_states.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Update agent state
            state = coordinator.update_agent_state(
                agent_id="agent-1",
                specialization="security",
                current_workload=5,
                capacity=10
            )
            
            assert state.agent_id == "agent-1", "Should set agent ID"
            assert state.utilization == 0.5, "Should calculate utilization"
            assert state.can_accept_work, "Should accept work at 50% capacity"
            
            print(f"  Agent utilization: {state.utilization:.0%}")
            print("✅ Agent state update works correctly")
            return True
            
        finally:
            AgentCoordinator.STATES_FILE = original_states
    
    return True


def test_message_sending():
    """Test sending messages between agents"""
    print("\n🧪 Test: Message Sending")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_messages = AgentCoordinator.MESSAGES_FILE
        AgentCoordinator.MESSAGES_FILE = f"{tmpdir}/messages.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Send message
            msg = coordinator.send_message(
                from_agent="agent-1",
                to_agent="agent-2",
                message_type=MessageType.WORKLOAD_OFFER,
                payload={'workload_count': 3},
                priority=4
            )
            
            assert msg.from_agent == "agent-1", "Should set sender"
            assert msg.to_agent == "agent-2", "Should set recipient"
            assert msg.message_type == MessageType.WORKLOAD_OFFER.value, "Should set type"
            assert msg.priority == 4, "Should set priority"
            
            print(f"  Sent message: {msg.id}")
            print("✅ Message sending works correctly")
            return True
            
        finally:
            AgentCoordinator.MESSAGES_FILE = original_messages
    
    return True


def test_message_retrieval():
    """Test retrieving messages for an agent"""
    print("\n🧪 Test: Message Retrieval")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_messages = AgentCoordinator.MESSAGES_FILE
        AgentCoordinator.MESSAGES_FILE = f"{tmpdir}/messages.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Send messages
            coordinator.send_message(
                from_agent="agent-1",
                to_agent="agent-2",
                message_type=MessageType.WORKLOAD_OFFER,
                payload={},
                priority=3
            )
            
            coordinator.send_message(
                from_agent="agent-3",
                to_agent=None,  # Broadcast
                message_type=MessageType.STATUS_UPDATE,
                payload={},
                priority=2
            )
            
            # Get messages for agent-2
            messages = coordinator.get_messages_for_agent("agent-2")
            
            assert len(messages) >= 2, "Should get direct and broadcast messages"
            print(f"  Agent-2 received {len(messages)} message(s)")
            print("✅ Message retrieval works correctly")
            return True
            
        finally:
            AgentCoordinator.MESSAGES_FILE = original_messages
    
    return True


def test_workload_redistribution():
    """Test workload redistribution"""
    print("\n🧪 Test: Workload Redistribution")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_states = AgentCoordinator.STATES_FILE
        original_messages = AgentCoordinator.MESSAGES_FILE
        AgentCoordinator.STATES_FILE = f"{tmpdir}/agent_states.json"
        AgentCoordinator.MESSAGES_FILE = f"{tmpdir}/messages.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Create overloaded agent
            coordinator.update_agent_state(
                agent_id="agent-overloaded",
                specialization="security",
                current_workload=9,
                capacity=10
            )
            
            # Create underutilized agent
            coordinator.update_agent_state(
                agent_id="agent-idle",
                specialization="security",
                current_workload=2,
                capacity=10
            )
            
            # Redistribute
            messages = coordinator.redistribute_workload("security")
            
            assert len(messages) > 0, "Should send redistribution messages"
            print(f"  Sent {len(messages)} redistribution message(s)")
            print("✅ Workload redistribution works correctly")
            return True
            
        finally:
            AgentCoordinator.STATES_FILE = original_states
            AgentCoordinator.MESSAGES_FILE = original_messages
    
    return True


def test_hibernation_detection():
    """Test identifying hibernation candidates"""
    print("\n🧪 Test: Hibernation Detection")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_states = AgentCoordinator.STATES_FILE
        AgentCoordinator.STATES_FILE = f"{tmpdir}/agent_states.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Create idle agent (old timestamp)
            old_time = (datetime.now() - timedelta(hours=48)).isoformat()
            
            state = AgentWorkloadState(
                agent_id="agent-idle",
                specialization="security",
                state=AgentState.ACTIVE.value,
                current_workload=1,
                capacity=10,
                utilization=0.1,
                last_activity=old_time,
                can_accept_work=True
            )
            coordinator.agent_states["agent-idle"] = state
            
            # Create another agent to maintain minimum
            coordinator.update_agent_state(
                agent_id="agent-active",
                specialization="security",
                current_workload=5,
                capacity=10
            )
            
            # Add third agent so we can hibernate one
            coordinator.update_agent_state(
                agent_id="agent-active-2",
                specialization="security",
                current_workload=4,
                capacity=10
            )
            
            # Find candidates
            candidates = coordinator.identify_hibernation_candidates()
            
            assert len(candidates) > 0, "Should identify idle agent"
            assert any(c.agent_id == "agent-idle" for c in candidates), "Should include idle agent"
            
            print(f"  Found {len(candidates)} hibernation candidate(s)")
            print("✅ Hibernation detection works correctly")
            return True
            
        finally:
            AgentCoordinator.STATES_FILE = original_states
    
    return True


def test_hibernation_execution():
    """Test hibernating an agent"""
    print("\n🧪 Test: Hibernation Execution")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_states = AgentCoordinator.STATES_FILE
        original_messages = AgentCoordinator.MESSAGES_FILE
        AgentCoordinator.STATES_FILE = f"{tmpdir}/agent_states.json"
        AgentCoordinator.MESSAGES_FILE = f"{tmpdir}/messages.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Create agent
            coordinator.update_agent_state(
                agent_id="agent-1",
                specialization="security",
                current_workload=1,
                capacity=10
            )
            
            # Hibernate
            coordinator.hibernate_agent("agent-1", reason="test_hibernation")
            
            # Check state
            state = coordinator.agent_states["agent-1"]
            assert state.state == AgentState.HIBERNATING.value, "Should be hibernating"
            
            # Check message sent
            messages = coordinator.get_messages_for_agent(None)
            hibernation_msgs = [
                m for m in messages
                if m.message_type == MessageType.HIBERNATION_NOTICE.value
            ]
            assert len(hibernation_msgs) > 0, "Should broadcast hibernation notice"
            
            print(f"  Agent state: {state.state}")
            print("✅ Hibernation execution works correctly")
            return True
            
        finally:
            AgentCoordinator.STATES_FILE = original_states
            AgentCoordinator.MESSAGES_FILE = original_messages
    
    return True


def test_wake_agent():
    """Test waking an agent from hibernation"""
    print("\n🧪 Test: Wake Agent")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_states = AgentCoordinator.STATES_FILE
        original_messages = AgentCoordinator.MESSAGES_FILE
        AgentCoordinator.STATES_FILE = f"{tmpdir}/agent_states.json"
        AgentCoordinator.MESSAGES_FILE = f"{tmpdir}/messages.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Create hibernating agent
            state = AgentWorkloadState(
                agent_id="agent-1",
                specialization="security",
                state=AgentState.HIBERNATING.value,
                current_workload=0,
                capacity=10,
                utilization=0.0,
                last_activity=datetime.now().isoformat(),
                can_accept_work=False
            )
            coordinator.agent_states["agent-1"] = state
            
            # Wake agent
            coordinator.wake_agent("agent-1", reason="workload_spike")
            
            # Check state
            state = coordinator.agent_states["agent-1"]
            assert state.state == AgentState.ACTIVE.value, "Should be active"
            
            print(f"  Agent state: {state.state}")
            print("✅ Wake agent works correctly")
            return True
            
        finally:
            AgentCoordinator.STATES_FILE = original_states
            AgentCoordinator.MESSAGES_FILE = original_messages
    
    return True


def test_collaboration_suggestions():
    """Test cross-specialization collaboration suggestions"""
    print("\n🧪 Test: Collaboration Suggestions")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_states = AgentCoordinator.STATES_FILE
        AgentCoordinator.STATES_FILE = f"{tmpdir}/agent_states.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Create agents in complementary specializations
            coordinator.update_agent_state(
                agent_id="agent-security",
                specialization="security",
                current_workload=5,
                capacity=10
            )
            
            coordinator.update_agent_state(
                agent_id="agent-testing",
                specialization="testing",
                current_workload=4,
                capacity=10
            )
            
            # Get suggestions
            suggestions = coordinator.suggest_cross_specialization_collaboration()
            
            assert len(suggestions) > 0, "Should suggest collaborations"
            
            # Check for security + testing collaboration
            sec_test_collab = [
                s for s in suggestions
                if s['primary_spec'] == 'security' and s['secondary_spec'] == 'testing'
            ]
            assert len(sec_test_collab) > 0, "Should suggest security + testing collaboration"
            
            print(f"  Found {len(suggestions)} collaboration opportunity(ies)")
            print("✅ Collaboration suggestions work correctly")
            return True
            
        finally:
            AgentCoordinator.STATES_FILE = original_states
    
    return True


def test_coordination_report():
    """Test coordination report generation"""
    print("\n🧪 Test: Coordination Report")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override file locations
        original_states = AgentCoordinator.STATES_FILE
        AgentCoordinator.STATES_FILE = f"{tmpdir}/agent_states.json"
        
        try:
            coordinator = AgentCoordinator()
            
            # Add some agents
            coordinator.update_agent_state(
                agent_id="agent-1",
                specialization="security",
                current_workload=5,
                capacity=10
            )
            
            coordinator.update_agent_state(
                agent_id="agent-2",
                specialization="testing",
                current_workload=3,
                capacity=10
            )
            
            # Generate report
            report = coordinator.generate_coordination_report()
            
            assert '# 🤝 Agent Coordination Report' in report, "Should have title"
            assert 'Active Agents' in report, "Should show active agents"
            assert 'Workload Distribution' in report, "Should show distribution"
            
            print(f"  Report length: {len(report)} characters")
            print("✅ Coordination report works correctly")
            return True
            
        finally:
            AgentCoordinator.STATES_FILE = original_states
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("🧪 Testing Agent Coordination System")
    print("=" * 80)
    
    tests = [
        test_agent_state_update,
        test_message_sending,
        test_message_retrieval,
        test_workload_redistribution,
        test_hibernation_detection,
        test_hibernation_execution,
        test_wake_agent,
        test_collaboration_suggestions,
        test_coordination_report,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{len(tests)} passed")
    
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")
    
    print("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
