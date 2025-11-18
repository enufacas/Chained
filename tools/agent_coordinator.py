#!/usr/bin/env python3
"""
Agent Coordination System

Enables sub-agents to coordinate and communicate about workload distribution.
Implements hibernation/wake-up cycles and cross-specialization collaboration.

Features:
- Agent-to-agent workload messaging
- Collaborative task distribution
- Hibernation for idle agents
- Wake-up triggers for needed agents
- Cross-domain collaboration patterns

Part of the Chained autonomous AI ecosystem.
Created by @accelerate-specialist - Efficient coordination with elegant algorithms.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from registry_manager import RegistryManager
except ImportError:
    RegistryManager = None


class AgentState(Enum):
    """Agent operational states"""
    ACTIVE = "active"
    IDLE = "idle"
    HIBERNATING = "hibernating"
    WAKING = "waking"


class MessageType(Enum):
    """Types of inter-agent messages"""
    WORKLOAD_OFFER = "workload_offer"
    WORKLOAD_REQUEST = "workload_request"
    COLLABORATION_INVITE = "collaboration_invite"
    HIBERNATION_NOTICE = "hibernation_notice"
    WAKE_REQUEST = "wake_request"
    STATUS_UPDATE = "status_update"


@dataclass
class AgentMessage:
    """Message between agents"""
    id: str
    timestamp: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcast
    message_type: str
    payload: Dict[str, Any]
    priority: int  # 1-5


@dataclass
class AgentWorkloadState:
    """Current workload state of an agent"""
    agent_id: str
    specialization: str
    state: str
    current_workload: int
    capacity: int
    utilization: float
    last_activity: str
    can_accept_work: bool


class AgentCoordinator:
    """
    Coordinates multiple agents for efficient workload distribution.
    
    Elegant coordination principles:
    - Decentralized decision-making
    - Minimal message passing overhead
    - Self-organizing task allocation
    - Graceful degradation
    """
    
    # Hibernation parameters
    IDLE_THRESHOLD_HOURS = 24  # Hours before considering hibernation
    HIBERNATION_UTILIZATION_THRESHOLD = 0.2  # 20% utilization triggers hibernation
    MIN_ACTIVE_AGENTS = 2  # Per specialization
    
    # Coordination files
    MESSAGES_FILE = ".github/agent-system/coordination/messages.json"
    STATES_FILE = ".github/agent-system/coordination/agent_states.json"
    
    def __init__(self, registry_path: str = ".github/agent-system"):
        """
        Initialize agent coordinator.
        
        Args:
            registry_path: Path to agent registry
        """
        self.registry_path = Path(registry_path)
        self.coordination_dir = self.registry_path / "coordination"
        self.coordination_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize registry
        if RegistryManager:
            try:
                self.registry = RegistryManager(str(self.registry_path))
            except Exception as e:
                print(f"Warning: Could not initialize registry: {e}")
                self.registry = None
        else:
            self.registry = None
        
        # Load coordination state
        self.messages = self._load_messages()
        self.agent_states = self._load_agent_states()
    
    def _load_messages(self) -> List[AgentMessage]:
        """Load inter-agent messages"""
        messages_path = Path(self.MESSAGES_FILE)
        
        if not messages_path.exists():
            return []
        
        try:
            with open(messages_path, 'r') as f:
                data = json.load(f)
            
            messages = []
            for msg_data in data.get('messages', []):
                messages.append(AgentMessage(**msg_data))
            
            return messages
        except Exception as e:
            print(f"Warning: Could not load messages: {e}")
            return []
    
    def _save_messages(self):
        """Save inter-agent messages"""
        messages_path = Path(self.MESSAGES_FILE)
        messages_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_messages': len(self.messages),
            'messages': [asdict(msg) for msg in self.messages[-100:]]  # Keep last 100
        }
        
        with open(messages_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_agent_states(self) -> Dict[str, AgentWorkloadState]:
        """Load agent workload states"""
        states_path = Path(self.STATES_FILE)
        
        if not states_path.exists():
            return {}
        
        try:
            with open(states_path, 'r') as f:
                data = json.load(f)
            
            states = {}
            for agent_id, state_data in data.get('states', {}).items():
                states[agent_id] = AgentWorkloadState(**state_data)
            
            return states
        except Exception as e:
            print(f"Warning: Could not load agent states: {e}")
            return {}
    
    def _save_agent_states(self):
        """Save agent workload states"""
        states_path = Path(self.STATES_FILE)
        states_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_agents': len(self.agent_states),
            'states': {
                agent_id: asdict(state)
                for agent_id, state in self.agent_states.items()
            }
        }
        
        with open(states_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_agent_state(self,
                          agent_id: str,
                          specialization: str,
                          current_workload: int,
                          capacity: int = 10) -> AgentWorkloadState:
        """
        Update workload state for an agent.
        
        Args:
            agent_id: Agent identifier
            specialization: Agent specialization
            current_workload: Current number of assigned tasks
            capacity: Maximum capacity
            
        Returns:
            Updated AgentWorkloadState
        """
        utilization = current_workload / capacity if capacity > 0 else 0.0
        
        state = AgentWorkloadState(
            agent_id=agent_id,
            specialization=specialization,
            state=AgentState.ACTIVE.value,
            current_workload=current_workload,
            capacity=capacity,
            utilization=utilization,
            last_activity=datetime.now().isoformat(),
            can_accept_work=current_workload < capacity
        )
        
        self.agent_states[agent_id] = state
        self._save_agent_states()
        
        return state
    
    def send_message(self,
                    from_agent: str,
                    to_agent: Optional[str],
                    message_type: MessageType,
                    payload: Dict[str, Any],
                    priority: int = 3) -> AgentMessage:
        """
        Send a message from one agent to another (or broadcast).
        
        Args:
            from_agent: Sending agent ID
            to_agent: Receiving agent ID (None for broadcast)
            message_type: Type of message
            payload: Message content
            priority: Message priority (1-5)
            
        Returns:
            Created AgentMessage
        """
        message = AgentMessage(
            id=f"msg-{datetime.now().timestamp()}-{abs(hash(from_agent)) % 10000}",
            timestamp=datetime.now().isoformat(),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type.value,
            payload=payload,
            priority=priority
        )
        
        self.messages.append(message)
        self._save_messages()
        
        return message
    
    def get_messages_for_agent(self, agent_id: str) -> List[AgentMessage]:
        """
        Get all unread messages for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            List of messages addressed to this agent or broadcast
        """
        return [
            msg for msg in self.messages
            if msg.to_agent == agent_id or msg.to_agent is None
        ]
    
    def redistribute_workload(self, specialization: str) -> List[AgentMessage]:
        """
        Redistribute workload among agents of a specialization.
        
        Finds overloaded and underutilized agents and coordinates transfers.
        
        Args:
            specialization: Specialization to balance
            
        Returns:
            List of coordination messages sent
        """
        # Get agents of this specialization
        agents = [
            state for state in self.agent_states.values()
            if state.specialization == specialization
            and state.state == AgentState.ACTIVE.value
        ]
        
        if len(agents) < 2:
            return []  # Need at least 2 agents to redistribute
        
        # Sort by utilization
        agents.sort(key=lambda a: a.utilization)
        
        messages = []
        
        # Match overloaded with underutilized
        underutilized = [a for a in agents if a.utilization < 0.5 and a.can_accept_work]
        overloaded = [a for a in agents if a.utilization > 0.8]
        
        for overloaded_agent in overloaded:
            for underutilized_agent in underutilized:
                if not underutilized_agent.can_accept_work:
                    continue
                
                # Calculate transfer amount
                excess = overloaded_agent.current_workload - (overloaded_agent.capacity * 0.7)
                available = underutilized_agent.capacity - underutilized_agent.current_workload
                transfer = min(int(excess), int(available))
                
                if transfer > 0:
                    # Send workload offer
                    msg = self.send_message(
                        from_agent=overloaded_agent.agent_id,
                        to_agent=underutilized_agent.agent_id,
                        message_type=MessageType.WORKLOAD_OFFER,
                        payload={
                            'specialization': specialization,
                            'workload_count': transfer,
                            'reason': 'load_balancing'
                        },
                        priority=4
                    )
                    messages.append(msg)
                    
                    # Update workload estimates
                    underutilized_agent.current_workload += transfer
                    underutilized_agent.utilization = (
                        underutilized_agent.current_workload / underutilized_agent.capacity
                    )
        
        return messages
    
    def identify_hibernation_candidates(self) -> List[AgentWorkloadState]:
        """
        Identify agents that should be hibernated due to low utilization.
        
        Returns:
            List of agents recommended for hibernation
        """
        candidates = []
        
        # Group agents by specialization
        by_spec = {}
        for agent_id, state in self.agent_states.items():
            if state.state != AgentState.ACTIVE.value:
                continue
            
            if state.specialization not in by_spec:
                by_spec[state.specialization] = []
            by_spec[state.specialization].append(state)
        
        # Check each specialization
        for spec, agents in by_spec.items():
            if len(agents) <= self.MIN_ACTIVE_AGENTS:
                continue  # Keep minimum active
            
            # Check for idle agents
            for agent in agents:
                # Skip if recently active
                last_activity = datetime.fromisoformat(agent.last_activity)
                hours_idle = (datetime.now() - last_activity).total_seconds() / 3600
                
                if hours_idle < self.IDLE_THRESHOLD_HOURS:
                    continue
                
                # Check utilization
                if agent.utilization <= self.HIBERNATION_UTILIZATION_THRESHOLD:
                    candidates.append(agent)
        
        return candidates
    
    def hibernate_agent(self, agent_id: str, reason: str = "low_utilization"):
        """
        Put an agent into hibernation.
        
        Args:
            agent_id: Agent to hibernate
            reason: Reason for hibernation
        """
        if agent_id not in self.agent_states:
            return
        
        state = self.agent_states[agent_id]
        state.state = AgentState.HIBERNATING.value
        
        # Broadcast hibernation notice
        self.send_message(
            from_agent=agent_id,
            to_agent=None,  # Broadcast
            message_type=MessageType.HIBERNATION_NOTICE,
            payload={
                'specialization': state.specialization,
                'reason': reason,
                'last_workload': state.current_workload
            },
            priority=2
        )
        
        self._save_agent_states()
    
    def wake_agent(self, agent_id: str, reason: str = "workload_increase"):
        """
        Wake an agent from hibernation.
        
        Args:
            agent_id: Agent to wake
            reason: Reason for waking
        """
        if agent_id not in self.agent_states:
            return
        
        state = self.agent_states[agent_id]
        state.state = AgentState.ACTIVE.value
        state.last_activity = datetime.now().isoformat()
        
        # Broadcast wake notice
        self.send_message(
            from_agent="system",
            to_agent=agent_id,
            message_type=MessageType.WAKE_REQUEST,
            payload={
                'specialization': state.specialization,
                'reason': reason
            },
            priority=5
        )
        
        self._save_agent_states()
    
    def suggest_cross_specialization_collaboration(self) -> List[Dict[str, Any]]:
        """
        Identify opportunities for cross-specialization collaboration.
        
        Returns:
            List of collaboration suggestions
        """
        suggestions = []
        
        # Common collaboration patterns
        patterns = [
            {
                'primary': 'security',
                'secondary': 'testing',
                'reason': 'Security testing collaboration'
            },
            {
                'primary': 'performance',
                'secondary': 'refactoring',
                'reason': 'Performance optimization with refactoring'
            },
            {
                'primary': 'feature',
                'secondary': 'documentation',
                'reason': 'Feature development with documentation'
            },
            {
                'primary': 'api',
                'secondary': 'testing',
                'reason': 'API development with integration testing'
            }
        ]
        
        for pattern in patterns:
            # Find active agents in both specializations
            primary_agents = [
                state for state in self.agent_states.values()
                if state.specialization == pattern['primary']
                and state.state == AgentState.ACTIVE.value
                and state.utilization < 0.9  # Has capacity
            ]
            
            secondary_agents = [
                state for state in self.agent_states.values()
                if state.specialization == pattern['secondary']
                and state.state == AgentState.ACTIVE.value
                and state.utilization < 0.9  # Has capacity
            ]
            
            if primary_agents and secondary_agents:
                suggestions.append({
                    'primary_agent': primary_agents[0].agent_id,
                    'secondary_agent': secondary_agents[0].agent_id,
                    'primary_spec': pattern['primary'],
                    'secondary_spec': pattern['secondary'],
                    'reason': pattern['reason']
                })
        
        return suggestions
    
    def generate_coordination_report(self) -> str:
        """
        Generate coordination status report.
        
        Returns:
            Formatted report string
        """
        lines = [
            "# 🤝 Agent Coordination Report",
            f"\n**Generated:** {datetime.now().isoformat()}",
            "\n## Active Agents\n"
        ]
        
        # Count by state
        by_state = {'active': 0, 'idle': 0, 'hibernating': 0}
        by_spec = {}
        
        for state in self.agent_states.values():
            by_state[state.state] = by_state.get(state.state, 0) + 1
            
            if state.state == AgentState.ACTIVE.value:
                by_spec[state.specialization] = by_spec.get(state.specialization, 0) + 1
        
        lines.extend([
            f"- **Active:** {by_state.get('active', 0)}",
            f"- **Hibernating:** {by_state.get('hibernating', 0)}",
            f"- **Total Tracked:** {len(self.agent_states)}",
            "\n## Workload Distribution\n"
        ])
        
        for spec, count in sorted(by_spec.items()):
            agents = [
                s for s in self.agent_states.values()
                if s.specialization == spec and s.state == AgentState.ACTIVE.value
            ]
            
            if agents:
                avg_util = sum(a.utilization for a in agents) / len(agents)
                lines.append(f"- **{spec.capitalize()}:** {count} agents, "
                           f"{avg_util:.0%} avg utilization")
        
        # Recent messages
        lines.extend([
            "\n## Recent Messages\n",
            f"- **Total Messages:** {len(self.messages)}",
            f"- **Last 24h:** {len([m for m in self.messages if (datetime.now() - datetime.fromisoformat(m.timestamp)).days == 0])}"
        ])
        
        # Hibernation candidates
        candidates = self.identify_hibernation_candidates()
        if candidates:
            lines.extend([
                "\n## Hibernation Candidates\n",
                f"- **Count:** {len(candidates)}"
            ])
            for candidate in candidates[:5]:
                lines.append(f"  - {candidate.agent_id} ({candidate.specialization}): "
                           f"{candidate.utilization:.0%} utilization")
        
        # Collaboration opportunities
        collabs = self.suggest_cross_specialization_collaboration()
        if collabs:
            lines.extend([
                "\n## Collaboration Opportunities\n",
                f"- **Count:** {len(collabs)}"
            ])
            for collab in collabs[:5]:
                lines.append(f"  - {collab['primary_spec']} + {collab['secondary_spec']}: "
                           f"{collab['reason']}")
        
        return '\n'.join(lines)


def main():
    """CLI interface for agent coordination"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Agent coordination and workload distribution'
    )
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='Generate coordination report'
    )
    parser.add_argument(
        '--redistribute', '-d',
        metavar='SPEC',
        help='Redistribute workload for specialization'
    )
    parser.add_argument(
        '--hibernate-idle', '-h',
        action='store_true',
        help='Hibernate idle agents'
    )
    
    args = parser.parse_args()
    
    # Create coordinator
    coordinator = AgentCoordinator()
    
    if args.report:
        print(coordinator.generate_coordination_report())
    
    if args.redistribute:
        print(f"\n🔄 Redistributing {args.redistribute} workload...")
        messages = coordinator.redistribute_workload(args.redistribute)
        print(f"✅ Sent {len(messages)} coordination message(s)")
    
    if args.hibernate_idle:
        print("\n😴 Checking for idle agents...")
        candidates = coordinator.identify_hibernation_candidates()
        print(f"Found {len(candidates)} hibernation candidate(s)")
        
        for candidate in candidates:
            print(f"  Hibernating: {candidate.agent_id} ({candidate.specialization})")
            coordinator.hibernate_agent(candidate.agent_id)
        
        print(f"✅ Hibernated {len(candidates)} agent(s)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
