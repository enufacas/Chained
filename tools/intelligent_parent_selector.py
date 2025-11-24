#!/usr/bin/env python3
"""
Intelligent Parent Selector - AI-Driven Parent Agent Selection for Sub-Agents

Selects optimal parent agents for sub-agent spawning using multi-criteria
scoring algorithm. Considers performance history, specialization match,
current workload, and collaboration potential.

Created by @create-guru - Inventive and visionary infrastructure development.

Features:
- Multi-criteria parent scoring (performance, workload, compatibility)
- Historical performance analysis
- Workload-aware selection (avoid overloaded parents)
- Specialization matching optimization
- Agent compatibility scoring
- Adaptive weight adjustment based on system state

Part of the Chained autonomous AI ecosystem.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from registry_manager import RegistryManager
except ImportError:
    print("Warning: registry_manager not found")
    RegistryManager = None


@dataclass
class ParentScore:
    """Score for a potential parent agent"""
    agent_id: str
    agent_name: str
    specialization: str
    total_score: float  # 0-100
    performance_score: float  # 0-100
    workload_score: float  # 0-100
    compatibility_score: float  # 0-100
    experience_score: float  # 0-100
    success_rate: float  # 0-1
    current_workload: int
    sub_agents_count: int
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class IntelligentParentSelector:
    """
    Selects optimal parent agents for sub-agent spawning.
    
    Design inspired by Tesla's inventive approach:
    - Multiple scoring criteria for holistic evaluation
    - Adaptive weighting based on system state
    - Historical performance analysis
    - Workload-aware selection
    """
    
    # Default scoring weights (can be adjusted dynamically)
    DEFAULT_WEIGHTS = {
        'performance': 0.35,    # 35% - Historical success
        'workload': 0.25,       # 25% - Current capacity
        'compatibility': 0.20,  # 20% - Specialization match
        'experience': 0.20      # 20% - Agent maturity
    }
    
    # Thresholds
    MAX_SUB_AGENTS_PER_PARENT = 5
    OPTIMAL_WORKLOAD_RANGE = (2, 8)  # Items per agent
    MIN_PARENT_EXPERIENCE_HOURS = 24  # Minimum age for parent
    
    def __init__(self, registry_manager: Optional['RegistryManager'] = None):
        """Initialize selector with registry manager"""
        self.registry = registry_manager or RegistryManager()
        self.weights = self.DEFAULT_WEIGHTS.copy()
    
    def select_parent(
        self, 
        specialization: str,
        required_traits: Optional[Dict[str, Any]] = None,
        exclude_agents: Optional[List[str]] = None,
        top_n: int = 1
    ) -> List[ParentScore]:
        """
        Select optimal parent agent(s) for sub-agent spawning.
        
        Args:
            specialization: Required specialization for parent
            required_traits: Optional specific traits needed
            exclude_agents: List of agent IDs to exclude from consideration
            top_n: Number of top candidates to return
        
        Returns:
            List of ParentScore objects, sorted by total_score (highest first)
        """
        # Get all active agents with matching specialization
        candidates = self._get_candidates(specialization, exclude_agents or [])
        
        if not candidates:
            print(f"⚠️  No suitable parent candidates found for {specialization}")
            return []
        
        # Score each candidate
        scores = []
        for agent in candidates:
            score = self._score_candidate(agent, specialization, required_traits)
            if score:
                scores.append(score)
        
        # Sort by total score (descending)
        scores.sort(key=lambda s: s.total_score, reverse=True)
        
        # Return top N
        return scores[:top_n]
    
    def _get_candidates(
        self, 
        specialization: str, 
        exclude: List[str]
    ) -> List[Dict[str, Any]]:
        """Get potential parent agent candidates"""
        all_agents = self.registry.list_agents(status='active')
        
        candidates = []
        for agent in all_agents:
            # Skip excluded agents
            if agent['id'] in exclude:
                continue
            
            # Must match specialization
            if agent.get('specialization') != specialization:
                continue
            
            # Must not be a sub-agent itself
            if agent.get('is_sub_agent', False):
                continue
            
            # Must meet minimum experience
            if not self._meets_experience_requirement(agent):
                continue
            
            # Must not be overloaded with sub-agents
            sub_agent_count = self._count_sub_agents(agent['id'])
            if sub_agent_count >= self.MAX_SUB_AGENTS_PER_PARENT:
                continue
            
            candidates.append(agent)
        
        return candidates
    
    def _score_candidate(
        self,
        agent: Dict[str, Any],
        specialization: str,
        required_traits: Optional[Dict[str, Any]]
    ) -> Optional[ParentScore]:
        """Score a candidate parent agent"""
        try:
            # Calculate individual scores
            performance = self._calculate_performance_score(agent)
            workload = self._calculate_workload_score(agent)
            compatibility = self._calculate_compatibility_score(agent, required_traits)
            experience = self._calculate_experience_score(agent)
            
            # Calculate weighted total
            total = (
                performance * self.weights['performance'] +
                workload * self.weights['workload'] +
                compatibility * self.weights['compatibility'] +
                experience * self.weights['experience']
            )
            
            # Get additional metrics
            metrics = agent.get('metrics', {})
            success_rate = self._calculate_success_rate(metrics)
            current_workload = self._estimate_current_workload(agent)
            sub_agents_count = self._count_sub_agents(agent['id'])
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                total, performance, workload, compatibility, experience
            )
            
            return ParentScore(
                agent_id=agent['id'],
                agent_name=agent.get('name', 'Unknown'),
                specialization=specialization,
                total_score=round(total, 2),
                performance_score=round(performance, 2),
                workload_score=round(workload, 2),
                compatibility_score=round(compatibility, 2),
                experience_score=round(experience, 2),
                success_rate=round(success_rate, 3),
                current_workload=current_workload,
                sub_agents_count=sub_agents_count,
                recommendation=recommendation
            )
        except Exception as e:
            print(f"⚠️  Error scoring candidate {agent.get('id', 'unknown')}: {e}")
            return None
    
    def _calculate_performance_score(self, agent: Dict[str, Any]) -> float:
        """Calculate performance score based on metrics (0-100)"""
        metrics = agent.get('metrics', {})
        
        # Overall score (if available)
        overall = metrics.get('overall_score', 0.5) * 100
        
        # Code quality
        quality = metrics.get('code_quality_score', 0.5) * 100
        
        # Success indicators
        resolved = metrics.get('issues_resolved', 0)
        merged = metrics.get('prs_merged', 0)
        reviews = metrics.get('reviews_given', 0)
        
        # Activity bonus (more activity = more reliable)
        activity_bonus = min((resolved + merged + reviews) / 10 * 10, 20)
        
        # Combine scores
        base_score = (overall * 0.6 + quality * 0.4)
        final_score = min(base_score + activity_bonus, 100)
        
        return final_score
    
    def _calculate_workload_score(self, agent: Dict[str, Any]) -> float:
        """Calculate workload score - higher if not overloaded (0-100)"""
        current_workload = self._estimate_current_workload(agent)
        sub_agents = self._count_sub_agents(agent['id'])
        
        # Penalize if overloaded
        optimal_min, optimal_max = self.OPTIMAL_WORKLOAD_RANGE
        
        if optimal_min <= current_workload <= optimal_max:
            workload_score = 100
        elif current_workload < optimal_min:
            # Underutilized - slight penalty
            workload_score = 80 + (current_workload / optimal_min) * 20
        else:
            # Overloaded - significant penalty
            penalty = min((current_workload - optimal_max) / optimal_max * 50, 60)
            workload_score = max(100 - penalty, 20)
        
        # Penalize if already has many sub-agents
        sub_agent_penalty = (sub_agents / self.MAX_SUB_AGENTS_PER_PARENT) * 30
        
        final_score = max(workload_score - sub_agent_penalty, 0)
        return final_score
    
    def _calculate_compatibility_score(
        self, 
        agent: Dict[str, Any],
        required_traits: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate compatibility score based on traits (0-100)"""
        if not required_traits:
            return 85  # Default good compatibility
        
        agent_traits = agent.get('traits', {})
        
        # Compare traits if specified
        trait_matches = 0
        trait_count = 0
        
        for trait_key, required_value in required_traits.items():
            if trait_key in agent_traits:
                agent_value = agent_traits[trait_key]
                # Calculate similarity (for numeric traits)
                if isinstance(agent_value, (int, float)) and isinstance(required_value, (int, float)):
                    diff = abs(agent_value - required_value)
                    match = max(100 - diff, 0)
                    trait_matches += match
                    trait_count += 1
                elif agent_value == required_value:
                    trait_matches += 100
                    trait_count += 1
        
        if trait_count > 0:
            return trait_matches / trait_count
        
        return 85  # Default if no comparable traits
    
    def _calculate_experience_score(self, agent: Dict[str, Any]) -> float:
        """Calculate experience score based on age (0-100)"""
        spawned_at = agent.get('spawned_at')
        if not spawned_at:
            return 50  # Unknown age
        
        try:
            spawn_time = datetime.fromisoformat(spawned_at.replace('Z', '+00:00'))
            age_hours = (datetime.now(spawn_time.tzinfo) - spawn_time).total_seconds() / 3600
            
            # Score increases with age, plateaus after 30 days
            if age_hours < self.MIN_PARENT_EXPERIENCE_HOURS:
                return 20  # Too young
            elif age_hours < 168:  # 1 week
                return 50 + (age_hours / 168) * 30
            elif age_hours < 720:  # 30 days
                return 80 + (age_hours / 720) * 20
            else:
                return 100  # Mature agent
        except Exception:
            return 50
    
    def _calculate_success_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate success rate from metrics (0-1)"""
        resolved = metrics.get('issues_resolved', 0)
        merged = metrics.get('prs_merged', 0)
        total_work = resolved + merged
        
        if total_work == 0:
            return 0.5  # Neutral for new agents
        
        # Estimate success rate from overall score
        overall = metrics.get('overall_score', 0.5)
        
        return overall
    
    def _estimate_current_workload(self, agent: Dict[str, Any]) -> int:
        """Estimate current workload for an agent"""
        # In a real implementation, this would query GitHub issues/PRs
        # For now, use a simple estimate based on metrics
        metrics = agent.get('metrics', {})
        
        # Estimate based on recent activity
        resolved = metrics.get('issues_resolved', 0)
        merged = metrics.get('prs_merged', 0)
        
        # Assume some ongoing work (simplified)
        estimated = min(resolved + merged, 10) // 2
        return max(estimated, 0)
    
    def _count_sub_agents(self, parent_id: str) -> int:
        """Count active sub-agents for a parent"""
        all_agents = self.registry.list_agents(status='active')
        
        count = 0
        for agent in all_agents:
            if agent.get('parent_agent_id') == parent_id:
                count += 1
        
        return count
    
    def _meets_experience_requirement(self, agent: Dict[str, Any]) -> bool:
        """Check if agent meets minimum experience requirement"""
        spawned_at = agent.get('spawned_at')
        if not spawned_at:
            return True  # Benefit of doubt for unknown
        
        try:
            spawn_time = datetime.fromisoformat(spawned_at.replace('Z', '+00:00'))
            age_hours = (datetime.now(spawn_time.tzinfo) - spawn_time).total_seconds() / 3600
            return age_hours >= self.MIN_PARENT_EXPERIENCE_HOURS
        except Exception:
            return True
    
    def _generate_recommendation(
        self,
        total: float,
        performance: float,
        workload: float,
        compatibility: float,
        experience: float
    ) -> str:
        """Generate human-readable recommendation"""
        if total >= 85:
            return "Excellent parent candidate"
        elif total >= 70:
            return "Good parent candidate"
        elif total >= 55:
            return "Acceptable parent candidate"
        elif total >= 40:
            # Identify weakness
            scores = {
                'performance': performance,
                'workload': workload,
                'compatibility': compatibility,
                'experience': experience
            }
            weakest = min(scores.items(), key=lambda x: x[1])
            return f"Marginal - low {weakest[0]}"
        else:
            return "Not recommended"
    
    def adjust_weights(self, system_state: Dict[str, Any]) -> None:
        """
        Dynamically adjust scoring weights based on system state.
        
        Args:
            system_state: Dictionary with keys like 'high_load', 'new_system', etc.
        """
        # Reset to defaults
        self.weights = self.DEFAULT_WEIGHTS.copy()
        
        # Adjust based on system state
        if system_state.get('high_load', False):
            # Prioritize workload capacity in high load
            self.weights['workload'] = 0.40
            self.weights['performance'] = 0.30
            self.weights['compatibility'] = 0.15
            self.weights['experience'] = 0.15
        
        if system_state.get('new_system', False):
            # Prioritize experience in new systems
            self.weights['experience'] = 0.35
            self.weights['performance'] = 0.35
            self.weights['workload'] = 0.20
            self.weights['compatibility'] = 0.10
        
        if system_state.get('quality_focus', False):
            # Prioritize performance/quality
            self.weights['performance'] = 0.50
            self.weights['compatibility'] = 0.25
            self.weights['experience'] = 0.15
            self.weights['workload'] = 0.10


def main():
    """CLI interface for parent selection"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Intelligent Parent Agent Selector'
    )
    parser.add_argument(
        'specialization',
        help='Required parent specialization'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=3,
        help='Number of top candidates to return'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    parser.add_argument(
        '--exclude',
        help='Comma-separated agent IDs to exclude'
    )
    
    args = parser.parse_args()
    
    # Parse exclusions
    exclude_list = []
    if args.exclude:
        exclude_list = [x.strip() for x in args.exclude.split(',')]
    
    # Select parents
    selector = IntelligentParentSelector()
    parents = selector.select_parent(
        specialization=args.specialization,
        exclude_agents=exclude_list,
        top_n=args.top_n
    )
    
    if args.format == 'json':
        output = {
            'specialization': args.specialization,
            'candidates': [p.to_dict() for p in parents],
            'count': len(parents)
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\n🎯 Parent Selection for: {args.specialization}")
        print("=" * 60)
        
        if not parents:
            print("⚠️  No suitable parent candidates found")
        else:
            for i, parent in enumerate(parents, 1):
                print(f"\n#{i} {parent.agent_name}")
                print(f"   ID: {parent.agent_id}")
                print(f"   Total Score: {parent.total_score}/100")
                print(f"   - Performance: {parent.performance_score}/100")
                print(f"   - Workload: {parent.workload_score}/100")
                print(f"   - Compatibility: {parent.compatibility_score}/100")
                print(f"   - Experience: {parent.experience_score}/100")
                print(f"   Current Workload: {parent.current_workload} items")
                print(f"   Sub-Agents: {parent.sub_agents_count}")
                print(f"   Success Rate: {parent.success_rate * 100:.1f}%")
                print(f"   Recommendation: {parent.recommendation}")


if __name__ == '__main__':
    main()
