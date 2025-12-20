#!/usr/bin/env python3
"""
Spawning Analytics and Dashboard Tool

Provides real-time analytics and historical insights into the AI sub-agent
spawning system's effectiveness, patterns, and performance.

Features:
- Spawning history analysis
- Effectiveness metrics
- Workload pattern detection
- Parent-child relationship analytics
- Spawning decision quality scoring
- Recommendation engine for spawning optimization

Created by @create-botter - Visionary infrastructure for the Chained ecosystem.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import argparse

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from registry_manager import RegistryManager
except ImportError as e:
    print(f"Error: Required modules not found: {e}")
    sys.exit(1)


@dataclass
class SpawningEvent:
    """Represents a spawning event"""
    timestamp: datetime
    agent_id: str
    agent_name: str
    specialization: str
    spawn_type: str
    spawn_reason: str
    parent_agent_id: Optional[str] = None
    workload_context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class SpawningMetrics:
    """Overall spawning system metrics"""
    total_spawns: int
    workload_based_spawns: int
    learning_based_spawns: int
    active_sub_agents: int
    deactivated_sub_agents: int
    avg_sub_agent_lifetime_hours: float
    avg_workload_per_agent: float
    most_spawned_specialization: str
    least_spawned_specialization: str
    spawning_frequency_per_day: float
    effectiveness_score: float  # 0-1 scale


@dataclass
class EffectivenessAnalysis:
    """Analysis of spawning effectiveness"""
    spawning_decision_quality: float  # 0-1 scale
    workload_reduction_rate: float  # Percentage
    sub_agent_utilization: float  # 0-1 scale
    parent_child_performance_correlation: float  # -1 to 1
    recommendations: List[str]


class SpawningAnalytics:
    """
    Analyze and report on the AI sub-agent spawning system.
    
    Visionary approach by @create-botter:
    - Holistic system view
    - Pattern recognition
    - Predictive insights
    - Actionable recommendations
    
    Note: Some metrics are currently placeholders pending additional data:
    - avg_workload_per_agent: Requires historical workload tracking
    - workload_reduction_rate: Requires before/after workload comparisons
    - parent_child_performance_correlation: Requires performance metrics
    
    These will be fully implemented in future enhancements.
    """
    
    def __init__(self, registry_path: str = ".github/agent-system"):
        """
        Initialize spawning analytics.
        
        Args:
            registry_path: Path to agent registry
        """
        self.registry_path = Path(registry_path)
        
        try:
            self.registry = RegistryManager(str(self.registry_path))
        except Exception as e:
            print(f"Warning: Could not initialize registry: {e}")
            self.registry = None
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """
        Parse timestamp string with error handling.
        
        Args:
            timestamp_str: ISO format timestamp string
            
        Returns:
            datetime object or None if parsing fails
        """
        try:
            return datetime.fromisoformat(
                timestamp_str.replace('Z', '+00:00')
            )
        except (ValueError, AttributeError):
            return None
    
    def collect_spawning_history(self) -> List[SpawningEvent]:
        """
        Collect all spawning events from registry.
        
        Returns:
            List of SpawningEvent objects
        """
        events = []
        
        if not self.registry:
            return events
        
        try:
            # Get all agents (active and inactive)
            all_agents = self.registry.list_agents(status=None)
            
            for agent in all_agents:
                # Only include spawned agents (not original agents)
                if agent.get('spawned_at'):
                    timestamp = self._parse_timestamp(agent['spawned_at'])
                    if not timestamp:
                        # Skip if timestamp invalid
                        continue
                    
                    event = SpawningEvent(
                        timestamp=timestamp,
                        agent_id=agent['id'],
                        agent_name=agent.get('name', 'Unknown'),
                        specialization=agent.get('specialization', 'unknown'),
                        spawn_type=agent.get('spawn_type', 'standard'),
                        spawn_reason=agent.get('spawn_reason', 'No reason provided'),
                        parent_agent_id=agent.get('parent_agent_id'),
                        workload_context=agent.get('workload_context')
                    )
                    events.append(event)
            
            # Sort by timestamp
            events.sort(key=lambda e: e.timestamp)
            
        except Exception as e:
            print(f"Warning: Could not collect spawning history: {e}")
        
        return events
    
    def calculate_metrics(self, events: List[SpawningEvent]) -> SpawningMetrics:
        """
        Calculate overall spawning metrics.
        
        Args:
            events: List of spawning events
            
        Returns:
            SpawningMetrics object
        """
        if not events:
            return SpawningMetrics(
                total_spawns=0,
                workload_based_spawns=0,
                learning_based_spawns=0,
                active_sub_agents=0,
                deactivated_sub_agents=0,
                avg_sub_agent_lifetime_hours=0.0,
                avg_workload_per_agent=0.0,
                most_spawned_specialization="none",
                least_spawned_specialization="none",
                spawning_frequency_per_day=0.0,
                effectiveness_score=0.0
            )
        
        # Count by spawn type
        spawn_types = Counter(e.spawn_type for e in events)
        
        # Count by specialization
        specializations = Counter(e.specialization for e in events)
        
        # Get active and deactivated sub-agents
        active_sub_agents = 0
        deactivated_sub_agents = 0
        lifetimes = []
        
        if self.registry:
            try:
                all_agents = self.registry.list_agents(status=None)
                
                for agent in all_agents:
                    if agent.get('is_sub_agent'):
                        if agent.get('status') == 'active':
                            active_sub_agents += 1
                        elif agent.get('status') == 'deactivated':
                            deactivated_sub_agents += 1
                            
                            # Calculate lifetime
                            if agent.get('spawned_at') and agent.get('deactivated_at'):
                                spawned = self._parse_timestamp(agent['spawned_at'])
                                deactivated = self._parse_timestamp(agent['deactivated_at'])
                                
                                if spawned and deactivated:
                                    lifetime = (deactivated - spawned).total_seconds() / 3600
                                    lifetimes.append(lifetime)
            except Exception as e:
                print(f"Warning: Could not analyze sub-agents: {e}")
        
        # Calculate spawning frequency
        if len(events) >= 2:
            time_range = (events[-1].timestamp - events[0].timestamp).total_seconds() / 86400
            spawning_frequency = len(events) / max(time_range, 1)
        else:
            spawning_frequency = 0.0
        
        # Calculate effectiveness (simplified version - focuses on retention)
        # Future enhancement: Could incorporate workload reduction, performance gains
        effectiveness = 0.5  # Default neutral score
        if active_sub_agents + deactivated_sub_agents > 0:
            # Higher score if more are still active (indicates good utilization)
            effectiveness = active_sub_agents / (active_sub_agents + deactivated_sub_agents)
        
        return SpawningMetrics(
            total_spawns=len(events),
            workload_based_spawns=spawn_types.get('workload_based', 0),
            learning_based_spawns=spawn_types.get('learning_based', 0),
            active_sub_agents=active_sub_agents,
            deactivated_sub_agents=deactivated_sub_agents,
            avg_sub_agent_lifetime_hours=sum(lifetimes) / len(lifetimes) if lifetimes else 0.0,
            avg_workload_per_agent=0.0,  # TODO: Requires workload tracking integration
            most_spawned_specialization=specializations.most_common(1)[0][0] if specializations else "none",
            least_spawned_specialization=specializations.most_common()[-1][0] if len(specializations) > 1 else specializations.most_common(1)[0][0] if specializations else "none",
            spawning_frequency_per_day=spawning_frequency,
            effectiveness_score=effectiveness
        )
    
    def analyze_effectiveness(self, events: List[SpawningEvent], 
                            metrics: SpawningMetrics) -> EffectivenessAnalysis:
        """
        Analyze the effectiveness of the spawning system.
        
        Args:
            events: List of spawning events
            metrics: Overall metrics
            
        Returns:
            EffectivenessAnalysis object
        """
        recommendations = []
        
        # Decision quality (based on ratio of workload-based spawns)
        if metrics.total_spawns > 0:
            decision_quality = metrics.workload_based_spawns / metrics.total_spawns
        else:
            decision_quality = 0.5
        
        # Sub-agent utilization
        total_sub_agents = metrics.active_sub_agents + metrics.deactivated_sub_agents
        if total_sub_agents > 0:
            utilization = metrics.active_sub_agents / total_sub_agents
        else:
            utilization = 0.0
        
        # Generate recommendations
        if metrics.spawning_frequency_per_day > 3:
            recommendations.append(
                "⚠️  High spawning frequency detected. Consider adjusting "
                "workload thresholds to reduce churn."
            )
        
        if utilization < 0.3:
            recommendations.append(
                "⚠️  Low sub-agent utilization. Many sub-agents are being "
                "deactivated. Review spawning criteria."
            )
        
        if metrics.avg_sub_agent_lifetime_hours < 6:
            recommendations.append(
                "⚠️  Short sub-agent lifetime. Sub-agents are being deactivated "
                "quickly. Consider longer cooldown periods."
            )
        
        if decision_quality < 0.7:
            recommendations.append(
                "💡 Increase focus on workload-based spawning for better "
                "system responsiveness."
            )
        
        if not recommendations:
            recommendations.append(
                "✅ Spawning system is performing well. No immediate "
                "optimizations needed."
            )
        
        return EffectivenessAnalysis(
            spawning_decision_quality=decision_quality,
            workload_reduction_rate=0.0,  # Would need historical workload data
            sub_agent_utilization=utilization,
            parent_child_performance_correlation=0.0,  # Would need performance data
            recommendations=recommendations
        )
    
    def generate_report(self, format: str = 'text') -> str:
        """
        Generate comprehensive spawning analytics report.
        
        Args:
            format: Output format ('text' or 'json')
            
        Returns:
            Formatted report string
        """
        events = self.collect_spawning_history()
        metrics = self.calculate_metrics(events)
        effectiveness = self.analyze_effectiveness(events, metrics)
        
        if format == 'json':
            report = {
                'timestamp': datetime.now().isoformat(),
                'metrics': asdict(metrics),
                'effectiveness': asdict(effectiveness),
                'recent_events': [e.to_dict() for e in events[-10:]]
            }
            return json.dumps(report, indent=2)
        
        # Text format
        lines = [
            "# 🤖 AI Sub-Agent Spawning Analytics Dashboard",
            f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Period**: {len(events)} spawning events tracked",
            "\n## 📊 Overall Metrics\n"
        ]
        
        lines.extend([
            f"- **Total Spawns**: {metrics.total_spawns}",
            f"- **Workload-Based**: {metrics.workload_based_spawns} "
            f"({metrics.workload_based_spawns/max(metrics.total_spawns, 1)*100:.1f}%)",
            f"- **Learning-Based**: {metrics.learning_based_spawns}",
            f"- **Active Sub-Agents**: {metrics.active_sub_agents}",
            f"- **Deactivated Sub-Agents**: {metrics.deactivated_sub_agents}",
            f"- **Avg Sub-Agent Lifetime**: {metrics.avg_sub_agent_lifetime_hours:.1f} hours",
            f"- **Spawning Frequency**: {metrics.spawning_frequency_per_day:.2f} spawns/day",
            f"- **Most Spawned**: {metrics.most_spawned_specialization}",
            f"- **Effectiveness Score**: {metrics.effectiveness_score*100:.1f}%",
        ])
        
        lines.extend([
            "\n## 🎯 Effectiveness Analysis\n",
            f"- **Decision Quality**: {effectiveness.spawning_decision_quality*100:.1f}%",
            f"- **Sub-Agent Utilization**: {effectiveness.sub_agent_utilization*100:.1f}%",
            "\n### 💡 Recommendations\n"
        ])
        
        for rec in effectiveness.recommendations:
            lines.append(f"- {rec}")
        
        if events:
            lines.extend([
                "\n## 📅 Recent Spawning Events\n"
            ])
            
            for event in events[-5:]:
                lines.append(
                    f"- **{event.timestamp.strftime('%Y-%m-%d %H:%M')}**: "
                    f"{event.agent_name} ({event.specialization}) - "
                    f"{event.spawn_type}"
                )
        
        lines.extend([
            "\n---",
            "\n*Created by @create-botter - Visionary infrastructure analytics*",
            "*Part of the Chained autonomous AI ecosystem* 🤖"
        ])
        
        return '\n'.join(lines)
    
    def get_specialization_distribution(self) -> Dict[str, int]:
        """
        Get distribution of spawned agents by specialization.
        
        Returns:
            Dictionary mapping specialization to count
        """
        events = self.collect_spawning_history()
        return dict(Counter(e.specialization for e in events))
    
    def get_spawning_timeline(self, days: int = 30) -> List[Tuple[str, int]]:
        """
        Get spawning timeline for the last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of (date, count) tuples
        """
        events = self.collect_spawning_history()
        cutoff = datetime.now()
        
        # Make cutoff timezone-aware if needed (do this once, not in loop)
        if events and events[0].timestamp.tzinfo is not None:
            from datetime import timezone
            cutoff = cutoff.replace(tzinfo=timezone.utc)
        
        cutoff = cutoff - timedelta(days=days)
        
        # Filter recent events
        recent = [e for e in events if e.timestamp >= cutoff]
        
        # Group by date
        by_date = defaultdict(int)
        for event in recent:
            date_key = event.timestamp.strftime('%Y-%m-%d')
            by_date[date_key] += 1
        
        # Sort by date
        timeline = sorted(by_date.items())
        
        return timeline


def main():
    """CLI interface for spawning analytics"""
    parser = argparse.ArgumentParser(
        description='Analyze AI sub-agent spawning system effectiveness'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    parser.add_argument(
        '--registry-path', '-r',
        default='.github/agent-system',
        help='Path to agent registry'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Create analytics instance
    analytics = SpawningAnalytics(registry_path=args.registry_path)
    
    # Generate report
    report = analytics.generate_report(format=args.format)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"✅ Report saved to {args.output}")
    else:
        print(report)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
