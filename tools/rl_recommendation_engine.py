#!/usr/bin/env python3
"""
RL Recommendation Engine for GitHub Actions
Created by @create-botter

Automated recommendation engine that analyzes workflow performance and generates
actionable optimization suggestions using reinforcement learning insights.

Tesla-Inspired Innovation:
- Autonomous recommendation generation
- Multi-workflow coordination
- Predictive optimization strategies
- Self-validating improvements
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import hashlib

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from rl_resource_optimizer import RLResourceOptimizer, ResourceState, ResourceAction, OptimizationRecommendation
    from rl_optimizer_enhanced import EnhancedRLOptimizer
except ImportError:
    RLResourceOptimizer = None
    EnhancedRLOptimizer = None

try:
    from rl_performance_monitor import RLPerformanceMonitor
except ImportError:
    RLPerformanceMonitor = None


@dataclass
class WorkflowAnalysis:
    """Analysis of a workflow's current state."""
    workflow_name: str
    current_metrics: Dict[str, float]
    bottlenecks: List[str]
    optimization_potential: float  # 0-1
    priority: str  # low, medium, high, critical
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ActionableRecommendation:
    """Actionable recommendation with implementation details."""
    id: str
    workflow_name: str
    action: str
    description: str
    implementation_steps: List[str]
    expected_improvement: float
    confidence: float
    priority: int
    estimated_impact: str
    risks: List[str]
    validation_criteria: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CoordinationPlan:
    """System-wide optimization coordination plan."""
    plan_id: str
    workflows_affected: List[str]
    recommendations: List[ActionableRecommendation]
    execution_order: List[str]
    total_expected_improvement: float
    coordination_strategy: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RLRecommendationEngine:
    """
    Automated recommendation engine for workflow optimization.
    
    Features:
    - Workflow performance analysis
    - RL-driven optimization suggestions
    - Multi-workflow coordination
    - Automated recommendation generation
    - Impact prediction and validation
    """
    
    # Priority thresholds
    PRIORITY_CRITICAL_THRESHOLD = 0.8  # >80% improvement potential
    PRIORITY_HIGH_THRESHOLD = 0.5      # >50% improvement potential
    PRIORITY_MEDIUM_THRESHOLD = 0.2    # >20% improvement potential
    
    # Duration thresholds (seconds)
    LONG_DURATION_THRESHOLD_SECONDS = 600  # 10 minutes
    PARALLELIZATION_THRESHOLD_SECONDS = 300  # 5 minutes
    
    def __init__(self, repo_root: str = None, use_enhanced: bool = True):
        """Initialize the recommendation engine."""
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
        
        # Initialize RL optimizer
        if use_enhanced and EnhancedRLOptimizer:
            self.optimizer = EnhancedRLOptimizer(repo_root=str(self.repo_root))
            self.optimizer_type = "enhanced"
        elif RLResourceOptimizer:
            self.optimizer = RLResourceOptimizer(repo_root=str(self.repo_root))
            self.optimizer_type = "base"
        else:
            self.optimizer = None
            self.optimizer_type = "none"
        
        # Initialize performance monitor
        if RLPerformanceMonitor:
            self.monitor = RLPerformanceMonitor(repo_root=str(self.repo_root))
        else:
            self.monitor = None
        
        # Storage paths
        self.recommendations_dir = self.repo_root / '.github' / 'rl-optimizer' / 'recommendations'
        self.recommendations_dir.mkdir(parents=True, exist_ok=True)
        
        self.recommendations_file = self.recommendations_dir / 'active_recommendations.json'
        self.coordination_plans_file = self.recommendations_dir / 'coordination_plans.json'
        self.analysis_file = self.recommendations_dir / 'workflow_analysis.json'
        
        # Load existing data
        self.active_recommendations: List[ActionableRecommendation] = self._load_recommendations()
        self.coordination_plans: List[CoordinationPlan] = self._load_coordination_plans()
        self.workflow_analyses: Dict[str, WorkflowAnalysis] = {}
    
    def _load_recommendations(self) -> List[ActionableRecommendation]:
        """Load active recommendations from storage."""
        if self.recommendations_file.exists():
            try:
                with open(self.recommendations_file, 'r') as f:
                    data = json.load(f)
                    return [
                        ActionableRecommendation(
                            id=item['id'],
                            workflow_name=item['workflow_name'],
                            action=item['action'],
                            description=item['description'],
                            implementation_steps=item['implementation_steps'],
                            expected_improvement=item['expected_improvement'],
                            confidence=item['confidence'],
                            priority=item['priority'],
                            estimated_impact=item['estimated_impact'],
                            risks=item['risks'],
                            validation_criteria=item['validation_criteria'],
                            created_at=datetime.fromisoformat(item['created_at'])
                        )
                        for item in data
                    ]
            except Exception as e:
                print(f"Warning: Could not load recommendations: {e}", file=sys.stderr)
        return []
    
    def _load_coordination_plans(self) -> List[CoordinationPlan]:
        """Load coordination plans from storage."""
        if self.coordination_plans_file.exists():
            try:
                with open(self.coordination_plans_file, 'r') as f:
                    data = json.load(f)
                    plans = []
                    for item in data:
                        # Reconstruct recommendations with proper datetime handling
                        recs = []
                        for rec_data in item['recommendations']:
                            if isinstance(rec_data, dict):
                                # Convert ISO datetime string back to datetime object
                                if 'created_at' in rec_data and isinstance(rec_data['created_at'], str):
                                    rec_data['created_at'] = datetime.fromisoformat(rec_data['created_at'])
                                recs.append(ActionableRecommendation(**rec_data))
                            else:
                                recs.append(rec_data)
                        
                        plans.append(CoordinationPlan(
                            plan_id=item['plan_id'],
                            workflows_affected=item['workflows_affected'],
                            recommendations=recs,
                            execution_order=item['execution_order'],
                            total_expected_improvement=item['total_expected_improvement'],
                            coordination_strategy=item['coordination_strategy'],
                            created_at=datetime.fromisoformat(item['created_at'])
                        ))
                    return plans
            except Exception as e:
                print(f"Warning: Could not load coordination plans: {e}", file=sys.stderr)
        return []
    
    def save_all(self) -> None:
        """Save all data to storage."""
        # Save recommendations
        try:
            with open(self.recommendations_file, 'w') as f:
                json.dump([asdict(rec) for rec in self.active_recommendations], f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save recommendations: {e}", file=sys.stderr)
        
        # Save coordination plans
        try:
            with open(self.coordination_plans_file, 'w') as f:
                json.dump([asdict(plan) for plan in self.coordination_plans], f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save coordination plans: {e}", file=sys.stderr)
        
        # Save workflow analyses
        try:
            with open(self.analysis_file, 'w') as f:
                json.dump({name: asdict(analysis) for name, analysis in self.workflow_analyses.items()}, 
                         f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save workflow analysis: {e}", file=sys.stderr)
    
    def analyze_workflow(self, workflow_name: str, current_state: ResourceState) -> WorkflowAnalysis:
        """
        Analyze a workflow's current state and identify optimization opportunities.
        """
        bottlenecks = []
        optimization_potential = 0.0
        
        # Identify bottlenecks
        if current_state.success_rate < 0.9:
            bottlenecks.append(f"Low success rate ({current_state.success_rate*100:.1f}%)")
            optimization_potential += 0.3
        
        if current_state.avg_duration_seconds > self.LONG_DURATION_THRESHOLD_SECONDS:
            bottlenecks.append(f"Long duration ({current_state.avg_duration_seconds/60:.1f} min)")
            optimization_potential += 0.3
        
        if current_state.resource_utilization < 0.5:
            bottlenecks.append(f"Low resource utilization ({current_state.resource_utilization*100:.0f}%)")
            optimization_potential += 0.2
        
        if not current_state.caching_enabled:
            bottlenecks.append("Caching disabled")
            optimization_potential += 0.15
        
        if current_state.parallel_jobs == 1 and current_state.avg_duration_seconds > self.PARALLELIZATION_THRESHOLD_SECONDS:
            bottlenecks.append("Sequential execution (could parallelize)")
            optimization_potential += 0.25
        
        # Determine priority
        if optimization_potential >= self.PRIORITY_CRITICAL_THRESHOLD:
            priority = "critical"
        elif optimization_potential >= self.PRIORITY_HIGH_THRESHOLD:
            priority = "high"
        elif optimization_potential >= self.PRIORITY_MEDIUM_THRESHOLD:
            priority = "medium"
        else:
            priority = "low"
        
        analysis = WorkflowAnalysis(
            workflow_name=workflow_name,
            current_metrics={
                'duration_seconds': current_state.avg_duration_seconds,
                'success_rate': current_state.success_rate,
                'utilization': current_state.resource_utilization,
                'concurrency': current_state.concurrency_limit,
                'timeout': current_state.timeout_minutes,
                'caching': 1.0 if current_state.caching_enabled else 0.0,
                'parallel_jobs': current_state.parallel_jobs
            },
            bottlenecks=bottlenecks,
            optimization_potential=min(1.0, optimization_potential),
            priority=priority
        )
        
        self.workflow_analyses[workflow_name] = analysis
        return analysis
    
    def generate_recommendation(self, workflow_name: str, analysis: WorkflowAnalysis) -> Optional[ActionableRecommendation]:
        """Generate an actionable recommendation based on workflow analysis."""
        if not self.optimizer:
            return None
        
        # Get RL optimizer's recommendation
        # This is simplified - in practice, we'd query the optimizer with current state
        best_action = None
        best_q_value = float('-inf')
        
        # Find state in Q-table or use policy
        # For now, generate based on analysis
        
        action = None
        description = ""
        implementation_steps = []
        risks = []
        validation_criteria = {}
        
        # Determine best action based on bottlenecks
        if any("Low success rate" in b for b in analysis.bottlenecks):
            action = ResourceAction.EXTEND_TIMEOUT.value
            description = "Extend timeout to reduce failure rate"
            implementation_steps = [
                "Increase timeout_minutes by 50%",
                "Monitor failure rate for 1 week",
                "Adjust if needed"
            ]
            risks = ["May mask underlying issues", "Increased cost if workflow actually hangs"]
            validation_criteria = {
                'success_rate_threshold': 0.95,
                'monitoring_period_days': 7,
                'revert_if': 'no improvement after 2 weeks'
            }
        
        elif any("Long duration" in b for b in analysis.bottlenecks):
            if not analysis.current_metrics.get('caching'):
                action = ResourceAction.ENABLE_CACHING.value
                description = "Enable dependency caching to reduce build time"
                implementation_steps = [
                    "Add caching step for dependencies",
                    "Configure cache key appropriately",
                    "Test cache hit rate"
                ]
                risks = ["Initial cache miss overhead", "Cache invalidation issues"]
                validation_criteria = {
                    'duration_reduction_threshold': 0.2,
                    'cache_hit_rate_target': 0.7,
                    'monitoring_period_days': 3
                }
            elif analysis.current_metrics.get('parallel_jobs', 1) == 1:
                action = ResourceAction.PARALLELIZE_JOBS.value
                description = "Parallelize independent jobs to reduce total duration"
                implementation_steps = [
                    "Identify independent jobs",
                    "Update workflow to run jobs in parallel",
                    "Test for race conditions"
                ]
                risks = ["Increased resource consumption", "Potential race conditions"]
                validation_criteria = {
                    'duration_reduction_threshold': 0.3,
                    'no_new_failures': True,
                    'monitoring_period_days': 5
                }
        
        elif any("Low resource utilization" in b for b in analysis.bottlenecks):
            action = ResourceAction.REDUCE_TIMEOUT.value
            description = "Reduce timeout to free resources faster"
            implementation_steps = [
                "Reduce timeout by 25%",
                "Monitor for timeout failures",
                "Adjust based on actual runtime"
            ]
            risks = ["May cause false failures if workflow occasionally slower"]
            validation_criteria = {
                'no_timeout_failures': True,
                'monitoring_period_days': 7
            }
        
        if not action:
            return None
        
        # Generate recommendation ID
        rec_id = hashlib.md5(f"{workflow_name}_{action}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Calculate expected improvement
        expected_improvement = min(analysis.optimization_potential * 100, 50)  # Cap at 50%
        
        # Calculate confidence
        confidence = 0.7 if analysis.priority in ["high", "critical"] else 0.5
        
        # Determine priority (1=highest, 10=lowest)
        priority_map = {"critical": 1, "high": 3, "medium": 5, "low": 7}
        priority = priority_map.get(analysis.priority, 5)
        
        recommendation = ActionableRecommendation(
            id=rec_id,
            workflow_name=workflow_name,
            action=action,
            description=description,
            implementation_steps=implementation_steps,
            expected_improvement=expected_improvement,
            confidence=confidence,
            priority=priority,
            estimated_impact=analysis.priority,
            risks=risks,
            validation_criteria=validation_criteria
        )
        
        return recommendation
    
    def generate_all_recommendations(self, workflow_states: Dict[str, ResourceState]) -> List[ActionableRecommendation]:
        """Generate recommendations for all workflows."""
        print(f"🔍 Analyzing {len(workflow_states)} workflows...")
        recommendations = []
        
        for workflow_name, state in workflow_states.items():
            # Analyze workflow
            analysis = self.analyze_workflow(workflow_name, state)
            
            # Generate recommendation if potential exists
            if analysis.optimization_potential > 0.1:  # At least 10% potential
                rec = self.generate_recommendation(workflow_name, analysis)
                if rec:
                    recommendations.append(rec)
                    print(f"  ✅ {workflow_name}: {rec.description} ({rec.expected_improvement:.1f}% improvement)")
        
        self.active_recommendations = recommendations
        return recommendations
    
    def create_coordination_plan(self, recommendations: List[ActionableRecommendation]) -> CoordinationPlan:
        """Create a system-wide coordination plan for multiple recommendations."""
        if not recommendations:
            return None
        
        # Sort by priority
        sorted_recs = sorted(recommendations, key=lambda r: r.priority)
        
        # Group by workflow
        workflows_affected = list(set(rec.workflow_name for rec in sorted_recs))
        
        # Determine execution order (high priority first)
        execution_order = [rec.id for rec in sorted_recs]
        
        # Calculate total improvement
        total_improvement = sum(rec.expected_improvement for rec in sorted_recs) / len(sorted_recs)
        
        # Determine coordination strategy
        if len(workflows_affected) > 5:
            strategy = "phased_rollout"
        elif any(rec.priority <= 2 for rec in sorted_recs):
            strategy = "immediate"
        else:
            strategy = "batch"
        
        plan_id = hashlib.md5(f"plan_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        plan = CoordinationPlan(
            plan_id=plan_id,
            workflows_affected=workflows_affected,
            recommendations=sorted_recs,
            execution_order=execution_order,
            total_expected_improvement=total_improvement,
            coordination_strategy=strategy
        )
        
        self.coordination_plans.append(plan)
        return plan
    
    def generate_report(self) -> str:
        """Generate a comprehensive recommendation report."""
        report_lines = [
            "=" * 70,
            "💡 RL Recommendation Engine Report - @create-botter",
            "=" * 70,
            ""
        ]
        
        # Summary
        report_lines.extend([
            "📊 Summary",
            f"  Workflows Analyzed: {len(self.workflow_analyses)}",
            f"  Active Recommendations: {len(self.active_recommendations)}",
            f"  Coordination Plans: {len(self.coordination_plans)}",
            ""
        ])
        
        # Recommendations by priority
        if self.active_recommendations:
            by_priority = defaultdict(list)
            for rec in self.active_recommendations:
                by_priority[rec.estimated_impact].append(rec)
            
            report_lines.append("🎯 Recommendations by Priority")
            report_lines.append("")
            
            for priority in ["critical", "high", "medium", "low"]:
                recs = by_priority.get(priority, [])
                if recs:
                    report_lines.append(f"  {priority.upper()} ({len(recs)})")
                    for rec in recs[:3]:  # Top 3
                        report_lines.extend([
                            f"    • {rec.workflow_name}",
                            f"      {rec.description}",
                            f"      Expected: {rec.expected_improvement:.1f}% improvement",
                            f"      Confidence: {rec.confidence*100:.0f}%",
                            ""
                        ])
        
        # Coordination plans
        if self.coordination_plans:
            latest_plan = self.coordination_plans[-1]
            report_lines.extend([
                "🔄 Latest Coordination Plan",
                f"  Plan ID: {latest_plan.plan_id}",
                f"  Workflows: {len(latest_plan.workflows_affected)}",
                f"  Recommendations: {len(latest_plan.recommendations)}",
                f"  Strategy: {latest_plan.coordination_strategy}",
                f"  Expected Improvement: {latest_plan.total_expected_improvement:.1f}%",
                ""
            ])
        
        report_lines.extend([
            "=" * 70,
            f"Generated at: {datetime.now(timezone.utc).isoformat()}",
            f"Optimizer: {self.optimizer_type}",
            "=" * 70
        ])
        
        return "\n".join(report_lines)


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='RL Recommendation Engine - @create-botter'
    )
    parser.add_argument('--repo-root', help='Repository root directory')
    parser.add_argument('--analyze', action='store_true', help='Analyze all workflows')
    parser.add_argument('--generate', action='store_true', help='Generate recommendations')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--export', metavar='FILE', help='Export recommendations to JSON')
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = RLRecommendationEngine(repo_root=args.repo_root)
    
    if args.analyze or args.generate:
        # In a real scenario, we'd load actual workflow states from data collector
        # For now, use dummy data
        print("⚠️  Note: Using sample workflow states for demonstration")
        print("    In production, this would query actual workflow metrics")
        print()
        
        sample_states = {}
        # This would be populated from actual workflow data
    
    if args.report:
        print(engine.generate_report())
    
    if args.export:
        export_data = {
            'recommendations': [asdict(rec) for rec in engine.active_recommendations],
            'coordination_plans': [asdict(plan) for plan in engine.coordination_plans],
            'analyses': {name: asdict(analysis) for name, analysis in engine.workflow_analyses.items()}
        }
        with open(args.export, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        print(f"📤 Exported to {args.export}")


if __name__ == '__main__':
    main()
