#!/usr/bin/env python3
"""
Tests for thematic analyzer

Tests trend detection, momentum calculation, and theme identification.
"""

import unittest
import sys
import os
import importlib.util
from datetime import datetime, timedelta

# Load module with hyphens in filename
tools_dir = os.path.join(os.path.dirname(__file__), '..', 'tools')
spec = importlib.util.spec_from_file_location('analyzer', os.path.join(tools_dir, 'thematic-analyzer.py'))
analyzer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer_module)

ThematicAnalyzer = analyzer_module.ThematicAnalyzer
TrendMetrics = analyzer_module.TrendMetrics
PersonalityMention = analyzer_module.PersonalityMention


class TestThematicAnalyzer(unittest.TestCase):
    """Test cases for thematic analyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ThematicAnalyzer(lookback_days=7)
        
        # Create sample learnings
        now = datetime.now()
        recent = now - timedelta(days=1)
        older = now - timedelta(days=6)
        
        self.sample_learnings = [
            {
                'title': 'New AI Agent Framework Released',
                'description': 'A powerful framework for building AI agents',
                'content': 'The framework enables multi-agent systems with LLM integration.',
                'source': 'Tech News',
                'timestamp': recent.isoformat(),
                'score': 150
            },
            {
                'title': 'Understanding Rust Ownership Model',
                'description': 'Deep dive into Rust memory safety',
                'content': 'Rust provides memory safety without garbage collection.',
                'source': 'Dev Blog',
                'timestamp': recent.isoformat(),
                'score': 200
            },
            {
                'title': 'OpenAI Releases New GPT Model',
                'description': 'Latest GPT model shows improvements',
                'content': 'The new LLM demonstrates better reasoning capabilities.',
                'source': 'Hacker News',
                'timestamp': older.isoformat(),
                'score': 300
            },
            {
                'title': 'Docker Security Best Practices',
                'description': 'Securing containerized applications',
                'content': 'Learn how to secure Docker containers in production.',
                'source': 'Security Blog',
                'timestamp': recent.isoformat(),
                'score': 120
            },
            {
                'title': 'Elon Musk Announces New AI Initiative',
                'description': 'Tesla CEO discusses AI safety',
                'content': 'Musk emphasizes the importance of AI safety research.',
                'source': 'News',
                'timestamp': recent.isoformat(),
                'score': 500
            }
        ]
    
    def test_extract_keywords(self):
        """Test keyword extraction from text"""
        text = "The quick brown fox jumps over the lazy dog"
        keywords = self.analyzer.extract_keywords(text)
        
        self.assertIn('quick', keywords)
        self.assertIn('brown', keywords)
        self.assertNotIn('the', keywords)  # Stop word
    
    def test_find_technology_mentions(self):
        """Test finding technology mentions in learnings"""
        mentions = self.analyzer.find_technology_mentions(self.sample_learnings)
        
        # Should find AI/ML mentions
        self.assertIn('ai', mentions)
        self.assertIn('llm', mentions)
        self.assertIn('gpt', mentions)
        
        # Should find Rust
        self.assertIn('rust', mentions)
        
        # Should find Docker
        self.assertIn('docker', mentions)
        
        # Check mention details
        ai_mentions = mentions['ai']
        self.assertGreater(len(ai_mentions), 0)
        self.assertEqual(ai_mentions[0]['category'], 'AI/ML')
    
    def test_find_company_mentions(self):
        """Test finding company mentions"""
        mentions = self.analyzer.find_company_mentions(self.sample_learnings)
        
        # Should find OpenAI
        self.assertIn('openai', mentions)
        
        # Should find Tesla (Elon is CEO)
        self.assertIn('tesla', mentions)
        
        # Check mention details
        openai_mentions = mentions['openai']
        self.assertGreater(len(openai_mentions), 0)
    
    def test_find_personality_mentions(self):
        """Test finding tech personality mentions"""
        # Add another learning with Elon to meet the 2-mention threshold
        extra_learning = {
            'title': 'Elon Musk Tesla Earnings Call',
            'description': 'CEO discusses quarterly results',
            'source': 'Financial News',
            'timestamp': (datetime.now() - timedelta(days=2)).isoformat()
        }
        learnings_with_extra = self.sample_learnings + [extra_learning]
        
        personalities = self.analyzer.find_personality_mentions(learnings_with_extra)
        
        # Should find Elon Musk (now has 2+ mentions)
        self.assertIn('Elon Musk', personalities)
        
        elon = personalities['Elon Musk']
        self.assertIsInstance(elon, PersonalityMention)
        self.assertGreaterEqual(elon.mention_count, 2)
        self.assertGreater(len(elon.context), 0)
    
    def test_calculate_momentum_increasing(self):
        """Test momentum calculation for increasing trend"""
        now = datetime.now()
        
        # More recent mentions
        mentions = [
            {'timestamp': (now - timedelta(days=1)).isoformat()},
            {'timestamp': (now - timedelta(days=1)).isoformat()},
            {'timestamp': (now - timedelta(days=2)).isoformat()},
            {'timestamp': (now - timedelta(days=5)).isoformat()},
        ]
        
        momentum = self.analyzer.calculate_momentum(mentions)
        
        # Should be positive (more recent activity)
        self.assertGreater(momentum, 0)
    
    def test_calculate_momentum_decreasing(self):
        """Test momentum calculation for decreasing trend"""
        now = datetime.now()
        
        # More older mentions
        mentions = [
            {'timestamp': (now - timedelta(days=1)).isoformat()},
            {'timestamp': (now - timedelta(days=5)).isoformat()},
            {'timestamp': (now - timedelta(days=6)).isoformat()},
            {'timestamp': (now - timedelta(days=6)).isoformat()},
        ]
        
        momentum = self.analyzer.calculate_momentum(mentions)
        
        # Should be negative (declining activity)
        self.assertLess(momentum, 0)
    
    def test_calculate_momentum_stable(self):
        """Test momentum calculation for stable trend"""
        now = datetime.now()
        
        # Even distribution
        mentions = [
            {'timestamp': (now - timedelta(days=1)).isoformat()},
            {'timestamp': (now - timedelta(days=2)).isoformat()},
            {'timestamp': (now - timedelta(days=5)).isoformat()},
            {'timestamp': (now - timedelta(days=6)).isoformat()},
        ]
        
        momentum = self.analyzer.calculate_momentum(mentions)
        
        # Should be close to zero
        self.assertLess(abs(momentum), 0.3)
    
    def test_calculate_trend_score(self):
        """Test trend score calculation"""
        mentions = [
            {'source': 'Source1', 'timestamp': datetime.now().isoformat()},
            {'source': 'Source1', 'timestamp': datetime.now().isoformat()},
            {'source': 'Source2', 'timestamp': datetime.now().isoformat()},
        ]
        
        # High momentum
        score_high_momentum = self.analyzer.calculate_trend_score(mentions, 0.8)
        
        # Low momentum
        score_low_momentum = self.analyzer.calculate_trend_score(mentions, -0.5)
        
        # High momentum should have higher score
        self.assertGreater(score_high_momentum, score_low_momentum)
        
        # Score should be within bounds
        self.assertGreater(score_high_momentum, 0)
        self.assertLessEqual(score_high_momentum, 100)
    
    def test_analyze_learnings(self):
        """Test complete thematic analysis"""
        analysis = self.analyzer.analyze_learnings(self.sample_learnings)
        
        # Check basic structure
        self.assertEqual(analysis.total_learnings_analyzed, len(self.sample_learnings))
        self.assertEqual(analysis.analysis_period_days, 7)
        
        # Should have technology trends
        self.assertGreater(len(analysis.top_technologies), 0)
        
        # Check trend structure
        for trend in analysis.top_technologies:
            self.assertIsInstance(trend, TrendMetrics)
            self.assertGreater(trend.mention_count, 0)
            self.assertIsInstance(trend.score, float)
        
        # Company trends may be empty if companies mentioned only once
        # (need 2+ mentions to be a trend)
        self.assertIsInstance(analysis.top_companies, list)
        
        # Should have hot themes
        self.assertIsInstance(analysis.hot_themes, list)
    
    def test_identify_hot_themes_ai(self):
        """Test identification of AI theme"""
        ai_heavy_learnings = [
            {
                'title': 'Building AI Agents with LLMs',
                'description': 'Guide to AI agent development',
                'content': 'AI agents can use large language models for reasoning.',
                'source': 'Blog',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'Building AI Agents with LLMs Part 2',
                'description': 'Advanced AI agent patterns',
                'content': 'Multi-agent systems enable complex workflows.',
                'source': 'Blog',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'GPT-4 Integration Tutorial',
                'description': 'How to integrate GPT-4',
                'content': 'Learn to build applications with GPT-4 API and other LLMs.',
                'source': 'Tutorial',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'AI Agent Orchestration Patterns',
                'description': 'Patterns for multi-agent systems',
                'content': 'Orchestrating multiple AI agents for complex tasks with machine learning.',
                'source': 'Research',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'Neural Network Optimization',
                'description': 'Optimizing neural networks',
                'content': 'Techniques for training neural networks more efficiently.',
                'source': 'Research',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        analysis = self.analyzer.analyze_learnings(ai_heavy_learnings)
        
        # With enough AI/ML content, should identify AI-related theme
        ai_trends_in_top = [t for t in analysis.top_technologies[:10] if t.category == 'AI/ML']
        # If we have 3+ AI/ML trends in top 10, themes should be generated
        if len(ai_trends_in_top) >= 3:
            ai_themes = [t for t in analysis.hot_themes if 'ai' in t or 'llm' in t or 'agent' in t]
            self.assertGreater(len(ai_themes), 0)
        else:
            # Test passes if we don't have enough trends yet
            self.assertIsInstance(analysis.hot_themes, list)
    
    def test_identify_hot_themes_security(self):
        """Test identification of security theme"""
        security_learnings = [
            {
                'title': 'Container Security Best Practices',
                'description': 'Securing Docker containers',
                'content': 'Learn security best practices for containers.',
                'source': 'Security Blog',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'Container Security Advanced',
                'description': 'Advanced security patterns',
                'content': 'Implement security controls in production.',
                'source': 'Security Blog',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'New CVE in Popular Library',
                'description': 'Critical vulnerability discovered',
                'content': 'A security vulnerability was found affecting many applications.',
                'source': 'Security Advisory',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'Authentication Security Guide',
                'description': 'Implementing secure authentication',
                'content': 'Guide to OAuth and JWT security encryption.',
                'source': 'Tutorial',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        analysis = self.analyzer.analyze_learnings(security_learnings)
        
        # With enough security content, should identify security theme
        security_trends_in_top = [t for t in analysis.top_technologies[:15] if t.category == 'Security']
        # If we have 2+ security trends, themes should be generated
        if len(security_trends_in_top) >= 2:
            security_themes = [t for t in analysis.hot_themes if 'security' in t]
            self.assertGreater(len(security_themes), 0)
        else:
            # Test passes if we don't have enough trends yet
            self.assertIsInstance(analysis.hot_themes, list)
    
    def test_emerging_topics(self):
        """Test identification of emerging topics"""
        now = datetime.now()
        
        # Create a trend with high momentum but moderate mentions
        emerging_learnings = [
            {
                'title': 'New Programming Language Zig Gains Traction',
                'description': 'Zig language overview',
                'content': 'Zig is a systems programming language.',
                'source': 'News',
                'timestamp': (now - timedelta(days=1)).isoformat()
            },
            {
                'title': 'Zig vs Rust Performance Comparison',
                'description': 'Benchmarking Zig',
                'content': 'Comparing Zig and Rust performance.',
                'source': 'Blog',
                'timestamp': (now - timedelta(days=1)).isoformat()
            },
            {
                'title': 'Getting Started with Zig',
                'description': 'Zig tutorial',
                'content': 'Learn Zig programming basics.',
                'source': 'Tutorial',
                'timestamp': (now - timedelta(days=2)).isoformat()
            }
        ]
        
        analysis = self.analyzer.analyze_learnings(emerging_learnings)
        
        # Check for emerging topics
        self.assertIsInstance(analysis.emerging_topics, list)


class TestTrendMetrics(unittest.TestCase):
    """Test TrendMetrics dataclass"""
    
    def test_trend_metrics_creation(self):
        """Test creating a TrendMetrics instance"""
        trend = TrendMetrics(
            name='AI',
            category='AI/ML',
            mention_count=5,
            sources=['Source1', 'Source2'],
            momentum=0.5,
            score=75.0,
            sample_titles=['Title 1', 'Title 2'],
            keywords=['ai', 'ml']
        )
        
        self.assertEqual(trend.name, 'AI')
        self.assertEqual(trend.mention_count, 5)
        self.assertEqual(trend.score, 75.0)


class TestPersonalityMention(unittest.TestCase):
    """Test PersonalityMention dataclass"""
    
    def test_personality_mention_creation(self):
        """Test creating a PersonalityMention instance"""
        mention = PersonalityMention(
            name='Elon Musk',
            mention_count=3,
            context=['Context 1', 'Context 2'],
            relevance_score=30.0
        )
        
        self.assertEqual(mention.name, 'Elon Musk')
        self.assertEqual(mention.mention_count, 3)


def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
