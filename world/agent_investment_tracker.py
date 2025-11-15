#!/usr/bin/env python3
"""
Agent Investment Tracker - Track and cultivate agent expertise in learning categories

This module manages agent investments in learning categories, tracking cultivation
events and identifying opportunities for specialization growth.

Created by: @organize-guru
Date: 2025-11-15
Version: 1.0

Philosophy:
    "Clean code is simple and direct. Clean code reads like well-written prose."
    - Robert C. Martin
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum


class InvestmentLevel(Enum):
    """Investment levels representing agent expertise depth."""
    NONE = 0
    CURIOUS = 1      # Initial interest
    LEARNING = 2     # Active learning
    PRACTICING = 3   # Regular practice
    PROFICIENT = 4   # Demonstrated competence
    EXPERT = 5       # Deep expertise


@dataclass
class CultivationEvent:
    """
    Single cultivation event when an agent works on a learning category.
    
    Attributes:
        timestamp: When the cultivation occurred
        category: Learning category cultivated
        learning_id: Optional ID of the specific learning item
        impact: Strength of cultivation (0.0 - 1.0)
        context: Additional context about the event
    """
    timestamp: str
    category: str
    learning_id: Optional[str] = None
    impact: float = 0.5
    context: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CultivationEvent':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CategoryInvestment:
    """
    Tracks agent investment in a specific learning category.
    
    Attributes:
        category: Learning category name
        level: Current investment level
        score: Numerical investment score (0.0 - 100.0)
        first_invested: When investment started
        last_cultivated: Most recent cultivation
        cultivation_count: Number of cultivation events
        cultivation_events: List of recent cultivation events
    """
    category: str
    level: InvestmentLevel = InvestmentLevel.NONE
    score: float = 0.0
    first_invested: Optional[str] = None
    last_cultivated: Optional[str] = None
    cultivation_count: int = 0
    cultivation_events: List[CultivationEvent] = None
    
    def __post_init__(self):
        """Initialize cultivation events list."""
        if self.cultivation_events is None:
            self.cultivation_events = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'category': self.category,
            'level': self.level.name,
            'score': self.score,
            'first_invested': self.first_invested,
            'last_cultivated': self.last_cultivated,
            'cultivation_count': self.cultivation_count,
            'cultivation_events': [e.to_dict() for e in self.cultivation_events]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CategoryInvestment':
        """Create from dictionary."""
        data = data.copy()
        data['level'] = InvestmentLevel[data['level']]
        events = data.get('cultivation_events', [])
        data['cultivation_events'] = [
            CultivationEvent.from_dict(e) for e in events
        ]
        return cls(**data)


class AgentInvestmentTracker:
    """
    Manages agent investments in learning categories.
    
    This tracker records cultivation events, calculates investment scores,
    and identifies opportunities for further specialization.
    
    Investment Model:
        - Investment grows through cultivation events
        - Decay occurs if not cultivated regularly
        - Higher impact events contribute more to score
        - Investment levels progress from Curious to Expert
    """
    
    # Configuration constants
    DECAY_DAYS = 30              # Days before decay starts
    DECAY_RATE = 0.02            # Daily decay rate (2%)
    MAX_EVENTS_STORED = 50       # Recent events to keep
    SCORE_THRESHOLDS = {         # Level transition thresholds
        InvestmentLevel.CURIOUS: 5.0,
        InvestmentLevel.LEARNING: 15.0,
        InvestmentLevel.PRACTICING: 35.0,
        InvestmentLevel.PROFICIENT: 60.0,
        InvestmentLevel.EXPERT: 85.0,
    }
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the investment tracker.
        
        Args:
            data_path: Path to the investment data JSON file.
                      If None, uses default location.
        """
        if data_path is None:
            data_path = Path(__file__).parent / "agent_investments.json"
        
        self.data_path = Path(data_path)
        self.investments = self._load_investments()
    
    def _load_investments(self) -> Dict[str, Dict[str, CategoryInvestment]]:
        """
        Load investment data from JSON file.
        
        Returns:
            Dictionary mapping agent_name -> category -> CategoryInvestment
        """
        if not self.data_path.exists():
            return {}
        
        # Check if file is empty
        if self.data_path.stat().st_size == 0:
            return {}
        
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        # Reconstruct investment objects
        investments = {}
        for agent, categories in data.get('investments', {}).items():
            investments[agent] = {}
            for category, inv_data in categories.items():
                investments[agent][category] = CategoryInvestment.from_dict(inv_data)
        
        return investments
    
    def _save_investments(self):
        """Save investment data to JSON file."""
        data = {
            'last_updated': datetime.now().isoformat(),
            'version': '1.0',
            'investments': {}
        }
        
        # Convert to serializable format
        for agent, categories in self.investments.items():
            data['investments'][agent] = {}
            for category, investment in categories.items():
                data['investments'][agent][category] = investment.to_dict()
        
        # Ensure directory exists
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write with pretty formatting
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_cultivation(
        self,
        agent_name: str,
        category: str,
        impact: float = 0.5,
        learning_id: Optional[str] = None,
        context: str = ""
    ) -> CategoryInvestment:
        """
        Record a cultivation event when an agent works on a learning category.
        
        Args:
            agent_name: Name of the agent
            category: Learning category being cultivated
            impact: Strength of cultivation (0.0 - 1.0), default 0.5
            learning_id: Optional ID of the specific learning item
            context: Additional context about the event
        
        Returns:
            Updated CategoryInvestment object
        """
        # Validate impact
        impact = max(0.0, min(1.0, impact))
        
        # Initialize agent investments if needed
        if agent_name not in self.investments:
            self.investments[agent_name] = {}
        
        # Initialize category investment if needed
        if category not in self.investments[agent_name]:
            self.investments[agent_name][category] = CategoryInvestment(
                category=category,
                first_invested=datetime.now().isoformat()
            )
        
        investment = self.investments[agent_name][category]
        
        # Create cultivation event
        event = CultivationEvent(
            timestamp=datetime.now().isoformat(),
            category=category,
            learning_id=learning_id,
            impact=impact,
            context=context
        )
        
        # Add event to history (keep only recent events)
        investment.cultivation_events.append(event)
        if len(investment.cultivation_events) > self.MAX_EVENTS_STORED:
            investment.cultivation_events = investment.cultivation_events[-self.MAX_EVENTS_STORED:]
        
        # Update investment metrics
        investment.last_cultivated = event.timestamp
        investment.cultivation_count += 1
        
        # Recalculate score
        investment.score = self._calculate_score(investment)
        
        # Update investment level
        investment.level = self._determine_level(investment.score)
        
        # Save changes
        self._save_investments()
        
        return investment
    
    def _calculate_score(self, investment: CategoryInvestment) -> float:
        """
        Calculate investment score based on cultivation history.
        
        Score calculation considers:
        - Number of cultivation events
        - Impact of each event
        - Recency of events
        - Time decay
        
        Args:
            investment: CategoryInvestment to calculate score for
        
        Returns:
            Investment score (0.0 - 100.0)
        """
        if not investment.cultivation_events:
            return 0.0
        
        score = 0.0
        now = datetime.now()
        
        for event in investment.cultivation_events:
            # Parse event timestamp
            event_time = datetime.fromisoformat(event.timestamp)
            days_ago = (now - event_time).days
            
            # Base contribution from impact
            contribution = event.impact * 10.0  # Scale to 0-10 range
            
            # Apply time decay
            if days_ago > self.DECAY_DAYS:
                decay_days = days_ago - self.DECAY_DAYS
                decay_factor = (1.0 - self.DECAY_RATE) ** decay_days
                contribution *= decay_factor
            else:
                # Recency boost for recent events
                recency_boost = 1.0 + (0.2 * (1.0 - days_ago / self.DECAY_DAYS))
                contribution *= recency_boost
            
            score += contribution
        
        # Cap at 100
        return min(100.0, score)
    
    def _determine_level(self, score: float) -> InvestmentLevel:
        """
        Determine investment level based on score.
        
        Args:
            score: Investment score
        
        Returns:
            Appropriate InvestmentLevel
        """
        if score >= self.SCORE_THRESHOLDS[InvestmentLevel.EXPERT]:
            return InvestmentLevel.EXPERT
        elif score >= self.SCORE_THRESHOLDS[InvestmentLevel.PROFICIENT]:
            return InvestmentLevel.PROFICIENT
        elif score >= self.SCORE_THRESHOLDS[InvestmentLevel.PRACTICING]:
            return InvestmentLevel.PRACTICING
        elif score >= self.SCORE_THRESHOLDS[InvestmentLevel.LEARNING]:
            return InvestmentLevel.LEARNING
        elif score >= self.SCORE_THRESHOLDS[InvestmentLevel.CURIOUS]:
            return InvestmentLevel.CURIOUS
        else:
            return InvestmentLevel.NONE
    
    def get_agent_investments(
        self,
        agent_name: str,
        min_level: Optional[InvestmentLevel] = None
    ) -> Dict[str, CategoryInvestment]:
        """
        Get all investments for an agent.
        
        Args:
            agent_name: Name of the agent
            min_level: Optional minimum investment level filter
        
        Returns:
            Dictionary mapping category to CategoryInvestment
        """
        if agent_name not in self.investments:
            return {}
        
        investments = self.investments[agent_name]
        
        if min_level is None:
            return investments
        
        # Filter by minimum level
        return {
            cat: inv for cat, inv in investments.items()
            if inv.level.value >= min_level.value
        }
    
    def get_category_experts(
        self,
        category: str,
        min_level: InvestmentLevel = InvestmentLevel.PROFICIENT
    ) -> List[Tuple[str, CategoryInvestment]]:
        """
        Get all agents invested in a category.
        
        Args:
            category: Learning category
            min_level: Minimum investment level (default: PROFICIENT)
        
        Returns:
            List of (agent_name, CategoryInvestment) tuples,
            sorted by investment score descending
        """
        experts = []
        
        for agent, categories in self.investments.items():
            if category in categories:
                investment = categories[category]
                if investment.level.value >= min_level.value:
                    experts.append((agent, investment))
        
        # Sort by score descending
        experts.sort(key=lambda x: x[1].score, reverse=True)
        
        return experts
    
    def find_cultivation_opportunities(
        self,
        agent_name: str,
        available_learnings: List[Dict],
        top_n: int = 10
    ) -> List[Dict]:
        """
        Identify cultivation opportunities for an agent.
        
        Prioritizes:
        1. Categories where agent has existing investment
        2. Categories related to agent's expertise
        3. Fresh, high-impact learning opportunities
        
        Args:
            agent_name: Name of the agent
            available_learnings: List of available learning items
            top_n: Number of top opportunities to return
        
        Returns:
            List of learning opportunities with cultivation potential
        """
        if agent_name not in self.investments:
            return available_learnings[:top_n]
        
        agent_investments = self.investments[agent_name]
        opportunities = []
        
        for learning in available_learnings:
            # Get learning categories
            categories = learning.get('categories', [])
            
            # Calculate opportunity score
            opp_score = 0.0
            invested_categories = []
            
            for category in categories:
                if category in agent_investments:
                    investment = agent_investments[category]
                    
                    # Higher score for categories already invested in
                    investment_bonus = investment.score * 0.01
                    opp_score += investment_bonus
                    
                    # Bonus for categories needing cultivation (not cultivated recently)
                    if investment.last_cultivated:
                        last_cultivated = datetime.fromisoformat(investment.last_cultivated)
                        days_since = (datetime.now() - last_cultivated).days
                        if days_since > 7:
                            opp_score += 0.5
                    
                    invested_categories.append(category)
            
            # Add base learning score if available
            base_score = learning.get('score', 0.0)
            opp_score += base_score
            
            opportunities.append({
                **learning,
                'cultivation_score': opp_score,
                'invested_categories': invested_categories
            })
        
        # Sort by cultivation score
        opportunities.sort(key=lambda x: x['cultivation_score'], reverse=True)
        
        return opportunities[:top_n]
    
    def get_investment_summary(self, agent_name: str) -> Dict:
        """
        Get a summary of an agent's investment portfolio.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Summary dictionary with statistics
        """
        if agent_name not in self.investments:
            return {
                'agent': agent_name,
                'total_investments': 0,
                'categories': [],
                'expertise_levels': {},
                'most_cultivated': None,
                'needs_cultivation': []
            }
        
        investments = self.investments[agent_name]
        
        # Count by level
        level_counts = defaultdict(int)
        for inv in investments.values():
            level_counts[inv.level.name] += 1
        
        # Find most cultivated
        most_cultivated = max(
            investments.items(),
            key=lambda x: x[1].cultivation_count,
            default=(None, None)
        )
        
        # Find categories needing cultivation
        now = datetime.now()
        needs_cultivation = []
        for category, inv in investments.items():
            if inv.last_cultivated:
                last = datetime.fromisoformat(inv.last_cultivated)
                days = (now - last).days
                if days > 14 and inv.level.value >= InvestmentLevel.LEARNING.value:
                    needs_cultivation.append({
                        'category': category,
                        'level': inv.level.name,
                        'days_since': days,
                        'score': inv.score
                    })
        
        needs_cultivation.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'agent': agent_name,
            'total_investments': len(investments),
            'categories': list(investments.keys()),
            'expertise_levels': dict(level_counts),
            'most_cultivated': {
                'category': most_cultivated[0],
                'count': most_cultivated[1].cultivation_count
            } if most_cultivated[0] else None,
            'needs_cultivation': needs_cultivation[:5]
        }
    
    def apply_decay(self) -> Dict[str, int]:
        """
        Apply time-based decay to all investments.
        
        Should be run periodically to maintain investment accuracy.
        
        Returns:
            Dictionary with decay statistics
        """
        stats = {
            'agents_processed': 0,
            'investments_decayed': 0,
            'investments_removed': 0
        }
        
        for agent_name, categories in list(self.investments.items()):
            stats['agents_processed'] += 1
            
            for category, investment in list(categories.items()):
                old_score = investment.score
                
                # Recalculate score (includes decay)
                new_score = self._calculate_score(investment)
                investment.score = new_score
                
                # Update level
                investment.level = self._determine_level(new_score)
                
                if old_score != new_score:
                    stats['investments_decayed'] += 1
                
                # Remove if score dropped to zero
                if new_score == 0.0:
                    del categories[category]
                    stats['investments_removed'] += 1
            
            # Remove agent if no investments remain
            if not categories:
                del self.investments[agent_name]
        
        self._save_investments()
        
        return stats


# Convenience functions for common operations

def record_learning_work(
    agent_name: str,
    categories: List[str],
    learning_id: Optional[str] = None,
    impact: float = 0.5,
    tracker: Optional[AgentInvestmentTracker] = None
) -> List[CategoryInvestment]:
    """
    Record that an agent worked on a learning item.
    
    Args:
        agent_name: Name of the agent
        categories: List of learning categories
        learning_id: Optional ID of the learning item
        impact: Cultivation impact (0.0 - 1.0)
        tracker: Optional tracker instance (creates new if None)
    
    Returns:
        List of updated CategoryInvestment objects
    """
    if tracker is None:
        tracker = AgentInvestmentTracker()
    
    results = []
    context = f"Learning work: {learning_id}" if learning_id else "Learning work"
    
    for category in categories:
        investment = tracker.record_cultivation(
            agent_name=agent_name,
            category=category,
            impact=impact,
            learning_id=learning_id,
            context=context
        )
        results.append(investment)
    
    return results


def get_top_agents_for_category(
    category: str,
    min_level: InvestmentLevel = InvestmentLevel.PROFICIENT,
    tracker: Optional[AgentInvestmentTracker] = None
) -> List[str]:
    """
    Get the top agents for a learning category.
    
    Args:
        category: Learning category
        min_level: Minimum investment level
        tracker: Optional tracker instance
    
    Returns:
        List of agent names sorted by expertise
    """
    if tracker is None:
        tracker = AgentInvestmentTracker()
    
    experts = tracker.get_category_experts(category, min_level)
    return [agent for agent, _ in experts]
