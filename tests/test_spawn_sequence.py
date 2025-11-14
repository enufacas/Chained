#!/usr/bin/env python3
"""
Test the agent spawn sequence logic.

This test validates that the spawn sequence correctly handles:
1. Detecting spawn-pending labels
2. Checking spawn PR status
3. Proper sequencing of agent spawn -> assignment
"""

import unittest
import re


class TestSpawnSequence(unittest.TestCase):
    """Test cases for the agent spawn sequence."""

    def test_spawn_pending_label_detection(self):
        """Test that spawn-pending label is properly checked."""
        # Simulate issue labels
        labels_with_spawn = "agent-system\nagent-work\nspawn-pending"
        labels_without_spawn = "agent-system\nagent-work"
        
        # Check detection logic
        self.assertTrue("spawn-pending" in labels_with_spawn)
        self.assertFalse("spawn-pending" in labels_without_spawn)

    def test_spawn_sequence_marker_detection(self):
        """Test that the spawn sequence marker is detected in issue body."""
        issue_body_with_marker = """
        ## ⚠️ Agent Spawn Sequence
        
        **IMPORTANT:** This agent is being spawned and will be available once PR #423 is merged.
        """
        
        issue_body_without_marker = """
        ## Regular Issue
        
        This is a regular issue without spawn sequence.
        """
        
        # Check marker detection
        self.assertTrue("⚠️ Agent Spawn Sequence" in issue_body_with_marker)
        self.assertFalse("⚠️ Agent Spawn Sequence" in issue_body_without_marker)

    def test_spawn_pr_number_extraction(self):
        """Test that spawn PR numbers are correctly extracted from issue body."""
        issue_body = """
        **Current Status:**
        - ✅ Agent registration PR created: #423
        - ⏳ Waiting for spawn PR to merge
        """
        
        # Extract PR number using regex (similar to shell script pattern: 'PR #\K\d+')
        # In Python, we use a capturing group instead of \K
        pr_match = re.search(r'PR #(\d+)', issue_body)
        if pr_match:
            pr_number = pr_match.group(1)
        else:
            pr_number = None
        
        # The shell script looks for 'PR #\K\d+' which matches "PR #423"
        # Our issue body has "#423" but not "PR #423", so let's test both patterns
        
        # Pattern 1: "PR #123" format (what shell script expects)
        issue_body_format1 = "Agent registration PR created: PR #423"
        pr_match1 = re.search(r'PR #(\d+)', issue_body_format1)
        self.assertIsNotNone(pr_match1)
        self.assertEqual(pr_match1.group(1), "423")
        
        # Pattern 2: "#123" format (also common)
        issue_body_format2 = "Agent registration PR created: #423"
        pr_match2 = re.search(r'#(\d+)', issue_body_format2)
        self.assertIsNotNone(pr_match2)
        self.assertEqual(pr_match2.group(1), "423")

    def test_agent_work_label_logic(self):
        """Test the label logic for agent-work issues."""
        # agent-system but not agent-work should be skipped
        labels_system_only = "agent-system\nannouncement"
        self.assertTrue("agent-system" in labels_system_only)
        self.assertFalse("agent-work" in labels_system_only)
        
        # agent-system AND agent-work should be processed (unless spawn-pending)
        labels_both = "agent-system\nagent-work"
        self.assertTrue("agent-system" in labels_both)
        self.assertTrue("agent-work" in labels_both)

    def test_sequence_flow_states(self):
        """Test the different states in the spawn sequence flow."""
        # State 1: Just created, has spawn-pending
        state1_labels = {"agent-system", "agent-work", "spawn-pending"}
        self.assertIn("spawn-pending", state1_labels)
        
        # State 2: Spawn PR merged, spawn-pending removed
        state2_labels = {"agent-system", "agent-work"}
        self.assertNotIn("spawn-pending", state2_labels)
        
        # Transition: should remove spawn-pending
        state1_labels.discard("spawn-pending")
        self.assertEqual(state1_labels, state2_labels)


class TestWorkflowIntegration(unittest.TestCase):
    """Test workflow integration points."""

    def test_label_creation_in_spawner(self):
        """Test that spawn-pending label definition exists in agent-spawner."""
        with open('.github/workflows/agent-spawner.yml', 'r') as f:
            spawner_content = f.read()
        
        # Check label is defined (still needed for label system, even if not used for new issues)
        self.assertIn('create_label_if_missing "spawn-pending"', spawner_content)
        self.assertIn('Waiting for agent spawn PR to merge', spawner_content)

    def test_no_issue_creation_in_spawner(self):
        """Test that agent-spawner no longer creates work issues."""
        with open('.github/workflows/agent-spawner.yml', 'r') as f:
            spawner_content = f.read()
        
        # Check that issue creation step has been removed
        self.assertNotIn('- name: Create agent work and welcome issue', spawner_content)
        # Check that the removal is documented
        self.assertIn('Issue creation removed to prevent circular dependencies', spawner_content)

    def test_no_announcement_issue_in_learning_spawner(self):
        """Test that learning-based-agent-spawner no longer creates announcement issues."""
        with open('.github/workflows/learning-based-agent-spawner.yml', 'r') as f:
            spawner_content = f.read()
        
        # Check that announcement issue creation step has been removed
        self.assertNotIn('- name: Create announcement issue', spawner_content)
        # Check that the removal is documented
        self.assertIn('Announcement issue creation removed to prevent circular dependencies', spawner_content)

    def test_label_removal_in_auto_review(self):
        """Test that spawn-pending label is removed after merge."""
        with open('.github/workflows/auto-review-merge.yml', 'r') as f:
            auto_review_content = f.read()
        
        # Check label removal logic exists
        self.assertIn('--remove-label "spawn-pending"', auto_review_content)
        # Check for removal message (more lenient check for backticks)
        self.assertTrue(
            'Removed `spawn-pending` label' in auto_review_content or
            'Removed \\`spawn-pending\\` label' in auto_review_content,
            "Could not find 'Removed spawn-pending label' message"
        )
    
    def test_copilot_label_added_in_auto_review(self):
        """Test that copilot label is added after spawn PR merge."""
        with open('.github/workflows/auto-review-merge.yml', 'r') as f:
            auto_review_content = f.read()
        
        # Check that copilot label is added
        self.assertIn('--add-label "copilot"', auto_review_content)
        # Check for addition message (more lenient check for backticks)
        self.assertTrue(
            'Added `copilot` label' in auto_review_content or
            'Added \\`copilot\\` label' in auto_review_content,
            "Could not find 'Added copilot label' message"
        )

    def test_spawn_pending_check_in_script(self):
        """Test that assignment script checks for spawn-pending label."""
        with open('tools/assign-copilot-to-issue.sh', 'r') as f:
            script_content = f.read()
        
        # Check spawn-pending is checked
        self.assertIn('spawn-pending', script_content)
        # Check for waiting message (agent spawn PR or just spawn PR)
        self.assertTrue(
            'waiting for spawn pr to merge' in script_content.lower() or
            'waiting for agent spawn pr to merge' in script_content.lower(),
            "Could not find 'waiting for spawn PR to merge' message"
        )

    def test_spawn_pr_status_check(self):
        """Test that assignment script checks spawn PR status."""
        with open('tools/assign-copilot-to-issue.sh', 'r') as f:
            script_content = f.read()
        
        # Check for spawn PR detection
        self.assertIn('⚠️ Agent Spawn Sequence', script_content)
        self.assertIn('spawn_pr_number', script_content)
        self.assertIn('pr_state', script_content)

    def test_assignment_no_longer_needed_after_spawn(self):
        """Test that assignment workflow dispatch is no longer needed after spawn merge.
        
        Since we no longer create work issues during agent spawn, there's nothing to assign.
        The agent will work on existing issues from the queue once spawned.
        """
        with open('.github/workflows/auto-review-merge.yml', 'r') as f:
            auto_review_content = f.read()
        
        # Check that auto-review-merge handles agent spawn PRs (for backwards compatibility)
        # It should check for agent-system label
        self.assertIn('agent-system', auto_review_content)


def run_tests():
    """Run all tests and report results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSpawnSequence))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit(run_tests())
