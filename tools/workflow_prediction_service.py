#!/usr/bin/env python3
"""
Real-Time Workflow Prediction Service
Created by @create-botter

Provides a simple API for getting workflow execution predictions
based on real historical data. Can be used for:
- Pre-workflow execution planning
- Resource allocation decisions
- Scheduling optimization
- Real-time dashboards
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
import argparse

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_workflow_predictor import AIWorkflowPredictor


class WorkflowPredictionService:
    """
    Real-time prediction service for workflow execution times.
    
    Provides instant predictions based on current historical data.
    """
    
    def __init__(self, repo_root: str = None):
        """Initialize the prediction service."""
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
        
        self.predictor = AIWorkflowPredictor(repo_root=str(self.repo_root))
    
    def get_prediction(self, workflow_name: str) -> Dict:
        """
        Get prediction for a specific workflow.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Dictionary containing prediction details
        """
        try:
            prediction = self.predictor.predict_optimal_time(workflow_name)
            
            return {
                'success': True,
                'workflow': workflow_name,
                'prediction': {
                    'recommended_time': prediction.recommended_time,
                    'confidence': round(prediction.confidence, 3),
                    'expected_duration_seconds': round(prediction.expected_duration, 1),
                    'predicted_success_rate': round(prediction.predicted_success_rate, 3),
                    'resource_impact': prediction.resource_impact,
                    'reasoning': prediction.reasoning
                },
                'metadata': {
                    'prediction_timestamp': datetime.now(timezone.utc).isoformat(),
                    'historical_executions': len(self.predictor.execution_history)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'workflow': workflow_name,
                'error': str(e),
                'metadata': {
                    'prediction_timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
    
    def get_all_predictions(self) -> Dict:
        """
        Get predictions for all known workflows.
        
        Returns:
            Dictionary containing all predictions
        """
        workflows_dir = self.repo_root / '.github' / 'workflows'
        
        if not workflows_dir.exists():
            return {
                'success': False,
                'error': 'Workflows directory not found',
                'predictions': []
            }
        
        workflow_names = [f.stem for f in workflows_dir.glob('*.yml')]
        predictions_dict = self.predictor.predict_batch(workflow_names)
        
        predictions = []
        for name, pred in predictions_dict.items():
            if pred:
                predictions.append({
                    'workflow': name,
                    'recommended_time': pred.recommended_time,
                    'confidence': round(pred.confidence, 3),
                    'expected_duration_seconds': round(pred.expected_duration, 1),
                    'predicted_success_rate': round(pred.predicted_success_rate, 3),
                    'resource_impact': pred.resource_impact
                })
        
        # Sort by confidence (highest first)
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'success': True,
            'total_workflows': len(predictions),
            'predictions': predictions,
            'metadata': {
                'prediction_timestamp': datetime.now(timezone.utc).isoformat(),
                'historical_executions': len(self.predictor.execution_history)
            }
        }
    
    def get_system_status(self) -> Dict:
        """
        Get current system status and statistics.
        
        Returns:
            Dictionary containing system status
        """
        history = self.predictor.execution_history
        
        if not history:
            return {
                'status': 'no_data',
                'message': 'No execution history available. Run workflows to collect data.',
                'statistics': {
                    'total_executions': 0,
                    'workflows_tracked': 0
                }
            }
        
        # Calculate statistics
        workflows_tracked = len(set(exec.workflow_name for exec in history))
        total_executions = len(history)
        success_rate = sum(1 for exec in history if exec.success) / total_executions
        avg_duration = sum(exec.duration_seconds for exec in history) / total_executions
        
        # Get date range
        start_date = min(exec.start_time for exec in history)
        end_date = max(exec.start_time for exec in history)
        
        return {
            'status': 'active',
            'message': 'System is learning from execution data',
            'statistics': {
                'total_executions': total_executions,
                'workflows_tracked': workflows_tracked,
                'success_rate': round(success_rate, 3),
                'average_duration_seconds': round(avg_duration, 1),
                'data_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': (end_date - start_date).days
                }
            },
            'metadata': {
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }
    
    def get_workflow_insights(self, workflow_name: str) -> Dict:
        """
        Get detailed insights for a specific workflow.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Dictionary containing workflow insights
        """
        workflow_execs = [
            exec for exec in self.predictor.execution_history
            if exec.workflow_name == workflow_name
        ]
        
        if not workflow_execs:
            return {
                'success': False,
                'workflow': workflow_name,
                'message': 'No execution history for this workflow'
            }
        
        # Calculate statistics
        total = len(workflow_execs)
        successes = sum(1 for exec in workflow_execs if exec.success)
        success_rate = successes / total
        
        durations = [exec.duration_seconds for exec in workflow_execs]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        # Time patterns
        hour_distribution = {}
        for exec in workflow_execs:
            hour = exec.hour_of_day
            if hour not in hour_distribution:
                hour_distribution[hour] = {'count': 0, 'successes': 0}
            hour_distribution[hour]['count'] += 1
            if exec.success:
                hour_distribution[hour]['successes'] += 1
        
        return {
            'success': True,
            'workflow': workflow_name,
            'statistics': {
                'total_executions': total,
                'success_rate': round(success_rate, 3),
                'duration': {
                    'average_seconds': round(avg_duration, 1),
                    'min_seconds': round(min_duration, 1),
                    'max_seconds': round(max_duration, 1)
                }
            },
            'patterns': {
                'hour_distribution': hour_distribution
            },
            'metadata': {
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Real-time workflow prediction service - @create-botter'
    )
    parser.add_argument(
        '--workflow',
        help='Get prediction for specific workflow'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Get predictions for all workflows'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Get system status and statistics'
    )
    parser.add_argument(
        '--insights',
        metavar='WORKFLOW',
        help='Get detailed insights for a workflow'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON (default is human-readable)'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory'
    )
    
    args = parser.parse_args()
    
    # Create service
    service = WorkflowPredictionService(repo_root=args.repo_root)
    
    # Handle different commands
    if args.status:
        result = service.get_system_status()
    elif args.workflow:
        result = service.get_prediction(args.workflow)
    elif args.insights:
        result = service.get_workflow_insights(args.insights)
    elif args.all:
        result = service.get_all_predictions()
    else:
        parser.print_help()
        return
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print("\n" + "="*70)
        print("🔮 Workflow Prediction Service - @create-botter")
        print("="*70 + "\n")
        
        if args.status:
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            print(f"\nStatistics:")
            for key, value in result['statistics'].items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"  {key}: {value}")
        
        elif args.workflow or args.insights:
            if result['success']:
                if 'prediction' in result:
                    pred = result['prediction']
                    print(f"Workflow: {result['workflow']}")
                    print(f"Recommended Time: {pred['recommended_time']}")
                    print(f"Confidence: {pred['confidence']*100:.1f}%")
                    print(f"Expected Duration: {pred['expected_duration_seconds']:.1f}s")
                    print(f"Success Rate: {pred['predicted_success_rate']*100:.1f}%")
                    print(f"Resource Impact: {pred['resource_impact']}")
                    print(f"\nReasoning:")
                    for reason in pred['reasoning']:
                        print(f"  • {reason}")
                else:
                    print(f"Workflow: {result['workflow']}")
                    stats = result['statistics']
                    print(f"\nStatistics:")
                    print(f"  Total Executions: {stats['total_executions']}")
                    print(f"  Success Rate: {stats['success_rate']*100:.1f}%")
                    print(f"  Avg Duration: {stats['duration']['average_seconds']:.1f}s")
                    print(f"  Min Duration: {stats['duration']['min_seconds']:.1f}s")
                    print(f"  Max Duration: {stats['duration']['max_seconds']:.1f}s")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif args.all:
            if result['success']:
                print(f"Total Workflows: {result['total_workflows']}")
                print(f"Historical Executions: {result['metadata']['historical_executions']}")
                print(f"\nTop Predictions (by confidence):\n")
                print(f"{'Workflow':<30} {'Confidence':<12} {'Duration':<12} {'Impact':<10}")
                print("-"*70)
                for pred in result['predictions'][:10]:
                    print(f"{pred['workflow']:<30} "
                          f"{pred['confidence']*100:>10.0f}% "
                          f"{pred['expected_duration_seconds']:>10.1f}s "
                          f"{pred['resource_impact']:<10}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
