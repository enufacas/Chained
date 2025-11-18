#!/usr/bin/env python3
"""
Adaptive Workload Monitor - ML-Enhanced Workload Analysis

Extends workload_monitor.py with:
- Adaptive thresholds based on historical patterns
- Time-of-day workload prediction
- Trend analysis and forecasting
- Self-tuning spawn decisions

Part of the Chained autonomous AI ecosystem.
Enhanced by @accelerate-specialist - Elegant efficiency with predictive intelligence.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from workload_monitor import (
    WorkloadMonitor, WorkloadMetrics, SpawningRecommendation
)


@dataclass
class WorkloadHistoryEntry:
    """Historical workload data point"""
    timestamp: str
    specialization: str
    open_issues: int
    pending_prs: int
    active_agents: int
    workload_per_agent: float
    bottleneck_severity: str


@dataclass
class AdaptiveThresholds:
    """Adaptive thresholds for a specialization"""
    specialization: str
    workload_threshold: float  # Adjusted based on patterns
    capacity_threshold: float
    spawn_confidence: float  # 0-1, how confident we are in spawning
    last_updated: str


class AdaptiveWorkloadMonitor(WorkloadMonitor):
    """
    Enhanced workload monitor with adaptive intelligence.
    
    Learns from historical patterns to make better spawning decisions.
    Uses elegant algorithms for efficient pattern detection.
    """
    
    # History tracking
    HISTORY_FILE = ".github/agent-system/workload_history.json"
    MAX_HISTORY_ENTRIES = 1000  # Keep last 1000 data points
    
    # Learning parameters
    LEARNING_RATE = 0.1  # How quickly to adapt thresholds
    MIN_HISTORY_FOR_LEARNING = 10  # Minimum data points needed
    
    def __init__(self, 
                 repo_path: str = ".",
                 registry_path: str = ".github/agent-system"):
        """
        Initialize adaptive workload monitor.
        
        Args:
            repo_path: Path to repository root
            registry_path: Path to agent registry
        """
        super().__init__(repo_path, registry_path)
        
        # Load historical data
        self.history = self._load_history()
        
        # Load or initialize adaptive thresholds
        self.adaptive_thresholds = self._load_adaptive_thresholds()
    
    def _load_history(self) -> List[WorkloadHistoryEntry]:
        """
        Load workload history from file.
        
        Returns:
            List of historical workload entries
        """
        history_path = Path(self.HISTORY_FILE)
        
        if not history_path.exists():
            return []
        
        try:
            with open(history_path, 'r') as f:
                data = json.load(f)
            
            # Convert to WorkloadHistoryEntry objects
            history = []
            for entry in data.get('entries', [])[:self.MAX_HISTORY_ENTRIES]:
                history.append(WorkloadHistoryEntry(**entry))
            
            return history
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
            return []
    
    def _save_history(self, new_metrics: Dict[str, WorkloadMetrics]):
        """
        Save current metrics to history.
        
        Args:
            new_metrics: Current workload metrics to add to history
        """
        timestamp = datetime.now().isoformat()
        
        # Add new entries
        for spec, metrics in new_metrics.items():
            entry = WorkloadHistoryEntry(
                timestamp=timestamp,
                specialization=spec,
                open_issues=metrics.open_issues,
                pending_prs=metrics.pending_prs,
                active_agents=metrics.active_agents,
                workload_per_agent=metrics.workload_per_agent,
                bottleneck_severity=metrics.bottleneck_severity
            )
            self.history.append(entry)
        
        # Keep only recent history
        if len(self.history) > self.MAX_HISTORY_ENTRIES:
            self.history = self.history[-self.MAX_HISTORY_ENTRIES:]
        
        # Save to file
        history_path = Path(self.HISTORY_FILE)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'last_updated': timestamp,
            'total_entries': len(self.history),
            'entries': [asdict(entry) for entry in self.history]
        }
        
        with open(history_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_adaptive_thresholds(self) -> Dict[str, AdaptiveThresholds]:
        """
        Load adaptive thresholds from file or initialize defaults.
        
        Returns:
            Dictionary mapping specialization to adaptive thresholds
        """
        thresholds_path = Path(".github/agent-system/adaptive_thresholds.json")
        
        if not thresholds_path.exists():
            return self._initialize_default_thresholds()
        
        try:
            with open(thresholds_path, 'r') as f:
                data = json.load(f)
            
            thresholds = {}
            for spec, thresh_data in data.get('thresholds', {}).items():
                thresholds[spec] = AdaptiveThresholds(**thresh_data)
            
            return thresholds
        except Exception as e:
            print(f"Warning: Could not load adaptive thresholds: {e}")
            return self._initialize_default_thresholds()
    
    def _initialize_default_thresholds(self) -> Dict[str, AdaptiveThresholds]:
        """
        Initialize default adaptive thresholds for all specializations.
        
        Returns:
            Default thresholds dictionary
        """
        thresholds = {}
        
        for spec in self.SPECIALIZATION_LABELS.keys():
            thresholds[spec] = AdaptiveThresholds(
                specialization=spec,
                workload_threshold=self.SPAWN_THRESHOLDS['workload_per_agent'],
                capacity_threshold=self.SPAWN_THRESHOLDS['bottleneck_threshold'],
                spawn_confidence=0.5,
                last_updated=datetime.now().isoformat()
            )
        
        return thresholds
    
    def _save_adaptive_thresholds(self):
        """Save adaptive thresholds to file"""
        thresholds_path = Path(".github/agent-system/adaptive_thresholds.json")
        thresholds_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'thresholds': {
                spec: asdict(thresh)
                for spec, thresh in self.adaptive_thresholds.items()
            }
        }
        
        with open(thresholds_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def analyze_workload_adaptive(self,
                                  issues_data: Optional[List[Dict]] = None,
                                  prs_data: Optional[List[Dict]] = None) -> Dict[str, WorkloadMetrics]:
        """
        Analyze workload with adaptive intelligence.
        
        Uses historical patterns to adjust spawn decisions.
        
        Args:
            issues_data: Optional list of issue data
            prs_data: Optional list of PR data
            
        Returns:
            Dictionary mapping specialization to WorkloadMetrics
        """
        # Get base metrics
        metrics = self.analyze_workload(issues_data, prs_data)
        
        # Apply adaptive adjustments
        for spec, metric in metrics.items():
            if spec in self.adaptive_thresholds:
                # Get historical trend
                trend = self._calculate_trend(spec)
                
                # Adjust priority score based on trend
                if trend > 0.2:  # Increasing workload
                    metric.priority_score *= 1.2
                elif trend < -0.2:  # Decreasing workload
                    metric.priority_score *= 0.8
                
                # Update confidence
                confidence = self._calculate_spawn_confidence(spec, metric)
                self.adaptive_thresholds[spec].spawn_confidence = confidence
        
        # Save current metrics to history
        self._save_history(metrics)
        
        # Learn and update thresholds
        self._update_adaptive_thresholds()
        
        return metrics
    
    def _calculate_trend(self, specialization: str, 
                        lookback_hours: int = 24) -> float:
        """
        Calculate workload trend for a specialization.
        
        Args:
            specialization: Specialization to analyze
            lookback_hours: Hours to look back
            
        Returns:
            Trend value (-1 to 1, negative=decreasing, positive=increasing)
        """
        # Get recent history for this specialization
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        
        recent_entries = [
            entry for entry in self.history
            if entry.specialization == specialization
            and datetime.fromisoformat(entry.timestamp) > cutoff
        ]
        
        if len(recent_entries) < 2:
            return 0.0  # Not enough data
        
        # Calculate simple linear trend
        workloads = [entry.workload_per_agent for entry in recent_entries]
        
        # Use first half vs second half comparison
        mid = len(workloads) // 2
        first_half_avg = statistics.mean(workloads[:mid])
        second_half_avg = statistics.mean(workloads[mid:])
        
        # Calculate normalized change
        if first_half_avg == 0:
            return 0.0
        
        change = (second_half_avg - first_half_avg) / first_half_avg
        
        # Normalize to -1 to 1
        return max(-1.0, min(1.0, change))
    
    def _calculate_spawn_confidence(self, 
                                   specialization: str,
                                   current_metrics: WorkloadMetrics) -> float:
        """
        Calculate confidence in spawning decision.
        
        Higher confidence when:
        - Consistent high workload pattern
        - Historical success with spawning
        - Clear upward trend
        
        Args:
            specialization: Specialization to analyze
            current_metrics: Current workload metrics
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Factor 1: Consistency of high workload
        recent_high = self._count_recent_bottlenecks(specialization, hours=12)
        if recent_high >= 3:
            confidence += 0.2
        elif recent_high >= 2:
            confidence += 0.1
        
        # Factor 2: Trend direction
        trend = self._calculate_trend(specialization)
        if trend > 0.3:
            confidence += 0.2
        elif trend > 0.1:
            confidence += 0.1
        
        # Factor 3: Current severity
        if current_metrics.bottleneck_severity == 'critical':
            confidence += 0.2
        elif current_metrics.bottleneck_severity == 'high':
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _count_recent_bottlenecks(self, specialization: str, 
                                  hours: int = 12) -> int:
        """
        Count recent bottleneck occurrences.
        
        Args:
            specialization: Specialization to check
            hours: Hours to look back
            
        Returns:
            Number of bottleneck occurrences
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        
        count = sum(
            1 for entry in self.history
            if entry.specialization == specialization
            and datetime.fromisoformat(entry.timestamp) > cutoff
            and entry.bottleneck_severity in ['high', 'critical']
        )
        
        return count
    
    def _update_adaptive_thresholds(self):
        """
        Update adaptive thresholds based on learning.
        
        Uses exponential moving average for smooth adaptation.
        """
        if len(self.history) < self.MIN_HISTORY_FOR_LEARNING:
            return  # Not enough data yet
        
        # Group history by specialization
        by_spec = defaultdict(list)
        for entry in self.history[-50:]:  # Last 50 entries
            by_spec[entry.specialization].append(entry)
        
        # Update thresholds for each specialization
        for spec, entries in by_spec.items():
            if spec not in self.adaptive_thresholds:
                continue
            
            # Calculate average workload
            avg_workload = statistics.mean(
                entry.workload_per_agent for entry in entries
            )
            
            # Calculate bottleneck frequency
            bottleneck_freq = sum(
                1 for entry in entries
                if entry.bottleneck_severity in ['high', 'critical']
            ) / len(entries)
            
            current = self.adaptive_thresholds[spec]
            
            # Adaptive threshold adjustment
            if bottleneck_freq > 0.5:
                # Frequent bottlenecks - lower threshold to spawn earlier
                new_threshold = current.workload_threshold * (1 - self.LEARNING_RATE)
            elif bottleneck_freq < 0.1:
                # Rare bottlenecks - raise threshold to spawn less
                new_threshold = current.workload_threshold * (1 + self.LEARNING_RATE)
            else:
                # Balanced - small adjustment toward average
                new_threshold = (
                    current.workload_threshold * (1 - self.LEARNING_RATE) +
                    avg_workload * self.LEARNING_RATE
                )
            
            # Update with bounds
            current.workload_threshold = max(
                2.0,  # Minimum threshold
                min(10.0, new_threshold)  # Maximum threshold
            )
            current.last_updated = datetime.now().isoformat()
        
        # Save updated thresholds
        self._save_adaptive_thresholds()
    
    def generate_spawning_recommendations_adaptive(self,
                                                  metrics: Dict[str, WorkloadMetrics],
                                                  max_spawns: int = 5) -> List[SpawningRecommendation]:
        """
        Generate spawning recommendations with adaptive intelligence.
        
        Args:
            metrics: Workload metrics by specialization
            max_spawns: Maximum number of spawning recommendations
            
        Returns:
            List of SpawningRecommendation, sorted by priority
        """
        recommendations = []
        
        for spec, metric in metrics.items():
            # Get adaptive threshold
            threshold = self.adaptive_thresholds.get(
                spec,
                self._initialize_default_thresholds()[spec]
            )
            
            # Check if spawning is needed (using adaptive threshold)
            should_spawn = (
                metric.workload_per_agent >= threshold.workload_threshold and
                metric.bottleneck_severity in ["high", "critical"] and
                metric.active_agents < self.SPAWN_THRESHOLDS['max_agents_per_category'] and
                threshold.spawn_confidence > 0.6  # Confidence gate
            )
            
            if not should_spawn:
                continue
            
            # Calculate spawn count based on confidence
            base_count = 2 if metric.bottleneck_severity == "critical" else 1
            count = min(
                int(base_count * threshold.spawn_confidence),
                self.SPAWN_THRESHOLDS['max_agents_per_category'] - metric.active_agents
            )
            
            if count == 0:
                continue
            
            # Calculate priority with confidence weighting
            priority_base = 5 if metric.priority_score >= 80 else \
                           4 if metric.priority_score >= 60 else \
                           3 if metric.priority_score >= 40 else \
                           2 if metric.priority_score >= 20 else 1
            
            priority = min(5, int(priority_base * threshold.spawn_confidence))
            
            # Build enhanced reason
            trend = self._calculate_trend(spec)
            trend_desc = "increasing" if trend > 0.1 else \
                        "decreasing" if trend < -0.1 else "stable"
            
            reason = (
                f"{spec.capitalize()} workload: {metric.open_issues} issues + "
                f"{metric.pending_prs} PRs with {metric.active_agents} agents "
                f"({metric.workload_per_agent:.1f} items/agent). "
                f"Severity: {metric.bottleneck_severity}. "
                f"Trend: {trend_desc} ({trend:+.2f}). "
                f"Confidence: {threshold.spawn_confidence:.0%}"
            )
            
            recommendations.append(SpawningRecommendation(
                should_spawn=should_spawn,
                specialization=spec,
                count=count,
                reason=reason,
                priority=priority,
                metrics=metric
            ))
        
        # Sort by priority and confidence
        recommendations.sort(
            key=lambda r: (
                r.priority,
                self.adaptive_thresholds.get(
                    r.specialization,
                    self._initialize_default_thresholds()[r.specialization]
                ).spawn_confidence,
                r.metrics.priority_score
            ),
            reverse=True
        )
        
        return recommendations[:max_spawns]
    
    def generate_adaptive_report(self,
                               metrics: Dict[str, WorkloadMetrics],
                               recommendations: List[SpawningRecommendation]) -> str:
        """
        Generate enhanced report with adaptive insights.
        
        Args:
            metrics: Workload metrics
            recommendations: Spawning recommendations
            
        Returns:
            Formatted report string
        """
        # Start with base report
        lines = [
            "# 📊 Adaptive Workload Analysis Report",
            f"\n**Generated:** {datetime.now().isoformat()}",
            f"**Mode:** Adaptive Intelligence Enabled 🧠",
            f"\n## System Overview\n",
        ]
        
        # Add adaptive insights
        total_entries = len(self.history)
        lines.extend([
            f"- **Historical Data Points:** {total_entries}",
            f"- **Learning Status:** {'Active' if total_entries >= self.MIN_HISTORY_FOR_LEARNING else 'Collecting Data'}",
        ])
        
        # Continue with standard metrics
        total_issues = sum(m.open_issues for m in metrics.values())
        total_prs = sum(m.pending_prs for m in metrics.values())
        total_agents = sum(m.active_agents for m in metrics.values())
        
        lines.extend([
            f"- **Total Open Issues:** {total_issues}",
            f"- **Total Pending PRs:** {total_prs}",
            f"- **Active Agents:** {total_agents}",
            f"- **Average Workload:** {(total_issues + total_prs) / max(total_agents, 1):.2f} items/agent",
            "\n## Workload by Specialization\n",
        ])
        
        # Add metrics with adaptive insights
        sorted_metrics = sorted(
            metrics.items(),
            key=lambda x: x[1].priority_score,
            reverse=True
        )
        
        for spec, metric in sorted_metrics:
            emoji = self._severity_emoji(metric.bottleneck_severity)
            
            # Get adaptive data
            threshold = self.adaptive_thresholds.get(spec)
            trend = self._calculate_trend(spec)
            trend_emoji = "📈" if trend > 0.1 else "📉" if trend < -0.1 else "➡️"
            
            lines.extend([
                f"### {emoji} {spec.capitalize()}",
                f"- **Issues:** {metric.open_issues}",
                f"- **PRs:** {metric.pending_prs}",
                f"- **Agents:** {metric.active_agents}",
                f"- **Workload/Agent:** {metric.workload_per_agent:.2f}",
                f"- **Capacity:** {metric.agent_capacity * 100:.0f}%",
                f"- **Severity:** {metric.bottleneck_severity}",
                f"- **Trend:** {trend_emoji} {trend:+.2%}",
            ])
            
            if threshold:
                lines.extend([
                    f"- **Adaptive Threshold:** {threshold.workload_threshold:.2f}",
                    f"- **Spawn Confidence:** {threshold.spawn_confidence:.0%}",
                ])
            
            lines.extend([
                f"- **Recommendation:** {metric.recommendation}",
                "",
            ])
        
        # Spawning recommendations
        if recommendations:
            lines.extend([
                "## 🚀 Adaptive Spawning Recommendations\n",
                f"**Total Recommendations:** {len(recommendations)}\n",
            ])
            
            for i, rec in enumerate(recommendations, 1):
                lines.extend([
                    f"### {i}. {rec.specialization.capitalize()} (Priority: {'⭐' * rec.priority})",
                    f"- **Should Spawn:** ✅ Yes",
                    f"- **Count:** {rec.count} agent(s)",
                    f"- **Reason:** {rec.reason}",
                    "",
                ])
        else:
            lines.append("\n## ✅ No Spawning Needed\n\nSystem is balanced based on adaptive thresholds.\n")
        
        return '\n'.join(lines)


def main():
    """CLI interface for adaptive workload monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Adaptive workload monitoring with ML-enhanced decisions'
    )
    parser.add_argument(
        '--output', '-o',
        default='.github/agent-system/workload_analysis.json',
        help='Output file for metrics'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Print human-readable report'
    )
    parser.add_argument(
        '--max-spawns', '-m',
        type=int,
        default=5,
        help='Maximum spawning recommendations'
    )
    
    args = parser.parse_args()
    
    # Create adaptive monitor
    monitor = AdaptiveWorkloadMonitor()
    
    # Analyze workload with adaptive intelligence
    print("🧠 Analyzing workload with adaptive intelligence...")
    metrics = monitor.analyze_workload_adaptive()
    
    # Generate adaptive recommendations
    print("🤔 Generating adaptive spawning recommendations...")
    recommendations = monitor.generate_spawning_recommendations_adaptive(
        metrics,
        max_spawns=args.max_spawns
    )
    
    # Save results
    print(f"💾 Saving results to {args.output}")
    monitor.save_metrics(metrics, recommendations, args.output)
    
    # Print report if requested
    if args.report:
        print("\n" + "=" * 80)
        report = monitor.generate_adaptive_report(metrics, recommendations)
        print(report)
        print("=" * 80)
    
    # Print summary
    print("\n✅ Adaptive workload analysis complete!")
    print(f"📊 {len(metrics)} specializations analyzed")
    print(f"🚀 {len(recommendations)} adaptive recommendations generated")
    print(f"📈 Learning from {len(monitor.history)} historical data points")
    
    if recommendations:
        print("\n⚠️  ADAPTIVE SPAWNING NEEDED:")
        for rec in recommendations:
            threshold = monitor.adaptive_thresholds.get(rec.specialization)
            confidence = threshold.spawn_confidence if threshold else 0.5
            print(f"  - {rec.specialization}: {rec.count} agent(s) "
                  f"(priority {rec.priority}, confidence {confidence:.0%})")
    else:
        print("\n✅ All specializations balanced with adaptive thresholds")
    
    return 0 if len(recommendations) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
