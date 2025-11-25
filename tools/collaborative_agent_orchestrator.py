#!/usr/bin/env python3
"""
Collaborative Agent Orchestrator

A unified system for coordinating specialized AI agents on complex tasks.
Combines task decomposition, hierarchical delegation, and real-time 
collaboration capabilities for the meta-coordinator.

Features:
- Unified interface for meta-agent coordination
- Real-time collaboration protocol between agents
- Progress tracking and status aggregation
- Automatic agent selection based on specialization and performance
- Support for parallel and sequential task execution
- Integration with existing agent system

Part of the Chained autonomous AI ecosystem.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import hashlib
import uuid

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from meta_agent_coordinator import (
        MetaAgentCoordinator,
        CoordinationPlan,
        SubTask,
        TaskComplexity,
        TaskStatus
    )
    from hierarchical_agent_system import (
        HierarchicalAgentSystem,
        AgentRole,
        DelegationChain,
        DelegationStatus
    )
except ImportError as e:
    print(f"Warning: Could not import dependencies: {e}", file=sys.stderr)


class CollaborationStatus(Enum):
    """Status of a collaboration session"""
    INITIALIZING = "initializing"
    PLANNING = "planning"
    DELEGATING = "delegating"
    EXECUTING = "executing"
    INTEGRATING = "integrating"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class AgentMessage(Enum):
    """Types of messages agents can exchange"""
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    PROGRESS_UPDATE = "progress_update"
    BLOCKED = "blocked"
    HELP_NEEDED = "help_needed"
    TASK_COMPLETED = "task_completed"
    INTEGRATION_READY = "integration_ready"
    REVIEW_REQUESTED = "review_requested"


@dataclass
class CollaborationMessage:
    """A message in the collaboration protocol"""
    id: str
    from_agent: str
    to_agents: List[str]
    message_type: AgentMessage
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    read_by: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'from_agent': self.from_agent,
            'to_agents': self.to_agents,
            'message_type': self.message_type.value,
            'content': self.content,
            'timestamp': self.timestamp,
            'read_by': self.read_by
        }


@dataclass
class CollaborationSession:
    """A collaboration session for a complex task"""
    session_id: str
    task_id: str
    task_description: str
    status: CollaborationStatus
    coordinator_agent: str
    participating_agents: Set[str]
    plan: Optional[CoordinationPlan]
    delegation_chain: Optional[DelegationChain]
    messages: List[CollaborationMessage]
    progress: Dict[str, float]  # subtask_id -> completion percentage
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'session_id': self.session_id,
            'task_id': self.task_id,
            'task_description': self.task_description,
            'status': self.status.value,
            'coordinator_agent': self.coordinator_agent,
            'participating_agents': list(self.participating_agents),
            'plan': self.plan.to_dict() if self.plan else None,
            'delegation_chain': self.delegation_chain.to_dict() if self.delegation_chain else None,
            'messages': [m.to_dict() for m in self.messages],
            'progress': self.progress,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at,
            'metadata': self.metadata
        }


class CollaborativeAgentOrchestrator:
    """
    Unified orchestrator for multi-agent collaboration.
    
    Combines the capabilities of MetaAgentCoordinator and HierarchicalAgentSystem
    to provide a complete solution for coordinating specialized agents.
    """
    
    def __init__(self, repo_root: str = None):
        """
        Initialize the collaborative orchestrator.
        
        Args:
            repo_root: Root directory of the repository
        """
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            # Detect repository root
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path.cwd()
        
        # Initialize subsystems
        self.coordinator = MetaAgentCoordinator(str(self.repo_root))
        self.hierarchy = HierarchicalAgentSystem(str(self.repo_root))
        
        # Session storage
        self.sessions_path = self.repo_root / '.github/agent-system/collaboration_sessions.json'
        self.sessions = self._load_sessions()
    
    def _load_sessions(self) -> Dict[str, CollaborationSession]:
        """Load existing collaboration sessions"""
        sessions = {}
        if self.sessions_path.exists():
            try:
                with open(self.sessions_path, 'r') as f:
                    data = json.load(f)
                for session_data in data.get('sessions', []):
                    # Reconstruct session objects
                    sessions[session_data['session_id']] = self._session_from_dict(session_data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load sessions: {e}", file=sys.stderr)
        return sessions
    
    def _session_from_dict(self, data: Dict) -> CollaborationSession:
        """Reconstruct a CollaborationSession from dictionary"""
        messages = [
            CollaborationMessage(
                id=m['id'],
                from_agent=m['from_agent'],
                to_agents=m['to_agents'],
                message_type=AgentMessage(m['message_type']),
                content=m['content'],
                timestamp=m['timestamp'],
                read_by=m.get('read_by', [])
            )
            for m in data.get('messages', [])
        ]
        
        return CollaborationSession(
            session_id=data['session_id'],
            task_id=data['task_id'],
            task_description=data['task_description'],
            status=CollaborationStatus(data['status']),
            coordinator_agent=data['coordinator_agent'],
            participating_agents=set(data['participating_agents']),
            plan=None,  # Plans are reconstructed separately if needed
            delegation_chain=None,
            messages=messages,
            progress=data.get('progress', {}),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            completed_at=data.get('completed_at'),
            metadata=data.get('metadata', {})
        )
    
    def _save_sessions(self):
        """Save all collaboration sessions"""
        self.sessions_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'version': '1.0.0',
            'sessions': [s.to_dict() for s in self.sessions.values()]
        }
        with open(self.sessions_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _generate_session_id(self, task_id: str) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        unique = hashlib.md5(f"{task_id}{timestamp}{uuid.uuid4()}".encode()).hexdigest()[:8]
        return f"collab-{task_id}-{timestamp}-{unique}"
    
    def _generate_message_id(self) -> str:
        """Generate a unique message ID"""
        return f"msg-{uuid.uuid4().hex[:12]}"
    
    def start_collaboration(
        self,
        task_id: str,
        task_description: str,
        task_context: Dict = None,
        force_complexity: TaskComplexity = None
    ) -> CollaborationSession:
        """
        Start a new collaboration session for a complex task.
        
        Args:
            task_id: Unique identifier for the task (e.g., issue number)
            task_description: Description of the task to coordinate
            task_context: Additional context (labels, comments, etc.)
            force_complexity: Force a specific complexity level
        
        Returns:
            CollaborationSession with the coordination plan
        """
        session_id = self._generate_session_id(task_id)
        
        # Create initial session
        session = CollaborationSession(
            session_id=session_id,
            task_id=task_id,
            task_description=task_description,
            status=CollaborationStatus.INITIALIZING,
            coordinator_agent='meta-coordinator',
            participating_agents={'meta-coordinator'},
            plan=None,
            delegation_chain=None,
            messages=[],
            progress={},
            metadata={'task_context': task_context or {}}
        )
        
        # Analyze and decompose task
        session.status = CollaborationStatus.PLANNING
        
        if force_complexity:
            # Use forced complexity
            plan = self.coordinator.decompose_task(task_id, task_description, task_context)
            plan.complexity = force_complexity
        else:
            plan = self.coordinator.decompose_task(task_id, task_description, task_context)
        
        session.plan = plan
        
        # Create hierarchical delegation chain
        _, delegation_chain = self.hierarchy.create_hierarchical_plan(
            task_id, task_description, task_context
        )
        session.delegation_chain = delegation_chain
        
        # Select agents for each subtask
        assignments = self.coordinator.select_agents(plan)
        
        # Add participating agents
        for agent_id in assignments.values():
            session.participating_agents.add(agent_id)
        
        # Initialize progress tracking
        for subtask in plan.sub_tasks:
            session.progress[subtask.id] = 0.0
        
        # Create task assignment messages
        session.status = CollaborationStatus.DELEGATING
        for subtask in plan.sub_tasks:
            agent = assignments.get(subtask.id)
            if agent:
                message = CollaborationMessage(
                    id=self._generate_message_id(),
                    from_agent='meta-coordinator',
                    to_agents=[agent],
                    message_type=AgentMessage.TASK_ASSIGNED,
                    content={
                        'subtask_id': subtask.id,
                        'description': subtask.description,
                        'priority': subtask.priority,
                        'dependencies': subtask.dependencies,
                        'completion_criteria': subtask.completion_criteria
                    }
                )
                session.messages.append(message)
        
        # Ready for execution
        session.status = CollaborationStatus.EXECUTING
        session.updated_at = datetime.now(timezone.utc).isoformat()
        
        # Store session
        self.sessions[session_id] = session
        self._save_sessions()
        
        return session
    
    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get a collaboration session by ID"""
        return self.sessions.get(session_id)
    
    def list_active_sessions(self) -> List[CollaborationSession]:
        """List all active collaboration sessions"""
        active_statuses = {
            CollaborationStatus.PLANNING,
            CollaborationStatus.DELEGATING,
            CollaborationStatus.EXECUTING,
            CollaborationStatus.INTEGRATING
        }
        return [
            s for s in self.sessions.values()
            if s.status in active_statuses
        ]
    
    def send_message(
        self,
        session_id: str,
        from_agent: str,
        to_agents: List[str],
        message_type: AgentMessage,
        content: Dict[str, Any]
    ) -> CollaborationMessage:
        """
        Send a message in a collaboration session.
        
        Args:
            session_id: ID of the collaboration session
            from_agent: ID of the sending agent
            to_agents: List of recipient agent IDs
            message_type: Type of message
            content: Message content
        
        Returns:
            The created message
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        message = CollaborationMessage(
            id=self._generate_message_id(),
            from_agent=from_agent,
            to_agents=to_agents,
            message_type=message_type,
            content=content
        )
        
        session.messages.append(message)
        session.updated_at = datetime.now(timezone.utc).isoformat()
        
        self._save_sessions()
        return message
    
    def update_progress(
        self,
        session_id: str,
        subtask_id: str,
        progress: float,
        agent_id: str
    ) -> None:
        """
        Update progress on a subtask.
        
        Args:
            session_id: ID of the collaboration session
            subtask_id: ID of the subtask
            progress: Completion percentage (0.0 to 100.0)
            agent_id: ID of the agent reporting progress
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.progress[subtask_id] = min(max(progress, 0.0), 100.0)
        session.updated_at = datetime.now(timezone.utc).isoformat()
        
        # Send progress update message
        self.send_message(
            session_id=session_id,
            from_agent=agent_id,
            to_agents=['meta-coordinator'],
            message_type=AgentMessage.PROGRESS_UPDATE,
            content={
                'subtask_id': subtask_id,
                'progress': progress,
                'status': 'in_progress' if progress < 100 else 'completed'
            }
        )
        
        # Check if subtask is complete
        if progress >= 100.0:
            self.send_message(
                session_id=session_id,
                from_agent=agent_id,
                to_agents=['meta-coordinator'],
                message_type=AgentMessage.TASK_COMPLETED,
                content={'subtask_id': subtask_id}
            )
        
        self._save_sessions()
    
    def mark_subtask_completed(
        self,
        session_id: str,
        subtask_id: str,
        agent_id: str,
        result: Dict = None
    ) -> None:
        """
        Mark a subtask as completed.
        
        Args:
            session_id: ID of the collaboration session
            subtask_id: ID of the subtask
            agent_id: ID of the completing agent
            result: Optional result data
        """
        self.update_progress(session_id, subtask_id, 100.0, agent_id)
        
        session = self.sessions.get(session_id)
        if session:
            # Check if all subtasks are complete
            all_complete = all(p >= 100.0 for p in session.progress.values())
            if all_complete:
                session.status = CollaborationStatus.INTEGRATING
                self._save_sessions()
    
    def complete_collaboration(
        self,
        session_id: str,
        summary: str = None
    ) -> CollaborationSession:
        """
        Mark a collaboration session as completed.
        
        Args:
            session_id: ID of the collaboration session
            summary: Optional completion summary
        
        Returns:
            The completed session
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.status = CollaborationStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc).isoformat()
        session.updated_at = session.completed_at
        
        if summary:
            session.metadata['completion_summary'] = summary
        
        self._save_sessions()
        return session
    
    def get_session_summary(self, session_id: str) -> Dict:
        """
        Get a summary of a collaboration session.
        
        Args:
            session_id: ID of the collaboration session
        
        Returns:
            Summary dictionary
        """
        session = self.sessions.get(session_id)
        if not session:
            return {'error': f'Session {session_id} not found'}
        
        # Calculate overall progress
        if session.progress:
            overall_progress = sum(session.progress.values()) / len(session.progress)
        else:
            overall_progress = 0.0
        
        # Count messages by type
        message_counts = {}
        for msg in session.messages:
            msg_type = msg.message_type.value
            message_counts[msg_type] = message_counts.get(msg_type, 0) + 1
        
        return {
            'session_id': session.session_id,
            'task_id': session.task_id,
            'status': session.status.value,
            'coordinator': session.coordinator_agent,
            'participating_agents': list(session.participating_agents),
            'subtask_count': len(session.progress),
            'overall_progress': round(overall_progress, 1),
            'completed_subtasks': sum(1 for p in session.progress.values() if p >= 100.0),
            'message_count': len(session.messages),
            'message_types': message_counts,
            'created_at': session.created_at,
            'updated_at': session.updated_at,
            'completed_at': session.completed_at,
            'duration': self._calculate_duration(session)
        }
    
    def _calculate_duration(self, session: CollaborationSession) -> str:
        """Calculate the duration of a session"""
        start = datetime.fromisoformat(session.created_at.replace('Z', '+00:00'))
        end_str = session.completed_at or session.updated_at
        end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        
        delta = end - start
        hours = delta.total_seconds() / 3600
        
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            return f"{hours / 24:.1f} days"
    
    def get_pending_messages(
        self,
        agent_id: str,
        session_id: str = None
    ) -> List[CollaborationMessage]:
        """
        Get unread messages for an agent.
        
        Args:
            agent_id: ID of the agent
            session_id: Optional specific session ID
        
        Returns:
            List of unread messages
        """
        pending = []
        
        sessions = [self.sessions[session_id]] if session_id else self.sessions.values()
        
        for session in sessions:
            for msg in session.messages:
                if agent_id in msg.to_agents and agent_id not in msg.read_by:
                    pending.append(msg)
        
        return pending
    
    def mark_message_read(
        self,
        message_id: str,
        agent_id: str
    ) -> None:
        """Mark a message as read by an agent"""
        for session in self.sessions.values():
            for msg in session.messages:
                if msg.id == message_id:
                    if agent_id not in msg.read_by:
                        msg.read_by.append(agent_id)
                    self._save_sessions()
                    return
    
    def request_help(
        self,
        session_id: str,
        from_agent: str,
        subtask_id: str,
        reason: str
    ) -> CollaborationMessage:
        """
        Request help from the coordinator for a subtask.
        
        Args:
            session_id: ID of the collaboration session
            from_agent: ID of the requesting agent
            subtask_id: ID of the subtask
            reason: Reason for requesting help
        
        Returns:
            The help request message
        """
        return self.send_message(
            session_id=session_id,
            from_agent=from_agent,
            to_agents=['meta-coordinator'],
            message_type=AgentMessage.HELP_NEEDED,
            content={
                'subtask_id': subtask_id,
                'reason': reason,
                'agent_specialization': self._get_agent_specialization(from_agent)
            }
        )
    
    def _get_agent_specialization(self, agent_id: str) -> str:
        """Get the specialization of an agent"""
        agent = self.coordinator.agents.get(agent_id)
        if agent:
            return agent.get('specialization', 'unknown')
        return 'unknown'
    
    def report_blocked(
        self,
        session_id: str,
        from_agent: str,
        subtask_id: str,
        blocking_subtasks: List[str],
        reason: str
    ) -> CollaborationMessage:
        """
        Report that a subtask is blocked.
        
        Args:
            session_id: ID of the collaboration session
            from_agent: ID of the reporting agent
            subtask_id: ID of the blocked subtask
            blocking_subtasks: IDs of subtasks causing the block
            reason: Reason for the block
        
        Returns:
            The block report message
        """
        return self.send_message(
            session_id=session_id,
            from_agent=from_agent,
            to_agents=['meta-coordinator'],
            message_type=AgentMessage.BLOCKED,
            content={
                'subtask_id': subtask_id,
                'blocking_subtasks': blocking_subtasks,
                'reason': reason
            }
        )
    
    def request_review(
        self,
        session_id: str,
        from_agent: str,
        subtask_id: str,
        reviewer_agents: List[str] = None
    ) -> CollaborationMessage:
        """
        Request a review for completed work.
        
        Args:
            session_id: ID of the collaboration session
            from_agent: ID of the requesting agent
            subtask_id: ID of the subtask to review
            reviewer_agents: Optional specific reviewers
        
        Returns:
            The review request message
        """
        reviewers = reviewer_agents or ['meta-coordinator']
        
        return self.send_message(
            session_id=session_id,
            from_agent=from_agent,
            to_agents=reviewers,
            message_type=AgentMessage.REVIEW_REQUESTED,
            content={
                'subtask_id': subtask_id,
                'agent': from_agent
            }
        )
    
    def get_collaboration_stats(self) -> Dict:
        """Get overall collaboration statistics"""
        stats = {
            'total_sessions': len(self.sessions),
            'active_sessions': 0,
            'completed_sessions': 0,
            'failed_sessions': 0,
            'total_messages': 0,
            'unique_agents': set(),
            'avg_subtasks_per_session': 0.0,
            'avg_agents_per_session': 0.0
        }
        
        subtask_counts = []
        agent_counts = []
        
        for session in self.sessions.values():
            if session.status == CollaborationStatus.COMPLETED:
                stats['completed_sessions'] += 1
            elif session.status == CollaborationStatus.FAILED:
                stats['failed_sessions'] += 1
            elif session.status not in {CollaborationStatus.COMPLETED, CollaborationStatus.FAILED}:
                stats['active_sessions'] += 1
            
            stats['total_messages'] += len(session.messages)
            stats['unique_agents'].update(session.participating_agents)
            subtask_counts.append(len(session.progress))
            agent_counts.append(len(session.participating_agents))
        
        if subtask_counts:
            stats['avg_subtasks_per_session'] = sum(subtask_counts) / len(subtask_counts)
        if agent_counts:
            stats['avg_agents_per_session'] = sum(agent_counts) / len(agent_counts)
        
        stats['unique_agents'] = len(stats['unique_agents'])
        
        return stats


def main():
    """Command-line interface for collaborative orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Collaborative Agent Orchestrator - Coordinate specialized AI agents'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start a new collaboration session')
    start_parser.add_argument('--task-id', required=True, help='Task ID (e.g., issue number)')
    start_parser.add_argument('--description', required=True, help='Task description')
    start_parser.add_argument('--context', help='Task context (JSON)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get session status')
    status_parser.add_argument('--session-id', required=True, help='Session ID')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List collaboration sessions')
    list_parser.add_argument('--active', action='store_true', help='Show only active sessions')
    
    # Progress command
    progress_parser = subparsers.add_parser('progress', help='Update subtask progress')
    progress_parser.add_argument('--session-id', required=True, help='Session ID')
    progress_parser.add_argument('--subtask-id', required=True, help='Subtask ID')
    progress_parser.add_argument('--progress', required=True, type=float, help='Progress percentage')
    progress_parser.add_argument('--agent', required=True, help='Agent ID')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show collaboration statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    orchestrator = CollaborativeAgentOrchestrator()
    
    if args.command == 'start':
        context = json.loads(args.context) if args.context else None
        session = orchestrator.start_collaboration(
            args.task_id,
            args.description,
            context
        )
        print(json.dumps(session.to_dict(), indent=2))
    
    elif args.command == 'status':
        summary = orchestrator.get_session_summary(args.session_id)
        print(json.dumps(summary, indent=2))
    
    elif args.command == 'list':
        if args.active:
            sessions = orchestrator.list_active_sessions()
        else:
            sessions = list(orchestrator.sessions.values())
        
        output = {
            'count': len(sessions),
            'sessions': [orchestrator.get_session_summary(s.session_id) for s in sessions]
        }
        print(json.dumps(output, indent=2))
    
    elif args.command == 'progress':
        orchestrator.update_progress(
            args.session_id,
            args.subtask_id,
            args.progress,
            args.agent
        )
        print(f"✓ Progress updated: {args.subtask_id} = {args.progress}%")
    
    elif args.command == 'stats':
        stats = orchestrator.get_collaboration_stats()
        print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
