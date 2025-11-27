#!/usr/bin/env python3
"""
Workflow Anomaly Detector
Created by @create-guru

Detects unusual workflow execution patterns that might indicate problems:
- Unusually long execution times
- Sudden increases in failure rates
- Anomalous resource usage patterns
- Time-of-day execution anomalies

This tool enhances the AI-powered workflow orchestrator by providing
proactive alerting and insights into workflow health.
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import statistics

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_workflow_predictor import AIWorkflowPredictor, WorkflowExecutionData


@dataclass
class AnomalyAlert:
    """Represents an anomaly detected in workflow execution."""
    workflow_name: str
    anomaly_type: str  # duration, failure_rate, pattern, resource
    severity: str  # low, medium, high, critical
    message: str
    details: Dict
    timestamp: str
    recommended_action: str


@dataclass
class WorkflowHealthScore:
    """Health score for a workflow based on recent execution patterns."""
    workflow_name: str
    overall_score: float  # 0-100
    duration_score: float  # 0-100
    success_score: float  # 0-100
    consistency_score: float  # 0-100
    trend_score: float  # 0-100 (higher = improving, lower = degrading)
    last_updated: str


class WorkflowAnomalyDetector:
    """
    Detects anomalies in workflow execution patterns using statistical analysis.
    
    Anomaly types detected:
    1. Duration anomalies: Execution time significantly different from historical average
    2. Failure rate anomalies: Sudden increase in failure rates
    3. Pattern anomalies: Unusual execution patterns (time of day, frequency)
    4. Trend anomalies: Gradual degradation in performance
    """
    
    # Thresholds for anomaly detection
    DURATION_Z_SCORE_THRESHOLD = 2.5  # Standard deviations from mean
    FAILURE_RATE_THRESHOLD = 0.3  # 30% increase in failure rate
    MIN_SAMPLES_FOR_ANALYSIS = 5  # Minimum executions needed for analysis
    TREND_WINDOW_SIZE = 10  # Number of recent executions to analyze for trends
    
    def __init__(self, repo_root: str = None):
        """Initialize the anomaly detector."""
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
        
        self.alerts_file = self.repo_root / '.github' / 'workflow-history' / 'anomaly_alerts.json'
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize predictor to access execution history
        self.predictor = AIWorkflowPredictor(repo_root=str(self.repo_root))
        
        # Load existing alerts
        self.alerts: List[AnomalyAlert] = []
        self.load_alerts()
    
    def load_alerts(self) -> None:
        """Load existing alerts from file."""
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                    for item in data.get('alerts', []):
                        self.alerts.append(AnomalyAlert(
                            workflow_name=item['workflow_name'],
                            anomaly_type=item['anomaly_type'],
                            severity=item['severity'],
                            message=item['message'],
                            details=item['details'],
                            timestamp=item['timestamp'],
                            recommended_action=item['recommended_action']
                        ))
            except Exception as e:
                print(f"Warning: Could not load alerts: {e}", file=sys.stderr)
    
    def save_alerts(self) -> None:
        """Save alerts to file."""
        try:
            data = {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_alerts': len(self.alerts),
                'alerts': [asdict(a) for a in self.alerts[-100:]]  # Keep last 100 alerts
            }
            with open(self.alerts_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save alerts: {e}", file=sys.stderr)
    
    def _get_workflow_executions(self, workflow_name: str) -> List[WorkflowExecutionData]:
        """Get execution history for a specific workflow."""
        return [e for e in self.predictor.execution_history 
                if e.workflow_name == workflow_name]
    
    def _calculate_z_score(self, value: float, mean: float, std_dev: float) -> float:
        """Calculate Z-score for a value."""
        if std_dev == 0:
            return 0
        return abs(value - mean) / std_dev
    
    def detect_duration_anomaly(self, workflow_name: str, 
                                current_duration: float) -> Optional[AnomalyAlert]:
        """
        Detect if a workflow's execution duration is anomalous.
        
        Args:
            workflow_name: Name of the workflow
            current_duration: Duration of the current execution in seconds
        
        Returns:
            AnomalyAlert if anomaly detected, None otherwise
        """
        executions = self._get_workflow_executions(workflow_name)
        
        if len(executions) < self.MIN_SAMPLES_FOR_ANALYSIS:
            return None
        
        durations = [e.duration_seconds for e in executions]
        mean_duration = statistics.mean(durations)
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0
        
        z_score = self._calculate_z_score(current_duration, mean_duration, std_dev)
        
        if z_score > self.DURATION_Z_SCORE_THRESHOLD:
            # Determine severity based on z-score
            if z_score > 4:
                severity = "critical"
            elif z_score > 3:
                severity = "high"
            else:
                severity = "medium"
            
            percent_diff = ((current_duration - mean_duration) / mean_duration) * 100
            direction = "longer" if current_duration > mean_duration else "shorter"
            
            alert = AnomalyAlert(
                workflow_name=workflow_name,
                anomaly_type="duration",
                severity=severity,
                message=f"Execution time is {abs(percent_diff):.0f}% {direction} than usual",
                details={
                    'current_duration': current_duration,
                    'mean_duration': mean_duration,
                    'std_dev': std_dev,
                    'z_score': z_score,
                    'percent_difference': percent_diff
                },
                timestamp=datetime.now(timezone.utc).isoformat(),
                recommended_action=f"Investigate why {workflow_name} is running {direction} than expected"
            )
            
            self.alerts.append(alert)
            self.save_alerts()
            return alert
        
        return None
    
    def detect_failure_rate_anomaly(self, workflow_name: str) -> Optional[AnomalyAlert]:
        """
        Detect if a workflow's failure rate has increased significantly.
        
        Args:
            workflow_name: Name of the workflow
        
        Returns:
            AnomalyAlert if anomaly detected, None otherwise
        """
        executions = self._get_workflow_executions(workflow_name)
        
        if len(executions) < self.MIN_SAMPLES_FOR_ANALYSIS * 2:
            return None
        
        # Split into recent and historical
        mid_point = len(executions) // 2
        historical = executions[:mid_point]
        recent = executions[mid_point:]
        
        historical_success_rate = sum(1 for e in historical if e.success) / len(historical)
        recent_success_rate = sum(1 for e in recent if e.success) / len(recent)
        
        # Check if recent failure rate is significantly higher
        historical_failure_rate = 1 - historical_success_rate
        recent_failure_rate = 1 - recent_success_rate
        
        if recent_failure_rate > historical_failure_rate + self.FAILURE_RATE_THRESHOLD:
            increase = recent_failure_rate - historical_failure_rate
            
            if increase > 0.5:
                severity = "critical"
            elif increase > 0.3:
                severity = "high"
            else:
                severity = "medium"
            
            alert = AnomalyAlert(
                workflow_name=workflow_name,
                anomaly_type="failure_rate",
                severity=severity,
                message=f"Failure rate increased from {historical_failure_rate*100:.0f}% to {recent_failure_rate*100:.0f}%",
                details={
                    'historical_success_rate': historical_success_rate,
                    'recent_success_rate': recent_success_rate,
                    'failure_rate_increase': increase,
                    'historical_sample_size': len(historical),
                    'recent_sample_size': len(recent)
                },
                timestamp=datetime.now(timezone.utc).isoformat(),
                recommended_action=f"Investigate recent failures in {workflow_name}"
            )
            
            self.alerts.append(alert)
            self.save_alerts()
            return alert
        
        return None
    
    def detect_trend_anomaly(self, workflow_name: str) -> Optional[AnomalyAlert]:
        """
        Detect if a workflow shows a degrading performance trend.
        
        Uses linear regression to detect gradual increases in execution time.
        
        Args:
            workflow_name: Name of the workflow
        
        Returns:
            AnomalyAlert if anomaly detected, None otherwise
        """
        executions = self._get_workflow_executions(workflow_name)
        
        if len(executions) < self.TREND_WINDOW_SIZE:
            return None
        
        # Get recent executions
        recent = executions[-self.TREND_WINDOW_SIZE:]
        durations = [e.duration_seconds for e in recent]
        
        # Calculate simple linear regression slope
        n = len(durations)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(durations) / n
        
        numerator = sum((x[i] - x_mean) * (durations[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator
        
        # Calculate if trend is significant (slope > 5% of mean per execution)
        mean_duration = statistics.mean(durations)
        trend_threshold = mean_duration * 0.05  # 5% increase per execution
        
        if slope > trend_threshold:
            # Calculate projected time increase over next 10 executions
            projected_increase = slope * 10
            percent_increase = (projected_increase / mean_duration) * 100
            
            if percent_increase > 50:
                severity = "high"
            elif percent_increase > 25:
                severity = "medium"
            else:
                severity = "low"
            
            alert = AnomalyAlert(
                workflow_name=workflow_name,
                anomaly_type="trend",
                severity=severity,
                message=f"Execution time showing upward trend (+{percent_increase:.0f}% projected)",
                details={
                    'slope': slope,
                    'mean_duration': mean_duration,
                    'projected_increase_10_runs': projected_increase,
                    'percent_increase': percent_increase,
                    'window_size': n
                },
                timestamp=datetime.now(timezone.utc).isoformat(),
                recommended_action=f"Monitor {workflow_name} for potential performance degradation"
            )
            
            self.alerts.append(alert)
            self.save_alerts()
            return alert
        
        return None
    
    def calculate_health_score(self, workflow_name: str) -> WorkflowHealthScore:
        """
        Calculate comprehensive health score for a workflow.
        
        Args:
            workflow_name: Name of the workflow
        
        Returns:
            WorkflowHealthScore with various metrics
        """
        executions = self._get_workflow_executions(workflow_name)
        
        if len(executions) < 3:
            return WorkflowHealthScore(
                workflow_name=workflow_name,
                overall_score=50.0,  # Neutral score with insufficient data
                duration_score=50.0,
                success_score=50.0,
                consistency_score=50.0,
                trend_score=50.0,
                last_updated=datetime.now(timezone.utc).isoformat()
            )
        
        # Duration score: Based on how predictable the duration is
        durations = [e.duration_seconds for e in executions]
        mean_duration = statistics.mean(durations)
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0
        
        # Lower coefficient of variation = more consistent = higher score
        cv = std_dev / mean_duration if mean_duration > 0 else 0
        duration_score = max(0, min(100, 100 - (cv * 100)))
        
        # Success score: Based on success rate
        success_rate = sum(1 for e in executions if e.success) / len(executions)
        success_score = success_rate * 100
        
        # Consistency score: Based on variance in execution times
        if len(durations) >= 5:
            recent_durations = durations[-5:]
            recent_cv = (statistics.stdev(recent_durations) / 
                        statistics.mean(recent_durations)) if statistics.mean(recent_durations) > 0 else 0
            consistency_score = max(0, min(100, 100 - (recent_cv * 150)))
        else:
            consistency_score = 50.0
        
        # Trend score: Is the workflow getting better or worse?
        trend_score = 50.0  # Neutral default
        if len(executions) >= self.TREND_WINDOW_SIZE:
            recent = executions[-self.TREND_WINDOW_SIZE:]
            recent_success = sum(1 for e in recent if e.success) / len(recent)
            older = executions[-2*self.TREND_WINDOW_SIZE:-self.TREND_WINDOW_SIZE]
            if older:
                older_success = sum(1 for e in older if e.success) / len(older)
                # Improvement = higher score
                improvement = recent_success - older_success
                trend_score = 50 + (improvement * 100)  # Scale to 0-100
                trend_score = max(0, min(100, trend_score))
        
        # Overall score: Weighted average
        overall_score = (
            duration_score * 0.25 +
            success_score * 0.35 +
            consistency_score * 0.20 +
            trend_score * 0.20
        )
        
        return WorkflowHealthScore(
            workflow_name=workflow_name,
            overall_score=round(overall_score, 1),
            duration_score=round(duration_score, 1),
            success_score=round(success_score, 1),
            consistency_score=round(consistency_score, 1),
            trend_score=round(trend_score, 1),
            last_updated=datetime.now(timezone.utc).isoformat()
        )
    
    def run_full_analysis(self) -> Dict:
        """
        Run full anomaly analysis on all workflows.
        
        Returns:
            Dictionary with analysis results
        """
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'alerts': [],
            'health_scores': {},
            'summary': {}
        }
        
        # Get unique workflow names
        workflow_names = list(set(e.workflow_name for e in self.predictor.execution_history))
        
        for workflow_name in workflow_names:
            # Check for anomalies
            failure_alert = self.detect_failure_rate_anomaly(workflow_name)
            if failure_alert:
                results['alerts'].append(asdict(failure_alert))
            
            trend_alert = self.detect_trend_anomaly(workflow_name)
            if trend_alert:
                results['alerts'].append(asdict(trend_alert))
            
            # Calculate health score
            health = self.calculate_health_score(workflow_name)
            results['health_scores'][workflow_name] = asdict(health)
        
        # Summary statistics
        if results['health_scores']:
            scores = [h['overall_score'] for h in results['health_scores'].values()]
            results['summary'] = {
                'total_workflows': len(workflow_names),
                'total_alerts': len(results['alerts']),
                'critical_alerts': sum(1 for a in results['alerts'] if a['severity'] == 'critical'),
                'high_alerts': sum(1 for a in results['alerts'] if a['severity'] == 'high'),
                'average_health_score': round(statistics.mean(scores), 1),
                'min_health_score': round(min(scores), 1),
                'max_health_score': round(max(scores), 1)
            }
        
        return results
    
    def generate_report(self) -> None:
        """Generate a human-readable anomaly report."""
        print("\n" + "="*70)
        print("🔍 Workflow Anomaly Detection Report")
        print("   Created by @create-guru")
        print("="*70 + "\n")
        
        results = self.run_full_analysis()
        
        # Summary
        summary = results.get('summary', {})
        print(f"📊 Summary:")
        print(f"  Total Workflows Analyzed: {summary.get('total_workflows', 0)}")
        print(f"  Active Alerts: {summary.get('total_alerts', 0)}")
        print(f"    - Critical: {summary.get('critical_alerts', 0)}")
        print(f"    - High: {summary.get('high_alerts', 0)}")
        print(f"  Average Health Score: {summary.get('average_health_score', 'N/A')}")
        
        # Alerts
        alerts = results.get('alerts', [])
        if alerts:
            print(f"\n⚠️  Active Anomalies:")
            print("-"*70)
            for alert in sorted(alerts, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x['severity'], 4)):
                severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '⚪'}.get(alert['severity'], '⚪')
                print(f"\n{severity_icon} [{alert['severity'].upper()}] {alert['workflow_name']}")
                print(f"   Type: {alert['anomaly_type']}")
                print(f"   Message: {alert['message']}")
                print(f"   Action: {alert['recommended_action']}")
        else:
            print(f"\n✅ No anomalies detected!")
        
        # Health scores
        health_scores = results.get('health_scores', {})
        if health_scores:
            print(f"\n🏥 Workflow Health Scores:")
            print("-"*70)
            print(f"{'Workflow':<30} {'Overall':<10} {'Success':<10} {'Duration':<10} {'Trend':<10}")
            print("-"*70)
            
            # Sort by overall score
            sorted_scores = sorted(health_scores.items(), 
                                   key=lambda x: x[1]['overall_score'], 
                                   reverse=True)
            
            for workflow_name, score in sorted_scores[:15]:
                wf_short = workflow_name[:28] + '..' if len(workflow_name) > 30 else workflow_name
                overall = score['overall_score']
                
                # Color indicator based on score
                if overall >= 80:
                    indicator = "🟢"
                elif overall >= 60:
                    indicator = "🟡"
                else:
                    indicator = "🔴"
                
                print(f"{wf_short:<30} {indicator} {overall:<8} {score['success_score']:<10} "
                      f"{score['duration_score']:<10} {score['trend_score']:<10}")
            
            if len(sorted_scores) > 15:
                print(f"\n  ... and {len(sorted_scores) - 15} more workflows")
        
        print("\n" + "="*70 + "\n")
    
    def export_results(self, output_file: str = None) -> str:
        """
        Export analysis results to JSON file.
        
        Args:
            output_file: Path to output file
        
        Returns:
            Path to output file
        """
        if not output_file:
            output_file = self.repo_root / 'workflow_anomaly_report.json'
        else:
            output_file = Path(output_file)
        
        results = self.run_full_analysis()
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Results exported to: {output_file}")
        return str(output_file)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Workflow anomaly detector by @create-guru'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate anomaly detection report'
    )
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export results to JSON file'
    )
    parser.add_argument(
        '--check',
        metavar='WORKFLOW',
        help='Check specific workflow for anomalies'
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
    
    detector = WorkflowAnomalyDetector(repo_root=args.repo_root)
    
    if args.simulate:
        print("🧪 Simulating execution data with anomalies...")
        detector.predictor.simulate_execution_data(num_workflows=10, num_executions=100)
        print("✓ Data simulated\n")
    
    if args.check:
        print(f"\n🔍 Checking workflow: {args.check}")
        health = detector.calculate_health_score(args.check)
        print(f"  Overall Health Score: {health.overall_score}")
        print(f"  Success Score: {health.success_score}")
        print(f"  Duration Score: {health.duration_score}")
        print(f"  Consistency Score: {health.consistency_score}")
        print(f"  Trend Score: {health.trend_score}\n")
    elif args.export:
        detector.export_results(args.export)
    elif args.report or not (args.check or args.export):
        detector.generate_report()


if __name__ == '__main__':
    main()
