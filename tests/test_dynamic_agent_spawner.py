#!/usr/bin/env python3
"""
Tests for dynamic agent spawner

Tests agent proposal creation, definition generation, and spawning logic.
"""

import unittest
import sys
import os
import tempfile
import shutil
import importlib.util
from pathlib import Path

# Load module with hyphens in filename
tools_dir = os.path.join(os.path.dirname(__file__), '..', 'tools')
spec = importlib.util.spec_from_file_location('spawner', os.path.join(tools_dir, 'dynamic-agent-spawner.py'))
spawner_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(spawner_module)

DynamicAgentSpawner = spawner_module.DynamicAgentSpawner
AgentProposal = spawner_module.AgentProposal


class TestDynamicAgentSpawner(unittest.TestCase):
    """Test cases for dynamic agent spawner"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.agents_dir = Path(self.test_dir) / 'agents'
        self.agents_dir.mkdir()
        self.tracking_file = Path(self.test_dir) / 'spawned.json'
        
        self.spawner = DynamicAgentSpawner(
            agents_dir=str(self.agents_dir),
            spawn_threshold=50.0,
            tracking_file=str(self.tracking_file)
        )
    
    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir)
    
    def test_generate_agent_id(self):
        """Test agent ID generation"""
        # Normal theme
        agent_id = self.spawner._generate_agent_id('ai-agents')
        self.assertEqual(agent_id, 'ai-agents')
        
        # Theme with special characters
        agent_id = self.spawner._generate_agent_id('AI/ML Integration')
        self.assertNotIn('/', agent_id)
        self.assertNotIn(' ', agent_id)
        
        # Check uniqueness handling
        self.spawner.existing_agents.append('test-theme')
        agent_id = self.spawner._generate_agent_id('test-theme')
        self.assertNotEqual(agent_id, 'test-theme')
        self.assertTrue(agent_id.startswith('test-theme'))
    
    def test_create_proposal_valid_theme(self):
        """Test creating a valid agent proposal"""
        trend_data = {
            'mention_count': 10,
            'momentum': 0.7,
            'keywords': ['ai', 'agents'],
            'sample_titles': ['Title 1', 'Title 2']
        }
        
        proposal = self.spawner.create_proposal('ai-agents', trend_data)
        
        self.assertIsNotNone(proposal)
        self.assertIsInstance(proposal, AgentProposal)
        self.assertEqual(proposal.theme, 'ai-agents')
        self.assertGreater(proposal.score, 0)
        self.assertIn('Agent Orchestrator', proposal.agent_name)
    
    def test_create_proposal_existing_agent(self):
        """Test that proposal is not created for existing agent"""
        self.spawner.existing_agents.append('ai-agents')
        
        trend_data = {
            'mention_count': 10,
            'momentum': 0.7,
            'keywords': ['ai', 'agents']
        }
        
        proposal = self.spawner.create_proposal('ai-agents', trend_data)
        
        self.assertIsNone(proposal)
    
    def test_create_proposal_custom_theme(self):
        """Test creating proposal for custom theme"""
        trend_data = {
            'mention_count': 8,
            'momentum': 0.5,
            'keywords': ['custom', 'tech']
        }
        
        proposal = self.spawner.create_proposal('custom-theme', trend_data)
        
        self.assertIsNotNone(proposal)
        self.assertIn('Specialist', proposal.agent_name)
    
    def test_generate_specialization(self):
        """Test specialization text generation"""
        spec = self.spawner._generate_specialization('ai-agents')
        self.assertIn('agent', spec.lower())
        
        spec = self.spawner._generate_specialization('security-automation')
        self.assertIn('security', spec.lower())
        
        # Unknown theme should get default
        spec = self.spawner._generate_specialization('unknown-theme')
        self.assertIn('unknown theme', spec.lower())
    
    def test_build_justification(self):
        """Test justification text building"""
        trend_data = {
            'mention_count': 10,
            'momentum': 0.6,
            'sample_titles': ['Title 1', 'Title 2', 'Title 3']
        }
        
        justification = self.spawner._build_justification('ai-agents', trend_data)
        
        self.assertIn('10 times', justification)
        self.assertIn('0.60', justification)
        self.assertIn('Title 1', justification)
    
    def test_generate_agent_definition(self):
        """Test agent definition file generation"""
        proposal = AgentProposal(
            agent_name='Test Agent',
            agent_id='test-agent',
            theme='test-theme',
            description='A test agent',
            specialization='Testing',
            tools=['view', 'edit', 'bash'],
            personality='focused',
            inspiration='Ada Lovelace',
            justification='Test justification',
            keywords=['test'],
            score=75.0
        )
        
        definition = self.spawner.generate_agent_definition(proposal)
        
        # Check structure
        self.assertIn('---', definition)
        self.assertIn('name: test-agent', definition)
        self.assertIn('Test Agent', definition)
        self.assertIn('view', definition)
        self.assertIn('edit', definition)
        self.assertIn('bash', definition)
        self.assertIn('Ada Lovelace', definition)
        
        # Check sections
        self.assertIn('## Core Responsibilities', definition)
        self.assertIn('## Approach', definition)
        self.assertIn('## Code Quality Standards', definition)
        self.assertIn('## Performance Tracking', definition)
    
    def test_emoji_for_theme(self):
        """Test emoji selection for themes"""
        emoji = self.spawner._emoji_for_theme('ai-agents')
        self.assertEqual(emoji, '🤖')
        
        emoji = self.spawner._emoji_for_theme('rust-specialist')
        self.assertEqual(emoji, '🦀')
        
        # Unknown theme gets default
        emoji = self.spawner._emoji_for_theme('unknown')
        self.assertEqual(emoji, '⚡')
    
    def test_generate_responsibilities(self):
        """Test responsibility generation"""
        # Known theme
        resp = self.spawner._generate_responsibilities('ai-agents')
        self.assertGreater(len(resp), 0)
        self.assertTrue(any('Agent Design' in r for r in resp))
        
        # Unknown theme gets default
        resp = self.spawner._generate_responsibilities('unknown-theme')
        self.assertGreater(len(resp), 0)
        self.assertTrue(any('Implementation' in r for r in resp))
    
    def test_spawn_agent_dry_run(self):
        """Test spawning agent in dry-run mode"""
        proposal = AgentProposal(
            agent_name='Test Agent',
            agent_id='test-agent',
            theme='test-theme',
            description='A test agent',
            specialization='Testing',
            tools=['view', 'edit'],
            personality='focused',
            inspiration='Ada Lovelace',
            justification='Test',
            keywords=['test'],
            score=80.0
        )
        
        result = self.spawner.spawn_agent(proposal, dry_run=True)
        
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['agent_id'], 'test-agent')
        self.assertIsNotNone(result['agent_file'])
        self.assertIsNotNone(result['agent_content_preview'])
        
        # File should not exist
        agent_file = Path(result['agent_file'])
        self.assertFalse(agent_file.exists())
    
    def test_spawn_agent_real(self):
        """Test actually spawning an agent"""
        proposal = AgentProposal(
            agent_name='Test Agent',
            agent_id='test-agent',
            theme='test-theme',
            description='A test agent',
            specialization='Testing',
            tools=['view', 'edit'],
            personality='focused',
            inspiration='Ada Lovelace',
            justification='Test',
            keywords=['test'],
            score=80.0
        )
        
        result = self.spawner.spawn_agent(proposal, dry_run=False)
        
        self.assertTrue(result['success'])
        self.assertFalse(result['dry_run'])
        
        # File should exist
        agent_file = Path(result['agent_file'])
        self.assertTrue(agent_file.exists())
        
        # Check file content
        content = agent_file.read_text()
        self.assertIn('Test Agent', content)
        self.assertIn('test-agent', content)
        
        # Check tracking
        self.assertIn('test-theme', self.spawner.spawned_agents['spawned'])
    
    def test_generate_github_issue_body(self):
        """Test GitHub issue body generation"""
        proposal = AgentProposal(
            agent_name='Test Agent',
            agent_id='test-agent',
            theme='test-theme',
            description='A test agent',
            specialization='Testing',
            tools=['view', 'edit'],
            personality='focused',
            inspiration='Ada Lovelace',
            justification='Test justification here',
            keywords=['test', 'keyword'],
            score=85.0
        )
        
        body = self.spawner.generate_github_issue_body(proposal)
        
        self.assertIn('Test Agent', body)
        self.assertIn('test-theme', body)
        self.assertIn('85.0', body)
        self.assertIn('Test justification here', body)
        self.assertIn('Ada Lovelace', body)
        self.assertIn('test, keyword', body)
    
    def test_evaluate_themes_above_threshold(self):
        """Test evaluating themes with scores above threshold"""
        themes = ['ai-agents', 'llm-specialist']
        trend_data = {
            'mention_count': 15,
            'momentum': 0.8
        }
        
        proposals = self.spawner.evaluate_themes(themes, trend_data)
        
        # Should create proposals for both themes
        self.assertGreater(len(proposals), 0)
        
        # Check sorting by score
        if len(proposals) > 1:
            for i in range(len(proposals) - 1):
                self.assertGreaterEqual(proposals[i].score, proposals[i + 1].score)
    
    def test_evaluate_themes_below_threshold(self):
        """Test evaluating themes with scores below threshold"""
        self.spawner.spawn_threshold = 100.0  # High threshold
        
        themes = ['ai-agents']
        trend_data = {
            'mention_count': 1,
            'momentum': 0.1
        }
        
        proposals = self.spawner.evaluate_themes(themes, trend_data)
        
        # Should not create proposals
        self.assertEqual(len(proposals), 0)
    
    def test_tracking_persistence(self):
        """Test that spawned agents are tracked persistently"""
        proposal = AgentProposal(
            agent_name='Test Agent',
            agent_id='test-agent',
            theme='test-theme',
            description='A test agent',
            specialization='Testing',
            tools=['view'],
            personality='focused',
            inspiration='Ada Lovelace',
            justification='Test',
            keywords=['test'],
            score=80.0
        )
        
        # Spawn agent
        self.spawner.spawn_agent(proposal, dry_run=False)
        
        # Create new spawner instance
        new_spawner = DynamicAgentSpawner(
            agents_dir=str(self.agents_dir),
            tracking_file=str(self.tracking_file)
        )
        
        # Should have loaded tracking data
        self.assertIn('test-theme', new_spawner.spawned_agents['spawned'])


class TestAgentProposal(unittest.TestCase):
    """Test AgentProposal dataclass"""
    
    def test_agent_proposal_creation(self):
        """Test creating an AgentProposal instance"""
        proposal = AgentProposal(
            agent_name='Test Agent',
            agent_id='test-agent',
            theme='test-theme',
            description='A test agent',
            specialization='Testing',
            tools=['view', 'edit'],
            personality='focused',
            inspiration='Ada Lovelace',
            justification='Test justification',
            keywords=['test', 'agent'],
            score=75.5
        )
        
        self.assertEqual(proposal.agent_name, 'Test Agent')
        self.assertEqual(proposal.agent_id, 'test-agent')
        self.assertEqual(proposal.score, 75.5)
        self.assertIn('view', proposal.tools)


def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
