#!/usr/bin/env python3
"""
Sub-Agent Performance Learner - Learn from Sub-Agent Successes and Failures

Analyzes sub-agent performance to improve future spawning decisions.
Tracks patterns, success rates, and optimal conditions for sub-agent effectiveness.

Created by @create-botter - Inventive and visionary, building adaptive systems.

Features:
- Historical performance tracking
- Pattern recognition for successful spawning
- Failure analysis and root cause identification
- Optimal spawning condition detection
- Adaptive threshold recommendations
- Parent-child performance correlation
- Specialization effectiveness metrics

Part of the Chained autonomous AI ecosystem.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from registry_manager import RegistryManager
except ImportError:
    print("Warning: registry_manager not found")
    RegistryManager = None


@dataclass
class PerformanceInsight:
    """Insight learned from sub-agent performance"""
    insight_type: str  # success_pattern, failure_pattern, threshold_recommendation
    specialization: str
    confidence: float  # 0-1
    description: str
    evidence: List[str]
    recommendation: str
    impact_score: float  # 0-100


@dataclass
class SubAgentAnalysis:
    """Analysis of a sub-agent's performance"""
    agent_id: str
    agent_name: str
    specialization: str
    parent_id: str
    spawned_at: str
    deactivated_at: Optional[str]
    lifetime_hours: float
    workload_at_spawn: float
    issues_resolved: int
    prs_merged: int
    overall_score: float
    success: bool
    failure_reason: Optional[str]


class SubAgentPerformanceLearner:
    """
    Learn from sub-agent performance to improve spawning decisions.
    
    Design inspired by Tesla's inventive vision:
    - Continuous learning from outcomes
    - Pattern recognition across agents
    - Adaptive improvement of spawning logic
    - Data-driven recommendations
    """
    
    # Success criteria
    MIN_SUCCESSFUL_LIFETIME_HOURS = 6
    MIN_SUCCESSFUL_CONTRIBUTIONS = 1
    MIN_SUCCESS_RATE_FOR_INSIGHT = 0.7
    MIN_SAMPLE_SIZE = 5
    
    def __init__(self, registry_manager: Optional['RegistryManager'] = None):
        """Initialize learner with registry manager"""
        self.registry = registry_manager or RegistryManager()
        self.learning_file = Path('.github/agent-system/subagent_learning.json')
        self.learning_data = self._load_learning_data()
    
    def analyze_all_subagents(self) -> List[SubAgentAnalysis]:
        """Analyze all sub-agents (active and deactivated)"""
        all_agents = self.registry.list_agents()  # All statuses
        
        analyses = []
        for agent in all_agents:
            if not agent.get('is_sub_agent', False):
                continue
            
            analysis = self._analyze_subagent(agent)
            if analysis:
                analyses.append(analysis)
        
        return analyses
    
    def learn_from_performance(self) -> List[PerformanceInsight]:
        """Learn insights from sub-agent performance"""
        analyses = self.analyze_all_subagents()
        
        if len(analyses) < self.MIN_SAMPLE_SIZE:
            print(f"⚠️  Insufficient data ({len(analyses)} sub-agents, need {self.MIN_SAMPLE_SIZE})")
            return []
        
        insights = []
        
        # Learn by specialization
        by_specialization = self._group_by_specialization(analyses)
        
        for spec, spec_analyses in by_specialization.items():
            # Success patterns
            success_insights = self._find_success_patterns(spec, spec_analyses)
            insights.extend(success_insights)
            
            # Failure patterns
            failure_insights = self._find_failure_patterns(spec, spec_analyses)
            insights.extend(failure_insights)
            
            # Threshold recommendations
            threshold_insights = self._recommend_thresholds(spec, spec_analyses)
            insights.extend(threshold_insights)
        
        # Parent effectiveness analysis
        parent_insights = self._analyze_parent_effectiveness(analyses)
        insights.extend(parent_insights)
        
        # Save insights to learning data
        self._update_learning_data(insights)
        
        return insights
    
    def get_spawning_recommendations(
        self, 
        specialization: str,
        current_workload: float
    ) -> Dict[str, Any]:
        """
        Get data-driven spawning recommendations based on learned patterns.
        
        Args:
            specialization: Specialization to spawn
            current_workload: Current workload per agent
        
        Returns:
            Dictionary with recommendations and confidence scores
        """
        spec_data = self.learning_data.get('by_specialization', {}).get(specialization, {})
        
        if not spec_data:
            return {
                'should_spawn': None,
                'confidence': 0.0,
                'reason': 'No historical data available',
                'recommended_count': 1
            }
        
        # Check success rate
        success_rate = spec_data.get('success_rate', 0.5)
        avg_workload_at_spawn = spec_data.get('avg_workload_at_spawn', 5.0)
        optimal_threshold = spec_data.get('optimal_threshold', 5.0)
        
        # Decision logic
        should_spawn = current_workload >= optimal_threshold
        confidence = success_rate if should_spawn else 0.5
        
        # Recommend count based on workload
        if current_workload >= optimal_threshold * 2:
            recommended_count = 3
        elif current_workload >= optimal_threshold * 1.5:
            recommended_count = 2
        else:
            recommended_count = 1
        
        reason_parts = []
        if should_spawn:
            reason_parts.append(f"Workload ({current_workload:.1f}) exceeds optimal threshold ({optimal_threshold:.1f})")
            reason_parts.append(f"Historical success rate: {success_rate*100:.1f}%")
        else:
            reason_parts.append(f"Workload ({current_workload:.1f}) below threshold ({optimal_threshold:.1f})")
        
        return {
            'should_spawn': should_spawn,
            'confidence': round(confidence, 3),
            'reason': '. '.join(reason_parts),
            'recommended_count': recommended_count,
            'success_rate': round(success_rate, 3),
            'optimal_threshold': round(optimal_threshold, 2)
        }
    
    def _analyze_subagent(self, agent: Dict[str, Any]) -> Optional[SubAgentAnalysis]:
        """Analyze a single sub-agent"""
        try:
            spawned_at = agent.get('spawned_at')
            if not spawned_at:
                return None
            
            spawn_time = datetime.fromisoformat(spawned_at.replace('Z', '+00:00'))
            
            # Calculate lifetime
            if agent.get('status') == 'deactivated':
                deactivated_at = agent.get('deactivated_at')
                if deactivated_at:
                    deactivate_time = datetime.fromisoformat(deactivated_at.replace('Z', '+00:00'))
                else:
                    deactivate_time = datetime.now(spawn_time.tzinfo)
            else:
                deactivate_time = datetime.now(spawn_time.tzinfo)
                deactivated_at = None
            
            lifetime_hours = (deactivate_time - spawn_time).total_seconds() / 3600
            
            # Get metrics
            metrics = agent.get('metrics', {})
            issues_resolved = metrics.get('issues_resolved', 0)
            prs_merged = metrics.get('prs_merged', 0)
            overall_score = metrics.get('overall_score', 0.0)
            
            # Workload at spawn (from spawn_reason if available)
            workload_at_spawn = self._extract_workload_from_spawn_reason(agent)
            
            # Determine success
            contributions = issues_resolved + prs_merged
            success = (
                lifetime_hours >= self.MIN_SUCCESSFUL_LIFETIME_HOURS and
                contributions >= self.MIN_SUCCESSFUL_CONTRIBUTIONS and
                overall_score >= 0.4
            )
            
            # Determine failure reason
            failure_reason = None
            if not success:
                if lifetime_hours < self.MIN_SUCCESSFUL_LIFETIME_HOURS:
                    failure_reason = "short_lifetime"
                elif contributions == 0:
                    failure_reason = "no_contributions"
                else:
                    failure_reason = "low_quality"
            
            return SubAgentAnalysis(
                agent_id=agent['id'],
                agent_name=agent.get('name', 'Unknown'),
                specialization=agent.get('specialization', 'unknown'),
                parent_id=agent.get('parent_agent_id', 'unknown'),
                spawned_at=spawned_at,
                deactivated_at=deactivated_at,
                lifetime_hours=round(lifetime_hours, 2),
                workload_at_spawn=workload_at_spawn,
                issues_resolved=issues_resolved,
                prs_merged=prs_merged,
                overall_score=round(overall_score, 3),
                success=success,
                failure_reason=failure_reason
            )
        except Exception as e:
            print(f"⚠️  Error analyzing sub-agent {agent.get('id', 'unknown')}: {e}")
            return None
    
    def _extract_workload_from_spawn_reason(self, agent: Dict[str, Any]) -> float:
        """
        Extract workload from spawn_reason field.
        
        Uses regex pattern matching for robustness.
        Format: "High workload: 8.5 items/agent" or similar variations
        """
        spawn_reason = agent.get('spawn_reason', '')
        
        # Try to parse workload from reason text using regex
        try:
            import re
            # Pattern: Look for number followed by "items/agent"
            pattern = r'(\d+\.?\d*)\s*items?/agent'
            match = re.search(pattern, spawn_reason, re.IGNORECASE)
            if match:
                return float(match.group(1))
        except Exception:
            pass
        
        return 5.0  # Default fallback
    
    def _group_by_specialization(
        self, 
        analyses: List[SubAgentAnalysis]
    ) -> Dict[str, List[SubAgentAnalysis]]:
        """Group analyses by specialization"""
        grouped = defaultdict(list)
        for analysis in analyses:
            grouped[analysis.specialization].append(analysis)
        return dict(grouped)
    
    def _find_success_patterns(
        self, 
        specialization: str,
        analyses: List[SubAgentAnalysis]
    ) -> List[PerformanceInsight]:
        """Find patterns in successful sub-agents"""
        successful = [a for a in analyses if a.success]
        
        if len(successful) < 3:
            return []
        
        insights = []
        
        # Success rate
        success_rate = len(successful) / len(analyses)
        
        if success_rate >= self.MIN_SUCCESS_RATE_FOR_INSIGHT:
            # Analyze successful workload range
            workloads = [a.workload_at_spawn for a in successful]
            avg_workload = statistics.mean(workloads)
            
            evidence = [
                f"{len(successful)}/{len(analyses)} sub-agents successful",
                f"Average workload at spawn: {avg_workload:.1f}",
                f"Success rate: {success_rate*100:.1f}%"
            ]
            
            insight = PerformanceInsight(
                insight_type='success_pattern',
                specialization=specialization,
                confidence=success_rate,
                description=f"Sub-agents for {specialization} are highly successful",
                evidence=evidence,
                recommendation=f"Continue spawning at workload ~{avg_workload:.1f}",
                impact_score=success_rate * 100
            )
            insights.append(insight)
        
        return insights
    
    def _find_failure_patterns(
        self, 
        specialization: str,
        analyses: List[SubAgentAnalysis]
    ) -> List[PerformanceInsight]:
        """Find patterns in failed sub-agents"""
        failed = [a for a in analyses if not a.success]
        
        if len(failed) < 2:
            return []
        
        insights = []
        
        # Analyze failure reasons
        failure_reasons = defaultdict(int)
        for analysis in failed:
            if analysis.failure_reason:
                failure_reasons[analysis.failure_reason] += 1
        
        # Identify primary failure mode
        if failure_reasons:
            primary_reason = max(failure_reasons.items(), key=lambda x: x[1])
            reason_name, count = primary_reason
            
            evidence = [
                f"{len(failed)}/{len(analyses)} sub-agents failed",
                f"Primary failure: {reason_name} ({count} cases)",
                f"Failure rate: {len(failed)/len(analyses)*100:.1f}%"
            ]
            
            # Recommendation based on failure type
            if reason_name == "short_lifetime":
                recommendation = "Increase spawning threshold to ensure longer-term need"
            elif reason_name == "no_contributions":
                recommendation = "Improve sub-agent assignment or reduce idle time"
            else:
                recommendation = "Review sub-agent capabilities and training"
            
            insight = PerformanceInsight(
                insight_type='failure_pattern',
                specialization=specialization,
                confidence=count / len(failed),
                description=f"Sub-agents often fail due to {reason_name}",
                evidence=evidence,
                recommendation=recommendation,
                impact_score=len(failed) / len(analyses) * 80
            )
            insights.append(insight)
        
        return insights
    
    def _recommend_thresholds(
        self, 
        specialization: str,
        analyses: List[SubAgentAnalysis]
    ) -> List[PerformanceInsight]:
        """Recommend optimal spawning thresholds"""
        if len(analyses) < self.MIN_SAMPLE_SIZE:
            return []
        
        successful = [a for a in analyses if a.success]
        
        if not successful:
            return []
        
        # Find optimal workload threshold
        workloads = [a.workload_at_spawn for a in successful]
        optimal_threshold = statistics.median(workloads)
        
        evidence = [
            f"Analyzed {len(successful)} successful spawns",
            f"Median workload at spawn: {optimal_threshold:.1f}",
            f"Range: {min(workloads):.1f} - {max(workloads):.1f}"
        ]
        
        insight = PerformanceInsight(
            insight_type='threshold_recommendation',
            specialization=specialization,
            confidence=len(successful) / max(len(analyses), 1),  # Normalized 0-1 (always <= 1.0)
            description=f"Optimal spawning threshold for {specialization}",
            evidence=evidence,
            recommendation=f"Set threshold to {optimal_threshold:.1f} items/agent",
            impact_score=70
        )
        
        return [insight]
    
    def _analyze_parent_effectiveness(
        self, 
        analyses: List[SubAgentAnalysis]
    ) -> List[PerformanceInsight]:
        """Analyze which parents produce successful sub-agents"""
        if len(analyses) < self.MIN_SAMPLE_SIZE:
            return []
        
        # Group by parent
        by_parent = defaultdict(list)
        for analysis in analyses:
            by_parent[analysis.parent_id].append(analysis)
        
        insights = []
        
        for parent_id, parent_analyses in by_parent.items():
            if len(parent_analyses) < 2:
                continue
            
            successful = [a for a in parent_analyses if a.success]
            success_rate = len(successful) / len(parent_analyses)
            
            if success_rate >= 0.8:  # High success parent
                parent_agent = self.registry.get_agent(parent_id)
                parent_name = parent_agent.get('name', 'Unknown') if parent_agent else 'Unknown'
                
                evidence = [
                    f"Parent: {parent_name} ({parent_id})",
                    f"{len(successful)}/{len(parent_analyses)} sub-agents successful",
                    f"Success rate: {success_rate*100:.1f}%"
                ]
                
                insight = PerformanceInsight(
                    insight_type='success_pattern',
                    specialization='parent_effectiveness',
                    confidence=success_rate,
                    description=f"Parent {parent_name} produces highly effective sub-agents",
                    evidence=evidence,
                    recommendation=f"Prioritize {parent_name} for future sub-agent spawning",
                    impact_score=success_rate * 90
                )
                insights.append(insight)
        
        return insights
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from file"""
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading learning data: {e}")
        
        return {
            'by_specialization': {},
            'by_parent': {},
            'insights': [],
            'last_updated': None
        }
    
    def _update_learning_data(self, insights: List[PerformanceInsight]) -> None:
        """Update learning data with new insights"""
        # Group insights by specialization
        by_spec = defaultdict(dict)
        
        for insight in insights:
            if insight.specialization == 'parent_effectiveness':
                continue
            
            if insight.insight_type == 'threshold_recommendation':
                # Store threshold value - extract from recommendation text
                # Format expected: "Set threshold to X.X items/agent"
                try:
                    import re
                    match = re.search(r'threshold to (\d+\.?\d*)', insight.recommendation)
                    if match:
                        threshold = float(match.group(1))
                        by_spec[insight.specialization]['optimal_threshold'] = threshold
                except Exception as e:
                    print(f"⚠️  Could not extract threshold from recommendation: {e}")
                    pass
            
            # Calculate success rate
            if insight.insight_type == 'success_pattern':
                by_spec[insight.specialization]['success_rate'] = insight.confidence
        
        # Update learning data
        self.learning_data['by_specialization'].update(by_spec)
        self.learning_data['insights'] = [
            {
                'type': i.insight_type,
                'specialization': i.specialization,
                'confidence': i.confidence,
                'description': i.description,
                'recommendation': i.recommendation,
                'timestamp': datetime.now().isoformat()
            }
            for i in insights
        ]
        self.learning_data['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        self.learning_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.learning_file, 'w') as f:
            json.dump(self.learning_data, f, indent=2)


def main():
    """CLI interface for performance learning"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sub-Agent Performance Learner'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze all sub-agents'
    )
    parser.add_argument(
        '--learn',
        action='store_true',
        help='Learn insights from performance'
    )
    parser.add_argument(
        '--recommend',
        help='Get spawning recommendations for specialization'
    )
    parser.add_argument(
        '--workload',
        type=float,
        default=5.0,
        help='Current workload for recommendation'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    learner = SubAgentPerformanceLearner()
    
    if args.analyze:
        analyses = learner.analyze_all_subagents()
        
        if args.format == 'json':
            output = [asdict(a) for a in analyses]
            print(json.dumps(output, indent=2))
        else:
            print(f"\n📊 Sub-Agent Performance Analysis")
            print("=" * 60)
            print(f"Total sub-agents analyzed: {len(analyses)}")
            
            successful = [a for a in analyses if a.success]
            print(f"Successful: {len(successful)} ({len(successful)/len(analyses)*100:.1f}%)")
            
            for analysis in analyses[:10]:  # Show first 10
                print(f"\n{analysis.agent_name} ({analysis.specialization})")
                print(f"  Lifetime: {analysis.lifetime_hours:.1f}h")
                print(f"  Contributions: {analysis.issues_resolved + analysis.prs_merged}")
                print(f"  Success: {'✅' if analysis.success else '❌'}")
                if analysis.failure_reason:
                    print(f"  Failure: {analysis.failure_reason}")
    
    elif args.learn:
        insights = learner.learn_from_performance()
        
        if args.format == 'json':
            output = [asdict(i) for i in insights]
            print(json.dumps(output, indent=2))
        else:
            print(f"\n🧠 Learning Insights")
            print("=" * 60)
            print(f"Total insights: {len(insights)}\n")
            
            for insight in insights:
                print(f"📌 {insight.description}")
                print(f"   Type: {insight.insight_type}")
                print(f"   Specialization: {insight.specialization}")
                print(f"   Confidence: {insight.confidence*100:.1f}%")
                print(f"   Impact: {insight.impact_score:.1f}/100")
                print(f"   💡 {insight.recommendation}")
                print()
    
    elif args.recommend:
        recommendation = learner.get_spawning_recommendations(
            args.recommend,
            args.workload
        )
        
        if args.format == 'json':
            print(json.dumps(recommendation, indent=2))
        else:
            print(f"\n🎯 Spawning Recommendation: {args.recommend}")
            print("=" * 60)
            print(f"Current Workload: {args.workload:.1f}")
            print(f"Should Spawn: {recommendation['should_spawn']}")
            print(f"Confidence: {recommendation['confidence']*100:.1f}%")
            print(f"Recommended Count: {recommendation['recommended_count']}")
            print(f"\n💬 {recommendation['reason']}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
