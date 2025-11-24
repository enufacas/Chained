#!/usr/bin/env python3
"""
Enhanced Sub-Agent Spawner - Intelligent Spawning with Learning

Combines workload monitoring, intelligent parent selection, and performance
learning to make optimal sub-agent spawning decisions.

Created by @create-guru - Inventive and visionary, building the future.

Features:
- Intelligent parent selection using multi-criteria scoring
- Performance-based spawning decisions (learn from history)
- Adaptive threshold adjustment
- Parent-child relationship optimization
- Predictive spawning based on patterns
- Comprehensive logging and reporting

Part of the Chained autonomous AI ecosystem.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from workload_monitor import WorkloadMonitor, SpawningRecommendation
    from intelligent_parent_selector import IntelligentParentSelector, ParentScore
    from subagent_performance_learner import SubAgentPerformanceLearner
    from registry_manager import RegistryManager
except ImportError as e:
    print(f"Error: Required module not found: {e}")
    sys.exit(1)


class EnhancedSubAgentSpawner:
    """
    Enhanced sub-agent spawner with intelligence and learning.
    
    @create-guru's innovative design:
    - Learns from past spawning outcomes
    - Selects optimal parent agents
    - Adapts thresholds based on success rates
    - Provides detailed reasoning for decisions
    """
    
    def __init__(self):
        """Initialize enhanced spawner"""
        self.registry = RegistryManager()
        self.workload_monitor = WorkloadMonitor()
        self.parent_selector = IntelligentParentSelector(self.registry)
        self.performance_learner = SubAgentPerformanceLearner(self.registry)
        
        # Load learning data
        self.learning_insights = None
    
    def spawn_with_intelligence(
        self,
        max_spawns: int = 5,
        use_learning: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Spawn sub-agents using intelligent decision-making.
        
        Args:
            max_spawns: Maximum number of agents to spawn
            use_learning: Whether to use performance learning
            dry_run: If True, simulate without creating agents
        
        Returns:
            Dictionary with spawning results and decisions
        """
        print("\n🤖 Enhanced Sub-Agent Spawner")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'use_learning': use_learning,
            'dry_run': dry_run,
            'decisions': [],
            'spawned_agents': [],
            'total_spawned': 0
        }
        
        # Step 1: Learn from past performance (if enabled)
        if use_learning:
            print("\n🧠 Learning from past performance...")
            try:
                self.learning_insights = self.performance_learner.learn_from_performance()
                print(f"   ✅ Generated {len(self.learning_insights)} insights")
            except Exception as e:
                print(f"   ⚠️  Learning failed: {e}")
                self.learning_insights = []
        
        # Step 2: Get workload-based recommendations
        print("\n📊 Analyzing current workload...")
        try:
            recommendations = self.workload_monitor.get_spawning_recommendations(
                max_recommendations=max_spawns
            )
            print(f"   ✅ Found {len(recommendations)} spawning recommendations")
        except Exception as e:
            print(f"   ❌ Workload analysis failed: {e}")
            return results
        
        if not recommendations:
            print("   ℹ️  No spawning needed - system is balanced")
            return results
        
        # Step 3: Process each recommendation with intelligence
        for rec in recommendations:
            if results['total_spawned'] >= max_spawns:
                break
            
            decision = self._make_intelligent_decision(rec, use_learning)
            results['decisions'].append(decision)
            
            if decision['should_spawn']:
                # Spawn the agents
                spawned = self._spawn_agents(decision, dry_run)
                results['spawned_agents'].extend(spawned)
                results['total_spawned'] += len(spawned)
        
        # Step 4: Summary
        print(f"\n📊 Summary")
        print("=" * 60)
        print(f"Decisions Made: {len(results['decisions'])}")
        print(f"Agents Spawned: {results['total_spawned']}/{max_spawns}")
        print(f"Dry Run: {dry_run}")
        
        return results
    
    def _make_intelligent_decision(
        self,
        recommendation: SpawningRecommendation,
        use_learning: bool
    ) -> Dict[str, Any]:
        """
        Make intelligent spawning decision for a recommendation.
        
        Args:
            recommendation: Workload-based recommendation
            use_learning: Whether to use learned patterns
        
        Returns:
            Decision dictionary with reasoning
        """
        category = recommendation.specialization
        metrics = recommendation.metrics
        
        print(f"\n🎯 Evaluating: {category}")
        print(f"   Workload: {metrics.workload_per_agent:.1f} items/agent")
        print(f"   Bottleneck: {metrics.bottleneck_severity}")
        print(f"   Priority: {recommendation.priority}")
        
        decision = {
            'category': category,
            'should_spawn': recommendation.should_spawn,
            'base_count': recommendation.count,
            'final_count': recommendation.count,
            'confidence': 0.5,
            'reasoning': [],
            'parent_candidates': [],
            'learned_threshold': None
        }
        
        # Check learning data (if available)
        if use_learning and self.performance_learner:
            try:
                learned_rec = self.performance_learner.get_spawning_recommendations(
                    category,
                    metrics.workload_per_agent
                )
                
                decision['learned_threshold'] = learned_rec.get('optimal_threshold')
                decision['confidence'] = learned_rec.get('confidence', 0.5)
                
                # Adjust decision based on learning
                if learned_rec['should_spawn'] != recommendation.should_spawn:
                    print(f"   🧠 Learning suggests: {learned_rec['should_spawn']}")
                    print(f"      Reason: {learned_rec['reason']}")
                    
                    # Trust learning if confidence is high
                    if learned_rec['confidence'] > 0.7:
                        decision['should_spawn'] = learned_rec['should_spawn']
                        decision['final_count'] = learned_rec.get('recommended_count', 1)
                        decision['reasoning'].append(
                            f"Learning override (confidence: {learned_rec['confidence']*100:.1f}%)"
                        )
                
                decision['reasoning'].append(
                    f"Historical success rate: {learned_rec.get('success_rate', 0)*100:.1f}%"
                )
            except Exception as e:
                print(f"   ⚠️  Could not apply learning: {e}")
        
        # Add base reasoning
        decision['reasoning'].append(
            f"Workload: {metrics.workload_per_agent:.1f} items/agent"
        )
        decision['reasoning'].append(
            f"Bottleneck severity: {metrics.bottleneck_severity}"
        )
        
        # Select parent agents (if spawning)
        if decision['should_spawn']:
            print(f"   👥 Selecting parent agents...")
            try:
                # Get specializations for this category
                specializations = self._get_specializations_for_category(category)
                
                parent_candidates = []
                for spec in specializations[:3]:  # Top 3 specializations
                    parents = self.parent_selector.select_parent(
                        specialization=spec,
                        top_n=1
                    )
                    if parents:
                        parent_candidates.extend(parents)
                
                # Sort by score
                parent_candidates.sort(key=lambda p: p.total_score, reverse=True)
                decision['parent_candidates'] = [
                    {
                        'id': p.agent_id,
                        'name': p.agent_name,
                        'specialization': p.specialization,
                        'score': p.total_score,
                        'recommendation': p.recommendation
                    }
                    for p in parent_candidates[:decision['final_count']]
                ]
                
                if parent_candidates:
                    print(f"      ✅ Found {len(parent_candidates)} suitable parents")
                    for p in parent_candidates[:3]:
                        print(f"         {p.agent_name}: {p.total_score:.1f}/100")
                else:
                    print(f"      ⚠️  No parent candidates found")
                    decision['should_spawn'] = False
                    decision['reasoning'].append("No suitable parent agents available")
                
            except Exception as e:
                print(f"      ❌ Parent selection failed: {e}")
                decision['should_spawn'] = False
                decision['reasoning'].append(f"Parent selection error: {e}")
        
        print(f"   Decision: {'✅ SPAWN' if decision['should_spawn'] else '⛔ SKIP'}")
        print(f"   Confidence: {decision['confidence']*100:.1f}%")
        
        return decision
    
    def _get_specializations_for_category(self, category: str) -> List[str]:
        """Get specializations for a category"""
        # Mapping from categories to specializations
        category_map = {
            'security': ['secure-specialist', 'secure-ninja', 'secure-pro'],
            'performance': ['accelerate-master', 'accelerate-specialist'],
            'bug-fix': ['organize-guru', 'cleaner-master', 'simplify-pro'],
            'feature': ['engineer-master', 'create-guru', 'develop-specialist'],
            'documentation': ['document-ninja', 'clarify-champion', 'support-master'],
            'testing': ['assert-specialist', 'assert-whiz', 'validator-pro'],
            'infrastructure': ['create-guru', 'infrastructure-specialist', 'tools-analyst'],
            'refactoring': ['organize-guru', 'refactor-champion', 'restructure-master'],
            'ai-ml': ['meta-coordinator', 'pioneer-sage', 'pioneer-pro'],
            'api': ['APIs-architect', 'connector-ninja', 'bridge-master'],
        }
        
        return category_map.get(category, [])
    
    def _spawn_agents(
        self,
        decision: Dict[str, Any],
        dry_run: bool
    ) -> List[Dict[str, Any]]:
        """
        Actually spawn the agents based on decision.
        
        Args:
            decision: Decision dictionary
            dry_run: If True, don't actually create agents
        
        Returns:
            List of spawned agent dictionaries
        """
        if not decision.get('parent_candidates'):
            return []
        
        spawned = []
        
        for i, parent_info in enumerate(decision['parent_candidates']):
            if i >= decision['final_count']:
                break
            
            print(f"\n   🤖 Spawning sub-agent #{i+1}...")
            print(f"      Parent: {parent_info['name']}")
            print(f"      Parent Score: {parent_info['score']:.1f}/100")
            
            if not dry_run:
                # Here you would call the actual spawning logic
                # For now, we'll create a mock entry
                agent_data = {
                    'parent_id': parent_info['id'],
                    'parent_name': parent_info['name'],
                    'specialization': parent_info['specialization'],
                    'category': decision['category'],
                    'spawned_at': datetime.now().isoformat(),
                    'reasoning': decision['reasoning'],
                    'confidence': decision['confidence']
                }
                spawned.append(agent_data)
                print(f"      ✅ Spawned (mock)")
            else:
                print(f"      ℹ️  Dry run - not creating")
                spawned.append({
                    'dry_run': True,
                    'parent_id': parent_info['id'],
                    'category': decision['category']
                })
        
        return spawned


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description='Enhanced Sub-Agent Spawner with Intelligence'
    )
    parser.add_argument(
        '--max-spawns',
        type=int,
        default=5,
        help='Maximum number of agents to spawn'
    )
    parser.add_argument(
        '--no-learning',
        action='store_true',
        help='Disable performance learning'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without creating agents'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    spawner = EnhancedSubAgentSpawner()
    
    results = spawner.spawn_with_intelligence(
        max_spawns=args.max_spawns,
        use_learning=not args.no_learning,
        dry_run=args.dry_run
    )
    
    if args.format == 'json':
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
