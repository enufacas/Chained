#!/usr/bin/env python3
"""
Tests for Self-Documenting AI from Discussions

Tests the automatic documentation generation from AI discussions.

Author: @create-botter
Date: 2025-12-16
"""

import unittest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add tools to path
tools_dir = Path(__file__).parent.parent / 'tools'
sys.path.insert(0, str(tools_dir))

# Import with proper name handling
import importlib.util
spec = importlib.util.spec_from_file_location(
    "auto_doc_from_discussions",
    tools_dir / "auto-doc-from-discussions.py"
)
auto_doc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auto_doc_module)

SelfDocumentingAI = auto_doc_module.SelfDocumentingAI
DocumentationEntry = auto_doc_module.DocumentationEntry


class TestSelfDocumentingAI(unittest.TestCase):
    """Test cases for SelfDocumentingAI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_discussions_dir = Path('learnings/discussions')
        self.test_output_dir = Path('/tmp/test_docs')
        
        # Create output directory
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create AI instance
        self.doc_ai = SelfDocumentingAI(
            discussions_dir=str(self.test_discussions_dir),
            output_dir=str(self.test_output_dir)
        )
    
    def tearDown(self):
        """Clean up test artifacts"""
        # Remove test output files
        for file in self.test_output_dir.glob('*.md'):
            file.unlink()
    
    def test_initialization(self):
        """Test SelfDocumentingAI initialization"""
        self.assertIsNotNone(self.doc_ai)
        self.assertEqual(
            self.doc_ai.discussions_dir,
            self.test_discussions_dir
        )
        self.assertEqual(
            self.doc_ai.output_dir,
            self.test_output_dir
        )
    
    def test_categories_defined(self):
        """Test that documentation categories are properly defined"""
        self.assertIn('agent_behavior', self.doc_ai.categories)
        self.assertIn('process', self.doc_ai.categories)
        self.assertIn('technical_decision', self.doc_ai.categories)
        self.assertEqual(
            self.doc_ai.categories['agent_behavior'],
            'Agent System Behavior'
        )
    
    def test_categorize_insights(self):
        """Test insight categorization"""
        test_insights = [
            {
                'insight_type': 'agent_behavior',
                'content': 'Agent performed well',
                'confidence': 0.8
            },
            {
                'insight_type': 'process',
                'content': 'Process improvement needed',
                'confidence': 0.7
            },
            {
                'insight_type': 'agent_behavior',
                'content': 'Another agent insight',
                'confidence': 0.9
            }
        ]
        
        categorized = self.doc_ai.categorize_insights(test_insights)
        
        self.assertEqual(len(categorized['agent_behavior']), 2)
        self.assertEqual(len(categorized['process']), 1)
    
    def test_generate_master_index(self):
        """Test master index generation"""
        categories = ['agent_behavior', 'process']
        
        index_content = self.doc_ai.generate_master_index(categories)
        
        self.assertIn('Self-Documented AI Learnings Index', index_content)
        self.assertIn('Agent System Behavior', index_content)
        self.assertIn('Development Processes', index_content)
        self.assertIn('@create-botter', index_content)
    
    def test_generate_topic_documentation(self):
        """Test topic documentation generation"""
        test_insights = [
            {
                'issue_number': 123,
                'issue_title': 'Test Issue',
                'content': 'Important insight about agents',
                'confidence': 0.85,
                'tags': ['agent', 'test'],
                'timestamp': '2025-12-16T10:00:00Z'
            }
        ]
        
        doc_content = self.doc_ai.generate_topic_documentation(
            'agent_behavior',
            test_insights
        )
        
        self.assertIn('Agent System Behavior', doc_content)
        self.assertIn('Issue #123', doc_content)
        self.assertIn('Test Issue', doc_content)
        self.assertIn('Important insight', doc_content)
        self.assertIn('@create-botter', doc_content)
    
    def test_generate_decision_log(self):
        """Test decision log generation"""
        test_insights = [
            {
                'issue_number': 456,
                'content': 'Decided to use Python for automation',
                'confidence': 0.9,
                'timestamp': '2025-12-16T10:00:00Z'
            }
        ]
        
        decision_log = self.doc_ai.generate_decision_log(test_insights)
        
        self.assertIn('Technical Decision Log', decision_log)
        self.assertIn('#456', decision_log)
        self.assertIn('Python for automation', decision_log)
    
    def test_write_documentation(self):
        """Test writing documentation to files"""
        test_docs = {
            'test_doc.md': '# Test Documentation\n\nContent here.',
            'test_index.md': '# Index\n\nLinks here.'
        }
        
        files_written = self.doc_ai.write_documentation(test_docs)
        
        self.assertEqual(files_written, 2)
        self.assertTrue((self.test_output_dir / 'test_doc.md').exists())
        self.assertTrue((self.test_output_dir / 'test_index.md').exists())
    
    def test_documentation_entry_dataclass(self):
        """Test DocumentationEntry dataclass"""
        entry = DocumentationEntry(
            id='test-123',
            title='Test Entry',
            category='agent_behavior',
            content='Test content',
            source_issue=123,
            source_discussion='discussion_issue_123.json',
            confidence=0.85,
            tags=['test', 'agent'],
            timestamp='2025-12-16T10:00:00Z',
            related_entries=['test-124']
        )
        
        self.assertEqual(entry.id, 'test-123')
        self.assertEqual(entry.title, 'Test Entry')
        self.assertEqual(entry.category, 'agent_behavior')
        
        # Test to_dict conversion
        entry_dict = entry.to_dict()
        self.assertIn('id', entry_dict)
        self.assertIn('title', entry_dict)
        self.assertEqual(entry_dict['confidence'], 0.85)
    
    def test_extract_discussions_handles_missing_files(self):
        """Test that extract_discussions handles missing files gracefully"""
        # Use a non-existent directory
        doc_ai = SelfDocumentingAI(
            discussions_dir='/tmp/nonexistent_discussions',
            output_dir=str(self.test_output_dir)
        )
        
        discussions = doc_ai.extract_discussions()
        
        # Should return empty list, not crash
        self.assertEqual(discussions, [])


class TestIntegration(unittest.TestCase):
    """Integration tests for full workflow"""
    
    def test_full_generation_workflow(self):
        """Test complete documentation generation workflow"""
        # Use real discussions directory if it exists
        discussions_dir = Path('learnings/discussions')
        output_dir = Path('/tmp/test_integration_docs')
        
        if not discussions_dir.exists():
            self.skipTest("Discussions directory not found")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            doc_ai = SelfDocumentingAI(
                discussions_dir=str(discussions_dir),
                output_dir=str(output_dir)
            )
            
            # Generate documentation
            docs = doc_ai.generate_all_documentation()
            
            # Should generate at least README
            self.assertIn('README.md', docs)
            self.assertGreater(len(docs), 0)
            
            # Write documentation
            files_written = doc_ai.write_documentation(docs)
            self.assertGreater(files_written, 0)
            
            # Verify README exists and has content
            readme_path = output_dir / 'README.md'
            self.assertTrue(readme_path.exists())
            
            with open(readme_path, 'r') as f:
                content = f.read()
                self.assertIn('Self-Documented AI', content)
                self.assertIn('@create-botter', content)
        
        finally:
            # Clean up
            for file in output_dir.glob('*.md'):
                file.unlink()
            output_dir.rmdir()


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSelfDocumentingAI))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
