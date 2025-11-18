#!/usr/bin/env python3
"""
Workload Monitor - Intelligent Workload Analysis for Sub-Agent Spawning

Monitors system workload across different specializations and determines
when and what type of sub-agents should be spawned to handle the load.

Features:
- Track open issues by label and category
- Monitor PR review queue depth
- Calculate agent capacity and utilization
- Identify performance bottlenecks
- Generate spawning recommendations

Part of the Chained autonomous AI ecosystem.
Created by @accelerate-specialist - Elegant efficiency with a twist of humor.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from registry_manager import RegistryManager
except ImportError:
    print("Warning: registry_manager not found, using minimal fallback")
    RegistryManager = None


@dataclass
class WorkloadMetrics:
    """Workload metrics for a specific specialization"""
    specialization: str
    open_issues: int
    pending_prs: int
    active_agents: int
    agent_capacity: float  # 0-1 scale
    workload_per_agent: float
    priority_score: float
    bottleneck_severity: str  # "none", "low", "medium", "high", "critical"
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SpawningRecommendation:
    """Recommendation for spawning sub-agents"""
    should_spawn: bool
    specialization: str
    count: int
    reason: str
    priority: int  # 1-5, 5 being highest
    metrics: WorkloadMetrics


class WorkloadMonitor:
    """
    Monitor system workload and recommend sub-agent spawning.
    
    Uses elegant algorithms inspired by Dijkstra's efficiency principles:
    - O(n) workload analysis
    - Minimal redundancy
    - Clear decision boundaries
    """
    
    # Specialization categories and their issue label mappings
    SPECIALIZATION_LABELS = {
        'security': ['security', 'vulnerability', 'CVE', 'exploit'],
        'performance': ['performance', 'optimization', 'slow', 'bottleneck'],
        'bug-fix': ['bug', 'error', 'crash', 'regression'],
        'feature': ['feature', 'enhancement', 'new'],
        'documentation': ['documentation', 'docs', 'readme'],
        'testing': ['test', 'testing', 'coverage', 'qa'],
        'infrastructure': ['infrastructure', 'deployment', 'ci-cd', 'devops'],
        'refactoring': ['refactor', 'cleanup', 'technical-debt'],
        'ai-ml': ['ai', 'ml', 'llm', 'agent', 'autonomous'],
        'api': ['api', 'integration', 'rest', 'graphql'],
    }
    
    # Agent specialization to category mapping
    AGENT_CATEGORIES = {
        'secure-specialist': 'security',
        'secure-ninja': 'security',
        'secure-pro': 'security',
        'guardian-master': 'security',
        'monitor-champion': 'security',
        'accelerate-master': 'performance',
        'accelerate-specialist': 'performance',
        'organize-guru': 'refactoring',
        'organize-specialist': 'refactoring',
        'refactor-champion': 'refactoring',
        'cleaner-master': 'refactoring',
        'simplify-pro': 'refactoring',
        'assert-specialist': 'testing',
        'assert-whiz': 'testing',
        'validator-pro': 'testing',
        'edge-cases-pro': 'testing',
        'engineer-master': 'feature',
        'engineer-wizard': 'feature',
        'create-guru': 'infrastructure',
        'infrastructure-specialist': 'infrastructure',
        'construct-specialist': 'infrastructure',
        'APIs-architect': 'api',
        'connector-ninja': 'api',
        'bridge-master': 'api',
        'integrate-specialist': 'api',
        'document-ninja': 'documentation',
        'clarify-champion': 'documentation',
        'support-master': 'documentation',
    }
    
    # Workload thresholds for spawning decisions
    SPAWN_THRESHOLDS = {
        'workload_per_agent': 5.0,  # Issues+PRs per agent
        'bottleneck_threshold': 0.8,  # 80% capacity
        'critical_threshold': 10.0,  # Critical if >10 items per agent
        'max_agents_per_category': 8,  # Max agents in one category
    }
    
    def __init__(self, 
                 repo_path: str = ".",
                 registry_path: str = ".github/agent-system"):
        """
        Initialize workload monitor.
        
        Args:
            repo_path: Path to repository root
            registry_path: Path to agent registry
        """
        self.repo_path = Path(repo_path)
        self.registry_path = Path(registry_path)
        
        # Load registry if available
        if RegistryManager:
            try:
                self.registry = RegistryManager(str(self.registry_path))
            except Exception as e:
                print(f"Warning: Could not load registry: {e}")
                self.registry = None
        else:
            self.registry = None
    
    def analyze_workload(self, 
                        issues_data: Optional[List[Dict]] = None,
                        prs_data: Optional[List[Dict]] = None) -> Dict[str, WorkloadMetrics]:
        """
        Analyze current workload across specializations.
        
        Args:
            issues_data: Optional list of issue data (for testing)
            prs_data: Optional list of PR data (for testing)
            
        Returns:
            Dictionary mapping specialization to WorkloadMetrics
        """
        # In production, would fetch from GitHub API
        # For now, use provided data or mock data
        if issues_data is None:
            issues_data = self._load_mock_issues()
        
        if prs_data is None:
            prs_data = self._load_mock_prs()
        
        # Categorize issues and PRs by specialization
        workload_by_spec = self._categorize_workload(issues_data, prs_data)
        
        # Get agent counts by specialization
        agent_counts = self._count_agents_by_specialization()
        
        # Calculate metrics for each specialization
        metrics = {}
        for spec, workload in workload_by_spec.items():
            agent_count = agent_counts.get(spec, 0)
            
            # Avoid division by zero
            workload_per_agent = (
                workload['issues'] + workload['prs']
            ) / max(agent_count, 1)
            
            # Calculate capacity (0-1 scale)
            capacity = min(workload_per_agent / self.SPAWN_THRESHOLDS['workload_per_agent'], 1.0)
            
            # Determine bottleneck severity
            severity = self._calculate_bottleneck_severity(
                workload_per_agent, 
                capacity,
                agent_count
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                spec,
                workload_per_agent,
                capacity,
                agent_count,
                severity
            )
            
            # Calculate priority score (0-100)
            priority_score = self._calculate_priority_score(
                workload_per_agent,
                capacity,
                severity
            )
            
            metrics[spec] = WorkloadMetrics(
                specialization=spec,
                open_issues=workload['issues'],
                pending_prs=workload['prs'],
                active_agents=agent_count,
                agent_capacity=capacity,
                workload_per_agent=workload_per_agent,
                priority_score=priority_score,
                bottleneck_severity=severity,
                recommendation=recommendation
            )
        
        return metrics
    
    def _categorize_workload(self, 
                           issues: List[Dict], 
                           prs: List[Dict]) -> Dict[str, Dict[str, int]]:
        """
        Categorize issues and PRs by specialization.
        
        Returns:
            Dictionary mapping specialization to {issues: int, prs: int}
        """
        workload = defaultdict(lambda: {'issues': 0, 'prs': 0})
        
        # Categorize issues
        for issue in issues:
            labels = issue.get('labels', [])
            specs = self._labels_to_specializations(labels)
            
            for spec in specs:
                workload[spec]['issues'] += 1
        
        # Categorize PRs
        for pr in prs:
            labels = pr.get('labels', [])
            specs = self._labels_to_specializations(labels)
            
            for spec in specs:
                workload[spec]['prs'] += 1
        
        return dict(workload)
    
    def _labels_to_specializations(self, labels: List[str]) -> List[str]:
        """
        Map issue/PR labels to specializations.
        
        Returns:
            List of relevant specializations
        """
        specializations = set()
        
        labels_lower = [label.lower() for label in labels]
        
        for spec, spec_labels in self.SPECIALIZATION_LABELS.items():
            for spec_label in spec_labels:
                if any(spec_label.lower() in label for label in labels_lower):
                    specializations.add(spec)
                    break
        
        # Default to 'feature' if no match
        if not specializations:
            specializations.add('feature')
        
        return list(specializations)
    
    def _count_agents_by_specialization(self) -> Dict[str, int]:
        """
        Count active agents by specialization category.
        
        Returns:
            Dictionary mapping specialization to agent count
        """
        counts = defaultdict(int)
        
        if not self.registry:
            # Return mock data for testing
            return {
                'security': 3,
                'performance': 2,
                'feature': 5,
                'testing': 3,
                'refactoring': 4,
                'infrastructure': 3,
                'documentation': 3,
                'api': 2,
                'ai-ml': 4,
            }
        
        try:
            agents = self.registry.list_agents(status='active')
            
            for agent in agents:
                spec_name = agent.get('specialization', '')
                category = self.AGENT_CATEGORIES.get(spec_name, 'feature')
                counts[category] += 1
        except Exception as e:
            print(f"Warning: Could not count agents: {e}")
        
        return dict(counts)
    
    def _calculate_bottleneck_severity(self,
                                      workload_per_agent: float,
                                      capacity: float,
                                      agent_count: int) -> str:
        """
        Calculate bottleneck severity based on metrics.
        
        Returns:
            Severity level: "none", "low", "medium", "high", "critical"
        """
        if workload_per_agent >= self.SPAWN_THRESHOLDS['critical_threshold']:
            return "critical"
        elif capacity >= 0.9:
            return "high"
        elif capacity >= 0.7:
            return "medium"
        elif capacity >= 0.5:
            return "low"
        else:
            return "none"
    
    def _generate_recommendation(self,
                                spec: str,
                                workload_per_agent: float,
                                capacity: float,
                                agent_count: int,
                                severity: str) -> str:
        """Generate human-readable recommendation"""
        if severity == "critical":
            return f"URGENT: Spawn 2-3 {spec} agents immediately"
        elif severity == "high":
            return f"Recommend spawning 1-2 {spec} agents"
        elif severity == "medium":
            return f"Consider spawning 1 {spec} agent"
        elif severity == "low":
            return f"Monitor {spec} workload, may need agent soon"
        else:
            return f"{spec} workload is manageable"
    
    def _calculate_priority_score(self,
                                  workload_per_agent: float,
                                  capacity: float,
                                  severity: str) -> float:
        """
        Calculate priority score (0-100).
        
        Higher score = more urgent need for sub-agents
        """
        # Base score from workload
        base_score = min(workload_per_agent * 5, 50)
        
        # Capacity multiplier
        capacity_bonus = capacity * 30
        
        # Severity bonus
        severity_bonuses = {
            "critical": 20,
            "high": 15,
            "medium": 10,
            "low": 5,
            "none": 0
        }
        severity_bonus = severity_bonuses.get(severity, 0)
        
        total_score = base_score + capacity_bonus + severity_bonus
        
        return min(total_score, 100)
    
    def generate_spawning_recommendations(self,
                                         metrics: Dict[str, WorkloadMetrics],
                                         max_spawns: int = 5) -> List[SpawningRecommendation]:
        """
        Generate recommendations for spawning sub-agents.
        
        Args:
            metrics: Workload metrics by specialization
            max_spawns: Maximum number of spawning recommendations
            
        Returns:
            List of SpawningRecommendation, sorted by priority
        """
        recommendations = []
        
        for spec, metric in metrics.items():
            # Check if spawning is needed
            should_spawn = (
                metric.bottleneck_severity in ["high", "critical"] and
                metric.active_agents < self.SPAWN_THRESHOLDS['max_agents_per_category']
            )
            
            if not should_spawn:
                continue
            
            # Calculate how many to spawn
            if metric.bottleneck_severity == "critical":
                count = min(3, self.SPAWN_THRESHOLDS['max_agents_per_category'] - metric.active_agents)
            else:  # high
                count = min(2, self.SPAWN_THRESHOLDS['max_agents_per_category'] - metric.active_agents)
            
            # Determine priority (1-5)
            if metric.priority_score >= 80:
                priority = 5
            elif metric.priority_score >= 60:
                priority = 4
            elif metric.priority_score >= 40:
                priority = 3
            elif metric.priority_score >= 20:
                priority = 2
            else:
                priority = 1
            
            # Build reason
            reason = (
                f"{spec.capitalize()} workload: {metric.open_issues} issues + "
                f"{metric.pending_prs} PRs with {metric.active_agents} agents "
                f"({metric.workload_per_agent:.1f} items/agent). "
                f"Severity: {metric.bottleneck_severity}"
            )
            
            recommendations.append(SpawningRecommendation(
                should_spawn=should_spawn,
                specialization=spec,
                count=count,
                reason=reason,
                priority=priority,
                metrics=metric
            ))
        
        # Sort by priority (highest first)
        recommendations.sort(key=lambda r: (r.priority, r.metrics.priority_score), reverse=True)
        
        # Limit to max_spawns
        return recommendations[:max_spawns]
    
    def _load_mock_issues(self) -> List[Dict]:
        """Load mock issue data for testing"""
        return [
            {'labels': ['security', 'bug'], 'state': 'open'},
            {'labels': ['security', 'vulnerability'], 'state': 'open'},
            {'labels': ['performance', 'optimization'], 'state': 'open'},
            {'labels': ['performance'], 'state': 'open'},
            {'labels': ['bug', 'error'], 'state': 'open'},
            {'labels': ['feature', 'enhancement'], 'state': 'open'},
            {'labels': ['feature'], 'state': 'open'},
            {'labels': ['documentation'], 'state': 'open'},
            {'labels': ['test', 'coverage'], 'state': 'open'},
            {'labels': ['infrastructure', 'ci-cd'], 'state': 'open'},
        ]
    
    def _load_mock_prs(self) -> List[Dict]:
        """Load mock PR data for testing"""
        return [
            {'labels': ['security'], 'state': 'open'},
            {'labels': ['performance'], 'state': 'open'},
            {'labels': ['feature'], 'state': 'open'},
            {'labels': ['bug'], 'state': 'open'},
        ]
    
    def generate_report(self,
                       metrics: Dict[str, WorkloadMetrics],
                       recommendations: List[SpawningRecommendation]) -> str:
        """
        Generate human-readable workload report.
        
        Args:
            metrics: Workload metrics
            recommendations: Spawning recommendations
            
        Returns:
            Formatted report string
        """
        lines = [
            "# 📊 Workload Analysis Report",
            f"\n**Generated:** {datetime.now().isoformat()}",
            f"\n## System Overview\n",
        ]
        
        # Summary statistics
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
        
        # Sort metrics by priority score
        sorted_metrics = sorted(
            metrics.items(),
            key=lambda x: x[1].priority_score,
            reverse=True
        )
        
        for spec, metric in sorted_metrics:
            emoji = self._severity_emoji(metric.bottleneck_severity)
            lines.extend([
                f"### {emoji} {spec.capitalize()}",
                f"- **Issues:** {metric.open_issues}",
                f"- **PRs:** {metric.pending_prs}",
                f"- **Agents:** {metric.active_agents}",
                f"- **Workload/Agent:** {metric.workload_per_agent:.2f}",
                f"- **Capacity:** {metric.agent_capacity * 100:.0f}%",
                f"- **Severity:** {metric.bottleneck_severity}",
                f"- **Priority Score:** {metric.priority_score:.1f}",
                f"- **Recommendation:** {metric.recommendation}",
                "",
            ])
        
        # Spawning recommendations
        if recommendations:
            lines.extend([
                "## 🚀 Spawning Recommendations\n",
                f"**Total Recommendations:** {len(recommendations)}\n",
            ])
            
            for i, rec in enumerate(recommendations, 1):
                lines.extend([
                    f"### {i}. {rec.specialization.capitalize()} (Priority: {'⭐' * rec.priority})",
                    f"- **Should Spawn:** {'✅ Yes' if rec.should_spawn else '❌ No'}",
                    f"- **Count:** {rec.count} agent(s)",
                    f"- **Reason:** {rec.reason}",
                    "",
                ])
        else:
            lines.append("\n## ✅ No Spawning Needed\n\nAll specializations are operating within capacity.\n")
        
        return '\n'.join(lines)
    
    def _severity_emoji(self, severity: str) -> str:
        """Get emoji for severity level"""
        emoji_map = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "none": "⚪"
        }
        return emoji_map.get(severity, "⚪")
    
    def save_metrics(self, 
                    metrics: Dict[str, WorkloadMetrics],
                    recommendations: List[SpawningRecommendation],
                    output_file: str = ".github/agent-system/workload_analysis.json"):
        """
        Save metrics and recommendations to JSON file.
        
        Args:
            metrics: Workload metrics
            recommendations: Spawning recommendations
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                spec: metric.to_dict() 
                for spec, metric in metrics.items()
            },
            'recommendations': [
                {
                    'should_spawn': rec.should_spawn,
                    'specialization': rec.specialization,
                    'count': rec.count,
                    'reason': rec.reason,
                    'priority': rec.priority,
                    'metrics': rec.metrics.to_dict()
                }
                for rec in recommendations
            ],
            'summary': {
                'total_bottlenecks': sum(
                    1 for m in metrics.values() 
                    if m.bottleneck_severity in ['high', 'critical']
                ),
                'spawning_needed': len(recommendations) > 0,
                'recommended_spawns': sum(rec.count for rec in recommendations)
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """CLI interface for workload monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Monitor workload and recommend sub-agent spawning'
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
    
    # Create monitor
    monitor = WorkloadMonitor()
    
    # Analyze workload
    print("🔍 Analyzing workload...")
    metrics = monitor.analyze_workload()
    
    # Generate recommendations
    print("🤔 Generating spawning recommendations...")
    recommendations = monitor.generate_spawning_recommendations(
        metrics,
        max_spawns=args.max_spawns
    )
    
    # Save results
    print(f"💾 Saving results to {args.output}")
    monitor.save_metrics(metrics, recommendations, args.output)
    
    # Print report if requested
    if args.report:
        print("\n" + "=" * 80)
        report = monitor.generate_report(metrics, recommendations)
        print(report)
        print("=" * 80)
    
    # Print summary
    print("\n✅ Workload analysis complete!")
    print(f"📊 {len(metrics)} specializations analyzed")
    print(f"🚀 {len(recommendations)} spawning recommendations generated")
    
    if recommendations:
        print("\n⚠️  SPAWNING NEEDED:")
        for rec in recommendations:
            print(f"  - {rec.specialization}: {rec.count} agent(s) (priority {rec.priority})")
    else:
        print("\n✅ All specializations operating within capacity")
    
    return 0 if len(recommendations) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
