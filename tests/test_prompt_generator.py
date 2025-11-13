#!/usr/bin/env python3
"""
Tests for Self-Improving Prompt Generator

Comprehensive test suite following @engineer-master's rigorous approach.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone
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
PromptTemplate = prompt_generator_module.PromptTemplate
PromptOutcome = prompt_generator_module.PromptOutcome


class TestPromptTemplate(unittest.TestCase):
    """Test PromptTemplate dataclass"""
    
    def test_template_creation(self):
        """Test creating a prompt template"""
        template = PromptTemplate(
            template_id="test_template",
            category="bug_fix",
            template="Test template: {agent} - {issue_body}",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.assertEqual(template.template_id, "test_template")
        self.assertEqual(template.category, "bug_fix")
        self.assertEqual(template.success_count, 0)
        self.assertEqual(template.total_uses, 0)
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        template = PromptTemplate(
            template_id="test",
            category="bug_fix",
            template="test",
            success_count=8,
            failure_count=2,
            total_uses=10
        )
        
        self.assertEqual(template.success_rate, 0.8)
    
    def test_success_rate_no_uses(self):
        """Test success rate with no uses"""
        template = PromptTemplate(
            template_id="test",
            category="bug_fix",
            template="test"
        )
        
        self.assertEqual(template.success_rate, 0.0)
    
    def test_effectiveness_score_no_data(self):
        """Test effectiveness score with no usage data"""
        template = PromptTemplate(
            template_id="test",
            category="bug_fix",
            template="test"
        )
        
        # Should return neutral score
        self.assertEqual(template.effectiveness_score, 0.5)
    
    def test_effectiveness_score_high_success(self):
        """Test effectiveness score with high success rate"""
        template = PromptTemplate(
            template_id="test",
            category="bug_fix",
            template="test",
            success_count=9,
            failure_count=1,
            total_uses=10,
            avg_resolution_time=2.0
        )
        
        # Should be high score
        self.assertGreater(template.effectiveness_score, 0.7)
    
    def test_effectiveness_score_slow_resolution(self):
        """Test effectiveness score penalty for slow resolution"""
        template = PromptTemplate(
            template_id="test",
            category="bug_fix",
            template="test",
            success_count=10,
            failure_count=0,
            total_uses=10,
            avg_resolution_time=100.0  # Very slow
        )
        
        # Should have penalty applied
        self.assertLess(template.effectiveness_score, 1.0)


class TestPromptOutcome(unittest.TestCase):
    """Test PromptOutcome dataclass"""
    
    def test_outcome_creation(self):
        """Test creating a prompt outcome"""
        outcome = PromptOutcome(
            prompt_id="test_template",
            issue_number=123,
            success=True,
            resolution_time_hours=2.5,
            agent_used="engineer-master",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.assertEqual(outcome.prompt_id, "test_template")
        self.assertEqual(outcome.issue_number, 123)
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.resolution_time_hours, 2.5)


class TestPromptGenerator(unittest.TestCase):
    """Test PromptGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.generator = PromptGenerator(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test prompt generator initialization"""
        self.assertIsNotNone(self.generator.templates)
        self.assertIsInstance(self.generator.templates, dict)
        self.assertTrue(len(self.generator.templates) > 0)
    
    def test_default_templates_created(self):
        """Test that default templates are created"""
        # Check for expected default templates
        expected_categories = ["bug_fix", "feature", "refactor", "documentation", "investigation", "security"]
        
        categories_found = set(t.category for t in self.generator.templates.values())
        
        for category in expected_categories:
            self.assertIn(category, categories_found)
    
    def test_generate_prompt_bug_fix(self):
        """Test generating a bug fix prompt"""
        issue_body = "There's a bug in the login function"
        prompt, template_id = self.generator.generate_prompt(
            issue_body=issue_body,
            category="bug_fix",
            agent="engineer-master"
        )
        
        self.assertIsNotNone(prompt)
        self.assertIn("@engineer-master", prompt)
        self.assertIn(issue_body, prompt)
        self.assertIsNotNone(template_id)
    
    def test_generate_prompt_feature(self):
        """Test generating a feature prompt"""
        issue_body = "Add user profile page"
        prompt, template_id = self.generator.generate_prompt(
            issue_body=issue_body,
            category="feature",
            agent="create-guru"
        )
        
        self.assertIn("@create-guru", prompt)
        self.assertIn(issue_body, prompt)
    
    def test_generate_prompt_with_learning_context(self):
        """Test generating prompt with learning context"""
        issue_body = "Optimize database queries"
        learning_context = [
            "Use indexed queries for better performance",
            "Consider caching frequently accessed data"
        ]
        
        prompt, template_id = self.generator.generate_prompt(
            issue_body=issue_body,
            category="refactor",
            agent="accelerate-master",
            learning_context=learning_context
        )
        
        self.assertIn("Recent Relevant Learnings", prompt)
        self.assertIn(learning_context[0], prompt)
    
    def test_template_usage_tracking(self):
        """Test that template usage is tracked"""
        # Generate a prompt
        initial_uses = self.generator.templates["bug_fix_systematic"].total_uses
        
        self.generator.generate_prompt(
            issue_body="Test issue",
            category="bug_fix"
        )
        
        final_uses = self.generator.templates["bug_fix_systematic"].total_uses
        self.assertEqual(final_uses, initial_uses + 1)
    
    def test_record_outcome_success(self):
        """Test recording a successful outcome"""
        initial_outcomes = len(self.generator.outcomes)
        
        self.generator.record_outcome(
            prompt_id="bug_fix_systematic",
            issue_number=123,
            success=True,
            resolution_time_hours=3.5,
            agent_used="engineer-master"
        )
        
        self.assertEqual(len(self.generator.outcomes), initial_outcomes + 1)
        
        # Check template statistics updated
        template = self.generator.templates["bug_fix_systematic"]
        self.assertGreater(template.success_count, 0)
    
    def test_record_outcome_failure(self):
        """Test recording a failed outcome"""
        self.generator.record_outcome(
            prompt_id="bug_fix_systematic",
            issue_number=124,
            success=False,
            resolution_time_hours=1.0,
            agent_used="engineer-master",
            error_type="build_failure"
        )
        
        template = self.generator.templates["bug_fix_systematic"]
        self.assertGreater(template.failure_count, 0)
    
    def test_select_best_template(self):
        """Test selecting the best template for a category"""
        # Create multiple templates with different performance
        self.generator.templates["bug_fix_good"] = PromptTemplate(
            template_id="bug_fix_good",
            category="bug_fix",
            template="Good template",
            success_count=8,
            failure_count=2,
            total_uses=10
        )
        
        self.generator.templates["bug_fix_bad"] = PromptTemplate(
            template_id="bug_fix_bad",
            category="bug_fix",
            template="Bad template",
            success_count=2,
            failure_count=8,
            total_uses=10
        )
        
        best = self.generator._select_best_template("bug_fix")
        
        # Should select the better performing template
        self.assertGreater(best.effectiveness_score, 0.5)
    
    def test_generic_template_creation(self):
        """Test creating a generic template for unknown category"""
        prompt, template_id = self.generator.generate_prompt(
            issue_body="Custom task",
            category="custom_category",
            agent="test-agent"
        )
        
        self.assertIsNotNone(prompt)
        self.assertIn("custom_category", template_id)
    
    def test_performance_report(self):
        """Test generating a performance report"""
        # Record some outcomes
        self.generator.record_outcome(
            prompt_id="bug_fix_systematic",
            issue_number=1,
            success=True,
            resolution_time_hours=2.0
        )
        
        report = self.generator.get_performance_report()
        
        self.assertIn("generated_at", report)
        self.assertIn("templates", report)
        self.assertIn("insights", report)
        self.assertIsInstance(report["templates"], dict)
    
    def test_insights_update(self):
        """Test that insights are updated after recording outcomes"""
        # Record multiple outcomes
        for i in range(5):
            self.generator.record_outcome(
                prompt_id="bug_fix_systematic",
                issue_number=100 + i,
                success=i < 4,  # 4 successes, 1 failure
                resolution_time_hours=2.0
            )
        
        # Check insights were generated
        self.assertIn("overall", self.generator.insights)
        self.assertIsInstance(self.generator.insights["overall"], dict)
    
    def test_optimize_templates_insufficient_data(self):
        """Test optimization with insufficient data"""
        suggestions = self.generator.optimize_templates()
        
        # Should return empty or None with insufficient data
        self.assertIsNotNone(suggestions)
    
    def test_optimize_templates_with_data(self):
        """Test optimization with sufficient data"""
        # Create template with poor performance
        self.generator.templates["test_poor"] = PromptTemplate(
            template_id="test_poor",
            category="test",
            template="Poor template",
            success_count=1,
            failure_count=9,
            total_uses=10
        )
        
        # Record outcomes
        for i in range(10):
            self.generator.record_outcome(
                prompt_id="test_poor",
                issue_number=200 + i,
                success=i == 0,  # Only 1 success
                resolution_time_hours=5.0,
                error_type="test_error"
            )
        
        suggestions = self.generator.optimize_templates()
        
        # Should have suggestions for poor performing template
        self.assertIsInstance(suggestions, list)
        if suggestions:
            self.assertTrue(any(s["template_id"] == "test_poor" for s in suggestions))
    
    def test_data_persistence(self):
        """Test that data is persisted across instances"""
        # Generate a prompt and record outcome
        self.generator.generate_prompt(
            issue_body="Test persistence",
            category="bug_fix"
        )
        
        self.generator.record_outcome(
            prompt_id="bug_fix_systematic",
            issue_number=999,
            success=True,
            resolution_time_hours=1.5
        )
        
        # Create new generator instance
        new_generator = PromptGenerator(data_dir=self.test_dir)
        
        # Check data was loaded
        self.assertGreater(len(new_generator.templates), 0)
        self.assertGreater(len(new_generator.outcomes), 0)
    
    def test_moving_average_resolution_time(self):
        """Test that resolution time uses moving average"""
        template_id = "bug_fix_systematic"
        
        # Record first outcome
        self.generator.record_outcome(
            prompt_id=template_id,
            issue_number=1,
            success=True,
            resolution_time_hours=4.0
        )
        
        first_avg = self.generator.templates[template_id].avg_resolution_time
        self.assertEqual(first_avg, 4.0)
        
        # Record second outcome with different time
        self.generator.record_outcome(
            prompt_id=template_id,
            issue_number=2,
            success=True,
            resolution_time_hours=2.0
        )
        
        second_avg = self.generator.templates[template_id].avg_resolution_time
        
        # Should be between the two values (weighted average)
        self.assertGreater(second_avg, 2.0)
        self.assertLess(second_avg, 4.0)


class TestPromptGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.generator = PromptGenerator(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def test_empty_issue_body(self):
        """Test handling empty issue body"""
        prompt, template_id = self.generator.generate_prompt(
            issue_body="",
            category="bug_fix"
        )
        
        self.assertIsNotNone(prompt)
    
    def test_special_characters_in_issue_body(self):
        """Test handling special characters"""
        issue_body = "Bug with {} and {agent} placeholders"
        prompt, template_id = self.generator.generate_prompt(
            issue_body=issue_body,
            category="bug_fix"
        )
        
        self.assertIn(issue_body, prompt)
    
    def test_very_long_issue_body(self):
        """Test handling very long issue body"""
        issue_body = "A" * 10000  # 10k characters
        prompt, template_id = self.generator.generate_prompt(
            issue_body=issue_body,
            category="feature"
        )
        
        self.assertIn(issue_body, prompt)
    
    def test_empty_learning_context(self):
        """Test with empty learning context"""
        prompt, template_id = self.generator.generate_prompt(
            issue_body="Test",
            category="bug_fix",
            learning_context=[]
        )
        
        # Should not include learning section
        self.assertNotIn("Recent Relevant Learnings", prompt)
    
    def test_invalid_template_id_in_outcome(self):
        """Test recording outcome for non-existent template"""
        # Should not raise error
        self.generator.record_outcome(
            prompt_id="nonexistent_template",
            issue_number=1,
            success=True,
            resolution_time_hours=1.0
        )
        
        # Outcome should still be recorded
        self.assertGreater(len(self.generator.outcomes), 0)


if __name__ == "__main__":
    unittest.main()
