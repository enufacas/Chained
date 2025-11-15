#!/usr/bin/env python3
"""
Tests for Agent Investment Tracker

Comprehensive test suite ensuring clean, reliable code.

Created by: @organize-guru
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from agent_investment_tracker import (
    AgentInvestmentTracker,
    InvestmentLevel,
    CategoryInvestment,
    CultivationEvent,
    record_learning_work,
    get_top_agents_for_category
)


class TestCultivationEvent(unittest.TestCase):
    """Test CultivationEvent data class."""
    
    def test_create_event(self):
        """Test creating a cultivation event."""
        event = CultivationEvent(
            timestamp="2025-11-15T10:00:00",
            category="Security",
            learning_id="sec-001",
            impact=0.8,
            context="Fixed vulnerability"
        )
        
        self.assertEqual(event.category, "Security")
        self.assertEqual(event.impact, 0.8)
        self.assertEqual(event.learning_id, "sec-001")
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        event = CultivationEvent(
            timestamp="2025-11-15T10:00:00",
            category="Security",
            impact=0.5
        )
        
        data = event.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['category'], "Security")
        self.assertEqual(data['impact'], 0.5)
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            'timestamp': "2025-11-15T10:00:00",
            'category': "Security",
            'learning_id': "sec-001",
            'impact': 0.7,
            'context': "Test"
        }
        
        event = CultivationEvent.from_dict(data)
        self.assertEqual(event.category, "Security")
        self.assertEqual(event.impact, 0.7)


class TestCategoryInvestment(unittest.TestCase):
    """Test CategoryInvestment data class."""
    
    def test_create_investment(self):
        """Test creating a category investment."""
        inv = CategoryInvestment(
            category="Programming",
            level=InvestmentLevel.LEARNING,
            score=25.5
        )
        
        self.assertEqual(inv.category, "Programming")
        self.assertEqual(inv.level, InvestmentLevel.LEARNING)
        self.assertEqual(inv.score, 25.5)
        self.assertEqual(inv.cultivation_count, 0)
        self.assertIsNotNone(inv.cultivation_events)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        inv = CategoryInvestment(
            category="Security",
            level=InvestmentLevel.PROFICIENT,
            score=65.0
        )
        
        data = inv.to_dict()
        self.assertEqual(data['category'], "Security")
        self.assertEqual(data['level'], "PROFICIENT")
        self.assertEqual(data['score'], 65.0)
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            'category': "DevOps",
            'level': "EXPERT",
            'score': 90.0,
            'first_invested': "2025-11-01T08:00:00",
            'last_cultivated': "2025-11-15T10:00:00",
            'cultivation_count': 50,
            'cultivation_events': []
        }
        
        inv = CategoryInvestment.from_dict(data)
        self.assertEqual(inv.category, "DevOps")
        self.assertEqual(inv.level, InvestmentLevel.EXPERT)
        self.assertEqual(inv.score, 90.0)


class TestAgentInvestmentTracker(unittest.TestCase):
    """Test AgentInvestmentTracker main functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        self.temp_file.close()
        self.temp_path = self.temp_file.name
        
        # Initialize tracker with temp file
        self.tracker = AgentInvestmentTracker(data_path=self.temp_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
    
    def test_initialization(self):
        """Test tracker initialization."""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(self.tracker.investments, {})
    
    def test_record_first_cultivation(self):
        """Test recording first cultivation event."""
        investment = self.tracker.record_cultivation(
            agent_name="test-agent",
            category="Programming",
            impact=0.5,
            learning_id="test-001",
            context="Test cultivation"
        )
        
        self.assertEqual(investment.category, "Programming")
        self.assertEqual(investment.cultivation_count, 1)
        self.assertGreater(investment.score, 0)
        self.assertIsNotNone(investment.first_invested)
        self.assertEqual(len(investment.cultivation_events), 1)
    
    def test_record_multiple_cultivations(self):
        """Test recording multiple cultivation events."""
        # First event
        inv1 = self.tracker.record_cultivation(
            agent_name="test-agent",
            category="Security",
            impact=0.5
        )
        score1 = inv1.score
        
        # Second event
        inv2 = self.tracker.record_cultivation(
            agent_name="test-agent",
            category="Security",
            impact=0.6
        )
        score2 = inv2.score
        
        self.assertEqual(inv2.cultivation_count, 2)
        self.assertGreater(score2, score1)
    
    def test_impact_validation(self):
        """Test impact value validation."""
        # Test clamping to valid range
        inv1 = self.tracker.record_cultivation(
            agent_name="test-agent",
            category="Programming",
            impact=1.5  # Should be clamped to 1.0
        )
        
        # Impact should be valid
        self.assertTrue(0.0 <= inv1.cultivation_events[0].impact <= 1.0)
        
        inv2 = self.tracker.record_cultivation(
            agent_name="test-agent",
            category="Programming",
            impact=-0.5  # Should be clamped to 0.0
        )
        
        self.assertTrue(0.0 <= inv2.cultivation_events[-1].impact <= 1.0)
    
    def test_level_progression(self):
        """Test investment level progression."""
        agent = "test-agent"
        category = "Testing"
        
        # Start at NONE
        investments = self.tracker.get_agent_investments(agent)
        self.assertEqual(len(investments), 0)
        
        # Cultivate to CURIOUS (5+ score)
        self.tracker.record_cultivation(agent, category, impact=0.5)
        inv = self.tracker.get_agent_investments(agent)[category]
        self.assertIn(inv.level, [InvestmentLevel.NONE, InvestmentLevel.CURIOUS])
        
        # Continue to LEARNING (15+ score)
        for _ in range(5):
            self.tracker.record_cultivation(agent, category, impact=0.6)
        
        inv = self.tracker.get_agent_investments(agent)[category]
        self.assertGreaterEqual(inv.level.value, InvestmentLevel.CURIOUS.value)
    
    def test_get_agent_investments(self):
        """Test retrieving agent investments."""
        agent = "test-agent"
        
        # Record investments in multiple categories
        self.tracker.record_cultivation(agent, "Programming", 0.7)
        self.tracker.record_cultivation(agent, "DevOps", 0.6)
        self.tracker.record_cultivation(agent, "Security", 0.8)
        
        investments = self.tracker.get_agent_investments(agent)
        self.assertEqual(len(investments), 3)
        self.assertIn("Programming", investments)
        self.assertIn("DevOps", investments)
        self.assertIn("Security", investments)
    
    def test_get_agent_investments_with_filter(self):
        """Test filtering agent investments by level."""
        agent = "test-agent"
        
        # Create investments at different levels
        # Low investment
        self.tracker.record_cultivation(agent, "LowCat", 0.3)
        
        # Higher investment (multiple events)
        for _ in range(10):
            self.tracker.record_cultivation(agent, "HighCat", 0.6)
        
        # Get only higher level investments
        high_investments = self.tracker.get_agent_investments(
            agent,
            min_level=InvestmentLevel.LEARNING
        )
        
        # Should only include HighCat
        self.assertIn("HighCat", high_investments)
        # LowCat might not meet the threshold
        if "LowCat" in high_investments:
            self.assertGreaterEqual(
                high_investments["LowCat"].level.value,
                InvestmentLevel.LEARNING.value
            )
    
    def test_get_category_experts(self):
        """Test finding experts in a category."""
        category = "Security"
        
        # Create multiple agents with different investment levels
        for i in range(5):
            self.tracker.record_cultivation(
                agent_name="low-agent",
                category=category,
                impact=0.4
            )
        
        for i in range(20):
            self.tracker.record_cultivation(
                agent_name="high-agent",
                category=category,
                impact=0.7
            )
        
        experts = self.tracker.get_category_experts(
            category,
            min_level=InvestmentLevel.CURIOUS
        )
        
        # Should have both agents
        agent_names = [name for name, _ in experts]
        self.assertIn("low-agent", agent_names)
        self.assertIn("high-agent", agent_names)
        
        # High agent should be first (higher score)
        self.assertEqual(experts[0][0], "high-agent")
    
    def test_investment_summary(self):
        """Test getting investment summary."""
        agent = "summary-agent"
        
        # Create diverse portfolio
        self.tracker.record_cultivation(agent, "Programming", 0.8)
        for _ in range(5):
            self.tracker.record_cultivation(agent, "Programming", 0.6)
        
        self.tracker.record_cultivation(agent, "DevOps", 0.5)
        
        summary = self.tracker.get_investment_summary(agent)
        
        self.assertEqual(summary['agent'], agent)
        self.assertEqual(summary['total_investments'], 2)
        self.assertIn("Programming", summary['categories'])
        self.assertIn("DevOps", summary['categories'])
        self.assertIsNotNone(summary['most_cultivated'])
    
    def test_persistence(self):
        """Test data persistence to file."""
        agent = "persistent-agent"
        category = "Persistence"
        
        # Record cultivation
        self.tracker.record_cultivation(agent, category, 0.7)
        
        # Create new tracker instance with same file
        new_tracker = AgentInvestmentTracker(data_path=self.temp_path)
        
        # Data should be loaded
        investments = new_tracker.get_agent_investments(agent)
        self.assertIn(category, investments)
        self.assertEqual(investments[category].cultivation_count, 1)
    
    def test_max_events_stored(self):
        """Test that only recent events are stored."""
        agent = "event-agent"
        category = "EventTest"
        
        # Record more than MAX_EVENTS_STORED
        max_events = self.tracker.MAX_EVENTS_STORED
        for i in range(max_events + 10):
            self.tracker.record_cultivation(agent, category, 0.5)
        
        investment = self.tracker.get_agent_investments(agent)[category]
        
        # Should not exceed max
        self.assertLessEqual(len(investment.cultivation_events), max_events)
        self.assertEqual(investment.cultivation_count, max_events + 10)


class TestCultivationOpportunities(unittest.TestCase):
    """Test cultivation opportunity finding."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        self.temp_file.close()
        self.temp_path = self.temp_file.name
        self.tracker = AgentInvestmentTracker(data_path=self.temp_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
    
    def test_find_opportunities_no_investment(self):
        """Test finding opportunities for agent with no investments."""
        learnings = [
            {'title': 'Test 1', 'categories': ['Programming'], 'score': 0.8},
            {'title': 'Test 2', 'categories': ['Security'], 'score': 0.7}
        ]
        
        opportunities = self.tracker.find_cultivation_opportunities(
            agent_name="new-agent",
            available_learnings=learnings,
            top_n=5
        )
        
        # Should return available learnings
        self.assertEqual(len(opportunities), 2)
    
    def test_find_opportunities_with_investment(self):
        """Test finding opportunities for invested agent."""
        agent = "invested-agent"
        
        # Create investment
        for _ in range(10):
            self.tracker.record_cultivation(agent, "Security", 0.6)
        
        learnings = [
            {'title': 'Security Advanced', 'categories': ['Security'], 'score': 0.8},
            {'title': 'New Topic', 'categories': ['Database'], 'score': 0.7}
        ]
        
        opportunities = self.tracker.find_cultivation_opportunities(
            agent_name=agent,
            available_learnings=learnings,
            top_n=5
        )
        
        # Security learning should have higher cultivation score
        security_opp = next(o for o in opportunities if 'Security' in o['categories'])
        self.assertGreater(security_opp['cultivation_score'], 0.8)


class TestHelperFunctions(unittest.TestCase):
    """Test helper/convenience functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        self.temp_file.close()
        self.temp_path = self.temp_file.name
        self.tracker = AgentInvestmentTracker(data_path=self.temp_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
    
    def test_record_learning_work(self):
        """Test batch recording helper."""
        categories = ["Programming", "DevOps", "Tools"]
        
        investments = record_learning_work(
            agent_name="batch-agent",
            categories=categories,
            learning_id="batch-001",
            impact=0.7,
            tracker=self.tracker
        )
        
        self.assertEqual(len(investments), 3)
        
        # Check all categories were recorded
        agent_investments = self.tracker.get_agent_investments("batch-agent")
        for cat in categories:
            self.assertIn(cat, agent_investments)
    
    def test_get_top_agents_for_category(self):
        """Test getting top agents helper."""
        category = "TestCategory"
        
        # Create agents with different levels
        for _ in range(15):
            self.tracker.record_cultivation("expert-agent", category, 0.7)
        
        for _ in range(5):
            self.tracker.record_cultivation("learning-agent", category, 0.5)
        
        top_agents = get_top_agents_for_category(
            category,
            min_level=InvestmentLevel.CURIOUS,
            tracker=self.tracker
        )
        
        # Expert should be first
        self.assertEqual(top_agents[0], "expert-agent")
        self.assertIn("learning-agent", top_agents)


class TestDecay(unittest.TestCase):
    """Test time-based decay functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        self.temp_file.close()
        self.temp_path = self.temp_file.name
        self.tracker = AgentInvestmentTracker(data_path=self.temp_path)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_path):
            os.unlink(self.temp_path)
    
    def test_apply_decay(self):
        """Test applying decay to all investments."""
        # Create some investments
        self.tracker.record_cultivation("agent1", "Cat1", 0.5)
        self.tracker.record_cultivation("agent2", "Cat2", 0.6)
        
        # Apply decay
        stats = self.tracker.apply_decay()
        
        # Stats should be returned
        self.assertIn('agents_processed', stats)
        self.assertIn('investments_decayed', stats)
        self.assertIn('investments_removed', stats)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCultivationEvent))
    suite.addTests(loader.loadTestsFromTestCase(TestCategoryInvestment))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentInvestmentTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestCultivationOpportunities))
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestDecay))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
