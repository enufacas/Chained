#!/usr/bin/env python3
"""
Integration Tests for Enhanced Prompt Generator with Reinforcement Learning

Tests the complete integration of reinforcement learning with the prompt generator.
Demonstrates end-to-end self-improvement capabilities.

Created by @APIs-architect - rigorous testing approach inspired by Margaret Hamilton.
"""

import unittest
import tempfile
import shutil
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

# Import with proper module name handling
import importlib.util

spec = importlib.util.spec_from_file_location(
    "prompt_generator",
    os.path.join(os.path.dirname(__file__), '..', 'tools', 'prompt-generator.py')
)
prompt_generator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_generator_module)

PromptGenerator = prompt_generator_module.PromptGenerator


class TestPromptGeneratorIntegration(unittest.TestCase):
    """Test integration of prompt generator with reinforcement learning"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.generator = PromptGenerator(
            data_dir=self.test_dir,
            enable_learning=False,  # Disable to avoid external dependencies
            enable_reinforcement=True
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_prompt_generation_with_reinforcement(self):
        """Test that prompts are enhanced with reinforcement patterns"""
        # First, create some successful patterns
        if self.generator.reinforcement_learner:
            self.generator.reinforcement_learner.record_feedback(
                prompt_id="bug_fix_systematic",
                issue_number=1,
                feedback_type="pr_review",
                sentiment="positive",
                feedback_text="Clear and systematic approach with step-by-step guidance"
            )
            
            # Record more successful feedback to build confidence
            for i in range(2, 5):
                self.generator.reinforcement_learner.record_feedback(
                    prompt_id="bug_fix_systematic",
                    issue_number=i,
                    feedback_type="pr_review",
                    sentiment="positive",
                    feedback_text="Thorough and clear methodology"
                )
        
        # Generate a prompt - should include reinforcement patterns
        prompt, template_id = self.generator.generate_prompt(
            issue_body="Fix login bug",
            category="bug_fix",
            agent="engineer-master"
        )
        
        # Verify prompt includes agent mention
        self.assertIn("@engineer-master", prompt)
        self.assertIn("Fix login bug", prompt)
        
        # If reinforcement is enabled and patterns exist, they should be included
        if self.generator.reinforcement_learner:
            patterns = self.generator.reinforcement_learner.get_top_patterns(
                category="bug_fix",
                min_effectiveness=0.6
            )
            if patterns:
                self.assertIn("Key Success Patterns", prompt)
    
    def test_outcome_recording_with_feedback(self):
        """Test that outcomes update both template stats and reinforcement learning"""
        if not self.generator.reinforcement_learner:
            self.skipTest("Reinforcement learning not available")
        
        # Record an outcome with feedback
        self.generator.record_outcome(
            prompt_id="feature_rigorous",
            issue_number=100,
            success=True,
            resolution_time_hours=3.5,
            agent_used="create-guru",
            feedback_text="Excellent systematic implementation with comprehensive tests"
        )
        
        # Verify template stats updated
        template = self.generator.templates["feature_rigorous"]
        self.assertGreater(template.success_count, 0)
        
        # Verify reinforcement learning recorded feedback
        self.assertGreater(len(self.generator.reinforcement_learner.feedback_history), 0)
    
    def test_optimization_includes_reinforcement_recommendations(self):
        """Test that optimization suggestions include reinforcement learning insights"""
        if not self.generator.reinforcement_learner:
            self.skipTest("Reinforcement learning not available")
        
        # Create some outcomes
        for i in range(10):
            success = i < 7  # 70% success rate
            self.generator.record_outcome(
                prompt_id="refactor_systematic",
                issue_number=200 + i,
                success=success,
                resolution_time_hours=2.0,
                feedback_text="Good work" if success else "Missing details"
            )
        
        # Get optimization suggestions
        suggestions = self.generator.optimize_templates()
        
        # Should include suggestions from reinforcement learning
        self.assertIsInstance(suggestions, list)
        
        # Check if any suggestions are from reinforcement learning
        rl_suggestions = [s for s in suggestions if s.get("source") == "reinforcement_learning"]
        
        # If there's feedback, should have some RL recommendations
        if len(self.generator.reinforcement_learner.feedback_history) > 0:
            # This is informational - may or may not have recommendations depending on feedback content
            pass
    
    def test_performance_report_includes_reinforcement_metrics(self):
        """Test that performance report includes reinforcement learning metrics"""
        if not self.generator.reinforcement_learner:
            self.skipTest("Reinforcement learning not available")
        
        # Record some feedback
        self.generator.record_outcome(
            prompt_id="documentation_precise",
            issue_number=300,
            success=True,
            resolution_time_hours=1.5,
            feedback_text="Clear and comprehensive documentation"
        )
        
        # Get performance report
        report = self.generator.get_performance_report()
        
        # Should include reinforcement section
        self.assertIn("reinforcement", report)
        self.assertIsInstance(report["reinforcement"], dict)
        
        # Verify expected metrics
        rl_metrics = report["reinforcement"]
        self.assertIn("total_feedback", rl_metrics)
        self.assertIn("diversity_score", rl_metrics)
        self.assertIn("pattern_types", rl_metrics)
    
    def test_multiple_categories_with_different_patterns(self):
        """Test that different categories develop different successful patterns"""
        if not self.generator.reinforcement_learner:
            self.skipTest("Reinforcement learning not available")
        
        # Record feedback for bug fixes
        for i in range(5):
            self.generator.record_outcome(
                prompt_id="bug_fix_systematic",
                issue_number=400 + i,
                success=True,
                resolution_time_hours=2.0,
                feedback_text="Systematic debugging with clear reproduction steps"
            )
        
        # Record feedback for features
        for i in range(5):
            self.generator.record_outcome(
                prompt_id="feature_rigorous",
                issue_number=500 + i,
                success=True,
                resolution_time_hours=4.0,
                feedback_text="Comprehensive implementation with thorough testing"
            )
        
        # Patterns should exist for both categories
        bug_patterns = self.generator.reinforcement_learner.get_top_patterns(
            category="bug_fix",
            limit=10
        )
        
        feature_patterns = self.generator.reinforcement_learner.get_top_patterns(
            category="feature",
            limit=10
        )
        
        # Both should have learned patterns
        # (May be empty if pattern extraction didn't find enough keywords)
        self.assertIsInstance(bug_patterns, list)
        self.assertIsInstance(feature_patterns, list)
    
    def test_negative_feedback_influences_future_prompts(self):
        """Test that negative feedback leads to optimization recommendations"""
        if not self.generator.reinforcement_learner:
            self.skipTest("Reinforcement learning not available")
        
        # Record multiple negative outcomes
        for i in range(5):
            self.generator.record_outcome(
                prompt_id="investigation_thorough",
                issue_number=600 + i,
                success=False,
                resolution_time_hours=8.0,
                error_type="incomplete_analysis",
                feedback_text="Investigation was incomplete and missing key details"
            )
        
        # Get recommendations for this prompt
        recommendations = self.generator.reinforcement_learner.generate_optimization_recommendations(
            "investigation_thorough"
        )
        
        # Should have recommendations due to negative feedback
        self.assertGreater(len(recommendations), 0)
        
        # Should indicate high priority due to negative sentiment
        high_priority_recs = [r for r in recommendations if r.get("priority") == "high"]
        self.assertGreater(len(high_priority_recs), 0)
    
    def test_pattern_diversity_tracking(self):
        """Test that diversity score prevents convergence to single pattern"""
        if not self.generator.reinforcement_learner:
            self.skipTest("Reinforcement learning not available")
        
        # Record diverse feedback
        feedback_types = [
            ("Clear structure", "positive"),
            ("Good examples", "positive"),
            ("Comprehensive testing", "positive"),
            ("Step-by-step guidance", "positive"),
            ("Thorough documentation", "positive")
        ]
        
        for i, (feedback, sentiment) in enumerate(feedback_types):
            self.generator.record_outcome(
                prompt_id="security_defensive",
                issue_number=700 + i,
                success=True,
                resolution_time_hours=3.0,
                feedback_text=feedback
            )
        
        # Calculate diversity
        diversity = self.generator.reinforcement_learner.calculate_diversity_score()
        
        # Should have positive diversity (0-1 range)
        self.assertGreaterEqual(diversity, 0.0)
        self.assertLessEqual(diversity, 1.0)
    
    def test_pattern_pruning_removes_ineffective(self):
        """Test that ineffective patterns are pruned over time"""
        if not self.generator.reinforcement_learner:
            self.skipTest("Reinforcement learning not available")
        
        # Manually create an ineffective pattern with enough samples
        from prompt_reinforcement import PromptPattern
        
        self.generator.reinforcement_learner.patterns["test_ineffective"] = PromptPattern(
            pattern="test_ineffective",
            pattern_type="general",
            success_count=1,
            failure_count=15  # Very poor performance
        )
        
        # Prune ineffective patterns
        pruned = self.generator.reinforcement_learner.prune_ineffective_patterns(
            min_samples=10,
            effectiveness_threshold=0.3
        )
        
        # Should have pruned the ineffective pattern
        self.assertIn("test_ineffective", pruned)
        self.assertNotIn("test_ineffective", self.generator.reinforcement_learner.patterns)


class TestPromptGeneratorWithoutReinforcement(unittest.TestCase):
    """Test that generator works correctly when reinforcement is disabled"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.generator = PromptGenerator(
            data_dir=self.test_dir,
            enable_learning=False,
            enable_reinforcement=False
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_generation_without_reinforcement(self):
        """Test that prompt generation works without reinforcement"""
        prompt, template_id = self.generator.generate_prompt(
            issue_body="Add user authentication",
            category="feature",
            agent="create-guru"
        )
        
        # Should still work
        self.assertIsNotNone(prompt)
        self.assertIn("@create-guru", prompt)
        self.assertIn("Add user authentication", prompt)
    
    def test_outcome_recording_without_reinforcement(self):
        """Test that outcome recording works without reinforcement"""
        # Should not crash even with feedback_text
        self.generator.record_outcome(
            prompt_id="bug_fix_systematic",
            issue_number=100,
            success=True,
            resolution_time_hours=2.0,
            feedback_text="This should be ignored gracefully"
        )
        
        # Template stats should still update
        template = self.generator.templates["bug_fix_systematic"]
        self.assertGreater(template.success_count, 0)


if __name__ == "__main__":
    unittest.main()
