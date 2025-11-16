#!/usr/bin/env python3
"""
AI-Powered Workflow Execution Time Predictor
Created by @coordinate-wizard

Predicts optimal workflow execution times using machine learning based on:
- Historical execution patterns
- Resource usage data
- Workflow dependencies
- Time-of-day patterns
- API quota constraints

This extends the existing workflow-orchestrator.py with intelligent prediction.
"""

import os
import sys
import json
import random
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import statistics


@dataclass
class WorkflowExecutionData:
    """Data about a workflow execution."""
    workflow_name: str
    start_time: datetime
    duration_seconds: float
    success: bool
    resource_usage: Dict[str, Any]
    day_of_week: int
    hour_of_day: int
    

@dataclass
class PredictionResult:
    """Prediction result for optimal execution time."""
    workflow_name: str
    recommended_time: str  # cron expression
    confidence: float  # 0-1
    reasoning: List[str]
    expected_duration: float  # seconds
    predicted_success_rate: float
    resource_impact: str  # low/medium/high
    

class AIWorkflowPredictor:
    """
    ML-based predictor for optimal workflow execution times.
    
    Uses historical data to learn patterns and predict:
    - Best execution times to avoid conflicts
    - Expected resource usage
    - Success probability
    - Optimal scheduling strategies
    """
    
    def __init__(self, repo_root: str = None):
        """Initialize the predictor."""
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
        
        self.history_file = self.repo_root / '.github' / 'workflow-history' / 'executions.json'
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize history storage
        self.execution_history: List[WorkflowExecutionData] = []
        self.load_history()
        
        # Pattern learning storage
        self.success_patterns: Dict[str, List[Tuple[int, int]]] = defaultdict(list)  # (day, hour)
        self.duration_patterns: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        self.conflict_patterns: Dict[str, List[str]] = defaultdict(list)
        
        self._analyze_patterns()
    
    def load_history(self) -> None:
        """Load execution history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    for item in data.get('executions', []):
                        # Parse datetime strings
                        start_time = datetime.fromisoformat(item['start_time'].replace('Z', '+00:00'))
                        self.execution_history.append(WorkflowExecutionData(
                            workflow_name=item['workflow_name'],
                            start_time=start_time,
                            duration_seconds=item['duration_seconds'],
                            success=item['success'],
                            resource_usage=item.get('resource_usage', {}),
                            day_of_week=start_time.weekday(),
                            hour_of_day=start_time.hour
                        ))
            except Exception as e:
                print(f"Warning: Could not load history: {e}", file=sys.stderr)
    
    def save_history(self) -> None:
        """Save execution history to file."""
        try:
            data = {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'executions': []
            }
            
            # Keep last 1000 executions
            recent = self.execution_history[-1000:]
            for exec_data in recent:
                data['executions'].append({
                    'workflow_name': exec_data.workflow_name,
                    'start_time': exec_data.start_time.isoformat(),
                    'duration_seconds': exec_data.duration_seconds,
                    'success': exec_data.success,
                    'resource_usage': exec_data.resource_usage,
                    'day_of_week': exec_data.day_of_week,
                    'hour_of_day': exec_data.hour_of_day
                })
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}", file=sys.stderr)
    
    def record_execution(self, workflow_name: str, start_time: datetime, 
                        duration_seconds: float, success: bool,
                        resource_usage: Optional[Dict[str, Any]] = None) -> None:
        """Record a workflow execution for learning."""
        exec_data = WorkflowExecutionData(
            workflow_name=workflow_name,
            start_time=start_time,
            duration_seconds=duration_seconds,
            success=success,
            resource_usage=resource_usage or {},
            day_of_week=start_time.weekday(),
            hour_of_day=start_time.hour
        )
        self.execution_history.append(exec_data)
        self.save_history()
        self._analyze_patterns()
    
    def _analyze_patterns(self) -> None:
        """Analyze historical data to identify patterns."""
        # Clear existing patterns
        self.success_patterns.clear()
        self.duration_patterns.clear()
        self.conflict_patterns.clear()
        
        # Group by workflow
        workflow_data = defaultdict(list)
        for exec_data in self.execution_history:
            workflow_data[exec_data.workflow_name].append(exec_data)
        
        # Analyze each workflow
        for workflow_name, executions in workflow_data.items():
            # Success patterns: when does this workflow succeed?
            for exec_data in executions:
                if exec_data.success:
                    self.success_patterns[workflow_name].append(
                        (exec_data.day_of_week, exec_data.hour_of_day)
                    )
            
            # Duration patterns: how long does it take at different times?
            for exec_data in executions:
                time_key = f"{exec_data.day_of_week}_{exec_data.hour_of_day}"
                self.duration_patterns[workflow_name][time_key].append(
                    exec_data.duration_seconds
                )
        
        # Detect conflicts: workflows running at same time
        time_buckets = defaultdict(list)
        for exec_data in self.execution_history:
            # Bucket by hour
            bucket_key = exec_data.start_time.replace(minute=0, second=0, microsecond=0)
            time_buckets[bucket_key].append(exec_data.workflow_name)
        
        # Find frequent co-occurrences
        for workflows in time_buckets.values():
            if len(workflows) > 1:
                for wf in workflows:
                    others = [w for w in workflows if w != wf]
                    self.conflict_patterns[wf].extend(others)
    
    def predict_optimal_time(self, workflow_name: str, 
                           current_schedule: Optional[str] = None) -> PredictionResult:
        """
        Predict the optimal execution time for a workflow.
        
        Args:
            workflow_name: Name of the workflow
            current_schedule: Current cron schedule (optional)
        
        Returns:
            PredictionResult with recommendations
        """
        reasoning = []
        
        # Get historical data for this workflow
        workflow_executions = [
            e for e in self.execution_history 
            if e.workflow_name == workflow_name
        ]
        
        if not workflow_executions:
            # No historical data - use conservative defaults
            return self._default_prediction(workflow_name, reasoning)
        
        # Analyze success rates by time
        success_by_hour = defaultdict(lambda: {'success': 0, 'total': 0})
        for exec_data in workflow_executions:
            hour = exec_data.hour_of_day
            success_by_hour[hour]['total'] += 1
            if exec_data.success:
                success_by_hour[hour]['success'] += 1
        
        # Find hours with highest success rate
        best_hours = []
        for hour, stats in success_by_hour.items():
            if stats['total'] >= 3:  # Need at least 3 samples
                success_rate = stats['success'] / stats['total']
                if success_rate >= 0.8:  # 80% success threshold
                    best_hours.append((hour, success_rate))
        
        if best_hours:
            best_hours.sort(key=lambda x: x[1], reverse=True)
            recommended_hour = best_hours[0][0]
            reasoning.append(f"Hour {recommended_hour} has {best_hours[0][1]*100:.0f}% success rate")
        else:
            # Fall back to least busy hour
            recommended_hour = self._find_least_busy_hour()
            reasoning.append(f"Selected hour {recommended_hour} (least resource contention)")
        
        # Calculate average duration
        durations = [e.duration_seconds for e in workflow_executions]
        avg_duration = statistics.mean(durations) if durations else 300
        
        # Calculate overall success rate
        successes = sum(1 for e in workflow_executions if e.success)
        success_rate = successes / len(workflow_executions)
        
        # Check for conflicts
        conflicts = set(self.conflict_patterns.get(workflow_name, []))
        if conflicts:
            reasoning.append(f"Often conflicts with: {', '.join(list(conflicts)[:3])}")
        
        # Determine resource impact
        if avg_duration > 600:  # 10 minutes
            resource_impact = "high"
            reasoning.append("Long-running workflow (>10 min)")
        elif avg_duration > 180:  # 3 minutes
            resource_impact = "medium"
        else:
            resource_impact = "low"
        
        # Generate cron expression
        # Prefer off-peak hours (0-6, 20-23 UTC)
        if recommended_hour < 6 or recommended_hour >= 20:
            reasoning.append("Scheduled during off-peak hours")
        
        cron_expr = f"0 {recommended_hour} * * *"
        
        # Calculate confidence based on data points
        confidence = min(0.95, 0.5 + (len(workflow_executions) / 100))
        
        return PredictionResult(
            workflow_name=workflow_name,
            recommended_time=cron_expr,
            confidence=confidence,
            reasoning=reasoning,
            expected_duration=avg_duration,
            predicted_success_rate=success_rate,
            resource_impact=resource_impact
        )
    
    def _default_prediction(self, workflow_name: str, reasoning: List[str]) -> PredictionResult:
        """Generate default prediction when no historical data exists."""
        reasoning.append("No historical data available")
        reasoning.append("Using conservative default schedule")
        
        # Default to daily at 3 AM UTC (off-peak)
        return PredictionResult(
            workflow_name=workflow_name,
            recommended_time="0 3 * * *",
            confidence=0.3,
            reasoning=reasoning,
            expected_duration=300,  # 5 minutes default
            predicted_success_rate=0.8,  # Conservative estimate
            resource_impact="medium"
        )
    
    def _find_least_busy_hour(self) -> int:
        """Find the hour with least workflow activity."""
        hour_counts = defaultdict(int)
        for exec_data in self.execution_history:
            hour_counts[exec_data.hour_of_day] += 1
        
        if not hour_counts:
            return 3  # Default to 3 AM UTC
        
        # Find hour with minimum activity
        min_hour = min(hour_counts.items(), key=lambda x: x[1])[0]
        return min_hour
    
    def predict_batch(self, workflow_names: List[str]) -> Dict[str, PredictionResult]:
        """Predict optimal times for multiple workflows."""
        predictions = {}
        used_hours = set()
        
        for workflow_name in workflow_names:
            prediction = self.predict_optimal_time(workflow_name)
            
            # Try to avoid scheduling multiple workflows at same hour
            hour = int(prediction.recommended_time.split()[1])
            if hour in used_hours:
                # Shift by 1-3 hours
                new_hour = (hour + 2) % 24
                prediction.recommended_time = f"0 {new_hour} * * *"
                prediction.reasoning.append(f"Shifted from hour {hour} to avoid conflicts")
            
            used_hours.add(hour)
            predictions[workflow_name] = prediction
        
        return predictions
    
    def generate_recommendations_report(self) -> Dict[str, Any]:
        """Generate a comprehensive recommendations report."""
        # Get all unique workflow names from history
        workflow_names = list(set(e.workflow_name for e in self.execution_history))
        
        if not workflow_names:
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': 'No historical data available yet',
                'recommendations': []
            }
        
        predictions = self.predict_batch(workflow_names)
        
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_workflows_analyzed': len(workflow_names),
            'total_executions_recorded': len(self.execution_history),
            'recommendations': []
        }
        
        for workflow_name, prediction in predictions.items():
            report['recommendations'].append({
                'workflow': workflow_name,
                'recommended_schedule': prediction.recommended_time,
                'confidence': f"{prediction.confidence * 100:.0f}%",
                'expected_duration': f"{prediction.expected_duration:.0f}s",
                'predicted_success_rate': f"{prediction.predicted_success_rate * 100:.0f}%",
                'resource_impact': prediction.resource_impact,
                'reasoning': prediction.reasoning
            })
        
        # Sort by confidence (highest first)
        report['recommendations'].sort(
            key=lambda x: float(x['confidence'].rstrip('%')), 
            reverse=True
        )
        
        return report
    
    def simulate_execution_data(self, num_workflows: int = 10, 
                               num_executions: int = 100) -> None:
        """
        Simulate execution data for testing and demonstration.
        
        Args:
            num_workflows: Number of different workflows to simulate
            num_executions: Total number of executions to simulate
        """
        workflow_names = [f"workflow-{i}" for i in range(num_workflows)]
        
        # Define some workflow characteristics
        workflow_profiles = {}
        for wf in workflow_names:
            workflow_profiles[wf] = {
                'preferred_hours': [2, 3, 8, 14, 20],  # Hours where it succeeds more
                'avg_duration': random.uniform(60, 600),  # 1-10 minutes
                'base_success_rate': random.uniform(0.7, 0.95)
            }
        
        # Generate simulated executions
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        for i in range(num_executions):
            # Random workflow
            workflow_name = random.choice(workflow_names)
            profile = workflow_profiles[workflow_name]
            
            # Random time in past 30 days
            days_ago = random.uniform(0, 30)
            exec_time = start_date + timedelta(days=days_ago)
            
            # Duration varies around average (normal distribution simulation)
            duration = max(30, profile['avg_duration'] + random.gauss(0, 60))
            
            # Success rate depends on hour
            hour = exec_time.hour
            if hour in profile['preferred_hours']:
                success_prob = profile['base_success_rate'] + 0.1
            else:
                success_prob = profile['base_success_rate'] - 0.1
            success = random.random() < success_prob
            
            # Resource usage (simulated)
            resource_usage = {
                'cpu_percent': random.uniform(10, 90),
                'memory_mb': random.uniform(100, 1000),
                'api_calls': int(random.uniform(5, 50))
            }
            
            self.record_execution(
                workflow_name=workflow_name,
                start_time=exec_time,
                duration_seconds=duration,
                success=success,
                resource_usage=resource_usage
            )
        
        print(f"✓ Simulated {num_executions} executions for {num_workflows} workflows")


def main():
    """Main entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AI-powered workflow execution time predictor'
    )
    parser.add_argument(
        '--workflow',
        help='Get prediction for a specific workflow'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate full recommendations report'
    )
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Simulate execution data for testing'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory'
    )
    
    args = parser.parse_args()
    
    predictor = AIWorkflowPredictor(repo_root=args.repo_root)
    
    if args.simulate:
        print("🧪 Simulating execution data...")
        predictor.simulate_execution_data(num_workflows=15, num_executions=200)
        print()
    
    if args.workflow:
        print(f"\n🔮 Prediction for workflow: {args.workflow}")
        print("="*70)
        prediction = predictor.predict_optimal_time(args.workflow)
        print(f"\nRecommended Schedule: {prediction.recommended_time}")
        print(f"Confidence: {prediction.confidence*100:.0f}%")
        print(f"Expected Duration: {prediction.expected_duration:.0f}s")
        print(f"Predicted Success Rate: {prediction.predicted_success_rate*100:.0f}%")
        print(f"Resource Impact: {prediction.resource_impact}")
        print(f"\nReasoning:")
        for reason in prediction.reasoning:
            print(f"  • {reason}")
        print()
    
    if args.report:
        print("\n📊 AI-Powered Workflow Recommendations")
        print("="*70)
        report = predictor.generate_recommendations_report()
        
        print(f"\nAnalysis Date: {report['timestamp']}")
        print(f"Workflows Analyzed: {report.get('total_workflows_analyzed', 0)}")
        print(f"Executions Recorded: {report.get('total_executions_recorded', 0)}")
        
        if 'recommendations' in report and report['recommendations']:
            print(f"\n{'Workflow':<25} {'Schedule':<15} {'Confidence':<12} {'Impact':<10}")
            print("-"*70)
            for rec in report['recommendations']:
                print(f"{rec['workflow']:<25} {rec['recommended_schedule']:<15} "
                      f"{rec['confidence']:<12} {rec['resource_impact']:<10}")
            
            # Show detailed reasoning for top 3
            print("\n📋 Top Recommendations (detailed):")
            for rec in report['recommendations'][:3]:
                print(f"\n{rec['workflow']}:")
                print(f"  Schedule: {rec['recommended_schedule']}")
                print(f"  Confidence: {rec['confidence']}")
                print(f"  Expected Duration: {rec['expected_duration']}")
                print(f"  Success Rate: {rec['predicted_success_rate']}")
                print(f"  Reasoning:")
                for reason in rec['reasoning']:
                    print(f"    • {reason}")
        else:
            print(f"\n{report.get('message', 'No recommendations available')}")
        
        print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
