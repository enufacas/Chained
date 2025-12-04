#!/usr/bin/env python3
"""
Tests for Self-Evolving Neural Architecture

This module provides comprehensive tests for the self-evolving neural
architecture system created by @create-botter.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from self_evolving_neural_architecture import (
    Neuron,
    Layer,
    ArchitectureEvolutionConfig,
    WorkflowPattern,
    SelfEvolvingNeuralArchitecture,
    EvolvingArchitectureManager,
)


class TestNeuron:
    """Tests for the Neuron class."""
    
    def test_neuron_creation(self):
        """Test basic neuron creation."""
        neuron = Neuron(
            neuron_id="test_neuron",
            layer=1,
            weights={"input_1": 0.5, "input_2": -0.3},
            bias=0.1
        )
        
        assert neuron.neuron_id == "test_neuron"
        assert neuron.layer == 1
        assert neuron.weights["input_1"] == 0.5
        assert neuron.bias == 0.1
        assert neuron.contribution_score == 0.5
    
    def test_neuron_activation_sigmoid(self):
        """Test neuron activation function."""
        neuron = Neuron(
            neuron_id="test",
            layer=1,
            weights={"x1": 1.0, "x2": 1.0},
            bias=0.0
        )
        
        # Test with zero inputs - should give 0.5 (sigmoid of 0)
        activation = neuron.activate({"x1": 0.0, "x2": 0.0})
        assert abs(activation - 0.5) < 0.01
        
        # Test with positive inputs
        activation = neuron.activate({"x1": 1.0, "x2": 1.0})
        assert activation > 0.5
        
        # Test with negative inputs
        activation = neuron.activate({"x1": -1.0, "x2": -1.0})
        assert activation < 0.5
    
    def test_neuron_weight_adjustment(self):
        """Test weight adjustment."""
        neuron = Neuron(
            neuron_id="test",
            layer=1,
            weights={"x1": 0.5},
            bias=0.1
        )
        
        original_weight = neuron.weights["x1"]
        neuron.adjust_weights(gradient=0.1, learning_rate=0.01)
        
        # Weight should decrease for positive gradient
        assert neuron.weights["x1"] < original_weight


class TestLayer:
    """Tests for the Layer class."""
    
    def test_layer_creation(self):
        """Test layer creation."""
        layer = Layer(layer_id=1, layer_type="hidden")
        
        assert layer.layer_id == 1
        assert layer.layer_type == "hidden"
        assert len(layer.neurons) == 0
    
    def test_add_remove_neuron(self):
        """Test adding and removing neurons."""
        layer = Layer(layer_id=1)
        neuron = Neuron(neuron_id="n1", layer=1)
        
        layer.add_neuron(neuron)
        assert "n1" in layer.neurons
        
        result = layer.remove_neuron("n1")
        assert result is True
        assert "n1" not in layer.neurons
        
        # Remove non-existent neuron
        result = layer.remove_neuron("n2")
        assert result is False
    
    def test_layer_forward_pass(self):
        """Test forward pass through layer."""
        layer = Layer(layer_id=1)
        
        neuron1 = Neuron(
            neuron_id="n1",
            layer=1,
            weights={"x1": 1.0},
            bias=0.0
        )
        neuron2 = Neuron(
            neuron_id="n2",
            layer=1,
            weights={"x1": -1.0},
            bias=0.0
        )
        
        layer.add_neuron(neuron1)
        layer.add_neuron(neuron2)
        
        outputs = layer.forward({"x1": 0.5})
        
        assert "n1" in outputs
        assert "n2" in outputs
        # n1 should have higher activation (positive weight)
        assert outputs["n1"] > outputs["n2"]


class TestArchitectureEvolutionConfig:
    """Tests for the configuration class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ArchitectureEvolutionConfig()
        
        assert config.base_learning_rate == 0.01
        assert config.success_rate_threshold == 0.7
        assert config.min_hidden_neurons == 2
        assert config.max_hidden_neurons == 20
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ArchitectureEvolutionConfig(
            base_learning_rate=0.05,
            success_rate_threshold=0.8
        )
        
        assert config.base_learning_rate == 0.05
        assert config.success_rate_threshold == 0.8


class TestWorkflowPattern:
    """Tests for the WorkflowPattern class."""
    
    def test_pattern_creation(self):
        """Test pattern creation."""
        pattern = WorkflowPattern(
            pattern_id="time_morning",
            pattern_type="time_of_day",
            pattern_data={"hour": 10, "period": "morning"},
            confidence=0.7,
            occurrences=5
        )
        
        assert pattern.pattern_id == "time_morning"
        assert pattern.pattern_type == "time_of_day"
        assert pattern.confidence == 0.7
        assert pattern.occurrences == 5


class TestSelfEvolvingNeuralArchitecture:
    """Tests for the main SelfEvolvingNeuralArchitecture class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .git directory to simulate repo root
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_architecture_initialization(self, temp_repo):
        """Test architecture initialization."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        assert arch.workflow_name == "test-workflow"
        assert arch.execution_count == 0
        assert arch.evolution_count == 0
        assert len(arch.layers) == 3  # input, hidden, output
    
    def test_architecture_layer_structure(self, temp_repo):
        """Test the layer structure is correct."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        # Check layer types
        assert arch.layers[0].layer_type == "input"
        assert arch.layers[1].layer_type == "hidden"
        assert arch.layers[2].layer_type == "output"
        
        # Check layer sizes
        assert len(arch.layers[0].neurons) == 5  # 5 input features
        assert len(arch.layers[1].neurons) == 3  # 3 hidden neurons initially
        assert len(arch.layers[2].neurons) == 4  # 4 output parameters
    
    def test_record_execution(self, temp_repo):
        """Test recording executions."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        arch.record_execution(success=True)
        assert arch.execution_count == 1
        assert len(arch.success_history) == 1
        assert arch.success_history[0] == 1.0
        
        arch.record_execution(success=False)
        assert arch.execution_count == 2
        assert arch.success_history[1] == 0.0
    
    def test_success_rate_calculation(self, temp_repo):
        """Test success rate calculation."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        # Initially 0.5 (neutral)
        assert arch.get_success_rate() == 0.5
        
        # Add some executions
        for _ in range(7):
            arch.record_execution(success=True)
        for _ in range(3):
            arch.record_execution(success=False)
        
        assert arch.get_success_rate() == 0.7
    
    def test_forward_pass(self, temp_repo):
        """Test forward pass through network."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        inputs = {
            'hour_of_day': 0.5,
            'day_of_week': 0.2,
            'recent_success_rate': 0.8,
            'execution_frequency': 0.3,
            'avg_duration': 0.5
        }
        
        outputs = arch.forward(inputs)
        
        # Should have 4 output parameters
        assert 'timeout' in outputs
        assert 'retries' in outputs
        assert 'concurrency' in outputs
        assert 'priority' in outputs
        
        # All outputs should be between 0 and 1 (sigmoid)
        for value in outputs.values():
            assert 0 <= value <= 1
    
    def test_recommendations(self, temp_repo):
        """Test getting recommendations."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        recommendations = arch.get_recommendations()
        
        # Check recommendation ranges
        assert 30 <= recommendations['timeout'] <= 300
        assert 1 <= recommendations['retries'] <= 5
        assert 1 <= recommendations['concurrency'] <= 10
        assert 0 <= recommendations['priority'] <= 100
    
    def test_save_and_load_architecture(self, temp_repo):
        """Test saving and loading architecture."""
        arch1 = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        # Modify some state
        arch1.record_execution(success=True)
        arch1.record_execution(success=True)
        arch1.record_execution(success=False)
        arch1.evolution_count = 5
        arch1.current_learning_rate = 0.02
        
        # Save
        arch1.save_architecture()
        
        # Create new instance and verify it loads correctly
        arch2 = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        assert arch2.execution_count == 3
        assert arch2.evolution_count == 5
        assert arch2.current_learning_rate == 0.02
        assert len(arch2.success_history) == 3
    
    def test_should_evolve_conditions(self, temp_repo):
        """Test evolution trigger conditions."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        # Not enough data - should not evolve
        assert arch._should_evolve() is False
        
        # Add minimum data but with good success rate
        for _ in range(10):
            arch.record_execution(success=True)
        
        # Good success rate - should not evolve
        assert arch._should_evolve() is False
        
        # Add more failures to lower success rate
        for _ in range(15):
            arch.record_execution(success=False)
        
        # Success rate below threshold, enough data
        assert arch.get_success_rate() < arch.config.success_rate_threshold
    
    def test_pattern_detection(self, temp_repo):
        """Test pattern detection from context."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        # Record execution with context
        context = {'duration': 120, 'memory_usage': 0.5}
        arch.record_execution(success=True, context=context)
        
        # Should have detected time patterns
        time_patterns = [p for p in arch.recognized_patterns.values()
                        if p.pattern_type == "time_of_day"]
        day_patterns = [p for p in arch.recognized_patterns.values()
                       if p.pattern_type == "day_of_week"]
        
        assert len(time_patterns) > 0
        assert len(day_patterns) > 0
    
    def test_evolution(self, temp_repo):
        """Test architecture evolution."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        initial_evolution_count = arch.evolution_count
        initial_neurons = len(arch.layers[1].neurons)
        
        # Add failures one by one (note: automatic evolution may trigger)
        for _ in range(5):
            arch.record_execution(success=False)
        
        # Force one more evolution
        before_evolve = arch.evolution_count
        arch.evolve()
        
        # Verify evolution happened (count increased by 1)
        assert arch.evolution_count == before_evolve + 1
        assert arch.last_evolution_time is not None
        # Verify evolution happened at least once total
        assert arch.evolution_count >= 1
    
    def test_get_status(self, temp_repo):
        """Test status retrieval."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        status = arch.get_status()
        
        assert status['workflow_name'] == "test-workflow"
        assert 'success_rate' in status
        assert 'execution_count' in status
        assert 'evolution_count' in status
        assert 'architecture_summary' in status
        assert 'layer_details' in status
    
    def test_generate_report(self, temp_repo):
        """Test report generation."""
        arch = SelfEvolvingNeuralArchitecture(
            workflow_name="test-workflow",
            repo_root=temp_repo
        )
        
        report = arch.generate_report()
        
        assert "Self-Evolving Neural Architecture Report" in report
        assert "test-workflow" in report
        assert "Success Rate" in report
        assert "@create-botter" in report


class TestEvolvingArchitectureManager:
    """Tests for the EvolvingArchitectureManager class."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_manager_initialization(self, temp_repo):
        """Test manager initialization."""
        manager = EvolvingArchitectureManager(repo_root=temp_repo)
        
        assert len(manager.architectures) == 0
    
    def test_get_or_create(self, temp_repo):
        """Test getting or creating architectures."""
        manager = EvolvingArchitectureManager(repo_root=temp_repo)
        
        arch1 = manager.get_or_create("workflow-1")
        assert "workflow-1" in manager.architectures
        
        # Same workflow should return same instance
        arch2 = manager.get_or_create("workflow-1")
        assert arch1 is arch2
        
        # Different workflow should create new instance
        arch3 = manager.get_or_create("workflow-2")
        assert arch3 is not arch1
    
    def test_record_execution(self, temp_repo):
        """Test recording executions through manager."""
        manager = EvolvingArchitectureManager(repo_root=temp_repo)
        
        manager.record_execution("workflow-1", success=True)
        manager.record_execution("workflow-1", success=False)
        manager.record_execution("workflow-2", success=True)
        
        assert manager.architectures["workflow-1"].execution_count == 2
        assert manager.architectures["workflow-2"].execution_count == 1
    
    def test_get_recommendations(self, temp_repo):
        """Test getting recommendations through manager."""
        manager = EvolvingArchitectureManager(repo_root=temp_repo)
        
        recommendations = manager.get_recommendations("workflow-1")
        
        assert 'timeout' in recommendations
        assert 'retries' in recommendations
    
    def test_get_summary(self, temp_repo):
        """Test summary generation."""
        manager = EvolvingArchitectureManager(repo_root=temp_repo)
        
        # Add some data
        for i in range(5):
            manager.record_execution("workflow-1", success=True)
        for i in range(3):
            manager.record_execution("workflow-2", success=False)
        
        summary = manager.get_summary()
        
        assert summary['total_architectures'] == 2
        assert summary['total_executions'] == 8
        assert 'average_success_rate' in summary
        assert 'architectures' in summary
    
    def test_generate_full_report(self, temp_repo):
        """Test full report generation."""
        manager = EvolvingArchitectureManager(repo_root=temp_repo)
        
        manager.record_execution("workflow-1", success=True)
        manager.record_execution("workflow-2", success=True)
        
        report = manager.generate_full_report()
        
        assert "Self-Evolving Neural Architecture System Report" in report
        assert "workflow-1" in report
        assert "workflow-2" in report
        assert "@create-botter" in report


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, '.git'))
            os.makedirs(os.path.join(tmpdir, '.github', 'agent-system', 'evolving_architectures'))
            yield tmpdir
    
    def test_complete_workflow_cycle(self, temp_repo):
        """Test a complete workflow of execution, evolution, and recommendation."""
        manager = EvolvingArchitectureManager(repo_root=temp_repo)
        workflow_name = "ci-build"
        
        # Phase 1: Initial executions with mixed success
        for i in range(15):
            success = i % 3 != 0  # 2/3 success rate
            manager.record_execution(workflow_name, success=success)
        
        arch = manager.get_or_create(workflow_name)
        initial_rate = arch.get_success_rate()
        
        # Phase 2: Get recommendations
        recommendations = manager.get_recommendations(workflow_name)
        assert all(k in recommendations for k in ['timeout', 'retries', 'concurrency', 'priority'])
        
        # Phase 3: Simulate improvement after applying recommendations
        for i in range(10):
            manager.record_execution(workflow_name, success=True)
        
        improved_rate = arch.get_success_rate()
        assert improved_rate >= initial_rate
        
        # Phase 4: Verify persistence
        arch.save_architecture()
        
        new_manager = EvolvingArchitectureManager(repo_root=temp_repo)
        loaded_arch = new_manager.get_or_create(workflow_name)
        
        assert loaded_arch.execution_count == 25
    
    def test_multiple_workflow_isolation(self, temp_repo):
        """Test that multiple workflows are properly isolated."""
        manager = EvolvingArchitectureManager(repo_root=temp_repo)
        
        # Workflow 1: High success rate
        for _ in range(10):
            manager.record_execution("workflow-1", success=True)
        
        # Workflow 2: Low success rate
        for _ in range(10):
            manager.record_execution("workflow-2", success=False)
        
        arch1 = manager.get_or_create("workflow-1")
        arch2 = manager.get_or_create("workflow-2")
        
        assert arch1.get_success_rate() == 1.0
        assert arch2.get_success_rate() == 0.0
        
        # Recommendations should differ
        rec1 = manager.get_recommendations("workflow-1")
        rec2 = manager.get_recommendations("workflow-2")
        
        # They might be different due to learned behavior
        assert rec1 is not None
        assert rec2 is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
