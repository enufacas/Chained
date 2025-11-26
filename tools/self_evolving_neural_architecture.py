#!/usr/bin/env python3
"""
Self-Evolving Neural Architecture for Workflow Adaptation
Created by @create-guru

This module implements a self-evolving neural architecture that automatically
adapts workflow configurations based on success rates. It extends the neural
workflow adapter with advanced capabilities for architecture evolution.

Key Features:
- Multi-layer neural architecture with dynamic layer sizing
- Automatic architecture evolution (adding/removing neurons)
- Success rate-based learning rules
- Pattern recognition for similar workflows
- Adaptive learning rates based on performance trends
- Self-pruning of ineffective connections
- Architecture complexity optimization

The system learns from workflow execution outcomes and continuously
evolves its structure to improve prediction accuracy and workflow success.

Architecture Overview:
- Input Layer: Workflow context features (time, patterns, history)
- Hidden Layers: Dynamically evolving layers with adaptive neurons
- Output Layer: Workflow parameter recommendations
- Evolution Engine: Modifies architecture based on performance metrics
"""

import json
import math
import os
import random
import statistics
import sys
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))


@dataclass
class Neuron:
    """
    Represents a single neuron in the neural architecture.
    
    Each neuron has connections to other neurons with weights,
    and can be activated based on input signals.
    """
    neuron_id: str
    layer: int
    weights: Dict[str, float] = field(default_factory=dict)  # input_id -> weight
    bias: float = 0.0
    activation: float = 0.0
    gradient: float = 0.0
    creation_time: str = ""
    contribution_score: float = 0.5  # How useful is this neuron
    
    def __post_init__(self):
        if not self.creation_time:
            self.creation_time = datetime.now(timezone.utc).isoformat()
    
    def activate(self, inputs: Dict[str, float]) -> float:
        """
        Compute neuron activation based on inputs.
        
        Args:
            inputs: Dictionary of input_id -> value
        
        Returns:
            Activation value after applying activation function
        """
        # Weighted sum
        z = sum(inputs.get(inp_id, 0.0) * weight 
                for inp_id, weight in self.weights.items())
        z += self.bias
        
        # Sigmoid activation for bounded output
        self.activation = 1.0 / (1.0 + math.exp(-max(-500, min(500, z))))
        return self.activation
    
    def adjust_weights(self, gradient: float, learning_rate: float = 0.01):
        """Adjust weights based on error gradient."""
        self.gradient = gradient
        for input_id in self.weights:
            self.weights[input_id] -= learning_rate * gradient
            # Clip weights to prevent explosion
            self.weights[input_id] = max(-5.0, min(5.0, self.weights[input_id]))
        self.bias -= learning_rate * gradient


@dataclass
class Layer:
    """Represents a layer of neurons in the architecture."""
    layer_id: int
    neurons: Dict[str, Neuron] = field(default_factory=dict)
    layer_type: str = "hidden"  # "input", "hidden", "output"
    
    def add_neuron(self, neuron: Neuron):
        """Add a neuron to this layer."""
        self.neurons[neuron.neuron_id] = neuron
    
    def remove_neuron(self, neuron_id: str) -> bool:
        """Remove a neuron from this layer."""
        if neuron_id in self.neurons:
            del self.neurons[neuron_id]
            return True
        return False
    
    def forward(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """Forward pass through all neurons in this layer."""
        outputs = {}
        for neuron_id, neuron in self.neurons.items():
            outputs[neuron_id] = neuron.activate(inputs)
        return outputs


@dataclass
class ArchitectureEvolutionConfig:
    """Configuration for architecture evolution."""
    # Learning parameters
    base_learning_rate: float = 0.01
    min_learning_rate: float = 0.001
    max_learning_rate: float = 0.1
    learning_rate_decay: float = 0.99
    
    # Evolution triggers
    success_rate_threshold: float = 0.7  # Evolve if below this
    evolution_interval: int = 10  # Minimum executions between evolutions
    min_data_for_evolution: int = 5  # Minimum data points needed
    
    # Architecture constraints
    min_hidden_neurons: int = 2
    max_hidden_neurons: int = 20
    max_hidden_layers: int = 3
    
    # Pruning parameters
    neuron_prune_threshold: float = 0.1  # Remove neurons with low contribution
    connection_prune_threshold: float = 0.01  # Remove weak connections
    
    # Growth parameters
    neuron_growth_rate: float = 0.2  # Probability of adding neuron
    connection_growth_rate: float = 0.3  # Probability of adding connection


@dataclass
class WorkflowPattern:
    """Pattern recognized in workflow execution."""
    pattern_id: str
    pattern_type: str  # "time_of_day", "day_of_week", "sequential", "concurrent"
    pattern_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    occurrences: int = 0
    last_seen: str = ""


class SelfEvolvingNeuralArchitecture:
    """
    Self-evolving neural architecture for workflow adaptation.
    
    This class implements a neural network that can modify its own
    structure based on performance feedback, automatically growing
    or pruning neurons and connections to optimize workflow outcomes.
    """
    
    def __init__(self, workflow_name: str, repo_root: str = None):
        """
        Initialize the self-evolving neural architecture.
        
        Args:
            workflow_name: Name of the workflow to optimize
            repo_root: Repository root path
        """
        self.workflow_name = workflow_name
        
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path.cwd()
        
        # Storage path
        self.storage_path = self.repo_root / '.github' / 'agent-system' / 'evolving_architectures'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Architecture components
        self.layers: Dict[int, Layer] = {}
        self.config = ArchitectureEvolutionConfig()
        
        # Performance tracking
        self.success_history: deque = deque(maxlen=100)
        self.execution_count: int = 0
        self.evolution_count: int = 0
        self.last_evolution_time: Optional[str] = None
        self.current_learning_rate: float = self.config.base_learning_rate
        
        # Pattern recognition
        self.recognized_patterns: Dict[str, WorkflowPattern] = {}
        
        # Architecture fitness tracking
        self.architecture_fitness: float = 0.5
        self.fitness_history: deque = deque(maxlen=50)
        
        # Load or initialize architecture
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing architecture or initialize a new one."""
        arch_file = self.storage_path / f"{self._safe_filename(self.workflow_name)}.json"
        
        if arch_file.exists():
            self._load_architecture(arch_file)
        else:
            self._initialize_architecture()
    
    def _safe_filename(self, name: str) -> str:
        """Convert workflow name to safe filename."""
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    
    def _initialize_architecture(self):
        """Initialize a new neural architecture with default structure."""
        # Input layer (5 input features)
        input_layer = Layer(layer_id=0, layer_type="input")
        input_features = [
            "hour_of_day", "day_of_week", "recent_success_rate",
            "execution_frequency", "avg_duration"
        ]
        for i, feature in enumerate(input_features):
            neuron = Neuron(
                neuron_id=f"input_{feature}",
                layer=0,
                weights={},
                bias=0.0
            )
            input_layer.add_neuron(neuron)
        self.layers[0] = input_layer
        
        # Hidden layer 1 (3 neurons to start)
        hidden_layer1 = Layer(layer_id=1, layer_type="hidden")
        for i in range(3):
            weights = {f"input_{f}": random.uniform(-0.5, 0.5) 
                      for f in input_features}
            neuron = Neuron(
                neuron_id=f"hidden1_{i}",
                layer=1,
                weights=weights,
                bias=random.uniform(-0.1, 0.1)
            )
            hidden_layer1.add_neuron(neuron)
        self.layers[1] = hidden_layer1
        
        # Output layer (workflow parameters)
        output_layer = Layer(layer_id=2, layer_type="output")
        output_params = ["timeout", "retries", "concurrency", "priority"]
        hidden_neuron_ids = [f"hidden1_{i}" for i in range(3)]
        for param in output_params:
            weights = {h_id: random.uniform(-0.5, 0.5) for h_id in hidden_neuron_ids}
            neuron = Neuron(
                neuron_id=f"output_{param}",
                layer=2,
                weights=weights,
                bias=random.uniform(-0.1, 0.1)
            )
            output_layer.add_neuron(neuron)
        self.layers[2] = output_layer
    
    def _load_architecture(self, arch_file: Path):
        """Load architecture from file."""
        try:
            with open(arch_file, 'r') as f:
                data = json.load(f)
            
            # Restore configuration
            if 'config' in data:
                cfg = data['config']
                self.config = ArchitectureEvolutionConfig(
                    base_learning_rate=cfg.get('base_learning_rate', 0.01),
                    success_rate_threshold=cfg.get('success_rate_threshold', 0.7),
                    min_hidden_neurons=cfg.get('min_hidden_neurons', 2),
                    max_hidden_neurons=cfg.get('max_hidden_neurons', 20),
                )
            
            # Restore layers and neurons
            for layer_data in data.get('layers', []):
                layer_id = layer_data['layer_id']
                layer = Layer(
                    layer_id=layer_id,
                    layer_type=layer_data.get('layer_type', 'hidden')
                )
                
                for neuron_data in layer_data.get('neurons', []):
                    neuron = Neuron(
                        neuron_id=neuron_data['neuron_id'],
                        layer=layer_id,
                        weights=neuron_data.get('weights', {}),
                        bias=neuron_data.get('bias', 0.0),
                        contribution_score=neuron_data.get('contribution_score', 0.5),
                        creation_time=neuron_data.get('creation_time', '')
                    )
                    layer.add_neuron(neuron)
                
                self.layers[layer_id] = layer
            
            # Restore metrics
            self.success_history = deque(data.get('success_history', []), maxlen=100)
            self.execution_count = data.get('execution_count', 0)
            self.evolution_count = data.get('evolution_count', 0)
            self.last_evolution_time = data.get('last_evolution_time')
            self.current_learning_rate = data.get('current_learning_rate', 0.01)
            self.architecture_fitness = data.get('architecture_fitness', 0.5)
            
            # Restore patterns
            for pattern_data in data.get('patterns', []):
                pattern = WorkflowPattern(
                    pattern_id=pattern_data['pattern_id'],
                    pattern_type=pattern_data['pattern_type'],
                    pattern_data=pattern_data.get('pattern_data', {}),
                    confidence=pattern_data.get('confidence', 0.5),
                    occurrences=pattern_data.get('occurrences', 0)
                )
                self.recognized_patterns[pattern.pattern_id] = pattern
            
        except Exception as e:
            print(f"Warning: Could not load architecture: {e}", file=sys.stderr)
            self._initialize_architecture()
    
    def save_architecture(self):
        """Save architecture to file."""
        arch_file = self.storage_path / f"{self._safe_filename(self.workflow_name)}.json"
        
        data = {
            'workflow_name': self.workflow_name,
            'version': '1.0.0',
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'config': {
                'base_learning_rate': self.config.base_learning_rate,
                'success_rate_threshold': self.config.success_rate_threshold,
                'min_hidden_neurons': self.config.min_hidden_neurons,
                'max_hidden_neurons': self.config.max_hidden_neurons,
            },
            'layers': [],
            'success_history': list(self.success_history),
            'execution_count': self.execution_count,
            'evolution_count': self.evolution_count,
            'last_evolution_time': self.last_evolution_time,
            'current_learning_rate': self.current_learning_rate,
            'architecture_fitness': self.architecture_fitness,
            'patterns': []
        }
        
        # Serialize layers
        for layer_id, layer in sorted(self.layers.items()):
            layer_data = {
                'layer_id': layer_id,
                'layer_type': layer.layer_type,
                'neurons': []
            }
            for neuron_id, neuron in layer.neurons.items():
                layer_data['neurons'].append({
                    'neuron_id': neuron.neuron_id,
                    'weights': neuron.weights,
                    'bias': neuron.bias,
                    'contribution_score': neuron.contribution_score,
                    'creation_time': neuron.creation_time
                })
            data['layers'].append(layer_data)
        
        # Serialize patterns
        for pattern in self.recognized_patterns.values():
            data['patterns'].append({
                'pattern_id': pattern.pattern_id,
                'pattern_type': pattern.pattern_type,
                'pattern_data': pattern.pattern_data,
                'confidence': pattern.confidence,
                'occurrences': pattern.occurrences
            })
        
        with open(arch_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def forward(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """
        Forward pass through the network.
        
        Args:
            inputs: Input feature values
        
        Returns:
            Output values (workflow parameter recommendations)
        """
        current_values = {}
        
        # Input layer - just pass through normalized inputs
        for neuron_id, neuron in self.layers[0].neurons.items():
            feature_name = neuron_id.replace("input_", "")
            current_values[neuron_id] = inputs.get(feature_name, 0.0)
        
        # Hidden and output layers
        layer_ids = sorted(k for k in self.layers.keys() if k > 0)
        for layer_id in layer_ids:
            layer = self.layers[layer_id]
            layer_outputs = layer.forward(current_values)
            current_values.update(layer_outputs)
        
        # Extract output values
        outputs = {}
        if 2 in self.layers:
            for neuron_id, neuron in self.layers[2].neurons.items():
                param_name = neuron_id.replace("output_", "")
                outputs[param_name] = neuron.activation
        
        return outputs
    
    def record_execution(self, success: bool, context: Optional[Dict[str, Any]] = None):
        """
        Record a workflow execution result.
        
        Args:
            success: Whether the execution was successful
            context: Optional execution context (time, duration, etc.)
        """
        self.success_history.append(1.0 if success else 0.0)
        self.execution_count += 1
        
        # Detect patterns from context
        if context:
            self._detect_patterns(context)
        
        # Check if evolution is needed
        if self._should_evolve():
            self.evolve()
    
    def _detect_patterns(self, context: Dict[str, Any]):
        """Detect patterns from execution context."""
        now = datetime.now(timezone.utc)
        
        # Time of day pattern
        hour = now.hour
        time_period = "morning" if 6 <= hour < 12 else (
            "afternoon" if 12 <= hour < 18 else (
                "evening" if 18 <= hour < 22 else "night"
            )
        )
        pattern_id = f"time_{time_period}"
        
        if pattern_id in self.recognized_patterns:
            pattern = self.recognized_patterns[pattern_id]
            pattern.occurrences += 1
            pattern.last_seen = now.isoformat()
            # Update confidence based on success
            if self.success_history:
                recent_success = sum(list(self.success_history)[-10:]) / min(10, len(self.success_history))
                pattern.confidence = 0.8 * pattern.confidence + 0.2 * recent_success
        else:
            self.recognized_patterns[pattern_id] = WorkflowPattern(
                pattern_id=pattern_id,
                pattern_type="time_of_day",
                pattern_data={"hour": hour, "period": time_period},
                confidence=0.5,
                occurrences=1,
                last_seen=now.isoformat()
            )
        
        # Day of week pattern
        day = now.strftime("%A").lower()
        pattern_id = f"day_{day}"
        
        if pattern_id in self.recognized_patterns:
            pattern = self.recognized_patterns[pattern_id]
            pattern.occurrences += 1
            pattern.last_seen = now.isoformat()
        else:
            self.recognized_patterns[pattern_id] = WorkflowPattern(
                pattern_id=pattern_id,
                pattern_type="day_of_week",
                pattern_data={"day": day, "weekday": now.weekday()},
                confidence=0.5,
                occurrences=1,
                last_seen=now.isoformat()
            )
    
    def _should_evolve(self) -> bool:
        """Determine if architecture evolution is needed."""
        # Need minimum data
        if len(self.success_history) < self.config.min_data_for_evolution:
            return False
        
        # Check evolution interval
        executions_since_evolution = (
            self.execution_count - 
            (self.evolution_count * self.config.evolution_interval)
        )
        if executions_since_evolution < self.config.evolution_interval:
            return False
        
        # Check success rate
        success_rate = self.get_success_rate()
        return success_rate < self.config.success_rate_threshold
    
    def get_success_rate(self) -> float:
        """Calculate current success rate."""
        if not self.success_history:
            return 0.5
        return sum(self.success_history) / len(self.success_history)
    
    def evolve(self):
        """
        Evolve the architecture based on performance.
        
        This is the core self-evolution mechanism that modifies
        the neural architecture structure.
        """
        print(f"\n🧬 Evolving architecture for {self.workflow_name}...")
        
        success_rate = self.get_success_rate()
        print(f"   Current success rate: {success_rate:.1%}")
        
        # Determine evolution strategy based on performance
        if success_rate < 0.3:
            # Very low performance - aggressive evolution
            self._aggressive_evolution()
        elif success_rate < 0.5:
            # Low performance - moderate evolution
            self._moderate_evolution()
        else:
            # Below threshold but not critical - fine tuning
            self._fine_tune_evolution()
        
        # Update learning rate based on performance trend
        self._update_learning_rate()
        
        # Update fitness tracking
        self.architecture_fitness = success_rate
        self.fitness_history.append(success_rate)
        
        # Record evolution
        self.evolution_count += 1
        self.last_evolution_time = datetime.now(timezone.utc).isoformat()
        
        print(f"   Evolution #{self.evolution_count} complete")
        print(f"   Architecture: {self._get_architecture_summary()}")
        
        # Save updated architecture
        self.save_architecture()
    
    def _aggressive_evolution(self):
        """Aggressive evolution for very low performance."""
        print("   Strategy: Aggressive evolution")
        
        # Prune underperforming neurons
        self._prune_weak_neurons()
        
        # Add new neurons with random weights
        self._grow_neurons(count=2)
        
        # Reset some weights randomly
        self._randomize_weak_connections()
        
        # Increase learning rate temporarily
        self.current_learning_rate = min(
            self.config.max_learning_rate,
            self.current_learning_rate * 1.5
        )
    
    def _moderate_evolution(self):
        """Moderate evolution for low performance."""
        print("   Strategy: Moderate evolution")
        
        # Prune only very weak neurons
        self._prune_weak_neurons(threshold=0.05)
        
        # Add one new neuron
        self._grow_neurons(count=1)
        
        # Adjust connection weights
        self._strengthen_successful_paths()
    
    def _fine_tune_evolution(self):
        """Fine tuning for performance just below threshold."""
        print("   Strategy: Fine tuning")
        
        # Just adjust weights, no structural changes
        self._strengthen_successful_paths()
        
        # Slightly reduce learning rate
        self.current_learning_rate = max(
            self.config.min_learning_rate,
            self.current_learning_rate * 0.95
        )
    
    def _prune_weak_neurons(self, threshold: Optional[float] = None):
        """Remove neurons with low contribution scores."""
        if threshold is None:
            threshold = self.config.neuron_prune_threshold
        
        for layer_id in [1]:  # Only prune hidden layers
            if layer_id not in self.layers:
                continue
            
            layer = self.layers[layer_id]
            neurons_to_remove = []
            
            for neuron_id, neuron in layer.neurons.items():
                if (neuron.contribution_score < threshold and
                    len(layer.neurons) > self.config.min_hidden_neurons):
                    neurons_to_remove.append(neuron_id)
            
            for neuron_id in neurons_to_remove:
                layer.remove_neuron(neuron_id)
                print(f"   Pruned neuron: {neuron_id}")
                
                # Remove references to this neuron from next layer
                if layer_id + 1 in self.layers:
                    for next_neuron in self.layers[layer_id + 1].neurons.values():
                        if neuron_id in next_neuron.weights:
                            del next_neuron.weights[neuron_id]
    
    def _grow_neurons(self, count: int = 1):
        """Add new neurons to hidden layers."""
        for layer_id in [1]:  # Add to first hidden layer
            if layer_id not in self.layers:
                continue
            
            layer = self.layers[layer_id]
            
            if len(layer.neurons) >= self.config.max_hidden_neurons:
                return
            
            for i in range(count):
                # Create new neuron
                new_id = f"hidden{layer_id}_{len(layer.neurons)}_{int(datetime.now().timestamp())}"
                
                # Connect to all neurons in previous layer
                prev_layer = self.layers.get(layer_id - 1)
                if prev_layer:
                    weights = {
                        n_id: random.uniform(-0.5, 0.5)
                        for n_id in prev_layer.neurons
                    }
                else:
                    weights = {}
                
                new_neuron = Neuron(
                    neuron_id=new_id,
                    layer=layer_id,
                    weights=weights,
                    bias=random.uniform(-0.1, 0.1)
                )
                layer.add_neuron(new_neuron)
                print(f"   Added neuron: {new_id}")
                
                # Connect this neuron to output layer
                if layer_id + 1 in self.layers:
                    for output_neuron in self.layers[layer_id + 1].neurons.values():
                        output_neuron.weights[new_id] = random.uniform(-0.5, 0.5)
    
    def _randomize_weak_connections(self):
        """Randomize weak connections to explore new paths."""
        for layer in self.layers.values():
            for neuron in layer.neurons.values():
                for input_id, weight in list(neuron.weights.items()):
                    if abs(weight) < 0.05:
                        neuron.weights[input_id] = random.uniform(-0.5, 0.5)
    
    def _strengthen_successful_paths(self):
        """Strengthen connections that contributed to successful executions."""
        if not self.success_history:
            return
        
        # Get recent success rate
        recent = list(self.success_history)[-20:]
        success_rate = sum(recent) / len(recent)
        
        # Adjust all weights toward success
        gradient = 1.0 - success_rate  # Error signal
        
        for layer_id in sorted(self.layers.keys(), reverse=True):
            if layer_id == 0:  # Skip input layer
                continue
            
            for neuron in self.layers[layer_id].neurons.values():
                neuron.adjust_weights(gradient, self.current_learning_rate)
                
                # Update contribution score
                neuron.contribution_score = (
                    0.9 * neuron.contribution_score +
                    0.1 * (1.0 - abs(neuron.gradient))
                )
    
    def _update_learning_rate(self):
        """Adjust learning rate based on performance trend."""
        if len(self.fitness_history) < 2:
            return
        
        recent = list(self.fitness_history)[-10:]
        if len(recent) >= 2:
            # Check if improving
            first_half = recent[:len(recent)//2]
            second_half = recent[len(recent)//2:]
            
            first_avg = sum(first_half) / len(first_half) if first_half else 0
            second_avg = sum(second_half) / len(second_half) if second_half else 0
            
            if second_avg > first_avg:
                # Improving - reduce learning rate for stability
                self.current_learning_rate *= self.config.learning_rate_decay
            else:
                # Not improving - increase learning rate to explore more
                self.current_learning_rate *= 1.1
            
            # Keep within bounds
            self.current_learning_rate = max(
                self.config.min_learning_rate,
                min(self.config.max_learning_rate, self.current_learning_rate)
            )
    
    def _get_architecture_summary(self) -> str:
        """Get a summary string of the architecture."""
        layer_sizes = []
        for layer_id in sorted(self.layers.keys()):
            layer_sizes.append(len(self.layers[layer_id].neurons))
        return " -> ".join(str(s) for s in layer_sizes)
    
    def get_recommendations(self, context: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Get workflow parameter recommendations.
        
        Args:
            context: Current execution context
        
        Returns:
            Recommended parameter values
        """
        if context is None:
            context = self._get_default_context()
        
        # Forward pass through network
        outputs = self.forward(context)
        
        # Scale outputs to reasonable parameter ranges
        recommendations = {
            'timeout': 30 + outputs.get('timeout', 0.5) * 270,  # 30-300
            'retries': 1 + int(outputs.get('retries', 0.5) * 4),  # 1-5
            'concurrency': 1 + int(outputs.get('concurrency', 0.5) * 9),  # 1-10
            'priority': int(outputs.get('priority', 0.5) * 100)  # 0-100
        }
        
        return recommendations
    
    def _get_default_context(self) -> Dict[str, float]:
        """Get default context based on current time and history."""
        now = datetime.now(timezone.utc)
        
        return {
            'hour_of_day': now.hour / 24.0,
            'day_of_week': now.weekday() / 7.0,
            'recent_success_rate': self.get_success_rate(),
            'execution_frequency': min(1.0, self.execution_count / 100.0),
            'avg_duration': 0.5  # Normalized placeholder
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current architecture status."""
        return {
            'workflow_name': self.workflow_name,
            'success_rate': self.get_success_rate(),
            'execution_count': self.execution_count,
            'evolution_count': self.evolution_count,
            'last_evolution': self.last_evolution_time,
            'current_learning_rate': self.current_learning_rate,
            'architecture_fitness': self.architecture_fitness,
            'architecture_summary': self._get_architecture_summary(),
            'layer_details': {
                layer_id: {
                    'type': layer.layer_type,
                    'neurons': len(layer.neurons)
                }
                for layer_id, layer in self.layers.items()
            },
            'recognized_patterns': len(self.recognized_patterns)
        }
    
    def generate_report(self) -> str:
        """Generate a detailed status report."""
        lines = [
            f"\n🧠 Self-Evolving Neural Architecture Report",
            f"=" * 60,
            f"Workflow: {self.workflow_name}",
            f"",
            f"📊 Performance Metrics:",
            f"   Success Rate: {self.get_success_rate():.1%}",
            f"   Executions: {self.execution_count}",
            f"   Evolutions: {self.evolution_count}",
            f"   Architecture Fitness: {self.architecture_fitness:.1%}",
            f"   Current Learning Rate: {self.current_learning_rate:.4f}",
            f"",
            f"🏗️ Architecture:",
            f"   Structure: {self._get_architecture_summary()}",
        ]
        
        for layer_id, layer in sorted(self.layers.items()):
            lines.append(f"   Layer {layer_id} ({layer.layer_type}): {len(layer.neurons)} neurons")
        
        lines.extend([
            f"",
            f"🔍 Recognized Patterns:",
        ])
        
        for pattern_id, pattern in self.recognized_patterns.items():
            lines.append(f"   {pattern_id}: {pattern.occurrences} occurrences (confidence: {pattern.confidence:.1%})")
        
        if self.last_evolution_time:
            lines.append(f"")
            lines.append(f"⏰ Last Evolution: {self.last_evolution_time}")
        
        lines.extend([
            f"",
            "=" * 60,
            f"🤖 Report generated by @create-guru"
        ])
        
        return "\n".join(lines)


class EvolvingArchitectureManager:
    """
    Manager for multiple self-evolving architectures.
    
    Coordinates evolution across multiple workflows and
    enables cross-workflow learning.
    """
    
    def __init__(self, repo_root: str = None):
        """Initialize the architecture manager."""
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path.cwd()
        
        self.storage_path = self.repo_root / '.github' / 'agent-system' / 'evolving_architectures'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.architectures: Dict[str, SelfEvolvingNeuralArchitecture] = {}
        
        # Load existing architectures
        self._load_existing_architectures()
    
    def _load_existing_architectures(self):
        """Load all existing architectures from storage."""
        if self.storage_path.exists():
            for arch_file in self.storage_path.glob("*.json"):
                try:
                    with open(arch_file, 'r') as f:
                        data = json.load(f)
                    workflow_name = data.get('workflow_name', arch_file.stem)
                    self.architectures[workflow_name] = SelfEvolvingNeuralArchitecture(
                        workflow_name=workflow_name,
                        repo_root=str(self.repo_root)
                    )
                except Exception as e:
                    print(f"Warning: Could not load {arch_file}: {e}", file=sys.stderr)
    
    def get_or_create(self, workflow_name: str) -> SelfEvolvingNeuralArchitecture:
        """Get existing or create new architecture for workflow."""
        if workflow_name not in self.architectures:
            self.architectures[workflow_name] = SelfEvolvingNeuralArchitecture(
                workflow_name=workflow_name,
                repo_root=str(self.repo_root)
            )
        return self.architectures[workflow_name]
    
    def record_execution(self, workflow_name: str, success: bool,
                        context: Optional[Dict[str, Any]] = None):
        """Record execution for a workflow."""
        arch = self.get_or_create(workflow_name)
        arch.record_execution(success, context)
    
    def get_recommendations(self, workflow_name: str,
                           context: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Get parameter recommendations for a workflow."""
        arch = self.get_or_create(workflow_name)
        return arch.get_recommendations(context)
    
    def evolve_all(self):
        """Trigger evolution check for all architectures."""
        print("\n🧬 Evolution Cycle - Checking all architectures")
        print("=" * 60)
        
        evolved = 0
        for workflow_name, arch in self.architectures.items():
            if arch._should_evolve():
                arch.evolve()
                evolved += 1
        
        print(f"\n✅ Evolution cycle complete. {evolved}/{len(self.architectures)} architectures evolved.")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all architectures."""
        summary = {
            'total_architectures': len(self.architectures),
            'total_executions': sum(a.execution_count for a in self.architectures.values()),
            'total_evolutions': sum(a.evolution_count for a in self.architectures.values()),
            'average_success_rate': 0.0,
            'architectures': {}
        }
        
        if self.architectures:
            success_rates = [a.get_success_rate() for a in self.architectures.values()]
            summary['average_success_rate'] = sum(success_rates) / len(success_rates)
        
        for name, arch in self.architectures.items():
            summary['architectures'][name] = arch.get_status()
        
        return summary
    
    def generate_full_report(self) -> str:
        """Generate comprehensive report for all architectures."""
        lines = [
            "\n🧠 Self-Evolving Neural Architecture System Report",
            "=" * 70,
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "📊 System Overview:",
        ]
        
        summary = self.get_summary()
        lines.extend([
            f"   Total Architectures: {summary['total_architectures']}",
            f"   Total Executions: {summary['total_executions']}",
            f"   Total Evolutions: {summary['total_evolutions']}",
            f"   Average Success Rate: {summary['average_success_rate']:.1%}",
            "",
        ])
        
        for name, arch in sorted(self.architectures.items()):
            lines.append("-" * 70)
            lines.append(arch.generate_report())
        
        lines.extend([
            "",
            "=" * 70,
            "🤖 Report generated by @create-guru's Self-Evolving Neural Architecture System",
        ])
        
        return "\n".join(lines)


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Self-Evolving Neural Architecture for Workflow Adaptation"
    )
    parser.add_argument(
        '--workflow',
        metavar='NAME',
        help='Workflow name to operate on'
    )
    parser.add_argument(
        '--record',
        choices=['success', 'failure'],
        help='Record an execution result'
    )
    parser.add_argument(
        '--recommend',
        action='store_true',
        help='Get parameter recommendations'
    )
    parser.add_argument(
        '--evolve',
        action='store_true',
        help='Force evolution of architecture'
    )
    parser.add_argument(
        '--evolve-all',
        action='store_true',
        help='Check and evolve all architectures'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show architecture status'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed report'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary of all architectures'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    manager = EvolvingArchitectureManager()
    
    if args.workflow and args.record:
        success = args.record == 'success'
        manager.record_execution(args.workflow, success)
        print(f"✅ Recorded {'success' if success else 'failure'} for {args.workflow}")
    
    elif args.workflow and args.recommend:
        recommendations = manager.get_recommendations(args.workflow)
        if args.json:
            print(json.dumps(recommendations, indent=2))
        else:
            print(f"\n📋 Recommendations for {args.workflow}:")
            for param, value in recommendations.items():
                print(f"   {param}: {value:.2f}")
    
    elif args.workflow and args.evolve:
        arch = manager.get_or_create(args.workflow)
        arch.evolve()
    
    elif args.evolve_all:
        manager.evolve_all()
    
    elif args.workflow and args.status:
        arch = manager.get_or_create(args.workflow)
        status = arch.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(arch.generate_report())
    
    elif args.report:
        print(manager.generate_full_report())
    
    elif args.summary:
        summary = manager.get_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n📊 System Summary:")
            print(f"   Architectures: {summary['total_architectures']}")
            print(f"   Executions: {summary['total_executions']}")
            print(f"   Evolutions: {summary['total_evolutions']}")
            print(f"   Avg Success Rate: {summary['average_success_rate']:.1%}")
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
