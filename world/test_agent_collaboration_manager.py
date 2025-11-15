#!/usr/bin/env python3
"""
Test suite for Agent Collaboration Manager

Tests collaboration request creation, helper matching, status tracking,
and outcome recording.

Created by: @coordinate-wizard
Date: 2025-11-15
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from agent_collaboration_manager import (
    AgentCollaborationManager,
    CollaborationRequest,
    CollaborationOutcome,
    CollaborationType,
    CollaborationStatus
)


class TestAgentCollaborationManager(unittest.TestCase):
    """Test cases for Agent Collaboration Manager."""
    
    def setUp(self):
        """Set up test environment."""
        # Use temporary file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, 'test_collaborations.json')
        self.manager = AgentCollaborationManager(data_path=self.data_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.data_path):
            os.remove(self.data_path)
        os.rmdir(self.temp_dir)
    
    def test_create_request(self):
        """Test creating a collaboration request."""
        request = self.manager.create_request(
            requester="test-agent-1",
            collaboration_type=CollaborationType.CONSULTATION,
            topic="Test Topic",
            description="Test description",
            learning_category="Programming",
            priority=0.8
        )
        
        self.assertIsNotNone(request)
        self.assertEqual(request.requester, "test-agent-1")
        self.assertEqual(request.collaboration_type, CollaborationType.CONSULTATION)
        self.assertEqual(request.topic, "Test Topic")
        self.assertEqual(request.status, CollaborationStatus.PENDING)
        self.assertEqual(request.priority, 0.8)
        
        # Verify it's saved
        self.assertIn(request.request_id, self.manager.data['active_requests'])
    
    def test_find_helpers_empty(self):
        """Test finding helpers when no agents available."""
        helpers = self.manager.find_helpers(
            topic="Some Topic",
            learning_category="Programming"
        )
        
        # Should return empty list when no agents in system
        self.assertEqual(len(helpers), 0)
    
    def test_accept_request(self):
        """Test accepting a collaboration request."""
        # Create request
        request = self.manager.create_request(
            requester="test-agent-1",
            collaboration_type=CollaborationType.CODE_REVIEW,
            topic="Review my code",
            description="Please review"
        )
        
        # Accept request
        success = self.manager.accept_request(
            request_id=request.request_id,
            helper="test-agent-2"
        )
        
        self.assertTrue(success)
        
        # Verify status changed
        updated_request = self.manager.data['active_requests'][request.request_id]
        self.assertEqual(updated_request.status, CollaborationStatus.ACCEPTED)
        self.assertEqual(updated_request.helper, "test-agent-2")
        self.assertIsNotNone(updated_request.accepted_at)
    
    def test_accept_request_with_specified_helper(self):
        """Test accepting request when helper is pre-specified."""
        # Create request with specific helper
        request = self.manager.create_request(
            requester="test-agent-1",
            collaboration_type=CollaborationType.DEBUGGING,
            topic="Help debug",
            description="Need help",
            helper="test-agent-2"
        )
        
        # Different agent tries to accept
        success = self.manager.accept_request(
            request_id=request.request_id,
            helper="test-agent-3"
        )
        
        self.assertFalse(success)
        
        # Correct helper accepts
        success = self.manager.accept_request(
            request_id=request.request_id,
            helper="test-agent-2"
        )
        
        self.assertTrue(success)
    
    def test_start_collaboration(self):
        """Test starting a collaboration."""
        # Create and accept request
        request = self.manager.create_request(
            requester="test-agent-1",
            collaboration_type=CollaborationType.PAIR_PROGRAMMING,
            topic="Pair program",
            description="Let's code together"
        )
        
        self.manager.accept_request(request.request_id, "test-agent-2")
        
        # Start collaboration
        success = self.manager.start_collaboration(request.request_id)
        
        self.assertTrue(success)
        
        # Verify status
        updated_request = self.manager.data['active_requests'][request.request_id]
        self.assertEqual(updated_request.status, CollaborationStatus.IN_PROGRESS)
    
    def test_complete_collaboration(self):
        """Test completing a collaboration with outcome."""
        # Create, accept, and start
        request = self.manager.create_request(
            requester="test-agent-1",
            collaboration_type=CollaborationType.KNOWLEDGE_SHARE,
            topic="Teach me",
            description="I want to learn",
            learning_category="Security"
        )
        
        self.manager.accept_request(request.request_id, "test-agent-2")
        self.manager.start_collaboration(request.request_id)
        
        # Create outcome
        outcome = CollaborationOutcome(
            request_id=request.request_id,
            success=True,
            duration_hours=3.5,
            outcome_description="Successfully learned security basics",
            learning_gained="Security best practices",
            value_rating=0.9
        )
        
        # Complete
        success = self.manager.complete_collaboration(request.request_id, outcome)
        
        self.assertTrue(success)
        
        # Verify moved to completed
        self.assertNotIn(request.request_id, self.manager.data['active_requests'])
        self.assertIn(request.request_id, self.manager.data['completed_requests'])
        
        # Verify outcome recorded
        self.assertIn(request.request_id, self.manager.data['outcomes'])
        recorded_outcome = self.manager.data['outcomes'][request.request_id]
        self.assertTrue(recorded_outcome.success)
        self.assertEqual(recorded_outcome.duration_hours, 3.5)
        
        # Verify collaboration graph updated
        self.assertIn("test-agent-2", self.manager.data['collaboration_graph']["test-agent-1"])
        self.assertIn("test-agent-1", self.manager.data['collaboration_graph']["test-agent-2"])
        
        # Verify statistics updated
        stats = self.manager.data['statistics']
        self.assertEqual(stats['total_completed'], 1)
        self.assertEqual(stats['total_successful'], 1)
    
    def test_decline_request(self):
        """Test declining a collaboration request."""
        # Create request with specific helper
        request = self.manager.create_request(
            requester="test-agent-1",
            collaboration_type=CollaborationType.RESEARCH,
            topic="Research topic",
            description="Help me research",
            helper="test-agent-2"
        )
        
        # Decline
        success = self.manager.decline_request(request.request_id, "test-agent-2")
        
        self.assertTrue(success)
        
        # Should move to completed since it was a directed request
        self.assertNotIn(request.request_id, self.manager.data['active_requests'])
        self.assertIn(request.request_id, self.manager.data['completed_requests'])
        
        # Verify status
        declined_request = self.manager.data['completed_requests'][request.request_id]
        self.assertEqual(declined_request.status, CollaborationStatus.DECLINED)
    
    def test_abandon_request(self):
        """Test abandoning a collaboration request."""
        # Create request
        request = self.manager.create_request(
            requester="test-agent-1",
            collaboration_type=CollaborationType.CONSULTATION,
            topic="Need advice",
            description="Some advice needed"
        )
        
        # Abandon
        success = self.manager.abandon_request(request.request_id, "test-agent-1")
        
        self.assertTrue(success)
        
        # Should move to completed
        self.assertNotIn(request.request_id, self.manager.data['active_requests'])
        self.assertIn(request.request_id, self.manager.data['completed_requests'])
        
        # Verify status
        abandoned_request = self.manager.data['completed_requests'][request.request_id]
        self.assertEqual(abandoned_request.status, CollaborationStatus.ABANDONED)
    
    def test_get_active_requests(self):
        """Test getting active requests with filters."""
        # Create multiple requests
        req1 = self.manager.create_request(
            requester="agent-1",
            collaboration_type=CollaborationType.CODE_REVIEW,
            topic="Topic 1",
            description="Desc 1",
            learning_category="Programming"
        )
        
        req2 = self.manager.create_request(
            requester="agent-2",
            collaboration_type=CollaborationType.DEBUGGING,
            topic="Topic 2",
            description="Desc 2",
            learning_category="DevOps"
        )
        
        req3 = self.manager.create_request(
            requester="agent-1",
            collaboration_type=CollaborationType.CODE_REVIEW,
            topic="Topic 3",
            description="Desc 3",
            learning_category="Security"
        )
        
        # Test no filter
        all_requests = self.manager.get_active_requests()
        self.assertEqual(len(all_requests), 3)
        
        # Test agent filter
        agent1_requests = self.manager.get_active_requests(agent="agent-1")
        self.assertEqual(len(agent1_requests), 2)
        
        # Test type filter
        review_requests = self.manager.get_active_requests(
            collaboration_type=CollaborationType.CODE_REVIEW
        )
        self.assertEqual(len(review_requests), 2)
        
        # Test category filter
        programming_requests = self.manager.get_active_requests(
            learning_category="Programming"
        )
        self.assertEqual(len(programming_requests), 1)
    
    def test_get_collaboration_history(self):
        """Test getting collaboration history."""
        # Create and complete a collaboration
        request = self.manager.create_request(
            requester="agent-1",
            collaboration_type=CollaborationType.CONSULTATION,
            topic="Test",
            description="Test"
        )
        
        self.manager.accept_request(request.request_id, "agent-2")
        self.manager.start_collaboration(request.request_id)
        
        outcome = CollaborationOutcome(
            request_id=request.request_id,
            success=True,
            duration_hours=2.0,
            outcome_description="Success"
        )
        
        self.manager.complete_collaboration(request.request_id, outcome)
        
        # Get history for agent-1
        history = self.manager.get_collaboration_history("agent-1")
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0].requester, "agent-1")
        self.assertIsNotNone(history[0][1])
    
    def test_get_collaboration_partners(self):
        """Test getting collaboration partners."""
        # Create and complete collaboration
        request = self.manager.create_request(
            requester="agent-1",
            collaboration_type=CollaborationType.PAIR_PROGRAMMING,
            topic="Test",
            description="Test"
        )
        
        self.manager.accept_request(request.request_id, "agent-2")
        self.manager.start_collaboration(request.request_id)
        
        outcome = CollaborationOutcome(
            request_id=request.request_id,
            success=True,
            duration_hours=1.0,
            outcome_description="Done"
        )
        
        self.manager.complete_collaboration(request.request_id, outcome)
        
        # Get partners
        partners_1 = self.manager.get_collaboration_partners("agent-1")
        partners_2 = self.manager.get_collaboration_partners("agent-2")
        
        self.assertIn("agent-2", partners_1)
        self.assertIn("agent-1", partners_2)
    
    def test_get_statistics(self):
        """Test getting collaboration statistics."""
        # Complete multiple collaborations
        for i in range(3):
            request = self.manager.create_request(
                requester=f"agent-{i}",
                collaboration_type=CollaborationType.CONSULTATION,
                topic=f"Topic {i}",
                description=f"Description {i}"
            )
            
            self.manager.accept_request(request.request_id, "helper-agent")
            self.manager.start_collaboration(request.request_id)
            
            outcome = CollaborationOutcome(
                request_id=request.request_id,
                success=(i < 2),  # First two successful
                duration_hours=float(i + 1),
                outcome_description="Test",
                value_rating=0.8
            )
            
            self.manager.complete_collaboration(request.request_id, outcome)
        
        # Get statistics
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['total_completed'], 3)
        self.assertEqual(stats['total_successful'], 2)
        self.assertAlmostEqual(stats['success_rate'], 2/3, places=2)
        self.assertGreater(stats['average_duration'], 0)
        self.assertEqual(stats['active_requests'], 0)
    
    def test_persistence(self):
        """Test that data persists across manager instances."""
        # Create request
        request = self.manager.create_request(
            requester="test-agent",
            collaboration_type=CollaborationType.KNOWLEDGE_SHARE,
            topic="Test persistence",
            description="Testing"
        )
        
        request_id = request.request_id
        
        # Create new manager instance with same data path
        manager2 = AgentCollaborationManager(data_path=self.data_path)
        
        # Verify data loaded
        self.assertIn(request_id, manager2.data['active_requests'])
        loaded_request = manager2.data['active_requests'][request_id]
        self.assertEqual(loaded_request.requester, "test-agent")
        self.assertEqual(loaded_request.topic, "Test persistence")
    
    def test_collaboration_request_serialization(self):
        """Test CollaborationRequest serialization."""
        request = CollaborationRequest(
            request_id="test-123",
            requester="agent-1",
            collaboration_type=CollaborationType.DEBUGGING,
            topic="Test topic",
            description="Test description",
            helper="agent-2",
            learning_category="Programming"
        )
        
        # Convert to dict
        request_dict = request.to_dict()
        
        # Verify structure
        self.assertEqual(request_dict['request_id'], "test-123")
        self.assertEqual(request_dict['collaboration_type'], "debugging")
        self.assertEqual(request_dict['status'], "pending")
        
        # Convert back
        restored = CollaborationRequest.from_dict(request_dict)
        
        self.assertEqual(restored.request_id, request.request_id)
        self.assertEqual(restored.collaboration_type, request.collaboration_type)
        self.assertEqual(restored.status, request.status)
    
    def test_collaboration_outcome_serialization(self):
        """Test CollaborationOutcome serialization."""
        outcome = CollaborationOutcome(
            request_id="test-123",
            success=True,
            duration_hours=5.5,
            outcome_description="Test outcome",
            value_rating=0.92
        )
        
        # Convert to dict
        outcome_dict = outcome.to_dict()
        
        # Verify structure
        self.assertEqual(outcome_dict['request_id'], "test-123")
        self.assertTrue(outcome_dict['success'])
        self.assertEqual(outcome_dict['duration_hours'], 5.5)
        
        # Convert back
        restored = CollaborationOutcome.from_dict(outcome_dict)
        
        self.assertEqual(restored.request_id, outcome.request_id)
        self.assertEqual(restored.success, outcome.success)
        self.assertEqual(restored.duration_hours, outcome.duration_hours)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
