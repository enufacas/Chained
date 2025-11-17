#!/usr/bin/env python3
"""
Agent Evolution System with Genetic Algorithms

Implements genetic algorithm-based evolution for the Chained agent system.
Agents with high performance can breed to create offspring, introducing
natural selection and evolution into the autonomous AI ecosystem.

Features:
- Genetic representation of agent traits
- Crossover (breeding) between successful agents
- Mutation for genetic diversity
- Fitness-based selection
- Generation tracking and history

Created by @accelerate-specialist - Inspired by Edsger Dijkstra's elegant efficiency.
"""

import json
import os
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import copy


@dataclass
class AgentGenes:
    """
    Genetic representation of an agent's inheritable traits.
    These form the "DNA" that can be passed to offspring.
    """
    creativity: int  # 0-100: Creative vs conservative
    caution: int     # 0-100: Cautious vs bold
    speed: int       # 0-100: Fast vs deliberate
    specialization: str  # Agent type (inherited or mutated)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert genes to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentGenes':
        """Create genes from dictionary."""
        return cls(**data)
    
    def mutate(self, mutation_rate: float = 0.1) -> 'AgentGenes':
        """
        Apply random mutations to genes.
        
        Args:
            mutation_rate: Probability of mutation per gene (0.0-1.0)
        
        Returns:
            New AgentGenes with potential mutations
        """
        mutated = copy.deepcopy(self)
        
        # Mutate numeric traits
        if random.random() < mutation_rate:
            mutated.creativity = max(0, min(100, self.creativity + random.randint(-20, 20)))
        
        if random.random() < mutation_rate:
            mutated.caution = max(0, min(100, self.caution + random.randint(-20, 20)))
        
        if random.random() < mutation_rate:
            mutated.speed = max(0, min(100, self.speed + random.randint(-20, 20)))
        
        # Small chance to mutate specialization (rare genetic shift)
        if random.random() < mutation_rate * 0.2:  # Much lower chance
            mutated.specialization = self._mutate_specialization(self.specialization)
        
        return mutated
    
    @staticmethod
    def _mutate_specialization(current: str) -> str:
        """Mutate specialization to a related one."""
        # Specialization families (similar roles)
        families = {
            'organize-guru': ['organize-expert', 'organize-specialist', 'refactor-champion'],
            'organize-expert': ['organize-guru', 'organize-specialist', 'cleaner-master'],
            'organize-specialist': ['organize-guru', 'organize-expert', 'simplify-pro'],
            'secure-specialist': ['secure-ninja', 'secure-pro', 'monitor-champion'],
            'secure-ninja': ['secure-specialist', 'secure-pro', 'guardian-master'],
            'secure-pro': ['secure-specialist', 'secure-ninja', 'monitor-champion'],
            'engineer-master': ['engineer-wizard', 'APIs-architect', 'construct-specialist'],
            'engineer-wizard': ['engineer-master', 'APIs-architect', 'create-guru'],
            'assert-specialist': ['assert-whiz', 'validator-pro', 'edge-cases-pro'],
            'assert-whiz': ['assert-specialist', 'validator-pro'],
            'investigate-champion': ['investigate-specialist'],
            'coach-master': ['coach-wizard', 'guide-wizard', 'support-master'],
            'create-guru': ['create-champion', 'develop-specialist', 'infrastructure-specialist'],
        }
        
        # Get related specializations or return current
        related = families.get(current, [current])
        if related:
            return random.choice(related)
        return current


@dataclass
class EvolutionRecord:
    """Record of an agent's evolutionary history."""
    generation: int
    parent1_id: Optional[str]
    parent2_id: Optional[str]
    birth_method: str  # 'spawn', 'crossover', 'mutation'
    genes: AgentGenes
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'generation': self.generation,
            'parent1_id': self.parent1_id,
            'parent2_id': self.parent2_id,
            'birth_method': self.birth_method,
            'genes': self.genes.to_dict(),
            'timestamp': self.timestamp
        }


class AgentEvolutionSystem:
    """
    Manages genetic algorithm-based evolution of agents.
    
    Features:
    - Breeding between high-performing agents
    - Genetic mutations for diversity
    - Fitness-based selection
    - Generation tracking
    - Evolution history
    """
    
    def __init__(self, registry_path: str = '.github/agent-system/registry.json',
                 evolution_data_path: str = '.github/agent-system/evolution_data.json'):
        """
        Initialize the evolution system.
        
        Args:
            registry_path: Path to agent registry
            evolution_data_path: Path to evolution data storage
        """
        self.registry_path = Path(registry_path)
        self.evolution_data_path = Path(evolution_data_path)
        self.evolution_data = self._load_evolution_data()
    
    def _load_evolution_data(self) -> Dict[str, Any]:
        """Load evolution data from file."""
        if self.evolution_data_path.exists():
            with open(self.evolution_data_path, 'r') as f:
                return json.load(f)
        
        # Initialize empty evolution data
        return {
            'current_generation': 0,
            'agent_lineages': {},  # agent_id -> evolution record
            'generation_history': [],  # list of generation summaries
            'breeding_pairs': [],  # history of successful breedings
            'config': {
                'mutation_rate': 0.15,  # 15% chance per gene
                'crossover_rate': 0.7,  # 70% chance to use crossover
                'elite_threshold': 0.75,  # Top 25% can breed
                'min_fitness_to_breed': 0.5,  # Minimum fitness to be parent
            }
        }
    
    def _save_evolution_data(self):
        """Save evolution data to file."""
        os.makedirs(self.evolution_data_path.parent, exist_ok=True)
        with open(self.evolution_data_path, 'w') as f:
            json.dump(self.evolution_data, f, indent=2)
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load agent registry."""
        with open(self.registry_path, 'r') as f:
            return json.load(f)
    
    def _save_registry(self, registry: Dict[str, Any]):
        """Save agent registry."""
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def extract_genes(self, agent: Dict[str, Any]) -> AgentGenes:
        """
        Extract genetic information from an agent.
        
        Args:
            agent: Agent dictionary from registry
        
        Returns:
            AgentGenes representing the agent's traits
        """
        traits = agent.get('traits', {})
        return AgentGenes(
            creativity=traits.get('creativity', 50),
            caution=traits.get('caution', 50),
            speed=traits.get('speed', 50),
            specialization=agent.get('specialization', 'create-guru')
        )
    
    def calculate_fitness(self, agent: Dict[str, Any]) -> float:
        """
        Calculate fitness score for an agent (0.0-1.0).
        Higher fitness = better performance = more likely to breed.
        
        Args:
            agent: Agent dictionary from registry
        
        Returns:
            Fitness score (0.0-1.0)
        """
        metrics = agent.get('metrics', {})
        
        # Get overall score (already weighted in registry)
        overall_score = metrics.get('overall_score', 0.0)
        
        # Bonus for longevity (agents that survive longer are more fit)
        spawned_at = agent.get('spawned_at', '')
        try:
            spawn_date = datetime.fromisoformat(spawned_at.replace('Z', '+00:00'))
            age_days = (datetime.now() - spawn_date.replace(tzinfo=None)).days
            longevity_bonus = min(0.1, age_days * 0.01)  # Up to 10% bonus
        except:
            longevity_bonus = 0.0
        
        # Final fitness with longevity bonus
        fitness = min(1.0, overall_score + longevity_bonus)
        
        return fitness
    
    def select_breeding_candidates(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Select agents eligible for breeding based on fitness.
        
        Args:
            agents: List of agent dictionaries
        
        Returns:
            List of agents eligible to breed
        """
        config = self.evolution_data['config']
        min_fitness = config['min_fitness_to_breed']
        elite_threshold = config['elite_threshold']
        
        # Calculate fitness for all agents
        agent_fitness = [(agent, self.calculate_fitness(agent)) for agent in agents]
        
        # Filter by minimum fitness
        eligible = [(agent, fitness) for agent, fitness in agent_fitness 
                   if fitness >= min_fitness]
        
        if not eligible:
            return []
        
        # Sort by fitness (descending)
        eligible.sort(key=lambda x: x[1], reverse=True)
        
        # Take top percentage as breeding candidates
        num_elite = max(2, int(len(eligible) * (1 - elite_threshold)))
        breeding_candidates = [agent for agent, _ in eligible[:num_elite]]
        
        return breeding_candidates
    
    def crossover(self, parent1_genes: AgentGenes, parent2_genes: AgentGenes) -> AgentGenes:
        """
        Perform genetic crossover between two parent genes.
        Creates offspring with mixed traits from both parents.
        
        Args:
            parent1_genes: Genes from first parent
            parent2_genes: Genes from second parent
        
        Returns:
            New AgentGenes for offspring
        """
        # Uniform crossover: randomly pick each gene from either parent
        offspring = AgentGenes(
            creativity=random.choice([parent1_genes.creativity, parent2_genes.creativity]),
            caution=random.choice([parent1_genes.caution, parent2_genes.caution]),
            speed=random.choice([parent1_genes.speed, parent2_genes.speed]),
            specialization=random.choice([parent1_genes.specialization, parent2_genes.specialization])
        )
        
        return offspring
    
    def breed_agents(self, parent1: Dict[str, Any], parent2: Dict[str, Any],
                    agent_id: str, agent_name: str) -> Dict[str, Any]:
        """
        Breed two agents to create offspring.
        
        Args:
            parent1: First parent agent dictionary
            parent2: Second parent agent dictionary
            agent_id: ID for new offspring agent
            agent_name: Name for new offspring agent
        
        Returns:
            New agent dictionary with bred traits
        """
        config = self.evolution_data['config']
        
        # Extract parent genes
        parent1_genes = self.extract_genes(parent1)
        parent2_genes = self.extract_genes(parent2)
        
        # Perform crossover
        offspring_genes = self.crossover(parent1_genes, parent2_genes)
        
        # Apply mutation
        offspring_genes = offspring_genes.mutate(config['mutation_rate'])
        
        # Create new agent with bred traits
        current_gen = self.evolution_data['current_generation']
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Create evolution record
        evolution_record = EvolutionRecord(
            generation=current_gen + 1,
            parent1_id=parent1.get('id'),
            parent2_id=parent2.get('id'),
            birth_method='crossover',
            genes=offspring_genes,
            timestamp=timestamp
        )
        
        # Store lineage
        self.evolution_data['agent_lineages'][agent_id] = evolution_record.to_dict()
        
        # Record breeding pair
        self.evolution_data['breeding_pairs'].append({
            'parent1_id': parent1.get('id'),
            'parent2_id': parent2.get('id'),
            'offspring_id': agent_id,
            'generation': current_gen + 1,
            'timestamp': timestamp
        })
        
        # Create offspring agent structure
        offspring = {
            'id': agent_id,
            'name': agent_name,
            'human_name': agent_name.split(' ', 1)[1] if ' ' in agent_name else agent_name,
            'specialization': offspring_genes.specialization,
            'status': 'active',
            'spawned_at': timestamp,
            'personality': self._inherit_personality(parent1, parent2),
            'communication_style': self._inherit_communication_style(parent1, parent2),
            'traits': {
                'creativity': offspring_genes.creativity,
                'caution': offspring_genes.caution,
                'speed': offspring_genes.speed
            },
            'metrics': {
                'issues_resolved': 0,
                'prs_merged': 0,
                'reviews_given': 0,
                'code_quality_score': 0.5,
                'overall_score': 0.43325
            },
            'contributions': [],
            'evolution': {
                'generation': evolution_record.generation,
                'parent1_id': parent1.get('id'),
                'parent2_id': parent2.get('id'),
                'birth_method': 'crossover'
            }
        }
        
        return offspring
    
    def _inherit_personality(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> str:
        """Mix personality traits from parents."""
        p1_traits = parent1.get('personality', '').split(' and ')
        p2_traits = parent2.get('personality', '').split(' and ')
        
        # Mix traits from both parents
        mixed = random.choice(p1_traits) if p1_traits else random.choice(p2_traits) if p2_traits else 'balanced'
        
        return mixed
    
    def _inherit_communication_style(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> str:
        """Mix communication styles from parents."""
        styles = [parent1.get('communication_style', ''), parent2.get('communication_style', '')]
        styles = [s for s in styles if s]
        
        return random.choice(styles) if styles else 'communicates clearly'
    
    def advance_generation(self):
        """Advance to the next generation."""
        self.evolution_data['current_generation'] += 1
        
        # Record generation summary
        self.evolution_data['generation_history'].append({
            'generation': self.evolution_data['current_generation'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_agents': len(self.evolution_data['agent_lineages']),
            'breeding_events': len(self.evolution_data['breeding_pairs'])
        })
        
        self._save_evolution_data()
    
    def evolve_population(self, max_offspring: int = 2) -> List[Dict[str, Any]]:
        """
        Evolve the agent population by breeding top performers.
        
        Args:
            max_offspring: Maximum number of offspring to create
        
        Returns:
            List of new offspring agents
        """
        # Load current registry
        registry = self._load_registry()
        agents = registry.get('agents', [])
        
        if len(agents) < 2:
            print("⚠️ Not enough agents to breed (need at least 2)")
            return []
        
        # Select breeding candidates
        candidates = self.select_breeding_candidates(agents)
        
        if len(candidates) < 2:
            print("⚠️ Not enough eligible candidates for breeding")
            return []
        
        print(f"🧬 Found {len(candidates)} breeding candidates")
        
        # Create offspring
        offspring_list = []
        for i in range(min(max_offspring, len(candidates) // 2)):
            # Select two different parents
            parent1 = random.choice(candidates)
            parent2 = random.choice([c for c in candidates if c['id'] != parent1['id']])
            
            # Generate unique ID and name for offspring
            offspring_id = f"agent-evolved-{int(datetime.utcnow().timestamp())}-{i}"
            offspring_name = f"🧬 {parent1.get('human_name', 'Agent')} Jr."
            
            # Breed agents
            offspring = self.breed_agents(parent1, parent2, offspring_id, offspring_name)
            offspring_list.append(offspring)
            
            print(f"✅ Bred {parent1['name']} × {parent2['name']} → {offspring_name}")
        
        # Advance generation
        if offspring_list:
            self.advance_generation()
            self._save_evolution_data()
        
        return offspring_list
    
    def get_lineage(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the complete evolutionary lineage of an agent.
        
        Args:
            agent_id: Agent ID to trace
        
        Returns:
            Dictionary with lineage information
        """
        lineage = []
        current_id = agent_id
        
        while current_id in self.evolution_data['agent_lineages']:
            record = self.evolution_data['agent_lineages'][current_id]
            lineage.append(record)
            
            # Trace back to parent
            parent1_id = record.get('parent1_id')
            if parent1_id and parent1_id in self.evolution_data['agent_lineages']:
                current_id = parent1_id
            else:
                break
        
        return {
            'agent_id': agent_id,
            'generations_back': len(lineage),
            'lineage': lineage
        }
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Get statistics about the evolution system."""
        return {
            'current_generation': self.evolution_data['current_generation'],
            'total_agents_evolved': len(self.evolution_data['agent_lineages']),
            'total_breeding_events': len(self.evolution_data['breeding_pairs']),
            'generation_history_length': len(self.evolution_data['generation_history']),
            'config': self.evolution_data['config']
        }


def main():
    """Main entry point for agent evolution system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Evolution System with Genetic Algorithms')
    parser.add_argument('--evolve', action='store_true', help='Evolve the population')
    parser.add_argument('--offspring', type=int, default=2, help='Number of offspring to create')
    parser.add_argument('--stats', action='store_true', help='Show evolution statistics')
    parser.add_argument('--lineage', type=str, help='Show lineage for agent ID')
    
    args = parser.parse_args()
    
    evolution_system = AgentEvolutionSystem()
    
    if args.evolve:
        print("🧬 Evolving agent population...")
        offspring = evolution_system.evolve_population(max_offspring=args.offspring)
        print(f"\n✅ Created {len(offspring)} offspring agents")
        
        if offspring:
            print("\n📊 New offspring:")
            for agent in offspring:
                print(f"  • {agent['name']} ({agent['specialization']})")
                print(f"    Traits: creativity={agent['traits']['creativity']}, "
                      f"caution={agent['traits']['caution']}, speed={agent['traits']['speed']}")
    
    elif args.stats:
        stats = evolution_system.get_evolution_stats()
        print("📊 Evolution System Statistics:")
        print(f"  Current Generation: {stats['current_generation']}")
        print(f"  Total Evolved Agents: {stats['total_agents_evolved']}")
        print(f"  Total Breeding Events: {stats['total_breeding_events']}")
        print(f"  Generations Tracked: {stats['generation_history_length']}")
        print(f"\n⚙️ Configuration:")
        for key, value in stats['config'].items():
            print(f"  {key}: {value}")
    
    elif args.lineage:
        lineage = evolution_system.get_lineage(args.lineage)
        print(f"🌳 Lineage for agent {args.lineage}:")
        print(f"  Generations back: {lineage['generations_back']}")
        for i, record in enumerate(lineage['lineage']):
            print(f"\n  Generation {record['generation']}:")
            print(f"    Birth method: {record['birth_method']}")
            if record.get('parent1_id'):
                print(f"    Parents: {record['parent1_id']} × {record['parent2_id']}")
            print(f"    Genes: creativity={record['genes']['creativity']}, "
                  f"caution={record['genes']['caution']}, speed={record['genes']['speed']}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
