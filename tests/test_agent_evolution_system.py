#!/usr/bin/env python3
"""
Tests for Agent Evolution System with Genetic Algorithms

Validates the genetic algorithm implementation for agent evolution.
Created by @accelerate-specialist
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

# Import with corrected module name
import importlib.util
spec = importlib.util.spec_from_file_location(
    "agent_evolution_system",
    Path(__file__).parent.parent / 'tools' / 'agent-evolution-system.py'
)
agent_evolution_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_evolution_system)

AgentGenes = agent_evolution_system.AgentGenes
EvolutionRecord = agent_evolution_system.EvolutionRecord
AgentEvolutionSystem = agent_evolution_system.AgentEvolutionSystem


def create_test_agent(agent_id: str, specialization: str = 'create-guru',
                     creativity: int = 50, caution: int = 50, speed: int = 50,
                     overall_score: float = 0.5) -> dict:
    """Create a test agent dictionary."""
    return {
        'id': agent_id,
        'name': f'Test Agent {agent_id}',
        'human_name': f'Agent {agent_id}',
        'specialization': specialization,
        'status': 'active',
        'spawned_at': datetime.utcnow().isoformat() + 'Z',
        'personality': 'test personality',
        'communication_style': 'test style',
        'traits': {
            'creativity': creativity,
            'caution': caution,
            'speed': speed
        },
        'metrics': {
            'issues_resolved': 1,
            'prs_merged': 1,
            'reviews_given': 0,
            'code_quality_score': 0.7,
            'overall_score': overall_score
        },
        'contributions': []
    }


class TestAgentGenes:
    """Test AgentGenes class."""
    
    def test_genes_creation(self):
        """Test creating genes."""
        genes = AgentGenes(
            creativity=75,
            caution=50,
            speed=90,
            specialization='engineer-master'
        )
        
        assert genes.creativity == 75
        assert genes.caution == 50
        assert genes.speed == 90
        assert genes.specialization == 'engineer-master'
        print("✅ Genes creation works")
    
    def test_genes_to_dict(self):
        """Test converting genes to dictionary."""
        genes = AgentGenes(70, 60, 80, 'organize-guru')
        gene_dict = genes.to_dict()
        
        assert gene_dict['creativity'] == 70
        assert gene_dict['caution'] == 60
        assert gene_dict['speed'] == 80
        assert gene_dict['specialization'] == 'organize-guru'
        print("✅ Genes to_dict works")
    
    def test_genes_from_dict(self):
        """Test creating genes from dictionary."""
        data = {
            'creativity': 65,
            'caution': 55,
            'speed': 75,
            'specialization': 'assert-specialist'
        }
        genes = AgentGenes.from_dict(data)
        
        assert genes.creativity == 65
        assert genes.caution == 55
        assert genes.speed == 75
        assert genes.specialization == 'assert-specialist'
        print("✅ Genes from_dict works")
    
    def test_mutation(self):
        """Test gene mutation."""
        genes = AgentGenes(50, 50, 50, 'create-guru')
        
        # Mutate with 100% rate to ensure changes
        mutated = genes.mutate(mutation_rate=1.0)
        
        # At least one trait should change
        traits_changed = (
            mutated.creativity != genes.creativity or
            mutated.caution != genes.caution or
            mutated.speed != genes.speed
        )
        
        assert traits_changed, "Mutation should change at least one trait"
        
        # Values should stay in valid range
        assert 0 <= mutated.creativity <= 100
        assert 0 <= mutated.caution <= 100
        assert 0 <= mutated.speed <= 100
        
        print("✅ Gene mutation works")
    
    def test_mutation_bounds(self):
        """Test mutation respects bounds."""
        # Test lower bound
        genes_low = AgentGenes(0, 0, 0, 'create-guru')
        mutated_low = genes_low.mutate(mutation_rate=1.0)
        
        assert mutated_low.creativity >= 0
        assert mutated_low.caution >= 0
        assert mutated_low.speed >= 0
        
        # Test upper bound
        genes_high = AgentGenes(100, 100, 100, 'create-guru')
        mutated_high = genes_high.mutate(mutation_rate=1.0)
        
        assert mutated_high.creativity <= 100
        assert mutated_high.caution <= 100
        assert mutated_high.speed <= 100
        
        print("✅ Mutation bounds work")


class TestEvolutionSystem:
    """Test AgentEvolutionSystem class."""
    
    def setup_temp_dirs(self):
        """Set up temporary directories for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = Path(self.temp_dir) / 'registry.json'
        self.evolution_path = Path(self.temp_dir) / 'evolution_data.json'
        
        # Create initial registry
        registry = {
            'version': '2.0.0',
            'agents': [],
            'hall_of_fame': [],
            'system_lead': None,
            'config': {}
        }
        
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def teardown_temp_dirs(self):
        """Clean up temporary directories."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test evolution system initialization."""
        self.setup_temp_dirs()
        
        try:
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            assert system.evolution_data is not None
            assert 'current_generation' in system.evolution_data
            assert system.evolution_data['current_generation'] == 0
            
            print("✅ Evolution system initialization works")
        finally:
            self.teardown_temp_dirs()
    
    def test_extract_genes(self):
        """Test extracting genes from agent."""
        self.setup_temp_dirs()
        
        try:
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            agent = create_test_agent('test-001', creativity=70, caution=60, speed=80)
            genes = system.extract_genes(agent)
            
            assert genes.creativity == 70
            assert genes.caution == 60
            assert genes.speed == 80
            assert genes.specialization == 'create-guru'
            
            print("✅ Gene extraction works")
        finally:
            self.teardown_temp_dirs()
    
    def test_calculate_fitness(self):
        """Test fitness calculation."""
        self.setup_temp_dirs()
        
        try:
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            # High performing agent
            agent_high = create_test_agent('test-001', overall_score=0.85)
            fitness_high = system.calculate_fitness(agent_high)
            
            # Low performing agent
            agent_low = create_test_agent('test-002', overall_score=0.25)
            fitness_low = system.calculate_fitness(agent_low)
            
            assert fitness_high > fitness_low, "Higher score should mean higher fitness"
            assert 0.0 <= fitness_high <= 1.0, "Fitness should be in [0, 1]"
            assert 0.0 <= fitness_low <= 1.0, "Fitness should be in [0, 1]"
            
            print("✅ Fitness calculation works")
        finally:
            self.teardown_temp_dirs()
    
    def test_crossover(self):
        """Test genetic crossover."""
        self.setup_temp_dirs()
        
        try:
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            parent1_genes = AgentGenes(80, 30, 90, 'engineer-master')
            parent2_genes = AgentGenes(40, 70, 50, 'organize-guru')
            
            offspring_genes = system.crossover(parent1_genes, parent2_genes)
            
            # Offspring should have genes from parents
            assert offspring_genes.creativity in [80, 40]
            assert offspring_genes.caution in [30, 70]
            assert offspring_genes.speed in [90, 50]
            assert offspring_genes.specialization in ['engineer-master', 'organize-guru']
            
            print("✅ Genetic crossover works")
        finally:
            self.teardown_temp_dirs()
    
    def test_breeding_candidates_selection(self):
        """Test selecting candidates for breeding."""
        self.setup_temp_dirs()
        
        try:
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            # Create agents with varying fitness
            agents = [
                create_test_agent('test-001', overall_score=0.85),  # High
                create_test_agent('test-002', overall_score=0.75),  # High
                create_test_agent('test-003', overall_score=0.55),  # Medium
                create_test_agent('test-004', overall_score=0.35),  # Low
                create_test_agent('test-005', overall_score=0.15),  # Very low
            ]
            
            candidates = system.select_breeding_candidates(agents)
            
            # Should select top performers
            assert len(candidates) >= 2, "Should have at least 2 candidates"
            
            # Verify candidates are high performers
            candidate_ids = [c['id'] for c in candidates]
            assert 'test-001' in candidate_ids, "Highest scorer should be candidate"
            
            print("✅ Breeding candidate selection works")
        finally:
            self.teardown_temp_dirs()
    
    def test_breed_agents(self):
        """Test breeding two agents."""
        self.setup_temp_dirs()
        
        try:
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            parent1 = create_test_agent('parent-001', creativity=80, caution=30, speed=90)
            parent2 = create_test_agent('parent-002', creativity=40, caution=70, speed=50)
            
            offspring = system.breed_agents(
                parent1, parent2,
                agent_id='offspring-001',
                agent_name='Test Offspring'
            )
            
            assert offspring['id'] == 'offspring-001'
            assert offspring['name'] == 'Test Offspring'
            assert offspring['status'] == 'active'
            assert 'evolution' in offspring
            assert offspring['evolution']['birth_method'] == 'crossover'
            assert offspring['evolution']['parent1_id'] == 'parent-001'
            assert offspring['evolution']['parent2_id'] == 'parent-002'
            
            # Check traits are within bounds
            assert 0 <= offspring['traits']['creativity'] <= 100
            assert 0 <= offspring['traits']['caution'] <= 100
            assert 0 <= offspring['traits']['speed'] <= 100
            
            print("✅ Agent breeding works")
        finally:
            self.teardown_temp_dirs()
    
    def test_evolve_population(self):
        """Test evolving an entire population."""
        self.setup_temp_dirs()
        
        try:
            # Create registry with multiple high-performing agents
            registry = {
                'version': '2.0.0',
                'agents': [
                    create_test_agent('agent-001', overall_score=0.85),
                    create_test_agent('agent-002', overall_score=0.80),
                    create_test_agent('agent-003', overall_score=0.75),
                    create_test_agent('agent-004', overall_score=0.70),
                ],
                'hall_of_fame': [],
                'system_lead': None,
                'config': {}
            }
            
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            # Evolve population
            offspring = system.evolve_population(max_offspring=2)
            
            assert len(offspring) <= 2, "Should create at most 2 offspring"
            assert len(offspring) > 0, "Should create at least 1 offspring"
            
            # Verify offspring structure
            for agent in offspring:
                assert 'id' in agent
                assert 'evolution' in agent
                assert agent['evolution']['birth_method'] == 'crossover'
                assert 'parent1_id' in agent['evolution']
                assert 'parent2_id' in agent['evolution']
            
            # Check generation advanced
            assert system.evolution_data['current_generation'] == 1
            
            print("✅ Population evolution works")
        finally:
            self.teardown_temp_dirs()
    
    def test_lineage_tracking(self):
        """Test lineage tracking."""
        self.setup_temp_dirs()
        
        try:
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            parent1 = create_test_agent('parent-001')
            parent2 = create_test_agent('parent-002')
            
            offspring = system.breed_agents(
                parent1, parent2,
                agent_id='offspring-001',
                agent_name='Offspring 1'
            )
            
            # Get lineage
            lineage = system.get_lineage('offspring-001')
            
            assert lineage['agent_id'] == 'offspring-001'
            assert lineage['generations_back'] >= 1
            assert len(lineage['lineage']) >= 1
            
            print("✅ Lineage tracking works")
        finally:
            self.teardown_temp_dirs()
    
    def test_evolution_stats(self):
        """Test evolution statistics."""
        self.setup_temp_dirs()
        
        try:
            system = AgentEvolutionSystem(
                registry_path=str(self.registry_path),
                evolution_data_path=str(self.evolution_path)
            )
            
            stats = system.get_evolution_stats()
            
            assert 'current_generation' in stats
            assert 'total_agents_evolved' in stats
            assert 'total_breeding_events' in stats
            assert 'config' in stats
            
            print("✅ Evolution statistics work")
        finally:
            self.teardown_temp_dirs()


def run_all_tests():
    """Run all tests."""
    print("🧬 Running Agent Evolution System Tests\n")
    
    # Test AgentGenes
    print("Testing AgentGenes...")
    genes_tests = TestAgentGenes()
    genes_tests.test_genes_creation()
    genes_tests.test_genes_to_dict()
    genes_tests.test_genes_from_dict()
    genes_tests.test_mutation()
    genes_tests.test_mutation_bounds()
    
    print("\nTesting AgentEvolutionSystem...")
    # Test AgentEvolutionSystem
    evolution_tests = TestEvolutionSystem()
    evolution_tests.test_initialization()
    evolution_tests.test_extract_genes()
    evolution_tests.test_calculate_fitness()
    evolution_tests.test_crossover()
    evolution_tests.test_breeding_candidates_selection()
    evolution_tests.test_breed_agents()
    evolution_tests.test_evolve_population()
    evolution_tests.test_lineage_tracking()
    evolution_tests.test_evolution_stats()
    
    print("\n" + "="*60)
    print("✅ All tests passed successfully!")
    print("="*60)


if __name__ == '__main__':
    run_all_tests()
