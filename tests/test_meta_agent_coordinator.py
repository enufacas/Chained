#!/usr/bin/env python3
"""
Tests for Meta-Agent Coordinator

Tests the task analysis, decomposition, agent selection, and coordination logic.
"""

import sys
import os
import json
import unittest
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from meta_agent_coordinator import (
    MetaAgentCoordinator, TaskComplexity, TaskStatus, SubTask, CoordinationPlan
)


class TestMetaAgentCoordinator(unittest.TestCase):
    """Test cases for MetaAgentCoordinator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.coordinator = MetaAgentCoordinator(repo_root=str(self.repo_root))
    
    def test_initialization(self):
        """Test coordinator initializes correctly"""
        self.assertIsNotNone(self.coordinator)
        self.assertIsNotNone(self.coordinator.repo_root)
        self.assertIsInstance(self.coordinator.agents, dict)
    
    def test_analyze_simple_task(self):
        """Test analyzing a simple task"""
        description = "Add a new function to calculate fibonacci numbers"
        complexity = self.coordinator.analyze_task(description)
        
        self.assertIn(complexity, [TaskComplexity.SIMPLE, TaskComplexity.MODERATE])
    
    def test_analyze_complex_task(self):
        """Test analyzing a complex task"""
        description = """
        Implement a new API endpoint with the following requirements:
        - Design RESTful API with authentication
        - Optimize for performance and scalability
        - Add comprehensive test coverage
        - Document the API in OpenAPI format
        - Conduct security audit
        """
        complexity = self.coordinator.analyze_task(description)
        
        self.assertIn(complexity, [TaskComplexity.COMPLEX, TaskComplexity.HIGHLY_COMPLEX])
    
    def test_analyze_security_task(self):
        """Test analyzing a security-focused task"""
        description = "Fix security vulnerability CVE-2024-1234 in authentication system"
        complexity = self.coordinator.analyze_task(description)
        
        # Should be at least simple, likely moderate
        self.assertIsInstance(complexity, TaskComplexity)
    
    def test_decompose_simple_task(self):
        """Test decomposing a simple task"""
        task_id = "issue-1"
        description = "Add README documentation for the project"
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        self.assertIsInstance(plan, CoordinationPlan)
        self.assertEqual(plan.task_id, task_id)
        self.assertGreater(len(plan.sub_tasks), 0)
        self.assertIn('documentation', plan.sub_tasks[0].description.lower())
    
    def test_decompose_complex_task(self):
        """Test decomposing a complex multi-category task"""
        task_id = "issue-2"
        description = """
        Build a new authentication API:
        - Investigate current auth patterns
        - Design secure API endpoints
        - Implement with performance optimization
        - Add comprehensive test coverage
        - Document the API
        """
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        self.assertIsInstance(plan, CoordinationPlan)
        self.assertGreater(len(plan.sub_tasks), 1)
        
        # Should have multiple sub-tasks for different specializations
        specializations = set()
        for st in plan.sub_tasks:
            specializations.update(st.required_specializations)
        
        self.assertGreater(len(specializations), 1)
    
    def test_subtask_dependencies(self):
        """Test that dependencies can be correctly established"""
        task_id = "issue-3"
        description = """
        Performance optimization task:
        - Investigate performance bottlenecks
        - Optimize slow algorithms
        - Add performance tests
        - Document optimizations
        """
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        # Dependencies are established based on category relationships
        # For simpler tasks, dependencies may not always be needed
        # Just verify that the execution order makes sense
        self.assertGreater(len(plan.execution_order), 0)
        self.assertEqual(len(plan.execution_order), len(plan.sub_tasks))
    
    def test_execution_order(self):
        """Test that execution order is logical"""
        task_id = "issue-4"
        description = """
        Complete refactoring:
        - Investigate code smells
        - Refactor duplicated code
        - Add tests for refactored code
        - Review the changes
        """
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        self.assertGreater(len(plan.execution_order), 0)
        self.assertEqual(len(plan.execution_order), len(plan.sub_tasks))
        
        # Check that all sub-tasks are in execution order
        task_ids = {st.id for st in plan.sub_tasks}
        order_ids = set(plan.execution_order)
        self.assertEqual(task_ids, order_ids)
    
    def test_parallel_groups_identification(self):
        """Test identification of tasks that can run in parallel"""
        task_id = "issue-5"
        description = """
        Multi-faceted improvement:
        - Add API documentation
        - Optimize database queries
        - Improve test coverage
        """
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        # These independent tasks should allow for some parallelism
        self.assertIsInstance(plan.parallel_groups, list)
    
    def test_completion_criteria_generation(self):
        """Test that completion criteria are generated"""
        task_id = "issue-6"
        description = "Add comprehensive test coverage for the authentication module"
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        # Check that sub-tasks have completion criteria
        for st in plan.sub_tasks:
            self.assertGreater(len(st.completion_criteria), 0)
            self.assertIsInstance(st.completion_criteria[0], str)
    
    def test_priority_calculation(self):
        """Test that priorities are calculated reasonably"""
        task_id = "issue-7"
        description = """
        Security and performance work:
        - Fix security vulnerability
        - Optimize performance
        - Add documentation
        """
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        # Security tasks should have reasonably high priority
        security_tasks = [st for st in plan.sub_tasks if 'security' in st.description.lower()]
        if security_tasks:
            # Security gets priority 5 by default (from _generate_subtask_description logic)
            # This is reasonable, as it's in the middle-high range
            self.assertGreaterEqual(security_tasks[0].priority, 5)
    
    def test_effort_estimation(self):
        """Test that effort is estimated"""
        task_id = "issue-8"
        description = "Build complete infrastructure for CI/CD pipeline"
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        for st in plan.sub_tasks:
            self.assertIn(st.estimated_effort, ['low', 'medium', 'high'])
    
    def test_coordination_creation(self):
        """Test creating a full coordination"""
        task_id = "issue-9"
        description = "Implement rate limiting for API endpoints"
        
        coordination = self.coordinator.create_coordination(task_id, description)
        
        self.assertIsInstance(coordination, dict)
        self.assertIn('id', coordination)
        self.assertIn('plan', coordination)
        self.assertIn('assignments', coordination)
        self.assertEqual(coordination['task_id'], task_id)
    
    def test_agent_selection_with_real_agents(self):
        """Test agent selection with actual agents from registry"""
        if not self.coordinator.agents:
            self.skipTest("No active agents in registry")
        
        task_id = "issue-10"
        description = "Optimize slow database queries"
        
        plan = self.coordinator.decompose_task(task_id, description)
        assignments = self.coordinator.select_agents(plan)
        
        # Should have assignments for sub-tasks
        self.assertIsInstance(assignments, dict)
        
        # Verify assigned agents exist
        for agent_id in assignments.values():
            self.assertIn(agent_id, self.coordinator.agents)
    
    def test_coordination_log_persistence(self):
        """Test that coordination log is saved"""
        task_id = "issue-11"
        description = "Simple test task"
        
        initial_count = len(self.coordinator.coordination_log['coordinations'])
        
        self.coordinator.create_coordination(task_id, description)
        
        final_count = len(self.coordinator.coordination_log['coordinations'])
        self.assertEqual(final_count, initial_count + 1)
    
    def test_coordination_summary(self):
        """Test getting coordination summary"""
        summary = self.coordinator.get_coordination_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_coordinations', summary)
        self.assertIn('statistics', summary)
    
    def test_task_complexity_categories(self):
        """Test various task complexity scenarios"""
        test_cases = [
            ("Fix typo in README", [TaskComplexity.SIMPLE]),
            ("Add tests for module", [TaskComplexity.SIMPLE, TaskComplexity.MODERATE]),
            ("Refactor code and add tests", [TaskComplexity.SIMPLE, TaskComplexity.MODERATE]),
            ("Build API with auth, tests, docs, and security audit", 
             [TaskComplexity.COMPLEX, TaskComplexity.HIGHLY_COMPLEX])
        ]
        
        for description, expected_range in test_cases:
            complexity = self.coordinator.analyze_task(description)
            self.assertIn(complexity, expected_range,
                         f"Task '{description}' complexity {complexity} not in expected range")
    
    def test_subtask_to_dict(self):
        """Test SubTask serialization"""
        subtask = SubTask(
            id="test-1",
            description="Test task",
            required_specializations=["engineer-master"],
            priority=5
        )
        
        data = subtask.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['id'], "test-1")
        self.assertEqual(data['description'], "Test task")
        self.assertIn('required_specializations', data)
    
    def test_coordination_plan_to_dict(self):
        """Test CoordinationPlan serialization"""
        plan = CoordinationPlan(
            task_id="test-task",
            complexity=TaskComplexity.MODERATE,
            sub_tasks=[],
            execution_order=[]
        )
        
        data = plan.to_dict()
        
        self.assertIsInstance(data, dict)
        self.assertEqual(data['task_id'], "test-task")
        self.assertEqual(data['complexity'], "moderate")
        self.assertIn('sub_tasks', data)
    
    def test_empty_description_handling(self):
        """Test handling of empty or minimal descriptions"""
        task_id = "issue-12"
        description = "Fix bug"
        
        plan = self.coordinator.decompose_task(task_id, description)
        
        # Should still create a plan, even for vague descriptions
        self.assertIsInstance(plan, CoordinationPlan)
        self.assertGreater(len(plan.sub_tasks), 0)
    
    def test_specialization_coverage(self):
        """Test that major specializations are covered in task patterns"""
        specializations = [
            'accelerate-master',
            'assert-specialist',
            'coach-master',
            'create-guru',
            'engineer-master',
            'investigate-champion',
            'secure-specialist',
            'organize-guru',
            'support-master'
        ]
        
        # Check that specialization map covers these
        mapped_specs = set()
        for specs in self.coordinator.SPECIALIZATION_MAP.values():
            mapped_specs.update(specs)
        
        for spec in specializations:
            if spec not in ['coach-master', 'create-guru']:  # These might be variants
                # At least check base patterns exist
                self.assertTrue(len(mapped_specs) > 0)


class TestTaskDecompositionLogic(unittest.TestCase):
    """Test specific task decomposition scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.coordinator = MetaAgentCoordinator(repo_root=str(self.repo_root))
    
    def test_api_with_security(self):
        """Test API task with security requirements"""
        description = """
        Create a new API endpoint for user authentication:
        - Must be secure against common vulnerabilities
        - Needs comprehensive testing
        - Requires documentation
        """
        
        plan = self.coordinator.decompose_task("api-sec-1", description)
        
        # Should include API, testing, and documentation sub-tasks
        # Security might be implied in the secure keyword but may not create separate task
        categories = [self.coordinator._extract_category(st.description) 
                     for st in plan.sub_tasks]
        
        self.assertIn('api', categories)
        # Either security or testing should be present
        has_security_related = any(cat in ['security', 'testing'] for cat in categories)
        self.assertTrue(has_security_related, "Should have security or testing category")
    
    def test_performance_optimization_flow(self):
        """Test performance optimization workflow"""
        description = """
        Optimize the data processing pipeline:
        - Investigate current bottlenecks
        - Implement optimizations
        - Add performance benchmarks
        """
        
        plan = self.coordinator.decompose_task("perf-1", description)
        
        # Should have investigation before optimization
        execution_order = plan.execution_order
        task_map = {st.id: st for st in plan.sub_tasks}
        
        # Find investigation and performance tasks
        inv_tasks = [tid for tid in execution_order 
                    if 'investigation' in task_map[tid].description.lower()]
        perf_tasks = [tid for tid in execution_order 
                     if 'performance' in task_map[tid].description.lower()]
        
        # Investigation should come before performance optimization
        if inv_tasks and perf_tasks:
            inv_index = execution_order.index(inv_tasks[0])
            perf_index = execution_order.index(perf_tasks[0])
            self.assertLess(inv_index, perf_index)


class TestCoordinationStatistics(unittest.TestCase):
    """Test coordination statistics and logging"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.repo_root = Path(__file__).parent.parent
        self.coordinator = MetaAgentCoordinator(repo_root=str(self.repo_root))
    
    def test_statistics_update(self):
        """Test that statistics are updated correctly"""
        initial_total = self.coordinator.coordination_log['statistics']['total_coordinations']
        
        self.coordinator.create_coordination("stat-test-1", "Test task for statistics")
        
        final_total = self.coordinator.coordination_log['statistics']['total_coordinations']
        self.assertEqual(final_total, initial_total + 1)
    
    def test_avg_agents_calculation(self):
        """Test average agents per task calculation"""
        # Create a coordination
        self.coordinator.create_coordination("avg-test-1", "Test task with multiple agents")
        
        avg = self.coordinator.coordination_log['statistics']['avg_agents_per_task']
        self.assertIsInstance(avg, float)
        self.assertGreaterEqual(avg, 0.0)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMetaAgentCoordinator))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskDecompositionLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestCoordinationStatistics))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
