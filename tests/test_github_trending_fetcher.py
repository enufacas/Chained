#!/usr/bin/env python3
"""
Tests for GitHub Trending Fetcher

Tests the fetch-github-trending.py tool functionality.
"""

import sys
import os
import json
import unittest
from unittest.mock import patch, Mock

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

# Import the module
import importlib.util
spec = importlib.util.spec_from_file_location('fetcher', 'tools/fetch-github-trending.py')
fetcher_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetcher_module)

GitHubTrendingFetcher = fetcher_module.GitHubTrendingFetcher


class TestGitHubTrendingFetcher(unittest.TestCase):
    """Test cases for GitHubTrendingFetcher"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fetcher = GitHubTrendingFetcher()
    
    def test_parse_count_simple(self):
        """Test parsing simple integer strings"""
        self.assertEqual(self.fetcher._parse_count('123'), 123)
        self.assertEqual(self.fetcher._parse_count('1,234'), 1234)
        self.assertEqual(self.fetcher._parse_count('12,345'), 12345)
    
    def test_parse_count_with_k(self):
        """Test parsing strings with 'k' suffix"""
        self.assertEqual(self.fetcher._parse_count('1k'), 1000)
        self.assertEqual(self.fetcher._parse_count('1.2k'), 1200)
        self.assertEqual(self.fetcher._parse_count('12.5k'), 12500)
    
    def test_parse_count_invalid(self):
        """Test parsing invalid strings returns 0"""
        self.assertEqual(self.fetcher._parse_count('invalid'), 0)
        self.assertEqual(self.fetcher._parse_count(''), 0)
    
    def test_base_url(self):
        """Test base URL is correct"""
        self.assertEqual(GitHubTrendingFetcher.BASE_URL, 'https://github.com/trending')
    
    def test_session_headers(self):
        """Test session has proper headers"""
        self.assertIn('User-Agent', self.fetcher.session.headers)
        self.assertIn('ChainedAI', self.fetcher.session.headers['User-Agent'])
    
    @patch('requests.Session.get')
    def test_fetch_trending_success(self, mock_get):
        """Test successful fetch returns list"""
        # Mock HTML response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
        <article class="Box-row">
            <h2 class="h3">
                <a href="/test/repo">test/repo</a>
            </h2>
            <p class="col-9">Test description</p>
            <span itemprop="programmingLanguage">Python</span>
        </article>
        </html>
        '''
        mock_get.return_value = mock_response
        
        repos = self.fetcher.fetch_trending(max_repos=1)
        
        # Should return a list
        self.assertIsInstance(repos, list)
        
        # Should have made the request
        mock_get.assert_called_once()
    
    def test_fetch_trending_network_error(self):
        """Test network error returns empty list"""
        import requests
        with patch.object(self.fetcher.session, 'get', side_effect=requests.RequestException("Network error")):
            repos = self.fetcher.fetch_trending()
            
            # Should return empty list on error
            self.assertEqual(repos, [])
    
    def test_fetch_multiple_languages(self):
        """Test fetch_multiple_languages returns dict"""
        # Use a mock to avoid actual network calls
        with patch.object(self.fetcher, 'fetch_trending', return_value=[]):
            results = self.fetcher.fetch_multiple_languages(
                languages=['python', 'javascript'],
                max_per_lang=1
            )
            
            # Should return dict with language keys
            self.assertIsInstance(results, dict)
            self.assertIn('python', results)
            self.assertIn('javascript', results)


class TestGitHubTrendingIntegration(unittest.TestCase):
    """Integration tests that hit real GitHub (run sparingly)"""
    
    @unittest.skip("Skipped to avoid excessive network calls during development")
    def test_real_fetch(self):
        """Test actual fetch from GitHub (skipped by default)"""
        fetcher = GitHubTrendingFetcher()
        repos = fetcher.fetch_trending(language='python', since='daily', max_repos=3)
        
        # Should return some repos
        self.assertGreater(len(repos), 0)
        
        # Check structure of first repo
        if repos:
            repo = repos[0]
            self.assertIn('full_name', repo)
            self.assertIn('url', repo)
            self.assertIn('description', repo)
            self.assertIn('language', repo)


class TestLearningFormatConversion(unittest.TestCase):
    """Test conversion to learning system format"""
    
    def test_repo_to_learning_format(self):
        """Test converting repo data to learning format"""
        repo = {
            'full_name': 'test/repo',
            'url': 'https://github.com/test/repo',
            'description': 'Test description',
            'language': 'Python',
            'stars': 1000,
            'forks': 100,
            'stars_period_count': 50
        }
        
        # Convert to learning format (as done in workflow)
        learning = {
            'title': f"{repo['full_name']} - {repo.get('description', 'No description')[:100]}",
            'description': repo.get('description', ''),
            'url': repo['url'],
            'source': 'GitHub Trending',
            'metadata': {
                'full_name': repo['full_name'],
                'language': repo.get('language', 'Unknown'),
                'stars': repo.get('stars', 0),
                'forks': repo.get('forks', 0),
                'stars_today': repo.get('stars_period_count', 0)
            }
        }
        
        # Verify structure
        self.assertEqual(learning['source'], 'GitHub Trending')
        self.assertEqual(learning['metadata']['language'], 'Python')
        self.assertEqual(learning['metadata']['stars'], 1000)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
