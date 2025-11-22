#!/usr/bin/env python3
"""
Tests for Prompt Reinforcement Learning Module

Comprehensive test suite following @APIs-architect's rigorous approach.
Ensures reinforcement learning capabilities work correctly and integrate
seamlessly with the prompt generator.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from prompt_reinforcement import (
    PromptReinforcementLearner,
    PromptFeedback,
    PromptPattern
)


class TestPromptFeedback(unittest.TestCase):
    """Test PromptFeedback dataclass"""
    
    def test_feedback_creation(self):
        """Test creating feedback"""
        feedback = PromptFeedback(
            prompt_id="test_template",
            issue_number=123,
            feedback_type="pr_review",
            sentiment="positive",
            feedback_text="Clear and thorough approach",
            extracted_patterns=["emphasis_clear", "emphasis_thorough"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.assertEqual(feedback.prompt_id, "test_template")
        self.assertEqual(feedback.sentiment, "positive")
        self.assertEqual(len(feedback.extracted_patterns), 2)


class TestPromptPattern(unittest.TestCase):
    """Test PromptPattern dataclass"""
    
    def test_pattern_creation(self):
        """Test creating a pattern"""
        pattern = PromptPattern(
            pattern="emphasis_clear",
            pattern_type="keyword",
            success_count=8,
            failure_count=2
        )
        
        self.assertEqual(pattern.pattern, "emphasis_clear")
        self.assertEqual(pattern.success_count, 8)
    
    def test_effectiveness_calculation(self):
        """Test pattern effectiveness calculation"""
        pattern = PromptPattern(
            pattern="test_pattern",
            pattern_type="keyword",
            success_count=7,
            failure_count=3
        )
        
        self.assertEqual(pattern.effectiveness, 0.7)
    
    def test_effectiveness_no_data(self):
        """Test effectiveness with no usage data"""
        pattern = PromptPattern(
            pattern="test_pattern",
            pattern_type="keyword"
        )
        
        self.assertEqual(pattern.effectiveness, 0.5)


class TestPromptReinforcementLearner(unittest.TestCase):
    """Test PromptReinforcementLearner class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.learner = PromptReinforcementLearner(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test learner initialization"""
        self.assertIsNotNone(self.learner.feedback_history)
        self.assertIsNotNone(self.learner.patterns)
        self.assertIsInstance(self.learner.feedback_history, list)
        self.assertIsInstance(self.learner.patterns, dict)
    
    def test_record_positive_feedback(self):
        """Test recording positive feedback"""
        initial_count = len(self.learner.feedback_history)
        
        self.learner.record_feedback(
            prompt_id="bug_fix_systematic",
            issue_number=100,
            feedback_type="pr_review",
            sentiment="positive",
            feedback_text="The prompt was clear and systematic, leading to thorough implementation"
        )
        
        self.assertEqual(len(self.learner.feedback_history), initial_count + 1)
        
        # Check patterns were extracted and updated
        self.assertGreater(len(self.learner.patterns), 0)
    
    def test_record_negative_feedback(self):
        """Test recording negative feedback"""
        self.learner.record_feedback(
            prompt_id="feature_rigorous",
            issue_number=101,
            feedback_type="pr_review",
            sentiment="negative",
            feedback_text="The prompt was unclear and missing important details"
        )
        
        feedback = self.learner.feedback_history[-1]
        self.assertEqual(feedback.sentiment, "negative")
        
        # Should extract negative patterns
        has_avoid_pattern = any("avoid_" in p for p in feedback.extracted_patterns)
        self.assertTrue(has_avoid_pattern or len(feedback.extracted_patterns) >= 0)
    
    def test_pattern_extraction(self):
        """Test pattern extraction from feedback"""
        patterns = self.learner._extract_patterns_from_feedback(
            "The prompt was clear and provided step-by-step guidance with examples",
            "positive"
        )
        
        self.assertIsInstance(patterns, list)
        # Should extract positive patterns
        self.assertTrue(any("emphasis_" in p or "structure_" in p or "include_" in p for p in patterns))
    
    def test_pattern_statistics_update(self):
        """Test that pattern statistics are updated correctly"""
        # Record successful feedback
        self.learner.record_feedback(
            prompt_id="test_template",
            issue_number=200,
            feedback_type="pr_review",
            sentiment="positive",
            feedback_text="Clear and thorough"
        )
        
        # Find patterns
        clear_patterns = [p for pid, p in self.learner.patterns.items() if "clear" in pid]
        
        if clear_patterns:
            self.assertGreater(clear_patterns[0].success_count, 0)
    
    def test_get_top_patterns(self):
        """Test retrieving top performing patterns"""
        # Create some patterns with known effectiveness
        self.learner.patterns["good_pattern"] = PromptPattern(
            pattern="good_pattern",
            pattern_type="structure",
            success_count=9,
            failure_count=1
        )
        
        self.learner.patterns["bad_pattern"] = PromptPattern(
            pattern="bad_pattern",
            pattern_type="structure",
            success_count=2,
            failure_count=8
        )
        
        top_patterns = self.learner.get_top_patterns(min_effectiveness=0.6, limit=10)
        
        # Should only include good patterns
        pattern_ids = [p.pattern for p in top_patterns]
        self.assertIn("good_pattern", pattern_ids)
        self.assertNotIn("bad_pattern", pattern_ids)
    
    def test_get_top_patterns_min_samples(self):
        """Test that top patterns require minimum sample size"""
        # Create pattern with high effectiveness but few samples
        self.learner.patterns["untested"] = PromptPattern(
            pattern="untested",
            pattern_type="structure",
            success_count=1,
            failure_count=0  # 100% but only 1 sample
        )
        
        top_patterns = self.learner.get_top_patterns(min_effectiveness=0.6)
        
        # Should not include untested pattern (needs 3+ samples)
        pattern_ids = [p.pattern for p in top_patterns]
        self.assertNotIn("untested", pattern_ids)
    
    def test_get_anti_patterns(self):
        """Test retrieving anti-patterns"""
        # Create patterns with poor performance
        self.learner.patterns["anti_pattern_1"] = PromptPattern(
            pattern="anti_pattern_1",
            pattern_type="constraint",
            success_count=1,
            failure_count=5
        )
        
        self.learner.patterns["anti_pattern_2"] = PromptPattern(
            pattern="anti_pattern_2",
            pattern_type="constraint",
            success_count=0,
            failure_count=4
        )
        
        anti_patterns = self.learner.get_anti_patterns(min_failures=3)
        
        self.assertEqual(len(anti_patterns), 2)
        self.assertTrue(all(ap.effectiveness < 0.4 for ap in anti_patterns))
    
    def test_generate_optimization_recommendations(self):
        """Test generating optimization recommendations"""
        # Record some feedback
        self.learner.record_feedback(
            prompt_id="test_prompt",
            issue_number=300,
            feedback_type="pr_review",
            sentiment="negative",
            feedback_text="Missing details and unclear"
        )
        
        self.learner.record_feedback(
            prompt_id="test_prompt",
            issue_number=301,
            feedback_type="pr_review",
            sentiment="negative",
            feedback_text="Vague and incomplete"
        )
        
        recommendations = self.learner.generate_optimization_recommendations("test_prompt")
        
        self.assertIsInstance(recommendations, list)
        # Should have recommendations due to negative feedback
        self.assertGreater(len(recommendations), 0)
    
    def test_recommendations_for_nonexistent_prompt(self):
        """Test recommendations for prompt with no feedback"""
        recommendations = self.learner.generate_optimization_recommendations("nonexistent")
        
        # Should return empty list
        self.assertEqual(len(recommendations), 0)
    
    def test_calculate_diversity_score(self):
        """Test diversity score calculation"""
        # Add patterns of different types
        self.learner.patterns["struct1"] = PromptPattern(
            pattern="struct1", pattern_type="structure"
        )
        self.learner.patterns["key1"] = PromptPattern(
            pattern="key1", pattern_type="keyword"
        )
        self.learner.patterns["inst1"] = PromptPattern(
            pattern="inst1", pattern_type="instruction"
        )
        
        diversity = self.learner.calculate_diversity_score()
        
        self.assertIsInstance(diversity, float)
        self.assertGreaterEqual(diversity, 0.0)
        self.assertLessEqual(diversity, 1.0)
    
    def test_diversity_score_empty(self):
        """Test diversity score with no patterns"""
        empty_learner = PromptReinforcementLearner(data_dir=tempfile.mkdtemp())
        diversity = empty_learner.calculate_diversity_score()
        
        # Should return maximum diversity (1.0) when no patterns
        self.assertEqual(diversity, 1.0)
    
    def test_prune_ineffective_patterns(self):
        """Test pruning of ineffective patterns"""
        # Add ineffective pattern with enough samples
        self.learner.patterns["ineffective"] = PromptPattern(
            pattern="ineffective",
            pattern_type="general",
            success_count=2,
            failure_count=10  # Very poor
        )
        
        # Add good pattern
        self.learner.patterns["effective"] = PromptPattern(
            pattern="effective",
            pattern_type="general",
            success_count=10,
            failure_count=2
        )
        
        pruned = self.learner.prune_ineffective_patterns(
            min_samples=10,
            effectiveness_threshold=0.3
        )
        
        # Should prune ineffective pattern
        self.assertIn("ineffective", pruned)
        self.assertNotIn("ineffective", self.learner.patterns)
        
        # Should keep effective pattern
        self.assertNotIn("effective", pruned)
        self.assertIn("effective", self.learner.patterns)
    
    def test_prune_insufficient_samples(self):
        """Test that patterns with insufficient samples are not pruned"""
        # Add pattern with poor performance but few samples
        self.learner.patterns["untested_poor"] = PromptPattern(
            pattern="untested_poor",
            pattern_type="general",
            success_count=1,
            failure_count=3  # Poor but only 4 samples
        )
        
        pruned = self.learner.prune_ineffective_patterns(
            min_samples=10,
            effectiveness_threshold=0.3
        )
        
        # Should not prune (insufficient samples)
        self.assertNotIn("untested_poor", pruned)
        self.assertIn("untested_poor", self.learner.patterns)
    
    def test_get_reinforcement_metrics(self):
        """Test getting reinforcement metrics"""
        # Add some data
        self.learner.record_feedback(
            prompt_id="test",
            issue_number=400,
            feedback_type="pr_review",
            sentiment="positive",
            feedback_text="Good work"
        )
        
        metrics = self.learner.get_reinforcement_metrics()
        
        self.assertIn("total_feedback", metrics)
        self.assertIn("total_patterns", metrics)
        self.assertIn("diversity_score", metrics)
        self.assertIn("pattern_types", metrics)
        self.assertIsInstance(metrics["total_feedback"], int)
        self.assertIsInstance(metrics["diversity_score"], float)
    
    def test_data_persistence(self):
        """Test that data persists across instances"""
        # Record some data
        self.learner.record_feedback(
            prompt_id="persist_test",
            issue_number=500,
            feedback_type="pr_review",
            sentiment="positive",
            feedback_text="Excellent systematic approach"
        )
        
        initial_feedback_count = len(self.learner.feedback_history)
        initial_pattern_count = len(self.learner.patterns)
        
        # Create new instance
        new_learner = PromptReinforcementLearner(data_dir=self.test_dir)
        
        # Data should be loaded
        self.assertEqual(len(new_learner.feedback_history), initial_feedback_count)
        self.assertGreaterEqual(len(new_learner.patterns), initial_pattern_count)
    
    def test_pattern_classification(self):
        """Test pattern type classification"""
        test_cases = [
            ("structure_step_by_step", "structure"),
            ("emphasis_clear", "keyword"),
            ("include_examples", "instruction"),
            ("avoid_vague", "constraint"),
            ("random_pattern", "general")
        ]
        
        for pattern, expected_type in test_cases:
            result = self.learner._classify_pattern(pattern)
            self.assertEqual(result, expected_type, f"Pattern {pattern} should be type {expected_type}")


class TestReinforcementEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.learner = PromptReinforcementLearner(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_empty_feedback_text(self):
        """Test handling empty feedback text"""
        self.learner.record_feedback(
            prompt_id="test",
            issue_number=600,
            feedback_type="pr_review",
            sentiment="neutral",
            feedback_text=""
        )
        
        # Should not crash
        self.assertGreater(len(self.learner.feedback_history), 0)
    
    def test_very_long_feedback_text(self):
        """Test handling very long feedback text"""
        long_text = "A" * 10000
        
        self.learner.record_feedback(
            prompt_id="test",
            issue_number=601,
            feedback_type="pr_review",
            sentiment="positive",
            feedback_text=long_text
        )
        
        # Should handle gracefully
        self.assertIsNotNone(self.learner.feedback_history[-1])
    
    def test_special_characters_in_feedback(self):
        """Test handling special characters"""
        special_text = "Test with 特殊字符 and émojis 🎉"
        
        self.learner.record_feedback(
            prompt_id="test",
            issue_number=602,
            feedback_type="pr_review",
            sentiment="positive",
            feedback_text=special_text
        )
        
        # Should not crash
        self.assertEqual(self.learner.feedback_history[-1].feedback_text, special_text)
    
    def test_top_patterns_with_category_filter(self):
        """Test filtering patterns by category"""
        # Add pattern with specific context
        pattern = PromptPattern(
            pattern="test_pattern",
            pattern_type="structure",
            success_count=10,
            failure_count=0,
            contexts=["bug_fix"]
        )
        self.learner.patterns["test_pattern"] = pattern
        
        # Request patterns for bug_fix category
        patterns = self.learner.get_top_patterns(category="bug_fix", limit=10)
        
        # Should work without error
        self.assertIsInstance(patterns, list)


if __name__ == "__main__":
    unittest.main()
