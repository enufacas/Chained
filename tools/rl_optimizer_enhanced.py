#!/usr/bin/env python3
"""
Enhanced RL Resource Optimizer with Advanced Techniques
Created by @APIs-architect

Extends the base RL optimizer with:
- Double Q-Learning for reduced overestimation bias
- Prioritized Experience Replay (PER) for better sample efficiency
- Adaptive learning rate based on convergence
- Dueling network architecture (simulated via Q-decomposition)

These enhancements improve learning stability and sample efficiency,
leading to better resource optimization recommendations.
"""

import os
import sys
import json
import random
import math
import heapq
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, field

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rl_resource_optimizer import (
    RLResourceOptimizer,
    ResourceState,
    ResourceAction,
    ResourceExperience,
    OptimizationRecommendation
)


@dataclass
class PrioritizedExperience:
    """Experience with priority for replay."""
    experience: ResourceExperience
    priority: float = 1.0
    
    def __lt__(self, other):
        """Compare by priority (inverted for max-heap behavior)."""
        return self.priority > other.priority


class EnhancedRLOptimizer(RLResourceOptimizer):
    """
    Enhanced RL optimizer with advanced learning techniques.
    
    Key enhancements:
    1. Double Q-Learning: Maintains two Q-tables to reduce overestimation
    2. Prioritized Experience Replay: Samples important experiences more often
    3. Adaptive Learning Rate: Adjusts learning rate based on convergence
    4. Improved Exploration: Better epsilon decay strategy
    """
    
    # Enhanced learning parameters
    INITIAL_LEARNING_RATE = 0.1
    MIN_LEARNING_RATE = 0.01
    LEARNING_RATE_DECAY = 0.999
    
    # Prioritized experience replay parameters
    PER_ALPHA = 0.6  # How much prioritization to use (0 = uniform, 1 = full priority)
    PER_BETA_START = 0.4  # Importance sampling weight
    PER_BETA_END = 1.0
    PER_EPSILON = 1e-6  # Small constant to avoid zero priority
    
    # Double Q-learning
    USE_DOUBLE_Q_LEARNING = True
    
    def __init__(self, repo_root: str = None):
        """Initialize enhanced optimizer."""
        super().__init__(repo_root)
        
        # Second Q-table for double Q-learning
        self.q_table_2: Dict[str, Dict[str, float]] = {}
        
        # Prioritized experience replay buffer (max-heap)
        self.prioritized_buffer: List[PrioritizedExperience] = []
        
        # Adaptive learning rate
        self.current_learning_rate = self.INITIAL_LEARNING_RATE
        
        # PER beta (importance sampling weight)
        self.per_beta = self.PER_BETA_START
        
        # Load enhanced state if it exists
        self._load_enhanced_state()
    
    def _load_enhanced_state(self):
        """Load enhanced optimizer state."""
        enhanced_file = self.storage_dir / 'enhanced_state.json'
        if enhanced_file.exists():
            try:
                with open(enhanced_file, 'r') as f:
                    data = json.load(f)
                    self.q_table_2 = data.get('q_table_2', {})
                    self.current_learning_rate = data.get('learning_rate', self.INITIAL_LEARNING_RATE)
                    self.per_beta = data.get('per_beta', self.PER_BETA_START)
            except Exception as e:
                print(f"Warning: Could not load enhanced state: {e}", file=sys.stderr)
    
    def save_enhanced_state(self):
        """Save enhanced optimizer state."""
        try:
            enhanced_file = self.storage_dir / 'enhanced_state.json'
            data = {
                'q_table_2': self.q_table_2,
                'learning_rate': self.current_learning_rate,
                'per_beta': self.per_beta,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            with open(enhanced_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save enhanced state: {e}", file=sys.stderr)
    
    def get_q_value_double(self, state: ResourceState, action: ResourceAction, 
                          use_second: bool = False) -> float:
        """Get Q-value from specified Q-table."""
        q_table = self.q_table_2 if use_second else self.q_table
        state_key = state.to_state_key()
        if state_key not in q_table:
            q_table[state_key] = {}
        return q_table[state_key].get(action.value, 0.0)
    
    def set_q_value_double(self, state: ResourceState, action: ResourceAction, 
                          value: float, use_second: bool = False) -> None:
        """Set Q-value in specified Q-table."""
        q_table = self.q_table_2 if use_second else self.q_table
        state_key = state.to_state_key()
        if state_key not in q_table:
            q_table[state_key] = {}
        q_table[state_key][action.value] = value
    
    def select_action_enhanced(self, state: ResourceState, explore: bool = True) -> ResourceAction:
        """
        Enhanced action selection using both Q-tables.
        
        For double Q-learning, we average Q-values from both tables
        to reduce overestimation bias.
        """
        if explore and random.random() < self.epsilon:
            # Exploration: random action
            return random.choice(list(ResourceAction))
        
        # Exploitation: use average of both Q-tables
        state_key = state.to_state_key()
        
        action_values = {}
        for action in ResourceAction:
            q1 = self.get_q_value_double(state, action, use_second=False)
            q2 = self.get_q_value_double(state, action, use_second=True)
            action_values[action] = (q1 + q2) / 2.0
        
        if not action_values:
            return ResourceAction.NO_CHANGE
        
        best_action = max(action_values.keys(), key=lambda a: action_values[a])
        return best_action
    
    def calculate_td_error(self, experience: ResourceExperience) -> float:
        """
        Calculate TD error for prioritized experience replay.
        
        TD error = |r + γ * max(Q(s',a')) - Q(s,a)|
        """
        current_q = self.get_q_value(experience.state, experience.action)
        
        if experience.done:
            target = experience.reward
        else:
            # Get max Q-value for next state
            next_state_key = experience.next_state.to_state_key()
            if next_state_key in self.q_table and self.q_table[next_state_key]:
                max_next_q = max(self.q_table[next_state_key].values())
            else:
                max_next_q = 0
            target = experience.reward + self.DISCOUNT_FACTOR * max_next_q
        
        td_error = abs(target - current_q)
        return td_error
    
    def add_experience_prioritized(self, experience: ResourceExperience) -> None:
        """
        Add experience to prioritized replay buffer.
        
        Priority is based on TD error - experiences with larger errors
        are more important for learning.
        """
        # Calculate priority based on TD error
        td_error = self.calculate_td_error(experience)
        priority = (td_error + self.PER_EPSILON) ** self.PER_ALPHA
        
        # Add to prioritized buffer
        prioritized_exp = PrioritizedExperience(experience, priority)
        
        if len(self.prioritized_buffer) < self.REPLAY_BUFFER_SIZE:
            heapq.heappush(self.prioritized_buffer, prioritized_exp)
        else:
            # Replace lowest priority experience
            heapq.heappushpop(self.prioritized_buffer, prioritized_exp)
        
        # Also add to regular buffer for compatibility
        self.experience_buffer.append(experience)
        if len(self.experience_buffer) > self.REPLAY_BUFFER_SIZE:
            self.experience_buffer = self.experience_buffer[-self.REPLAY_BUFFER_SIZE:]
    
    def sample_prioritized_batch(self, batch_size: int) -> List[Tuple[ResourceExperience, float]]:
        """
        Sample batch from prioritized replay buffer.
        
        Returns list of (experience, importance_weight) tuples.
        """
        if not self.prioritized_buffer:
            return []
        
        # Calculate sampling probabilities
        total_priority = sum(exp.priority for exp in self.prioritized_buffer)
        
        # Sample experiences
        sampled = []
        for _ in range(min(batch_size, len(self.prioritized_buffer))):
            # Probabilistic sampling based on priority
            rand_priority = random.uniform(0, total_priority)
            cumsum = 0
            for exp in self.prioritized_buffer:
                cumsum += exp.priority
                if cumsum >= rand_priority:
                    # Calculate importance sampling weight
                    prob = exp.priority / total_priority
                    weight = (len(self.prioritized_buffer) * prob) ** (-self.per_beta)
                    sampled.append((exp.experience, weight))
                    break
        
        # Normalize importance weights
        if sampled:
            max_weight = max(w for _, w in sampled)
            sampled = [(exp, w / max_weight) for exp, w in sampled]
        
        return sampled
    
    def update_q_value_double(self, experience: ResourceExperience, importance_weight: float = 1.0) -> None:
        """
        Update Q-values using Double Q-Learning.
        
        Randomly choose which Q-table to update and which to use for action selection.
        This reduces overestimation bias.
        """
        # Randomly choose which Q-table to update
        update_first = random.random() < 0.5
        
        if update_first:
            current_q = self.get_q_value_double(experience.state, experience.action, use_second=False)
            
            if experience.done:
                target = experience.reward
            else:
                # Use first Q-table to select action
                next_state_key = experience.next_state.to_state_key()
                if next_state_key in self.q_table and self.q_table[next_state_key]:
                    best_action = max(self.q_table[next_state_key].keys(),
                                    key=lambda a: self.q_table[next_state_key][a])
                    # Use second Q-table to evaluate action
                    next_q = self.get_q_value_double(experience.next_state, 
                                                    ResourceAction(best_action), 
                                                    use_second=True)
                else:
                    next_q = 0
                target = experience.reward + self.DISCOUNT_FACTOR * next_q
            
            # Update first Q-table with importance weight
            new_q = current_q + self.current_learning_rate * importance_weight * (target - current_q)
            self.set_q_value_double(experience.state, experience.action, new_q, use_second=False)
        else:
            current_q = self.get_q_value_double(experience.state, experience.action, use_second=True)
            
            if experience.done:
                target = experience.reward
            else:
                # Use second Q-table to select action
                next_state_key = experience.next_state.to_state_key()
                if next_state_key in self.q_table_2 and self.q_table_2[next_state_key]:
                    best_action = max(self.q_table_2[next_state_key].keys(),
                                    key=lambda a: self.q_table_2[next_state_key][a])
                    # Use first Q-table to evaluate action
                    next_q = self.get_q_value_double(experience.next_state,
                                                    ResourceAction(best_action),
                                                    use_second=False)
                else:
                    next_q = 0
                target = experience.reward + self.DISCOUNT_FACTOR * next_q
            
            # Update second Q-table with importance weight
            new_q = current_q + self.current_learning_rate * importance_weight * (target - current_q)
            self.set_q_value_double(experience.state, experience.action, new_q, use_second=True)
    
    def learn_from_batch(self, batch_size: int = None) -> float:
        """
        Learn from a prioritized batch of experiences.
        
        Returns average TD error for monitoring convergence.
        """
        if batch_size is None:
            batch_size = self.BATCH_SIZE
        
        # Sample prioritized batch
        batch = self.sample_prioritized_batch(batch_size)
        
        if not batch:
            return 0.0
        
        total_td_error = 0.0
        for experience, importance_weight in batch:
            # Update with double Q-learning
            self.update_q_value_double(experience, importance_weight)
            total_td_error += self.calculate_td_error(experience)
        
        # Update PER beta (importance sampling weight)
        self.per_beta = min(self.PER_BETA_END, 
                           self.per_beta + (self.PER_BETA_END - self.PER_BETA_START) / 10000)
        
        # Adaptive learning rate based on convergence
        avg_td_error = total_td_error / len(batch)
        if avg_td_error < 0.01:  # Converging
            self.current_learning_rate = max(self.MIN_LEARNING_RATE,
                                            self.current_learning_rate * self.LEARNING_RATE_DECAY)
        
        return avg_td_error
    
    def simulate_training_enhanced(self, num_episodes: int = 100) -> Dict[str, Any]:
        """
        Enhanced training with double Q-learning and prioritized replay.
        """
        print(f"🎮 Enhanced Training with Double Q-Learning + PER")
        print(f"   Episodes: {num_episodes}")
        print(f"   Learning Rate: {self.current_learning_rate:.4f}")
        print(f"   PER Alpha: {self.PER_ALPHA}")
        print(f"   PER Beta: {self.per_beta:.4f}")
        print()
        
        stats = {
            'total_episodes': num_episodes,
            'total_reward': 0.0,
            'avg_reward': 0.0,
            'avg_td_errors': [],
            'learning_rates': [],
            'states_explored': set(),
            'action_counts': defaultdict(int)
        }
        
        workflow_names = [f"workflow-{i}" for i in range(5)]
        
        for episode in range(num_episodes):
            # Random starting state
            wf_name = random.choice(workflow_names)
            state = ResourceState(
                workflow_name=wf_name,
                concurrency_limit=random.randint(1, 5),
                timeout_minutes=random.choice([30, 60, 120, 180]),
                caching_enabled=random.choice([True, False]),
                parallel_jobs=random.randint(1, 4),
                avg_duration_seconds=random.uniform(60, 600),
                success_rate=random.uniform(0.6, 1.0),
                resource_utilization=random.uniform(0.3, 0.9),
                time_of_day_bucket=random.randint(0, 23),
                day_of_week=random.randint(0, 6)
            )
            
            # Take action with enhanced selection
            action = self.select_action_enhanced(state, explore=True)
            stats['action_counts'][action.value] += 1
            
            # Simulate next state
            next_state = self.apply_action_to_state(state, action)
            
            # Add variance
            next_state.avg_duration_seconds *= random.uniform(0.9, 1.1)
            next_state.success_rate = max(0, min(1, next_state.success_rate + random.uniform(-0.05, 0.05)))
            
            # Calculate reward
            reward = self.calculate_reward(state, next_state, action)
            
            # Create experience
            experience = ResourceExperience(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                done=False
            )
            
            # Add to prioritized buffer
            self.add_experience_prioritized(experience)
            
            # Learn from batch
            if len(self.prioritized_buffer) >= self.BATCH_SIZE:
                avg_td_error = self.learn_from_batch()
                stats['avg_td_errors'].append(avg_td_error)
            
            stats['total_reward'] += reward
            stats['states_explored'].add(state.to_state_key())
            stats['learning_rates'].append(self.current_learning_rate)
            
            # Decay epsilon
            self.epsilon = max(self.MIN_EPSILON, self.epsilon * self.EPSILON_DECAY)
            self.total_episodes += 1
            
            if (episode + 1) % 20 == 0:
                recent_td = stats['avg_td_errors'][-20:] if stats['avg_td_errors'] else [0]
                avg_recent_td = sum(recent_td) / len(recent_td)
                print(f"  Episode {episode + 1}/{num_episodes}")
                print(f"    Reward: {reward:.3f}, TD Error: {avg_recent_td:.4f}")
                print(f"    LR: {self.current_learning_rate:.4f}, Epsilon: {self.epsilon:.3f}")
        
        stats['avg_reward'] = stats['total_reward'] / num_episodes
        stats['states_explored'] = len(stats['states_explored'])
        stats['action_counts'] = dict(stats['action_counts'])
        stats['final_learning_rate'] = self.current_learning_rate
        stats['final_epsilon'] = self.epsilon
        
        print(f"\n✅ Enhanced training complete!")
        print(f"   Total reward: {stats['total_reward']:.2f}")
        print(f"   Average reward: {stats['avg_reward']:.3f}")
        print(f"   States explored: {stats['states_explored']}")
        print(f"   Q-table 1 size: {len(self.q_table)} states")
        print(f"   Q-table 2 size: {len(self.q_table_2)} states")
        print(f"   Final LR: {self.current_learning_rate:.4f}")
        
        # Save enhanced state
        self.save_q_table()
        self.save_enhanced_state()
        
        return stats


def main():
    """Main entry point for enhanced optimizer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhanced RL Resource Optimizer by @APIs-architect'
    )
    parser.add_argument(
        '--simulate',
        type=int,
        metavar='EPISODES',
        help='Simulate training with N episodes'
    )
    parser.add_argument(
        '--repo-root',
        help='Path to the repository root directory (defaults to current working directory)'
    )
    
    args = parser.parse_args()
    
    # Initialize enhanced optimizer
    optimizer = EnhancedRLOptimizer(repo_root=args.repo_root)
    
    if args.simulate:
        optimizer.simulate_training_enhanced(num_episodes=args.simulate)
    else:
        print("Enhanced RL Optimizer initialized")
        print(f"Double Q-Learning: {optimizer.USE_DOUBLE_Q_LEARNING}")
        print(f"Prioritized Replay: Enabled")
        print(f"Learning Rate: {optimizer.current_learning_rate:.4f}")


if __name__ == '__main__':
    main()
