#!/usr/bin/env python3
"""
Workflow Orchestrator API
Created by @APIs-architect

Provides REST-like API interface for the AI-powered workflow orchestrator
with real-time execution time predictions.

Features:
- Real-time prediction API
- Historical data query
- Batch prediction endpoints
- Prediction accuracy metrics
- Workflow scheduling recommendations
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import statistics

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_workflow_predictor import AIWorkflowPredictor, PredictionResult
from workflow_execution_tracker import WorkflowExecutionTracker


@dataclass
class APIResponse:
    """Standard API response format."""
    success: bool
    data: Any
    message: str
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class WorkflowOrchestratorAPI:
    """
    API layer for AI-powered workflow orchestrator.
    
    Provides programmatic access to prediction and tracking capabilities
    for integration with GitHub Actions and monitoring systems.
    """
    
    def __init__(self, repo_root: str = None):
        """Initialize the API."""
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
        self.tracker = WorkflowExecutionTracker(repo_root=str(self.repo_root))
    
    def predict_execution_time(self, workflow_name: str) -> APIResponse:
        """
        Predict optimal execution time for a single workflow.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            APIResponse with prediction data
        """
        try:
            prediction = self.predictor.predict_optimal_time(workflow_name)
            
            if not prediction:
                return APIResponse(
                    success=False,
                    data=None,
                    message=f"No prediction available for {workflow_name}",
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
            
            return APIResponse(
                success=True,
                data={
                    'workflow_name': prediction.workflow_name,
                    'recommended_schedule': prediction.recommended_time,
                    'confidence': round(prediction.confidence, 2),
                    'expected_duration_seconds': round(prediction.expected_duration, 1),
                    'predicted_success_rate': round(prediction.predicted_success_rate, 2),
                    'resource_impact': prediction.resource_impact,
                    'reasoning': prediction.reasoning
                },
                message="Prediction generated successfully",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                message=f"Error generating prediction: {str(e)}",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    def predict_batch(self, workflow_names: List[str]) -> APIResponse:
        """
        Predict optimal execution times for multiple workflows.
        
        Args:
            workflow_names: List of workflow names
            
        Returns:
            APIResponse with batch prediction data
        """
        try:
            predictions = self.predictor.predict_batch(workflow_names)
            
            results = {}
            for name, prediction in predictions.items():
                if prediction:
                    results[name] = {
                        'recommended_schedule': prediction.recommended_time,
                        'confidence': round(prediction.confidence, 2),
                        'expected_duration_seconds': round(prediction.expected_duration, 1),
                        'predicted_success_rate': round(prediction.predicted_success_rate, 2),
                        'resource_impact': prediction.resource_impact
                    }
            
            return APIResponse(
                success=True,
                data={
                    'predictions': results,
                    'total_workflows': len(workflow_names),
                    'successful_predictions': len(results)
                },
                message="Batch predictions generated successfully",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                message=f"Error generating batch predictions: {str(e)}",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    def get_execution_history(self, workflow_name: Optional[str] = None, 
                             limit: int = 100) -> APIResponse:
        """
        Retrieve execution history for workflows.
        
        Args:
            workflow_name: Optional workflow name filter
            limit: Maximum number of records to return
            
        Returns:
            APIResponse with execution history
        """
        try:
            history = self.predictor.execution_history
            
            # Filter by workflow name if specified
            if workflow_name:
                history = [e for e in history if e.workflow_name == workflow_name]
            
            # Limit results
            history = history[-limit:]
            
            # Convert to serializable format
            history_data = []
            for execution in history:
                history_data.append({
                    'workflow_name': execution.workflow_name,
                    'start_time': execution.start_time.isoformat(),
                    'duration_seconds': round(execution.duration_seconds, 1),
                    'success': execution.success,
                    'resource_usage': execution.resource_usage,
                    'day_of_week': execution.day_of_week,
                    'hour_of_day': execution.hour_of_day
                })
            
            return APIResponse(
                success=True,
                data={
                    'history': history_data,
                    'total_records': len(history_data),
                    'workflow_filter': workflow_name
                },
                message="Execution history retrieved successfully",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                message=f"Error retrieving history: {str(e)}",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    def get_accuracy_metrics(self, workflow_name: Optional[str] = None) -> APIResponse:
        """
        Get prediction accuracy metrics.
        
        Args:
            workflow_name: Optional workflow name filter
            
        Returns:
            APIResponse with accuracy metrics
        """
        try:
            accuracy = self.tracker.calculate_accuracy(workflow_name)
            
            if not accuracy:
                return APIResponse(
                    success=False,
                    data=None,
                    message="No accuracy data available",
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
            
            return APIResponse(
                success=True,
                data={
                    'workflow_name': workflow_name or 'all',
                    'mean_absolute_error': round(accuracy.get('mae', 0), 1),
                    'mean_percentage_error': round(accuracy.get('mape', 0), 1),
                    'accuracy_score': round(accuracy.get('accuracy', 0), 2),
                    'total_comparisons': accuracy.get('count', 0)
                },
                message="Accuracy metrics calculated successfully",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                message=f"Error calculating accuracy: {str(e)}",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    def record_execution(self, workflow_name: str, start_time: str,
                        duration_seconds: float, success: bool,
                        resource_usage: Dict[str, Any]) -> APIResponse:
        """
        Record a workflow execution for learning.
        
        Args:
            workflow_name: Name of the workflow
            start_time: ISO format start time
            duration_seconds: Duration in seconds
            success: Whether execution succeeded
            resource_usage: Resource usage metrics
            
        Returns:
            APIResponse confirming recording
        """
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            self.predictor.record_execution(
                workflow_name=workflow_name,
                start_time=start_dt,
                duration_seconds=duration_seconds,
                success=success,
                resource_usage=resource_usage
            )
            
            return APIResponse(
                success=True,
                data={
                    'workflow_name': workflow_name,
                    'recorded_at': datetime.now(timezone.utc).isoformat()
                },
                message="Execution recorded successfully",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                message=f"Error recording execution: {str(e)}",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    def get_workflow_insights(self, workflow_name: str) -> APIResponse:
        """
        Get comprehensive insights for a workflow.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            APIResponse with workflow insights
        """
        try:
            # Get prediction
            prediction = self.predictor.predict_optimal_time(workflow_name)
            
            # Get execution history
            history = [e for e in self.predictor.execution_history 
                      if e.workflow_name == workflow_name]
            
            if not history:
                return APIResponse(
                    success=False,
                    data=None,
                    message=f"No data available for {workflow_name}",
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
            
            # Calculate statistics
            durations = [e.duration_seconds for e in history]
            successes = [e.success for e in history]
            
            insights = {
                'workflow_name': workflow_name,
                'total_executions': len(history),
                'success_rate': round(sum(successes) / len(successes), 2),
                'average_duration': round(statistics.mean(durations), 1),
                'min_duration': round(min(durations), 1),
                'max_duration': round(max(durations), 1),
                'duration_std_dev': round(statistics.stdev(durations), 1) if len(durations) > 1 else 0,
                'most_common_hour': max(set(e.hour_of_day for e in history), 
                                       key=lambda x: sum(1 for e in history if e.hour_of_day == x)),
                'recommended_schedule': prediction.recommended_time if prediction else None,
                'prediction_confidence': round(prediction.confidence, 2) if prediction else None
            }
            
            return APIResponse(
                success=True,
                data=insights,
                message="Workflow insights generated successfully",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                message=f"Error generating insights: {str(e)}",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
    
    def health_check(self) -> APIResponse:
        """
        API health check endpoint.
        
        Returns:
            APIResponse with health status
        """
        try:
            return APIResponse(
                success=True,
                data={
                    'status': 'healthy',
                    'predictor_loaded': self.predictor is not None,
                    'tracker_loaded': self.tracker is not None,
                    'total_workflows': len(set(e.workflow_name for e in self.predictor.execution_history)),
                    'total_executions': len(self.predictor.execution_history)
                },
                message="API is healthy",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.now(timezone.utc).isoformat()
            )


def main():
    """CLI interface for the API."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Workflow Orchestrator API - @APIs-architect'
    )
    parser.add_argument('command', choices=[
        'predict', 'batch', 'history', 'accuracy', 'insights', 'health'
    ], help='API command to execute')
    parser.add_argument('--workflow', help='Workflow name')
    parser.add_argument('--workflows', nargs='+', help='List of workflow names for batch')
    parser.add_argument('--limit', type=int, default=100, help='Limit for history')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    
    args = parser.parse_args()
    
    api = WorkflowOrchestratorAPI()
    
    # Execute command
    if args.command == 'predict':
        if not args.workflow:
            print("Error: --workflow required for predict command")
            sys.exit(1)
        response = api.predict_execution_time(args.workflow)
    
    elif args.command == 'batch':
        if not args.workflows:
            print("Error: --workflows required for batch command")
            sys.exit(1)
        response = api.predict_batch(args.workflows)
    
    elif args.command == 'history':
        response = api.get_execution_history(args.workflow, args.limit)
    
    elif args.command == 'accuracy':
        response = api.get_accuracy_metrics(args.workflow)
    
    elif args.command == 'insights':
        if not args.workflow:
            print("Error: --workflow required for insights command")
            sys.exit(1)
        response = api.get_workflow_insights(args.workflow)
    
    elif args.command == 'health':
        response = api.health_check()
    
    # Output response
    if args.json:
        print(json.dumps(response.to_dict(), indent=2))
    else:
        print(f"\n{'='*70}")
        print(f"📡 Workflow Orchestrator API - @APIs-architect")
        print(f"{'='*70}\n")
        print(f"Status: {'✅ Success' if response.success else '❌ Failed'}")
        print(f"Message: {response.message}")
        print(f"Timestamp: {response.timestamp}")
        print(f"\nData:")
        print(json.dumps(response.data, indent=2))
        print()


if __name__ == '__main__':
    main()
