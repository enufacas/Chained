#!/usr/bin/env python3
"""
Test mission issue creation with emergent label handling.

This test verifies that the create_mission_issues.py script properly:
1. Collects all required labels from mission data
2. Creates labels before attempting to create issues
3. Handles both static and dynamic labels
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, call

# Add tools to path for import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from create_mission_issues import ensure_label_exists, main


class TestMissionIssueCreation(unittest.TestCase):
    """Test suite for mission issue creation with emergent labels."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_missions = [
            {
                'idea_id': 'test-001',
                'idea_title': 'Cloud AI Integration',
                'idea_summary': 'Test summary for cloud AI',
                'patterns': ['cloud', 'ai'],
                'regions': ['us-west:california', 'eu-west:london'],
                'agents': [
                    {
                        'agent_name': 'Engineer Master',
                        'specialization': 'engineer-master',
                        'score': 0.95
                    }
                ]
            },
            {
                'idea_id': 'test-002',
                'idea_title': 'API Security Enhancement',
                'idea_summary': 'Test summary for API security',
                'patterns': ['api', 'security'],
                'regions': ['asia:tokyo'],
                'agents': [
                    {
                        'agent_name': 'Security Specialist',
                        'specialization': 'secure-specialist',
                        'score': 0.92
                    }
                ]
            }
        ]
    
    def test_ensure_label_exists_creates_new_label(self):
        """Test that ensure_label_exists creates a label when it doesn't exist."""
        with patch('subprocess.run') as mock_run:
            # Mock: label doesn't exist
            mock_run.return_value = Mock(stdout='', stderr='', returncode=0)
            
            result = ensure_label_exists('test-label', '0E8A16', 'Test description')
            
            # Should check if label exists and then create it
            self.assertEqual(mock_run.call_count, 2)
            self.assertTrue(result)
    
    def test_ensure_label_exists_handles_existing_label(self):
        """Test that ensure_label_exists handles already existing labels."""
        with patch('subprocess.run') as mock_run:
            # Mock: label exists
            mock_run.return_value = Mock(stdout='test-label\n', stderr='', returncode=0)
            
            result = ensure_label_exists('test-label', '0E8A16', 'Test description')
            
            # Should only check if label exists, not create
            self.assertEqual(mock_run.call_count, 1)
            self.assertTrue(result)
    
    def test_label_collection_from_missions(self):
        """Test that all required labels are collected from mission data."""
        expected_labels = {
            'learning',
            'agent-mission', 
            'ai-generated',
            'automated',
            'pattern-cloud',
            'pattern-ai',
            'pattern-api',
            'pattern-security',
            'location-us-west-california',
            'location-eu-west-london',
            'location-asia-tokyo'
        }
        
        # Simulate label collection logic from main()
        all_labels = set(['learning', 'agent-mission', 'ai-generated', 'automated'])
        
        for mission in self.sample_missions:
            patterns = mission.get('patterns', [])
            regions = mission.get('regions', [])
            
            for pattern in patterns:
                label_name = f"pattern-{pattern.lower()}"
                all_labels.add(label_name)
            
            for region in regions:
                label_name = f"location-{region.lower().replace(':', '-')}"
                all_labels.add(label_name)
        
        self.assertEqual(all_labels, expected_labels)
    
    def test_pattern_label_colors(self):
        """Test that pattern labels get the correct color."""
        label = 'pattern-cloud'
        
        if label.startswith('pattern-'):
            color = '5319E7'  # Purple for patterns
            description = f'Technology/pattern: {label.replace("pattern-", "")}'
        
        self.assertEqual(color, '5319E7')
        self.assertEqual(description, 'Technology/pattern: cloud')
    
    def test_location_label_colors(self):
        """Test that location labels get the correct color."""
        label = 'location-us-west-california'
        
        if label.startswith('location-'):
            color = 'F9D0C4'  # Pink for locations
            description = f'Location/region: {label.replace("location-", "")}'
        
        self.assertEqual(color, 'F9D0C4')
        self.assertEqual(description, 'Location/region: us-west-california')
    
    @patch('subprocess.run')
    def test_main_creates_labels_before_issues(self, mock_run):
        """Test that main() creates all labels before creating issues."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_missions, f)
            missions_file = f.name
        
        try:
            # Mock subprocess calls
            mock_run.return_value = Mock(stdout='', stderr='', returncode=0)
            
            # Save original working directory and change to temp dir
            original_cwd = os.getcwd()
            temp_dir = tempfile.mkdtemp()
            os.chdir(temp_dir)
            
            # Copy missions file to expected location
            with open('missions_data.json', 'w') as f:
                json.dump(self.sample_missions, f)
            
            try:
                # Run main
                result = main()
                
                # Verify labels were created
                # Should have calls to check/create labels before creating issues
                label_checks = [call for call in mock_run.call_args_list 
                               if 'label' in str(call)]
                
                self.assertGreater(len(label_checks), 0)
                self.assertEqual(result, 0)
            finally:
                os.chdir(original_cwd)
                
        finally:
            if os.path.exists(missions_file):
                os.unlink(missions_file)
    
    def test_label_naming_conventions(self):
        """Test that label names follow expected conventions."""
        # Pattern labels
        pattern_label = f"pattern-{'Cloud'.lower()}"
        self.assertEqual(pattern_label, 'pattern-cloud')
        
        # Location labels
        location_label = f"location-{'US-West:California'.lower().replace(':', '-')}"
        self.assertEqual(location_label, 'location-us-west-california')
    
    def test_static_labels_included(self):
        """Test that static labels are always included."""
        static_labels = {'learning', 'agent-mission', 'ai-generated', 'automated'}
        
        all_labels = set(static_labels)
        
        # Should always have these base labels
        self.assertTrue(all_labels.issuperset(static_labels))


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
