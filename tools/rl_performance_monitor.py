#!/usr/bin/env python3
"""
RL Performance Monitor for GitHub Actions
Created by @create-botter

Real-time performance monitoring and analytics for the RL resource optimizer.
Tracks learning progress, recommendation effectiveness, and system-wide metrics.

Tesla-Inspired Features:
- Autonomous performance tracking
- Predictive convergence detection
- Self-optimizing feedback loops
- Visual performance dashboards
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import statistics

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))


@dataclass
class PerformanceMetric:
    """Performance metric snapshot."""
    timestamp: datetime
    metric_name: str
    value: float
    workflow_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningProgress:
    """Tracks RL agent learning progress."""
    episode: int
    total_reward: float
    avg_reward: float
    epsilon: float
    learning_rate: float
    q_table_size: int
    convergence_score: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RecommendationOutcome:
    """Tracks outcome of applying a recommendation."""
    workflow_name: str
    recommendation_id: str
    action_taken: str
    applied_at: datetime
    before_duration: float
    after_duration: float
    before_success_rate: float
    after_success_rate: float
    improvement_percentage: float
    validated: bool = False


class RLPerformanceMonitor:
    """
    Performance monitoring and analytics for RL resource optimizer.
    
    Features:
    - Real-time metric collection
    - Learning progress tracking
    - Recommendation effectiveness analysis
    - Convergence detection
    - Performance visualization data
    """
    
    def __init__(self, repo_root: str = None):
        """Initialize the performance monitor."""
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
        self.metrics_dir = self.repo_root / '.github' / 'rl-optimizer' / 'metrics'
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.learning_history_file = self.metrics_dir / 'learning_history.json'
        self.recommendation_outcomes_file = self.metrics_dir / 'recommendation_outcomes.json'
        self.performance_metrics_file = self.metrics_dir / 'performance_metrics.json'
        self.convergence_file = self.metrics_dir / 'convergence_metrics.json'
        
        # Load existing data
        self.learning_history: List[LearningProgress] = self._load_learning_history()
        self.recommendation_outcomes: List[RecommendationOutcome] = self._load_recommendation_outcomes()
        self.performance_metrics: List[PerformanceMetric] = self._load_performance_metrics()
    
    def _load_learning_history(self) -> List[LearningProgress]:
        """Load learning history from storage."""
        if self.learning_history_file.exists():
            try:
                with open(self.learning_history_file, 'r') as f:
                    data = json.load(f)
                    return [
                        LearningProgress(
                            episode=item['episode'],
                            total_reward=item['total_reward'],
                            avg_reward=item['avg_reward'],
                            epsilon=item['epsilon'],
                            learning_rate=item['learning_rate'],
                            q_table_size=item['q_table_size'],
                            convergence_score=item['convergence_score'],
                            timestamp=datetime.fromisoformat(item['timestamp'])
                        )
                        for item in data
                    ]
            except Exception as e:
                print(f"Warning: Could not load learning history: {e}", file=sys.stderr)
        return []
    
    def _load_recommendation_outcomes(self) -> List[RecommendationOutcome]:
        """Load recommendation outcomes from storage."""
        if self.recommendation_outcomes_file.exists():
            try:
                with open(self.recommendation_outcomes_file, 'r') as f:
                    data = json.load(f)
                    return [
                        RecommendationOutcome(
                            workflow_name=item['workflow_name'],
                            recommendation_id=item['recommendation_id'],
                            action_taken=item['action_taken'],
                            applied_at=datetime.fromisoformat(item['applied_at']),
                            before_duration=item['before_duration'],
                            after_duration=item['after_duration'],
                            before_success_rate=item['before_success_rate'],
                            after_success_rate=item['after_success_rate'],
                            improvement_percentage=item['improvement_percentage'],
                            validated=item.get('validated', False)
                        )
                        for item in data
                    ]
            except Exception as e:
                print(f"Warning: Could not load recommendation outcomes: {e}", file=sys.stderr)
        return []
    
    def _load_performance_metrics(self) -> List[PerformanceMetric]:
        """Load performance metrics from storage."""
        if self.performance_metrics_file.exists():
            try:
                with open(self.performance_metrics_file, 'r') as f:
                    data = json.load(f)
                    # Keep only last 1000 metrics to prevent unbounded growth
                    return [
                        PerformanceMetric(
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            metric_name=item['metric_name'],
                            value=item['value'],
                            workflow_name=item.get('workflow_name'),
                            metadata=item.get('metadata', {})
                        )
                        for item in data[-1000:]
                    ]
            except Exception as e:
                print(f"Warning: Could not load performance metrics: {e}", file=sys.stderr)
        return []
    
    def save_all(self) -> None:
        """Save all tracked data to storage."""
        # Save learning history
        try:
            with open(self.learning_history_file, 'w') as f:
                json.dump([asdict(lp) for lp in self.learning_history], f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save learning history: {e}", file=sys.stderr)
        
        # Save recommendation outcomes
        try:
            with open(self.recommendation_outcomes_file, 'w') as f:
                json.dump([asdict(ro) for ro in self.recommendation_outcomes], f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save recommendation outcomes: {e}", file=sys.stderr)
        
        # Save performance metrics
        try:
            with open(self.performance_metrics_file, 'w') as f:
                json.dump([asdict(pm) for pm in self.performance_metrics], f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save performance metrics: {e}", file=sys.stderr)
    
    def record_learning_progress(self, episode: int, total_reward: float, avg_reward: float,
                                 epsilon: float, learning_rate: float, q_table_size: int) -> None:
        """Record learning progress snapshot."""
        # Calculate convergence score
        convergence_score = self._calculate_convergence_score(avg_reward)
        
        progress = LearningProgress(
            episode=episode,
            total_reward=total_reward,
            avg_reward=avg_reward,
            epsilon=epsilon,
            learning_rate=learning_rate,
            q_table_size=q_table_size,
            convergence_score=convergence_score
        )
        
        self.learning_history.append(progress)
    
    def _calculate_convergence_score(self, current_avg_reward: float) -> float:
        """
        Calculate convergence score (0-1) based on reward stability.
        
        Higher score indicates better convergence (less variance in recent rewards).
        """
        if len(self.learning_history) < 10:
            return 0.0
        
        # Get last 10 average rewards
        recent_rewards = [lp.avg_reward for lp in self.learning_history[-10:]]
        recent_rewards.append(current_avg_reward)
        
        # Need at least 2 values for stdev
        if len(recent_rewards) < 2:
            return 0.0
        
        # Calculate coefficient of variation (lower is better)
        mean_reward = statistics.mean(recent_rewards)
        if mean_reward == 0:
            return 0.0
        
        try:
            std_reward = statistics.stdev(recent_rewards)
        except statistics.StatisticsError:
            return 0.0
        
        cv = std_reward / abs(mean_reward)
        
        # Convert to 0-1 score (lower CV = higher score)
        # CV of 0.1 or less = score of 0.9+
        convergence_score = max(0.0, 1.0 - cv)
        
        return convergence_score
    
    def record_recommendation_outcome(self, workflow_name: str, recommendation_id: str,
                                     action_taken: str, before_duration: float,
                                     after_duration: float, before_success_rate: float,
                                     after_success_rate: float) -> None:
        """Record outcome of applying a recommendation."""
        # Calculate improvement (positive = improvement, negative = regression)
        if before_duration > 0:
            improvement = ((before_duration - after_duration) / before_duration * 100)
        else:
            improvement = 0.0
        
        outcome = RecommendationOutcome(
            workflow_name=workflow_name,
            recommendation_id=recommendation_id,
            action_taken=action_taken,
            applied_at=datetime.now(timezone.utc),
            before_duration=before_duration,
            after_duration=after_duration,
            before_success_rate=before_success_rate,
            after_success_rate=after_success_rate,
            improvement_percentage=improvement,
            validated=False
        )
        
        self.recommendation_outcomes.append(outcome)
    
    def record_metric(self, metric_name: str, value: float, workflow_name: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a performance metric."""
        metric = PerformanceMetric(
            timestamp=datetime.now(timezone.utc),
            metric_name=metric_name,
            value=value,
            workflow_name=workflow_name,
            metadata=metadata or {}
        )
        
        self.performance_metrics.append(metric)
        
        # Keep only last 1000 metrics
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
    
    def get_convergence_status(self) -> Dict[str, Any]:
        """Get current convergence status."""
        if not self.learning_history:
            return {
                'converged': False,
                'convergence_score': 0.0,
                'episodes_trained': 0,
                'status': 'no_data'
            }
        
        latest = self.learning_history[-1]
        
        # Consider converged if:
        # - Convergence score > 0.8
        # - Epsilon < 0.1 (mostly exploitation)
        # - At least 50 episodes
        converged = (
            latest.convergence_score > 0.8 and
            latest.epsilon < 0.1 and
            latest.episode >= 50
        )
        
        status = 'converged' if converged else 'learning'
        if latest.episode < 10:
            status = 'initializing'
        
        return {
            'converged': converged,
            'convergence_score': latest.convergence_score,
            'episodes_trained': latest.episode,
            'epsilon': latest.epsilon,
            'q_table_size': latest.q_table_size,
            'avg_reward': latest.avg_reward,
            'status': status
        }
    
    def get_recommendation_effectiveness(self) -> Dict[str, Any]:
        """Calculate effectiveness of recommendations."""
        if not self.recommendation_outcomes:
            return {
                'total_recommendations': 0,
                'avg_improvement': 0.0,
                'success_rate': 0.0,
                'workflows_optimized': 0
            }
        
        improvements = [ro.improvement_percentage for ro in self.recommendation_outcomes]
        successful = sum(1 for ro in self.recommendation_outcomes if ro.improvement_percentage > 0)
        workflows = len(set(ro.workflow_name for ro in self.recommendation_outcomes))
        
        return {
            'total_recommendations': len(self.recommendation_outcomes),
            'avg_improvement': statistics.mean(improvements) if improvements else 0.0,
            'median_improvement': statistics.median(improvements) if improvements else 0.0,
            'success_rate': successful / len(self.recommendation_outcomes) if self.recommendation_outcomes else 0.0,
            'workflows_optimized': workflows,
            'best_improvement': max(improvements) if improvements else 0.0,
            'worst_case': min(improvements) if improvements else 0.0
        }
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for performance dashboard."""
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'convergence': self.get_convergence_status(),
            'effectiveness': self.get_recommendation_effectiveness(),
            'learning_progress': {
                'total_episodes': len(self.learning_history),
                'latest_reward': self.learning_history[-1].avg_reward if self.learning_history else 0.0,
                'reward_trend': self._calculate_reward_trend()
            },
            'system_metrics': self._get_system_metrics()
        }
    
    def _calculate_reward_trend(self) -> str:
        """Calculate trend in rewards (improving, stable, declining)."""
        if len(self.learning_history) < 5:
            return 'insufficient_data'
        
        recent = [lp.avg_reward for lp in self.learning_history[-5:]]
        older = [lp.avg_reward for lp in self.learning_history[-10:-5]] if len(self.learning_history) >= 10 else recent
        
        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        
        if recent_avg > older_avg * 1.05:
            return 'improving'
        elif recent_avg < older_avg * 0.95:
            return 'declining'
        else:
            return 'stable'
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get aggregated system metrics."""
        # Group metrics by type
        metrics_by_type = defaultdict(list)
        for metric in self.performance_metrics[-100:]:  # Last 100 metrics
            metrics_by_type[metric.metric_name].append(metric.value)
        
        aggregated = {}
        for metric_name, values in metrics_by_type.items():
            aggregated[metric_name] = {
                'current': values[-1] if values else 0.0,
                'avg': statistics.mean(values) if values else 0.0,
                'min': min(values) if values else 0.0,
                'max': max(values) if values else 0.0
            }
        
        return aggregated
    
    def generate_report(self) -> str:
        """Generate a human-readable performance report."""
        report_lines = [
            "=" * 70,
            "🎯 RL Performance Monitor Report - @create-botter",
            "=" * 70,
            ""
        ]
        
        # Convergence status
        convergence = self.get_convergence_status()
        report_lines.extend([
            "📊 Learning Status",
            f"  Status: {convergence['status'].upper()}",
            f"  Convergence Score: {convergence['convergence_score']:.2f}",
            f"  Episodes Trained: {convergence['episodes_trained']}",
            f"  Exploration Rate (ε): {convergence.get('epsilon', 0):.3f}",
            f"  Q-Table Size: {convergence.get('q_table_size', 0)} states",
            ""
        ])
        
        # Recommendation effectiveness
        effectiveness = self.get_recommendation_effectiveness()
        report_lines.extend([
            "💡 Recommendation Effectiveness",
            f"  Total Applied: {effectiveness['total_recommendations']}",
            f"  Success Rate: {effectiveness['success_rate']*100:.1f}%",
            f"  Average Improvement: {effectiveness['avg_improvement']:.1f}%",
            f"  Median Improvement: {effectiveness.get('median_improvement', 0):.1f}%",
            f"  Best Result: {effectiveness.get('best_improvement', 0):.1f}%",
            f"  Workflows Optimized: {effectiveness['workflows_optimized']}",
            ""
        ])
        
        # Learning trend
        if self.learning_history:
            trend = self._calculate_reward_trend()
            report_lines.extend([
                "📈 Learning Trend",
                f"  Direction: {trend.upper()}",
                f"  Latest Avg Reward: {self.learning_history[-1].avg_reward:.3f}",
                ""
            ])
        
        # Recent recommendations
        if self.recommendation_outcomes:
            report_lines.extend([
                "🔍 Recent Recommendations (Last 5)",
                ""
            ])
            for outcome in self.recommendation_outcomes[-5:]:
                report_lines.extend([
                    f"  • {outcome.workflow_name}",
                    f"    Action: {outcome.action_taken}",
                    f"    Improvement: {outcome.improvement_percentage:.1f}%",
                    f"    Duration: {outcome.before_duration:.0f}s → {outcome.after_duration:.0f}s",
                    ""
                ])
        
        report_lines.extend([
            "=" * 70,
            f"Generated at: {datetime.now(timezone.utc).isoformat()}",
            "=" * 70
        ])
        
        return "\n".join(report_lines)


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='RL Performance Monitor - @create-botter'
    )
    parser.add_argument('--repo-root', help='Repository root directory')
    parser.add_argument('--report', action='store_true', help='Generate performance report')
    parser.add_argument('--dashboard', action='store_true', help='Generate dashboard data')
    parser.add_argument('--export', metavar='FILE', help='Export dashboard data to JSON')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = RLPerformanceMonitor(repo_root=args.repo_root)
    
    if args.report:
        print(monitor.generate_report())
    
    if args.dashboard or args.export:
        dashboard_data = monitor.generate_dashboard_data()
        
        if args.export:
            with open(args.export, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
            print(f"📊 Dashboard data exported to {args.export}")
        else:
            print(json.dumps(dashboard_data, indent=2))


if __name__ == '__main__':
    main()
