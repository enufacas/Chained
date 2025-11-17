#!/usr/bin/env python3
"""
Demo script showing the Agent Evolution System in action.

Creates a simulated scenario with high-performing agents
to demonstrate breeding, mutation, and evolution.

Created by @accelerate-specialist
"""

import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
import shutil

# Import the evolution system
import sys
sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "agent_evolution_system",
    Path(__file__).parent / 'agent-evolution-system.py'
)
agent_evolution_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_evolution_system)

AgentEvolutionSystem = agent_evolution_system.AgentEvolutionSystem


def create_demo_agent(agent_id: str, name: str, specialization: str,
                     creativity: int, caution: int, speed: int,
                     overall_score: float) -> dict:
    """Create a demo agent with specific traits."""
    return {
        'id': agent_id,
        'name': name,
        'human_name': name.split(' ', 1)[1] if ' ' in name else name,
        'specialization': specialization,
        'status': 'active',
        'spawned_at': datetime.utcnow().isoformat() + 'Z',
        'personality': 'innovative and efficient',
        'communication_style': 'clear and concise',
        'traits': {
            'creativity': creativity,
            'caution': caution,
            'speed': speed
        },
        'metrics': {
            'issues_resolved': int(overall_score * 10),
            'prs_merged': int(overall_score * 8),
            'reviews_given': int(overall_score * 5),
            'code_quality_score': min(1.0, overall_score + 0.2),
            'overall_score': overall_score
        },
        'contributions': []
    }


def run_demo():
    """Run the evolution system demo."""
    print("🧬 Agent Evolution System Demo")
    print("=" * 60)
    print()
    
    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp()
    registry_path = Path(temp_dir) / 'registry.json'
    evolution_path = Path(temp_dir) / 'evolution_data.json'
    
    try:
        # Create demo population with high-performing agents
        print("📋 Step 1: Creating Demo Population")
        print("-" * 60)
        
        demo_agents = [
            create_demo_agent(
                'agent-demo-001',
                '🧹 Robert Martin',
                'organize-guru',
                creativity=72, caution=42, speed=77,
                overall_score=0.85
            ),
            create_demo_agent(
                'agent-demo-002',
                '🧪 Tesla',
                'assert-specialist',
                creativity=62, caution=33, speed=98,
                overall_score=0.80
            ),
            create_demo_agent(
                'agent-demo-003',
                '💭 Turing',
                'coach-master',
                creativity=66, caution=81, speed=78,
                overall_score=0.75
            ),
            create_demo_agent(
                'agent-demo-004',
                '🎯 Liskov',
                'investigate-champion',
                creativity=78, caution=75, speed=95,
                overall_score=0.70
            ),
            create_demo_agent(
                'agent-demo-005',
                '🔨 Linus',
                'construct-specialist',
                creativity=55, caution=40, speed=88,
                overall_score=0.65
            ),
            create_demo_agent(
                'agent-demo-006',
                '🛡️ Bruce',
                'secure-specialist',
                creativity=50, caution=90, speed=60,
                overall_score=0.60
            ),
        ]
        
        # Create registry
        registry = {
            'version': '2.0.0',
            'agents': demo_agents,
            'hall_of_fame': [],
            'system_lead': None,
            'config': {}
        }
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"✅ Created {len(demo_agents)} demo agents")
        for agent in demo_agents:
            print(f"  • {agent['name']} ({agent['specialization']}) - "
                  f"Score: {agent['metrics']['overall_score']:.2f}")
        print()
        
        # Initialize evolution system
        print("📋 Step 2: Initializing Evolution System")
        print("-" * 60)
        evolution = AgentEvolutionSystem(
            registry_path=str(registry_path),
            evolution_data_path=str(evolution_path)
        )
        
        stats = evolution.get_evolution_stats()
        print(f"✅ Evolution system initialized")
        print(f"  • Current generation: {stats['current_generation']}")
        print(f"  • Mutation rate: {stats['config']['mutation_rate']}")
        print(f"  • Elite threshold: {stats['config']['elite_threshold']}")
        print()
        
        # Calculate fitness for all agents
        print("📋 Step 3: Calculating Fitness Scores")
        print("-" * 60)
        
        for agent in demo_agents[:4]:  # Show top 4
            fitness = evolution.calculate_fitness(agent)
            print(f"  • {agent['name']}: {fitness:.3f}")
        print()
        
        # Select breeding candidates
        print("📋 Step 4: Selecting Breeding Candidates")
        print("-" * 60)
        
        candidates = evolution.select_breeding_candidates(demo_agents)
        print(f"✅ Found {len(candidates)} eligible candidates")
        for candidate in candidates:
            print(f"  • {candidate['name']} - Score: {candidate['metrics']['overall_score']:.2f}")
        print()
        
        # Evolve population
        print("📋 Step 5: Evolving Population (Creating Offspring)")
        print("-" * 60)
        
        offspring = evolution.evolve_population(max_offspring=3)
        
        if offspring:
            print(f"\n✅ Successfully created {len(offspring)} offspring agents!")
            print()
            
            for i, child in enumerate(offspring, 1):
                print(f"🧬 Offspring #{i}: {child['name']}")
                print(f"  • ID: {child['id']}")
                print(f"  • Specialization: {child['specialization']}")
                print(f"  • Traits:")
                print(f"    - Creativity: {child['traits']['creativity']}")
                print(f"    - Caution: {child['traits']['caution']}")
                print(f"    - Speed: {child['traits']['speed']}")
                print(f"  • Evolution:")
                print(f"    - Generation: {child['evolution']['generation']}")
                print(f"    - Parent 1: {child['evolution']['parent1_id']}")
                print(f"    - Parent 2: {child['evolution']['parent2_id']}")
                print(f"    - Birth method: {child['evolution']['birth_method']}")
                print()
        
        # Show evolution statistics
        print("📋 Step 6: Evolution Statistics")
        print("-" * 60)
        
        stats = evolution.get_evolution_stats()
        print(f"  • Current generation: {stats['current_generation']}")
        print(f"  • Total agents evolved: {stats['total_agents_evolved']}")
        print(f"  • Total breeding events: {stats['total_breeding_events']}")
        print()
        
        # Show lineage for first offspring
        if offspring:
            print("📋 Step 7: Lineage Tracking Example")
            print("-" * 60)
            
            first_offspring_id = offspring[0]['id']
            lineage = evolution.get_lineage(first_offspring_id)
            
            print(f"🌳 Lineage for {offspring[0]['name']}:")
            print(f"  • Generations back: {lineage['generations_back']}")
            print(f"  • Direct ancestors: {len(lineage['lineage'])}")
            print()
            
            for record in lineage['lineage']:
                print(f"  Generation {record['generation']}:")
                print(f"    Birth: {record['birth_method']}")
                if record.get('parent1_id'):
                    print(f"    Parents: {record['parent1_id'][:15]}... × {record['parent2_id'][:15]}...")
                print()
        
        # Summary
        print("=" * 60)
        print("✅ Demo Complete!")
        print()
        print("Key Achievements:")
        print(f"  ✓ Created demo population of {len(demo_agents)} agents")
        print(f"  ✓ Selected {len(candidates)} breeding candidates")
        print(f"  ✓ Evolved {len(offspring)} offspring agents")
        print(f"  ✓ Advanced to generation {stats['current_generation']}")
        print(f"  ✓ Tracked complete evolutionary lineage")
        print()
        print("The evolution system successfully demonstrated:")
        print("  • Fitness-based selection")
        print("  • Genetic crossover (breeding)")
        print("  • Random mutations")
        print("  • Generation tracking")
        print("  • Lineage preservation")
        print()
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        print("🧹 Cleaned up demo files")
        print()
        print("To use with real agents, ensure they have overall_score >= 0.5")


if __name__ == '__main__':
    run_demo()
