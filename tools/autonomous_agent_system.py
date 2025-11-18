#!/usr/bin/env python3
"""
Integrated Autonomous Agent System

Combines adaptive monitoring, coordination, and spawning into a unified system.
This is the main orchestrator for the autonomous agent ecosystem.

Features:
- Adaptive workload monitoring with ML
- Agent coordination and load balancing
- Intelligent sub-agent spawning
- Hibernation management
- Cross-specialization collaboration

Created by @accelerate-specialist - The complete autonomous agent solution.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from adaptive_workload_monitor import AdaptiveWorkloadMonitor
from agent_coordinator import AgentCoordinator
from workload_subagent_spawner import SubAgentSpawner
from predictive_spawning_engine import PredictiveSpawningEngine


class AutonomousAgentSystem:
    """
    Integrated autonomous agent system.
    
    Orchestrates all aspects of the self-managing agent ecosystem:
    1. Adaptive monitoring (detects patterns, predicts needs)
    2. Coordination (load balancing, communication)
    3. Spawning (creates new agents as needed)
    4. Lifecycle management (hibernation, wake-up)
    """
    
    def __init__(self, 
                 repo_path: str = ".",
                 registry_path: str = ".github/agent-system"):
        """
        Initialize the autonomous agent system.
        
        Args:
            repo_path: Path to repository root
            registry_path: Path to agent registry
        """
        self.repo_path = repo_path
        self.registry_path = registry_path
        
        # Initialize components
        self.monitor = AdaptiveWorkloadMonitor(repo_path, registry_path)
        self.coordinator = AgentCoordinator(registry_path)
        self.spawner = SubAgentSpawner(repo_path, registry_path)
        self.predictor = PredictiveSpawningEngine(repo_path)
    
    def run_full_cycle(self, 
                      max_spawns: int = 5,
                      enable_hibernation: bool = True,
                      enable_redistribution: bool = True) -> Dict[str, Any]:
        """
        Run a complete autonomous cycle.
        
        This is the main orchestration method that:
        1. Analyzes workload adaptively
        2. Coordinates existing agents
        3. Spawns new agents if needed
        4. Manages agent lifecycle
        
        Args:
            max_spawns: Maximum new agents to spawn
            enable_hibernation: Whether to hibernate idle agents
            enable_redistribution: Whether to redistribute workload
            
        Returns:
            Summary of actions taken
        """
        print("🚀 Starting Autonomous Agent System Cycle")
        print("=" * 80)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'phases': {},
            'actions_taken': []
        }
        
        # Phase 1: Adaptive Workload Analysis
        print("\n📊 Phase 1: Adaptive Workload Analysis")
        print("-" * 80)
        
        metrics = self.monitor.analyze_workload_adaptive()
        recommendations = self.monitor.generate_spawning_recommendations_adaptive(
            metrics,
            max_spawns=max_spawns
        )
        
        summary['phases']['adaptive_analysis'] = {
            'metrics_count': len(metrics),
            'recommendations': len(recommendations),
            'history_size': len(self.monitor.history),
            'learning_active': len(self.monitor.history) >= self.monitor.MIN_HISTORY_FOR_LEARNING
        }
        
        print(f"  ✅ Analyzed {len(metrics)} specializations")
        print(f"  ✅ Generated {len(recommendations)} recommendations")
        print(f"  ✅ Learning from {len(self.monitor.history)} historical data points")
        
        # Phase 2: Agent Coordination
        print("\n🤝 Phase 2: Agent Coordination")
        print("-" * 80)
        
        coordination_actions = []
        
        # Update agent states based on current metrics
        for spec, metric in metrics.items():
            # Update state for active agents
            for i in range(metric.active_agents):
                agent_id = f"{spec}-agent-{i+1}"
                self.coordinator.update_agent_state(
                    agent_id=agent_id,
                    specialization=spec,
                    current_workload=int(metric.workload_per_agent),
                    capacity=10
                )
        
        # Redistribute workload if enabled
        if enable_redistribution:
            for spec in metrics.keys():
                redistribution_msgs = self.coordinator.redistribute_workload(spec)
                if redistribution_msgs:
                    coordination_actions.append({
                        'type': 'redistribution',
                        'specialization': spec,
                        'messages': len(redistribution_msgs)
                    })
                    print(f"  ✅ Redistributed {spec} workload ({len(redistribution_msgs)} messages)")
        
        # Manage hibernation if enabled
        hibernation_count = 0
        if enable_hibernation:
            candidates = self.coordinator.identify_hibernation_candidates()
            for candidate in candidates:
                self.coordinator.hibernate_agent(candidate.agent_id)
                coordination_actions.append({
                    'type': 'hibernation',
                    'agent_id': candidate.agent_id,
                    'specialization': candidate.specialization
                })
                hibernation_count += 1
            
            if hibernation_count > 0:
                print(f"  😴 Hibernated {hibernation_count} idle agent(s)")
        
        # Suggest collaborations
        collaborations = self.coordinator.suggest_cross_specialization_collaboration()
        for collab in collaborations:
            coordination_actions.append({
                'type': 'collaboration_suggestion',
                'primary': collab['primary_spec'],
                'secondary': collab['secondary_spec'],
                'reason': collab['reason']
            })
        
        if collaborations:
            print(f"  🤝 Suggested {len(collaborations)} collaboration(s)")
        
        summary['phases']['coordination'] = {
            'actions': len(coordination_actions),
            'redistributions': sum(1 for a in coordination_actions if a['type'] == 'redistribution'),
            'hibernations': hibernation_count,
            'collaboration_suggestions': len(collaborations)
        }
        
        summary['actions_taken'].extend(coordination_actions)
        
        # Phase 3: Intelligent Spawning
        print("\n🌱 Phase 3: Intelligent Agent Spawning")
        print("-" * 80)
        
        spawned_count = 0
        if recommendations:
            for rec in recommendations:
                print(f"  🎯 Spawning {rec.count} {rec.specialization} agent(s)")
                print(f"     Reason: {rec.reason}")
                
                # Get adaptive threshold for confidence info
                threshold = self.monitor.adaptive_thresholds.get(rec.specialization)
                if threshold:
                    print(f"     Confidence: {threshold.spawn_confidence:.0%}")
                
                # Execute spawning
                result = self.spawner.spawn_agents(
                    specialization=rec.specialization,
                    count=rec.count,
                    priority=rec.priority,
                    reason=rec.reason
                )
                
                if result.get('success'):
                    spawned_count += result.get('spawned', 0)
                    summary['actions_taken'].append({
                        'type': 'spawn',
                        'specialization': rec.specialization,
                        'count': result.get('spawned', 0),
                        'priority': rec.priority,
                        'confidence': threshold.spawn_confidence if threshold else 0.5
                    })
                    print(f"  ✅ Spawned {result.get('spawned', 0)} agent(s)")
                else:
                    print(f"  ⚠️  Spawn failed: {result.get('reason', 'unknown')}")
        else:
            print("  ✅ No spawning needed - system is balanced")
        
        summary['phases']['spawning'] = {
            'recommendations': len(recommendations),
            'spawned': spawned_count
        }
        
        # Phase 3.5: Predictive/Proactive Spawning
        print("\n🔮 Phase 3.5: Predictive Spawning (Advanced)")
        print("-" * 80)
        
        predictive_spawns = 0
        predictive_recommendations = self.predictor.get_predictive_recommendations()
        
        if predictive_recommendations:
            print(f"  🔮 {len(predictive_recommendations)} predictive recommendation(s)")
            
            # Record observations for learning
            for spec, metric in metrics.items():
                workload = metric.open_issues + metric.pending_prs
                self.predictor.record_observation(spec, workload)
            
            # Execute top predictive spawns (limited to avoid over-spawning)
            max_predictive = max(0, max_spawns - spawned_count)
            for rec in predictive_recommendations[:max_predictive]:
                if rec['confidence'] >= self.predictor.parameters['confidence_threshold']:
                    print(f"  🔮 Predictive spawn: {rec['category']} ({rec['agents_needed']} agents)")
                    print(f"     Confidence: {rec['confidence']:.0%}, Lead time: {rec['lead_time_hours']}h")
                    print(f"     Reason: {rec['reason']}")
                    
                    # Execute predictive spawning
                    result = self.spawner.spawn_agents(
                        specialization=rec['category'],
                        count=rec['agents_needed'],
                        priority=rec['priority'],
                        reason=f"[PREDICTIVE] {rec['reason']}"
                    )
                    
                    if result.get('success'):
                        predictive_spawns += result.get('spawned', 0)
                        summary['actions_taken'].append({
                            'type': 'predictive_spawn',
                            'specialization': rec['category'],
                            'count': result.get('spawned', 0),
                            'confidence': rec['confidence'],
                            'lead_time_hours': rec['lead_time_hours']
                        })
                        print(f"  ✅ Predictively spawned {result.get('spawned', 0)} agent(s)")
        else:
            print("  ✅ No predictive spawning needed - workload trends stable")
        
        summary['phases']['predictive_spawning'] = {
            'recommendations': len(predictive_recommendations),
            'spawned': predictive_spawns,
            'history_size': len(self.predictor.history)
        }
        
        # Phase 4: System Health Check
        print("\n🏥 Phase 4: System Health Check")
        print("-" * 80)
        
        total_agents = sum(m.active_agents for m in metrics.values())
        total_workload = sum(m.open_issues + m.pending_prs for m in metrics.values())
        avg_utilization = (
            sum(m.agent_capacity for m in metrics.values()) / len(metrics)
            if metrics else 0.0
        )
        
        bottleneck_count = sum(
            1 for m in metrics.values()
            if m.bottleneck_severity in ['high', 'critical']
        )
        
        summary['health'] = {
            'total_agents': total_agents,
            'total_workload': total_workload,
            'avg_utilization': avg_utilization,
            'bottlenecks': bottleneck_count,
            'status': 'healthy' if bottleneck_count == 0 else 'needs_attention'
        }
        
        print(f"  📊 Total Agents: {total_agents}")
        print(f"  📊 Total Workload: {total_workload} items")
        print(f"  📊 Avg Utilization: {avg_utilization:.0%}")
        print(f"  📊 Bottlenecks: {bottleneck_count}")
        
        health_emoji = "✅" if bottleneck_count == 0 else "⚠️"
        print(f"  {health_emoji} System Status: {summary['health']['status']}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 Cycle Summary")
        print("=" * 80)
        print(f"  • Analyzed: {len(metrics)} specializations")
        print(f"  • Coordinated: {len(coordination_actions)} actions")
        print(f"  • Reactive Spawns: {spawned_count} new agents")
        print(f"  • Predictive Spawns: {predictive_spawns} new agents")
        print(f"  • Hibernated: {hibernation_count} idle agents")
        print(f"  • Total Actions: {len(summary['actions_taken'])}")
        
        return summary
    
    def generate_integrated_report(self, summary: Dict[str, Any]) -> str:
        """
        Generate comprehensive system report.
        
        Args:
            summary: Summary from run_full_cycle
            
        Returns:
            Formatted markdown report
        """
        lines = [
            "# 🤖 Autonomous Agent System Report",
            f"\n**Generated:** {summary['timestamp']}",
            "\n## Executive Summary\n",
        ]
        
        # Health status
        health = summary.get('health', {})
        status_emoji = "✅" if health.get('status') == 'healthy' else "⚠️"
        
        lines.extend([
            f"**System Status:** {status_emoji} {health.get('status', 'unknown').upper()}",
            f"**Total Agents:** {health.get('total_agents', 0)}",
            f"**Total Workload:** {health.get('total_workload', 0)} items",
            f"**Average Utilization:** {health.get('avg_utilization', 0) * 100:.0f}%",
            f"**Active Bottlenecks:** {health.get('bottlenecks', 0)}",
            "\n## Cycle Phases\n"
        ])
        
        # Phase summaries
        phases = summary.get('phases', {})
        
        if 'adaptive_analysis' in phases:
            phase = phases['adaptive_analysis']
            learning = "🧠 Active" if phase.get('learning_active') else "📚 Collecting Data"
            
            lines.extend([
                "### 📊 Phase 1: Adaptive Analysis",
                f"- Specializations Analyzed: {phase.get('metrics_count', 0)}",
                f"- Recommendations Generated: {phase.get('recommendations', 0)}",
                f"- Historical Data Points: {phase.get('history_size', 0)}",
                f"- Learning Status: {learning}",
                ""
            ])
        
        if 'coordination' in phases:
            phase = phases['coordination']
            
            lines.extend([
                "### 🤝 Phase 2: Agent Coordination",
                f"- Total Coordination Actions: {phase.get('actions', 0)}",
                f"- Workload Redistributions: {phase.get('redistributions', 0)}",
                f"- Agents Hibernated: {phase.get('hibernations', 0)}",
                f"- Collaboration Suggestions: {phase.get('collaboration_suggestions', 0)}",
                ""
            ])
        
        if 'spawning' in phases:
            phase = phases['spawning']
            
            lines.extend([
                "### 🌱 Phase 3: Intelligent Spawning (Reactive)",
                f"- Spawn Recommendations: {phase.get('recommendations', 0)}",
                f"- Agents Spawned: {phase.get('spawned', 0)}",
                ""
            ])
        
        if 'predictive_spawning' in phases:
            phase = phases['predictive_spawning']
            
            lines.extend([
                "### 🔮 Phase 3.5: Predictive Spawning (Proactive)",
                f"- Predictive Recommendations: {phase.get('recommendations', 0)}",
                f"- Agents Pre-spawned: {phase.get('spawned', 0)}",
                f"- Prediction History Size: {phase.get('history_size', 0)}",
                ""
            ])
        
        # Detailed actions
        actions = summary.get('actions_taken', [])
        if actions:
            lines.extend([
                "## Detailed Actions\n",
                f"**Total Actions:** {len(actions)}\n"
            ])
            
            # Group by type
            by_type = {}
            for action in actions:
                action_type = action.get('type', 'unknown')
                by_type.setdefault(action_type, []).append(action)
            
            for action_type, type_actions in by_type.items():
                lines.extend([
                    f"### {action_type.replace('_', ' ').title()}",
                    ""
                ])
                
                for i, action in enumerate(type_actions[:10], 1):  # Show first 10
                    if action_type == 'spawn':
                        lines.append(
                            f"{i}. Spawned {action.get('count', 0)} "
                            f"{action.get('specialization', 'unknown')} agent(s) "
                            f"(priority {action.get('priority', 0)}, "
                            f"confidence {action.get('confidence', 0):.0%})"
                        )
                    elif action_type == 'redistribution':
                        lines.append(
                            f"{i}. Redistributed {action.get('specialization', 'unknown')} "
                            f"workload ({action.get('messages', 0)} messages)"
                        )
                    elif action_type == 'hibernation':
                        lines.append(
                            f"{i}. Hibernated {action.get('agent_id', 'unknown')} "
                            f"({action.get('specialization', 'unknown')})"
                        )
                    elif action_type == 'collaboration_suggestion':
                        lines.append(
                            f"{i}. Suggested {action.get('primary', 'unknown')} + "
                            f"{action.get('secondary', 'unknown')}: "
                            f"{action.get('reason', '')}"
                        )
                
                if len(type_actions) > 10:
                    lines.append(f"\n... and {len(type_actions) - 10} more")
                
                lines.append("")
        
        # Footer
        lines.extend([
            "---",
            "*Generated by Autonomous Agent System*",
            "*Enhanced by @accelerate-specialist - Elegant orchestration for autonomous intelligence*"
        ])
        
        return '\n'.join(lines)


def main():
    """CLI interface for integrated autonomous agent system"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Integrated autonomous agent system orchestrator'
    )
    parser.add_argument(
        '--max-spawns', '-m',
        type=int,
        default=5,
        help='Maximum agents to spawn'
    )
    parser.add_argument(
        '--no-hibernation',
        action='store_true',
        help='Disable hibernation of idle agents'
    )
    parser.add_argument(
        '--no-redistribution',
        action='store_true',
        help='Disable workload redistribution'
    )
    parser.add_argument(
        '--output', '-o',
        default='.github/agent-system/autonomous_report.json',
        help='Output file for cycle summary'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Print detailed report'
    )
    
    args = parser.parse_args()
    
    # Create system
    print("🤖 Initializing Autonomous Agent System...")
    system = AutonomousAgentSystem()
    
    # Run full cycle
    summary = system.run_full_cycle(
        max_spawns=args.max_spawns,
        enable_hibernation=not args.no_hibernation,
        enable_redistribution=not args.no_redistribution
    )
    
    # Save summary
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Summary saved to {args.output}")
    
    # Generate report if requested
    if args.report:
        print("\n" + "=" * 80)
        report = system.generate_integrated_report(summary)
        print(report)
        print("=" * 80)
    
    # Exit code based on system health
    health_status = summary.get('health', {}).get('status', 'unknown')
    return 0 if health_status == 'healthy' else 1


if __name__ == '__main__':
    sys.exit(main())
