#!/usr/bin/env python3
"""
Reinforcement Learning Resource Optimizer for GitHub Actions
Created by @create-guru

Uses Q-Learning to optimize GitHub Actions resource allocation:
- Runner type selection (ubuntu, windows, macos, self-hosted)
- Concurrency settings
- Timeout configurations
- Caching strategies
- Job parallelization

The agent learns from workflow execution history to minimize:
- Total execution time
- Resource waste (unused time quota)
- Workflow failures
- Cost (for self-hosted runners)

This extends the existing AI workflow predictor with RL-based optimization.
"""

import os
import sys
import json
import random
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib


class ResourceAction(Enum):
    """Possible actions the RL agent can take."""
    INCREASE_CONCURRENCY = "increase_concurrency"
    DECREASE_CONCURRENCY = "decrease_concurrency"
    EXTEND_TIMEOUT = "extend_timeout"
    REDUCE_TIMEOUT = "reduce_timeout"
    ENABLE_CACHING = "enable_caching"
    DISABLE_CACHING = "disable_caching"
    PARALLELIZE_JOBS = "parallelize_jobs"
    SERIALIZE_JOBS = "serialize_jobs"
    NO_CHANGE = "no_change"


@dataclass
class ResourceState:
    """Current state of a workflow's resource configuration."""
    workflow_name: str
    concurrency_limit: int  # 1-10
    timeout_minutes: int  # 1-360
    caching_enabled: bool
    parallel_jobs: int  # 1-10
    avg_duration_seconds: float
    success_rate: float  # 0-1
    resource_utilization: float  # 0-1
    time_of_day_bucket: int  # 0-23 (hour)
    day_of_week: int  # 0-6

    # Discretization constants for state key generation
    DURATION_BUCKET_SIZE_SECONDS: int = 120  # 2-minute buckets
    MAX_DURATION_BUCKETS: int = 5  # Maximum 5 buckets (0-5)
    TIME_BUCKET_SIZE_HOURS: int = 6  # 6-hour buckets (0-3)

    def to_state_key(self) -> str:
        """Convert state to a hashable key for Q-table lookup."""
        # Discretize continuous values into buckets
        duration_bucket = min(self.MAX_DURATION_BUCKETS, int(self.avg_duration_seconds / self.DURATION_BUCKET_SIZE_SECONDS))
        success_bucket = int(self.success_rate * 10)  # 0-10
        util_bucket = int(self.resource_utilization * 5)  # 0-5
        time_bucket = self.time_of_day_bucket // self.TIME_BUCKET_SIZE_HOURS

        return f"{self.concurrency_limit}_{self.timeout_minutes // 60}_{int(self.caching_enabled)}_{self.parallel_jobs}_{duration_bucket}_{success_bucket}_{util_bucket}_{time_bucket}_{self.day_of_week}"


@dataclass
class ResourceExperience:
    """Experience tuple for RL learning."""
    state: ResourceState
    action: ResourceAction
    reward: float
    next_state: ResourceState
    done: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OptimizationRecommendation:
    """Recommendation from the RL optimizer."""
    workflow_name: str
    current_state: Dict[str, Any]
    recommended_action: str
    expected_improvement: float  # percentage
    confidence: float  # 0-1
    reasoning: List[str]
    alternative_actions: List[Dict[str, Any]]


class RLResourceOptimizer:
    """
    Reinforcement Learning agent for GitHub Actions resource optimization.

    Uses Q-Learning with experience replay to learn optimal resource
    configurations for workflows based on historical execution data.

    Key features:
    - Epsilon-greedy exploration strategy
    - Experience replay buffer for stable learning
    - State discretization for manageable Q-table
    - Multi-objective reward function
    """

    # Learning parameters
    LEARNING_RATE = 0.1  # Alpha: how much to update Q-values
    DISCOUNT_FACTOR = 0.95  # Gamma: importance of future rewards
    INITIAL_EPSILON = 1.0  # Starting exploration rate
    EPSILON_DECAY = 0.995  # How fast to reduce exploration
    MIN_EPSILON = 0.05  # Minimum exploration rate
    REPLAY_BUFFER_SIZE = 1000  # Max experiences to store
    BATCH_SIZE = 32  # Mini-batch size for learning

    # Reward weights
    REWARD_WEIGHT_DURATION = 0.4
    REWARD_WEIGHT_SUCCESS = 0.35
    REWARD_WEIGHT_UTILIZATION = 0.25

    # Scaling constants
    Q_VALUE_TO_PERCENTAGE_SCALE = 10  # Scale Q-values to percentage improvements

    # Simulation variance parameters
    SIMULATION_DURATION_VARIANCE_MIN = 0.9
    SIMULATION_DURATION_VARIANCE_MAX = 1.1
    SIMULATION_SUCCESS_RATE_VARIANCE = 0.05

    def __init__(self, repo_root: str = None):
        """Initialize the RL optimizer."""
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path.cwd()

        # Storage paths
        self.storage_dir = self.repo_root / '.github' / 'rl-optimizer'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.q_table_file = self.storage_dir / 'q_table.json'
        self.experience_file = self.storage_dir / 'experiences.json'
        self.metrics_file = self.storage_dir / 'metrics.json'

        # Initialize Q-table: state -> action -> Q-value
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Current epsilon for exploration (may be overwritten by load)
        self.epsilon = self.INITIAL_EPSILON
        self.total_episodes = 0
        
        # Load persisted state (will update epsilon if saved)
        self.load_q_table()

        # Experience replay buffer
        self.experience_buffer: List[ResourceExperience] = []
        self.load_experiences()

        # Track workflow states
        self.workflow_states: Dict[str, ResourceState] = {}

        # Load metrics
        self.metrics = self._load_metrics()

    def load_q_table(self) -> None:
        """Load Q-table from persistent storage."""
        if self.q_table_file.exists():
            try:
                with open(self.q_table_file, 'r') as f:
                    data = json.load(f)
                    self.q_table = data.get('q_table', {})
                    self.epsilon = data.get('epsilon', self.INITIAL_EPSILON)
                    self.total_episodes = data.get('total_episodes', 0)
            except Exception as e:
                print(f"Warning: Could not load Q-table: {e}", file=sys.stderr)
                self.q_table = {}

    def save_q_table(self) -> None:
        """Save Q-table to persistent storage."""
        try:
            data = {
                'q_table': self.q_table,
                'epsilon': self.epsilon,
                'total_episodes': self.total_episodes,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'stats': {
                    'num_states': len(self.q_table),
                    'total_q_entries': sum(len(actions) for actions in self.q_table.values())
                }
            }
            with open(self.q_table_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Q-table: {e}", file=sys.stderr)

    def load_experiences(self) -> None:
        """Load experience buffer from storage."""
        if self.experience_file.exists():
            try:
                with open(self.experience_file, 'r') as f:
                    data = json.load(f)
                    # Keep only recent experiences
                    self.experience_buffer = []
                    for exp_data in data.get('experiences', [])[-self.REPLAY_BUFFER_SIZE:]:
                        self.experience_buffer.append(self._experience_from_dict(exp_data))
            except Exception as e:
                print(f"Warning: Could not load experiences: {e}", file=sys.stderr)

    def save_experiences(self) -> None:
        """Save experience buffer to storage."""
        try:
            data = {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_experiences': len(self.experience_buffer),
                'experiences': [self._experience_to_dict(exp) for exp in self.experience_buffer[-self.REPLAY_BUFFER_SIZE:]]
            }
            with open(self.experience_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save experiences: {e}", file=sys.stderr)

    def _experience_to_dict(self, exp: ResourceExperience) -> Dict[str, Any]:
        """Convert experience to dictionary for serialization."""
        return {
            'state': asdict(exp.state),
            'action': exp.action.value,
            'reward': exp.reward,
            'next_state': asdict(exp.next_state),
            'done': exp.done,
            'timestamp': exp.timestamp.isoformat()
        }

    def _experience_from_dict(self, data: Dict[str, Any]) -> ResourceExperience:
        """Reconstruct experience from dictionary."""
        return ResourceExperience(
            state=ResourceState(**data['state']),
            action=ResourceAction(data['action']),
            reward=data['reward'],
            next_state=ResourceState(**data['next_state']),
            done=data['done'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        )

    def _load_metrics(self) -> Dict[str, Any]:
        """Load optimizer metrics."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'avg_improvement': 0.0,
            'workflow_improvements': {}
        }

    def _save_metrics(self) -> None:
        """Save optimizer metrics."""
        try:
            self.metrics['last_updated'] = datetime.now(timezone.utc).isoformat()
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}", file=sys.stderr)

    def get_current_state(self, workflow_name: str,
                         execution_history: Optional[List[Dict]] = None) -> ResourceState:
        """
        Get current resource state for a workflow.

        Args:
            workflow_name: Name of the workflow
            execution_history: Optional list of recent executions

        Returns:
            Current ResourceState for the workflow
        """
        now = datetime.now(timezone.utc)

        # Default state
        default_state = ResourceState(
            workflow_name=workflow_name,
            concurrency_limit=1,
            timeout_minutes=60,
            caching_enabled=False,
            parallel_jobs=1,
            avg_duration_seconds=300,
            success_rate=0.8,
            resource_utilization=0.5,
            time_of_day_bucket=now.hour,
            day_of_week=now.weekday()
        )

        if not execution_history:
            return self.workflow_states.get(workflow_name, default_state)

        # Calculate metrics from history
        durations = [e.get('duration_seconds', 300) for e in execution_history]
        successes = [e.get('success', True) for e in execution_history]

        avg_duration = sum(durations) / len(durations) if durations else 300
        success_rate = sum(successes) / len(successes) if successes else 0.8

        # Estimate resource utilization based on duration variance
        if len(durations) > 1 and avg_duration > 0:
            duration_std = (sum((d - avg_duration) ** 2 for d in durations) / len(durations)) ** 0.5
            utilization = 1 - min(1, duration_std / avg_duration)
        else:
            utilization = 0.5

        state = ResourceState(
            workflow_name=workflow_name,
            concurrency_limit=self._infer_concurrency(execution_history),
            timeout_minutes=self._infer_timeout(execution_history, avg_duration),
            caching_enabled=self._infer_caching(execution_history),
            parallel_jobs=self._infer_parallelism(execution_history),
            avg_duration_seconds=avg_duration,
            success_rate=success_rate,
            resource_utilization=utilization,
            time_of_day_bucket=now.hour,
            day_of_week=now.weekday()
        )

        self.workflow_states[workflow_name] = state
        return state

    def _infer_concurrency(self, history: List[Dict]) -> int:
        """Infer current concurrency setting from execution patterns."""
        # Count concurrent runs in the same time window
        if len(history) < 2:
            return 1

        concurrent_count = 1
        for i, run1 in enumerate(history):
            start1 = run1.get('start_time')
            end1 = run1.get('end_time')
            if not start1 or not end1:
                continue

            count = 1
            for j, run2 in enumerate(history):
                if i == j:
                    continue
                start2 = run2.get('start_time')
                end2 = run2.get('end_time')
                if not start2 or not end2:
                    continue

                # Check for overlap
                if start1 <= end2 and start2 <= end1:
                    count += 1

            concurrent_count = max(concurrent_count, count)

        return min(10, concurrent_count)

    def _infer_timeout(self, history: List[Dict], avg_duration: float) -> int:
        """Infer timeout setting based on max duration."""
        if not history:
            return 60

        max_duration = max(e.get('duration_seconds', 0) for e in history)
        # Timeout should be at least 2x the max observed duration
        timeout = max(10, int((max_duration * 2) / 60))
        return min(360, timeout)

    def _infer_caching(self, history: List[Dict]) -> bool:
        """Infer if caching is likely enabled based on duration patterns."""
        if len(history) < 3:
            return False

        durations = sorted(e.get('duration_seconds', 0) for e in history)
        # If there's a significant speed difference, caching might be in use
        if durations[-1] > 0 and durations[0] / durations[-1] < 0.7:
            return True
        return False

    def _infer_parallelism(self, history: List[Dict]) -> int:
        """Infer parallel job count from resource usage."""
        if not history:
            return 1

        # Check for concurrent job indicators in resource usage
        resource_usage = [e.get('resource_usage', {}) for e in history if e.get('resource_usage')]
        if not resource_usage:
            return 1

        # Higher CPU usage suggests more parallel jobs
        avg_cpu = sum(r.get('estimated_cpu_percent', 20) for r in resource_usage) / len(resource_usage)
        if avg_cpu > 70:
            return 4
        elif avg_cpu > 50:
            return 2
        return 1

    def get_q_value(self, state: ResourceState, action: ResourceAction) -> float:
        """Get Q-value for a state-action pair."""
        state_key = state.to_state_key()
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        return self.q_table[state_key].get(action.value, 0.0)

    def set_q_value(self, state: ResourceState, action: ResourceAction, value: float) -> None:
        """Set Q-value for a state-action pair."""
        state_key = state.to_state_key()
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        self.q_table[state_key][action.value] = value

    def select_action(self, state: ResourceState, explore: bool = True) -> ResourceAction:
        """
        Select an action using epsilon-greedy strategy.

        Args:
            state: Current state
            explore: Whether to explore (True) or exploit (False)

        Returns:
            Selected action
        """
        if explore and random.random() < self.epsilon:
            # Exploration: random action
            return random.choice(list(ResourceAction))

        # Exploitation: best known action
        state_key = state.to_state_key()
        if state_key not in self.q_table or not self.q_table[state_key]:
            return ResourceAction.NO_CHANGE

        action_values = self.q_table[state_key]
        best_action = max(action_values.keys(), key=lambda a: action_values[a])
        return ResourceAction(best_action)

    def calculate_reward(self, state: ResourceState, next_state: ResourceState,
                        action: ResourceAction) -> float:
        """
        Calculate reward for a state transition.

        Multi-objective reward function considering:
        - Duration improvement (negative change is good)
        - Success rate improvement
        - Resource utilization improvement
        """
        # Duration improvement (normalize by expected range)
        duration_improvement = (state.avg_duration_seconds - next_state.avg_duration_seconds) / max(state.avg_duration_seconds, 1)
        duration_reward = self.REWARD_WEIGHT_DURATION * duration_improvement

        # Success rate improvement
        success_improvement = next_state.success_rate - state.success_rate
        success_reward = self.REWARD_WEIGHT_SUCCESS * success_improvement * 10  # Scale up

        # Utilization improvement
        util_improvement = next_state.resource_utilization - state.resource_utilization
        util_reward = self.REWARD_WEIGHT_UTILIZATION * util_improvement * 5

        # Penalty for actions that don't improve anything
        if action == ResourceAction.NO_CHANGE:
            no_change_penalty = 0.0
        else:
            total_improvement = duration_improvement + success_improvement + util_improvement
            no_change_penalty = -0.1 if total_improvement <= 0 else 0

        total_reward = duration_reward + success_reward + util_reward + no_change_penalty

        # Clamp reward to reasonable range
        return max(-1, min(1, total_reward))

    def update_q_value(self, experience: ResourceExperience) -> None:
        """
        Update Q-value using the Q-learning update rule.

        Q(s,a) = Q(s,a) + α * (r + γ * max(Q(s',a')) - Q(s,a))
        """
        current_q = self.get_q_value(experience.state, experience.action)

        if experience.done:
            target = experience.reward
        else:
            # Get max Q-value for next state
            next_state_key = experience.next_state.to_state_key()
            if next_state_key in self.q_table:
                max_next_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0
            else:
                max_next_q = 0
            target = experience.reward + self.DISCOUNT_FACTOR * max_next_q

        new_q = current_q + self.LEARNING_RATE * (target - current_q)
        self.set_q_value(experience.state, experience.action, new_q)

    def learn_from_experience(self, state: ResourceState, action: ResourceAction,
                             next_state: ResourceState, done: bool = False) -> float:
        """
        Learn from a single experience.

        Args:
            state: State before action
            action: Action taken
            next_state: State after action
            done: Whether this is a terminal state

        Returns:
            Calculated reward
        """
        reward = self.calculate_reward(state, next_state, action)

        experience = ResourceExperience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done
        )

        # Add to experience buffer
        self.experience_buffer.append(experience)
        if len(self.experience_buffer) > self.REPLAY_BUFFER_SIZE:
            self.experience_buffer.pop(0)

        # Update Q-value
        self.update_q_value(experience)

        # Experience replay: sample from buffer and learn
        if len(self.experience_buffer) >= self.BATCH_SIZE:
            batch = random.sample(self.experience_buffer, self.BATCH_SIZE)
            for exp in batch:
                self.update_q_value(exp)

        # Decay epsilon
        self.epsilon = max(self.MIN_EPSILON, self.epsilon * self.EPSILON_DECAY)
        self.total_episodes += 1

        # Persist learning
        self.save_q_table()
        self.save_experiences()

        return reward

    def get_recommendation(self, workflow_name: str,
                          execution_history: Optional[List[Dict]] = None) -> OptimizationRecommendation:
        """
        Get optimization recommendation for a workflow.

        Args:
            workflow_name: Name of the workflow
            execution_history: Optional recent execution history

        Returns:
            OptimizationRecommendation with suggested action
        """
        state = self.get_current_state(workflow_name, execution_history)
        best_action = self.select_action(state, explore=False)

        # Get all action Q-values for this state
        state_key = state.to_state_key()
        action_values = self.q_table.get(state_key, {})

        # Calculate confidence based on experience
        num_experiences = len([e for e in self.experience_buffer
                              if e.state.workflow_name == workflow_name])
        confidence = min(0.95, 0.3 + (num_experiences / 50))

        # Expected improvement estimation
        if best_action == ResourceAction.NO_CHANGE:
            expected_improvement = 0.0
        else:
            best_q = action_values.get(best_action.value, 0)
            expected_improvement = max(0, best_q * self.Q_VALUE_TO_PERCENTAGE_SCALE)

        # Generate reasoning
        reasoning = self._generate_reasoning(state, best_action, action_values)

        # Get alternative actions
        alternatives = []
        for action_name, q_value in sorted(action_values.items(), key=lambda x: x[1], reverse=True):
            if action_name != best_action.value:
                alternatives.append({
                    'action': action_name,
                    'q_value': q_value,
                    'expected_improvement': max(0, q_value * self.Q_VALUE_TO_PERCENTAGE_SCALE)
                })
        alternatives = alternatives[:3]  # Top 3 alternatives

        return OptimizationRecommendation(
            workflow_name=workflow_name,
            current_state={
                'concurrency_limit': state.concurrency_limit,
                'timeout_minutes': state.timeout_minutes,
                'caching_enabled': state.caching_enabled,
                'parallel_jobs': state.parallel_jobs,
                'avg_duration_seconds': state.avg_duration_seconds,
                'success_rate': f"{state.success_rate * 100:.1f}%",
                'resource_utilization': f"{state.resource_utilization * 100:.1f}%"
            },
            recommended_action=best_action.value,
            expected_improvement=expected_improvement,
            confidence=confidence,
            reasoning=reasoning,
            alternative_actions=alternatives
        )

    def _generate_reasoning(self, state: ResourceState, action: ResourceAction,
                           action_values: Dict[str, float]) -> List[str]:
        """Generate human-readable reasoning for the recommendation."""
        reasoning = []

        # State analysis
        if state.success_rate < 0.8:
            reasoning.append(f"⚠️ Low success rate ({state.success_rate * 100:.0f}%) indicates reliability issues")

        if state.avg_duration_seconds > 600:
            reasoning.append(f"⏱️ Long average duration ({state.avg_duration_seconds / 60:.1f}min) - optimization potential")

        if state.resource_utilization < 0.5:
            reasoning.append(f"📊 Low resource utilization ({state.resource_utilization * 100:.0f}%) - resources may be over-provisioned")

        # Action reasoning
        action_reasons = {
            ResourceAction.INCREASE_CONCURRENCY: "Increasing concurrency can speed up parallel workloads",
            ResourceAction.DECREASE_CONCURRENCY: "Decreasing concurrency can improve stability",
            ResourceAction.EXTEND_TIMEOUT: "Extending timeout prevents premature failures",
            ResourceAction.REDUCE_TIMEOUT: "Reducing timeout frees resources faster",
            ResourceAction.ENABLE_CACHING: "Enabling caching can significantly reduce build times",
            ResourceAction.DISABLE_CACHING: "Disabling caching may help with cache invalidation issues",
            ResourceAction.PARALLELIZE_JOBS: "Parallelizing jobs can reduce total workflow time",
            ResourceAction.SERIALIZE_JOBS: "Serializing jobs can reduce resource contention",
            ResourceAction.NO_CHANGE: "Current configuration appears optimal"
        }

        reasoning.append(f"💡 {action_reasons.get(action, 'Action recommended based on learned patterns')}")

        # Q-value insight
        if action_values:
            best_q = action_values.get(action.value, 0)
            if best_q > 0.1:
                reasoning.append(f"📈 High confidence action (Q-value: {best_q:.3f})")
            elif best_q < -0.1:
                reasoning.append(f"⚠️ Action has mixed results historically (Q-value: {best_q:.3f})")

        # Experience count
        num_exp = len(self.experience_buffer)
        if num_exp < 50:
            reasoning.append(f"ℹ️ Still learning (only {num_exp} experiences) - recommendations will improve")

        return reasoning

    def apply_action_to_state(self, state: ResourceState, action: ResourceAction) -> ResourceState:
        """
        Apply an action to a state and return the hypothetical next state.

        This is used for simulation and planning.
        """
        new_state = ResourceState(
            workflow_name=state.workflow_name,
            concurrency_limit=state.concurrency_limit,
            timeout_minutes=state.timeout_minutes,
            caching_enabled=state.caching_enabled,
            parallel_jobs=state.parallel_jobs,
            avg_duration_seconds=state.avg_duration_seconds,
            success_rate=state.success_rate,
            resource_utilization=state.resource_utilization,
            time_of_day_bucket=state.time_of_day_bucket,
            day_of_week=state.day_of_week
        )

        # Apply action effects (simplified model)
        if action == ResourceAction.INCREASE_CONCURRENCY:
            new_state.concurrency_limit = min(10, state.concurrency_limit + 1)
            new_state.avg_duration_seconds *= 0.9  # 10% faster
        elif action == ResourceAction.DECREASE_CONCURRENCY:
            new_state.concurrency_limit = max(1, state.concurrency_limit - 1)
            new_state.success_rate = min(1.0, state.success_rate + 0.05)
        elif action == ResourceAction.EXTEND_TIMEOUT:
            new_state.timeout_minutes = min(360, state.timeout_minutes + 30)
            new_state.success_rate = min(1.0, state.success_rate + 0.02)
        elif action == ResourceAction.REDUCE_TIMEOUT:
            new_state.timeout_minutes = max(10, state.timeout_minutes - 15)
            new_state.resource_utilization += 0.1
        elif action == ResourceAction.ENABLE_CACHING:
            new_state.caching_enabled = True
            new_state.avg_duration_seconds *= 0.7  # 30% faster
        elif action == ResourceAction.DISABLE_CACHING:
            new_state.caching_enabled = False
            new_state.success_rate = min(1.0, state.success_rate + 0.03)
        elif action == ResourceAction.PARALLELIZE_JOBS:
            new_state.parallel_jobs = min(10, state.parallel_jobs + 1)
            new_state.avg_duration_seconds *= 0.85
        elif action == ResourceAction.SERIALIZE_JOBS:
            new_state.parallel_jobs = max(1, state.parallel_jobs - 1)
            new_state.resource_utilization += 0.05

        return new_state

    def simulate_training(self, num_episodes: int = 100) -> Dict[str, Any]:
        """
        Simulate training episodes for testing and demonstration.

        Args:
            num_episodes: Number of episodes to simulate

        Returns:
            Training statistics
        """
        print(f"🎮 Simulating {num_episodes} training episodes...")

        stats = {
            'total_episodes': num_episodes,
            'total_reward': 0.0,
            'avg_reward': 0.0,
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

            # Take action
            action = self.select_action(state, explore=True)
            stats['action_counts'][action.value] += 1

            # Simulate next state
            next_state = self.apply_action_to_state(state, action)

            # Add some randomness to simulate real-world variance
            next_state.avg_duration_seconds *= random.uniform(
                self.SIMULATION_DURATION_VARIANCE_MIN,
                self.SIMULATION_DURATION_VARIANCE_MAX
            )
            next_state.success_rate = max(0, min(1, next_state.success_rate + random.uniform(
                -self.SIMULATION_SUCCESS_RATE_VARIANCE,
                self.SIMULATION_SUCCESS_RATE_VARIANCE
            )))

            # Learn from experience
            reward = self.learn_from_experience(state, action, next_state)
            stats['total_reward'] += reward
            stats['states_explored'].add(state.to_state_key())

            if (episode + 1) % 20 == 0:
                print(f"  Episode {episode + 1}/{num_episodes}, Reward: {reward:.3f}, Epsilon: {self.epsilon:.3f}")

        stats['avg_reward'] = stats['total_reward'] / num_episodes
        stats['states_explored'] = len(stats['states_explored'])
        stats['action_counts'] = dict(stats['action_counts'])

        print(f"\n✅ Training complete!")
        print(f"   Total reward: {stats['total_reward']:.2f}")
        print(f"   Average reward: {stats['avg_reward']:.3f}")
        print(f"   States explored: {stats['states_explored']}")
        print(f"   Q-table size: {len(self.q_table)} states")

        return stats

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive optimization report."""
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'model_stats': {
                'total_episodes': self.total_episodes,
                'epsilon': self.epsilon,
                'q_table_size': len(self.q_table),
                'experience_buffer_size': len(self.experience_buffer)
            },
            'metrics': self.metrics,
            'workflow_recommendations': []
        }

        # Get recommendations for known workflows
        for workflow_name in self.workflow_states.keys():
            rec = self.get_recommendation(workflow_name)
            report['workflow_recommendations'].append({
                'workflow': rec.workflow_name,
                'current_state': rec.current_state,
                'recommended_action': rec.recommended_action,
                'expected_improvement': f"{rec.expected_improvement:.1f}%",
                'confidence': f"{rec.confidence * 100:.0f}%",
                'reasoning': rec.reasoning
            })

        return report


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='RL-based GitHub Actions Resource Optimizer by @create-guru'
    )
    parser.add_argument(
        '--workflow',
        help='Get optimization recommendation for a specific workflow'
    )
    parser.add_argument(
        '--simulate',
        type=int,
        metavar='EPISODES',
        help='Simulate training with N episodes'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate optimization report'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory'
    )

    args = parser.parse_args()

    optimizer = RLResourceOptimizer(repo_root=args.repo_root)

    print("\n" + "="*70)
    print("🤖 RL Resource Optimizer for GitHub Actions")
    print("   Created by @create-guru")
    print("="*70 + "\n")

    if args.simulate:
        stats = optimizer.simulate_training(num_episodes=args.simulate)
        print("\n📊 Training Statistics:")
        print(json.dumps(stats, indent=2, default=str))

    if args.workflow:
        print(f"\n🔍 Analyzing workflow: {args.workflow}")
        print("-"*50)
        rec = optimizer.get_recommendation(args.workflow)
        print(f"\n📋 Recommendation for: {rec.workflow_name}")
        print(f"   Current State:")
        for k, v in rec.current_state.items():
            print(f"     - {k}: {v}")
        print(f"\n   ✨ Recommended Action: {rec.recommended_action}")
        print(f"   📈 Expected Improvement: {rec.expected_improvement:.1f}%")
        print(f"   🎯 Confidence: {rec.confidence * 100:.0f}%")
        print(f"\n   💭 Reasoning:")
        for reason in rec.reasoning:
            print(f"     {reason}")

        if rec.alternative_actions:
            print(f"\n   🔄 Alternative Actions:")
            for alt in rec.alternative_actions:
                print(f"     - {alt['action']} (expected: {alt['expected_improvement']:.1f}%)")

    if args.report:
        report = optimizer.generate_report()
        print("\n📊 Optimization Report")
        print("="*50)
        print(json.dumps(report, indent=2, default=str))

    if not (args.simulate or args.workflow or args.report):
        parser.print_help()
        print("\n💡 Try: --simulate 100 to train the model")
        print("💡 Try: --workflow my-workflow to get recommendations")


if __name__ == '__main__':
    main()
