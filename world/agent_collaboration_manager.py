#!/usr/bin/env python3
"""
Agent Collaboration Manager - Orchestrate cross-agent collaboration

This module manages collaboration between agents in the Chained autonomous AI ecosystem.
It enables agents to request help from specialists, tracks collaboration outcomes,
and builds a knowledge graph of successful agent interactions.

Created by: @coordinate-wizard
Date: 2025-11-15
Version: 1.0

Philosophy:
    "Music is the soul of language." - Quincy Jones
    Like a great orchestra, agents harmonize their expertise through collaboration.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict


class CollaborationStatus(Enum):
    """Status of a collaboration request."""
    PENDING = "pending"           # Awaiting acceptance
    ACCEPTED = "accepted"         # Helper agent has accepted
    IN_PROGRESS = "in_progress"   # Active collaboration
    COMPLETED = "completed"       # Successfully completed
    DECLINED = "declined"         # Helper declined to help
    ABANDONED = "abandoned"       # Requester abandoned request
    FAILED = "failed"            # Collaboration failed


class CollaborationType(Enum):
    """Types of collaboration between agents."""
    KNOWLEDGE_SHARE = "knowledge_share"     # Share expertise on a topic
    CODE_REVIEW = "code_review"             # Review code changes
    PAIR_PROGRAMMING = "pair_programming"   # Work together on implementation
    CONSULTATION = "consultation"           # Ask for advice/guidance
    DEBUGGING = "debugging"                 # Help debug an issue
    RESEARCH = "research"                   # Collaborate on research


@dataclass
class CollaborationRequest:
    """
    Represents a request for collaboration between agents.
    
    Attributes:
        request_id: Unique identifier for the request
        requester: Agent requesting help
        helper: Agent being asked to help (None if open request)
        collaboration_type: Type of collaboration needed
        topic: Main topic/area of collaboration
        learning_category: Related learning category (optional)
        description: Detailed description of what help is needed
        context: Additional context (issue number, PR, etc.)
        status: Current status of the request
        created_at: When request was created
        updated_at: When request was last updated
        accepted_at: When helper accepted (optional)
        completed_at: When collaboration completed (optional)
        priority: Priority level (0.0 - 1.0, higher = more urgent)
        estimated_duration: Estimated time needed (hours)
        tags: Additional tags for categorization
    """
    request_id: str
    requester: str
    collaboration_type: CollaborationType
    topic: str
    description: str
    status: CollaborationStatus = CollaborationStatus.PENDING
    helper: Optional[str] = None
    learning_category: Optional[str] = None
    context: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    accepted_at: Optional[str] = None
    completed_at: Optional[str] = None
    priority: float = 0.5
    estimated_duration: float = 1.0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['collaboration_type'] = self.collaboration_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CollaborationRequest':
        """Create from dictionary."""
        data = data.copy()
        data['collaboration_type'] = CollaborationType(data['collaboration_type'])
        data['status'] = CollaborationStatus(data['status'])
        return cls(**data)


@dataclass
class CollaborationOutcome:
    """
    Records the outcome of a completed collaboration.
    
    Attributes:
        request_id: Reference to the collaboration request
        success: Whether collaboration was successful
        duration_hours: Actual duration of collaboration
        outcome_description: Description of what was accomplished
        learning_gained: What the requester learned
        knowledge_shared: What knowledge was shared
        value_rating: Perceived value (0.0 - 1.0)
        would_collaborate_again: Whether agents would work together again
        artifacts: Links to work produced (PRs, issues, docs)
        feedback_requester: Feedback from requesting agent
        feedback_helper: Feedback from helping agent
    """
    request_id: str
    success: bool
    duration_hours: float
    outcome_description: str
    learning_gained: str = ""
    knowledge_shared: str = ""
    value_rating: float = 0.5
    would_collaborate_again: bool = True
    artifacts: List[str] = field(default_factory=list)
    feedback_requester: str = ""
    feedback_helper: str = ""
    recorded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CollaborationOutcome':
        """Create from dictionary."""
        return cls(**data)


class AgentCollaborationManager:
    """
    Manages collaboration between agents in the ecosystem.
    
    This manager orchestrates:
    - Creation and matching of collaboration requests
    - Finding suitable helper agents based on expertise
    - Tracking collaboration status and outcomes
    - Building collaboration history and patterns
    - Preventing overload and circular dependencies
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the collaboration manager.
        
        Args:
            data_path: Path to collaboration data JSON file
        """
        if data_path is None:
            data_path = Path(__file__).parent / "agent_collaborations.json"
        
        self.data_path = Path(data_path)
        self.data = self._load_data()
        
        # Integration points
        self.investment_tracker = None
        self.learning_matcher = None
    
    def _load_data(self) -> Dict:
        """Load collaboration data from JSON file."""
        if not self.data_path.exists():
            return self._create_empty_data()
        
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                
            # Convert stored data back to objects
            if 'active_requests' in data:
                data['active_requests'] = {
                    req_id: CollaborationRequest.from_dict(req_data)
                    for req_id, req_data in data['active_requests'].items()
                }
            
            if 'completed_requests' in data:
                data['completed_requests'] = {
                    req_id: CollaborationRequest.from_dict(req_data)
                    for req_id, req_data in data['completed_requests'].items()
                }
            
            if 'outcomes' in data:
                data['outcomes'] = {
                    req_id: CollaborationOutcome.from_dict(outcome_data)
                    for req_id, outcome_data in data['outcomes'].items()
                }
            
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading collaboration data: {e}")
            return self._create_empty_data()
    
    def _create_empty_data(self) -> Dict:
        """Create empty collaboration data structure."""
        return {
            'version': '1.0',
            'last_updated': datetime.utcnow().isoformat(),
            'active_requests': {},
            'completed_requests': {},
            'outcomes': {},
            'collaboration_graph': {},  # Agent -> [Agents they've collaborated with]
            'statistics': {
                'total_requests': 0,
                'total_completed': 0,
                'total_successful': 0,
                'average_duration': 0.0,
                'average_value_rating': 0.0
            }
        }
    
    def _save_data(self):
        """Save collaboration data to JSON file."""
        data_to_save = self.data.copy()
        
        # Convert objects to dictionaries
        data_to_save['active_requests'] = {
            req_id: req.to_dict()
            for req_id, req in self.data['active_requests'].items()
        }
        
        data_to_save['completed_requests'] = {
            req_id: req.to_dict()
            for req_id, req in self.data['completed_requests'].items()
        }
        
        data_to_save['outcomes'] = {
            req_id: outcome.to_dict()
            for req_id, outcome in self.data['outcomes'].items()
        }
        
        data_to_save['last_updated'] = datetime.utcnow().isoformat()
        
        # Ensure directory exists
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.data_path, 'w') as f:
            json.dump(data_to_save, f, indent=2)
    
    def create_request(
        self,
        requester: str,
        collaboration_type: CollaborationType,
        topic: str,
        description: str,
        helper: Optional[str] = None,
        learning_category: Optional[str] = None,
        priority: float = 0.5,
        estimated_duration: float = 1.0,
        context: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> CollaborationRequest:
        """
        Create a new collaboration request.
        
        Args:
            requester: Agent requesting help
            collaboration_type: Type of collaboration
            topic: Main topic/area
            description: Detailed description
            helper: Specific helper agent (None for open request)
            learning_category: Related learning category
            priority: Priority (0.0 - 1.0)
            estimated_duration: Estimated hours needed
            context: Additional context
            tags: Categorization tags
            
        Returns:
            Created CollaborationRequest
        """
        # Generate unique request ID with microseconds
        now = datetime.utcnow()
        timestamp = now.strftime('%Y%m%d-%H%M%S') + f'-{now.microsecond:06d}'
        request_id = f"collab-{requester}-{timestamp}"
        
        request = CollaborationRequest(
            request_id=request_id,
            requester=requester,
            collaboration_type=collaboration_type,
            topic=topic,
            description=description,
            helper=helper,
            learning_category=learning_category,
            priority=priority,
            estimated_duration=estimated_duration,
            context=context or {},
            tags=tags or []
        )
        
        self.data['active_requests'][request_id] = request
        self.data['statistics']['total_requests'] += 1
        self._save_data()
        
        return request
    
    def find_helpers(
        self,
        topic: str,
        learning_category: Optional[str] = None,
        collaboration_type: Optional[CollaborationType] = None,
        exclude_agents: Optional[List[str]] = None,
        max_results: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find suitable helper agents for a topic.
        
        This uses a multi-factor scoring system considering:
        - Expertise in the learning category (from investment tracker)
        - Past collaboration success
        - Current workload (number of active collaborations)
        - Availability (not overloaded)
        
        Args:
            topic: Topic needing help with
            learning_category: Optional learning category
            collaboration_type: Optional collaboration type filter
            exclude_agents: Agents to exclude from search
            max_results: Maximum number of helpers to return
            
        Returns:
            List of (agent_name, score) tuples, sorted by score descending
        """
        exclude_agents = exclude_agents or []
        agent_scores = {}
        
        # Get all agents from collaboration graph and investment tracker
        all_agents = set()
        
        if self.data['collaboration_graph']:
            for agent in self.data['collaboration_graph'].keys():
                all_agents.add(agent)
        
        # Try to get agents from investment tracker
        if self.investment_tracker:
            try:
                investments = self.investment_tracker.get_all_investments()
                for agent in investments.keys():
                    all_agents.add(agent)
            except Exception:
                pass
        
        # If we have a learning category and investment tracker, use expertise
        if learning_category and self.investment_tracker:
            try:
                # Get agents invested in this category
                category_investments = self.investment_tracker.get_category_investments(
                    learning_category
                )
                
                for agent, investment in category_investments.items():
                    if agent in exclude_agents:
                        continue
                    
                    # Base score from investment level
                    score = investment.score / 100.0
                    agent_scores[agent] = score
            except Exception:
                pass
        
        # Factor in collaboration history
        for agent in all_agents:
            if agent in exclude_agents:
                continue
            
            if agent not in agent_scores:
                agent_scores[agent] = 0.5  # Base score
            
            # Boost score based on successful past collaborations
            past_success = self._get_collaboration_success_rate(agent)
            agent_scores[agent] = agent_scores[agent] * 0.7 + past_success * 0.3
            
            # Penalize for current workload
            workload = self._get_agent_workload(agent)
            workload_penalty = min(workload * 0.1, 0.3)  # Max 30% penalty
            agent_scores[agent] = max(0.0, agent_scores[agent] - workload_penalty)
        
        # Sort by score and return top results
        sorted_helpers = sorted(
            agent_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_helpers[:max_results]
    
    def accept_request(
        self,
        request_id: str,
        helper: str
    ) -> bool:
        """
        Accept a collaboration request.
        
        Args:
            request_id: Request to accept
            helper: Agent accepting the request
            
        Returns:
            True if accepted successfully
        """
        if request_id not in self.data['active_requests']:
            return False
        
        request = self.data['active_requests'][request_id]
        
        # Check if request is still pending
        if request.status != CollaborationStatus.PENDING:
            return False
        
        # If request specified a helper, verify it matches
        if request.helper and request.helper != helper:
            return False
        
        request.helper = helper
        request.status = CollaborationStatus.ACCEPTED
        request.accepted_at = datetime.utcnow().isoformat()
        request.updated_at = datetime.utcnow().isoformat()
        
        self._save_data()
        return True
    
    def start_collaboration(self, request_id: str) -> bool:
        """
        Mark a collaboration as started.
        
        Args:
            request_id: Request to start
            
        Returns:
            True if started successfully
        """
        if request_id not in self.data['active_requests']:
            return False
        
        request = self.data['active_requests'][request_id]
        
        if request.status != CollaborationStatus.ACCEPTED:
            return False
        
        request.status = CollaborationStatus.IN_PROGRESS
        request.updated_at = datetime.utcnow().isoformat()
        
        self._save_data()
        return True
    
    def complete_collaboration(
        self,
        request_id: str,
        outcome: CollaborationOutcome
    ) -> bool:
        """
        Complete a collaboration and record the outcome.
        
        Args:
            request_id: Request to complete
            outcome: Outcome of the collaboration
            
        Returns:
            True if completed successfully
        """
        if request_id not in self.data['active_requests']:
            return False
        
        request = self.data['active_requests'][request_id]
        
        request.status = CollaborationStatus.COMPLETED
        request.completed_at = datetime.utcnow().isoformat()
        request.updated_at = datetime.utcnow().isoformat()
        
        # Record outcome
        self.data['outcomes'][request_id] = outcome
        
        # Move to completed requests
        self.data['completed_requests'][request_id] = request
        del self.data['active_requests'][request_id]
        
        # Update collaboration graph
        requester = request.requester
        helper = request.helper
        
        if requester not in self.data['collaboration_graph']:
            self.data['collaboration_graph'][requester] = []
        if helper not in self.data['collaboration_graph'][requester]:
            self.data['collaboration_graph'][requester].append(helper)
        
        if helper not in self.data['collaboration_graph']:
            self.data['collaboration_graph'][helper] = []
        if requester not in self.data['collaboration_graph'][helper]:
            self.data['collaboration_graph'][helper].append(requester)
        
        # Update statistics
        self.data['statistics']['total_completed'] += 1
        if outcome.success:
            self.data['statistics']['total_successful'] += 1
        
        # Update average duration
        total = self.data['statistics']['total_completed']
        old_avg = self.data['statistics']['average_duration']
        new_avg = (old_avg * (total - 1) + outcome.duration_hours) / total
        self.data['statistics']['average_duration'] = new_avg
        
        # Update average value rating
        old_rating_avg = self.data['statistics']['average_value_rating']
        new_rating_avg = (old_rating_avg * (total - 1) + outcome.value_rating) / total
        self.data['statistics']['average_value_rating'] = new_rating_avg
        
        self._save_data()
        return True
    
    def decline_request(self, request_id: str, helper: str) -> bool:
        """
        Decline a collaboration request.
        
        Args:
            request_id: Request to decline
            helper: Agent declining
            
        Returns:
            True if declined successfully
        """
        if request_id not in self.data['active_requests']:
            return False
        
        request = self.data['active_requests'][request_id]
        
        if request.helper and request.helper != helper:
            return False
        
        request.status = CollaborationStatus.DECLINED
        request.updated_at = datetime.utcnow().isoformat()
        
        # If this was a directed request, move to completed
        if request.helper:
            self.data['completed_requests'][request_id] = request
            del self.data['active_requests'][request_id]
        else:
            # Open request stays active for others to accept
            request.helper = None
        
        self._save_data()
        return True
    
    def abandon_request(self, request_id: str, requester: str) -> bool:
        """
        Abandon a collaboration request.
        
        Args:
            request_id: Request to abandon
            requester: Agent abandoning (must be the requester)
            
        Returns:
            True if abandoned successfully
        """
        if request_id not in self.data['active_requests']:
            return False
        
        request = self.data['active_requests'][request_id]
        
        if request.requester != requester:
            return False
        
        request.status = CollaborationStatus.ABANDONED
        request.updated_at = datetime.utcnow().isoformat()
        
        self.data['completed_requests'][request_id] = request
        del self.data['active_requests'][request_id]
        
        self._save_data()
        return True
    
    def get_active_requests(
        self,
        agent: Optional[str] = None,
        collaboration_type: Optional[CollaborationType] = None,
        learning_category: Optional[str] = None
    ) -> List[CollaborationRequest]:
        """
        Get active collaboration requests.
        
        Args:
            agent: Filter by requester or helper
            collaboration_type: Filter by type
            learning_category: Filter by category
            
        Returns:
            List of matching active requests
        """
        requests = list(self.data['active_requests'].values())
        
        if agent:
            requests = [
                r for r in requests
                if r.requester == agent or r.helper == agent
            ]
        
        if collaboration_type:
            requests = [
                r for r in requests
                if r.collaboration_type == collaboration_type
            ]
        
        if learning_category:
            requests = [
                r for r in requests
                if r.learning_category == learning_category
            ]
        
        return requests
    
    def get_collaboration_history(
        self,
        agent: str,
        limit: Optional[int] = None
    ) -> List[Tuple[CollaborationRequest, Optional[CollaborationOutcome]]]:
        """
        Get collaboration history for an agent.
        
        Args:
            agent: Agent to get history for
            limit: Maximum number of records to return
            
        Returns:
            List of (request, outcome) tuples
        """
        history = []
        
        for request_id, request in self.data['completed_requests'].items():
            if request.requester == agent or request.helper == agent:
                outcome = self.data['outcomes'].get(request_id)
                history.append((request, outcome))
        
        # Sort by completion time, most recent first
        history.sort(
            key=lambda x: x[0].completed_at or x[0].updated_at,
            reverse=True
        )
        
        if limit:
            history = history[:limit]
        
        return history
    
    def get_collaboration_partners(self, agent: str) -> List[str]:
        """
        Get all agents this agent has collaborated with.
        
        Args:
            agent: Agent to get partners for
            
        Returns:
            List of agent names
        """
        return self.data['collaboration_graph'].get(agent, [])
    
    def get_statistics(self) -> Dict:
        """
        Get collaboration statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = self.data['statistics'].copy()
        
        # Add success rate
        total = stats['total_completed']
        if total > 0:
            stats['success_rate'] = stats['total_successful'] / total
        else:
            stats['success_rate'] = 0.0
        
        # Add active requests count
        stats['active_requests'] = len(self.data['active_requests'])
        
        return stats
    
    def _get_collaboration_success_rate(self, agent: str) -> float:
        """
        Get collaboration success rate for an agent.
        
        Args:
            agent: Agent to check
            
        Returns:
            Success rate (0.0 - 1.0)
        """
        total = 0
        successful = 0
        
        for request_id, request in self.data['completed_requests'].items():
            if request.helper != agent:
                continue
            
            total += 1
            outcome = self.data['outcomes'].get(request_id)
            if outcome and outcome.success:
                successful += 1
        
        if total == 0:
            return 0.5  # Neutral score for no history
        
        return successful / total
    
    def _get_agent_workload(self, agent: str) -> int:
        """
        Get current workload for an agent.
        
        Args:
            agent: Agent to check
            
        Returns:
            Number of active collaborations
        """
        count = 0
        
        for request in self.data['active_requests'].values():
            if request.helper == agent:
                count += 1
        
        return count
    
    def suggest_collaborations(
        self,
        agent: str,
        limit: int = 5
    ) -> List[Tuple[str, str, float]]:
        """
        Suggest potential collaboration opportunities for an agent.
        
        Based on:
        - Agent's investment areas (from investment tracker)
        - Open requests matching their expertise
        - Agents who might benefit from their help
        
        Args:
            agent: Agent to suggest collaborations for
            limit: Maximum suggestions to return
            
        Returns:
            List of (agent_needing_help, topic, relevance_score) tuples
        """
        suggestions = []
        
        # Check open requests that match agent's expertise
        for request in self.data['active_requests'].values():
            if request.status != CollaborationStatus.PENDING:
                continue
            
            if request.helper and request.helper != agent:
                continue
            
            # Skip if already the requester
            if request.requester == agent:
                continue
            
            # Calculate relevance score
            score = 0.5
            
            # Check if agent has expertise in the learning category
            if request.learning_category and self.investment_tracker:
                try:
                    investment = self.investment_tracker.get_investment(
                        agent,
                        request.learning_category
                    )
                    if investment:
                        score = investment.score / 100.0
                except Exception:
                    pass
            
            # Boost by priority
            score = score * 0.7 + request.priority * 0.3
            
            suggestions.append((
                request.requester,
                request.topic,
                score
            ))
        
        # Sort by score and return top results
        suggestions.sort(key=lambda x: x[2], reverse=True)
        return suggestions[:limit]
    
    def integrate_investment_tracker(self, tracker):
        """
        Integrate with the investment tracker.
        
        Args:
            tracker: AgentInvestmentTracker instance
        """
        self.investment_tracker = tracker
    
    def integrate_learning_matcher(self, matcher):
        """
        Integrate with the learning matcher.
        
        Args:
            matcher: AgentLearningMatcher instance
        """
        self.learning_matcher = matcher
