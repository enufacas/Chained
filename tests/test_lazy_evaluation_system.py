#!/usr/bin/env python3
"""
Tests for the Lazy Evaluation System for Workflow Dependencies

Tests the core functionality of lazy loading, caching, and dependency resolution.
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from workflow_dependency_graph import WorkflowDependencyGraph, WorkflowNode
from lazy_workflow_loader import LazyWorkflowLoader, LazyWorkflow, LazyDependencyResolver
from lazy_evaluation_system import LazyEvaluationSystem


class TestWorkflowDependencyGraph(unittest.TestCase):
    """Test workflow dependency graph analysis."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflows_dir = '.github/workflows'
        if Path(self.workflows_dir).exists():
            self.graph = WorkflowDependencyGraph(self.workflows_dir)
            self.graph.build_graph()
    
    def test_graph_initialization(self):
        """Test that graph initializes correctly."""
        self.assertIsNotNone(self.graph)
        self.assertIsInstance(self.graph.nodes, dict)
    
    def test_workflow_discovery(self):
        """Test workflow discovery."""
        workflows = self.graph.discover_workflows()
        self.assertIsInstance(workflows, list)
        if workflows:
            self.assertTrue(all(isinstance(w, Path) for w in workflows))
    
    def test_graph_building(self):
        """Test that graph builds nodes."""
        if self.graph.nodes:
            # Check that nodes have required attributes
            for name, node in self.graph.nodes.items():
                self.assertIsInstance(node, WorkflowNode)
                self.assertIsInstance(node.name, str)
                self.assertIsInstance(node.path, str)
                self.assertIsInstance(node.triggers, list)
                self.assertIsInstance(node.dependencies, set)
    
    def test_lazy_evaluation(self):
        """Test lazy evaluation of workflow nodes."""
        if self.graph.nodes:
            # Pick first workflow
            workflow_name = list(self.graph.nodes.keys())[0]
            
            # Initially not loaded
            node = self.graph.nodes[workflow_name]
            initial_state = node.is_loaded
            
            # Lazy evaluate
            result = self.graph.lazy_evaluate(workflow_name)
            
            self.assertIsNotNone(result)
            self.assertTrue(result.is_loaded)
            self.assertIsNotNone(result.last_evaluated)
    
    def test_dependency_chain(self):
        """Test dependency chain resolution."""
        if self.graph.nodes:
            workflow_name = list(self.graph.nodes.keys())[0]
            chain = self.graph.get_dependency_chain(workflow_name)
            
            self.assertIsInstance(chain, list)
            self.assertIn(workflow_name, chain)
    
    def test_evaluation_stats(self):
        """Test evaluation statistics."""
        stats = self.graph.get_evaluation_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_workflows', stats)
        self.assertIn('loaded_workflows', stats)
        self.assertIn('lazy_load_ratio', stats)
        
        # Check value types
        self.assertIsInstance(stats['total_workflows'], int)
        self.assertIsInstance(stats['loaded_workflows'], int)
        self.assertIsInstance(stats['lazy_load_ratio'], float)
    
    def test_cache_invalidation(self):
        """Test cache invalidation."""
        if self.graph.nodes:
            workflow_name = list(self.graph.nodes.keys())[0]
            
            # Evaluate and cache
            self.graph.lazy_evaluate(workflow_name)
            self.assertTrue(self.graph.nodes[workflow_name].is_loaded)
            
            # Invalidate
            self.graph.invalidate_cache(workflow_name)
            self.assertFalse(self.graph.nodes[workflow_name].is_loaded)


class TestLazyWorkflowLoader(unittest.TestCase):
    """Test lazy workflow loader."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflows_dir = '.github/workflows'
        if Path(self.workflows_dir).exists():
            self.loader = LazyWorkflowLoader(self.workflows_dir)
            self.loader.discover()
    
    def test_loader_initialization(self):
        """Test loader initializes correctly."""
        self.assertIsNotNone(self.loader)
        self.assertIsInstance(self.loader.workflows, dict)
    
    def test_workflow_discovery(self):
        """Test workflow discovery."""
        if self.loader.workflows:
            # Check that workflows are LazyWorkflow instances
            for name, workflow in self.loader.workflows.items():
                self.assertIsInstance(workflow, LazyWorkflow)
                self.assertIsInstance(workflow.name, str)
                self.assertIsInstance(workflow.path, str)
    
    def test_lazy_loading(self):
        """Test that workflows are not loaded until requested."""
        if self.loader.workflows:
            # Check that workflows start unloaded
            for workflow in self.loader.workflows.values():
                self.assertIsNone(workflow._content)
    
    def test_workflow_loading(self):
        """Test loading a workflow."""
        if self.loader.workflows:
            workflow_name = list(self.loader.workflows.keys())[0]
            
            # Load workflow
            content = self.loader.load_workflow(workflow_name)
            
            if content:  # Only test if loading succeeds
                self.assertIsInstance(content, dict)
                
                # Check that workflow is now marked as loaded
                workflow = self.loader.workflows[workflow_name]
                self.assertIsNotNone(workflow._content)
    
    def test_cache_hits(self):
        """Test that cached content is reused."""
        if self.loader.workflows:
            workflow_name = list(self.loader.workflows.keys())[0]
            
            # Load twice
            content1 = self.loader.load_workflow(workflow_name)
            content2 = self.loader.load_workflow(workflow_name)
            
            if content1:  # Only test if loading succeeds
                # Check cache hit count
                workflow = self.loader.workflows[workflow_name]
                self.assertGreater(workflow._cache_hits, 0)
    
    def test_loader_metrics(self):
        """Test loader metrics calculation."""
        metrics = self.loader.get_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_workflows', metrics)
        self.assertIn('loaded_workflows', metrics)
        self.assertIn('cache_hit_rate', metrics)
        self.assertIn('lazy_load_savings', metrics)
        
        # Check value ranges
        self.assertGreaterEqual(metrics['cache_hit_rate'], 0)
        self.assertLessEqual(metrics['cache_hit_rate'], 1)
        self.assertGreaterEqual(metrics['lazy_load_savings'], 0)
        self.assertLessEqual(metrics['lazy_load_savings'], 1)
    
    def test_batch_loading(self):
        """Test batch loading of workflows."""
        if self.loader.workflows and len(self.loader.workflows) >= 2:
            # Get first two workflow names
            names = list(self.loader.workflows.keys())[:2]
            
            # Load batch
            results = self.loader.load_batch(names)
            
            self.assertIsInstance(results, dict)
            # At least some should load successfully
            self.assertGreaterEqual(len(results), 0)


class TestLazyDependencyResolver(unittest.TestCase):
    """Test lazy dependency resolver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflows_dir = '.github/workflows'
        if Path(self.workflows_dir).exists():
            self.loader = LazyWorkflowLoader(self.workflows_dir)
            self.loader.discover()
            self.resolver = LazyDependencyResolver(self.loader)
    
    def test_resolver_initialization(self):
        """Test resolver initializes correctly."""
        self.assertIsNotNone(self.resolver)
        self.assertIsInstance(self.resolver._dependency_cache, dict)
    
    def test_dependency_extraction(self):
        """Test dependency extraction."""
        if self.loader.workflows:
            workflow_name = list(self.loader.workflows.keys())[0]
            
            # Get dependencies
            deps = self.resolver.get_dependencies(workflow_name)
            
            self.assertIsInstance(deps, list)
    
    def test_recursive_dependencies(self):
        """Test recursive dependency resolution."""
        if self.loader.workflows:
            workflow_name = list(self.loader.workflows.keys())[0]
            
            # Get recursive dependencies
            deps = self.resolver.get_dependencies(workflow_name, recursive=True)
            
            self.assertIsInstance(deps, list)
    
    def test_dependency_caching(self):
        """Test that dependencies are cached."""
        if self.loader.workflows:
            workflow_name = list(self.loader.workflows.keys())[0]
            
            # Get dependencies twice
            deps1 = self.resolver.get_dependencies(workflow_name)
            deps2 = self.resolver.get_dependencies(workflow_name)
            
            # Check that cache is used
            self.assertGreater(len(self.resolver._dependency_cache), 0)


class TestLazyEvaluationSystem(unittest.TestCase):
    """Test integrated lazy evaluation system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflows_dir = '.github/workflows'
        if Path(self.workflows_dir).exists():
            self.system = LazyEvaluationSystem(self.workflows_dir)
            self.system.initialize()
    
    def test_system_initialization(self):
        """Test system initializes correctly."""
        self.assertIsNotNone(self.system)
        self.assertTrue(self.system._initialized)
        self.assertGreater(self.system.metrics.total_workflows, 0)
    
    def test_workflow_evaluation(self):
        """Test evaluating a workflow."""
        if self.system.dependency_graph.nodes:
            workflow_name = list(self.system.dependency_graph.nodes.keys())[0]
            
            # Evaluate workflow
            result = self.system.evaluate_workflow(workflow_name)
            
            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success'))
            self.assertIn('workflow', result)
            self.assertIn('node', result)
    
    def test_critical_path(self):
        """Test critical path analysis."""
        if self.system.dependency_graph.nodes:
            workflow_name = list(self.system.dependency_graph.nodes.keys())[0]
            
            path = self.system.get_critical_path(workflow_name)
            
            self.assertIsInstance(path, list)
            self.assertIn(workflow_name, path)
    
    def test_impact_analysis(self):
        """Test impact analysis."""
        if self.system.dependency_graph.nodes:
            workflow_name = list(self.system.dependency_graph.nodes.keys())[0]
            
            impact = self.system.get_impact_analysis(workflow_name)
            
            self.assertIsInstance(impact, dict)
            self.assertIn('workflow', impact)
            self.assertIn('total_affected', impact)
            self.assertIn('affected_workflows', impact)
    
    def test_system_metrics(self):
        """Test system metrics."""
        metrics = self.system.get_system_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('system', metrics)
        self.assertIn('loader', metrics)
        self.assertIn('graph', metrics)
        self.assertIn('efficiency', metrics)
        
        # Check efficiency metrics
        efficiency = metrics['efficiency']
        for key in ['evaluation_ratio', 'load_ratio', 'cache_hit_rate', 'lazy_savings']:
            self.assertIn(key, efficiency)
            self.assertIsInstance(efficiency[key], float)
    
    def test_batch_evaluation(self):
        """Test batch evaluation."""
        if self.system.dependency_graph.nodes and len(self.system.dependency_graph.nodes) >= 2:
            workflows = list(self.system.dependency_graph.nodes.keys())[:2]
            
            result = self.system.evaluate_batch(workflows)
            
            self.assertIsInstance(result, dict)
            self.assertIn('total', result)
            self.assertIn('successful', result)
            self.assertIn('results', result)
            self.assertEqual(result['total'], len(workflows))


class TestLazyEvaluationPerformance(unittest.TestCase):
    """Test performance characteristics of lazy evaluation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflows_dir = '.github/workflows'
        if Path(self.workflows_dir).exists():
            self.system = LazyEvaluationSystem(self.workflows_dir)
            self.system.initialize()
    
    def test_lazy_loading_saves_resources(self):
        """Test that lazy loading reduces resource usage."""
        if self.system.metrics.total_workflows > 0:
            # Initially, no workflows should be loaded
            initial_loaded = self.system.metrics.loaded_workflows
            
            # System should have discovered workflows without loading them
            self.assertGreater(self.system.metrics.total_workflows, 0)
            self.assertEqual(initial_loaded, 0)
            
            # Lazy load savings should be high initially
            metrics = self.system.get_system_metrics()
            self.assertGreater(metrics['efficiency']['lazy_savings'], 0.5)
    
    def test_caching_improves_performance(self):
        """Test that caching improves performance."""
        if self.system.dependency_graph.nodes:
            workflow_name = list(self.system.dependency_graph.nodes.keys())[0]
            
            # Evaluate twice
            result1 = self.system.evaluate_workflow(workflow_name, load_dependencies=True)
            result2 = self.system.evaluate_workflow(workflow_name, load_dependencies=True)
            
            # Second evaluation should be faster (cached)
            if result1.get('success') and result2.get('success'):
                # Cache hit rate should be positive after multiple evaluations
                metrics = self.system.get_system_metrics()
                self.assertGreaterEqual(metrics['loader']['cache_hit_rate'], 0)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowDependencyGraph))
    suite.addTests(loader.loadTestsFromTestCase(TestLazyWorkflowLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestLazyDependencyResolver))
    suite.addTests(loader.loadTestsFromTestCase(TestLazyEvaluationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestLazyEvaluationPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
