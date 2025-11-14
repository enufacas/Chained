#!/usr/bin/env python3
"""
Security tests for the registry validator.

Tests the registry_validator.py tool to ensure it properly:
- Validates registry schema
- Detects data corruption
- Identifies security issues
- Handles edge cases

Created by: @secure-ninja (Moxie Marlinspike)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Import the validator
from registry_validator import RegistryValidator, RegistryValidationError


class TestRegistryValidator(unittest.TestCase):
    """Test suite for the registry validator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_registry = Path(self.temp_dir) / "registry.json"
        
        # Valid registry template
        self.valid_registry = {
            "version": "2.0.0",
            "agents": [
                {
                    "id": "agent-1234567890",
                    "name": "🤖 Test Agent",
                    "human_name": "Test Agent",
                    "specialization": "test-specialist",
                    "status": "active",
                    "spawned_at": "2025-11-13T00:00:00.000000Z",
                    "personality": "test personality",
                    "communication_style": "test style",
                    "traits": {
                        "creativity": 50,
                        "caution": 50,
                        "speed": 50
                    },
                    "metrics": {
                        "issues_resolved": 0,
                        "prs_merged": 0,
                        "reviews_given": 0,
                        "code_quality_score": 0.5,
                        "overall_score": 0.0
                    },
                    "contributions": []
                }
            ],
            "hall_of_fame": [],
            "system_lead": None,
            "config": {
                "spawn_interval_hours": 3,
                "max_active_agents": 10,
                "elimination_threshold": 0.3,
                "promotion_threshold": 0.85,
                "metrics_weight": {
                    "code_quality": 0.3,
                    "issue_resolution": 0.2,
                    "pr_success": 0.2,
                    "peer_review": 0.15,
                    "creativity": 0.15
                }
            }
        }
    
    def _write_registry(self, data):
        """Write registry data to temp file."""
        with open(self.temp_registry, 'w') as f:
            json.dump(data, f)
    
    def test_valid_registry(self):
        """Test that a valid registry passes validation."""
        self._write_registry(self.valid_registry)
        validator = RegistryValidator(self.temp_registry)
        
        self.assertTrue(validator.validate())
        self.assertEqual(len(validator.errors), 0)
    
    def test_missing_version(self):
        """Test detection of missing version field."""
        data = self.valid_registry.copy()
        del data['version']
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('version' in error.lower() for error in validator.errors))
    
    def test_invalid_version_format(self):
        """Test detection of invalid version format."""
        data = self.valid_registry.copy()
        data['version'] = "2.0"  # Should be X.Y.Z
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('version' in error.lower() for error in validator.errors))
    
    def test_missing_required_fields(self):
        """Test detection of missing required fields."""
        data = self.valid_registry.copy()
        del data['agents']
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('agents' in error.lower() for error in validator.errors))
    
    def test_invalid_agent_id_format(self):
        """Test detection of invalid agent ID format."""
        data = self.valid_registry.copy()
        data['agents'][0]['id'] = "invalid-id"
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('agent id' in error.lower() for error in validator.errors))
    
    def test_duplicate_agent_ids(self):
        """Test detection of duplicate agent IDs."""
        data = self.valid_registry.copy()
        # Add duplicate agent
        duplicate_agent = data['agents'][0].copy()
        data['agents'].append(duplicate_agent)
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('duplicate' in error.lower() for error in validator.errors))
    
    def test_invalid_agent_status(self):
        """Test detection of invalid agent status."""
        data = self.valid_registry.copy()
        data['agents'][0]['status'] = "invalid_status"
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('status' in error.lower() for error in validator.errors))
    
    def test_traits_out_of_range(self):
        """Test detection of trait values out of range."""
        data = self.valid_registry.copy()
        data['agents'][0]['traits']['creativity'] = 150  # Should be 0-100
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('creativity' in error.lower() for error in validator.errors))
    
    def test_negative_metrics(self):
        """Test detection of negative metric values."""
        data = self.valid_registry.copy()
        data['agents'][0]['metrics']['issues_resolved'] = -1
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('issues_resolved' in error.lower() for error in validator.errors))
    
    def test_score_out_of_range(self):
        """Test detection of scores outside 0-1 range."""
        data = self.valid_registry.copy()
        data['agents'][0]['metrics']['code_quality_score'] = 1.5
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('code_quality_score' in error.lower() for error in validator.errors))
    
    def test_invalid_timestamp(self):
        """Test detection of invalid timestamp format."""
        data = self.valid_registry.copy()
        data['agents'][0]['spawned_at'] = "not-a-timestamp"
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('timestamp' in error.lower() for error in validator.errors))
    
    def test_future_timestamp_warning(self):
        """Test that future timestamps generate warnings."""
        data = self.valid_registry.copy()
        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        data['agents'][0]['spawned_at'] = future_time
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        validator.validate()
        self.assertTrue(any('future' in warning.lower() for warning in validator.warnings))
    
    def test_config_validation(self):
        """Test configuration validation."""
        data = self.valid_registry.copy()
        data['config']['elimination_threshold'] = 1.5  # Should be 0-1
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('elimination_threshold' in error.lower() for error in validator.errors))
    
    def test_metrics_weight_sum(self):
        """Test that metrics weights should sum to 1.0."""
        data = self.valid_registry.copy()
        data['config']['metrics_weight'] = {
            "code_quality": 0.5,
            "issue_resolution": 0.5,
            "pr_success": 0.5  # Total = 1.5
        }
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        validator.validate()
        # Should generate a warning
        self.assertTrue(any('weight' in warning.lower() for warning in validator.warnings))
    
    def test_malformed_json(self):
        """Test handling of malformed JSON."""
        with open(self.temp_registry, 'w') as f:
            f.write("{invalid json")
        
        validator = RegistryValidator(self.temp_registry)
        # Should return False and have errors
        self.assertFalse(validator.validate())
        self.assertTrue(len(validator.errors) > 0)
    
    def test_missing_file(self):
        """Test handling of missing registry file."""
        nonexistent = Path(self.temp_dir) / "nonexistent.json"
        validator = RegistryValidator(nonexistent)
        
        # Should return False and have errors
        self.assertFalse(validator.validate())
        self.assertTrue(len(validator.errors) > 0)
    
    def test_empty_agents_list(self):
        """Test that empty agents list is valid."""
        data = self.valid_registry.copy()
        data['agents'] = []
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertTrue(validator.validate())
    
    def test_max_active_agents_validation(self):
        """Test validation of max_active_agents config."""
        data = self.valid_registry.copy()
        data['config']['max_active_agents'] = 0  # Should be at least 1
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('max_active_agents' in error.lower() for error in validator.errors))
    
    def test_spawn_interval_validation(self):
        """Test validation of spawn_interval_hours config."""
        data = self.valid_registry.copy()
        data['config']['spawn_interval_hours'] = -1  # Should be positive
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('spawn_interval_hours' in error.lower() for error in validator.errors))
    
    def test_missing_agent_fields(self):
        """Test detection of missing agent fields."""
        data = self.valid_registry.copy()
        del data['agents'][0]['specialization']
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('specialization' in error.lower() for error in validator.errors))
    
    def test_invalid_specialization_format(self):
        """Test detection of invalid specialization format."""
        data = self.valid_registry.copy()
        data['agents'][0]['specialization'] = "invalid spec!"  # Special chars not allowed
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertFalse(validator.validate())
        self.assertTrue(any('specialization' in error.lower() for error in validator.errors))
    
    def test_report_generation(self):
        """Test that validation report is generated correctly."""
        self._write_registry(self.valid_registry)
        validator = RegistryValidator(self.temp_registry)
        validator.validate()
        
        report = validator.get_report()
        self.assertIn("Registry Security Validation", report)
        self.assertIn("validation checks passed", report)
    
    def test_report_with_errors(self):
        """Test report generation with errors."""
        data = self.valid_registry.copy()
        del data['version']
        self._write_registry(data)
        
        validator = RegistryValidator(self.temp_registry)
        validator.validate()
        
        report = validator.get_report()
        self.assertIn("Errors:", report)
        self.assertIn("version", report.lower())


class TestSecurityEdgeCases(unittest.TestCase):
    """Test edge cases and security scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_registry = Path(self.temp_dir) / "registry.json"
    
    def test_very_large_metrics(self):
        """Test handling of extremely large metric values."""
        data = {
            "version": "2.0.0",
            "agents": [{
                "id": "agent-1234567890",
                "name": "Test",
                "human_name": "Test",
                "specialization": "test-spec",
                "status": "active",
                "spawned_at": "2025-11-13T00:00:00Z",
                "personality": "test",
                "communication_style": "test",
                "traits": {"creativity": 50, "caution": 50, "speed": 50},
                "metrics": {
                    "issues_resolved": 999999999,  # Very large
                    "prs_merged": 0,
                    "reviews_given": 0,
                    "code_quality_score": 0.5,
                    "overall_score": 0.0
                },
                "contributions": []
            }],
            "config": {
                "spawn_interval_hours": 3,
                "max_active_agents": 10,
                "elimination_threshold": 0.3,
                "promotion_threshold": 0.85,
                "metrics_weight": {"code_quality": 1.0}
            }
        }
        
        with open(self.temp_registry, 'w') as f:
            json.dump(data, f)
        
        validator = RegistryValidator(self.temp_registry)
        # Should still validate (large but valid)
        self.assertTrue(validator.validate())
    
    def test_unicode_in_names(self):
        """Test handling of Unicode characters in agent names."""
        data = {
            "version": "2.0.0",
            "agents": [{
                "id": "agent-1234567890",
                "name": "🤖 Test 測試 тест",
                "human_name": "Test 測試",
                "specialization": "test-spec",
                "status": "active",
                "spawned_at": "2025-11-13T00:00:00Z",
                "personality": "test",
                "communication_style": "test",
                "traits": {"creativity": 50, "caution": 50, "speed": 50},
                "metrics": {
                    "issues_resolved": 0,
                    "prs_merged": 0,
                    "reviews_given": 0,
                    "code_quality_score": 0.5,
                    "overall_score": 0.0
                },
                "contributions": []
            }],
            "config": {
                "spawn_interval_hours": 3,
                "max_active_agents": 10,
                "elimination_threshold": 0.3,
                "promotion_threshold": 0.85,
                "metrics_weight": {"code_quality": 1.0}
            }
        }
        
        with open(self.temp_registry, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        
        validator = RegistryValidator(self.temp_registry)
        self.assertTrue(validator.validate())


def main():
    """Run the test suite."""
    print("=" * 70)
    print("🔒 Registry Validator Security Test Suite")
    print("=" * 70)
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestRegistryValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All security tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
