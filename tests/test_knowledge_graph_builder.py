#!/usr/bin/env python3
"""
Tests for Knowledge Graph Builder
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from knowledge_graph_builder import (
    CodeAnalyzer, GitAnalyzer, TestCoverageAnalyzer, KnowledgeGraphBuilder
)


class TestCodeAnalyzer(unittest.TestCase):
    """Test code analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.analyzer = CodeAnalyzer(self.test_dir)
    
    def test_analyze_simple_file(self):
        """Test analyzing a simple Python file"""
        # Create test file
        test_file = Path(self.test_dir) / "test_module.py"
        test_file.write_text("""
import os
import sys
from typing import Dict, List

def hello_world():
    return "Hello"

class TestClass:
    def method(self):
        pass
""")
        
        result = self.analyzer.analyze_file(test_file)
        
        self.assertIsNotNone(result)
        # from typing import Dict, List creates 2 separate imports, so >= 3
        self.assertGreaterEqual(len(result['imports']), 3)
        self.assertGreaterEqual(len(result['functions']), 1)
        self.assertGreaterEqual(len(result['classes']), 1)
        # Check specific names exist
        func_names = [f['name'] for f in result['functions']]
        class_names = [c['name'] for c in result['classes']]
        self.assertIn('hello_world', func_names)
        self.assertIn('TestClass', class_names)
    
    def test_extract_imports(self):
        """Test import extraction"""
        test_file = Path(self.test_dir) / "imports.py"
        test_file.write_text("""
import json
from pathlib import Path
from typing import Dict, List
""")
        
        result = self.analyzer.analyze_file(test_file)
        
        imports = result['imports']
        # from typing import Dict, List creates 2 separate imports
        self.assertGreaterEqual(len(imports), 3)
        
        # Check import types
        import_types = {imp['type'] for imp in imports}
        self.assertIn('import', import_types)
        self.assertIn('from_import', import_types)
    
    def test_extract_function_calls(self):
        """Test function call extraction"""
        test_file = Path(self.test_dir) / "calls.py"
        test_file.write_text("""
def test():
    print("hello")
    len([1, 2, 3])
    custom_function()
""")
        
        result = self.analyzer.analyze_file(test_file)
        
        self.assertIn('print', result['function_calls'])
        self.assertIn('len', result['function_calls'])
        self.assertIn('custom_function', result['function_calls'])
    
    def test_invalid_file(self):
        """Test handling of invalid Python file"""
        test_file = Path(self.test_dir) / "invalid.py"
        test_file.write_text("this is not valid python {{{")
        
        result = self.analyzer.analyze_file(test_file)
        
        self.assertIsNone(result)


class TestGitAnalyzer(unittest.TestCase):
    """Test git history analysis"""
    
    def test_extract_agent_from_commit(self):
        """Test agent extraction from commit messages"""
        analyzer = GitAnalyzer('.')
        
        # Test with agent mentions
        self.assertEqual(
            analyzer.extract_agent_from_commit("feature-architect: Add new feature"),
            'feature-architect'
        )
        self.assertEqual(
            analyzer.extract_agent_from_commit("bug-hunter fixed critical issue"),
            'bug-hunter'
        )
        self.assertEqual(
            analyzer.extract_agent_from_commit("Regular commit message"),
            'unknown'
        )


class TestTestCoverageAnalyzer(unittest.TestCase):
    """Test test coverage analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.analyzer = TestCoverageAnalyzer(self.test_dir)
    
    def test_find_test_files(self):
        """Test finding test files"""
        # Create test files
        (Path(self.test_dir) / "test_module.py").touch()
        (Path(self.test_dir) / "module_test.py").touch()
        (Path(self.test_dir) / "module.py").touch()
        
        test_files = self.analyzer.find_test_files()
        
        self.assertEqual(len(test_files), 2)
        self.assertTrue(any('test_module.py' in f for f in test_files))
        self.assertTrue(any('module_test.py' in f for f in test_files))
    
    def test_map_tests_to_code(self):
        """Test mapping tests to code"""
        test_files = ['test_agent_system.py', 'test_knowledge_graph.py']
        code_analysis = [
            {'filepath': 'agent_system.py', 'functions': []},
            {'filepath': 'knowledge_graph.py', 'functions': []},
            {'filepath': 'other.py', 'functions': []}
        ]
        
        mapping = self.analyzer.map_tests_to_code(test_files, code_analysis)
        
        self.assertIn('test_agent_system.py', mapping)
        self.assertTrue(any('agent_system' in f for f in mapping['test_agent_system.py']))


class TestKnowledgeGraphBuilder(unittest.TestCase):
    """Test complete knowledge graph building"""
    
    def test_build_graph_structure(self):
        """Test that build_graph returns correct structure"""
        builder = KnowledgeGraphBuilder('.')
        graph = builder.build_graph()
        
        # Check structure
        self.assertIn('metadata', graph)
        self.assertIn('nodes', graph)
        self.assertIn('relationships', graph)
        self.assertIn('statistics', graph)
        
        # Check metadata
        self.assertIn('generated_at', graph['metadata'])
        self.assertIn('total_files', graph['metadata'])
        
        # Check nodes
        self.assertIsInstance(graph['nodes'], list)
        if graph['nodes']:
            node = graph['nodes'][0]
            self.assertIn('id', node)
            self.assertIn('type', node)
            self.assertIn('label', node)
        
        # Check relationships
        self.assertIsInstance(graph['relationships'], list)
        if graph['relationships']:
            rel = graph['relationships'][0]
            self.assertIn('source', rel)
            self.assertIn('target', rel)
            self.assertIn('type', rel)
        
        # Check statistics
        self.assertIn('total_nodes', graph['statistics'])
        self.assertIn('total_relationships', graph['statistics'])
    
    def test_relationship_types(self):
        """Test that various relationship types are created"""
        builder = KnowledgeGraphBuilder('.')
        graph = builder.build_graph()
        
        relationship_types = {rel['type'] for rel in graph['relationships']}
        
        # Should have at least imports and tests
        self.assertTrue(len(relationship_types) > 0)
        self.assertIn('imports', relationship_types)
        self.assertIn('tests', relationship_types)
    
    def test_node_types(self):
        """Test that various node types are created"""
        builder = KnowledgeGraphBuilder('.')
        graph = builder.build_graph()
        
        node_types = {node['type'] for node in graph['nodes']}
        
        # Should have code files and test files
        self.assertIn('code_file', node_types)
        self.assertIn('test_file', node_types)
    
    def test_save_graph(self):
        """Test saving graph to file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = f"{tmpdir}/test-graph.json"
            builder = KnowledgeGraphBuilder('.')
            builder.save_graph(output_path)
            
            # Check file exists
            self.assertTrue(Path(output_path).exists())
            
            # Check file is valid JSON
            with open(output_path) as f:
                data = json.load(f)
            
            self.assertIn('nodes', data)
            self.assertIn('relationships', data)


class TestGraphIntegrity(unittest.TestCase):
    """Test graph integrity and consistency"""
    
    def setUp(self):
        """Load generated graph"""
        graph_path = 'docs/data/codebase-graph.json'
        if Path(graph_path).exists():
            with open(graph_path) as f:
                self.graph = json.load(f)
        else:
            self.graph = None
    
    def test_graph_exists(self):
        """Test that graph file was generated"""
        self.assertIsNotNone(self.graph, "Graph file not found. Run knowledge-graph-builder.py first")
    
    def test_all_relationship_nodes_exist(self):
        """Test that all relationship endpoints exist as nodes"""
        if not self.graph:
            self.skipTest("Graph not available")
        
        node_ids = {node['id'] for node in self.graph['nodes']}
        
        for rel in self.graph['relationships']:
            self.assertIn(rel['source'], node_ids, 
                         f"Relationship source {rel['source']} not in nodes")
            self.assertIn(rel['target'], node_ids,
                         f"Relationship target {rel['target']} not in nodes")
    
    def test_statistics_match_data(self):
        """Test that statistics match actual data"""
        if not self.graph:
            self.skipTest("Graph not available")
        
        stats = self.graph['statistics']
        
        # Check node count
        actual_nodes = len(self.graph['nodes'])
        self.assertEqual(stats['total_nodes'], actual_nodes)
        
        # Check relationship count
        actual_relationships = len(self.graph['relationships'])
        self.assertEqual(stats['total_relationships'], actual_relationships)
    
    def test_no_self_references(self):
        """Test that relationships don't point to themselves"""
        if not self.graph:
            self.skipTest("Graph not available")
        
        for rel in self.graph['relationships']:
            self.assertNotEqual(rel['source'], rel['target'],
                              f"Self-reference found: {rel['source']}")
    
    def test_relationship_types_are_valid(self):
        """Test that relationship types are from expected set"""
        if not self.graph:
            self.skipTest("Graph not available")
        
        valid_types = {'imports', 'tests', 'worked_on', 'changes_with'}
        
        for rel in self.graph['relationships']:
            self.assertIn(rel['type'], valid_types,
                         f"Invalid relationship type: {rel['type']}")


def main():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
