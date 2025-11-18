#!/usr/bin/env python3
"""
Workload-Based Sub-Agent Spawner

Spawns specialized sub-agents automatically based on workload analysis.
Integrates with workload_monitor.py to make intelligent spawning decisions.

Features:
- Workload-driven spawning (not random)
- Specialization matching to bottlenecks
- Capacity-aware (respects agent limits)
- Registry integration
- Batch spawning for efficiency

Part of the Chained autonomous AI ecosystem.
Created by @accelerate-specialist - Efficient algorithms with Dijkstra's elegance.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from workload_monitor import WorkloadMonitor, SpawningRecommendation
    from registry_manager import RegistryManager
    from generate_new_agent import generate_agent_personality, SPECIALIZATION_TEMPLATES
except ImportError as e:
    print(f"Error: Required modules not found: {e}")
    sys.exit(1)


@dataclass
class SubAgentSpec:
    """Specification for a sub-agent to be spawned"""
    agent_id: str
    human_name: str
    specialization: str
    category: str
    personality: str
    communication_style: str
    creativity: int
    caution: int
    speed: int
    justification: str
    workload_metrics: Dict[str, Any]


class WorkloadSubAgentSpawner:
    """
    Spawn sub-agents based on workload analysis.
    
    Elegant design principles:
    - Single responsibility: spawn agents for specific workload needs
    - Dependency injection: uses WorkloadMonitor and RegistryManager
    - Clear interfaces: well-defined inputs and outputs
    """
    
    # Specialization category to agent type mapping
    CATEGORY_TO_SPECIALIZATION = {
        'security': [
            'secure-specialist', 'secure-ninja', 'secure-pro',
            'guardian-master', 'monitor-champion'
        ],
        'performance': [
            'accelerate-master', 'accelerate-specialist'
        ],
        'bug-fix': [
            'organize-guru', 'cleaner-master', 'simplify-pro'
        ],
        'feature': [
            'engineer-master', 'engineer-wizard', 'create-guru',
            'develop-specialist', 'construct-specialist'
        ],
        'documentation': [
            'document-ninja', 'clarify-champion', 'support-master',
            'communicator-maestro'
        ],
        'testing': [
            'assert-specialist', 'assert-whiz', 'validator-pro',
            'edge-cases-pro'
        ],
        'infrastructure': [
            'create-guru', 'infrastructure-specialist', 'tools-analyst'
        ],
        'refactoring': [
            'organize-guru', 'organize-specialist', 'refactor-champion',
            'restructure-master', 'cleaner-master', 'simplify-pro'
        ],
        'ai-ml': [
            'meta-coordinator', 'pioneer-sage', 'pioneer-pro'
        ],
        'api': [
            'APIs-architect', 'connector-ninja', 'bridge-master',
            'integrate-specialist'
        ],
    }
    
    def __init__(self, 
                 registry_path: str = ".github/agent-system",
                 profiles_dir: str = ".github/agent-system/profiles"):
        """
        Initialize sub-agent spawner.
        
        Args:
            registry_path: Path to agent registry
            profiles_dir: Directory for agent profiles
        """
        self.registry_path = Path(registry_path)
        self.profiles_dir = Path(profiles_dir)
        
        # Initialize components
        try:
            self.registry = RegistryManager(str(self.registry_path))
        except Exception as e:
            print(f"Warning: Could not initialize registry: {e}")
            self.registry = None
        
        self.workload_monitor = WorkloadMonitor(registry_path=str(self.registry_path))
        
        # Track used human names to avoid collisions
        self.used_names = self._load_used_names()
    
    def _load_used_names(self) -> set:
        """Load names already used by active agents"""
        used = set()
        
        if not self.registry:
            return used
        
        try:
            agents = self.registry.list_agents(status='active')
            for agent in agents:
                human_name = agent.get('human_name', '')
                if human_name:
                    used.add(human_name.lower())
        except Exception as e:
            print(f"Warning: Could not load used names: {e}")
        
        return used
    
    def spawn_from_recommendations(self,
                                  recommendations: List[SpawningRecommendation],
                                  max_total_spawns: int = 5,
                                  dry_run: bool = False) -> List[SubAgentSpec]:
        """
        Spawn sub-agents based on workload recommendations.
        
        Args:
            recommendations: List of spawning recommendations
            max_total_spawns: Maximum agents to spawn in this batch
            dry_run: If True, don't actually create agents
            
        Returns:
            List of SubAgentSpec for spawned agents
        """
        spawned_agents = []
        total_spawned = 0
        
        for recommendation in recommendations:
            if total_spawned >= max_total_spawns:
                print(f"⚠️  Reached max spawns limit ({max_total_spawns})")
                break
            
            # How many to spawn for this recommendation
            spawn_count = min(
                recommendation.count,
                max_total_spawns - total_spawned
            )
            
            print(f"\n🎯 Processing: {recommendation.specialization}")
            print(f"   Spawning {spawn_count} agent(s)")
            print(f"   Priority: {recommendation.priority}")
            print(f"   Reason: {recommendation.reason}")
            
            # Spawn agents for this category
            for i in range(spawn_count):
                try:
                    agent_spec = self._create_sub_agent(
                        recommendation.specialization,
                        recommendation.metrics.to_dict(),
                        dry_run=dry_run
                    )
                    
                    if agent_spec:
                        spawned_agents.append(agent_spec)
                        total_spawned += 1
                        print(f"   ✅ Created: {agent_spec.human_name} ({agent_spec.specialization})")
                    else:
                        print(f"   ⚠️  Failed to create agent {i+1}")
                        
                except Exception as e:
                    print(f"   ❌ Error creating agent {i+1}: {e}")
                    continue
        
        print(f"\n📊 Total spawned: {total_spawned}/{max_total_spawns}")
        
        return spawned_agents
    
    def _create_sub_agent(self,
                         category: str,
                         workload_metrics: Dict[str, Any],
                         dry_run: bool = False) -> Optional[SubAgentSpec]:
        """
        Create a sub-agent for a specific category.
        
        Args:
            category: Specialization category (e.g., 'security', 'performance')
            workload_metrics: Metrics that triggered this spawn
            dry_run: If True, don't register agent
            
        Returns:
            SubAgentSpec if successful, None otherwise
        """
        # Select appropriate specialization
        specializations = self.CATEGORY_TO_SPECIALIZATION.get(category, [])
        if not specializations:
            print(f"Warning: No specializations found for category '{category}'")
            return None
        
        # Choose specialization with least agents (load balancing)
        specialization = self._select_least_loaded_specialization(specializations)
        
        # Generate unique agent ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        random_suffix = abs(hash(f"{specialization}{timestamp}")) % 10000
        agent_id = f"agent-{timestamp}-{random_suffix}"
        
        # Generate unique human name
        human_name = self._generate_unique_name()
        
        # Generate personality traits
        personality_traits = self._generate_personality()
        
        # Build justification
        justification = (
            f"Spawned to handle {category} workload: "
            f"{workload_metrics.get('open_issues', 0)} issues + "
            f"{workload_metrics.get('pending_prs', 0)} PRs. "
            f"Severity: {workload_metrics.get('bottleneck_severity', 'unknown')}"
        )
        
        # Create agent spec
        agent_spec = SubAgentSpec(
            agent_id=agent_id,
            human_name=human_name,
            specialization=specialization,
            category=category,
            personality=personality_traits['personality'],
            communication_style=personality_traits['communication_style'],
            creativity=personality_traits['creativity'],
            caution=personality_traits['caution'],
            speed=personality_traits['speed'],
            justification=justification,
            workload_metrics=workload_metrics
        )
        
        if not dry_run:
            # Register agent in registry
            success = self._register_agent(agent_spec)
            if not success:
                return None
            
            # Create agent profile
            self._create_agent_profile(agent_spec)
        
        return agent_spec
    
    def _select_least_loaded_specialization(self, 
                                           specializations: List[str]) -> str:
        """
        Select specialization with fewest active agents (load balancing).
        
        Args:
            specializations: List of possible specializations
            
        Returns:
            Selected specialization name
        """
        if not self.registry:
            # Return random if no registry
            import random
            return random.choice(specializations)
        
        try:
            # Count agents per specialization
            counts = {}
            agents = self.registry.list_agents(status='active')
            
            for spec in specializations:
                counts[spec] = sum(
                    1 for agent in agents 
                    if agent.get('specialization') == spec
                )
            
            # Select least loaded
            min_count = min(counts.values()) if counts else 0
            candidates = [spec for spec, count in counts.items() if count == min_count]
            
            import random
            return random.choice(candidates)
            
        except Exception as e:
            print(f"Warning: Could not determine least loaded: {e}")
            import random
            return random.choice(specializations)
    
    def _generate_unique_name(self) -> str:
        """
        Generate a unique human name for the agent.
        
        Returns:
            Unique human name
        """
        # Name pool (could expand this)
        names = [
            "Alex", "Jordan", "Taylor", "Morgan", "Casey",
            "Riley", "Quinn", "Avery", "Dakota", "Skylar",
            "Sage", "River", "Phoenix", "Rowan", "Kai",
            "Blake", "Drew", "Cameron", "Eden", "Harper"
        ]
        
        import random
        
        # Try to find unused name
        available = [name for name in names if name.lower() not in self.used_names]
        
        if available:
            name = random.choice(available)
            self.used_names.add(name.lower())
            return name
        
        # If all names used, append number
        for i in range(1, 100):
            name = f"{random.choice(names)}{i}"
            if name.lower() not in self.used_names:
                self.used_names.add(name.lower())
                return name
        
        # Fallback: use timestamp
        return f"Agent{datetime.now().strftime('%H%M%S')}"
    
    def _generate_personality(self) -> Dict[str, Any]:
        """
        Generate personality traits for sub-agent.
        
        Returns:
            Dictionary with personality, communication_style, and trait scores
        """
        import random
        
        personalities = [
            "methodical and precise",
            "enthusiastic and energetic",
            "calm and thoughtful",
            "bold and innovative",
            "analytical and strategic"
        ]
        
        comm_styles = [
            "uses technical jargon",
            "explains with analogies",
            "gets to the point",
            "adds encouraging emojis",
            "provides detailed explanations"
        ]
        
        return {
            'personality': random.choice(personalities),
            'communication_style': random.choice(comm_styles),
            'creativity': random.randint(50, 95),
            'caution': random.randint(30, 80),
            'speed': random.randint(40, 90)
        }
    
    def _register_agent(self, agent_spec: SubAgentSpec) -> bool:
        """
        Register agent in the registry.
        
        Args:
            agent_spec: Agent specification
            
        Returns:
            True if successful, False otherwise
        """
        if not self.registry:
            print("Warning: No registry available, skipping registration")
            return True  # Don't fail in dry run
        
        try:
            agent_data = {
                "id": agent_spec.agent_id,
                "name": f"🤖 {agent_spec.human_name}",
                "human_name": agent_spec.human_name,
                "specialization": agent_spec.specialization,
                "status": "active",
                "spawned_at": datetime.now(datetime.timezone.utc).isoformat(),
                "spawn_type": "workload_based",
                "spawn_reason": agent_spec.justification,
                "personality": agent_spec.personality,
                "communication_style": agent_spec.communication_style,
                "traits": {
                    "creativity": agent_spec.creativity,
                    "caution": agent_spec.caution,
                    "speed": agent_spec.speed
                },
                "metrics": {
                    "issues_resolved": 0,
                    "prs_merged": 0,
                    "reviews_given": 0,
                    "code_quality_score": 0.5,
                    "overall_score": 0.0
                },
                "contributions": [],
                "workload_context": agent_spec.workload_metrics
            }
            
            self.registry.add_agent(agent_data)
            return True
            
        except Exception as e:
            print(f"Error registering agent: {e}")
            return False
    
    def _create_agent_profile(self, agent_spec: SubAgentSpec):
        """
        Create agent profile markdown file.
        
        Args:
            agent_spec: Agent specification
        """
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        profile_path = self.profiles_dir / f"{agent_spec.agent_id}.md"
        
        # Get specialization description
        spec_desc = self._get_specialization_description(agent_spec.specialization)
        
        content = f"""# 🤖 {agent_spec.human_name}

**ID**: {agent_spec.agent_id}  
**Human Name**: {agent_spec.human_name}  
**Specialization**: {agent_spec.specialization}  
**Category**: {agent_spec.category}  
**Status**: 🟢 Active  
**Spawned**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Spawn Type**: Workload-Based Sub-Agent

## Personality

**Character**: {agent_spec.personality}  
**Communication Style**: {agent_spec.communication_style}

## Performance Traits

- **Creativity**: {agent_spec.creativity}/100
- **Caution**: {agent_spec.caution}/100
- **Speed**: {agent_spec.speed}/100

## Mission

{spec_desc}

## Spawn Context

{agent_spec.justification}

### Workload Metrics at Spawn

- **Open Issues**: {agent_spec.workload_metrics.get('open_issues', 0)}
- **Pending PRs**: {agent_spec.workload_metrics.get('pending_prs', 0)}
- **Active Agents**: {agent_spec.workload_metrics.get('active_agents', 0)}
- **Workload/Agent**: {agent_spec.workload_metrics.get('workload_per_agent', 0):.2f}
- **Bottleneck Severity**: {agent_spec.workload_metrics.get('bottleneck_severity', 'unknown')}

## Performance Metrics

- Issues Resolved: 0
- PRs Merged: 0
- Reviews Given: 0
- Overall Score: 0%

---

*Spawned by Workload-Based Sub-Agent System to address system bottlenecks*
*Part of @accelerate-specialist's autonomous workload optimization*
"""
        
        with open(profile_path, 'w') as f:
            f.write(content)
    
    def _get_specialization_description(self, specialization: str) -> str:
        """Get description for a specialization"""
        descriptions = {
            'secure-specialist': 'Security specialist focused on vulnerability detection and remediation',
            'secure-ninja': 'Security ninja specializing in access control and authentication',
            'secure-pro': 'Security professional focused on proactive threat detection',
            'accelerate-master': 'Performance optimization expert focused on system efficiency',
            'accelerate-specialist': 'Algorithm optimization specialist with Dijkstra\'s elegance',
            'organize-guru': 'Code organization guru focused on eliminating duplication',
            'engineer-master': 'API engineering expert with systematic approach',
            'assert-specialist': 'Test coverage specialist with specification-driven approach',
            'document-ninja': 'Documentation specialist creating clear tutorials',
            'create-guru': 'Infrastructure creation expert with visionary approach',
        }
        
        return descriptions.get(
            specialization,
            f'Specialized agent for {specialization} domain'
        )
    
    def generate_summary_report(self, 
                               spawned_agents: List[SubAgentSpec]) -> str:
        """
        Generate summary report of spawned agents.
        
        Args:
            spawned_agents: List of spawned agent specs
            
        Returns:
            Formatted report string
        """
        if not spawned_agents:
            return "## No Agents Spawned\n\nAll specializations operating within capacity."
        
        lines = [
            "# 🚀 Workload-Based Sub-Agent Spawn Report",
            f"\n**Timestamp:** {datetime.now().isoformat()}",
            f"**Total Spawned:** {len(spawned_agents)}",
            "\n## Spawned Agents\n"
        ]
        
        for i, agent in enumerate(spawned_agents, 1):
            lines.extend([
                f"### {i}. {agent.human_name} ({agent.specialization})",
                f"- **ID:** `{agent.agent_id}`",
                f"- **Category:** {agent.category}",
                f"- **Personality:** {agent.personality}",
                f"- **Justification:** {agent.justification}",
                f"- **Traits:** Creativity {agent.creativity}, "
                f"Caution {agent.caution}, Speed {agent.speed}",
                ""
            ])
        
        # Summary by category
        category_counts = {}
        for agent in spawned_agents:
            category_counts[agent.category] = category_counts.get(agent.category, 0) + 1
        
        lines.extend([
            "\n## Summary by Category\n"
        ])
        
        for category, count in sorted(category_counts.items()):
            lines.append(f"- **{category.capitalize()}:** {count} agent(s)")
        
        return '\n'.join(lines)


def main():
    """CLI interface for workload-based sub-agent spawner"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Spawn sub-agents based on workload analysis'
    )
    parser.add_argument(
        '--analysis', '-a',
        default='.github/agent-system/workload_analysis.json',
        help='Workload analysis JSON file'
    )
    parser.add_argument(
        '--max-spawns', '-m',
        type=int,
        default=5,
        help='Maximum agents to spawn'
    )
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Dry run - don\'t actually create agents'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Print detailed report'
    )
    
    args = parser.parse_args()
    
    # Load workload analysis
    try:
        with open(args.analysis, 'r') as f:
            analysis_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Analysis file not found: {args.analysis}")
        print("Run workload_monitor.py first to generate analysis")
        return 1
    
    # Convert to SpawningRecommendation objects
    recommendations = []
    for rec_data in analysis_data.get('recommendations', []):
        # Reconstruct WorkloadMetrics
        from workload_monitor import WorkloadMetrics
        metrics = WorkloadMetrics(**rec_data['metrics'])
        
        # Create recommendation
        rec = SpawningRecommendation(
            should_spawn=rec_data['should_spawn'],
            specialization=rec_data['specialization'],
            count=rec_data['count'],
            reason=rec_data['reason'],
            priority=rec_data['priority'],
            metrics=metrics
        )
        recommendations.append(rec)
    
    if not recommendations:
        print("✅ No spawning recommendations - system is balanced")
        return 0
    
    print(f"📋 Found {len(recommendations)} spawning recommendation(s)")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No agents will be created\n")
    
    # Create spawner
    spawner = WorkloadSubAgentSpawner()
    
    # Spawn agents
    print("\n🚀 Spawning sub-agents...\n")
    spawned_agents = spawner.spawn_from_recommendations(
        recommendations,
        max_total_spawns=args.max_spawns,
        dry_run=args.dry_run
    )
    
    # Generate report
    if args.report or spawned_agents:
        print("\n" + "=" * 80)
        report = spawner.generate_summary_report(spawned_agents)
        print(report)
        print("=" * 80)
    
    print(f"\n✅ Spawning complete! Created {len(spawned_agents)} sub-agent(s)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
