#!/usr/bin/env python3
"""
Tests for Neural Architecture API

Comprehensive tests for the neural architecture API created by @APIs-architect.
Tests API endpoints, error handling, and integration with the underlying
self-evolving neural architecture system.
"""

import json
import os
import sys
import tempfile
from http import HTTPStatus
from pathlib import Path
from unittest import mock

import pytest

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from neural_architecture_api import NeuralArchitectureAPI


class TestArchitectureManagement:
    """Tests for architecture lifecycle management."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_create_architecture_success(self, temp_repo):
        """Test successful architecture creation."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.create_architecture("test-workflow")
        
        assert status == HTTPStatus.CREATED
        assert response['workflow_name'] == "test-workflow"
        assert 'architecture_summary' in response
        assert 'created_at' in response
    
    def test_create_architecture_with_config(self, temp_repo):
        """Test architecture creation with custom config."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        config = {
            'base_learning_rate': 0.05,
            'success_rate_threshold': 0.8,
            'min_hidden_neurons': 5,
            'max_hidden_neurons': 30
        }
        
        status, response = api.create_architecture("test-workflow", config=config)
        
        assert status == HTTPStatus.CREATED
        assert response['config']['base_learning_rate'] == 0.05
        assert response['config']['success_rate_threshold'] == 0.8
    
    def test_create_architecture_empty_name(self, temp_repo):
        """Test architecture creation with empty name."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.create_architecture("")
        
        assert status == HTTPStatus.BAD_REQUEST
        assert response['code'] == "INVALID_WORKFLOW_NAME"
    
    def test_create_architecture_duplicate(self, temp_repo):
        """Test architecture creation when it already exists."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create first time
        api.create_architecture("test-workflow")
        
        # Try to create again
        status, response = api.create_architecture("test-workflow")
        
        assert status == HTTPStatus.CONFLICT
        assert response['code'] == "ARCHITECTURE_EXISTS"
    
    def test_get_architecture_success(self, temp_repo):
        """Test getting architecture details."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create architecture first
        api.create_architecture("test-workflow")
        
        # Get it
        status, response = api.get_architecture("test-workflow")
        
        assert status == HTTPStatus.OK
        assert response['workflow_name'] == "test-workflow"
        assert 'status' in response
        assert 'patterns' in response
    
    def test_get_architecture_not_found(self, temp_repo):
        """Test getting non-existent architecture."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.get_architecture("non-existent")
        
        assert status == HTTPStatus.NOT_FOUND
        assert response['code'] == "ARCHITECTURE_NOT_FOUND"
    
    def test_delete_architecture_success(self, temp_repo):
        """Test deleting architecture."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create architecture first
        api.create_architecture("test-workflow")
        
        # Delete it
        status, response = api.delete_architecture("test-workflow")
        
        assert status == HTTPStatus.OK
        assert 'deleted_at' in response
        
        # Verify it's gone
        status, _ = api.get_architecture("test-workflow")
        assert status == HTTPStatus.NOT_FOUND
    
    def test_delete_architecture_not_found(self, temp_repo):
        """Test deleting non-existent architecture."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.delete_architecture("non-existent")
        
        assert status == HTTPStatus.NOT_FOUND
        assert response['code'] == "ARCHITECTURE_NOT_FOUND"
    
    def test_list_architectures(self, temp_repo):
        """Test listing all architectures."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create some architectures
        api.create_architecture("workflow-1")
        api.create_architecture("workflow-2")
        api.create_architecture("workflow-3")
        
        status, response = api.list_architectures()
        
        assert status == HTTPStatus.OK
        assert response['count'] == 3
        assert len(response['architectures']) == 3
    
    def test_list_architectures_empty(self, temp_repo):
        """Test listing when no architectures exist."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.list_architectures()
        
        assert status == HTTPStatus.OK
        assert response['count'] == 0


class TestExecutionRecording:
    """Tests for execution recording."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_record_execution_success(self, temp_repo):
        """Test recording successful execution."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.record_execution("test-workflow", success=True)
        
        assert status == HTTPStatus.OK
        assert response['success'] is True
        assert response['execution_count'] == 1
    
    def test_record_execution_failure(self, temp_repo):
        """Test recording failed execution."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.record_execution("test-workflow", success=False)
        
        assert status == HTTPStatus.OK
        assert response['success'] is False
    
    def test_record_execution_with_context(self, temp_repo):
        """Test recording execution with context."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        context = {'duration': 120, 'memory_usage': 0.8}
        status, response = api.record_execution(
            "test-workflow", 
            success=True, 
            context=context
        )
        
        assert status == HTTPStatus.OK
        assert response['execution_count'] == 1
    
    def test_record_execution_empty_name(self, temp_repo):
        """Test recording execution with empty name."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.record_execution("", success=True)
        
        assert status == HTTPStatus.BAD_REQUEST
        assert response['code'] == "INVALID_WORKFLOW_NAME"
    
    def test_record_multiple_executions(self, temp_repo):
        """Test recording multiple executions."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        for i in range(10):
            success = i % 2 == 0
            api.record_execution("test-workflow", success=success)
        
        status, response = api.get_architecture("test-workflow")
        
        assert status == HTTPStatus.OK
        assert response['status']['execution_count'] == 10
    
    def test_batch_record_executions(self, temp_repo):
        """Test batch recording of executions."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        executions = [
            {"workflow_name": "workflow-1", "success": True},
            {"workflow_name": "workflow-1", "success": False},
            {"workflow_name": "workflow-2", "success": True},
        ]
        
        status, response = api.batch_record_executions(executions)
        
        assert status == HTTPStatus.OK
        assert response['recorded'] == 3
        assert response['errors'] == 0
    
    def test_batch_record_with_errors(self, temp_repo):
        """Test batch recording with some invalid records."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        executions = [
            {"workflow_name": "workflow-1", "success": True},
            {"success": True},  # Missing workflow_name
            {"workflow_name": "workflow-2"},  # Missing success
        ]
        
        status, response = api.batch_record_executions(executions)
        
        assert status == HTTPStatus.OK
        assert response['recorded'] == 1
        assert response['errors'] == 2
    
    def test_batch_record_empty(self, temp_repo):
        """Test batch recording with empty list."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.batch_record_executions([])
        
        assert status == HTTPStatus.BAD_REQUEST
        assert response['code'] == "EMPTY_BATCH"


class TestEvolutionControl:
    """Tests for evolution control."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_trigger_evolution_not_needed(self, temp_repo):
        """Test triggering evolution when not needed."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create architecture with good success rate
        api.create_architecture("test-workflow")
        for _ in range(10):
            api.record_execution("test-workflow", success=True)
        
        status, response = api.trigger_evolution("test-workflow")
        
        assert status == HTTPStatus.OK
        assert response['evolved'] is False
    
    def test_trigger_evolution_force(self, temp_repo):
        """Test forcing evolution."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create architecture
        api.create_architecture("test-workflow")
        for _ in range(5):
            api.record_execution("test-workflow", success=False)
        
        status, response = api.trigger_evolution("test-workflow", force=True)
        
        assert status == HTTPStatus.OK
        assert response['evolved'] is True
        assert 'before' in response
        assert 'after' in response
    
    def test_trigger_evolution_not_found(self, temp_repo):
        """Test triggering evolution for non-existent architecture."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.trigger_evolution("non-existent")
        
        assert status == HTTPStatus.NOT_FOUND
    
    def test_evolve_all(self, temp_repo):
        """Test evolving all architectures."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create some architectures
        api.create_architecture("workflow-1")
        api.create_architecture("workflow-2")
        
        status, response = api.evolve_all()
        
        assert status == HTTPStatus.OK
        assert response['total_architectures'] == 2


class TestRecommendations:
    """Tests for recommendations."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_get_recommendations(self, temp_repo):
        """Test getting recommendations."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.get_recommendations("test-workflow")
        
        assert status == HTTPStatus.OK
        assert 'recommendations' in response
        assert 'timeout' in response['recommendations']
        assert 'retries' in response['recommendations']
        assert 'concurrency' in response['recommendations']
        assert 'priority' in response['recommendations']
    
    def test_get_recommendations_with_context(self, temp_repo):
        """Test getting recommendations with context."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        context = {
            'hour_of_day': 0.5,
            'day_of_week': 0.3,
            'recent_success_rate': 0.8,
            'execution_frequency': 0.5,
            'avg_duration': 0.5
        }
        
        status, response = api.get_recommendations("test-workflow", context=context)
        
        assert status == HTTPStatus.OK
        assert 'recommendations' in response
    
    def test_get_recommendations_empty_name(self, temp_repo):
        """Test getting recommendations with empty name."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.get_recommendations("")
        
        assert status == HTTPStatus.BAD_REQUEST


class TestPatternAnalysis:
    """Tests for pattern analysis."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_get_patterns(self, temp_repo):
        """Test getting patterns."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create architecture and record some executions
        api.create_architecture("test-workflow")
        for _ in range(5):
            api.record_execution("test-workflow", success=True, context={})
        
        status, response = api.get_patterns("test-workflow")
        
        assert status == HTTPStatus.OK
        assert 'patterns' in response
        assert isinstance(response['patterns'], list)
    
    def test_get_patterns_with_filter(self, temp_repo):
        """Test getting patterns with type filter."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create architecture and record some executions
        api.create_architecture("test-workflow")
        for _ in range(5):
            api.record_execution("test-workflow", success=True, context={})
        
        status, response = api.get_patterns("test-workflow", pattern_type="time_of_day")
        
        assert status == HTTPStatus.OK
        assert response['filter'] == "time_of_day"
    
    def test_get_patterns_not_found(self, temp_repo):
        """Test getting patterns for non-existent architecture."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.get_patterns("non-existent")
        
        assert status == HTTPStatus.NOT_FOUND


class TestSystemHealth:
    """Tests for system health and status."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_get_system_summary(self, temp_repo):
        """Test getting system summary."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create some architectures
        api.create_architecture("workflow-1")
        api.create_architecture("workflow-2")
        
        status, response = api.get_system_summary()
        
        assert status == HTTPStatus.OK
        assert response['total_architectures'] == 2
        assert 'timestamp' in response
    
    def test_get_health_status_empty(self, temp_repo):
        """Test health status when no architectures exist."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        status, response = api.get_health_status()
        
        assert status == HTTPStatus.OK
        assert response['status'] == "healthy"
        assert response['architectures'] == 0
    
    def test_get_health_status_healthy(self, temp_repo):
        """Test health status when all is healthy."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create architecture with good success rate
        api.create_architecture("test-workflow")
        for _ in range(10):
            api.record_execution("test-workflow", success=True)
        
        status, response = api.get_health_status()
        
        assert status == HTTPStatus.OK
        assert response['status'] == "healthy"
    
    def test_get_health_status_degraded(self, temp_repo):
        """Test health status when degraded."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create architecture with mixed success rate
        api.create_architecture("workflow-1")
        api.create_architecture("workflow-2")
        api.create_architecture("workflow-3")
        
        # workflow-1: low success
        for _ in range(10):
            api.record_execution("workflow-1", success=False)
        
        # workflow-2: low success
        for _ in range(10):
            api.record_execution("workflow-2", success=False)
        
        # workflow-3: good success
        for _ in range(10):
            api.record_execution("workflow-3", success=True)
        
        status, response = api.get_health_status()
        
        assert status == HTTPStatus.OK
        # Status should be degraded or worse
        assert response['status'] in ['degraded', 'critical', 'warning']
    
    def test_generate_report(self, temp_repo):
        """Test report generation."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # Create some architectures
        api.create_architecture("test-workflow")
        
        status, response = api.generate_report()
        
        assert status == HTTPStatus.OK
        assert 'report' in response
        assert 'generated_at' in response


class TestIntegration:
    """Integration tests for the complete API."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_full_workflow_cycle(self, temp_repo):
        """Test complete workflow cycle through API."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        # 1. Create architecture
        status, response = api.create_architecture("ci-build")
        assert status == HTTPStatus.CREATED
        
        # 2. Record some executions with mixed results
        for i in range(20):
            success = i % 3 != 0  # ~67% success
            api.record_execution("ci-build", success=success)
        
        # 3. Get recommendations
        status, response = api.get_recommendations("ci-build")
        assert status == HTTPStatus.OK
        assert 30 <= response['recommendations']['timeout'] <= 300
        
        # 4. Check patterns
        status, response = api.get_patterns("ci-build")
        assert status == HTTPStatus.OK
        
        # 5. Force evolution
        status, response = api.trigger_evolution("ci-build", force=True)
        assert status == HTTPStatus.OK
        
        # 6. Get final status
        status, response = api.get_architecture("ci-build")
        assert status == HTTPStatus.OK
        assert response['status']['execution_count'] == 20
    
    def test_multiple_workflows(self, temp_repo):
        """Test managing multiple workflows."""
        api = NeuralArchitectureAPI(repo_root=temp_repo)
        
        workflows = ["ci-build", "deploy", "test-suite"]
        
        # Create all workflows
        for wf in workflows:
            status, _ = api.create_architecture(wf)
            assert status == HTTPStatus.CREATED
        
        # Record executions for each
        for wf in workflows:
            for i in range(5):
                api.record_execution(wf, success=i % 2 == 0)
        
        # Get list
        status, response = api.list_architectures()
        assert status == HTTPStatus.OK
        assert response['count'] == 3
        
        # Check health
        status, response = api.get_health_status()
        assert status == HTTPStatus.OK


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
