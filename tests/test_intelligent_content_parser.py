#!/usr/bin/env python3
"""
Tests for intelligent content parser

Tests ad filtering, emoji cleaning, text normalization, and content quality validation.
"""

import unittest
import sys
import os
import importlib.util

# Load module with hyphens in filename
tools_dir = os.path.join(os.path.dirname(__file__), '..', 'tools')
spec = importlib.util.spec_from_file_location('parser', os.path.join(tools_dir, 'intelligent-content-parser.py'))
parser_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser_module)

IntelligentContentParser = parser_module.IntelligentContentParser
ContentQuality = parser_module.ContentQuality


class TestIntelligentContentParser(unittest.TestCase):
    """Test cases for intelligent content parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = IntelligentContentParser()
    
    def test_clean_emoji_malformed(self):
        """Test cleaning of malformed emoji unicode sequences"""
        # Test malformed emoji
        text = "SoftBank dumps Nvidia \ud83d\udcb0, SpaceX GigaBay \ud83d\ude80"
        cleaned = self.parser.clean_emoji(text)
        
        # Should have real emojis or be cleaned
        self.assertNotIn('\\u', cleaned)
        self.assertIn('Nvidia', cleaned)
    
    def test_clean_emoji_normal_text(self):
        """Test that normal text is unchanged"""
        text = "This is normal text without emojis"
        cleaned = self.parser.clean_emoji(text)
        self.assertEqual(text, cleaned)
    
    def test_is_sponsor_content_explicit(self):
        """Test detection of explicit sponsor content"""
        sponsor_text = """
        Coffee Chat: Turn Supabase Events Into Automated Workflows (Sponsor)
        Modern apps run on data, APIs, and automation.... but making all of them work together is hard.
        Join Orkes for a Developer Coffee Chat on November 13 at 9 AM PST
        """
        
        is_sponsor, reasons = self.parser.is_sponsor_content(sponsor_text)
        
        self.assertTrue(is_sponsor)
        self.assertGreater(len(reasons), 0)
    
    def test_is_sponsor_content_call_to_action(self):
        """Test detection of call-to-action patterns"""
        cta_text = """
        Sign up now and get $500 in credits!
        Register for free today and start building.
        """
        
        is_sponsor, reasons = self.parser.is_sponsor_content(cta_text)
        
        self.assertTrue(is_sponsor)
        self.assertGreater(len(reasons), 0)
    
    def test_is_sponsor_content_clean_content(self):
        """Test that clean content is not flagged as sponsor"""
        clean_text = """
        New research shows that neural networks can achieve better performance
        with improved training techniques. The study was published in Nature.
        """
        
        is_sponsor, reasons = self.parser.is_sponsor_content(clean_text)
        
        self.assertFalse(is_sponsor)
    
    def test_is_promo_section_title(self):
        """Test detection of promotional section titles"""
        promo_titles = [
            "Coffee Chat: Turn Supabase Events (Sponsor)",
            "Get $500 Google Cloud credits",
            "Goodbye low test coverage",
            "100 prompts for Notion Agents"
        ]
        
        for title in promo_titles:
            result = self.parser.is_promo_section_title(title)
            self.assertTrue(result, f"Failed to detect promo title: {title}")
    
    def test_is_not_promo_section_title(self):
        """Test that normal titles are not flagged as promo"""
        normal_titles = [
            "Apple releases new iPhone features",
            "Understanding Rust ownership model",
            "How to build scalable APIs"
        ]
        
        for title in normal_titles:
            result = self.parser.is_promo_section_title(title)
            self.assertFalse(result, f"Incorrectly flagged as promo: {title}")
    
    def test_extract_clean_content(self):
        """Test extraction of clean content from mixed text"""
        mixed_content = """This is a real article about technology trends. It discusses important developments in the field.

Sign up now for unlimited access! Get started today with our special offer. Join thousands of developers who trust our platform.

The article continues with valuable insights about the industry."""
        
        cleaned = self.parser.extract_clean_content(mixed_content)
        
        # Should keep real content
        self.assertIn('technology trends', cleaned)
        self.assertIn('valuable insights', cleaned)
        
        # Should remove promotional content
        self.assertNotIn('Sign up now', cleaned)
        self.assertNotIn('special offer', cleaned)
    
    def test_clean_title(self):
        """Test title cleaning"""
        # Test with malformed emojis
        title = "\ud83d\udcb0 Breaking News: Apple announces new product \ud83d\ude80"
        cleaned = self.parser.clean_title(title)
        
        self.assertIn('Breaking News', cleaned)
        self.assertIn('Apple', cleaned)
        self.assertNotIn('\\u', cleaned)
    
    def test_assess_content_quality_valid(self):
        """Test quality assessment of valid content"""
        learning = {
            'title': 'Understanding Machine Learning Fundamentals',
            'url': 'https://example.com/ml-guide',
            'content': 'Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data. This comprehensive guide covers the key concepts and algorithms used in modern ML applications.',
            'source': 'Tech Blog'
        }
        
        quality = self.parser.assess_content_quality(learning)
        
        self.assertTrue(quality.is_valid)
        self.assertGreater(quality.confidence, 0.7)
    
    def test_assess_content_quality_sponsor(self):
        """Test quality assessment rejects pure sponsor content"""
        learning = {
            'title': 'Coffee Chat: Turn Supabase Events (Sponsor)',
            'content': 'Sign up now for our developer coffee chat! Join Orkes and get unlimited access. Register today!',
            'source': 'TLDR'
        }
        
        quality = self.parser.assess_content_quality(learning)
        
        self.assertFalse(quality.is_valid)
    
    def test_assess_content_quality_partial_sponsor(self):
        """Test quality assessment with partial sponsor content"""
        learning = {
            'title': 'New AI Model Achieves State of the Art',
            'content': '''Researchers at University X have developed a new transformer model. The model shows significant improvements in natural language understanding tasks. It uses a novel attention mechanism that reduces computational requirements.

Sponsor: Sign up for AI Cloud and get credits today! Register now for unlimited access.''',
            'source': 'Research News'
        }
        
        quality = self.parser.assess_content_quality(learning)
        
        # Should extract clean content
        self.assertTrue(quality.is_valid)
        self.assertIsNotNone(quality.cleaned_content)
        self.assertIn('transformer model', quality.cleaned_content)
        self.assertNotIn('Sign up', quality.cleaned_content)
    
    def test_parse_learning_valid(self):
        """Test parsing a valid learning entry"""
        learning = {
            'title': 'Python 3.12 \ud83d\ude80 New Features',
            'description': 'Python 3.12 introduces several performance improvements',
            'url': 'https://example.com/python-3.12',
            'source': 'Tech News'
        }
        
        parsed = self.parser.parse_learning(learning)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['title'], 'Python 3.12 🚀 New Features')
        self.assertIn('quality_score', parsed)
        self.assertTrue(parsed.get('parsed'))
    
    def test_parse_learning_sponsor(self):
        """Test that sponsor content is filtered out"""
        learning = {
            'title': 'Get $500 Credits (Sponsor)',
            'content': 'Sign up now and claim your benefits!',
            'source': 'TLDR'
        }
        
        parsed = self.parser.parse_learning(learning)
        
        self.assertIsNone(parsed)
    
    def test_parse_learnings_batch(self):
        """Test parsing a batch of learnings"""
        learnings = [
            {
                'title': 'Real Article About Rust',
                'content': 'Rust provides memory safety without garbage collection.',
                'url': 'https://example.com/rust'
            },
            {
                'title': 'Sponsor: Get Free Credits',
                'content': 'Sign up now for unlimited access!'
            },
            {
                'title': 'Understanding Docker Containers',
                'content': 'Docker containers provide lightweight virtualization.',
                'url': 'https://example.com/docker'
            }
        ]
        
        cleaned, stats = self.parser.parse_learnings(learnings)
        
        self.assertEqual(stats['total_input'], 3)
        self.assertEqual(stats['accepted'], 2)
        self.assertEqual(stats['rejected'], 1)
        self.assertGreater(stats['acceptance_rate'], 0.6)
    
    def test_parse_learnings_all_sponsor(self):
        """Test parsing when all content is sponsor"""
        learnings = [
            {'title': 'Sponsor Title 1', 'content': 'Sign up now!'},
            {'title': 'Get Credits Today', 'content': 'Register for free!'}
        ]
        
        cleaned, stats = self.parser.parse_learnings(learnings)
        
        self.assertEqual(stats['accepted'], 0)
        self.assertEqual(stats['rejected'], 2)
        self.assertEqual(stats['acceptance_rate'], 0.0)


class TestContentQuality(unittest.TestCase):
    """Test ContentQuality dataclass"""
    
    def test_content_quality_creation(self):
        """Test creating a ContentQuality instance"""
        quality = ContentQuality(
            is_valid=True,
            confidence=0.95,
            issues=['High quality content'],
            cleaned_content='Clean text'
        )
        
        self.assertTrue(quality.is_valid)
        self.assertEqual(quality.confidence, 0.95)
        self.assertEqual(len(quality.issues), 1)


def run_tests():
    """Run all tests"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
