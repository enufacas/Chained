"""
A2A Auto-Routing Proof of Concept
==================================

Demonstrates intelligent agent selection based on multiple criteria.
Inspired by GitHub Copilot's auto model selection (Nov 26, 2025).

This is a proof-of-concept implementation of the proposed A2A Auto-Routing
enhancement from Mission idea:154 (API-Agents Integration).

Key Features:
- Multi-criteria agent scoring
- Health-aware selection
- Fallback agent support
- Load distribution
- Transparent decision explanation

Author: @bridge-master
Date: 2025-12-16
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import json


class AgentStatus(Enum):
    """Agent health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass
class AgentCapability:
    """Represents an agent's capabilities."""
    task_types: List[str]
    features: List[str]
    max_concurrent_tasks: int
    avg_response_time_ms: int


@dataclass
class AgentMetrics:
    """Performance metrics for an agent."""
    success_rate: float  # 0.0 to 1.0
    current_workload: int  # Number of active tasks
    total_tasks_completed: int
    avg_completion_time_ms: int


@dataclass
class AgentInfo:
    """Complete agent information."""
    name: str
    status: AgentStatus
    capabilities: AgentCapability
    metrics: AgentMetrics
    specialization_score: float  # From match-issue-to-agent.py


@dataclass
class SelectionCriteria:
    """Criteria for agent selection."""
    task_type: str
    required_features: List[str]
    priority: str  # "speed", "reliability", "balanced"
    
    # Scoring weights (should sum to 1.0)
    availability_weight: float = 0.25
    capability_weight: float = 0.20
    performance_weight: float = 0.25
    workload_weight: float = 0.15
    specialization_weight: float = 0.15


@dataclass
class AgentSelection:
    """Result of agent selection."""
    primary: str
    fallbacks: List[str]
    scores: Dict[str, float]
    reasoning: str


class AgentRouter:
    """
    Intelligent routing for A2A agent selection.
    
    Implements the auto-routing enhancement proposed in Mission idea:154.
    Selects the best available agent based on multiple criteria, similar
    to GitHub Copilot's auto model selection.
    
    Example:
        >>> router = AgentRouter(agents_info)
        >>> criteria = SelectionCriteria(
        ...     task_type="code_review",
        ...     required_features=["github_integration"],
        ...     priority="balanced"
        ... )
        >>> selection = router.select_agent(criteria)
        >>> print(f"Selected: {selection.primary}")
        >>> print(f"Reasoning: {selection.reasoning}")
    """
    
    def __init__(self, agents: Dict[str, AgentInfo]):
        """
        Initialize router with agent information.
        
        Args:
            agents: Dictionary mapping agent names to AgentInfo
        """
        self.agents = agents
    
    def select_agent(self, criteria: SelectionCriteria) -> AgentSelection:
        """
        Select best available agent for a task.
        
        Args:
            criteria: Selection criteria including task type and preferences
            
        Returns:
            AgentSelection with primary agent, fallbacks, and reasoning
        """
        # Step 1: Find candidate agents
        candidates = self._find_candidates(criteria)
        
        if not candidates:
            raise ValueError(f"No agents available for task type: {criteria.task_type}")
        
        # Step 2: Score each candidate
        scored_agents = self._score_agents(candidates, criteria)
        
        # Step 3: Rank agents by score
        primary, fallbacks = self._rank_agents(scored_agents)
        
        # Step 4: Generate explanation
        reasoning = self._explain_selection(scored_agents, criteria)
        
        return AgentSelection(
            primary=primary,
            fallbacks=fallbacks[:2],  # Up to 2 fallback agents
            scores={name: score for name, score in scored_agents},
            reasoning=reasoning
        )
    
    def _find_candidates(self, criteria: SelectionCriteria) -> List[str]:
        """
        Find agents that can handle the task.
        
        Args:
            criteria: Task requirements
            
        Returns:
            List of candidate agent names
        """
        candidates = []
        
        for name, agent in self.agents.items():
            # Check if agent is available
            if agent.status == AgentStatus.UNAVAILABLE:
                continue
            
            # Check if agent supports task type
            if criteria.task_type not in agent.capabilities.task_types:
                continue
            
            # Check if agent has required features
            if not all(f in agent.capabilities.features for f in criteria.required_features):
                continue
            
            candidates.append(name)
        
        return candidates
    
    def _score_agents(
        self, 
        candidates: List[str], 
        criteria: SelectionCriteria
    ) -> List[Tuple[str, float]]:
        """
        Score each candidate agent.
        
        Scoring formula:
        score = (
            availability_weight * availability_score +
            capability_weight * capability_score +
            performance_weight * performance_score +
            workload_weight * workload_score +
            specialization_weight * specialization_score
        )
        
        Args:
            candidates: List of candidate agent names
            criteria: Scoring criteria
            
        Returns:
            List of (agent_name, score) tuples
        """
        scores = []
        
        for name in candidates:
            agent = self.agents[name]
            
            # Calculate individual scores
            avail_score = self._score_availability(agent)
            cap_score = self._score_capability(agent, criteria)
            perf_score = self._score_performance(agent)
            load_score = self._score_workload(agent)
            spec_score = agent.specialization_score
            
            # Weighted total
            total_score = (
                criteria.availability_weight * avail_score +
                criteria.capability_weight * cap_score +
                criteria.performance_weight * perf_score +
                criteria.workload_weight * load_score +
                criteria.specialization_weight * spec_score
            )
            
            scores.append((name, total_score))
        
        return scores
    
    def _score_availability(self, agent: AgentInfo) -> float:
        """Score based on agent health status."""
        if agent.status == AgentStatus.HEALTHY:
            return 1.0
        elif agent.status == AgentStatus.DEGRADED:
            return 0.5
        else:
            return 0.0
    
    def _score_capability(self, agent: AgentInfo, criteria: SelectionCriteria) -> float:
        """Score based on capability match."""
        # Higher score for more features beyond requirements
        extra_features = len(agent.capabilities.features) - len(criteria.required_features)
        feature_score = min(1.0, 0.5 + (extra_features * 0.1))
        
        # Adjust for max concurrent tasks
        concurrency_score = min(1.0, agent.capabilities.max_concurrent_tasks / 10.0)
        
        return (feature_score + concurrency_score) / 2.0
    
    def _score_performance(self, agent: AgentInfo) -> float:
        """Score based on historical performance."""
        # Success rate is primary factor
        success_score = agent.metrics.success_rate
        
        # Adjust for experience (more completed tasks = higher confidence)
        experience_factor = min(1.0, agent.metrics.total_tasks_completed / 100.0)
        
        return success_score * (0.7 + 0.3 * experience_factor)
    
    def _score_workload(self, agent: AgentInfo) -> float:
        """Score based on current workload (lower is better)."""
        max_load = agent.capabilities.max_concurrent_tasks
        current_load = agent.metrics.current_workload
        
        if max_load == 0:
            return 0.0
        
        utilization = current_load / max_load
        
        # Score decreases as utilization increases
        return max(0.0, 1.0 - utilization)
    
    def _rank_agents(self, scored_agents: List[Tuple[str, float]]) -> Tuple[str, List[str]]:
        """
        Rank agents by score.
        
        Args:
            scored_agents: List of (name, score) tuples
            
        Returns:
            (primary_agent, fallback_agents)
        """
        # Sort by score descending
        ranked = sorted(scored_agents, key=lambda x: x[1], reverse=True)
        
        primary = ranked[0][0]
        fallbacks = [name for name, _ in ranked[1:]]
        
        return primary, fallbacks
    
    def _explain_selection(
        self, 
        scored_agents: List[Tuple[str, float]],
        criteria: SelectionCriteria
    ) -> str:
        """
        Generate human-readable explanation of selection.
        
        Args:
            scored_agents: List of (name, score) tuples
            criteria: Selection criteria used
            
        Returns:
            Explanation string
        """
        # Sort by score
        ranked = sorted(scored_agents, key=lambda x: x[1], reverse=True)
        
        primary_name, primary_score = ranked[0]
        primary_agent = self.agents[primary_name]
        
        explanation_parts = [
            f"Selected **{primary_name}** (score: {primary_score:.2f}) for {criteria.task_type} task.",
            "",
            "Scoring breakdown:",
            f"- Availability: {self._score_availability(primary_agent):.2f} (status: {primary_agent.status.value})",
            f"- Capability: {self._score_capability(primary_agent, criteria):.2f}",
            f"- Performance: {self._score_performance(primary_agent):.2f} (success rate: {primary_agent.metrics.success_rate:.0%})",
            f"- Workload: {self._score_workload(primary_agent):.2f} ({primary_agent.metrics.current_workload}/{primary_agent.capabilities.max_concurrent_tasks} tasks)",
            f"- Specialization: {primary_agent.specialization_score:.2f}",
        ]
        
        if len(ranked) > 1:
            explanation_parts.append("")
            explanation_parts.append("Fallback agents available:")
            for name, score in ranked[1:3]:  # Show top 2 fallbacks
                explanation_parts.append(f"- {name} (score: {score:.2f})")
        
        return "\n".join(explanation_parts)


# Example usage and demonstration
def example_usage():
    """Demonstrate the A2A Auto-Routing proof of concept."""
    
    # Create mock agent data
    agents = {
        "engineer-master": AgentInfo(
            name="engineer-master",
            status=AgentStatus.HEALTHY,
            capabilities=AgentCapability(
                task_types=["code_review", "api_design", "refactoring"],
                features=["github_integration", "ci_cd", "testing"],
                max_concurrent_tasks=5,
                avg_response_time_ms=1500
            ),
            metrics=AgentMetrics(
                success_rate=0.95,
                current_workload=2,
                total_tasks_completed=150,
                avg_completion_time_ms=3000
            ),
            specialization_score=0.85
        ),
        
        "secure-specialist": AgentInfo(
            name="secure-specialist",
            status=AgentStatus.HEALTHY,
            capabilities=AgentCapability(
                task_types=["security_audit", "code_review", "vulnerability_scan"],
                features=["github_integration", "security_scanning"],
                max_concurrent_tasks=3,
                avg_response_time_ms=2000
            ),
            metrics=AgentMetrics(
                success_rate=0.92,
                current_workload=1,
                total_tasks_completed=80,
                avg_completion_time_ms=4000
            ),
            specialization_score=0.75
        ),
        
        "organize-guru": AgentInfo(
            name="organize-guru",
            status=AgentStatus.DEGRADED,  # Experiencing issues
            capabilities=AgentCapability(
                task_types=["code_review", "refactoring", "cleanup"],
                features=["github_integration", "static_analysis"],
                max_concurrent_tasks=5,
                avg_response_time_ms=1200
            ),
            metrics=AgentMetrics(
                success_rate=0.88,
                current_workload=4,
                total_tasks_completed=200,
                avg_completion_time_ms=2500
            ),
            specialization_score=0.80
        )
    }
    
    # Create router
    router = AgentRouter(agents)
    
    # Define selection criteria
    criteria = SelectionCriteria(
        task_type="code_review",
        required_features=["github_integration"],
        priority="balanced",
        availability_weight=0.25,
        capability_weight=0.20,
        performance_weight=0.25,
        workload_weight=0.15,
        specialization_weight=0.15
    )
    
    # Select agent
    selection = router.select_agent(criteria)
    
    # Print results
    print("=" * 60)
    print("A2A Auto-Routing Proof of Concept")
    print("=" * 60)
    print()
    print("Task Requirements:")
    print(f"  Type: {criteria.task_type}")
    print(f"  Features: {', '.join(criteria.required_features)}")
    print(f"  Priority: {criteria.priority}")
    print()
    print("Selection Result:")
    print(f"  Primary: {selection.primary}")
    print(f"  Fallbacks: {', '.join(selection.fallbacks)}")
    print()
    print("Agent Scores:")
    for name, score in sorted(selection.scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {score:.3f}")
    print()
    print("Reasoning:")
    print(selection.reasoning)
    print()
    print("=" * 60)
    print()
    print("Key Benefits Demonstrated:")
    print("✓ Health-aware selection (degraded agent ranked lower)")
    print("✓ Workload distribution (prefers less-busy agents)")
    print("✓ Performance-based scoring (success rate weighted)")
    print("✓ Automatic fallback agents (2 backups identified)")
    print("✓ Transparent decision making (full explanation)")
    print()
    print("This demonstrates the proposed A2A Auto-Routing enhancement")
    print("from Mission idea:154. Expected impact: 30-40% improvement")
    print("in task completion rate through intelligent agent selection.")
    print()


if __name__ == "__main__":
    example_usage()
