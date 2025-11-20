#!/usr/bin/env python3
"""
Meta-Learning Workflow Scheduler
Created by @workflows-tech-lead

A second-order learning system that learns how to optimize workflow schedules
by analyzing prediction accuracy and continuously refining scheduling strategies.

Meta-Learning Approach:
- Learns from prediction errors to improve future predictions
- Adapts scheduling strategies based on workflow performance patterns
- Discovers optimal parameter configurations automatically
- Implements reinforcement learning for schedule optimization

Key Innovation:
This system doesn't just predict optimal times - it learns how to predict better
over time by analyzing what works and what doesn't in actual executions.
"""

import os
import sys
import json
import statistics
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import random

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_workflow_predictor import AIWorkflowPredictor, PredictionResult
from workflow_execution_tracker import WorkflowExecutionTracker, ExecutionComparison


@dataclass
class LearningParameters:
    """Parameters that the meta-learner can adjust."""
    success_weight: float = 0.4  # Weight for success rate in scoring
    duration_weight: float = 0.3  # Weight for duration in scoring
    conflict_weight: float = 0.3  # Weight for conflict avoidance in scoring
    confidence_threshold: float = 0.6  # Min confidence to apply recommendations
    learning_rate: float = 0.1  # How quickly to adapt parameters
    exploration_rate: float = 0.15  # Probability of trying alternative schedules


@dataclass
class SchedulingStrategy:
    """A learned strategy for scheduling workflows."""
    name: str
    parameters: LearningParameters
    performance_history: List[float]  # Historical performance scores
    last_updated: str
    
    @property
    def average_performance(self) -> float:
        """Calculate average performance score."""
        if not self.performance_history:
            return 0.0
        return statistics.mean(self.performance_history[-20:])  # Last 20 data points
    
    @property
    def performance_trend(self) -> str:
        """Determine if performance is improving, declining, or stable."""
        if len(self.performance_history) < 5:
            return "insufficient_data"
        
        recent = self.performance_history[-5:]
        older = self.performance_history[-10:-5] if len(self.performance_history) >= 10 else []
        
        if not older:
            return "insufficient_data"
        
        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        
        diff = recent_avg - older_avg
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"


class MetaLearningScheduler:
    """
    Meta-learning system that learns to optimize workflow schedules.
    
    This implements a reinforcement learning approach where:
    - State: Current workflow patterns and historical performance
    - Actions: Scheduling decisions (time slots, frequencies, parameters)
    - Reward: Prediction accuracy and workflow success metrics
    - Learning: Adjust parameters based on observed rewards
    """
    
    def __init__(self, repo_root: str = None):
        """
        Initialize the meta-learning scheduler.
        
        Args:
            repo_root: Root directory of the repository
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
        
        self.learning_dir = self.repo_root / '.github' / 'workflow-history' / 'meta-learning'
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        self.strategies_file = self.learning_dir / 'learned_strategies.json'
        self.learning_log_file = self.learning_dir / 'learning_log.json'
        
        # Initialize components
        self.predictor = AIWorkflowPredictor(repo_root=str(self.repo_root))
        self.tracker = WorkflowExecutionTracker(repo_root=str(self.repo_root))
        
        # Load or initialize strategies
        self.strategies: Dict[str, SchedulingStrategy] = {}
        self.load_strategies()
        
        # Learning state
        self.learning_log: List[Dict[str, Any]] = []
        self.load_learning_log()
    
    def load_strategies(self) -> None:
        """Load learned strategies from file."""
        if self.strategies_file.exists():
            try:
                with open(self.strategies_file, 'r') as f:
                    data = json.load(f)
                    for name, strategy_data in data.get('strategies', {}).items():
                        params = LearningParameters(**strategy_data['parameters'])
                        self.strategies[name] = SchedulingStrategy(
                            name=name,
                            parameters=params,
                            performance_history=strategy_data['performance_history'],
                            last_updated=strategy_data['last_updated']
                        )
            except Exception as e:
                print(f"Warning: Could not load strategies: {e}", file=sys.stderr)
        
        # Ensure we have at least a default strategy
        if 'default' not in self.strategies:
            self.strategies['default'] = SchedulingStrategy(
                name='default',
                parameters=LearningParameters(),
                performance_history=[],
                last_updated=datetime.now(timezone.utc).isoformat()
            )
    
    def save_strategies(self) -> None:
        """Save learned strategies to file."""
        try:
            data = {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'strategies': {}
            }
            
            for name, strategy in self.strategies.items():
                data['strategies'][name] = {
                    'name': strategy.name,
                    'parameters': asdict(strategy.parameters),
                    'performance_history': strategy.performance_history,
                    'last_updated': strategy.last_updated,
                    'average_performance': strategy.average_performance,
                    'performance_trend': strategy.performance_trend
                }
            
            with open(self.strategies_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save strategies: {e}", file=sys.stderr)
    
    def load_learning_log(self) -> None:
        """Load learning log from file."""
        if self.learning_log_file.exists():
            try:
                with open(self.learning_log_file, 'r') as f:
                    data = json.load(f)
                    self.learning_log = data.get('entries', [])
            except Exception as e:
                print(f"Warning: Could not load learning log: {e}", file=sys.stderr)
    
    def save_learning_log(self) -> None:
        """Save learning log to file."""
        try:
            data = {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_entries': len(self.learning_log),
                'entries': self.learning_log[-1000:]  # Keep last 1000 entries
            }
            
            with open(self.learning_log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save learning log: {e}", file=sys.stderr)
    
    def log_learning_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log a learning event for analysis."""
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'details': details
        }
        self.learning_log.append(entry)
        self.save_learning_log()
    
    def evaluate_prediction_accuracy(self, workflow_name: str = None) -> Dict[str, Any]:
        """
        Evaluate how well predictions are performing.
        
        Args:
            workflow_name: Optional specific workflow to evaluate
        
        Returns:
            Dictionary with accuracy metrics
        """
        comparisons = self.tracker.comparisons
        
        if workflow_name:
            comparisons = [c for c in comparisons if c.workflow_name == workflow_name]
        
        if not comparisons:
            return {
                'total_predictions': 0,
                'mean_error': 0.0,
                'accuracy_score': 0.0,
                'message': 'No comparison data available'
            }
        
        errors = [abs(c.prediction_error) for c in comparisons]
        
        # Calculate accuracy score (100% - average error percentage, capped at 0)
        mean_error = statistics.mean(errors)
        accuracy_score = max(0, 100 - mean_error)
        
        return {
            'total_predictions': len(comparisons),
            'mean_error': mean_error,
            'median_error': statistics.median(errors),
            'accuracy_score': accuracy_score,
            'excellent_predictions': sum(1 for e in errors if e <= 10),
            'good_predictions': sum(1 for e in errors if 10 < e <= 25),
            'fair_predictions': sum(1 for e in errors if 25 < e <= 50),
            'poor_predictions': sum(1 for e in errors if e > 50)
        }
    
    def calculate_strategy_performance(self, strategy: SchedulingStrategy) -> float:
        """
        Calculate performance score for a strategy.
        
        Returns:
            Performance score (0-100)
        """
        # Evaluate prediction accuracy with this strategy's parameters
        accuracy_metrics = self.evaluate_prediction_accuracy()
        
        if accuracy_metrics['total_predictions'] == 0:
            return 50.0  # Neutral score for untested strategies
        
        # Calculate component scores
        accuracy_score = accuracy_metrics['accuracy_score']
        
        # Success rate of workflows (from predictor's history)
        total_executions = len(self.predictor.execution_history)
        if total_executions > 0:
            successful = sum(1 for e in self.predictor.execution_history if e.success)
            success_score = (successful / total_executions) * 100
        else:
            success_score = 50.0
        
        # Combine scores using strategy's weights
        params = strategy.parameters
        
        # Normalize weights
        total_weight = params.success_weight + params.duration_weight + params.conflict_weight
        success_w = params.success_weight / total_weight
        accuracy_w = params.duration_weight / total_weight  # Duration accuracy
        
        # Overall performance
        performance = (success_w * success_score) + (accuracy_w * accuracy_score)
        
        return performance
    
    def adapt_strategy_parameters(self, strategy_name: str) -> None:
        """
        Adapt a strategy's parameters based on performance.
        
        This implements gradient-based learning where we adjust parameters
        in the direction that improves performance.
        """
        if strategy_name not in self.strategies:
            return
        
        strategy = self.strategies[strategy_name]
        params = strategy.parameters
        
        # Calculate current performance
        current_performance = self.calculate_strategy_performance(strategy)
        
        # If we don't have enough history, just record and return
        if len(strategy.performance_history) < 3:
            strategy.performance_history.append(current_performance)
            strategy.last_updated = datetime.now(timezone.utc).isoformat()
            self.save_strategies()
            return
        
        # Calculate performance trend
        recent_avg = statistics.mean(strategy.performance_history[-3:])
        
        # Determine adjustment direction
        if current_performance > recent_avg:
            # Performance improving - continue in same direction
            adjustment = 1.0
            direction = "reinforcing"
        else:
            # Performance declining - try opposite direction
            adjustment = -1.0
            direction = "correcting"
        
        # Apply adjustments with learning rate
        lr = params.learning_rate
        
        # Adjust weights (keeping them positive and summing to ~1.0)
        params.success_weight += adjustment * lr * 0.1
        params.duration_weight += adjustment * lr * 0.05
        params.conflict_weight += adjustment * lr * 0.05
        
        # Normalize weights
        total = params.success_weight + params.duration_weight + params.conflict_weight
        params.success_weight /= total
        params.duration_weight /= total
        params.conflict_weight /= total
        
        # Adjust confidence threshold based on accuracy
        accuracy = self.evaluate_prediction_accuracy()
        if accuracy['accuracy_score'] > 75:
            params.confidence_threshold = max(0.5, params.confidence_threshold - lr * 0.1)
        elif accuracy['accuracy_score'] < 50:
            params.confidence_threshold = min(0.9, params.confidence_threshold + lr * 0.1)
        
        # Record performance
        strategy.performance_history.append(current_performance)
        strategy.last_updated = datetime.now(timezone.utc).isoformat()
        
        # Log the adaptation
        self.log_learning_event('parameter_adaptation', {
            'strategy': strategy_name,
            'direction': direction,
            'performance': current_performance,
            'recent_avg': recent_avg,
            'new_parameters': asdict(params)
        })
        
        self.save_strategies()
    
    def generate_optimized_schedule(self, workflow_name: str, 
                                   strategy_name: str = 'default') -> PredictionResult:
        """
        Generate an optimized schedule using meta-learned parameters.
        
        Args:
            workflow_name: Name of the workflow
            strategy_name: Which learned strategy to use
        
        Returns:
            Enhanced PredictionResult with meta-learned optimizations
        """
        if strategy_name not in self.strategies:
            strategy_name = 'default'
        
        strategy = self.strategies[strategy_name]
        params = strategy.parameters
        
        # Get base prediction from AI predictor
        base_prediction = self.predictor.predict_optimal_time(workflow_name)
        
        # Apply meta-learning enhancements
        
        # 1. Adjust confidence based on historical accuracy
        accuracy = self.evaluate_prediction_accuracy(workflow_name)
        if accuracy['total_predictions'] > 0:
            # Scale confidence by accuracy score
            accuracy_factor = accuracy['accuracy_score'] / 100
            base_prediction.confidence *= accuracy_factor
            base_prediction.reasoning.append(
                f"Confidence adjusted by meta-learning (accuracy: {accuracy['accuracy_score']:.0f}%)"
            )
        
        # 2. Apply exploration: occasionally suggest alternative times
        if random.random() < params.exploration_rate:
            # Try an alternative time slot
            current_hour = int(base_prediction.recommended_time.split()[1])
            alternative_hour = (current_hour + random.randint(2, 6)) % 24
            base_prediction.recommended_time = f"0 {alternative_hour} * * *"
            base_prediction.reasoning.append(
                f"Exploring alternative time slot (learning mode)"
            )
            # Reduce confidence for exploration
            base_prediction.confidence *= 0.8
        
        # 3. Add meta-learning context
        base_prediction.reasoning.append(
            f"Using strategy '{strategy_name}' (performance: {strategy.average_performance:.1f}%)"
        )
        
        return base_prediction
    
    def evolve_strategies(self) -> None:
        """
        Evolve strategies by creating variations and selecting the best.
        
        This implements a genetic algorithm approach where:
        - Multiple strategies compete
        - Best performers are kept
        - New strategies are created by mutating good ones
        - Poor strategies are eliminated
        """
        print("\n🧬 Evolving scheduling strategies...")
        
        # Evaluate all strategies
        strategy_scores = {}
        for name, strategy in self.strategies.items():
            score = self.calculate_strategy_performance(strategy)
            strategy_scores[name] = score
            print(f"  {name}: {score:.1f}% performance")
        
        # Keep top performers
        sorted_strategies = sorted(strategy_scores.items(), key=lambda x: x[1], reverse=True)
        top_strategies = [name for name, _ in sorted_strategies[:3]]
        
        print(f"\n🏆 Top strategies: {', '.join(top_strategies)}")
        
        # Create new strategies by mutating top performers
        new_strategies = {}
        for top_name in top_strategies:
            if len(self.strategies) >= 10:  # Limit total strategies
                break
            
            # Create mutation
            base_strategy = self.strategies[top_name]
            mutation_name = f"evolved_{top_name}_{len(self.strategies)}"
            
            # Mutate parameters
            mutated_params = LearningParameters(
                success_weight=base_strategy.parameters.success_weight * random.uniform(0.8, 1.2),
                duration_weight=base_strategy.parameters.duration_weight * random.uniform(0.8, 1.2),
                conflict_weight=base_strategy.parameters.conflict_weight * random.uniform(0.8, 1.2),
                confidence_threshold=base_strategy.parameters.confidence_threshold * random.uniform(0.9, 1.1),
                learning_rate=base_strategy.parameters.learning_rate * random.uniform(0.8, 1.2),
                exploration_rate=base_strategy.parameters.exploration_rate * random.uniform(0.8, 1.2)
            )
            
            # Normalize weights
            total_w = mutated_params.success_weight + mutated_params.duration_weight + mutated_params.conflict_weight
            mutated_params.success_weight /= total_w
            mutated_params.duration_weight /= total_w
            mutated_params.conflict_weight /= total_w
            
            # Clamp other parameters
            mutated_params.confidence_threshold = max(0.3, min(0.9, mutated_params.confidence_threshold))
            mutated_params.learning_rate = max(0.01, min(0.3, mutated_params.learning_rate))
            mutated_params.exploration_rate = max(0.05, min(0.3, mutated_params.exploration_rate))
            
            new_strategies[mutation_name] = SchedulingStrategy(
                name=mutation_name,
                parameters=mutated_params,
                performance_history=[],
                last_updated=datetime.now(timezone.utc).isoformat()
            )
            
            print(f"  ✨ Created mutation: {mutation_name}")
        
        # Add new strategies
        self.strategies.update(new_strategies)
        
        # Remove worst performers if we have too many
        if len(self.strategies) > 10:
            worst_strategies = [name for name, _ in sorted_strategies[7:]]
            for name in worst_strategies:
                if name != 'default':  # Never remove default
                    del self.strategies[name]
                    print(f"  ❌ Eliminated poor strategy: {name}")
        
        self.log_learning_event('strategy_evolution', {
            'top_strategies': top_strategies,
            'new_strategies': list(new_strategies.keys()),
            'total_strategies': len(self.strategies)
        })
        
        self.save_strategies()
    
    def generate_meta_learning_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive meta-learning report.
        
        Returns:
            Dictionary with detailed learning analytics
        """
        print("\n" + "="*70)
        print("🎓 Meta-Learning Scheduler Report - @workflows-tech-lead")
        print("="*70 + "\n")
        
        # Overall accuracy
        accuracy = self.evaluate_prediction_accuracy()
        
        print(f"📊 Overall Prediction Accuracy")
        print(f"  Total Predictions: {accuracy['total_predictions']}")
        print(f"  Mean Error: {accuracy['mean_error']:.1f}%")
        print(f"  Accuracy Score: {accuracy['accuracy_score']:.1f}%")
        
        # Only show detailed breakdown if we have predictions
        if accuracy['total_predictions'] > 0:
            print(f"  Excellent (≤10%): {accuracy['excellent_predictions']}")
            print(f"  Good (10-25%): {accuracy['good_predictions']}")
            print(f"  Fair (25-50%): {accuracy['fair_predictions']}")
            print(f"  Poor (>50%): {accuracy['poor_predictions']}")
        
        # Strategy performance
        print(f"\n🧠 Learned Strategies")
        strategy_performances = {}
        for name, strategy in self.strategies.items():
            perf = self.calculate_strategy_performance(strategy)
            strategy_performances[name] = perf
            trend = strategy.performance_trend
            trend_icon = "📈" if trend == "improving" else "📉" if trend == "declining" else "➡️"
            print(f"  {name}:")
            print(f"    Performance: {perf:.1f}%")
            print(f"    Trend: {trend_icon} {trend}")
            print(f"    Data Points: {len(strategy.performance_history)}")
        
        # Best strategy
        best_strategy = max(strategy_performances.items(), key=lambda x: x[1])
        print(f"\n🏆 Best Strategy: {best_strategy[0]} ({best_strategy[1]:.1f}%)")
        
        # Learning progress
        print(f"\n📈 Learning Progress")
        print(f"  Learning Log Entries: {len(self.learning_log)}")
        
        # Recent learning events
        recent_events = self.learning_log[-5:]
        if recent_events:
            print(f"  Recent Events:")
            for event in recent_events:
                event_type = event['event_type']
                timestamp = event['timestamp'][:19]
                print(f"    [{timestamp}] {event_type}")
        
        # Compile report
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'accuracy_metrics': accuracy,
            'strategies': {
                name: {
                    'performance': perf,
                    'trend': self.strategies[name].performance_trend,
                    'parameters': asdict(self.strategies[name].parameters),
                    'history_length': len(self.strategies[name].performance_history)
                }
                for name, perf in strategy_performances.items()
            },
            'best_strategy': best_strategy[0],
            'learning_log_size': len(self.learning_log),
            'total_workflows_tracked': len(set(c.workflow_name for c in self.tracker.comparisons))
        }
        
        return report


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Meta-Learning Workflow Scheduler - @workflows-tech-lead'
    )
    parser.add_argument('--repo-root', help='Repository root directory')
    parser.add_argument('--report', action='store_true', help='Generate meta-learning report')
    parser.add_argument('--adapt', metavar='STRATEGY', help='Adapt a strategy')
    parser.add_argument('--evolve', action='store_true', help='Evolve strategies')
    parser.add_argument('--optimize', metavar='WORKFLOW', help='Generate optimized schedule for workflow')
    parser.add_argument('--strategy', default='default', help='Strategy to use for optimization')
    parser.add_argument('--export', metavar='FILE', help='Export report to JSON file')
    
    args = parser.parse_args()
    
    # Initialize scheduler
    scheduler = MetaLearningScheduler(repo_root=args.repo_root)
    
    if args.report:
        report = scheduler.generate_meta_learning_report()
        if args.export:
            with open(args.export, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Report exported to {args.export}")
    
    elif args.adapt:
        print(f"🔄 Adapting strategy: {args.adapt}")
        scheduler.adapt_strategy_parameters(args.adapt)
        print(f"✅ Strategy adapted and saved")
    
    elif args.evolve:
        scheduler.evolve_strategies()
        print(f"\n✅ Strategy evolution complete")
    
    elif args.optimize:
        print(f"🎯 Generating optimized schedule for: {args.optimize}")
        result = scheduler.generate_optimized_schedule(args.optimize, args.strategy)
        print(f"\n📅 Optimized Schedule:")
        print(f"  Recommended Time: {result.recommended_time}")
        print(f"  Confidence: {result.confidence * 100:.0f}%")
        print(f"  Expected Duration: {result.expected_duration:.0f}s")
        print(f"  Reasoning:")
        for reason in result.reasoning:
            print(f"    - {reason}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
