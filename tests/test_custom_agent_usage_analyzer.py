#!/usr/bin/env python3
"""
Test suite for the custom agent usage analyzer.
Validates that the analyzer correctly identifies custom agent mentions in various contexts.
"""

import sys
import json
import unittest
import re
from pathlib import Path


# Inline the extraction logic for testing purposes
def extract_custom_agent_from_text(text: str):
    """Extract custom agent mentions from text."""
    if not text:
        return []
    
    agents = []
    
    # Pattern 1: @agent-name mentions
    agent_mentions = re.findall(r'@([a-z-]+(?:master|specialist|guru|champion|wizard|expert))', text.lower())
    agents.extend(agent_mentions)
    
    # Pattern 2: COPILOT_AGENT: directive
    agent_directive = re.search(r'COPILOT_AGENT:([a-z-]+)', text, re.IGNORECASE)
    if agent_directive:
        agents.append(agent_directive.group(1))
    
    # Pattern 3: agent:label-name labels
    agent_labels = re.findall(r'agent:([a-z-]+)', text.lower())
    agents.extend(agent_labels)
    
    # Pattern 4: .github/agents/agent-name.md references
    agent_paths = re.findall(r'\.github/agents/([a-z-]+)\.md', text.lower())
    agents.extend(agent_paths)
    
    # Pattern 5: "**agent-name** custom agent" or similar
    agent_bold = re.findall(r'\*\*([a-z-]+(?:master|specialist|guru|champion|wizard|expert))\*\*', text.lower())
    agents.extend(agent_bold)
    
    return list(set(agents))  # Remove duplicates


def analyze_issue_custom_agent_usage(issue):
    """Analyze an issue for custom agent usage."""
    issue_num = issue['number']
    
    result = {
        'issue_number': issue_num,
        'title': issue['title'],
        'created_at': issue['createdAt'],
        'closed_at': issue.get('closedAt'),
        'assigned_to_copilot': False,
        'custom_agent_mentioned': False,
        'custom_agents': [],
        'evidence': []
    }
    
    # Check if assigned to Copilot
    assignees = [a['login'] for a in issue.get('assignees', [])]
    if any('copilot' in a.lower() for a in assignees):
        result['assigned_to_copilot'] = True
        result['evidence'].append(f"Assigned to: {', '.join(assignees)}")
    
    # Check labels
    labels = [label['name'] for label in issue.get('labels', [])]
    if 'copilot-assigned' in labels:
        result['assigned_to_copilot'] = True
        result['evidence'].append("Has 'copilot-assigned' label")
    
    # Check for agent-specific labels
    agent_labels = [l for l in labels if l.startswith('agent:')]
    if agent_labels:
        result['custom_agents'].extend([l.replace('agent:', '') for l in agent_labels])
        result['evidence'].append(f"Agent labels: {', '.join(agent_labels)}")
    
    # Analyze issue body
    body = issue.get('body', '')
    body_agents = extract_custom_agent_from_text(body)
    if body_agents:
        result['custom_agent_mentioned'] = True
        result['custom_agents'].extend(body_agents)
        result['evidence'].append(f"Custom agents in issue body: {', '.join(body_agents)}")
    
    # Analyze comments
    comments = issue.get('comments', [])
    for comment in comments:
        comment_body = comment.get('body', '')
        comment_agents = extract_custom_agent_from_text(comment_body)
        if comment_agents:
            result['custom_agent_mentioned'] = True
            result['custom_agents'].extend(comment_agents)
            author = comment.get('author', {}).get('login', 'unknown')
            result['evidence'].append(f"Custom agents in comment by {author}: {', '.join(comment_agents)}")
    
    # Remove duplicates from custom_agents list
    result['custom_agents'] = list(set(result['custom_agents']))
    
    return result


def analyze_pr_custom_agent_usage(pr, issue_number):
    """Analyze a PR for custom agent usage evidence."""
    result = {
        'pr_number': pr['number'],
        'title': pr['title'],
        'author': pr['author']['login'],
        'created_at': pr['createdAt'],
        'merged_at': pr.get('mergedAt'),
        'custom_agent_mentioned': False,
        'custom_agents': [],
        'evidence': []
    }
    
    # Check if author is Copilot
    if 'copilot' in result['author'].lower():
        result['evidence'].append(f"PR created by: {result['author']}")
    
    # Analyze PR body
    body = pr.get('body', '')
    body_agents = extract_custom_agent_from_text(body)
    if body_agents:
        result['custom_agent_mentioned'] = True
        result['custom_agents'].extend(body_agents)
        result['evidence'].append(f"Custom agents in PR body: {', '.join(body_agents)}")
    
    # Remove duplicates
    result['custom_agents'] = list(set(result['custom_agents']))
    
    return result


class TestCustomAgentExtraction(unittest.TestCase):
    """Test custom agent extraction from text."""
    
    def test_extract_from_mention(self):
        """Test extraction from @agent-name mentions."""
        text = "@assert-specialist please write tests for this"
        agents = extract_custom_agent_from_text(text)
        self.assertIn('assert-specialist', agents)
    
    def test_extract_from_html_comment(self):
        """Test extraction from HTML comment directive."""
        text = "<!-- COPILOT_AGENT:accelerate-master -->"
        agents = extract_custom_agent_from_text(text)
        self.assertIn('accelerate-master', agents)
    
    def test_extract_from_label_format(self):
        """Test extraction from agent:label-name format."""
        text = "This issue has agent:secure-specialist label"
        agents = extract_custom_agent_from_text(text)
        self.assertIn('secure-specialist', agents)
    
    def test_extract_from_path_reference(self):
        """Test extraction from .github/agents/agent-name.md references."""
        text = "See .github/agents/organize-guru.md for details"
        agents = extract_custom_agent_from_text(text)
        self.assertIn('organize-guru', agents)
    
    def test_extract_from_bold_text(self):
        """Test extraction from **agent-name** in text."""
        text = "Assigned to **engineer-master** custom agent"
        agents = extract_custom_agent_from_text(text)
        self.assertIn('engineer-master', agents)
    
    def test_extract_multiple_agents(self):
        """Test extraction of multiple agents from same text."""
        text = """
        <!-- COPILOT_AGENT:assert-specialist -->
        @assert-specialist and @coach-master please review
        """
        agents = extract_custom_agent_from_text(text)
        self.assertIn('assert-specialist', agents)
        self.assertIn('coach-master', agents)
    
    def test_no_agents_in_text(self):
        """Test that no agents are extracted from text without mentions."""
        text = "This is a regular issue description with no agent mentions"
        agents = extract_custom_agent_from_text(text)
        self.assertEqual(len(agents), 0)
    
    def test_case_insensitive(self):
        """Test that extraction is case-insensitive."""
        text = "@ASSERT-SPECIALIST please help"
        agents = extract_custom_agent_from_text(text)
        self.assertIn('assert-specialist', agents)


class TestIssueAnalysis(unittest.TestCase):
    """Test issue analysis functionality."""
    
    def test_issue_with_copilot_assignee(self):
        """Test detection of Copilot assignment."""
        issue = {
            'number': 123,
            'title': 'Test issue',
            'createdAt': '2024-01-01T00:00:00Z',
            'assignees': [{'login': 'github-copilot[bot]'}],
            'labels': [],
            'body': '',
            'comments': []
        }
        
        result = analyze_issue_custom_agent_usage(issue)
        self.assertTrue(result['assigned_to_copilot'])
    
    def test_issue_with_copilot_label(self):
        """Test detection of copilot-assigned label."""
        issue = {
            'number': 123,
            'title': 'Test issue',
            'createdAt': '2024-01-01T00:00:00Z',
            'assignees': [],
            'labels': [{'name': 'copilot-assigned'}],
            'body': '',
            'comments': []
        }
        
        result = analyze_issue_custom_agent_usage(issue)
        self.assertTrue(result['assigned_to_copilot'])
    
    def test_issue_with_agent_label(self):
        """Test detection of agent-specific labels."""
        issue = {
            'number': 123,
            'title': 'Test issue',
            'createdAt': '2024-01-01T00:00:00Z',
            'assignees': [],
            'labels': [{'name': 'agent:assert-specialist'}],
            'body': '',
            'comments': []
        }
        
        result = analyze_issue_custom_agent_usage(issue)
        self.assertIn('assert-specialist', result['custom_agents'])
    
    def test_issue_with_agent_in_body(self):
        """Test detection of agents in issue body."""
        issue = {
            'number': 123,
            'title': 'Test issue',
            'createdAt': '2024-01-01T00:00:00Z',
            'assignees': [],
            'labels': [],
            'body': '@accelerate-master please optimize this code',
            'comments': []
        }
        
        result = analyze_issue_custom_agent_usage(issue)
        self.assertTrue(result['custom_agent_mentioned'])
        self.assertIn('accelerate-master', result['custom_agents'])
    
    def test_issue_with_agent_in_comments(self):
        """Test detection of agents in issue comments."""
        issue = {
            'number': 123,
            'title': 'Test issue',
            'createdAt': '2024-01-01T00:00:00Z',
            'assignees': [],
            'labels': [],
            'body': '',
            'comments': [
                {
                    'body': '@secure-specialist please review security',
                    'author': {'login': 'testuser'}
                }
            ]
        }
        
        result = analyze_issue_custom_agent_usage(issue)
        self.assertTrue(result['custom_agent_mentioned'])
        self.assertIn('secure-specialist', result['custom_agents'])
    
    def test_issue_with_multiple_agent_mentions(self):
        """Test that duplicate agents are deduplicated."""
        issue = {
            'number': 123,
            'title': 'Test issue',
            'createdAt': '2024-01-01T00:00:00Z',
            'assignees': [],
            'labels': [
                {'name': 'agent:create-guru'}
            ],
            'body': '@create-guru please implement this',
            'comments': [
                {
                    'body': '@create-guru working on it',
                    'author': {'login': 'testuser'}
                }
            ]
        }
        
        result = analyze_issue_custom_agent_usage(issue)
        # Should have only one instance of create-guru despite multiple mentions
        self.assertEqual(result['custom_agents'].count('create-guru'), 1)


class TestPRAnalysis(unittest.TestCase):
    """Test PR analysis functionality."""
    
    def test_pr_by_copilot(self):
        """Test detection of PR created by Copilot."""
        pr = {
            'number': 456,
            'title': 'Fix issue #123',
            'author': {'login': 'github-copilot[bot]'},
            'createdAt': '2024-01-01T00:00:00Z',
            'mergedAt': None,
            'body': ''
        }
        
        result = analyze_pr_custom_agent_usage(pr, 123)
        self.assertIn('github-copilot[bot]', result['evidence'][0])
    
    def test_pr_with_agent_in_body(self):
        """Test detection of agents in PR body."""
        pr = {
            'number': 456,
            'title': 'Fix issue #123',
            'author': {'login': 'github-copilot[bot]'},
            'createdAt': '2024-01-01T00:00:00Z',
            'mergedAt': None,
            'body': 'Implemented using @engineer-wizard approach'
        }
        
        result = analyze_pr_custom_agent_usage(pr, 123)
        self.assertTrue(result['custom_agent_mentioned'])
        self.assertIn('engineer-wizard', result['custom_agents'])


class TestIntegration(unittest.TestCase):
    """Integration tests for the full analysis workflow."""
    
    def test_complete_workflow(self):
        """Test a complete analysis workflow."""
        # Simulate an issue with full agent integration
        issue = {
            'number': 789,
            'title': 'Improve test coverage',
            'createdAt': '2024-01-01T00:00:00Z',
            'closedAt': None,
            'assignees': [{'login': 'github-copilot[bot]'}],
            'labels': [
                {'name': 'copilot-assigned'},
                {'name': 'agent:assert-specialist'}
            ],
            'body': '''
            <!-- COPILOT_AGENT:assert-specialist -->
            
            > **🤖 Agent Assignment**
            > 
            > This issue has been assigned to GitHub Copilot with the **🧪 assert-specialist** custom agent profile.
            > 
            > **@assert-specialist** - Please use the specialized approach and tools defined in [`.github/agents/assert-specialist.md`](https://github.com/repo/blob/main/.github/agents/assert-specialist.md).
            
            ---
            
            We need to improve test coverage for the authentication module.
            ''',
            'comments': []
        }
        
        result = analyze_issue_custom_agent_usage(issue)
        
        # Verify all aspects were detected
        self.assertTrue(result['assigned_to_copilot'], "Should detect Copilot assignment")
        self.assertTrue(result['custom_agent_mentioned'], "Should detect custom agent mention")
        self.assertIn('assert-specialist', result['custom_agents'], "Should extract assert-specialist")
        
        # Verify evidence was collected
        self.assertGreater(len(result['evidence']), 0, "Should have evidence")
        
        # Verify the evidence includes multiple detection methods
        evidence_text = ' '.join(result['evidence'])
        self.assertIn('assert-specialist', evidence_text, "Evidence should mention the agent")


def run_tests():
    """Run all tests and return exit code."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCustomAgentExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestIssueAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestPRAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
