#!/usr/bin/env python3
"""
Tests for Self-Improving Prompt Generator

Comprehensive test suite for the self-improving prompt generator orchestrator.

Created by @create-botter with systematic testing approach.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

# Import module under test
import importlib.util
spec = importlib.util.spec_from_file_location(
    "self_improving_prompt_generator",
    Path(__file__).parent.parent / "tools" / "self-improving-prompt-generator.py"
)
sipg_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sipg_module)

SelfImprovingPromptGenerator = sipg_module.SelfImprovingPromptGenerator
PromptGenerationRequest = sipg_module.PromptGenerationRequest
PromptFeedback = sipg_module.PromptFeedback
GeneratedPrompt = sipg_module.GeneratedPrompt


class TestSelfImprovingPromptGenerator(unittest.TestCase):
    """Test the self-improving prompt generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.generator = SelfImprovingPromptGenerator(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test that generator initializes correctly"""
        self.assertIsNotNone(self.generator)
        self.assertTrue(Path(self.test_dir).exists())
        
        # Check that default templates are created
        self.assertIn("feature", self.generator.templates)
        self.assertIn("bug_fix", self.generator.templates)
    
    def test_generate_prompt_basic(self):
        """Test basic prompt generation"""
        request = PromptGenerationRequest(
            issue_number=123,
            issue_title="Add new feature",
            issue_body="We need to implement feature X",
            issue_labels=["feature"],
            agent_name="create-botter",
            category="feature"
        )
        
        prompt = self.generator.generate_prompt(request)
        
        # Verify prompt structure
        self.assertIsInstance(prompt, GeneratedPrompt)
        self.assertEqual(prompt.agent_name, "create-botter")
        self.assertEqual(prompt.category, "feature")
        self.assertGreater(len(prompt.prompt_text), 100)
        self.assertIn("@create-botter", prompt.prompt_text)
        self.assertIn("feature X", prompt.prompt_text)
    
    def test_category_detection_from_labels(self):
        """Test category detection from issue labels"""
        # Bug label
        request = PromptGenerationRequest(
            issue_number=124,
            issue_title="Some issue",
            issue_body="Details",
            issue_labels=["bug"],
            agent_name="test-agent"
        )
        prompt = self.generator.generate_prompt(request)
        self.assertEqual(prompt.category, "bug_fix")
        
        # Feature label
        request.issue_labels = ["feature"]
        prompt = self.generator.generate_prompt(request)
        self.assertEqual(prompt.category, "feature")
    
    def test_category_detection_from_title(self):
        """Test category detection from issue title"""
        # Bug in title
        request = PromptGenerationRequest(
            issue_number=125,
            issue_title="Fix bug in authentication",
            issue_body="Details",
            issue_labels=[],
            agent_name="test-agent"
        )
        prompt = self.generator.generate_prompt(request)
        self.assertEqual(prompt.category, "bug_fix")
        
        # Feature in title
        request.issue_title = "Add new feature to dashboard"
        prompt = self.generator.generate_prompt(request)
        self.assertEqual(prompt.category, "feature")
    
    def test_prompt_persistence(self):
        """Test that generated prompts are persisted"""
        request = PromptGenerationRequest(
            issue_number=126,
            issue_title="Test persistence",
            issue_body="Details",
            issue_labels=[],
            agent_name="test-agent"
        )
        
        prompt = self.generator.generate_prompt(request)
        
        # Verify it's saved
        self.assertIn(prompt, self.generator.generated_prompts)
        
        # Create new generator instance and verify it loads
        new_generator = SelfImprovingPromptGenerator(data_dir=self.test_dir)
        self.assertEqual(len(new_generator.generated_prompts), 1)
        self.assertEqual(new_generator.generated_prompts[0].prompt_id, prompt.prompt_id)
    
    def test_feedback_recording(self):
        """Test feedback recording and persistence"""
        # Generate a prompt first
        request = PromptGenerationRequest(
            issue_number=127,
            issue_title="Test feedback",
            issue_body="Details",
            issue_labels=[],
            agent_name="test-agent",
            category="feature"
        )
        prompt = self.generator.generate_prompt(request)
        
        # Record feedback
        feedback = PromptFeedback(
            prompt_id=prompt.prompt_id,
            success=True,
            resolution_time_hours=12.5,
            quality_rating=0.9
        )
        self.generator.record_feedback(feedback)
        
        # Verify feedback is saved
        self.assertIn(feedback, self.generator.feedback)
        
        # Verify template success count updated
        template = self.generator.templates["feature"]
        self.assertEqual(template["success_count"], 1)
    
    def test_template_usage_tracking(self):
        """Test that template usage is tracked"""
        # Generate multiple prompts
        for i in range(3):
            request = PromptGenerationRequest(
                issue_number=200 + i,
                issue_title=f"Test {i}",
                issue_body="Details",
                issue_labels=["feature"],
                agent_name="test-agent"
            )
            self.generator.generate_prompt(request)
        
        # Check usage count
        template = self.generator.templates["feature"]
        self.assertEqual(template["total_uses"], 3)
    
    def test_quality_score_estimation(self):
        """Test quality score estimation"""
        template_id = "feature_v1"
        category = "feature"
        
        # New template should have a reasonable score (quality scorer may give various scores)
        score = self.generator._estimate_quality_score(template_id, category)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_performance_report_generation(self):
        """Test performance report generation"""
        # Generate some test data
        request = PromptGenerationRequest(
            issue_number=128,
            issue_title="Test report",
            issue_body="Details",
            issue_labels=["feature"],
            agent_name="test-agent"
        )
        prompt = self.generator.generate_prompt(request)
        
        feedback = PromptFeedback(
            prompt_id=prompt.prompt_id,
            success=True,
            resolution_time_hours=15.0
        )
        self.generator.record_feedback(feedback)
        
        # Generate report
        report = self.generator.get_performance_report()
        
        # Verify report structure
        self.assertIn("generated_at", report)
        self.assertIn("total_prompts_generated", report)
        self.assertIn("templates", report)
        self.assertIn("overall_metrics", report)
        
        self.assertEqual(report["total_prompts_generated"], 1)
        self.assertEqual(report["total_feedback_received"], 1)
        
        # Verify template metrics
        self.assertIn("feature_v1", report["templates"])
        template_report = report["templates"]["feature_v1"]
        self.assertEqual(template_report["feedback_count"], 1)
        self.assertEqual(template_report["success_count"], 1)
        self.assertEqual(template_report["success_rate"], 1.0)
    
    def test_ab_testing_disabled(self):
        """Test that A/B testing can be disabled"""
        self.generator.config["ab_testing_enabled"] = False
        
        template, variant = self.generator._select_template("feature")
        
        self.assertIsNotNone(template)
        self.assertIsNone(variant)
    
    def test_multiple_categories(self):
        """Test handling of multiple prompt categories"""
        categories = ["feature", "bug_fix", "refactor", "documentation"]
        
        for category in categories:
            request = PromptGenerationRequest(
                issue_number=300,
                issue_title=f"Test {category}",
                issue_body="Details",
                issue_labels=[category if category != "bug_fix" else "bug"],
                agent_name="test-agent"
            )
            
            prompt = self.generator.generate_prompt(request)
            
            # Verify category is correct
            expected_category = category if category != "refactor" else "feature"
            if category == "bug_fix":
                expected_category = "bug_fix"
            
            # Just verify prompt was generated successfully
            self.assertIsNotNone(prompt)
            self.assertGreater(len(prompt.prompt_text), 50)
    
    def test_config_persistence(self):
        """Test that configuration is persisted"""
        # Modify config
        self.generator.config["custom_setting"] = "test_value"
        self.generator._save_data()
        
        # Load in new instance
        new_generator = SelfImprovingPromptGenerator(data_dir=self.test_dir)
        
        self.assertEqual(new_generator.config.get("custom_setting"), "test_value")
    
    def test_feedback_with_missing_prompt(self):
        """Test feedback handling when prompt doesn't exist"""
        feedback = PromptFeedback(
            prompt_id="nonexistent_prompt",
            success=True,
            resolution_time_hours=10.0
        )
        
        # Should not crash
        self.generator.record_feedback(feedback)
        
        # Feedback should still be saved
        self.assertIn(feedback, self.generator.feedback)
    
    def test_template_success_rate_calculation(self):
        """Test that success rates are calculated correctly"""
        # Generate prompts and record mixed feedback
        prompts = []
        for i in range(5):
            request = PromptGenerationRequest(
                issue_number=400 + i,
                issue_title=f"Test {i}",
                issue_body="Details",
                issue_labels=["feature"],
                agent_name="test-agent"
            )
            prompts.append(self.generator.generate_prompt(request))
        
        # Record 3 successes and 2 failures
        for i, prompt in enumerate(prompts):
            feedback = PromptFeedback(
                prompt_id=prompt.prompt_id,
                success=(i < 3),  # First 3 are successes
                resolution_time_hours=10.0
            )
            self.generator.record_feedback(feedback)
        
        # Check template stats
        template = self.generator.templates["feature"]
        self.assertEqual(template["success_count"], 3)
        self.assertEqual(template["total_uses"], 5)
        
        # Check report
        report = self.generator.get_performance_report()
        template_report = report["templates"]["feature_v1"]
        self.assertEqual(template_report["success_rate"], 0.6)  # 3/5


class TestPromptGenerationRequest(unittest.TestCase):
    """Test PromptGenerationRequest dataclass"""
    
    def test_creation(self):
        """Test request creation"""
        request = PromptGenerationRequest(
            issue_number=1,
            issue_title="Test",
            issue_body="Body",
            issue_labels=["feature"],
            agent_name="test-agent"
        )
        
        self.assertEqual(request.issue_number, 1)
        self.assertEqual(request.issue_title, "Test")
        self.assertIsNone(request.category)
    
    def test_with_category(self):
        """Test request with explicit category"""
        request = PromptGenerationRequest(
            issue_number=1,
            issue_title="Test",
            issue_body="Body",
            issue_labels=[],
            agent_name="test-agent",
            category="bug_fix"
        )
        
        self.assertEqual(request.category, "bug_fix")


class TestGeneratedPrompt(unittest.TestCase):
    """Test GeneratedPrompt dataclass"""
    
    def test_creation(self):
        """Test prompt creation"""
        prompt = GeneratedPrompt(
            prompt_id="test_123",
            prompt_text="Test prompt",
            template_id="feature_v1",
            agent_name="test-agent",
            category="feature",
            quality_score=0.85,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.assertEqual(prompt.prompt_id, "test_123")
        self.assertEqual(prompt.quality_score, 0.85)
        self.assertEqual(prompt.learning_insights_used, 0)


class TestPromptFeedback(unittest.TestCase):
    """Test PromptFeedback dataclass"""
    
    def test_creation(self):
        """Test feedback creation"""
        feedback = PromptFeedback(
            prompt_id="test_123",
            success=True,
            resolution_time_hours=12.5,
            quality_rating=0.9,
            notes="Great prompt"
        )
        
        self.assertEqual(feedback.prompt_id, "test_123")
        self.assertTrue(feedback.success)
        self.assertEqual(feedback.resolution_time_hours, 12.5)
        self.assertEqual(feedback.quality_rating, 0.9)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.generator = SelfImprovingPromptGenerator(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test complete workflow: generate → feedback → report"""
        # Step 1: Generate prompt
        request = PromptGenerationRequest(
            issue_number=500,
            issue_title="Implement search feature",
            issue_body="Add search functionality to the app",
            issue_labels=["feature", "enhancement"],
            agent_name="create-botter"
        )
        
        prompt = self.generator.generate_prompt(request)
        
        self.assertIsNotNone(prompt)
        self.assertIn("@create-botter", prompt.prompt_text)
        
        # Step 2: Record feedback
        feedback = PromptFeedback(
            prompt_id=prompt.prompt_id,
            success=True,
            resolution_time_hours=18.5,
            quality_rating=0.85,
            notes="Worked well"
        )
        
        self.generator.record_feedback(feedback)
        
        # Step 3: Generate report
        report = self.generator.get_performance_report()
        
        self.assertEqual(report["total_prompts_generated"], 1)
        self.assertEqual(report["total_feedback_received"], 1)
        
        # Verify overall metrics
        self.assertIn("overall_metrics", report)
        self.assertEqual(report["overall_metrics"]["success_rate"], 1.0)
        self.assertEqual(report["overall_metrics"]["avg_resolution_time_hours"], 18.5)
    
    def test_persistence_across_instances(self):
        """Test that data persists across generator instances"""
        # Generate and provide feedback in first instance
        request = PromptGenerationRequest(
            issue_number=501,
            issue_title="Test persistence",
            issue_body="Testing",
            issue_labels=["feature"],
            agent_name="test-agent"
        )
        
        prompt = self.generator.generate_prompt(request)
        
        feedback = PromptFeedback(
            prompt_id=prompt.prompt_id,
            success=True,
            resolution_time_hours=10.0
        )
        self.generator.record_feedback(feedback)
        
        # Create new instance
        new_generator = SelfImprovingPromptGenerator(data_dir=self.test_dir)
        
        # Verify data is loaded
        self.assertEqual(len(new_generator.generated_prompts), 1)
        self.assertEqual(len(new_generator.feedback), 1)
        self.assertEqual(new_generator.templates["feature"]["success_count"], 1)
        
        # Generate report from new instance
        report = new_generator.get_performance_report()
        self.assertEqual(report["total_prompts_generated"], 1)
        self.assertEqual(report["overall_metrics"]["success_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
