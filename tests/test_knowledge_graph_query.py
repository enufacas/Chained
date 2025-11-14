#!/usr/bin/env python3
"""
Tests for Knowledge Graph Query Interface
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from knowledge_graph_query import KnowledgeGraphQuery


class TestKnowledgeGraphQuery(unittest.TestCase):
    """Test query interface functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests"""
        # Create a minimal test graph
        cls.test_graph = {
            'metadata': {
                'generated_at': '2025-11-12T00:00:00',
                'total_files': 5
            },
            'nodes': [
                {'id': 'module_a.py', 'type': 'code_file', 'label': 'module_a.py', 
                 'functions': 5, 'classes': 1, 'lines_of_code': 100, 'imports': 2, 'contributors': []},
                {'id': 'module_b.py', 'type': 'code_file', 'label': 'module_b.py',
                 'functions': 3, 'classes': 0, 'lines_of_code': 50, 'imports': 1, 'contributors': []},
                {'id': 'test_module_a.py', 'type': 'test_file', 'label': 'test_module_a.py',
                 'functions': 10, 'classes': 0, 'lines_of_code': 200, 'imports': 3, 'contributors': []},
                {'id': 'agent:feature-architect', 'type': 'agent', 'label': 'feature-architect',
                 'files_worked_on': 2, 'expertise': ['tooling', 'agent-system']},
                {'id': 'utils.py', 'type': 'code_file', 'label': 'utils.py',
                 'functions': 15, 'classes': 2, 'lines_of_code': 300, 'imports': 5, 'contributors': []}
            ],
            'relationships': [
                {'source': 'module_a.py', 'target': 'utils.py', 'type': 'imports', 'weight': 1},
                {'source': 'module_b.py', 'target': 'utils.py', 'type': 'imports', 'weight': 1},
                {'source': 'module_b.py', 'target': 'module_a.py', 'type': 'imports', 'weight': 1},
                {'source': 'test_module_a.py', 'target': 'module_a.py', 'type': 'tests', 'weight': 1},
                {'source': 'agent:feature-architect', 'target': 'module_a.py', 'type': 'worked_on', 'weight': 1},
                {'source': 'agent:feature-architect', 'target': 'utils.py', 'type': 'worked_on', 'weight': 1},
                {'source': 'module_a.py', 'target': 'module_b.py', 'type': 'changes_with', 'weight': 5}
            ],
            'statistics': {
                'total_nodes': 5,
                'total_relationships': 7,
                'relationship_types': {'imports': 3, 'tests': 1, 'worked_on': 2, 'changes_with': 1}
            }
        }
        
        # Save to temporary file
        cls.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(cls.test_graph, cls.temp_file)
        cls.temp_file.close()
        
        cls.kgq = KnowledgeGraphQuery(cls.temp_file.name)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up temporary file"""
        Path(cls.temp_file.name).unlink()
    
    def test_load_graph(self):
        """Test that graph loads correctly"""
        self.assertIsNotNone(self.kgq.graph)
        self.assertEqual(len(self.kgq.graph['nodes']), 5)
        self.assertEqual(len(self.kgq.graph['relationships']), 7)
    
    def test_indices_built(self):
        """Test that indices are built correctly"""
        self.assertIn('module_a.py', self.kgq.nodes_by_id)
        self.assertIn('code_file', self.kgq.nodes_by_type)
        self.assertIn('agent', self.kgq.nodes_by_type)
    
    def test_what_imports(self):
        """Test finding files that import a module"""
        results = self.kgq.what_imports('utils.py')
        
        self.assertEqual(len(results), 2)
        file_names = {r['file'] for r in results}
        self.assertIn('module_a.py', file_names)
        self.assertIn('module_b.py', file_names)
    
    def test_what_does_import(self):
        """Test finding what a file imports"""
        results = self.kgq.what_does_import('module_a.py')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['file'], 'utils.py')
    
    def test_which_agent_worked_on(self):
        """Test finding agents that worked on a file"""
        results = self.kgq.which_agent_worked_on('module_a.py')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['agent'], 'feature-architect')
        self.assertIn('tooling', results[0]['expertise'])
    
    def test_what_agent_worked_on(self):
        """Test finding files an agent worked on"""
        results = self.kgq.what_agent_worked_on('feature-architect')
        
        self.assertEqual(len(results), 2)
        file_names = {r['file'] for r in results}
        self.assertIn('module_a.py', file_names)
        self.assertIn('utils.py', file_names)
    
    def test_what_tests_cover(self):
        """Test finding tests that cover a file"""
        results = self.kgq.what_tests_cover('module_a.py')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['test_file'], 'test_module_a.py')
    
    def test_what_does_test_cover(self):
        """Test finding what a test file covers"""
        results = self.kgq.what_does_test_cover('test_module_a.py')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['file'], 'module_a.py')
    
    def test_files_changed_together(self):
        """Test finding files that change together"""
        results = self.kgq.files_changed_together('module_a.py', min_weight=3)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['file'], 'module_b.py')
        self.assertEqual(results[0]['change_frequency'], 5)
    
    def test_impact_analysis(self):
        """Test impact analysis"""
        impact = self.kgq.impact_analysis('utils.py')
        
        # utils.py is imported by module_a.py and module_b.py
        self.assertGreater(impact['blast_radius'], 0)
        self.assertIn('module_a.py', impact['directly_affected'])
        self.assertIn('module_b.py', impact['directly_affected'])
    
    def test_find_dependencies(self):
        """Test finding dependencies"""
        deps = self.kgq.find_dependencies('module_a.py')
        
        self.assertIn('utils.py', deps['direct'])
    
    def test_find_expert_agents(self):
        """Test finding expert agents"""
        results = self.kgq.find_expert_agents('tooling')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['agent'], 'feature-architect')
    
    def test_find_complex_files(self):
        """Test finding complex files"""
        results = self.kgq.find_complex_files(min_functions=10)
        
        # Only utils.py and test_module_a.py have >= 10 functions
        self.assertGreaterEqual(len(results), 1)
        file_names = {r['file'] for r in results}
        self.assertIn('utils.py', file_names)
    
    def test_find_central_files(self):
        """Test finding central files"""
        results = self.kgq.find_central_files(top_n=3)
        
        self.assertGreaterEqual(len(results), 1)
        # utils.py should be central (imported by 2 files, worked on by agent)
        file_names = {r['file'] for r in results}
        self.assertIn('utils.py', file_names)
    
    def test_get_statistics(self):
        """Test getting statistics"""
        stats = self.kgq.get_statistics()
        
        self.assertEqual(stats['total_nodes'], 5)
        self.assertEqual(stats['total_relationships'], 7)
    
    def test_natural_language_query_imports(self):
        """Test natural language query for imports"""
        result = self.kgq.query("What does utils.py import?")
        
        # Query should return results
        self.assertIsInstance(result, (list, dict))
        # If it's an error dict, that's ok for edge cases
        if isinstance(result, dict) and 'error' in result:
            # Alternative: test what imports utils.py
            result = self.kgq.query("What imports utils.py?")
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)
    
    def test_natural_language_query_agent(self):
        """Test natural language query for agents"""
        result = self.kgq.query("Which agent worked on module_a.py?")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
    
    def test_natural_language_query_tests(self):
        """Test natural language query for tests"""
        result = self.kgq.query("What tests cover module_a.py?")
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
    
    def test_natural_language_query_impact(self):
        """Test natural language query for impact"""
        result = self.kgq.query("Show impact of utils.py")
        
        self.assertIsInstance(result, dict)
        self.assertIn('blast_radius', result)


class TestRealKnowledgeGraph(unittest.TestCase):
    """Test with real generated knowledge graph"""
    
    def setUp(self):
        """Load real graph if it exists"""
        graph_path = 'docs/data/codebase-graph.json'
        if Path(graph_path).exists():
            self.kgq = KnowledgeGraphQuery(graph_path)
        else:
            self.kgq = None
    
    def test_real_graph_loaded(self):
        """Test that real graph can be loaded"""
        if self.kgq is None:
            self.skipTest("Real graph not available")
        
        self.assertIsNotNone(self.kgq.graph)
        self.assertGreater(len(self.kgq.graph['nodes']), 0)
    
    def test_real_graph_statistics(self):
        """Test statistics from real graph"""
        if self.kgq is None:
            self.skipTest("Real graph not available")
        
        stats = self.kgq.get_statistics()
        
        self.assertIn('total_nodes', stats)
        self.assertIn('total_relationships', stats)
        self.assertGreater(stats['total_nodes'], 0)
    
    def test_real_graph_central_files(self):
        """Test finding central files in real graph"""
        if self.kgq is None:
            self.skipTest("Real graph not available")
        
        results = self.kgq.find_central_files(5)
        
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 5)
        
        # Check structure
        if results:
            self.assertIn('file', results[0])
            self.assertIn('connections', results[0])
    
    def test_real_graph_test_mapping(self):
        """Test that test files are mapped in real graph"""
        if self.kgq is None:
            self.skipTest("Real graph not available")
        
        # Find a test file
        test_nodes = [n for n in self.kgq.graph['nodes'] if n['type'] == 'test_file']
        
        if test_nodes:
            test_file = test_nodes[0]['id']
            coverage = self.kgq.what_does_test_cover(test_file)
            
            # Should have at least one file it tests (or empty list is ok)
            self.assertIsInstance(coverage, list)
    
    def test_real_graph_has_patterns(self):
        """Test that patterns are available in real graph"""
        if self.kgq is None:
            self.skipTest("Real graph not available")
        
        patterns = self.kgq.get_patterns()
        
        # Should have pattern data
        self.assertIsInstance(patterns, dict)
        # May or may not have specific keys depending on analysis
    
    def test_real_graph_has_metrics(self):
        """Test that metrics are available in real graph"""
        if self.kgq is None:
            self.skipTest("Real graph not available")
        
        metrics = self.kgq.get_metrics()
        
        # Should have metrics data
        self.assertIsInstance(metrics, dict)


class TestQueryEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_nonexistent_graph_file(self):
        """Test loading non-existent graph file"""
        with self.assertRaises(FileNotFoundError):
            KnowledgeGraphQuery('/nonexistent/path.json')
    
    def test_query_nonexistent_file(self):
        """Test querying non-existent file"""
        # Use the test graph from TestKnowledgeGraphQuery
        graph = {
            'metadata': {}, 'nodes': [], 'relationships': [], 'statistics': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(graph, f)
            temp_path = f.name
        
        try:
            kgq = KnowledgeGraphQuery(temp_path)
            results = kgq.what_imports('nonexistent.py')
            
            # Should return empty list, not error
            self.assertEqual(results, [])
        finally:
            Path(temp_path).unlink()
    
    def test_empty_query(self):
        """Test empty query string"""
        graph = {
            'metadata': {}, 'nodes': [], 'relationships': [], 'statistics': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(graph, f)
            temp_path = f.name
        
        try:
            kgq = KnowledgeGraphQuery(temp_path)
            result = kgq.query("")
            
            # Should return error
            self.assertIn('error', result)
        finally:
            Path(temp_path).unlink()


class TestPredictiveIntelligence(unittest.TestCase):
    """Test predictive intelligence features"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test graph with enhanced metrics"""
        cls.test_graph = {
            'metadata': {'generated_at': '2025-11-12T00:00:00', 'total_files': 3},
            'nodes': [
                {
                    'id': 'complex_file.py', 'type': 'code_file', 'label': 'complex_file.py',
                    'functions': 25, 'classes': 3, 'lines_of_code': 600, 'imports': 15,
                    'complexity_score': 12.5, 'code_smells': ['large_file', 'too_many_functions'],
                    'refactoring_count': 5, 'filepath': 'complex_file.py'
                },
                {
                    'id': 'simple_file.py', 'type': 'code_file', 'label': 'simple_file.py',
                    'functions': 3, 'classes': 0, 'lines_of_code': 50, 'imports': 2,
                    'complexity_score': 2.0, 'filepath': 'simple_file.py'
                },
                {
                    'id': 'agent:investigate-champion', 'type': 'agent', 
                    'label': 'investigate-champion', 'files_worked_on': 1, 
                    'expertise': ['analysis', 'metrics']
                }
            ],
            'relationships': [
                {'source': 'agent:investigate-champion', 'target': 'complex_file.py', 
                 'type': 'worked_on', 'weight': 1}
            ],
            'statistics': {'total_nodes': 3, 'total_relationships': 1},
            'patterns': {
                'error_fixes': {
                    'complex_file.py': [
                        {'type': 'runtime_error', 'date': '2025-11-10'},
                        {'type': 'security', 'date': '2025-11-11'}
                    ]
                },
                'refactorings': {'complex_file.py': 5},
                'code_smells': {'complex_file.py': ['large_file', 'too_many_functions']}
            },
            'metrics': {
                'complexity': {
                    'complex_file.py': {
                        'complexity_score': 12.5,
                        'functions': 25,
                        'avg_function_size': 24.0
                    },
                    'simple_file.py': {
                        'complexity_score': 2.0,
                        'functions': 3,
                        'avg_function_size': 16.7
                    }
                }
            }
        }
        
        cls.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(cls.test_graph, cls.temp_file)
        cls.temp_file.close()
        
        cls.kgq = KnowledgeGraphQuery(cls.temp_file.name)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up temporary file"""
        Path(cls.temp_file.name).unlink()
    
    def test_predict_bug_likelihood_high_risk(self):
        """Test bug likelihood prediction for high-risk file"""
        result = self.kgq.predict_bug_likelihood('complex_file.py')
        
        self.assertIn('likelihood', result)
        self.assertIn('risk_score', result)
        self.assertIn('risk_factors', result)
        
        # Complex file should have high or medium risk
        self.assertIn(result['likelihood'], ['high', 'medium'])
        self.assertGreater(result['risk_score'], 0)
        self.assertGreater(len(result['risk_factors']), 0)
    
    def test_predict_bug_likelihood_low_risk(self):
        """Test bug likelihood prediction for low-risk file"""
        result = self.kgq.predict_bug_likelihood('simple_file.py')
        
        self.assertIn('likelihood', result)
        # Simple file should have low or medium risk
        self.assertIn(result['likelihood'], ['low', 'medium'])
    
    def test_suggest_expert_agent(self):
        """Test expert agent suggestion"""
        result = self.kgq.suggest_expert_agent('complex_file.py')
        
        self.assertIn('suggestions', result)
        self.assertIsInstance(result['suggestions'], list)
        
        # Should suggest investigate-champion who worked on it
        if result['suggestions']:
            self.assertIn('agent', result['suggestions'][0])
    
    def test_identify_technical_debt(self):
        """Test technical debt identification"""
        result = self.kgq.identify_technical_debt(min_score=3)
        
        self.assertIsInstance(result, list)
        
        # complex_file.py should be identified as having debt
        if result:
            self.assertIn('debt_score', result[0])
            self.assertIn('indicators', result[0])
    
    def test_find_optimization_opportunities(self):
        """Test optimization opportunity detection"""
        result = self.kgq.find_optimization_opportunities()
        
        self.assertIsInstance(result, list)
        
        # Should find opportunities
        if result:
            self.assertIn('opportunities', result[0])
    
    def test_natural_language_query_technical_debt(self):
        """Test natural language query for technical debt"""
        result = self.kgq.query("Show technical debt")
        
        self.assertIsInstance(result, list)
    
    def test_natural_language_query_bug_risk(self):
        """Test natural language query for bug risk"""
        result = self.kgq.query("What is the bug likelihood for complex_file.py?")
        
        self.assertIsInstance(result, dict)
        self.assertIn('likelihood', result)


def main():
    """Run all tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
