#!/usr/bin/env python3
"""
Hierarchical Agent System

Implements a true hierarchical structure for the Chained autonomous AI ecosystem:
- Coordinator tier: High-level task management and delegation
- Specialist tier: Domain-specific implementation
- Worker tier: Focused execution of specific subtasks

This extends the existing meta-agent coordinator with role-based hierarchies,
delegation chains, and oversight mechanisms.

Part of the Chained autonomous AI ecosystem.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

# Import the base coordinator
sys.path.insert(0, str(Path(__file__).parent))
from meta_agent_coordinator import (
    MetaAgentCoordinator, 
    CoordinationPlan, 
    SubTask, 
    TaskComplexity,
    TaskStatus
)


class AgentRole(Enum):
    """Hierarchical roles in the agent system"""
    COORDINATOR = "coordinator"      # Top-level task management and delegation
    SPECIALIST = "specialist"        # Domain-specific implementation
    WORKER = "worker"               # Focused execution of subtasks


class DelegationStatus(Enum):
    """Status of delegated work"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    REJECTED = "rejected"


@dataclass
class AgentTier:
    """Represents an agent's tier in the hierarchy"""
    agent_id: str
    role: AgentRole
    specialization: str
    can_delegate_to: List[AgentRole] = field(default_factory=list)
    reports_to: Optional[AgentRole] = None
    oversight_enabled: bool = True
    
    def to_dict(self) -> Dict:
        return {
            'agent_id': self.agent_id,
            'role': self.role.value,
            'specialization': self.specialization,
            'can_delegate_to': [r.value for r in self.can_delegate_to],
            'reports_to': self.reports_to.value if self.reports_to else None,
            'oversight_enabled': self.oversight_enabled
        }


@dataclass
class DelegationChain:
    """Tracks a chain of delegation from coordinator to workers"""
    chain_id: str
    root_task_id: str
    coordinator_id: str
    hierarchy: List[Dict[str, Any]] = field(default_factory=list)  # Level-by-level breakdown
    current_level: int = 0
    status: DelegationStatus = DelegationStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'chain_id': self.chain_id,
            'root_task_id': self.root_task_id,
            'coordinator_id': self.coordinator_id,
            'hierarchy': self.hierarchy,
            'current_level': self.current_level,
            'status': self.status.value,
            'created_at': self.created_at
        }


class HierarchicalAgentSystem:
    """
    Manages hierarchical agent coordination with role-based tiers.
    
    Architecture:
    - Coordinator agents receive complex tasks and break them down
    - Specialist agents receive domain-specific subtasks
    - Worker agents execute focused work items
    - Each tier reports up and delegates down
    """
    
    # Default role assignments based on specialization
    ROLE_ASSIGNMENTS = {
        'meta-coordinator': AgentRole.COORDINATOR,
        'coach-master': AgentRole.COORDINATOR,
        'support-master': AgentRole.COORDINATOR,
        
        'engineer-master': AgentRole.SPECIALIST,
        'engineer-wizard': AgentRole.SPECIALIST,
        'investigate-champion': AgentRole.SPECIALIST,
        'secure-specialist': AgentRole.SPECIALIST,
        'create-guru': AgentRole.SPECIALIST,
        'organize-guru': AgentRole.SPECIALIST,
        'monitor-champion': AgentRole.SPECIALIST,
        
        'accelerate-master': AgentRole.WORKER,
        'assert-specialist': AgentRole.WORKER,
        'refactor-champion': AgentRole.WORKER,
        'document-ninja': AgentRole.WORKER,
    }
    
    # Delegation rules: who can delegate to whom
    DELEGATION_RULES = {
        AgentRole.COORDINATOR: [AgentRole.SPECIALIST, AgentRole.WORKER],
        AgentRole.SPECIALIST: [AgentRole.WORKER],
        AgentRole.WORKER: []  # Workers don't delegate
    }
    
    # Reporting structure: who reports to whom
    REPORTING_STRUCTURE = {
        AgentRole.WORKER: AgentRole.SPECIALIST,
        AgentRole.SPECIALIST: AgentRole.COORDINATOR,
        AgentRole.COORDINATOR: None  # Top level
    }
    
    def __init__(self, repo_root: str = None):
        """
        Initialize the hierarchical agent system.
        
        Args:
            repo_root: Root directory of the repository
        """
        self.base_coordinator = MetaAgentCoordinator(repo_root)
        self.repo_root = self.base_coordinator.repo_root
        
        self.hierarchy_config_path = self.repo_root / '.github/agent-system/hierarchy.json'
        self.delegation_log_path = self.repo_root / '.github/agent-system/delegation_log.json'
        
        # Load hierarchical configuration
        self.hierarchy_config = self._load_hierarchy_config()
        self.delegation_log = self._load_delegation_log()
        
        # Build agent tier mappings
        self.agent_tiers = self._build_agent_tiers()
    
    def _load_hierarchy_config(self) -> Dict:
        """Load or initialize hierarchy configuration"""
        if self.hierarchy_config_path.exists():
            try:
                with open(self.hierarchy_config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Invalid hierarchy config, creating new one", file=sys.stderr)
        
        return {
            'version': '1.0.0',
            'enabled': True,
            'role_assignments': {k: v.value for k, v in self.ROLE_ASSIGNMENTS.items()},
            'delegation_rules': {
                k.value: [r.value for r in v] 
                for k, v in self.DELEGATION_RULES.items()
            },
            'oversight_enabled': True,
            'auto_escalation_enabled': True
        }
    
    def _save_hierarchy_config(self):
        """Save hierarchy configuration"""
        self.hierarchy_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.hierarchy_config_path, 'w') as f:
            json.dump(self.hierarchy_config, f, indent=2)
    
    def _load_delegation_log(self) -> Dict:
        """Load or initialize delegation log"""
        if self.delegation_log_path.exists():
            try:
                with open(self.delegation_log_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Invalid delegation log, creating new one", file=sys.stderr)
        
        return {
            'version': '1.0.0',
            'delegation_chains': [],
            'statistics': {
                'total_delegations': 0,
                'successful_delegations': 0,
                'escalations': 0,
                'avg_chain_length': 0.0
            }
        }
    
    def _save_delegation_log(self):
        """Save delegation log"""
        self.delegation_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.delegation_log_path, 'w') as f:
            json.dump(self.delegation_log, f, indent=2)
    
    def _build_agent_tiers(self) -> Dict[str, AgentTier]:
        """Build agent tier mappings from registry and configuration"""
        tiers = {}
        
        for agent_id, agent in self.base_coordinator.agents.items():
            specialization = agent.get('specialization', 'unknown')
            
            # Determine role from configuration or defaults
            role_str = self.hierarchy_config.get('role_assignments', {}).get(
                specialization,
                self.ROLE_ASSIGNMENTS.get(specialization, AgentRole.WORKER).value
            )
            role = AgentRole(role_str)
            
            # Get delegation and reporting rules
            can_delegate_to = [
                AgentRole(r) for r in 
                self.hierarchy_config.get('delegation_rules', {}).get(role.value, [])
            ]
            reports_to = self.REPORTING_STRUCTURE.get(role)
            
            tier = AgentTier(
                agent_id=agent_id,
                role=role,
                specialization=specialization,
                can_delegate_to=can_delegate_to,
                reports_to=reports_to,
                oversight_enabled=self.hierarchy_config.get('oversight_enabled', True)
            )
            
            tiers[agent_id] = tier
        
        return tiers
    
    def get_coordinator_agents(self) -> List[str]:
        """Get all agents with coordinator role"""
        return [
            agent_id for agent_id, tier in self.agent_tiers.items()
            if tier.role == AgentRole.COORDINATOR
        ]
    
    def get_specialist_agents(self, specialization: str = None) -> List[str]:
        """Get all specialist agents, optionally filtered by specialization"""
        agents = [
            agent_id for agent_id, tier in self.agent_tiers.items()
            if tier.role == AgentRole.SPECIALIST
        ]
        
        if specialization:
            agents = [
                agent_id for agent_id in agents
                if self.agent_tiers[agent_id].specialization == specialization
            ]
        
        return agents
    
    def get_worker_agents(self, specialization: str = None) -> List[str]:
        """Get all worker agents, optionally filtered by specialization"""
        agents = [
            agent_id for agent_id, tier in self.agent_tiers.items()
            if tier.role == AgentRole.WORKER
        ]
        
        if specialization:
            agents = [
                agent_id for agent_id in agents
                if self.agent_tiers[agent_id].specialization == specialization
            ]
        
        return agents
    
    def create_hierarchical_plan(self, task_id: str, task_description: str, 
                                 task_context: Dict = None) -> Tuple[CoordinationPlan, DelegationChain]:
        """
        Create a hierarchical coordination plan with delegation chain.
        
        Args:
            task_id: Unique identifier for the task
            task_description: The task description
            task_context: Additional context
        
        Returns:
            Tuple of (CoordinationPlan, DelegationChain)
        """
        # Use base coordinator to create initial plan
        plan = self.base_coordinator.decompose_task(task_id, task_description, task_context)
        
        # Select a coordinator agent
        coordinators = self.get_coordinator_agents()
        if not coordinators:
            # Fallback to meta-coordinator if available
            coordinators = [
                agent_id for agent_id, agent in self.base_coordinator.agents.items()
                if agent.get('specialization') == 'meta-coordinator'
            ]
        
        coordinator_id = coordinators[0] if coordinators else None
        
        # Build delegation chain
        chain = DelegationChain(
            chain_id=f"chain-{task_id}-{int(datetime.now(timezone.utc).timestamp())}",
            root_task_id=task_id,
            coordinator_id=coordinator_id or "system"
        )
        
        # Level 0: Coordinator receives task
        chain.hierarchy.append({
            'level': 0,
            'role': 'coordinator',
            'agent_id': coordinator_id,
            'task_id': task_id,
            'task_description': task_description,
            'status': 'pending'
        })
        
        # Level 1: Coordinator delegates to specialists
        level_1_tasks = []
        for subtask in plan.sub_tasks:
            # Find appropriate specialist
            specialists = self._find_agents_for_subtask(subtask, AgentRole.SPECIALIST)
            specialist_id = specialists[0] if specialists else None
            
            level_1_tasks.append({
                'subtask_id': subtask.id,
                'role': 'specialist',
                'agent_id': specialist_id,
                'description': subtask.description,
                'status': 'pending'
            })
        
        chain.hierarchy.append({
            'level': 1,
            'tasks': level_1_tasks
        })
        
        # Level 2: Specialists can delegate to workers (if needed)
        # This would be determined during execution based on subtask complexity
        
        return plan, chain
    
    def _find_agents_for_subtask(self, subtask: SubTask, preferred_role: AgentRole) -> List[str]:
        """Find agents suitable for a subtask with the preferred role"""
        candidates = []
        
        for spec in subtask.required_specializations:
            # Find agents with this specialization and role
            for agent_id, tier in self.agent_tiers.items():
                if tier.specialization == spec and tier.role == preferred_role:
                    agent = self.base_coordinator.agents.get(agent_id)
                    if agent:
                        # Score by performance
                        score = agent.get('metrics', {}).get('overall_score', 0)
                        candidates.append((agent_id, score))
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [agent_id for agent_id, _ in candidates]
    
    def delegate_task(self, from_agent: str, to_agent: str, 
                     task_description: str, context: Dict = None) -> Dict:
        """
        Delegate a task from one agent to another following hierarchy rules.
        
        Args:
            from_agent: Agent ID delegating the task
            to_agent: Agent ID receiving the delegation
            task_description: Description of the delegated task
            context: Additional context
        
        Returns:
            Delegation record
        """
        from_tier = self.agent_tiers.get(from_agent)
        to_tier = self.agent_tiers.get(to_agent)
        
        if not from_tier or not to_tier:
            raise ValueError("Invalid agent IDs")
        
        # Verify delegation is allowed
        if to_tier.role not in from_tier.can_delegate_to:
            raise ValueError(
                f"Agent {from_agent} ({from_tier.role.value}) cannot delegate to "
                f"{to_agent} ({to_tier.role.value})"
            )
        
        delegation = {
            'delegation_id': f"del-{int(datetime.now(timezone.utc).timestamp())}",
            'from_agent': from_agent,
            'from_role': from_tier.role.value,
            'to_agent': to_agent,
            'to_role': to_tier.role.value,
            'task_description': task_description,
            'context': context or {},
            'status': DelegationStatus.PENDING.value,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Log delegation
        self.delegation_log['delegation_chains'].append(delegation)
        self.delegation_log['statistics']['total_delegations'] += 1
        self._save_delegation_log()
        
        return delegation
    
    def escalate_task(self, from_agent: str, task_id: str, reason: str) -> Dict:
        """
        Escalate a task up the hierarchy when a lower-tier agent needs help.
        
        Args:
            from_agent: Agent ID requesting escalation
            task_id: ID of the task to escalate
            reason: Reason for escalation
        
        Returns:
            Escalation record
        """
        from_tier = self.agent_tiers.get(from_agent)
        if not from_tier:
            raise ValueError("Invalid agent ID")
        
        if not from_tier.reports_to:
            raise ValueError(f"Agent {from_agent} is at top of hierarchy, cannot escalate")
        
        # Find an agent in the reporting tier
        supervisor_role = from_tier.reports_to
        supervisors = [
            agent_id for agent_id, tier in self.agent_tiers.items()
            if tier.role == supervisor_role
        ]
        
        if not supervisors:
            raise ValueError(f"No {supervisor_role.value} agents available for escalation")
        
        # Select best supervisor (by performance)
        best_supervisor = max(
            supervisors,
            key=lambda a: self.base_coordinator.agents.get(a, {}).get('metrics', {}).get('overall_score', 0)
        )
        
        escalation = {
            'escalation_id': f"esc-{int(datetime.now(timezone.utc).timestamp())}",
            'from_agent': from_agent,
            'from_role': from_tier.role.value,
            'to_agent': best_supervisor,
            'to_role': supervisor_role.value,
            'task_id': task_id,
            'reason': reason,
            'status': 'pending',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Log escalation
        self.delegation_log['statistics']['escalations'] += 1
        self._save_delegation_log()
        
        return escalation
    
    def get_hierarchy_summary(self) -> Dict:
        """Get a summary of the hierarchical agent system"""
        summary = {
            'total_agents': len(self.agent_tiers),
            'by_role': {},
            'delegation_chains': len(self.delegation_log.get('delegation_chains', [])),
            'statistics': self.delegation_log.get('statistics', {}),
            'coordinator_agents': [],
            'specialist_agents': [],
            'worker_agents': []
        }
        
        # Count by role
        for tier in self.agent_tiers.values():
            role = tier.role.value
            summary['by_role'][role] = summary['by_role'].get(role, 0) + 1
            
            # Add to role-specific lists
            agent_info = {
                'agent_id': tier.agent_id,
                'specialization': tier.specialization
            }
            
            if tier.role == AgentRole.COORDINATOR:
                summary['coordinator_agents'].append(agent_info)
            elif tier.role == AgentRole.SPECIALIST:
                summary['specialist_agents'].append(agent_info)
            elif tier.role == AgentRole.WORKER:
                summary['worker_agents'].append(agent_info)
        
        return summary


def main():
    """Command-line interface for hierarchical agent system"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Hierarchical Agent System - Coordinate agents with role-based tiers'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show hierarchy summary')
    
    # Plan command
    plan_parser = subparsers.add_parser('plan', help='Create hierarchical coordination plan')
    plan_parser.add_argument('--task-id', required=True, help='Task ID')
    plan_parser.add_argument('--description', required=True, help='Task description')
    plan_parser.add_argument('--context', help='Task context (JSON)')
    
    # Delegate command
    delegate_parser = subparsers.add_parser('delegate', help='Delegate task between agents')
    delegate_parser.add_argument('--from', dest='from_agent', required=True, help='Delegating agent ID')
    delegate_parser.add_argument('--to', dest='to_agent', required=True, help='Receiving agent ID')
    delegate_parser.add_argument('--description', required=True, help='Task description')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List agents by role')
    list_parser.add_argument('--role', choices=['coordinator', 'specialist', 'worker'], 
                            help='Filter by role')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize system
    system = HierarchicalAgentSystem()
    
    if args.command == 'summary':
        summary = system.get_hierarchy_summary()
        print(json.dumps(summary, indent=2))
    
    elif args.command == 'plan':
        context = json.loads(args.context) if args.context else None
        plan, chain = system.create_hierarchical_plan(
            args.task_id,
            args.description,
            context
        )
        
        output = {
            'coordination_plan': plan.to_dict(),
            'delegation_chain': chain.to_dict()
        }
        print(json.dumps(output, indent=2))
    
    elif args.command == 'delegate':
        delegation = system.delegate_task(
            args.from_agent,
            args.to_agent,
            args.description
        )
        print(json.dumps(delegation, indent=2))
    
    elif args.command == 'list':
        if args.role == 'coordinator':
            agents = system.get_coordinator_agents()
        elif args.role == 'specialist':
            agents = system.get_specialist_agents()
        elif args.role == 'worker':
            agents = system.get_worker_agents()
        else:
            agents = list(system.agent_tiers.keys())
        
        output = {
            'role': args.role or 'all',
            'count': len(agents),
            'agents': [
                {
                    'agent_id': agent_id,
                    'role': system.agent_tiers[agent_id].role.value,
                    'specialization': system.agent_tiers[agent_id].specialization
                }
                for agent_id in agents
            ]
        }
        print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
