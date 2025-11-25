#!/usr/bin/env python3
"""
Tests for Collaborative Agent Orchestrator

Validates the unified multi-agent collaboration system.
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

from collaborative_agent_orchestrator import (
    CollaborativeAgentOrchestrator,
    CollaborationSession,
    CollaborationMessage,
    CollaborationStatus,
    AgentMessage
)


def create_test_registry(temp_dir: Path) -> None:
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
                'id': 'agent-eng-1',
                'name': '⚙️ Margaret Hamilton',
                'specialization': 'engineer-master',
                'status': 'active',
                'metrics': {'overall_score': 0.85}
            },
            {
                'id': 'agent-sec-1',
                'name': '🔒 Bruce Schneier',
                'specialization': 'secure-specialist',
                'status': 'active',
                'metrics': {'overall_score': 0.8}
            },
            {
                'id': 'agent-perf-1',
                'name': '⚡ Rich Hickey',
                'specialization': 'accelerate-master',
                'status': 'active',
                'metrics': {'overall_score': 0.75}
            },
            {
                'id': 'agent-test-1',
                'name': '🧪 Leslie Lamport',
                'specialization': 'assert-specialist',
                'status': 'active',
                'metrics': {'overall_score': 0.7}
            },
            {
                'id': 'agent-doc-1',
                'name': '📚 Donald Knuth',
                'specialization': 'support-master',
                'status': 'active',
                'metrics': {'overall_score': 0.72}
            }
        ]
    }
    
    agent_system_dir = temp_dir / '.github' / 'agent-system'
    agent_system_dir.mkdir(parents=True, exist_ok=True)
    
    with open(agent_system_dir / 'registry.json', 'w') as f:
        json.dump(registry, f, indent=2)


class TestCollaborativeAgentOrchestrator:
    """Test suite for CollaborativeAgentOrchestrator"""
    
    def __init__(self):
        self.temp_dir = None
        self.orchestrator = None
    
    def setup(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        create_test_registry(self.temp_dir)
        self.orchestrator = CollaborativeAgentOrchestrator(str(self.temp_dir))
    
    def teardown(self):
        """Clean up test environment"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        print("Testing orchestrator initialization...")
        
        assert self.orchestrator is not None
        assert self.orchestrator.coordinator is not None
        assert self.orchestrator.hierarchy is not None
        assert isinstance(self.orchestrator.sessions, dict)
        
        print("✓ Orchestrator initialization test passed")
    
    def test_start_collaboration_simple(self):
        """Test starting a simple collaboration session"""
        print("Testing simple collaboration start...")
        
        session = self.orchestrator.start_collaboration(
            task_id="issue-1",
            task_description="Add README documentation"
        )
        
        assert session is not None
        assert isinstance(session, CollaborationSession)
        assert session.task_id == "issue-1"
        assert session.status == CollaborationStatus.EXECUTING
        assert 'meta-coordinator' in session.participating_agents
        
        print("✓ Simple collaboration start test passed")
    
    def test_start_collaboration_complex(self):
        """Test starting a complex collaboration session"""
        print("Testing complex collaboration start...")
        
        session = self.orchestrator.start_collaboration(
            task_id="issue-2",
            task_description="""
                Build a secure authentication API:
                - Security audit
                - API design and implementation
                - Performance optimization
                - Comprehensive testing
                - Documentation
            """
        )
        
        assert session is not None
        assert session.plan is not None
        assert len(session.plan.sub_tasks) > 1
        assert len(session.participating_agents) > 1
        assert len(session.messages) > 0
        
        print("✓ Complex collaboration start test passed")
    
    def test_session_persistence(self):
        """Test that sessions are persisted"""
        print("Testing session persistence...")
        
        session = self.orchestrator.start_collaboration(
            task_id="persist-test",
            task_description="Test persistence"
        )
        
        # Create new orchestrator instance
        new_orchestrator = CollaborativeAgentOrchestrator(str(self.temp_dir))
        
        # Verify session was loaded
        loaded_session = new_orchestrator.get_session(session.session_id)
        assert loaded_session is not None
        assert loaded_session.task_id == "persist-test"
        
        print("✓ Session persistence test passed")
    
    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        print("Testing progress tracking...")
        
        session = self.orchestrator.start_collaboration(
            task_id="progress-test",
            task_description="Test progress tracking with API and documentation"
        )
        
        subtask_ids = list(session.progress.keys())
        assert len(subtask_ids) > 0
        
        # Update progress
        self.orchestrator.update_progress(
            session_id=session.session_id,
            subtask_id=subtask_ids[0],
            progress=50.0,
            agent_id='agent-eng-1'
        )
        
        # Verify progress was updated
        updated_session = self.orchestrator.get_session(session.session_id)
        assert updated_session.progress[subtask_ids[0]] == 50.0
        
        print("✓ Progress tracking test passed")
    
    def test_message_sending(self):
        """Test message sending between agents"""
        print("Testing message sending...")
        
        session = self.orchestrator.start_collaboration(
            task_id="message-test",
            task_description="Test message passing"
        )
        
        initial_message_count = len(session.messages)
        
        # Send a message
        message = self.orchestrator.send_message(
            session_id=session.session_id,
            from_agent='agent-eng-1',
            to_agents=['meta-coordinator'],
            message_type=AgentMessage.PROGRESS_UPDATE,
            content={'status': 'working'}
        )
        
        assert message is not None
        assert message.from_agent == 'agent-eng-1'
        assert 'meta-coordinator' in message.to_agents
        
        # Verify message was added
        updated_session = self.orchestrator.get_session(session.session_id)
        assert len(updated_session.messages) == initial_message_count + 1
        
        print("✓ Message sending test passed")
    
    def test_help_request(self):
        """Test help request functionality"""
        print("Testing help request...")
        
        session = self.orchestrator.start_collaboration(
            task_id="help-test",
            task_description="Test help requests"
        )
        
        subtask_ids = list(session.progress.keys())
        
        message = self.orchestrator.request_help(
            session_id=session.session_id,
            from_agent='agent-eng-1',
            subtask_id=subtask_ids[0],
            reason='Need guidance on approach'
        )
        
        assert message is not None
        assert message.message_type == AgentMessage.HELP_NEEDED
        assert message.content['reason'] == 'Need guidance on approach'
        
        print("✓ Help request test passed")
    
    def test_blocked_report(self):
        """Test blocked report functionality"""
        print("Testing blocked report...")
        
        session = self.orchestrator.start_collaboration(
            task_id="blocked-test",
            task_description="Test blocking with API and testing tasks"
        )
        
        subtask_ids = list(session.progress.keys())
        
        if len(subtask_ids) >= 2:
            message = self.orchestrator.report_blocked(
                session_id=session.session_id,
                from_agent='agent-test-1',
                subtask_id=subtask_ids[1],
                blocking_subtasks=[subtask_ids[0]],
                reason='Waiting for API implementation'
            )
            
            assert message is not None
            assert message.message_type == AgentMessage.BLOCKED
            assert subtask_ids[0] in message.content['blocking_subtasks']
        
        print("✓ Blocked report test passed")
    
    def test_review_request(self):
        """Test review request functionality"""
        print("Testing review request...")
        
        session = self.orchestrator.start_collaboration(
            task_id="review-test",
            task_description="Test review requests"
        )
        
        subtask_ids = list(session.progress.keys())
        
        message = self.orchestrator.request_review(
            session_id=session.session_id,
            from_agent='agent-eng-1',
            subtask_id=subtask_ids[0],
            reviewer_agents=['agent-sec-1']
        )
        
        assert message is not None
        assert message.message_type == AgentMessage.REVIEW_REQUESTED
        assert 'agent-sec-1' in message.to_agents
        
        print("✓ Review request test passed")
    
    def test_subtask_completion(self):
        """Test subtask completion flow"""
        print("Testing subtask completion...")
        
        session = self.orchestrator.start_collaboration(
            task_id="complete-test",
            task_description="Test completion flow"
        )
        
        subtask_ids = list(session.progress.keys())
        
        # Complete a subtask
        self.orchestrator.mark_subtask_completed(
            session_id=session.session_id,
            subtask_id=subtask_ids[0],
            agent_id='agent-eng-1',
            result={'status': 'done'}
        )
        
        # Verify completion
        updated_session = self.orchestrator.get_session(session.session_id)
        assert updated_session.progress[subtask_ids[0]] == 100.0
        
        print("✓ Subtask completion test passed")
    
    def test_collaboration_completion(self):
        """Test completing a full collaboration"""
        print("Testing collaboration completion...")
        
        session = self.orchestrator.start_collaboration(
            task_id="full-complete-test",
            task_description="Test full completion"
        )
        
        # Complete all subtasks
        for subtask_id in session.progress.keys():
            self.orchestrator.mark_subtask_completed(
                session_id=session.session_id,
                subtask_id=subtask_id,
                agent_id='agent-eng-1'
            )
        
        # Complete the collaboration
        completed = self.orchestrator.complete_collaboration(
            session_id=session.session_id,
            summary='All tasks completed successfully'
        )
        
        assert completed.status == CollaborationStatus.COMPLETED
        assert completed.completed_at is not None
        
        print("✓ Collaboration completion test passed")
    
    def test_session_summary(self):
        """Test session summary generation"""
        print("Testing session summary...")
        
        session = self.orchestrator.start_collaboration(
            task_id="summary-test",
            task_description="Test summary generation with API tasks"
        )
        
        summary = self.orchestrator.get_session_summary(session.session_id)
        
        assert 'session_id' in summary
        assert 'status' in summary
        assert 'overall_progress' in summary
        assert 'participating_agents' in summary
        assert 'message_count' in summary
        
        print("✓ Session summary test passed")
    
    def test_pending_messages(self):
        """Test getting pending messages for an agent"""
        print("Testing pending messages...")
        
        session = self.orchestrator.start_collaboration(
            task_id="pending-test",
            task_description="Test pending messages"
        )
        
        # Get pending messages for an agent
        # Note: Task assignment messages are sent during start_collaboration
        subtask_ids = list(session.progress.keys())
        
        # Send a direct message
        self.orchestrator.send_message(
            session_id=session.session_id,
            from_agent='meta-coordinator',
            to_agents=['agent-eng-1'],
            message_type=AgentMessage.TASK_ASSIGNED,
            content={'test': True}
        )
        
        pending = self.orchestrator.get_pending_messages('agent-eng-1')
        assert len(pending) >= 1
        
        print("✓ Pending messages test passed")
    
    def test_message_read_tracking(self):
        """Test marking messages as read"""
        print("Testing message read tracking...")
        
        session = self.orchestrator.start_collaboration(
            task_id="read-test",
            task_description="Test read tracking"
        )
        
        # Get a message
        if session.messages:
            message = session.messages[0]
            
            # Mark as read
            self.orchestrator.mark_message_read(message.id, 'test-agent')
            
            # Verify read status
            updated_session = self.orchestrator.get_session(session.session_id)
            updated_message = next(m for m in updated_session.messages if m.id == message.id)
            assert 'test-agent' in updated_message.read_by
        
        print("✓ Message read tracking test passed")
    
    def test_list_active_sessions(self):
        """Test listing active sessions"""
        print("Testing list active sessions...")
        
        # Create some sessions
        session1 = self.orchestrator.start_collaboration(
            task_id="list-test-1",
            task_description="First test"
        )
        session2 = self.orchestrator.start_collaboration(
            task_id="list-test-2",
            task_description="Second test"
        )
        
        active = self.orchestrator.list_active_sessions()
        assert len(active) >= 2
        
        # Complete one
        self.orchestrator.complete_collaboration(session1.session_id)
        
        active_after = self.orchestrator.list_active_sessions()
        assert len(active_after) == len(active) - 1
        
        print("✓ List active sessions test passed")
    
    def test_collaboration_stats(self):
        """Test collaboration statistics"""
        print("Testing collaboration stats...")
        
        # Create some sessions
        for i in range(3):
            self.orchestrator.start_collaboration(
                task_id=f"stats-test-{i}",
                task_description=f"Test {i}"
            )
        
        stats = self.orchestrator.get_collaboration_stats()
        
        assert 'total_sessions' in stats
        assert 'active_sessions' in stats
        assert 'total_messages' in stats
        assert stats['total_sessions'] >= 3
        
        print("✓ Collaboration stats test passed")
    
    def test_delegation_chain_creation(self):
        """Test delegation chain is created for complex tasks"""
        print("Testing delegation chain creation...")
        
        session = self.orchestrator.start_collaboration(
            task_id="chain-test",
            task_description="""
                Complex task requiring multiple specializations:
                - Security audit
                - API implementation
                - Performance testing
                - Documentation
            """
        )
        
        assert session.delegation_chain is not None
        assert session.delegation_chain.root_task_id == "chain-test"
        
        print("✓ Delegation chain creation test passed")
    
    def test_task_context_handling(self):
        """Test task context is properly handled"""
        print("Testing task context handling...")
        
        context = {
            'labels': ['security', 'api'],
            'priority': 'high',
            'requester': 'user-1'
        }
        
        session = self.orchestrator.start_collaboration(
            task_id="context-test",
            task_description="Test with context",
            task_context=context
        )
        
        assert session.metadata.get('task_context') == context
        
        print("✓ Task context handling test passed")
    
    def run_all_tests(self):
        """Run all tests"""
        tests = [
            self.test_orchestrator_initialization,
            self.test_start_collaboration_simple,
            self.test_start_collaboration_complex,
            self.test_session_persistence,
            self.test_progress_tracking,
            self.test_message_sending,
            self.test_help_request,
            self.test_blocked_report,
            self.test_review_request,
            self.test_subtask_completion,
            self.test_collaboration_completion,
            self.test_session_summary,
            self.test_pending_messages,
            self.test_message_read_tracking,
            self.test_list_active_sessions,
            self.test_collaboration_stats,
            self.test_delegation_chain_creation,
            self.test_task_context_handling,
        ]
        
        print("\n" + "=" * 60)
        print("Running Collaborative Agent Orchestrator Tests")
        print("=" * 60 + "\n")
        
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
        
        print("\n" + "=" * 60)
        print(f"Test Results: {passed} passed, {failed} failed")
        print("=" * 60 + "\n")
        
        return failed == 0


def main():
    """Run tests"""
    test_suite = TestCollaborativeAgentOrchestrator()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
