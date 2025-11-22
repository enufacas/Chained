#!/usr/bin/env python3
"""
🌌 Universal Truth Evaluator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A visionary infrastructure for discovering, validating, and tracking fundamental
truths that govern the Chained autonomous AI ecosystem.

Inspired by Nikola Tesla's approach to discovering universal principles through
observation, experimentation, and pattern recognition.

Architecture:
    Truth Discovery → Validation → Evolution Tracking → Insight Generation

Core Principles:
    • Empirical observation trumps assumption
    • Patterns reveal underlying laws
    • Truth evolves with system complexity
    • Multiple perspectives validate universality

@author: create-guru (Tesla-inspired infrastructure builder)
@version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import re


@dataclass
class UniversalTruth:
    """Represents a discovered universal truth about the system."""
    truth_id: str
    category: str  # agent_behavior, system_dynamics, collaboration, evolution
    statement: str
    confidence: float  # 0.0 to 1.0
    evidence_count: int
    first_observed: str
    last_validated: str
    supporting_data: List[Dict[str, Any]]
    counter_examples: List[Dict[str, Any]]
    evolution_history: List[Dict[str, Any]]
    related_truths: List[str]
    
    def is_stable(self) -> bool:
        """Truth is stable if it hasn't been challenged in recent validations."""
        return len(self.counter_examples) == 0 or self.confidence > 0.8
    
    def needs_revalidation(self, days: int = 7) -> bool:
        """Check if truth needs revalidation based on time."""
        last_val = datetime.fromisoformat(self.last_validated)
        return (datetime.now() - last_val).days > days


class UniversalTruthEvaluator:
    """
    🔮 Discovers and validates fundamental truths about the autonomous AI ecosystem.
    
    Like Tesla discovering the laws of electromagnetism, this system discovers
    the laws governing agent behavior, collaboration patterns, and system evolution.
    """
    
    def __init__(self, repo_root: Path = None):
        """Initialize the Universal Truth Evaluator."""
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.world_dir = self.repo_root / "world"
        self.learnings_dir = self.repo_root / "learnings"
        self.analysis_dir = self.repo_root / "analysis"
        self.truths_file = self.repo_root / "world" / "universal_truths.json"
        
        self.truths: Dict[str, UniversalTruth] = {}
        self._load_truths()
        
    def _load_truths(self):
        """Load existing universal truths from storage."""
        if self.truths_file.exists():
            with open(self.truths_file, 'r') as f:
                data = json.load(f)
                for truth_id, truth_data in data.get('truths', {}).items():
                    self.truths[truth_id] = UniversalTruth(**truth_data)
    
    def _save_truths(self):
        """Persist universal truths to storage."""
        data = {
            'version': '1.0.0',
            'last_updated': datetime.now().isoformat(),
            'total_truths': len(self.truths),
            'truths': {tid: asdict(truth) for tid, truth in self.truths.items()}
        }
        self.truths_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.truths_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def discover_truths_from_agents(self) -> List[UniversalTruth]:
        """
        🤖 Discover universal truths about agent behavior.
        
        Analyzes agent performance, patterns, and evolution to extract
        fundamental principles governing agent success and failure.
        """
        truths = []
        
        # Load world state
        world_state_file = self.world_dir / "world_state.json"
        if not world_state_file.exists():
            return truths
        
        with open(world_state_file, 'r') as f:
            world_state = json.load(f)
        
        agents = world_state.get('agents', [])
        if not agents:
            return truths
        
        # Truth 1: Score Distribution Law
        scores = [a.get('metrics', {}).get('overall_score', 0) for a in agents]
        avg_score = sum(scores) / len(scores) if scores else 0
        high_performers = [s for s in scores if s > 0.7]
        low_performers = [s for s in scores if s < 0.4]
        
        if len(high_performers) > 0:
            truth = self._create_or_update_truth(
                'agent_performance_distribution',
                'agent_behavior',
                f"Agent performance follows a natural distribution with {len(high_performers)/len(scores)*100:.1f}% high performers (>0.7) and {len(low_performers)/len(scores)*100:.1f}% low performers (<0.4). Average score: {avg_score:.3f}",
                confidence=0.85,
                evidence={'scores': scores, 'sample_size': len(agents)}
            )
            truths.append(truth)
        
        # Truth 2: Specialization Diversity Law
        specializations = [a.get('specialization', 'unknown') for a in agents]
        unique_specs = len(set(specializations))
        
        truth = self._create_or_update_truth(
            'specialization_diversity',
            'system_dynamics',
            f"Ecosystem maintains {unique_specs} distinct specializations across {len(agents)} agents, suggesting diversity is a core system property (diversity ratio: {unique_specs/len(agents):.2f})",
            confidence=0.9,
            evidence={'specializations': list(set(specializations)), 'total_agents': len(agents)}
        )
        truths.append(truth)
        
        # Truth 3: Geographic Distribution Law
        regions = [a.get('location_region_id', 'unknown') for a in agents]
        unique_regions = len(set(regions))
        
        if unique_regions > 1:
            truth = self._create_or_update_truth(
                'geographic_distribution',
                'system_dynamics',
                f"Agents naturally distribute across {unique_regions} geographic regions, indicating spatial organization emerges from system dynamics",
                confidence=0.75,
                evidence={'regions': list(set(regions)), 'distribution': dict(zip(*zip(*[(r, regions.count(r)) for r in set(regions)])))}
            )
            truths.append(truth)
        
        # Truth 4: Status Patterns Law
        statuses = [a.get('status', 'unknown') for a in agents]
        status_counts = {s: statuses.count(s) for s in set(statuses)}
        dominant_status = max(status_counts.items(), key=lambda x: x[1])[0]
        
        truth = self._create_or_update_truth(
            'agent_status_equilibrium',
            'agent_behavior',
            f"System tends toward equilibrium with '{dominant_status}' as dominant status ({status_counts[dominant_status]/len(agents)*100:.1f}% of agents)",
            confidence=0.7,
            evidence={'status_distribution': status_counts}
        )
        truths.append(truth)
        
        return truths
    
    def discover_truths_from_learnings(self) -> List[UniversalTruth]:
        """
        📚 Discover universal truths about learning patterns.
        
        Analyzes accumulated learnings to extract principles about
        knowledge acquisition and system evolution.
        """
        truths = []
        
        # Analyze learning files
        learning_files = list(self.learnings_dir.glob('*.json'))
        if not learning_files:
            return truths
        
        # Truth 5: Learning Accumulation Rate
        learning_dates = []
        for lf in learning_files:
            # Extract date from filename
            date_match = re.search(r'(\d{8})', lf.name)
            if date_match:
                learning_dates.append(date_match.group(1))
        
        if len(learning_dates) > 1:
            learning_dates.sort()
            recent_count = sum(1 for d in learning_dates if d >= (datetime.now() - timedelta(days=7)).strftime('%Y%m%d'))
            
            truth = self._create_or_update_truth(
                'learning_accumulation_rate',
                'evolution',
                f"System accumulates knowledge at {recent_count} learnings per week, indicating continuous learning is a fundamental property",
                confidence=0.85,
                evidence={'total_learnings': len(learning_dates), 'recent_count': recent_count}
            )
            truths.append(truth)
        
        # Truth 6: Knowledge Graph Connectivity
        kg_file = self.learnings_dir / "discussions" / "knowledge_graph.json"
        if kg_file.exists():
            with open(kg_file, 'r') as f:
                kg = json.load(f)
                insights = kg.get('insights', {})
                connections = kg.get('connections', [])
                
                if insights:
                    avg_connections = len(connections) / len(insights) if insights else 0
                    
                    truth = self._create_or_update_truth(
                        'knowledge_interconnectedness',
                        'evolution',
                        f"Knowledge naturally forms interconnected networks with average {avg_connections:.1f} connections per insight, revealing emergent structure",
                        confidence=0.8,
                        evidence={'total_insights': len(insights), 'total_connections': len(connections)}
                    )
                    truths.append(truth)
        
        return truths
    
    def discover_truths_from_collaboration(self) -> List[UniversalTruth]:
        """
        🤝 Discover universal truths about agent collaboration.
        
        Analyzes collaboration patterns to extract principles about
        multi-agent dynamics and emergent cooperation.
        """
        truths = []
        
        collab_file = self.world_dir / "agent_collaborations.json"
        if not collab_file.exists():
            return truths
        
        with open(collab_file, 'r') as f:
            collabs = json.load(f)
        
        active_collabs = collabs.get('collaborations', {})
        if not active_collabs:
            return truths
        
        # Truth 7: Collaboration Frequency Law
        collaboration_counts = defaultdict(int)
        for collab_data in active_collabs.values():
            for agent in collab_data.get('agents', []):
                collaboration_counts[agent] += 1
        
        if collaboration_counts:
            max_collabs = max(collaboration_counts.values())
            collaborative_agents = sum(1 for c in collaboration_counts.values() if c > 1)
            
            truth = self._create_or_update_truth(
                'collaboration_emergence',
                'collaboration',
                f"{collaborative_agents}/{len(collaboration_counts)} agents participate in multiple collaborations, showing cooperation emerges naturally",
                confidence=0.75,
                evidence={'collaboration_distribution': dict(collaboration_counts)}
            )
            truths.append(truth)
        
        return truths
    
    def discover_truths_from_analysis(self) -> List[UniversalTruth]:
        """
        📊 Discover universal truths from system analysis data.
        
        Analyzes archeology, patterns, and metrics to extract
        deep insights about system behavior.
        """
        truths = []
        
        # Analyze pattern files
        pattern_files = list(self.analysis_dir.glob('*-patterns.json'))
        
        for pf in pattern_files:
            with open(pf, 'r') as f:
                patterns = json.load(f)
            
            if patterns:
                pattern_type = pf.stem.replace('-patterns', '')
                
                truth = self._create_or_update_truth(
                    f'{pattern_type}_pattern_persistence',
                    'system_dynamics',
                    f"System exhibits persistent {pattern_type} patterns ({len(patterns)} distinct patterns), indicating structural invariants",
                    confidence=0.7,
                    evidence={'pattern_count': len(patterns), 'pattern_type': pattern_type}
                )
                truths.append(truth)
        
        return truths
    
    def _create_or_update_truth(
        self,
        truth_id: str,
        category: str,
        statement: str,
        confidence: float,
        evidence: Dict[str, Any]
    ) -> UniversalTruth:
        """Create a new truth or update existing one."""
        now = datetime.now().isoformat()
        
        if truth_id in self.truths:
            # Update existing truth
            truth = self.truths[truth_id]
            truth.last_validated = now
            truth.evidence_count += 1
            truth.supporting_data.append({
                'timestamp': now,
                'data': evidence
            })
            truth.evolution_history.append({
                'timestamp': now,
                'confidence': confidence,
                'statement': statement
            })
            # Update confidence with exponential moving average
            truth.confidence = 0.7 * truth.confidence + 0.3 * confidence
        else:
            # Create new truth
            truth = UniversalTruth(
                truth_id=truth_id,
                category=category,
                statement=statement,
                confidence=confidence,
                evidence_count=1,
                first_observed=now,
                last_validated=now,
                supporting_data=[{'timestamp': now, 'data': evidence}],
                counter_examples=[],
                evolution_history=[{'timestamp': now, 'confidence': confidence, 'statement': statement}],
                related_truths=[]
            )
            self.truths[truth_id] = truth
        
        return truth
    
    def validate_truth(self, truth_id: str, new_evidence: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Validate a truth against new evidence.
        
        Returns:
            (is_valid, new_confidence)
        """
        if truth_id not in self.truths:
            return False, 0.0
        
        truth = self.truths[truth_id]
        
        # Simple validation: if new evidence is provided, truth is reinforced
        truth.supporting_data.append({
            'timestamp': datetime.now().isoformat(),
            'data': new_evidence
        })
        truth.evidence_count += 1
        truth.last_validated = datetime.now().isoformat()
        
        # Increase confidence slightly with each validation
        truth.confidence = min(1.0, truth.confidence + 0.05)
        
        return True, truth.confidence
    
    def challenge_truth(self, truth_id: str, counter_evidence: Dict[str, Any]) -> float:
        """
        Challenge a truth with counter-evidence.
        
        Returns:
            Updated confidence level
        """
        if truth_id not in self.truths:
            return 0.0
        
        truth = self.truths[truth_id]
        truth.counter_examples.append({
            'timestamp': datetime.now().isoformat(),
            'data': counter_evidence
        })
        
        # Decrease confidence based on counter-evidence
        truth.confidence = max(0.0, truth.confidence - 0.15)
        
        return truth.confidence
    
    def discover_relationships(self):
        """Discover relationships between truths."""
        truth_list = list(self.truths.values())
        
        for i, truth1 in enumerate(truth_list):
            for truth2 in truth_list[i+1:]:
                # Simple relationship detection based on category overlap
                if truth1.category == truth2.category:
                    if truth2.truth_id not in truth1.related_truths:
                        truth1.related_truths.append(truth2.truth_id)
                    if truth1.truth_id not in truth2.related_truths:
                        truth2.related_truths.append(truth1.truth_id)
    
    def generate_insights(self) -> Dict[str, Any]:
        """
        Generate actionable insights from discovered truths.
        
        Returns:
            Dictionary of insights, recommendations, and meta-observations
        """
        insights = {
            'timestamp': datetime.now().isoformat(),
            'total_truths': len(self.truths),
            'stable_truths': sum(1 for t in self.truths.values() if t.is_stable()),
            'high_confidence_truths': sum(1 for t in self.truths.values() if t.confidence > 0.8),
            'category_distribution': self._get_category_distribution(),
            'key_discoveries': self._get_key_discoveries(),
            'recommendations': self._generate_recommendations(),
            'meta_observations': self._generate_meta_observations()
        }
        
        return insights
    
    def _get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of truths by category."""
        dist = defaultdict(int)
        for truth in self.truths.values():
            dist[truth.category] += 1
        return dict(dist)
    
    def _get_key_discoveries(self) -> List[Dict[str, Any]]:
        """Get the most significant truth discoveries."""
        # Sort by confidence and evidence count
        sorted_truths = sorted(
            self.truths.values(),
            key=lambda t: (t.confidence, t.evidence_count),
            reverse=True
        )
        
        return [
            {
                'truth_id': t.truth_id,
                'statement': t.statement,
                'confidence': t.confidence,
                'category': t.category
            }
            for t in sorted_truths[:10]
        ]
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on truths."""
        recommendations = []
        
        # Analyze truths for actionable insights
        for truth in self.truths.values():
            if truth.confidence > 0.8:
                if 'performance' in truth.truth_id:
                    recommendations.append(
                        f"High-confidence discovery: {truth.statement[:100]}... "
                        "Consider using this pattern to optimize agent allocation."
                    )
                elif 'diversity' in truth.truth_id:
                    recommendations.append(
                        f"Diversity principle confirmed: {truth.statement[:100]}... "
                        "Maintain specialization variety for system resilience."
                    )
                elif 'collaboration' in truth.truth_id:
                    recommendations.append(
                        f"Collaboration insight: {truth.statement[:100]}... "
                        "Encourage collaborative patterns that have emerged naturally."
                    )
        
        return recommendations
    
    def _generate_meta_observations(self) -> List[str]:
        """Generate meta-level observations about the truths themselves."""
        observations = []
        
        # Observation about truth stability
        stable_count = sum(1 for t in self.truths.values() if t.is_stable())
        observations.append(
            f"System stability: {stable_count}/{len(self.truths)} truths are stable, "
            f"indicating {'high' if stable_count/len(self.truths) > 0.7 else 'moderate'} "
            "system predictability."
        )
        
        # Observation about truth evolution
        evolving_truths = sum(1 for t in self.truths.values() if len(t.evolution_history) > 2)
        if evolving_truths > 0:
            observations.append(
                f"{evolving_truths} truths show significant evolution, "
                "suggesting the system is in active development phase."
            )
        
        # Observation about interconnectedness
        connected_truths = sum(1 for t in self.truths.values() if len(t.related_truths) > 0)
        if connected_truths > 0:
            observations.append(
                f"{connected_truths} truths are interconnected, "
                "revealing emergent systemic patterns beyond individual observations."
            )
        
        return observations
    
    def run_full_discovery(self) -> Dict[str, Any]:
        """
        🌟 Run a complete truth discovery cycle.
        
        This is the main entry point for discovering universal truths
        across all system dimensions.
        """
        print("🌌 Universal Truth Evaluator - Discovery Cycle")
        print("=" * 60)
        
        all_truths = []
        
        print("\n🤖 Discovering truths from agent behavior...")
        agent_truths = self.discover_truths_from_agents()
        all_truths.extend(agent_truths)
        print(f"   ✓ Discovered {len(agent_truths)} agent behavior truths")
        
        print("\n📚 Discovering truths from learning patterns...")
        learning_truths = self.discover_truths_from_learnings()
        all_truths.extend(learning_truths)
        print(f"   ✓ Discovered {len(learning_truths)} learning pattern truths")
        
        print("\n🤝 Discovering truths from collaboration...")
        collab_truths = self.discover_truths_from_collaboration()
        all_truths.extend(collab_truths)
        print(f"   ✓ Discovered {len(collab_truths)} collaboration truths")
        
        print("\n📊 Discovering truths from analysis data...")
        analysis_truths = self.discover_truths_from_analysis()
        all_truths.extend(analysis_truths)
        print(f"   ✓ Discovered {len(analysis_truths)} systemic truths")
        
        print("\n🔗 Discovering relationships between truths...")
        self.discover_relationships()
        print(f"   ✓ Mapped relationships across {len(self.truths)} truths")
        
        print("\n💾 Persisting universal truths...")
        self._save_truths()
        print(f"   ✓ Saved to {self.truths_file}")
        
        print("\n💡 Generating insights...")
        insights = self.generate_insights()
        
        print("\n" + "=" * 60)
        print(f"✨ Discovery Complete!")
        print(f"   Total Truths: {insights['total_truths']}")
        print(f"   Stable Truths: {insights['stable_truths']}")
        print(f"   High Confidence: {insights['high_confidence_truths']}")
        print("=" * 60)
        
        return insights


def main():
    """Main entry point for CLI usage."""
    evaluator = UniversalTruthEvaluator()
    
    # Run full discovery
    insights = evaluator.run_full_discovery()
    
    # Print key discoveries
    print("\n🌟 KEY DISCOVERIES:")
    for i, discovery in enumerate(insights['key_discoveries'], 1):
        print(f"\n{i}. [{discovery['category']}] (confidence: {discovery['confidence']:.2f})")
        print(f"   {discovery['statement']}")
    
    # Print recommendations
    print("\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(insights['recommendations'], 1):
        print(f"\n{i}. {rec}")
    
    # Print meta-observations
    print("\n🔮 META-OBSERVATIONS:")
    for i, obs in enumerate(insights['meta_observations'], 1):
        print(f"\n{i}. {obs}")
    
    # Save insights
    insights_file = Path(__file__).parent.parent / "analysis" / "universal_truths_insights.json"
    with open(insights_file, 'w') as f:
        json.dump(insights, f, indent=2)
    print(f"\n💾 Insights saved to: {insights_file}")


if __name__ == "__main__":
    main()
