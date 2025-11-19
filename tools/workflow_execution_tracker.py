#!/usr/bin/env python3
"""
Workflow Execution Time Tracker
Created by @workflows-tech-lead

Tracks actual workflow execution times and compares them with predictions
to improve the AI-powered workflow orchestrator's accuracy.

This tool:
- Records actual workflow execution times from GitHub Actions
- Compares predictions vs actual execution times
- Calculates prediction accuracy metrics
- Provides feedback to improve future predictions
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_workflow_predictor import AIWorkflowPredictor


@dataclass
class ExecutionComparison:
    """Comparison of predicted vs actual execution time."""
    workflow_name: str
    predicted_duration: float
    actual_duration: float
    prediction_error: float  # Percentage error
    timestamp: str
    success: bool


class WorkflowExecutionTracker:
    """
    Tracks and analyzes workflow execution times to improve predictions.
    
    This class integrates with the AI predictor to provide feedback
    on prediction accuracy and help improve future predictions.
    """
    
    def __init__(self, repo_root: str = None):
        """Initialize the execution tracker."""
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
        
        self.comparisons_file = self.repo_root / '.github' / 'workflow-history' / 'execution_comparisons.json'
        self.comparisons_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize predictor
        self.predictor = AIWorkflowPredictor(repo_root=str(self.repo_root))
        
        # Load comparison history
        self.comparisons: List[ExecutionComparison] = []
        self.load_comparisons()
    
    def load_comparisons(self) -> None:
        """Load execution comparisons from file."""
        if self.comparisons_file.exists():
            try:
                with open(self.comparisons_file, 'r') as f:
                    data = json.load(f)
                    for item in data.get('comparisons', []):
                        self.comparisons.append(ExecutionComparison(
                            workflow_name=item['workflow_name'],
                            predicted_duration=item['predicted_duration'],
                            actual_duration=item['actual_duration'],
                            prediction_error=item['prediction_error'],
                            timestamp=item['timestamp'],
                            success=item['success']
                        ))
            except Exception as e:
                print(f"Warning: Could not load comparisons: {e}", file=sys.stderr)
    
    def save_comparisons(self) -> None:
        """Save execution comparisons to file."""
        try:
            data = {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_comparisons': len(self.comparisons),
                'comparisons': []
            }
            
            # Keep last 500 comparisons
            recent = self.comparisons[-500:]
            for comp in recent:
                data['comparisons'].append(asdict(comp))
            
            with open(self.comparisons_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save comparisons: {e}", file=sys.stderr)
    
    def track_execution(self, workflow_name: str, start_time: datetime,
                       end_time: datetime, success: bool,
                       resource_usage: Optional[Dict] = None) -> ExecutionComparison:
        """
        Track a workflow execution and compare with prediction.
        
        Args:
            workflow_name: Name of the workflow
            start_time: When the workflow started
            end_time: When the workflow ended
            success: Whether the workflow succeeded
            resource_usage: Optional resource usage data
        
        Returns:
            ExecutionComparison object with prediction vs actual
        """
        actual_duration = (end_time - start_time).total_seconds()
        
        # Get prediction for this workflow
        prediction = self.predictor.predict_optimal_time(workflow_name)
        predicted_duration = prediction.expected_duration
        
        # Calculate prediction error
        if predicted_duration > 0:
            error = abs(actual_duration - predicted_duration) / predicted_duration * 100
        else:
            error = 100.0
        
        # Create comparison
        comparison = ExecutionComparison(
            workflow_name=workflow_name,
            predicted_duration=predicted_duration,
            actual_duration=actual_duration,
            prediction_error=error,
            timestamp=end_time.isoformat(),
            success=success
        )
        
        # Record in predictor for future learning
        self.predictor.record_execution(
            workflow_name=workflow_name,
            start_time=start_time,
            duration_seconds=actual_duration,
            success=success,
            resource_usage=resource_usage
        )
        
        # Save comparison
        self.comparisons.append(comparison)
        self.save_comparisons()
        
        return comparison
    
    def get_accuracy_metrics(self, workflow_name: Optional[str] = None) -> Dict:
        """
        Calculate prediction accuracy metrics.
        
        Args:
            workflow_name: Optional workflow to filter by
        
        Returns:
            Dictionary with accuracy metrics
        """
        relevant_comps = self.comparisons
        if workflow_name:
            relevant_comps = [c for c in self.comparisons if c.workflow_name == workflow_name]
        
        if not relevant_comps:
            return {
                'total_comparisons': 0,
                'message': 'No execution data available'
            }
        
        errors = [c.prediction_error for c in relevant_comps]
        
        # Calculate accuracy metrics
        metrics = {
            'total_comparisons': len(relevant_comps),
            'mean_error_percent': statistics.mean(errors),
            'median_error_percent': statistics.median(errors),
            'min_error_percent': min(errors),
            'max_error_percent': max(errors),
            'std_dev_percent': statistics.stdev(errors) if len(errors) > 1 else 0,
        }
        
        # Accuracy buckets
        excellent = sum(1 for e in errors if e <= 10)
        good = sum(1 for e in errors if 10 < e <= 25)
        fair = sum(1 for e in errors if 25 < e <= 50)
        poor = sum(1 for e in errors if e > 50)
        
        metrics['accuracy_distribution'] = {
            'excellent_10_percent': excellent,
            'good_25_percent': good,
            'fair_50_percent': fair,
            'poor_over_50_percent': poor
        }
        
        # Overall accuracy score (percentage of predictions within 25% error)
        within_25 = excellent + good
        metrics['overall_accuracy_score'] = (within_25 / len(relevant_comps)) * 100
        
        return metrics
    
    def generate_accuracy_report(self) -> None:
        """Generate a comprehensive accuracy report."""
        print("\n" + "="*70)
        print("📊 Workflow Execution Time Prediction Accuracy Report")
        print("   Created by @workflows-tech-lead")
        print("="*70 + "\n")
        
        # Overall metrics
        overall = self.get_accuracy_metrics()
        
        if overall.get('total_comparisons', 0) == 0:
            print("⚠️  No execution data available yet.")
            print("   Run workflows and use track_execution() to collect data.\n")
            return
        
        print(f"📈 Overall Prediction Accuracy")
        print(f"  Total Comparisons: {overall['total_comparisons']}")
        print(f"  Mean Error: {overall['mean_error_percent']:.1f}%")
        print(f"  Median Error: {overall['median_error_percent']:.1f}%")
        print(f"  Std Deviation: {overall['std_dev_percent']:.1f}%")
        print(f"  Overall Accuracy Score: {overall['overall_accuracy_score']:.1f}%")
        
        print(f"\n📊 Accuracy Distribution:")
        dist = overall['accuracy_distribution']
        total = overall['total_comparisons']
        print(f"  Excellent (≤10% error): {dist['excellent_10_percent']} ({dist['excellent_10_percent']/total*100:.0f}%)")
        print(f"  Good (10-25% error):    {dist['good_25_percent']} ({dist['good_25_percent']/total*100:.0f}%)")
        print(f"  Fair (25-50% error):    {dist['fair_50_percent']} ({dist['fair_50_percent']/total*100:.0f}%)")
        print(f"  Poor (>50% error):      {dist['poor_over_50_percent']} ({dist['poor_over_50_percent']/total*100:.0f}%)")
        
        # Per-workflow breakdown
        print(f"\n📋 Per-Workflow Accuracy:")
        print(f"{'Workflow':<30} {'Comparisons':<12} {'Mean Error':<12} {'Accuracy':<10}")
        print("-"*70)
        
        workflow_names = set(c.workflow_name for c in self.comparisons)
        workflow_metrics = []
        
        for wf_name in sorted(workflow_names):
            metrics = self.get_accuracy_metrics(wf_name)
            workflow_metrics.append((
                wf_name,
                metrics['total_comparisons'],
                metrics['mean_error_percent'],
                metrics['overall_accuracy_score']
            ))
        
        # Sort by accuracy score
        workflow_metrics.sort(key=lambda x: x[3], reverse=True)
        
        for wf_name, count, mean_error, accuracy in workflow_metrics[:20]:  # Top 20
            wf_short = wf_name[:28] + '..' if len(wf_name) > 30 else wf_name
            print(f"{wf_short:<30} {count:<12} {mean_error:>10.1f}% {accuracy:>8.0f}%")
        
        if len(workflow_metrics) > 20:
            print(f"\n  ... and {len(workflow_metrics) - 20} more workflows")
        
        # Recent predictions (last 10)
        print(f"\n🕐 Recent Predictions (Last 10):")
        print(f"{'Workflow':<25} {'Predicted':<10} {'Actual':<10} {'Error':<8} {'Status'}")
        print("-"*70)
        
        for comp in self.comparisons[-10:]:
            wf_short = comp.workflow_name[:23] + '..' if len(comp.workflow_name) > 25 else comp.workflow_name
            status = "✓" if comp.success else "✗"
            print(f"{wf_short:<25} {comp.predicted_duration:>8.0f}s {comp.actual_duration:>8.0f}s "
                  f"{comp.prediction_error:>6.1f}% {status}")
        
        print("\n" + "="*70 + "\n")
    
    def get_worst_predictions(self, limit: int = 10) -> List[ExecutionComparison]:
        """Get workflows with worst prediction accuracy."""
        return sorted(self.comparisons, key=lambda x: x.prediction_error, reverse=True)[:limit]
    
    def get_best_predictions(self, limit: int = 10) -> List[ExecutionComparison]:
        """Get workflows with best prediction accuracy."""
        return sorted(self.comparisons, key=lambda x: x.prediction_error)[:limit]
    
    def export_metrics(self, output_file: str = None) -> str:
        """
        Export accuracy metrics to JSON file.
        
        Args:
            output_file: Path to output file
        
        Returns:
            Path to output file
        """
        if not output_file:
            output_file = self.repo_root / 'workflow_prediction_accuracy.json'
        else:
            output_file = Path(output_file)
        
        overall = self.get_accuracy_metrics()
        
        # Per-workflow metrics
        workflow_names = set(c.workflow_name for c in self.comparisons)
        per_workflow = {}
        for wf_name in workflow_names:
            per_workflow[wf_name] = self.get_accuracy_metrics(wf_name)
        
        export_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'overall_metrics': overall,
            'per_workflow_metrics': per_workflow,
            'recent_comparisons': [asdict(c) for c in self.comparisons[-50:]]
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Metrics exported to: {output_file}")
        return str(output_file)


def main():
    """Main entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Workflow execution time tracker by @workflows-tech-lead'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate accuracy report'
    )
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export metrics to JSON file'
    )
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Simulate tracked executions for testing'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory'
    )
    
    args = parser.parse_args()
    
    tracker = WorkflowExecutionTracker(repo_root=args.repo_root)
    
    if args.simulate:
        print("🧪 Simulating tracked executions...")
        
        # First, create some prediction data
        tracker.predictor.simulate_execution_data(num_workflows=10, num_executions=100)
        
        # Now simulate some actual executions with varying accuracy
        workflow_names = [f"workflow-{i}" for i in range(10)]
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        
        for i in range(50):
            wf_name = workflow_names[i % len(workflow_names)]
            
            # Get prediction
            prediction = tracker.predictor.predict_optimal_time(wf_name)
            predicted = prediction.expected_duration
            
            # Simulate actual duration with some variance
            # Sometimes accurate, sometimes not
            if i % 5 == 0:
                # 20% of time: very accurate (within 5%)
                variance = predicted * 0.05
            elif i % 3 == 0:
                # 33% of time: somewhat accurate (within 20%)
                variance = predicted * 0.20
            else:
                # Rest: moderate accuracy (within 40%)
                variance = predicted * 0.40
            
            import random
            actual = predicted + random.uniform(-variance, variance)
            actual = max(30, actual)  # At least 30 seconds
            
            start_time = base_time + timedelta(hours=i)
            end_time = start_time + timedelta(seconds=actual)
            
            tracker.track_execution(
                workflow_name=wf_name,
                start_time=start_time,
                end_time=end_time,
                success=random.random() > 0.1  # 90% success rate
            )
        
        print(f"✓ Simulated 50 tracked executions\n")
    
    if args.report:
        tracker.generate_accuracy_report()
    
    if args.export:
        tracker.export_metrics(args.export)
    
    if not (args.report or args.export or args.simulate):
        # Default: show quick stats
        metrics = tracker.get_accuracy_metrics()
        if metrics.get('total_comparisons', 0) > 0:
            print(f"\n📊 Quick Stats:")
            print(f"  Total Predictions Tracked: {metrics['total_comparisons']}")
            print(f"  Mean Error: {metrics['mean_error_percent']:.1f}%")
            print(f"  Overall Accuracy: {metrics['overall_accuracy_score']:.1f}%")
            print(f"\nUse --report for detailed analysis\n")
        else:
            print("\n⚠️  No execution data available yet.")
            print("   Use --simulate to generate test data\n")


if __name__ == '__main__':
    main()
