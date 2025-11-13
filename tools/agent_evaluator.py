#!/usr/bin/env python3
"""
Agent Evaluation Engine

A beautifully crafted evaluation system that determines the fate of agents
based on their performance metrics. This module embodies the principle that
code should read like poetry - clear, elegant, and expressive.

Philosophy:
    - Clarity over cleverness
    - Self-documenting code
    - Elegant abstractions
    - Graceful error handling
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any


# Constants that speak for themselves
REGISTRY_PATH = Path(".github/agent-system/registry.json")


@dataclass
class EvaluationThresholds:
    """Clear boundaries that determine an agent's fate"""
    elimination: float
    promotion: float
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'EvaluationThresholds':
        """Create thresholds from configuration dictionary"""
        return cls(
            elimination=config.get('elimination_threshold', 0.3),
            promotion=config.get('promotion_threshold', 0.85)
        )


@dataclass
class AgentFate:
    """The destiny of an agent after evaluation"""
    agent_id: str
    name: str
    score: float
    outcome: str  # 'promoted', 'eliminated', or 'maintained'
    
    def is_promoted(self) -> bool:
        return self.outcome == 'promoted'
    
    def is_eliminated(self) -> bool:
        return self.outcome == 'eliminated'
    
    def is_maintained(self) -> bool:
        return self.outcome == 'maintained'


@dataclass
class EvaluationResults:
    """A complete snapshot of evaluation outcomes"""
    promoted: List[AgentFate] = field(default_factory=list)
    eliminated: List[AgentFate] = field(default_factory=list)
    maintained: List[AgentFate] = field(default_factory=list)
    
    @property
    def total_evaluated(self) -> int:
        """Count of all agents evaluated"""
        return len(self.promoted) + len(self.eliminated) + len(self.maintained)
    
    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert to dictionary for serialization"""
        return {
            'promoted': [
                {'id': a.agent_id, 'name': a.name, 'score': a.score}
                for a in self.promoted
            ],
            'eliminated': [
                {'id': a.agent_id, 'name': a.name, 'score': a.score}
                for a in self.eliminated
            ],
            'maintained': [
                {'id': a.agent_id, 'name': a.name, 'score': a.score}
                for a in self.maintained
            ]
        }


class RegistryManager:
    """
    Elegant interface to the agent registry.
    
    Handles all registry operations with grace and clarity,
    abstracting away the complexity of file operations.
    """
    
    def __init__(self, registry_path: Path = REGISTRY_PATH):
        self.path = registry_path
        self._registry: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """Load the registry with graceful error handling"""
        if not self.path.exists():
            raise FileNotFoundError(f"Registry not found at {self.path}")
        
        with open(self.path, 'r') as file:
            self._registry = json.load(file)
        
        return self._registry
    
    def save(self) -> None:
        """Persist the registry with beautiful formatting"""
        if self._registry is None:
            raise ValueError("Cannot save unloaded registry")
        
        with open(self.path, 'w') as file:
            json.dump(self._registry, file, indent=2)
    
    @property
    def registry(self) -> Dict[str, Any]:
        """Access the loaded registry"""
        if self._registry is None:
            raise ValueError("Registry not loaded. Call load() first.")
        return self._registry
    
    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Retrieve all active agents"""
        return [
            agent for agent in self.registry.get('agents', [])
            if agent.get('status') == 'active'
        ]
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration settings"""
        return self.registry.get('config', {})
    
    def update_agent_status(
        self,
        agent: Dict[str, Any],
        new_status: str,
        timestamp: Optional[str] = None
    ) -> None:
        """Update an agent's status with timestamp"""
        agent['status'] = new_status
        
        if timestamp is None:
            timestamp = self._current_timestamp()
        
        if new_status == 'hall_of_fame':
            agent['promoted_at'] = timestamp
        elif new_status == 'eliminated':
            agent['eliminated_at'] = timestamp
    
    def promote_to_hall_of_fame(self, agent: Dict[str, Any]) -> None:
        """Elevate an agent to the Hall of Fame"""
        self.update_agent_status(agent, 'hall_of_fame')
        self.registry.setdefault('hall_of_fame', []).append(agent)
    
    def eliminate_agent(self, agent: Dict[str, Any], reason: str) -> None:
        """Remove an agent from active duty"""
        self.update_agent_status(agent, 'eliminated')
        agent['elimination_reason'] = reason
    
    def update_system_lead(self) -> Optional[str]:
        """
        Select the highest performing Hall of Fame member as system lead.
        Returns the lead agent's ID, or None if no Hall of Fame members exist.
        """
        hall_of_fame = self.registry.get('hall_of_fame', [])
        
        if not hall_of_fame:
            return None
        
        champion = max(
            hall_of_fame,
            key=lambda agent: agent['metrics']['overall_score']
        )
        
        lead_id = champion['id']
        self.registry['system_lead'] = lead_id
        
        return lead_id
    
    def finalize_evaluation(self) -> None:
        """Clean up after evaluation - remove promoted/eliminated from active list"""
        self.registry['agents'] = [
            agent for agent in self.registry.get('agents', [])
            if agent.get('status') == 'active'
        ]
        self.registry['last_evaluation'] = self._current_timestamp()
    
    @staticmethod
    def _current_timestamp() -> str:
        """Generate ISO timestamp with timezone"""
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


class AgentEvaluator:
    """
    The heart of the evaluation system.
    
    Makes fate-determining decisions with elegance and clarity,
    evaluating each agent against performance thresholds.
    """
    
    def __init__(self, registry_manager: RegistryManager):
        self.registry = registry_manager
        self.thresholds = EvaluationThresholds.from_config(
            registry_manager.get_config()
        )
        self.metrics_collector = self._initialize_metrics_collector()
    
    def _initialize_metrics_collector(self):
        """Attempt to initialize the real metrics collector"""
        try:
            sys.path.insert(0, 'tools')
            import importlib.util
            
            spec = importlib.util.spec_from_file_location(
                "agent_metrics_collector",
                "tools/agent-metrics-collector.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            collector = module.MetricsCollector()
            print("✅ Using real GitHub metrics collector")
            return collector
            
        except Exception as error:
            print(f"⚠️  Metrics collector unavailable: {error}", file=sys.stderr)
            return None
    
    def evaluate_all(self, lookback_days: int = 7) -> EvaluationResults:
        """
        Evaluate all active agents and determine their fates.
        
        This is the main entry point - elegant and clear in purpose.
        """
        active_agents = self.registry.get_active_agents()
        
        if not active_agents:
            print("No active agents to evaluate")
            return EvaluationResults()
        
        print(f"📊 Evaluating {len(active_agents)} active agents...")
        
        results = EvaluationResults()
        
        for agent in active_agents:
            fate = self._evaluate_single_agent(agent, lookback_days)
            self._apply_fate(agent, fate)
            self._record_fate(results, fate)
        
        self.registry.finalize_evaluation()
        self._announce_system_lead()
        
        return results
    
    def _evaluate_single_agent(
        self,
        agent: Dict[str, Any],
        lookback_days: int
    ) -> AgentFate:
        """Determine the fate of a single agent"""
        agent_id = agent['id']
        agent_name = agent['name']
        
        score = self._calculate_score(agent, lookback_days)
        outcome = self._determine_outcome(score)
        
        return AgentFate(
            agent_id=agent_id,
            name=agent_name,
            score=score,
            outcome=outcome
        )
    
    def _calculate_score(
        self,
        agent: Dict[str, Any],
        lookback_days: int
    ) -> float:
        """
        Calculate performance score for an agent.
        
        Uses real metrics when available, falls back to graceful defaults.
        """
        if self.metrics_collector:
            return self._score_from_metrics(agent, lookback_days)
        else:
            return self._fallback_score(agent)
    
    def _score_from_metrics(
        self,
        agent: Dict[str, Any],
        lookback_days: int
    ) -> float:
        """Calculate score using real GitHub metrics"""
        try:
            metrics = self.metrics_collector.collect_metrics(
                agent['id'],
                since_days=lookback_days
            )
            
            # Update agent's stored metrics
            agent['metrics'].update({
                'issues_resolved': metrics.activity.issues_resolved,
                'prs_merged': metrics.activity.prs_merged,
                'reviews_given': metrics.activity.reviews_given,
                'code_quality_score': metrics.scores.code_quality,
                'overall_score': metrics.scores.overall
            })
            
            print(f"\n{agent['name']}: {metrics.scores.overall:.2%} (real metrics)")
            return metrics.scores.overall
            
        except Exception as error:
            print(f"⚠️  Metrics collection failed for {agent['id']}: {error}")
            return self._fallback_score(agent)
    
    def _fallback_score(self, agent: Dict[str, Any]) -> float:
        """Conservative scoring for new agents or when metrics unavailable"""
        from datetime import datetime
        
        spawned_time = datetime.fromisoformat(
            agent['spawned_at'].replace('Z', '+00:00')
        )
        
        age_hours = (
            datetime.now(timezone.utc) - spawned_time
        ).total_seconds() / 3600
        
        # New agents get up to 50% score based on age (max at 48 hours)
        score = min(0.5, age_hours / 48.0)
        
        agent['metrics']['overall_score'] = score
        print(f"\n{agent['name']}: {score:.2%} (fallback)")
        
        return score
    
    def _determine_outcome(self, score: float) -> str:
        """Determine fate based on score and thresholds"""
        if score >= self.thresholds.promotion:
            return 'promoted'
        elif score < self.thresholds.elimination:
            return 'eliminated'
        else:
            return 'maintained'
    
    def _apply_fate(self, agent: Dict[str, Any], fate: AgentFate) -> None:
        """Apply the determined fate to the agent"""
        if fate.is_promoted():
            self.registry.promote_to_hall_of_fame(agent)
            print(f"  🏆 PROMOTED to Hall of Fame!")
        elif fate.is_eliminated():
            reason = (
                f"Score {fate.score:.2%} below threshold "
                f"{self.thresholds.elimination:.2%}"
            )
            self.registry.eliminate_agent(agent, reason)
            print(f"  ❌ ELIMINATED (score too low)")
        else:
            print(f"  ✅ Maintained (active)")
    
    def _record_fate(self, results: EvaluationResults, fate: AgentFate) -> None:
        """Record the fate in evaluation results"""
        if fate.is_promoted():
            results.promoted.append(fate)
        elif fate.is_eliminated():
            results.eliminated.append(fate)
        else:
            results.maintained.append(fate)
    
    def _announce_system_lead(self) -> None:
        """Announce the system lead after evaluation"""
        lead_id = self.registry.update_system_lead()
        
        if lead_id:
            hall_of_fame = self.registry.registry.get('hall_of_fame', [])
            lead = next(
                (agent for agent in hall_of_fame if agent['id'] == lead_id),
                None
            )
            if lead:
                print(f"\n👑 System Lead: {lead['name']}")


def evaluate_agents() -> EvaluationResults:
    """
    Main entry point for agent evaluation.
    
    Beautiful in its simplicity - this function orchestrates the entire
    evaluation process with clear, elegant steps.
    """
    # Create our elegant managers and evaluators
    registry = RegistryManager()
    registry.load()
    
    evaluator = AgentEvaluator(registry)
    
    # Run the evaluation
    results = evaluator.evaluate_all()
    
    # Persist the changes
    registry.save()
    
    # Report the summary
    print(f"\n📊 Evaluation Summary:")
    print(f"  🏆 Promoted: {len(results.promoted)}")
    print(f"  ❌ Eliminated: {len(results.eliminated)}")
    print(f"  ✅ Maintained: {len(results.maintained)}")
    
    return results


if __name__ == '__main__':
    results = evaluate_agents()
    
    # Save results for downstream processing
    output_path = Path('/tmp/evaluation_results.json')
    with open(output_path, 'w') as file:
        json.dump(results.to_dict(), file, indent=2)
