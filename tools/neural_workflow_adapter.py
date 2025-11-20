#!/usr/bin/env python3
"""
Neural Workflow Adapter - Self-Evolving Architecture System
Created by @workflows-tech-lead

A neural-inspired adaptive system that monitors workflow success rates and
automatically evolves workflow configurations to optimize performance.

This system implements:
- Neural network-inspired weight adjustments for workflow parameters
- Success rate tracking and trend analysis
- Adaptive learning from workflow outcomes
- Automatic configuration optimization
- Backpropagation-style feedback loops

Architecture:
- Input Layer: Workflow execution data, success rates, metrics
- Hidden Layer: Weighted parameter adjustments (weights, biases)
- Output Layer: Optimized workflow configurations
- Learning: Gradient descent-inspired adaptation from feedback
"""

import json
import os
import sys
import math
import statistics
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from workflow_execution_tracker import WorkflowExecutionTracker
except ImportError:
    WorkflowExecutionTracker = None


@dataclass
class NeuralWeight:
    """
    Represents a neural weight for a workflow parameter.
    
    Like neurons in a neural network, these weights are adjusted
    based on feedback (backpropagation analogy).
    """
    parameter_name: str
    current_value: float
    weight: float  # Neural weight (0.0-1.0)
    bias: float  # Neural bias (-1.0 to 1.0)
    gradient: float = 0.0  # Gradient for learning
    momentum: float = 0.0  # Momentum for smooth updates
    learning_history: List[float] = field(default_factory=list)
    
    def adjust(self, gradient: float, learning_rate: float = 0.01, momentum: float = 0.9):
        """
        Adjust weight using gradient descent with momentum.
        
        Args:
            gradient: Error gradient
            learning_rate: Learning rate (0.0-1.0)
            momentum: Momentum factor (0.0-1.0)
        """
        # Update momentum (exponential moving average of gradients)
        self.momentum = momentum * self.momentum + (1 - momentum) * gradient
        
        # Update weight
        self.weight = max(0.0, min(1.0, self.weight - learning_rate * self.momentum))
        
        # Store gradient for analysis
        self.gradient = gradient
        self.learning_history.append(self.weight)
        
        # Keep history bounded
        if len(self.learning_history) > 100:
            self.learning_history.pop(0)
    
    def compute_value(self) -> float:
        """Compute the output value using neural activation function."""
        # Weighted sum with bias
        z = self.current_value * self.weight + self.bias
        
        # ReLU-like activation (ensure positive)
        return max(0.1, z)


@dataclass
class WorkflowNeuralArchitecture:
    """
    Neural architecture for a specific workflow.
    
    Represents the "brain" of workflow optimization with layers of
    interconnected parameters that adapt based on success.
    """
    workflow_name: str
    weights: Dict[str, NeuralWeight]  # Parameter name -> weight
    success_history: deque = field(default_factory=lambda: deque(maxlen=50))
    adaptation_count: int = 0
    last_adapted: Optional[str] = None
    confidence: float = 0.5  # Confidence in current configuration
    
    def compute_success_rate(self) -> float:
        """Compute recent success rate."""
        if not self.success_history:
            return 0.5  # Neutral default
        return sum(self.success_history) / len(self.success_history)
    
    def compute_success_variance(self) -> float:
        """Compute variance in success (instability metric)."""
        if len(self.success_history) < 2:
            return 1.0  # High variance when insufficient data
        return statistics.variance(self.success_history)
    
    def record_execution(self, success: bool):
        """Record a workflow execution result."""
        self.success_history.append(1.0 if success else 0.0)
    
    def needs_adaptation(self, threshold: float = 0.7) -> bool:
        """
        Determine if workflow needs adaptation.
        
        Args:
            threshold: Success rate threshold below which to adapt
        
        Returns:
            True if adaptation is needed
        """
        if len(self.success_history) < 5:
            return False  # Need minimum data
        
        success_rate = self.compute_success_rate()
        variance = self.compute_success_variance()
        
        # Adapt if success rate is low or variance is high
        return success_rate < threshold or variance > 0.3
    
    def adapt(self, learning_rate: float = 0.01):
        """
        Adapt neural weights based on current performance.
        
        Uses backpropagation-inspired learning from success feedback.
        
        Args:
            learning_rate: Learning rate for weight updates
        """
        success_rate = self.compute_success_rate()
        target_success_rate = 0.95  # Target 95% success
        
        # Compute error (loss function)
        error = target_success_rate - success_rate
        
        # Adjust each parameter weight
        for param_name, weight_obj in self.weights.items():
            # Compute gradient (simplified - assumes linear relationship)
            # In real neural nets, this would use chain rule
            gradient = error * (1.0 if success_rate < target_success_rate else -1.0)
            
            # Adjust weight with momentum
            weight_obj.adjust(gradient, learning_rate=learning_rate)
        
        self.adaptation_count += 1
        self.last_adapted = datetime.now(timezone.utc).isoformat()
        
        # Update confidence based on success variance
        variance = self.compute_success_variance()
        self.confidence = 1.0 - min(1.0, variance)


class NeuralWorkflowAdapter:
    """
    Main neural adaptation system for workflows.
    
    Monitors workflow success rates and automatically evolves configurations
    using neural network-inspired learning algorithms.
    """
    
    def __init__(self, repo_root: str = None):
        """
        Initialize the neural workflow adapter.
        
        Args:
            repo_root: Repository root path
        """
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
        
        # Storage paths
        self.neural_config_path = self.repo_root / '.github' / 'agent-system' / 'neural_config.json'
        self.neural_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Neural architectures for each workflow
        self.architectures: Dict[str, WorkflowNeuralArchitecture] = {}
        
        # Global learning parameters
        self.global_learning_rate = 0.01
        self.adaptation_threshold = 0.7  # Success rate threshold
        
        # Load existing configuration
        self._load_config()
        
        # Initialize workflow tracker if available
        self.tracker = None
        if WorkflowExecutionTracker:
            try:
                self.tracker = WorkflowExecutionTracker(repo_root=str(self.repo_root))
            except Exception as e:
                print(f"Warning: Could not initialize workflow tracker: {e}", file=sys.stderr)
    
    def _load_config(self):
        """Load neural configuration from file."""
        if self.neural_config_path.exists():
            try:
                with open(self.neural_config_path, 'r') as f:
                    data = json.load(f)
                
                self.global_learning_rate = data.get('global_learning_rate', 0.01)
                self.adaptation_threshold = data.get('adaptation_threshold', 0.7)
                
                # Load architectures
                for arch_data in data.get('architectures', []):
                    arch = self._architecture_from_dict(arch_data)
                    self.architectures[arch.workflow_name] = arch
                
                print(f"✅ Loaded neural config for {len(self.architectures)} workflows")
            except Exception as e:
                print(f"Warning: Could not load neural config: {e}", file=sys.stderr)
    
    def _save_config(self):
        """Save neural configuration to file."""
        try:
            data = {
                'version': '1.0.0',
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'global_learning_rate': self.global_learning_rate,
                'adaptation_threshold': self.adaptation_threshold,
                'architectures': [
                    self._architecture_to_dict(arch)
                    for arch in self.architectures.values()
                ]
            }
            
            with open(self.neural_config_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Saved neural config for {len(self.architectures)} workflows")
        except Exception as e:
            print(f"Error: Could not save neural config: {e}", file=sys.stderr)
    
    def _architecture_to_dict(self, arch: WorkflowNeuralArchitecture) -> Dict[str, Any]:
        """Convert architecture to dictionary."""
        return {
            'workflow_name': arch.workflow_name,
            'weights': {
                name: {
                    'parameter_name': w.parameter_name,
                    'current_value': w.current_value,
                    'weight': w.weight,
                    'bias': w.bias,
                    'gradient': w.gradient,
                    'momentum': w.momentum,
                    'learning_history': w.learning_history
                }
                for name, w in arch.weights.items()
            },
            'success_history': list(arch.success_history),
            'adaptation_count': arch.adaptation_count,
            'last_adapted': arch.last_adapted,
            'confidence': arch.confidence
        }
    
    def _architecture_from_dict(self, data: Dict[str, Any]) -> WorkflowNeuralArchitecture:
        """Create architecture from dictionary."""
        weights = {}
        for name, w_data in data.get('weights', {}).items():
            weights[name] = NeuralWeight(
                parameter_name=w_data['parameter_name'],
                current_value=w_data['current_value'],
                weight=w_data['weight'],
                bias=w_data['bias'],
                gradient=w_data.get('gradient', 0.0),
                momentum=w_data.get('momentum', 0.0),
                learning_history=w_data.get('learning_history', [])
            )
        
        arch = WorkflowNeuralArchitecture(
            workflow_name=data['workflow_name'],
            weights=weights,
            adaptation_count=data.get('adaptation_count', 0),
            last_adapted=data.get('last_adapted'),
            confidence=data.get('confidence', 0.5)
        )
        
        # Restore success history
        arch.success_history = deque(data.get('success_history', []), maxlen=50)
        
        return arch
    
    def register_workflow(self, workflow_name: str, parameters: Dict[str, float]):
        """
        Register a workflow for neural adaptation.
        
        Args:
            workflow_name: Name of the workflow
            parameters: Initial parameter values (e.g., {'timeout': 300, 'retries': 3})
        """
        if workflow_name in self.architectures:
            print(f"⚠️  Workflow {workflow_name} already registered")
            return
        
        # Create neural weights for each parameter
        weights = {}
        for param_name, initial_value in parameters.items():
            weights[param_name] = NeuralWeight(
                parameter_name=param_name,
                current_value=initial_value,
                weight=0.8,  # Start optimistic
                bias=0.1,  # Slight positive bias
                learning_history=[]
            )
        
        arch = WorkflowNeuralArchitecture(
            workflow_name=workflow_name,
            weights=weights
        )
        
        self.architectures[workflow_name] = arch
        print(f"✅ Registered workflow: {workflow_name} with {len(parameters)} parameters")
    
    def record_execution(self, workflow_name: str, success: bool):
        """
        Record a workflow execution result.
        
        Args:
            workflow_name: Name of the workflow
            success: Whether execution was successful
        """
        if workflow_name not in self.architectures:
            print(f"⚠️  Unknown workflow: {workflow_name}")
            return
        
        arch = self.architectures[workflow_name]
        arch.record_execution(success)
        
        print(f"📊 Recorded execution for {workflow_name}: {'✅' if success else '❌'}")
        print(f"   Success rate: {arch.compute_success_rate():.1%}")
    
    def adapt_workflow(self, workflow_name: str) -> Optional[Dict[str, float]]:
        """
        Adapt a workflow's configuration based on performance.
        
        Args:
            workflow_name: Name of the workflow
        
        Returns:
            Optimized parameter values, or None if no adaptation needed
        """
        if workflow_name not in self.architectures:
            print(f"⚠️  Unknown workflow: {workflow_name}")
            return None
        
        arch = self.architectures[workflow_name]
        
        if not arch.needs_adaptation(threshold=self.adaptation_threshold):
            print(f"✅ No adaptation needed for {workflow_name} (success rate: {arch.compute_success_rate():.1%})")
            return None
        
        print(f"🧠 Adapting neural architecture for {workflow_name}...")
        print(f"   Current success rate: {arch.compute_success_rate():.1%}")
        print(f"   Variance: {arch.compute_success_variance():.3f}")
        
        # Perform neural adaptation
        arch.adapt(learning_rate=self.global_learning_rate)
        
        # Compute new parameter values
        optimized_params = {}
        for param_name, weight_obj in arch.weights.items():
            optimized_params[param_name] = weight_obj.compute_value()
        
        print(f"✅ Adaptation complete (iteration {arch.adaptation_count})")
        print(f"   Confidence: {arch.confidence:.1%}")
        print(f"   Optimized parameters:")
        for param, value in optimized_params.items():
            print(f"      {param}: {value:.2f}")
        
        return optimized_params
    
    def adapt_all_workflows(self) -> Dict[str, Optional[Dict[str, float]]]:
        """
        Adapt all registered workflows that need it.
        
        Returns:
            Dictionary of workflow_name -> optimized parameters
        """
        results = {}
        
        print(f"\n🧠 Neural Workflow Adaptation Cycle")
        print(f"=" * 60)
        print(f"Evaluating {len(self.architectures)} workflows...\n")
        
        for workflow_name in self.architectures:
            optimized = self.adapt_workflow(workflow_name)
            results[workflow_name] = optimized
        
        print(f"\n{'=' * 60}")
        
        adapted_count = sum(1 for v in results.values() if v is not None)
        print(f"✅ Adapted {adapted_count}/{len(self.architectures)} workflows")
        
        # Save updated configuration
        self._save_config()
        
        return results
    
    def get_workflow_status(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a workflow's neural architecture.
        
        Args:
            workflow_name: Name of the workflow
        
        Returns:
            Status dictionary or None if workflow not found
        """
        if workflow_name not in self.architectures:
            return None
        
        arch = self.architectures[workflow_name]
        
        return {
            'workflow_name': workflow_name,
            'success_rate': arch.compute_success_rate(),
            'variance': arch.compute_success_variance(),
            'confidence': arch.confidence,
            'adaptation_count': arch.adaptation_count,
            'last_adapted': arch.last_adapted,
            'needs_adaptation': arch.needs_adaptation(self.adaptation_threshold),
            'parameters': {
                name: {
                    'current_value': w.current_value,
                    'weight': w.weight,
                    'bias': w.bias,
                    'computed_value': w.compute_value()
                }
                for name, w in arch.weights.items()
            }
        }
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive adaptation report.
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("🧠 Neural Workflow Adaptation Report")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"Total workflows: {len(self.architectures)}")
        report.append(f"Global learning rate: {self.global_learning_rate}")
        report.append(f"Adaptation threshold: {self.adaptation_threshold:.1%}")
        report.append("")
        
        # Summary statistics
        if self.architectures:
            success_rates = [arch.compute_success_rate() for arch in self.architectures.values()]
            report.append(f"Average success rate: {statistics.mean(success_rates):.1%}")
            report.append(f"Success rate range: {min(success_rates):.1%} - {max(success_rates):.1%}")
            report.append("")
        
        # Per-workflow details
        for workflow_name, arch in sorted(self.architectures.items()):
            report.append(f"\n📊 {workflow_name}")
            report.append("-" * 80)
            report.append(f"Success rate: {arch.compute_success_rate():.1%} ({len(arch.success_history)} executions)")
            report.append(f"Variance: {arch.compute_success_variance():.3f}")
            report.append(f"Confidence: {arch.confidence:.1%}")
            report.append(f"Adaptations: {arch.adaptation_count}")
            if arch.last_adapted:
                report.append(f"Last adapted: {arch.last_adapted}")
            report.append(f"Needs adaptation: {'Yes ⚠️' if arch.needs_adaptation(self.adaptation_threshold) else 'No ✅'}")
            
            report.append(f"\nParameters:")
            for param_name, weight_obj in arch.weights.items():
                report.append(f"  {param_name}:")
                report.append(f"    Current: {weight_obj.current_value:.2f}")
                report.append(f"    Weight: {weight_obj.weight:.3f}")
                report.append(f"    Bias: {weight_obj.bias:.3f}")
                report.append(f"    Computed: {weight_obj.compute_value():.2f}")
        
        report.append("\n" + "=" * 80)
        report.append("🤖 Report generated by @workflows-tech-lead's Neural Workflow Adapter")
        
        return "\n".join(report)


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Neural Workflow Adapter - Self-evolving workflow optimization"
    )
    parser.add_argument(
        '--register',
        metavar='WORKFLOW',
        help='Register a workflow for adaptation'
    )
    parser.add_argument(
        '--params',
        type=json.loads,
        help='Initial parameters (JSON format)'
    )
    parser.add_argument(
        '--record',
        metavar='WORKFLOW',
        help='Record an execution result'
    )
    parser.add_argument(
        '--success',
        action='store_true',
        help='Execution was successful'
    )
    parser.add_argument(
        '--adapt',
        metavar='WORKFLOW',
        help='Adapt a specific workflow'
    )
    parser.add_argument(
        '--adapt-all',
        action='store_true',
        help='Adapt all registered workflows'
    )
    parser.add_argument(
        '--status',
        metavar='WORKFLOW',
        help='Get workflow status'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive report'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    adapter = NeuralWorkflowAdapter()
    
    # Register workflow
    if args.register:
        if not args.params:
            print("Error: --params required when registering", file=sys.stderr)
            sys.exit(1)
        adapter.register_workflow(args.register, args.params)
        adapter._save_config()
    
    # Record execution
    elif args.record:
        adapter.record_execution(args.record, args.success)
        adapter._save_config()
    
    # Adapt workflow
    elif args.adapt:
        result = adapter.adapt_workflow(args.adapt)
        if args.json:
            print(json.dumps(result, indent=2))
        adapter._save_config()
    
    # Adapt all workflows
    elif args.adapt_all:
        results = adapter.adapt_all_workflows()
        if args.json:
            print(json.dumps(results, indent=2))
    
    # Get status
    elif args.status:
        status = adapter.get_workflow_status(args.status)
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(json.dumps(status, indent=2))
    
    # Generate report
    elif args.report:
        report = adapter.generate_report()
        print(report)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
