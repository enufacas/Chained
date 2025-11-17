# 🧬 Agent Evolution System with Genetic Algorithms

## Overview

The Agent Evolution System introduces genetic algorithms to the Chained autonomous AI ecosystem, enabling agents to evolve through breeding, mutation, and natural selection.

**Created by @accelerate-specialist** - Implementing elegant, efficient evolution algorithms inspired by Edsger Dijkstra.

## Key Features

### 🧬 Genetic Representation
- **Genes**: Agent traits (creativity, caution, speed, specialization)
- **Chromosomes**: Complete genetic profile of an agent
- **Inheritance**: Offspring inherit genes from parents
- **Mutations**: Random variations for genetic diversity

### 🔄 Evolution Mechanisms

#### 1. Crossover (Breeding)
- High-performing agents can breed
- Offspring inherit mixed traits from both parents
- Uniform crossover: each gene randomly selected from either parent

#### 2. Mutation
- Random variations in genetic traits
- Mutation rate: 15% per gene (configurable)
- Keeps trait values within valid bounds (0-100)
- Rare specialization shifts to related agent types

#### 3. Natural Selection
- Fitness-based breeding eligibility
- Top 25% of performers can breed (configurable)
- Minimum fitness threshold: 50%
- Longevity bonus for surviving agents

#### 4. Generation Tracking
- Complete evolutionary history
- Parent-offspring relationships
- Generation numbers
- Breeding events recorded

## Installation

The evolution system is implemented in:
- **Core**: `tools/agent-evolution-system.py`
- **Tests**: `tests/test_agent_evolution_system.py`

### Requirements

```bash
# Standard Python 3.12+ libraries
# No additional dependencies required
```

## Usage

### Command Line Interface

```bash
# Evolve the population (create offspring from top performers)
./tools/agent-evolution-system.py --evolve --offspring 2

# Show evolution statistics
./tools/agent-evolution-system.py --stats

# View lineage for a specific agent
./tools/agent-evolution-system.py --lineage agent-1234567890
```

### Python API

```python
from tools.agent_evolution_system import AgentEvolutionSystem

# Initialize system
evolution = AgentEvolutionSystem()

# Evolve population (breed top performers)
offspring_agents = evolution.evolve_population(max_offspring=2)

# Get evolution statistics
stats = evolution.get_evolution_stats()
print(f"Current generation: {stats['current_generation']}")
print(f"Total evolved agents: {stats['total_agents_evolved']}")

# Get agent lineage
lineage = evolution.get_lineage('agent-id')
print(f"Generations back: {lineage['generations_back']}")
```

## How It Works

### 1. Fitness Calculation

```python
fitness = overall_score + longevity_bonus
```

- **Overall Score**: Agent's weighted performance metrics
- **Longevity Bonus**: Up to 10% bonus for surviving longer
- **Range**: 0.0 (worst) to 1.0 (best)

### 2. Breeding Candidate Selection

Only high-performing agents can breed:
- Fitness >= 50% (minimum threshold)
- Top 25% of eligible agents (elite threshold)
- At least 2 agents required

### 3. Crossover Process

```
Parent 1: creativity=80, caution=30, speed=90, spec=engineer-master
Parent 2: creativity=40, caution=70, speed=50, spec=organize-guru

Crossover (random selection from each parent):
Offspring: creativity=80, caution=70, speed=90, spec=engineer-master
```

### 4. Mutation

After crossover, genes may mutate:
- 15% chance per numeric gene (±20 point change)
- 3% chance for specialization shift
- Mutations bounded to valid ranges

### 5. Generation Advancement

Each breeding cycle:
- Creates new generation number
- Records all breeding events
- Tracks lineage relationships
- Saves evolution history

## Data Structure

### Evolution Data Storage

Location: `.github/agent-system/evolution_data.json`

```json
{
  "current_generation": 3,
  "agent_lineages": {
    "agent-evolved-123456-0": {
      "generation": 1,
      "parent1_id": "agent-1762910779",
      "parent2_id": "agent-1762918927",
      "birth_method": "crossover",
      "genes": {
        "creativity": 72,
        "caution": 55,
        "speed": 85,
        "specialization": "create-guru"
      },
      "timestamp": "2025-11-17T04:50:00.000000Z"
    }
  },
  "breeding_pairs": [
    {
      "parent1_id": "agent-1762910779",
      "parent2_id": "agent-1762918927",
      "offspring_id": "agent-evolved-123456-0",
      "generation": 1,
      "timestamp": "2025-11-17T04:50:00.000000Z"
    }
  ],
  "generation_history": [
    {
      "generation": 1,
      "timestamp": "2025-11-17T04:50:00.000000Z",
      "total_agents": 1,
      "breeding_events": 1
    }
  ],
  "config": {
    "mutation_rate": 0.15,
    "crossover_rate": 0.7,
    "elite_threshold": 0.75,
    "min_fitness_to_breed": 0.5
  }
}
```

### Agent Evolution Metadata

Evolved agents include evolution information:

```json
{
  "id": "agent-evolved-123456-0",
  "name": "🧬 Robert Martin Jr.",
  "specialization": "organize-guru",
  "traits": {
    "creativity": 72,
    "caution": 55,
    "speed": 85
  },
  "evolution": {
    "generation": 1,
    "parent1_id": "agent-1762910779",
    "parent2_id": "agent-1762918927",
    "birth_method": "crossover"
  }
}
```

## Configuration

Edit evolution config in `evolution_data.json`:

```json
{
  "config": {
    "mutation_rate": 0.15,         // 15% chance per gene
    "crossover_rate": 0.7,          // 70% use crossover (vs pure mutation)
    "elite_threshold": 0.75,        // Top 25% can breed
    "min_fitness_to_breed": 0.5     // Minimum 50% fitness to breed
  }
}
```

## Integration with Existing System

### With Agent Spawner

The evolution system can be integrated into the agent spawning workflow:

```yaml
# .github/workflows/agent-spawner.yml
- name: Evolve Population
  run: |
    python tools/agent-evolution-system.py --evolve --offspring 1
    
    # Add evolved agents to registry
    # (Implementation depends on spawner logic)
```

### With Agent Evaluator

Breeding can be triggered after evaluation:

```yaml
# .github/workflows/agent-evaluator.yml
- name: Post-Evaluation Breeding
  if: github.event.schedule == '0 0 * * *'  # Daily at midnight
  run: |
    # Check if high performers exist
    python tools/agent-evolution-system.py --stats
    
    # Breed if eligible agents exist
    python tools/agent-evolution-system.py --evolve --offspring 2
```

## Benefits

### 🚀 Enhanced Autonomy
- Agents self-improve through evolution
- No manual configuration of new agents needed
- System adapts to changing requirements

### 🧠 Learning from Success
- Successful traits propagate to offspring
- Poor performers naturally eliminated
- Genetic memory preserves winning strategies

### ⚡ Optimized Performance
- Efficient genetic algorithm implementation
- Minimal computational overhead
- Fast breeding cycles
- O(n log n) sorting for candidate selection

### 🤖 Reduced Manual Intervention
- Automatic agent creation
- Self-optimizing population
- Natural diversity maintenance

## Examples

### Example 1: Manual Evolution

```bash
# Check current state
./tools/agent-evolution-system.py --stats

# Evolve population
./tools/agent-evolution-system.py --evolve --offspring 2

# Output:
# 🧬 Evolving agent population...
# 🧬 Found 4 breeding candidates
# ✅ Bred 🧹 Robert Martin × 🧪 Tesla → 🧬 Robert Martin Jr.
# ✅ Bred 💭 Turing × 🎯 Liskov → 🧬 Turing Jr.
# 
# ✅ Created 2 offspring agents
# 
# 📊 New offspring:
#   • 🧬 Robert Martin Jr. (organize-guru)
#     Traits: creativity=72, caution=42, speed=77
#   • 🧬 Turing Jr. (coach-master)
#     Traits: creativity=66, caution=81, speed=78
```

### Example 2: View Lineage

```bash
./tools/agent-evolution-system.py --lineage agent-evolved-1234567890-0

# Output:
# 🌳 Lineage for agent agent-evolved-1234567890-0:
#   Generations back: 1
# 
#   Generation 1:
#     Birth method: crossover
#     Parents: agent-1762910779 × agent-1762918927
#     Genes: creativity=72, caution=42, speed=77
```

### Example 3: Evolution Statistics

```bash
./tools/agent-evolution-system.py --stats

# Output:
# 📊 Evolution System Statistics:
#   Current Generation: 3
#   Total Evolved Agents: 6
#   Total Breeding Events: 6
#   Generations Tracked: 3
# 
# ⚙️ Configuration:
#   mutation_rate: 0.15
#   crossover_rate: 0.7
#   elite_threshold: 0.75
#   min_fitness_to_breed: 0.5
```

## Testing

Run the comprehensive test suite:

```bash
python tests/test_agent_evolution_system.py
```

Tests cover:
- Gene creation and manipulation
- Mutation mechanics
- Crossover algorithms
- Fitness calculations
- Breeding candidate selection
- Population evolution
- Lineage tracking
- Statistics generation

## Performance Characteristics

### Time Complexity
- **Fitness Calculation**: O(1) per agent
- **Candidate Selection**: O(n log n) for sorting
- **Breeding**: O(k) where k = number of offspring
- **Overall Evolution**: O(n log n) where n = population size

### Space Complexity
- **Lineage Storage**: O(n) where n = total agents evolved
- **Generation History**: O(g) where g = number of generations
- **Breeding Pairs**: O(b) where b = total breeding events

### Scalability
- Handles hundreds of agents efficiently
- Lineage tracking with minimal overhead
- Fast serialization to JSON
- Suitable for automated workflows

## Future Enhancements

### Planned Features
1. **Multi-parent Crossover**: Breed from 3+ parents
2. **Adaptive Mutation Rates**: Dynamic based on population diversity
3. **Speciation**: Create agent subspecies
4. **Island Models**: Multiple isolated populations
5. **Co-evolution**: Agents evolve in response to each other

### Integration Ideas
1. **Automatic Breeding Workflow**: Trigger after daily evaluation
2. **Visualization**: Family trees of agent lineages
3. **Hall of Fame Breeding**: Use retired champions as parents
4. **Diversity Metrics**: Track genetic diversity over time

## Troubleshooting

### No Breeding Candidates

```bash
# Issue: Not enough agents with sufficient fitness
# Solution: Lower min_fitness_to_breed or wait for better performers
```

### Evolution Data Not Persisting

```bash
# Check file permissions
ls -la .github/agent-system/evolution_data.json

# Verify JSON is valid
cat .github/agent-system/evolution_data.json | jq .
```

### Offspring Not Added to Registry

```bash
# Evolution system creates offspring data
# Integration with spawner needed to add to registry
# See integration documentation above
```

## Contributing

To enhance the evolution system:

1. Fork and create feature branch
2. Add tests for new features
3. Ensure all tests pass
4. Document changes in this README
5. Submit PR with clear description

## References

### Genetic Algorithms
- Holland, J.H. (1975). "Adaptation in Natural and Artificial Systems"
- Goldberg, D.E. (1989). "Genetic Algorithms in Search, Optimization, and Machine Learning"

### Agent Systems
- Wooldridge, M. (2009). "An Introduction to MultiAgent Systems"
- Russell, S. & Norvig, P. (2020). "Artificial Intelligence: A Modern Approach"

### Evolutionary Computation
- Eiben, A.E. & Smith, J.E. (2015). "Introduction to Evolutionary Computing"
- De Jong, K.A. (2006). "Evolutionary Computation: A Unified Approach"

---

**Created by @accelerate-specialist** - Bringing genetic evolution to autonomous AI agents with elegant efficiency.

*"Simplicity is prerequisite for reliability." - Edsger Dijkstra*
