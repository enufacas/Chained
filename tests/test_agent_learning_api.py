#!/usr/bin/env python3
"""
Test Suite for Agent Learning API

Tests the agent-learning-api.py to ensure reliable proactive guidance
for AI agents learning from historical PR failures.

Built by @APIs-architect to ensure reliability and correctness.
"""

import unittest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess


class TestAgentLearningAPI(unittest.TestCase):
    """Test suite for Agent Learning API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_script = Path("tools/agent-learning-api.py")
        self.assertTrue(self.api_script.exists(), "API script must exist")
    
    def run_api_command(self, command: list) -> dict:
        """
        Helper to run API command and parse JSON response.
        
        Args:
            command: List of command arguments
            
        Returns:
            Parsed JSON response
        """
        result = subprocess.run(
            ["python3", str(self.api_script)] + command,
            capture_output=True,
            text=True
        )
        
        # If command failed, print stderr for debugging
        if result.returncode != 0:
            print(f"Command failed: {' '.join(command)}", file=sys.stderr)
            print(f"stderr: {result.stderr}", file=sys.stderr)
            print(f"stdout: {result.stdout}", file=sys.stderr)
        
        self.assertEqual(result.returncode, 0, f"Command should succeed: {' '.join(command)}")
        
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            self.fail(f"Failed to parse JSON response: {e}\nOutput: {result.stdout}")
    
    def test_query_command_basic(self):
        """Test basic query command with required parameters"""
        response = self.run_api_command([
            "query",
            "--agent", "engineer-master",
            "--task-type", "api-development"
        ])
        
        # Validate response structure
        self.assertIn("agent_id", response)
        self.assertIn("task_type", response)
        self.assertIn("confidence", response)
        self.assertIn("risk_level", response)
        self.assertIn("recommendations", response)
        self.assertIn("warnings", response)
        self.assertIn("best_practices", response)
        self.assertIn("similar_failures", response)
        self.assertIn("success_patterns", response)
        self.assertIn("timestamp", response)
        
        # Validate data types
        self.assertEqual(response["agent_id"], "engineer-master")
        self.assertEqual(response["task_type"], "api-development")
        self.assertIsInstance(response["confidence"], float)
        self.assertIn(response["risk_level"], ["low", "medium", "high"])
        self.assertIsInstance(response["recommendations"], list)
        self.assertIsInstance(response["warnings"], list)
        self.assertIsInstance(response["best_practices"], list)
        self.assertIsInstance(response["similar_failures"], list)
        self.assertIsInstance(response["success_patterns"], list)
    
    def test_query_command_with_description(self):
        """Test query command with optional task description"""
        response = self.run_api_command([
            "query",
            "--agent", "secure-specialist",
            "--task-type", "security",
            "--task-description", "Implement authentication system"
        ])
        
        self.assertEqual(response["agent_id"], "secure-specialist")
        self.assertEqual(response["task_type"], "security")
        
        # Security tasks should have security-specific recommendations
        recommendations_text = " ".join(response["recommendations"])
        self.assertTrue(
            "security" in recommendations_text.lower() or 
            "validation" in recommendations_text.lower() or
            "input" in recommendations_text.lower() or
            "privilege" in recommendations_text.lower(),
            "Security task should have security-related recommendations"
        )
    
    def test_query_different_task_types(self):
        """Test query with different task types"""
        task_types = [
            "api-development",
            "refactoring",
            "testing",
            "security",
            "documentation"
        ]
        
        for task_type in task_types:
            with self.subTest(task_type=task_type):
                response = self.run_api_command([
                    "query",
                    "--agent", "organize-guru",
                    "--task-type", task_type
                ])
                
                self.assertEqual(response["task_type"], task_type)
                self.assertGreater(len(response["recommendations"]), 0, 
                    f"Should have recommendations for {task_type}")
    
    def test_assess_risk_command(self):
        """Test risk assessment command"""
        response = self.run_api_command([
            "assess-risk",
            "--agent", "secure-specialist",
            "--files", "src/auth.py,tests/test_auth.py,.github/workflows/ci.yml"
        ])
        
        # Validate response structure
        self.assertIn("overall_risk", response)
        self.assertIn("file_risks", response)
        self.assertIn("risk_factors", response)
        self.assertIn("recommendations", response)
        self.assertIn("similar_issues", response)
        
        # Validate data types
        self.assertIsInstance(response["overall_risk"], float)
        self.assertIsInstance(response["file_risks"], dict)
        self.assertIsInstance(response["risk_factors"], list)
        self.assertIsInstance(response["recommendations"], list)
        self.assertIsInstance(response["similar_issues"], list)
        
        # Validate risk scores are in valid range
        self.assertGreaterEqual(response["overall_risk"], 0.0)
        self.assertLessEqual(response["overall_risk"], 1.0)
        
        for file_path, risk in response["file_risks"].items():
            self.assertGreaterEqual(risk, 0.0)
            self.assertLessEqual(risk, 1.0)
    
    def test_assess_risk_workflow_files(self):
        """Test that workflow files are flagged as higher risk"""
        response = self.run_api_command([
            "assess-risk",
            "--agent", "workflows-tech-lead",
            "--files", ".github/workflows/test.yml"
        ])
        
        # Workflow files should have higher risk
        self.assertGreater(response["file_risks"][".github/workflows/test.yml"], 0.0)
        
        # Should have workflow-specific recommendations
        recommendations_text = " ".join(response["recommendations"])
        self.assertTrue(
            "workflow" in recommendations_text.lower() or 
            "yaml" in recommendations_text.lower(),
            "Workflow files should have workflow-specific recommendations"
        )
    
    def test_best_practices_command(self):
        """Test best practices command"""
        response = self.run_api_command([
            "best-practices",
            "--agent", "refactor-champion"
        ])
        
        # Validate response structure
        self.assertIn("agent_id", response)
        self.assertIn("best_practices", response)
        
        # Validate data
        self.assertEqual(response["agent_id"], "refactor-champion")
        self.assertIsInstance(response["best_practices"], list)
        self.assertGreater(len(response["best_practices"]), 0,
            "Should have at least some best practices")
    
    def test_warnings_command(self):
        """Test warnings command"""
        response = self.run_api_command([
            "warnings",
            "--agent", "secure-specialist",
            "--task-type", "security"
        ])
        
        # Validate response structure
        self.assertIn("agent_id", response)
        self.assertIn("warnings", response)
        
        # Validate data
        self.assertEqual(response["agent_id"], "secure-specialist")
        self.assertIsInstance(response["warnings"], list)
        self.assertGreater(len(response["warnings"]), 0,
            "Should have at least some warnings")
    
    def test_warnings_task_specific(self):
        """Test that warnings are task-specific"""
        # Test refactoring warnings
        refactor_response = self.run_api_command([
            "warnings",
            "--agent", "refactor-champion",
            "--task-type", "refactoring"
        ])
        
        warnings_text = " ".join(refactor_response["warnings"])
        self.assertTrue(
            "behavior" in warnings_text.lower() or
            "refactor" in warnings_text.lower(),
            "Refactoring warnings should mention behavior preservation"
        )
    
    def test_confidence_scores(self):
        """Test that confidence scores are in valid range"""
        response = self.run_api_command([
            "query",
            "--agent", "engineer-master",
            "--task-type", "api-development"
        ])
        
        confidence = response["confidence"]
        self.assertGreaterEqual(confidence, 0.0, "Confidence should be >= 0")
        self.assertLessEqual(confidence, 1.0, "Confidence should be <= 1")
    
    def test_risk_levels(self):
        """Test that risk levels are valid values"""
        agents = ["engineer-master", "secure-specialist", "refactor-champion"]
        
        for agent in agents:
            with self.subTest(agent=agent):
                response = self.run_api_command([
                    "query",
                    "--agent", agent,
                    "--task-type", "general"
                ])
                
                self.assertIn(response["risk_level"], ["low", "medium", "high"],
                    f"Risk level must be low, medium, or high for {agent}")
    
    def test_graceful_fallback(self):
        """Test that API provides guidance even with no historical data for agent"""
        # Use an agent that likely has no profile
        response = self.run_api_command([
            "query",
            "--agent", "nonexistent-agent",
            "--task-type", "general"
        ])
        
        # Should still provide useful guidance
        self.assertGreater(len(response["recommendations"]), 0,
            "Should provide recommendations even for unknown agent")
        self.assertGreater(len(response["best_practices"]), 0,
            "Should provide best practices even for unknown agent")
    
    def test_similar_failures_structure(self):
        """Test that similar failures have correct structure"""
        response = self.run_api_command([
            "query",
            "--agent", "engineer-master",
            "--task-type", "api-development"
        ])
        
        for failure in response["similar_failures"]:
            self.assertIn("pr_number", failure)
            self.assertIn("title", failure)
            self.assertIn("failure_type", failure)
            self.assertIn("lesson", failure)
            
            self.assertIsInstance(failure["pr_number"], int)
            self.assertIsInstance(failure["title"], str)
            self.assertIsInstance(failure["failure_type"], str)
            self.assertIsInstance(failure["lesson"], str)
    
    def test_timestamp_format(self):
        """Test that timestamp is in ISO 8601 format"""
        response = self.run_api_command([
            "query",
            "--agent", "engineer-master",
            "--task-type", "api-development"
        ])
        
        timestamp = response["timestamp"]
        # Should be parseable as ISO 8601
        from datetime import datetime
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            self.fail(f"Timestamp is not valid ISO 8601 format: {timestamp}")
    
    def test_api_returns_actionable_recommendations(self):
        """Test that recommendations are actionable (start with emoji or action verb)"""
        response = self.run_api_command([
            "query",
            "--agent", "organize-guru",
            "--task-type", "refactoring"
        ])
        
        for recommendation in response["recommendations"]:
            # Should start with emoji (✅) or be a clear action statement
            self.assertTrue(
                recommendation.startswith("✅") or
                any(recommendation.lower().startswith(verb) for verb in 
                    ["ensure", "include", "add", "write", "test", "validate", "follow"]),
                f"Recommendation should be actionable: {recommendation}"
            )
    
    def test_api_script_is_executable(self):
        """Test that the API script is executable"""
        import os
        self.assertTrue(
            os.access(self.api_script, os.X_OK),
            "API script should be executable"
        )
    
    def test_help_command(self):
        """Test that help command works"""
        result = subprocess.run(
            ["python3", str(self.api_script), "--help"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Agent Learning API", result.stdout)
        self.assertIn("query", result.stdout)
        self.assertIn("assess-risk", result.stdout)
        self.assertIn("best-practices", result.stdout)
        self.assertIn("warnings", result.stdout)


class TestAPIIntegration(unittest.TestCase):
    """Test integration with agent assignment workflow"""
    
    def test_assignment_script_calls_api(self):
        """Test that assignment script contains API integration"""
        assignment_script = Path("tools/assign-copilot-to-issue.sh")
        self.assertTrue(assignment_script.exists(), "Assignment script must exist")
        
        with open(assignment_script) as f:
            content = f.read()
        
        # Should call the Agent Learning API
        self.assertIn("agent-learning-api.py", content,
            "Assignment script should call agent-learning-api.py")
        self.assertIn("learning_guidance", content,
            "Assignment script should query learning guidance")
    
    def test_api_documentation_exists(self):
        """Test that API documentation exists"""
        readme = Path("tools/AGENT_LEARNING_API_README.md")
        self.assertTrue(readme.exists(), "API README must exist")
        
        with open(readme) as f:
            content = f.read()
        
        # Should contain key sections
        self.assertIn("Agent Learning API", content)
        self.assertIn("@APIs-architect", content)
        self.assertIn("CLI Interface", content)
        self.assertIn("Integration", content)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAgentLearningAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
