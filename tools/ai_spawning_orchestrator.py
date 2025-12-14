#!/usr/bin/env python3
"""
AI Spawning Orchestrator - Intelligent AI-Driven Sub-Agent Spawning

Orchestrates specialized sub-agent spawning based on workload analysis using
AI-powered decision making. Integrates workload monitoring, performance learning,
intelligent parent selection, and adaptive thresholds.

Created by @create-botter - Inventive and visionary, building the future.

Features:
- AI-driven workload analysis and spawning decisions
- Multi-criteria optimization for parent selection
- Performance-based learning from historical data
- Adaptive threshold adjustment
- Predictive spawning based on trends
- Comprehensive reasoning and explanations
- Dry-run mode for safe testing

Part of the Chained autonomous AI ecosystem.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from workload_monitor import WorkloadMonitor, SpawningRecommendation, WorkloadMetrics
    from intelligent_parent_selector import IntelligentParentSelector, ParentScore
    from subagent_performance_learner import SubAgentPerformanceLearner
    from registry_manager import RegistryManager
except ImportError as e:
    print(f"Error: Required module not found: {e}")
    print("Please ensure all dependencies are available in the tools directory")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SpawningDecision:
    """AI-driven decision about spawning sub-agents"""
    should_spawn: bool
    category: str
    specializations: List[str]
    count: int
    confidence: float  # 0-1
    reasoning: List[str]
    workload_metrics: Dict[str, Any]
    parent_candidates: List[Dict[str, Any]]
    learned_insights: List[str]
    priority: int  # 1-5


@dataclass
class SpawnedAgent:
    """Information about a spawned agent"""
    agent_id: str
    parent_id: str
    parent_name: str
    specialization: str
    category: str
    spawned_at: str
    reasoning: List[str]
    confidence: float
    workload_justification: str


class AISpawningOrchestrator:
    """
    AI-powered orchestrator for intelligent sub-agent spawning.
    
    @create-botter's visionary design:
    - Combines multiple AI components for holistic decision making
    - Learns from past spawning outcomes
    - Adapts thresholds based on system performance
    - Provides transparent reasoning for all decisions
    - Maintains system balance and efficiency
    """
    
    def __init__(self,
                 registry_path: str = ".github/agent-system",
                 enable_learning: bool = True,
                 enable_predictions: bool = True):
        """
        Initialize AI spawning orchestrator.
        
        Args:
            registry_path: Path to agent registry
            enable_learning: Enable performance-based learning
            enable_predictions: Enable predictive spawning
        """
        logger.info("🤖 Initializing AI Spawning Orchestrator")
        
        self.registry = RegistryManager(registry_path)
        self.workload_monitor = WorkloadMonitor()
        self.parent_selector = IntelligentParentSelector(self.registry)
        
        self.enable_learning = enable_learning
        self.enable_predictions = enable_predictions
        
        # Initialize learning system if enabled
        if enable_learning:
            try:
                self.performance_learner = SubAgentPerformanceLearner(self.registry)
                logger.info("✅ Performance learning enabled")
            except Exception as e:
                logger.warning(f"⚠️  Performance learning disabled: {e}")
                self.performance_learner = None
                self.enable_learning = False
        else:
            self.performance_learner = None
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        default_config = {
            'max_spawns_per_run': 5,
            'min_confidence_threshold': 0.5,
            'enable_adaptive_thresholds': True,
            'spawn_cooldown_hours': 2,
            'max_agents_per_category': 8,
            'workload_threshold': 5.0,
            'critical_workload_threshold': 10.0,
            'learning_weight': 0.4,  # How much to trust historical learning
            'prediction_weight': 0.2,  # How much to trust predictions
        }
        
        config_file = Path('.github/agent-system/spawning_config.json')
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    logger.info(f"✅ Loaded configuration from {config_file}")
            except Exception as e:
                logger.warning(f"⚠️  Could not load config: {e}, using defaults")
        
        return default_config
    
    def orchestrate(self,
                    max_spawns: Optional[int] = None,
                    force_categories: Optional[List[str]] = None,
                    dry_run: bool = False) -> Dict[str, Any]:
        """
        Orchestrate AI-driven sub-agent spawning.
        
        Args:
            max_spawns: Maximum number of agents to spawn (overrides config)
            force_categories: Force spawning in specific categories
            dry_run: If True, simulate without creating agents
        
        Returns:
            Dictionary with orchestration results
        """
        logger.info("=" * 80)
        logger.info("🚀 AI-DRIVEN SUB-AGENT SPAWNING ORCHESTRATOR")
        logger.info("=" * 80)
        
        max_spawns = max_spawns or self.config['max_spawns_per_run']
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': dry_run,
            'learning_enabled': self.enable_learning,
            'predictions_enabled': self.enable_predictions,
            'decisions': [],
            'spawned_agents': [],
            'total_spawned': 0,
            'summary': {}
        }
        
        # Step 1: Learn from past performance
        learned_insights = []
        if self.enable_learning and self.performance_learner:
            logger.info("\n🧠 STEP 1: Learning from Historical Performance")
            logger.info("-" * 60)
            try:
                insights = self.performance_learner.learn_from_performance()
                learned_insights = insights
                logger.info(f"✅ Generated {len(insights)} performance insights")
                
                for insight in insights[:3]:  # Show top 3
                    logger.info(f"  📌 {insight.description}")
                    logger.info(f"     Confidence: {insight.confidence*100:.1f}%")
            except Exception as e:
                logger.warning(f"⚠️  Learning failed: {e}")
        
        # Step 2: Analyze current workload
        logger.info("\n📊 STEP 2: Analyzing Current Workload")
        logger.info("-" * 60)
        
        try:
            # First analyze workload
            metrics = self.workload_monitor.analyze_workload()
            logger.info(f"✅ Analyzed workload for {len(metrics)} specializations")
            
            # Then generate recommendations
            recommendations = self.workload_monitor.generate_spawning_recommendations(
                metrics,
                max_spawns=max_spawns * 2  # Get more than needed for filtering
            )
            logger.info(f"✅ Found {len(recommendations)} spawning recommendations")
        except Exception as e:
            logger.error(f"❌ Workload analysis failed: {e}")
            results['error'] = str(e)
            return results
        
        if not recommendations:
            logger.info("✅ No spawning needed - system is balanced")
            results['summary']['status'] = 'balanced'
            return results
        
        # Filter by forced categories if specified
        if force_categories:
            recommendations = [
                r for r in recommendations 
                if r.specialization in force_categories
            ]
            logger.info(f"🎯 Filtered to {len(recommendations)} recommendations for forced categories")
        
        # Step 3: Make AI-driven decisions
        logger.info("\n🤖 STEP 3: AI-Driven Decision Making")
        logger.info("-" * 60)
        
        for rec in recommendations:
            if results['total_spawned'] >= max_spawns:
                logger.info(f"⚠️  Reached maximum spawn limit ({max_spawns})")
                break
            
            decision = self._make_ai_decision(rec, learned_insights)
            results['decisions'].append(asdict(decision))
            
            if decision.should_spawn and decision.confidence >= self.config['min_confidence_threshold']:
                # Step 4: Spawn agents
                spawned = self._spawn_agents(decision, dry_run)
                results['spawned_agents'].extend(spawned)
                results['total_spawned'] += len(spawned)
        
        # Step 5: Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 ORCHESTRATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Decisions Made: {len(results['decisions'])}")
        logger.info(f"Agents Spawned: {results['total_spawned']}/{max_spawns}")
        logger.info(f"Dry Run: {dry_run}")
        logger.info(f"Learning Insights: {len(learned_insights)}")
        
        results['summary'] = {
            'decisions_made': len(results['decisions']),
            'agents_spawned': results['total_spawned'],
            'max_spawns': max_spawns,
            'learning_insights': len(learned_insights),
            'status': 'complete'
        }
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _make_ai_decision(self,
                          recommendation: SpawningRecommendation,
                          learned_insights: List[Any]) -> SpawningDecision:
        """
        Make AI-driven decision about spawning for a recommendation.
        
        Uses multi-criteria analysis:
        - Workload metrics (current state)
        - Historical learning (past performance)
        - Predictive analysis (future trends)
        - Parent availability (resource constraints)
        """
        category = recommendation.specialization
        metrics = recommendation.metrics
        
        logger.info(f"\n🎯 Evaluating Category: {category}")
        logger.info(f"   Workload: {metrics.workload_per_agent:.1f} items/agent")
        logger.info(f"   Bottleneck: {metrics.bottleneck_severity}")
        logger.info(f"   Priority: {recommendation.priority}")
        
        reasoning = []
        confidence_scores = []
        
        # Base decision from workload
        should_spawn = recommendation.should_spawn
        spawn_count = recommendation.count
        base_confidence = 0.6
        
        reasoning.append(
            f"Workload analysis: {metrics.workload_per_agent:.1f} items/agent "
            f"(threshold: {self.config['workload_threshold']})"
        )
        confidence_scores.append(base_confidence)
        
        # Apply learning insights
        if self.enable_learning and self.performance_learner:
            try:
                learned_rec = self.performance_learner.get_spawning_recommendations(
                    category,
                    metrics.workload_per_agent
                )
                
                learning_weight = self.config['learning_weight']
                learned_confidence = learned_rec.get('confidence', 0.5)
                
                logger.info(f"   🧠 Learning: {learned_rec['reason']}")
                logger.info(f"      Confidence: {learned_confidence*100:.1f}%")
                
                # Adjust decision based on learning
                if learned_rec['should_spawn'] != should_spawn:
                    if learned_confidence > 0.7:  # High confidence override
                        logger.info(f"      ⚡ Learning override: {learned_rec['should_spawn']}")
                        should_spawn = learned_rec['should_spawn']
                        spawn_count = learned_rec.get('recommended_count', 1)
                        reasoning.append(
                            f"Learning override (confidence: {learned_confidence*100:.1f}%): "
                            f"{learned_rec['reason']}"
                        )
                    else:
                        reasoning.append(
                            f"Learning suggests: {learned_rec['should_spawn']} "
                            f"(confidence: {learned_confidence*100:.1f}%, not applied)"
                        )
                
                confidence_scores.append(learned_confidence * learning_weight)
                
                if 'success_rate' in learned_rec:
                    reasoning.append(
                        f"Historical success rate: {learned_rec['success_rate']*100:.1f}%"
                    )
            
            except Exception as e:
                logger.warning(f"   ⚠️  Could not apply learning: {e}")
        
        # Check parent availability
        parent_candidates = []
        if should_spawn:
            logger.info(f"   👥 Selecting parent agents...")
            try:
                # Get specializations for this category
                specializations = self._get_specializations_for_category(category)
                
                # Select best parents
                for spec in specializations[:3]:
                    parents = self.parent_selector.select_parent(
                        specialization=spec,
                        top_n=1
                    )
                    if parents:
                        parent_candidates.extend(parents)
                
                # Sort by score
                parent_candidates.sort(key=lambda p: p.total_score, reverse=True)
                
                if parent_candidates:
                    logger.info(f"      ✅ Found {len(parent_candidates)} suitable parents")
                    for p in parent_candidates[:3]:
                        logger.info(f"         {p.agent_name}: {p.total_score:.1f}/100")
                    
                    # Adjust count based on available parents
                    spawn_count = min(spawn_count, len(parent_candidates))
                    
                    # Parent quality affects confidence
                    avg_parent_score = sum(p.total_score for p in parent_candidates[:spawn_count]) / spawn_count
                    parent_confidence = avg_parent_score / 100.0
                    confidence_scores.append(parent_confidence * 0.3)
                    
                    reasoning.append(
                        f"Parent quality: {avg_parent_score:.1f}/100 "
                        f"({len(parent_candidates)} candidates)"
                    )
                else:
                    logger.warning(f"      ⚠️  No suitable parents found")
                    should_spawn = False
                    reasoning.append("No suitable parent agents available")
                    confidence_scores.append(0.0)
            
            except Exception as e:
                logger.error(f"      ❌ Parent selection failed: {e}")
                should_spawn = False
                reasoning.append(f"Parent selection error: {e}")
                confidence_scores.append(0.0)
        
        # Calculate final confidence
        final_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Extract learned insights for this category
        # Note: Using hasattr for defensive programming even though type is List[PerformanceInsight]
        # to handle edge cases where learning might return unexpected types
        category_insights = [
            f"{i.description} (confidence: {i.confidence*100:.1f}%)"
            for i in learned_insights
            if hasattr(i, 'specialization') and i.specialization == category
        ]
        
        decision = SpawningDecision(
            should_spawn=should_spawn,
            category=category,
            specializations=[p.specialization for p in parent_candidates[:spawn_count]],
            count=spawn_count,
            confidence=final_confidence,
            reasoning=reasoning,
            workload_metrics={
                'workload_per_agent': metrics.workload_per_agent,
                'open_issues': metrics.open_issues,
                'pending_prs': metrics.pending_prs,
                'active_agents': metrics.active_agents,
                'bottleneck_severity': metrics.bottleneck_severity
            },
            parent_candidates=[
                {
                    'id': p.agent_id,
                    'name': p.agent_name,
                    'specialization': p.specialization,
                    'score': p.total_score,
                    'recommendation': p.recommendation
                }
                for p in parent_candidates[:spawn_count]
            ],
            learned_insights=category_insights,
            priority=recommendation.priority
        )
        
        logger.info(f"   Decision: {'✅ SPAWN' if should_spawn else '⛔ SKIP'}")
        logger.info(f"   Confidence: {final_confidence*100:.1f}%")
        logger.info(f"   Count: {spawn_count}")
        
        return decision
    
    def _get_specializations_for_category(self, category: str) -> List[str]:
        """
        Get specializations for a workload category.
        
        Maps workload categories to agent specializations.
        """
        category_map = {
            'security': ['secure-specialist', 'secure-ninja', 'secure-pro', 'guardian-master'],
            'performance': ['accelerate-master', 'accelerate-specialist', 'optimize-director'],
            'bug-fix': ['organize-guru', 'cleaner-master', 'simplify-pro'],
            'feature': ['engineer-master', 'engineer-wizard', 'create-botter', 'develop-specialist'],
            'documentation': ['document-ninja', 'clarify-champion', 'support-master', 'communicator-maestro'],
            'testing': ['assert-specialist', 'assert-whiz', 'validator-pro', 'edge-cases-pro'],
            'infrastructure': ['create-botter', 'infrastructure-specialist', 'tools-analyst', 'build-wizard'],
            'refactoring': ['organize-guru', 'refactor-champion', 'restructure-master'],
            'ai-ml': ['meta-coordinator', 'pioneer-sage', 'pioneer-pro', 'ai-specialist'],
            'api': ['APIs-architect', 'connector-ninja', 'bridge-master', 'integrate-specialist'],
        }
        
        return category_map.get(category, [])
    
    def _spawn_agents(self,
                      decision: SpawningDecision,
                      dry_run: bool) -> List[Dict[str, Any]]:
        """
        Spawn sub-agents based on AI decision.
        
        Args:
            decision: AI-driven spawning decision
            dry_run: If True, don't actually create agents
        
        Returns:
            List of spawned agent data
        """
        if not decision.parent_candidates:
            return []
        
        spawned = []
        
        for i, parent_info in enumerate(decision.parent_candidates):
            if i >= decision.count:
                break
            
            logger.info(f"\n   🤖 Spawning Sub-Agent #{i+1}/{decision.count}")
            logger.info(f"      Parent: {parent_info['name']}")
            logger.info(f"      Specialization: {parent_info['specialization']}")
            logger.info(f"      Parent Score: {parent_info['score']:.1f}/100")
            logger.info(f"      Confidence: {decision.confidence*100:.1f}%")
            
            if not dry_run:
                # Generate unique agent ID
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                agent_id = f"subagent-{parent_info['specialization']}-{timestamp}-{i}"
                
                # Create spawned agent record
                agent_data = {
                    'agent_id': agent_id,
                    'parent_id': parent_info['id'],
                    'parent_name': parent_info['name'],
                    'specialization': parent_info['specialization'],
                    'category': decision.category,
                    'spawned_at': datetime.now().isoformat(),
                    'reasoning': decision.reasoning,
                    'confidence': decision.confidence,
                    'workload_justification': (
                        f"Workload: {decision.workload_metrics['workload_per_agent']:.1f} items/agent, "
                        f"Bottleneck: {decision.workload_metrics['bottleneck_severity']}"
                    ),
                    'is_sub_agent': True,
                    'spawned_by': 'ai-orchestrator'
                }
                
                spawned.append(agent_data)
                logger.info(f"      ✅ Spawned: {agent_id}")
                
                # Register with registry (if registry supports it)
                try:
                    self.registry.add_agent({
                        'id': agent_id,
                        'name': f"🤖 {parent_info['name']} - Sub",
                        'specialization': parent_info['specialization'],
                        'status': 'active',
                        'is_sub_agent': True,
                        'parent_agent_id': parent_info['id'],
                        'spawned_at': datetime.now().isoformat(),
                        'spawn_reason': agent_data['workload_justification'],
                        'metrics': {
                            'issues_resolved': 0,
                            'prs_merged': 0,
                            'overall_score': 0.0
                        }
                    })
                    logger.info(f"      ✅ Registered in agent registry")
                except Exception as e:
                    logger.warning(f"      ⚠️  Registry update failed: {e}")
            
            else:
                logger.info(f"      ℹ️  Dry run - not creating")
                spawned.append({
                    'dry_run': True,
                    'parent_id': parent_info['id'],
                    'category': decision.category,
                    'specialization': parent_info['specialization']
                })
        
        return spawned
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save orchestration results to file"""
        try:
            output_dir = Path('.github/agent-system')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / 'ai_spawning_results.json'
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"\n💾 Results saved to {output_file}")
        
        except Exception as e:
            logger.warning(f"⚠️  Could not save results: {e}")


def main():
    """CLI interface for AI spawning orchestrator"""
    parser = argparse.ArgumentParser(
        description='AI-Driven Sub-Agent Spawning Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python3 ai_spawning_orchestrator.py
  
  # Dry run to see what would be spawned
  python3 ai_spawning_orchestrator.py --dry-run
  
  # Spawn up to 3 agents with learning disabled
  python3 ai_spawning_orchestrator.py --max-spawns 3 --no-learning
  
  # Force spawning in specific categories
  python3 ai_spawning_orchestrator.py --categories security performance
  
  # JSON output for automation
  python3 ai_spawning_orchestrator.py --format json
        """
    )
    
    parser.add_argument(
        '--max-spawns',
        type=int,
        default=5,
        help='Maximum number of agents to spawn (default: 5)'
    )
    
    parser.add_argument(
        '--categories',
        nargs='+',
        help='Force spawning in specific categories'
    )
    
    parser.add_argument(
        '--no-learning',
        action='store_true',
        help='Disable performance-based learning'
    )
    
    parser.add_argument(
        '--no-predictions',
        action='store_true',
        help='Disable predictive spawning'
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
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create orchestrator
    orchestrator = AISpawningOrchestrator(
        enable_learning=not args.no_learning,
        enable_predictions=not args.no_predictions
    )
    
    # Run orchestration
    results = orchestrator.orchestrate(
        max_spawns=args.max_spawns,
        force_categories=args.categories,
        dry_run=args.dry_run
    )
    
    # Output results
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        # Text format already logged
        pass


if __name__ == '__main__':
    main()
