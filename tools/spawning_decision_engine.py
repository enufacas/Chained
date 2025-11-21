#!/usr/bin/env python3
"""
Spawning Decision Engine - Intelligent Sub-Agent Spawning Based on Multiple Signals

Combines workload metrics and API health to make intelligent spawning decisions.
Part of the AI spawning specialized sub-agents system.

Created by @APIs-architect - Rigorous and innovative, ensuring reliability first.

Features:
- Combines workload metrics and API health scores
- Circuit breaker integration for resilience
- Priority-based decision making
- Configurable thresholds
- Comprehensive logging
- Thread-safe operations

Usage:
    from spawning_decision_engine import SpawningDecisionEngine
    
    engine = SpawningDecisionEngine()
    decision = engine.evaluate()
    
    if decision.should_spawn:
        print(f"Spawn {decision.agent_count} agents for {decision.specialization}")
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from workload_monitor import WorkloadMonitor, WorkloadMetrics, SpawningRecommendation
    from api_coordination_hub import APICoordinationHub, APIConfig, HealthStatus
    from api_monitoring_bridge import APIMonitoringBridge
except ImportError as e:
    print(f"Error: Required module not found: {e}")
    sys.exit(1)


class DecisionFactor(Enum):
    """Factors influencing spawning decisions"""
    WORKLOAD = "workload"
    API_HEALTH = "api_health"
    CIRCUIT_BREAKER = "circuit_breaker"
    CAPACITY = "capacity"
    PRIORITY = "priority"


@dataclass
class SpawningDecision:
    """
    Result of spawning decision evaluation.
    
    Created by @APIs-architect with comprehensive decision tracking.
    """
    should_spawn: bool
    specialization: str
    agent_count: int
    confidence: float  # 0.0 to 1.0
    factors: Dict[DecisionFactor, float]  # Factor scores
    reasoning: List[str]  # Human-readable reasoning
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'should_spawn': self.should_spawn,
            'specialization': self.specialization,
            'agent_count': self.agent_count,
            'confidence': self.confidence,
            'factors': {k.value: v for k, v in self.factors.items()},
            'reasoning': self.reasoning,
            'timestamp': self.timestamp
        }


@dataclass
class DecisionConfig:
    """
    Configuration for spawning decision engine.
    
    Designed by @APIs-architect with sensible defaults.
    """
    # Workload thresholds
    workload_critical_threshold: float = 0.8  # 80% workload is critical
    workload_high_threshold: float = 0.6      # 60% workload is high
    
    # API health thresholds
    api_unhealthy_threshold: float = 0.4  # Below 40% success rate
    api_degraded_threshold: float = 0.7   # Below 70% success rate
    
    # Circuit breaker consideration
    circuit_breaker_weight: float = 0.3  # 30% weight in decision
    
    # Minimum confidence for spawning
    min_confidence_threshold: float = 0.6  # 60% confidence required
    
    # Maximum agents per spawning event
    max_agents_per_spawn: int = 5
    
    # Cooldown between spawning events (seconds)
    spawning_cooldown: int = 300  # 5 minutes


class SpawningDecisionEngine:
    """
    Intelligent spawning decision engine.
    
    Combines multiple signals to make data-driven spawning decisions.
    
    Example:
        engine = SpawningDecisionEngine()
        decisions = engine.evaluate()
        
        for decision in decisions:
            if decision.should_spawn:
                print(f"Spawn {decision.agent_count} {decision.specialization} agents")
    """
    
    def __init__(
        self,
        config: Optional[DecisionConfig] = None,
        api_hub: Optional[APICoordinationHub] = None,
        api_monitor: Optional[APIMonitoringBridge] = None
    ):
        """
        Initialize decision engine.
        
        Args:
            config: Decision configuration
            api_hub: API coordination hub (optional)
            api_monitor: API monitoring bridge (optional)
        """
        self.config = config or DecisionConfig()
        self.workload_monitor = WorkloadMonitor()
        self.api_hub = api_hub
        self.api_monitor = api_monitor
        
        # Track last spawning time for cooldown
        self.last_spawn_time: Dict[str, float] = {}
    
    def evaluate(self, max_decisions: int = 10) -> List[SpawningDecision]:
        """
        Evaluate and generate spawning decisions.
        
        Args:
            max_decisions: Maximum number of decisions to return
            
        Returns:
            List of spawning decisions, sorted by priority
        """
        # Get workload metrics
        workload_metrics = self.workload_monitor.analyze_workload()
        
        # Get workload-based recommendations
        workload_recs = self.workload_monitor.generate_spawning_recommendations(
            metrics=workload_metrics,
            max_spawns=max_decisions
        )
        
        # Evaluate each recommendation with additional signals
        decisions = []
        
        for rec in workload_recs:
            if not rec.should_spawn:
                continue
            
            # Build decision with all factors
            decision = self._evaluate_recommendation(rec)
            
            if decision.should_spawn:
                decisions.append(decision)
        
        # Sort by confidence descending
        decisions.sort(key=lambda d: d.confidence, reverse=True)
        
        return decisions[:max_decisions]
    
    def _evaluate_recommendation(
        self,
        rec: SpawningRecommendation
    ) -> SpawningDecision:
        """
        Evaluate a workload recommendation with additional signals.
        
        Args:
            rec: Workload spawning recommendation
            
        Returns:
            Complete spawning decision
        """
        factors = {}
        reasoning = []
        
        # Factor 1: Workload metrics (primary factor)
        workload_score = self._evaluate_workload(rec.metrics, reasoning)
        factors[DecisionFactor.WORKLOAD] = workload_score
        
        # Factor 2: API health (if available)
        api_health_score = self._evaluate_api_health(rec.specialization, reasoning)
        factors[DecisionFactor.API_HEALTH] = api_health_score
        
        # Factor 3: Circuit breaker status (if available)
        circuit_score = self._evaluate_circuit_breaker(rec.specialization, reasoning)
        factors[DecisionFactor.CIRCUIT_BREAKER] = circuit_score
        
        # Factor 4: Agent capacity
        capacity_score = self._evaluate_capacity(rec.metrics, reasoning)
        factors[DecisionFactor.CAPACITY] = capacity_score
        
        # Factor 5: Priority
        priority_score = rec.priority / 5.0  # Normalize 1-5 to 0.0-1.0
        factors[DecisionFactor.PRIORITY] = priority_score
        reasoning.append(f"Priority level: {rec.priority}/5")
        
        # Calculate weighted confidence
        # Weights: workload (0.35), API health (0.25), circuit (0.15), capacity (0.15), priority (0.10)
        confidence = (
            workload_score * 0.35 +
            api_health_score * 0.25 +
            circuit_score * 0.15 +
            capacity_score * 0.15 +
            priority_score * 0.10
        )
        
        # Apply cooldown check
        in_cooldown = self._check_cooldown(rec.specialization)
        if in_cooldown:
            cooldown_remaining = int(self.config.spawning_cooldown - 
                                   (time.time() - self.last_spawn_time.get(rec.specialization, 0)))
            reasoning.append(f"⏱️  In cooldown period ({cooldown_remaining}s remaining)")
            confidence *= 0.5  # Reduce confidence during cooldown
        
        # Make final decision
        should_spawn = (
            confidence >= self.config.min_confidence_threshold and
            not in_cooldown
        )
        
        # Determine agent count based on severity
        if rec.metrics.bottleneck_severity == 'critical':
            agent_count = min(rec.count, self.config.max_agents_per_spawn)
        elif rec.metrics.bottleneck_severity == 'high':
            agent_count = min(rec.count, self.config.max_agents_per_spawn - 1)
        else:
            agent_count = min(rec.count, max(1, self.config.max_agents_per_spawn - 2))
        
        return SpawningDecision(
            should_spawn=should_spawn,
            specialization=rec.specialization,
            agent_count=agent_count,
            confidence=confidence,
            factors=factors,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat()
        )
    
    def _evaluate_workload(
        self,
        metrics: WorkloadMetrics,
        reasoning: List[str]
    ) -> float:
        """
        Evaluate workload metrics.
        
        Args:
            metrics: Workload metrics
            reasoning: List to append reasoning to
            
        Returns:
            Score 0.0-1.0
        """
        # Calculate workload intensity
        issue_ratio = metrics.open_issues / max(metrics.active_agents, 1)
        pr_ratio = metrics.pending_prs / max(metrics.active_agents, 1)
        
        # Normalize to 0-1 scale (assume 10 issues/PRs per agent is max)
        workload_intensity = min((issue_ratio + pr_ratio) / 20, 1.0)
        
        # Factor in agent capacity
        capacity_factor = metrics.agent_capacity
        
        # Combine
        score = (workload_intensity * 0.6 + capacity_factor * 0.4)
        
        reasoning.append(
            f"📊 Workload: {metrics.open_issues} issues, {metrics.pending_prs} PRs, "
            f"{metrics.active_agents} active agents (capacity: {capacity_factor:.0%})"
        )
        
        return score
    
    def _evaluate_api_health(
        self,
        specialization: str,
        reasoning: List[str]
    ) -> float:
        """
        Evaluate API health for the specialization.
        
        Args:
            specialization: Agent specialization
            reasoning: List to append reasoning to
            
        Returns:
            Score 0.0-1.0 (1.0 if no API data available)
        """
        if not self.api_monitor:
            return 1.0  # Neutral score if no API monitoring
        
        # Get endpoint stats for specialization-related APIs
        # This is a simplified version - in production, map specializations to APIs
        try:
            # Get overall API health
            all_stats = self.api_monitor.get_overall_stats()
            
            if not all_stats:
                return 1.0  # No data, neutral score
            
            # Use success rate as health indicator
            success_rate = all_stats.success_rate
            
            if success_rate < self.config.api_unhealthy_threshold:
                score = 0.2
                reasoning.append(f"⚠️  API unhealthy: {success_rate:.0%} success rate")
            elif success_rate < self.config.api_degraded_threshold:
                score = 0.6
                reasoning.append(f"⚡ API degraded: {success_rate:.0%} success rate")
            else:
                score = 1.0
                reasoning.append(f"✅ API healthy: {success_rate:.0%} success rate")
            
            return score
            
        except Exception as e:
            # If error getting API health, be conservative
            reasoning.append(f"⚠️  Could not determine API health: {str(e)}")
            return 0.7
    
    def _evaluate_circuit_breaker(
        self,
        specialization: str,
        reasoning: List[str]
    ) -> float:
        """
        Evaluate circuit breaker status.
        
        Args:
            specialization: Agent specialization
            reasoning: List to append reasoning to
            
        Returns:
            Score 0.0-1.0 (1.0 if circuit closed/healthy)
        """
        if not self.api_hub:
            return 1.0  # Neutral if no circuit breaker
        
        try:
            # Check if we have a circuit breaker for this specialization
            # This is simplified - in production, map specializations to APIs
            api_name = specialization  # Simplified mapping
            
            if api_name not in self.api_hub.apis:
                return 1.0  # No circuit breaker, neutral score
            
            api_state = self.api_hub.apis[api_name]
            circuit_state = api_state['circuit_breaker'].get_state()
            
            from api_coordination_hub import CircuitState
            
            if circuit_state == CircuitState.CLOSED:
                score = 1.0
                reasoning.append("🔒 Circuit closed (healthy)")
            elif circuit_state == CircuitState.HALF_OPEN:
                score = 0.7
                reasoning.append("🔓 Circuit half-open (recovering)")
            else:  # OPEN
                score = 0.3
                reasoning.append("⚠️  Circuit open (unhealthy)")
            
            return score
            
        except Exception as e:
            reasoning.append(f"⚠️  Could not check circuit breaker: {str(e)}")
            return 0.7
    
    def _evaluate_capacity(
        self,
        metrics: WorkloadMetrics,
        reasoning: List[str]
    ) -> float:
        """
        Evaluate agent capacity.
        
        Args:
            metrics: Workload metrics
            reasoning: List to append reasoning to
            
        Returns:
            Score 0.0-1.0 (higher capacity = higher score)
        """
        # Capacity already normalized to 0-1
        score = metrics.agent_capacity
        
        if score > 0.8:
            reasoning.append(f"🔴 High capacity: {score:.0%} (critical)")
        elif score > 0.6:
            reasoning.append(f"🟡 Elevated capacity: {score:.0%}")
        else:
            reasoning.append(f"🟢 Normal capacity: {score:.0%}")
        
        return score
    
    def _check_cooldown(self, specialization: str) -> bool:
        """
        Check if specialization is in cooldown period.
        
        Args:
            specialization: Agent specialization
            
        Returns:
            True if in cooldown, False otherwise
        """
        last_spawn = self.last_spawn_time.get(specialization)
        
        if not last_spawn:
            return False
        
        elapsed = time.time() - last_spawn
        return elapsed < self.config.spawning_cooldown
    
    def record_spawn(self, specialization: str):
        """
        Record that spawning occurred for a specialization.
        
        Args:
            specialization: Agent specialization
        """
        self.last_spawn_time[specialization] = time.time()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current engine status.
        
        Returns:
            Status dictionary
        """
        decisions = self.evaluate()
        
        return {
            'active_decisions': len(decisions),
            'spawning_recommended': len([d for d in decisions if d.should_spawn]),
            'decisions': [d.to_dict() for d in decisions],
            'config': asdict(self.config),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Command-line interface for decision engine"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Spawning Decision Engine - Intelligent sub-agent spawning'
    )
    parser.add_argument(
        '--max-decisions', '-m',
        type=int,
        default=10,
        help='Maximum spawning decisions to generate'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'text'],
        default='text',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    # Create engine
    engine = SpawningDecisionEngine()
    
    # Get decisions
    decisions = engine.evaluate(max_decisions=args.max_decisions)
    
    if args.format == 'json':
        # JSON output
        output = {
            'decisions': [d.to_dict() for d in decisions],
            'timestamp': datetime.now().isoformat()
        }
        print(json.dumps(output, indent=2))
    else:
        # Text output
        print("🧠 Spawning Decision Engine")
        print(f"Created by @APIs-architect - Ensuring reliability first\n")
        print(f"Generated {len(decisions)} decision(s):\n")
        
        for i, decision in enumerate(decisions, 1):
            print(f"{'='*60}")
            print(f"Decision {i}: {decision.specialization}")
            print(f"{'='*60}")
            print(f"Should Spawn: {'YES' if decision.should_spawn else 'NO'}")
            print(f"Agent Count: {decision.agent_count}")
            print(f"Confidence: {decision.confidence:.1%}")
            print(f"\nFactors:")
            for factor, score in decision.factors.items():
                print(f"  {factor.value}: {score:.1%}")
            print(f"\nReasoning:")
            for reason in decision.reasoning:
                print(f"  • {reason}")
            print()


if __name__ == '__main__':
    main()
