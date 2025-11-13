#!/usr/bin/env python3
"""
Tests for Chained TV Episode Generator

Tests episode generation, JSON formatting, and story logic.
"""

import unittest
import json
import sys
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from generate_episode import EpisodeGenerator


class TestEpisodeGenerator(unittest.TestCase):
    """Test episode generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = EpisodeGenerator(token="fake_token", repo="owner/repo")
    
    def test_initialization(self):
        """Test generator initialization"""
        self.assertEqual(self.generator.owner, "owner")
        self.assertEqual(self.generator.repo_name, "repo")
        self.assertEqual(self.generator.token, "fake_token")
    
    def test_quiet_episode_generation(self):
        """Test generation of quiet/filler episode"""
        episode = self.generator._generate_quiet_episode()
        
        # Verify structure
        self.assertIn('date', episode)
        self.assertIn('title', episode)
        self.assertIn('scenes', episode)
        
        # Verify content
        self.assertEqual(episode['title'], "The Calm Before the Storm")
        self.assertIsInstance(episode['scenes'], list)
        self.assertGreater(len(episode['scenes']), 0)
        
        # Verify scene structure
        for scene in episode['scenes']:
            self.assertIn('bg', scene)
            self.assertIn('narration', scene)
            self.assertIn('characters', scene)
            self.assertIsInstance(scene['characters'], list)
    
    def test_episode_with_no_activity(self):
        """Test episode generation with empty issues and PRs"""
        episode = self.generator.generate_episode([], [])
        
        # Should generate quiet episode
        self.assertIn('date', episode)
        self.assertIn('title', episode)
        self.assertIn('scenes', episode)
        self.assertGreater(len(episode['scenes']), 0)
    
    def test_episode_with_merged_prs(self):
        """Test episode generation with merged PRs"""
        mock_pr = {
            'number': 123,
            'title': 'Test PR',
            'state': 'closed',
            'merged_at': '2025-11-13T00:00:00Z',
            'user': {'login': 'testuser'},
            'additions': 100,
            'deletions': 50
        }
        
        episode = self.generator.generate_episode([], [mock_pr])
        
        # Verify episode structure
        self.assertIn('title', episode)
        self.assertIn('scenes', episode)
        self.assertGreater(len(episode['scenes']), 0)
        
        # Should include merge-related content
        scenes_text = json.dumps(episode['scenes'])
        self.assertTrue('merge' in scenes_text.lower() or 'Merge' in scenes_text)
    
    def test_episode_with_open_prs(self):
        """Test episode generation with open PRs"""
        mock_pr = {
            'number': 456,
            'title': 'Open PR',
            'state': 'open',
            'user': {'login': 'developer'},
            'additions': 50,
            'deletions': 25
        }
        
        episode = self.generator.generate_episode([], [mock_pr])
        
        # Verify structure
        self.assertIn('scenes', episode)
        self.assertGreater(len(episode['scenes']), 0)
        
        # Should mention the open PR
        scenes_text = json.dumps(episode['scenes'])
        self.assertIn('456', scenes_text)
    
    def test_episode_with_closed_issues(self):
        """Test episode generation with closed issues"""
        mock_issue = {
            'number': 789,
            'title': 'Bug fix',
            'state': 'closed',
            'user': {'login': 'bugfixer'}
        }
        
        episode = self.generator.generate_episode([mock_issue], [])
        
        # Verify structure
        self.assertIn('scenes', episode)
        self.assertGreater(len(episode['scenes']), 0)
    
    def test_title_generation_merged_prs(self):
        """Test title generation for merged PRs"""
        mock_prs = [
            {'number': 1, 'merged_at': '2025-11-13T00:00:00Z', 'user': {'login': 'dev1'}},
            {'number': 2, 'merged_at': '2025-11-13T00:00:00Z', 'user': {'login': 'dev2'}},
            {'number': 3, 'merged_at': '2025-11-13T00:00:00Z', 'user': {'login': 'dev3'}},
            {'number': 4, 'merged_at': '2025-11-13T00:00:00Z', 'user': {'login': 'dev4'}},
        ]
        
        actors = {'dev1', 'dev2', 'dev3', 'dev4'}
        title = self.generator._generate_title([], mock_prs, actors)
        
        # Should generate merge-related title
        self.assertIn('Merge', title)
    
    def test_intro_scene_generation(self):
        """Test intro scene generation"""
        mock_issues = [{'number': 1, 'state': 'open', 'user': {'login': 'user1'}}]
        mock_prs = [{'number': 2, 'state': 'open', 'user': {'login': 'user2'}}]
        actors = {'user1', 'user2'}
        
        scene = self.generator._generate_intro_scene(mock_issues, mock_prs, actors)
        
        # Verify scene structure
        self.assertIn('bg', scene)
        self.assertIn('narration', scene)
        self.assertIn('characters', scene)
        
        # Verify narration mentions activity
        self.assertIn('2 events', scene['narration'])
        self.assertIn('2 collaborators', scene['narration'])
    
    def test_character_structure(self):
        """Test that characters have required fields"""
        episode = self.generator._generate_quiet_episode()
        
        for scene in episode['scenes']:
            for character in scene['characters']:
                self.assertIn('name', character)
                self.assertIn('side', character)
                self.assertIn('mood', character)
                self.assertIn('line', character)
                
                # Verify valid side values
                self.assertIn(character['side'], ['left', 'right', 'center'])
                
                # Verify valid mood values
                self.assertIn(character['mood'], ['determined', 'smug', 'angry', 'worried', 'happy'])
    
    def test_scene_structure(self):
        """Test that scenes have required fields"""
        episode = self.generator._generate_quiet_episode()
        
        for scene in episode['scenes']:
            self.assertIn('bg', scene)
            self.assertIn('narration', scene)
            self.assertIn('characters', scene)
            
            # Verify valid background values
            self.assertIn(scene['bg'], ['night', 'alert', 'calm', 'lab'])
            
            # Verify narration is a non-empty string
            self.assertIsInstance(scene['narration'], str)
            self.assertGreater(len(scene['narration']), 0)
    
    def test_episode_json_serializable(self):
        """Test that generated episodes are JSON serializable"""
        episode = self.generator.generate_episode([], [])
        
        # Should not raise exception
        json_str = json.dumps(episode)
        
        # Should be able to parse back
        parsed = json.loads(json_str)
        self.assertEqual(parsed['title'], episode['title'])
    
    def test_merge_scene_generation(self):
        """Test merge scene generation"""
        mock_prs = [
            {
                'number': 100,
                'user': {'login': 'contributor'},
                'additions': 200,
                'deletions': 50,
                'merged_at': '2025-11-13T00:00:00Z'
            }
        ]
        
        scene = self.generator._generate_merge_scene(mock_prs)
        
        # Verify scene exists
        self.assertIsNotNone(scene)
        self.assertIn('bg', scene)
        self.assertIn('narration', scene)
        self.assertIn('characters', scene)
        
        # Should mention the PR number
        self.assertIn('100', scene['narration'])
    
    def test_closed_pr_scene_generation(self):
        """Test closed unmerged PR scene generation"""
        mock_prs = [
            {
                'number': 200,
                'state': 'closed',
                'user': {'login': 'developer'}
            }
        ]
        
        scene = self.generator._generate_closed_pr_scene(mock_prs)
        
        # Verify scene
        self.assertIsNotNone(scene)
        self.assertIn('200', scene['narration'])
        self.assertIn('closed', scene['narration'].lower())
    
    def test_multiple_authors(self):
        """Test episode with multiple authors"""
        mock_prs = [
            {'number': 1, 'state': 'open', 'user': {'login': 'dev1'}},
            {'number': 2, 'state': 'open', 'user': {'login': 'dev2'}},
            {'number': 3, 'state': 'open', 'user': {'login': 'dev3'}},
        ]
        
        episode = self.generator.generate_episode([], mock_prs)
        
        # Should generate episode
        self.assertIn('scenes', episode)
        self.assertGreater(len(episode['scenes']), 0)


class TestEpisodeJSONFormat(unittest.TestCase):
    """Test JSON format compliance"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = EpisodeGenerator(token="fake_token", repo="owner/repo")
    
    def test_date_is_iso_format(self):
        """Test that date is in ISO format"""
        episode = self.generator.generate_episode([], [])
        
        # Should be parseable as datetime
        date = datetime.fromisoformat(episode['date'].replace('Z', '+00:00'))
        self.assertIsInstance(date, datetime)
    
    def test_all_required_fields_present(self):
        """Test that all required fields are present"""
        episode = self.generator.generate_episode([], [])
        
        required_fields = ['date', 'title', 'scenes']
        for field in required_fields:
            self.assertIn(field, episode)
    
    def test_scenes_is_list(self):
        """Test that scenes is a list"""
        episode = self.generator.generate_episode([], [])
        self.assertIsInstance(episode['scenes'], list)
    
    def test_characters_is_list(self):
        """Test that characters is a list in each scene"""
        episode = self.generator.generate_episode([], [])
        
        for scene in episode['scenes']:
            self.assertIsInstance(scene['characters'], list)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("Running Chained TV Episode Generator Tests")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEpisodeGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestEpisodeJSONFormat))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
