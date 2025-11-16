#!/usr/bin/env python3
"""
Agent Learning Matcher - Match agents to relevant learnings

This module provides intelligent matching between custom agents and learning content
based on specializations, categories, keywords, and semantic similarity.

Created by: @investigate-champion
Date: 2025-11-15
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict


class AgentLearningMatcher:
    """
    Matches agents to relevant learning content based on their specializations.
    
    This matcher uses a multi-factor scoring system that considers:
    - Category alignment (primary and secondary)
    - Keyword matching
    - Agent learning affinity
    - Content recency
    - Source preferences
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the matcher with configuration.
        
        Args:
            config_path: Path to the configuration JSON file.
                        If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "agent_learning_matching_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.categories = self.config['learning_categories']
        self.agents = self.config['agent_specializations']
        self.weights = self.config['scoring_weights']
        self.thresholds = self.config['matching_thresholds']
        
        # Build reverse index for faster lookup
        self._build_keyword_index()
    
    def _build_keyword_index(self):
        """Build keyword index for categories."""
        self.category_keywords = {}
        for category, info in self.categories.items():
            self.category_keywords[category] = set(
                kw.lower() for kw in info['keywords']
            )
    
    def _extract_keywords_from_text(self, text: str) -> Set[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            Set of lowercase keywords
        """
        if not text:
            return set()
        
        # Convert to lowercase and split on word boundaries
        words = re.findall(r'\b\w+\b', text.lower())
        return set(words)
    
    def _categorize_learning(self, learning: Dict) -> List[Tuple[str, float]]:
        """
        Categorize a learning item based on content.
        
        Args:
            learning: Learning dictionary with title, description, etc.
            
        Returns:
            List of (category, score) tuples, sorted by score descending
        """
        # Extract text for analysis (handle both description and content fields)
        text_fields = [
            learning.get('title', ''),
            learning.get('description', ''),
            learning.get('content', '')[:1000],  # First 1000 chars of content
        ]
        full_text = ' '.join(text_fields).lower()
        learning_keywords = self._extract_keywords_from_text(full_text)
        
        # Score each category
        category_scores = {}
        for category, info in self.categories.items():
            score = 0.0
            cat_keywords = self.category_keywords[category]
            
            # Count keyword matches
            matches = learning_keywords.intersection(cat_keywords)
            if matches:
                # Weight by keyword importance (normalize by category keyword count)
                score = len(matches) / max(len(cat_keywords), 1)
                score *= info.get('priority_weight', 1.0)
            
            category_scores[category] = score
        
        # Sort by score
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return categories with non-zero scores
        return [(cat, score) for cat, score in sorted_categories if score > 0]
    
    def _score_match(
        self,
        agent_name: str,
        learning: Dict,
        learning_categories: List[Tuple[str, float]],
        recency_factor: float = 1.0
    ) -> float:
        """
        Score how well a learning matches an agent.
        
        Args:
            agent_name: Name of the agent
            learning: Learning dictionary
            learning_categories: Pre-categorized learning categories with scores
            recency_factor: Multiplier based on learning age (1.0 = current)
            
        Returns:
            Match score between 0.0 and 1.0
        """
        agent_info = self.agents.get(agent_name)
        if not agent_info:
            return 0.0
        
        score = 0.0
        
        # 1. Category matching
        learning_cats = {cat: cat_score for cat, cat_score in learning_categories}
        
        for primary_cat in agent_info.get('primary_categories', []):
            if primary_cat in learning_cats:
                score += (
                    self.weights['category_match_primary'] 
                    * learning_cats[primary_cat]
                )
        
        for secondary_cat in agent_info.get('secondary_categories', []):
            if secondary_cat in learning_cats:
                score += (
                    self.weights['category_match_secondary'] 
                    * learning_cats[secondary_cat]
                )
        
        # 2. Keyword matching
        learning_text = ' '.join([
            learning.get('title', ''),
            learning.get('description', ''),
            learning.get('content', '')[:500],  # Include content field
        ]).lower()
        
        agent_keywords = set(kw.lower() for kw in agent_info.get('keywords', []))
        learning_words = self._extract_keywords_from_text(learning_text)
        
        keyword_matches = agent_keywords.intersection(learning_words)
        if keyword_matches:
            keyword_score = len(keyword_matches) / max(len(agent_keywords), 1)
            score += self.weights['keyword_match'] * keyword_score
        
        # 3. Agent learning affinity
        affinity = agent_info.get('learning_affinity_score', 0.8)
        score += self.weights['learning_affinity'] * affinity
        
        # 4. Recency boost
        score += self.weights['recency_boost'] * recency_factor
        
        # 5. Source preference
        source = learning.get('source', '').lower()
        if source:
            source_key = 'hn' if 'hacker' in source else (source.split()[0].lower() if source.split() else 'other')
        else:
            source_key = 'other'
        source_multiplier = self.weights['source_preference'].get(
            source_key, 
            1.0
        )
        score *= source_multiplier
        
        # Normalize to 0-1 range (approximate)
        # Max theoretical score with all bonuses ~= 2.5-3.0
        normalized_score = min(score / 2.5, 1.0)
        
        return normalized_score
    
    def match_agent_to_learnings(
        self,
        agent_name: str,
        learnings: List[Dict],
        max_results: int = 10,
        min_score: Optional[float] = None
    ) -> List[Dict]:
        """
        Find the most relevant learnings for an agent.
        
        Args:
            agent_name: Name of the agent
            learnings: List of learning dictionaries
            max_results: Maximum number of results to return
            min_score: Minimum relevance score (None = use config threshold)
            
        Returns:
            List of learning dictionaries with added 'relevance_score' field,
            sorted by relevance descending
        """
        if min_score is None:
            min_score = self.thresholds['minimum_score']
        
        scored_learnings = []
        
        for learning in learnings:
            # Categorize learning
            categories = self._categorize_learning(learning)
            
            # Calculate recency factor (if timestamp available)
            recency = 1.0
            if 'timestamp' in learning or 'date' in learning:
                try:
                    timestamp_str = learning.get('timestamp') or learning.get('date')
                    learning_date = datetime.fromisoformat(
                        timestamp_str.replace('Z', '+00:00')
                    )
                    age_days = (datetime.now().astimezone() - learning_date).days
                    # Decay: 1.0 at day 0, 0.5 at day 7, 0.25 at day 14
                    recency = max(0.1, 1.0 / (1 + age_days / 7))
                except (ValueError, TypeError):
                    pass
            
            # Score the match
            score = self._score_match(agent_name, learning, categories, recency)
            
            if score >= min_score:
                learning_with_score = learning.copy()
                learning_with_score['relevance_score'] = score
                learning_with_score['matched_categories'] = [
                    cat for cat, _ in categories[:3]  # Top 3 categories
                ]
                scored_learnings.append(learning_with_score)
        
        # Sort by score descending
        scored_learnings.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scored_learnings[:max_results]
    
    def match_learning_to_agents(
        self,
        learning: Dict,
        agent_names: Optional[List[str]] = None,
        max_results: int = 5,
        min_score: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """
        Find the most suitable agents for a learning item.
        
        Args:
            learning: Learning dictionary
            agent_names: List of agent names to consider (None = all agents)
            max_results: Maximum number of results to return
            min_score: Minimum relevance score (None = use config threshold)
            
        Returns:
            List of (agent_name, score) tuples, sorted by score descending
        """
        if min_score is None:
            min_score = self.thresholds['minimum_score']
        
        if agent_names is None:
            agent_names = list(self.agents.keys())
        
        # Categorize learning once
        categories = self._categorize_learning(learning)
        
        # Calculate recency
        recency = 1.0
        if 'timestamp' in learning or 'date' in learning:
            try:
                timestamp_str = learning.get('timestamp') or learning.get('date')
                learning_date = datetime.fromisoformat(
                    timestamp_str.replace('Z', '+00:00')
                )
                age_days = (datetime.now().astimezone() - learning_date).days
                recency = max(0.1, 1.0 / (1 + age_days / 7))
            except (ValueError, TypeError):
                pass
        
        # Score each agent
        agent_scores = []
        for agent_name in agent_names:
            score = self._score_match(agent_name, learning, categories, recency)
            if score >= min_score:
                agent_scores.append((agent_name, score))
        
        # Sort by score descending
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        return agent_scores[:max_results]
    
    def get_agent_learning_summary(
        self,
        agent_name: str,
        learnings: List[Dict]
    ) -> Dict:
        """
        Get a summary of learning matches for an agent.
        
        Args:
            agent_name: Name of the agent
            learnings: List of all available learnings
            
        Returns:
            Dictionary with summary statistics
        """
        matches = self.match_agent_to_learnings(
            agent_name,
            learnings,
            max_results=100,  # Get many for stats
            min_score=0.0  # Include all for analysis
        )
        
        if not matches:
            return {
                'agent_name': agent_name,
                'total_relevant': 0,
                'high_relevance': 0,
                'perfect_matches': 0,
                'top_categories': [],
                'top_sources': [],
                'average_score': 0.0
            }
        
        # Calculate statistics
        high_relevance = sum(
            1 for m in matches 
            if m['relevance_score'] >= self.thresholds['high_relevance']
        )
        perfect_matches = sum(
            1 for m in matches 
            if m['relevance_score'] >= self.thresholds['perfect_match']
        )
        
        # Top categories
        category_counts = defaultdict(int)
        for match in matches[:20]:  # Top 20 matches
            for cat in match.get('matched_categories', []):
                category_counts[cat] += 1
        top_categories = sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Top sources
        source_counts = defaultdict(int)
        for match in matches[:20]:
            source = match.get('source', 'Unknown')
            source_counts[source] += 1
        top_sources = sorted(
            source_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            'agent_name': agent_name,
            'total_relevant': len(matches),
            'high_relevance': high_relevance,
            'perfect_matches': perfect_matches,
            'top_categories': [cat for cat, _ in top_categories],
            'top_sources': [src for src, _ in top_sources],
            'average_score': sum(m['relevance_score'] for m in matches) / len(matches)
        }
    
    def suggest_learning_distribution(
        self,
        learnings: List[Dict],
        max_agents_per_learning: int = 3
    ) -> Dict[str, List[str]]:
        """
        Suggest optimal distribution of learnings to agents.
        
        Args:
            learnings: List of learning dictionaries
            max_agents_per_learning: Max agents to assign per learning
            
        Returns:
            Dictionary mapping agent_name -> list of learning IDs/indices
        """
        distribution = defaultdict(list)
        
        for idx, learning in enumerate(learnings):
            # Find best matching agents
            best_agents = self.match_learning_to_agents(
                learning,
                max_results=max_agents_per_learning,
                min_score=self.thresholds['high_relevance']
            )
            
            # Distribute to top agents
            for agent_name, score in best_agents:
                learning_id = learning.get('id', idx)
                distribution[agent_name].append({
                    'learning_id': learning_id,
                    'title': learning.get('title', 'Untitled'),
                    'score': score,
                    'url': learning.get('url', '')
                })
        
        return dict(distribution)
    
    def assign_learnings_to_agents_diverse(
        self,
        learnings: List[Dict],
        agent_names: Optional[List[str]] = None,
        max_assignments: int = 5,
        min_score: Optional[float] = None,
        diversity_weight: float = 0.5
    ) -> List[Dict]:
        """
        Assign learnings to agents with diversity constraints.
        
        This method ensures that:
        1. Each learning is assigned to at most one agent
        2. Agents are distributed evenly across assignments
        3. The best matches are still prioritized
        
        Args:
            learnings: List of learning dictionaries
            agent_names: List of agent names to consider (None = all agents)
            max_assignments: Maximum number of assignments to create
            min_score: Minimum match score (None = use config threshold)
            diversity_weight: Weight for diversity penalty (0-1, higher = more diverse)
            
        Returns:
            List of assignment dictionaries with keys:
                - agent_id: agent name
                - learning: learning dict with relevance_score
                - score: match score
                - categories: matched categories
        """
        if min_score is None:
            min_score = self.thresholds['minimum_score']
        
        if agent_names is None:
            agent_names = list(self.agents.keys())
        
        # Track which agents have been assigned
        agent_assignment_count = defaultdict(int)
        
        # Track which learnings have been assigned
        assigned_learning_ids = set()
        
        assignments = []
        
        # For each learning, find best available agent
        for learning in learnings:
            if len(assignments) >= max_assignments:
                break
            
            # Skip if already assigned
            learning_id = id(learning)  # Use object id as unique identifier
            if learning_id in assigned_learning_ids:
                continue
            
            # Get all potential agent matches
            agent_scores = self.match_learning_to_agents(
                learning,
                agent_names=agent_names,
                max_results=len(agent_names),
                min_score=min_score
            )
            
            if not agent_scores:
                continue
            
            # Apply diversity penalty based on how many times agent has been assigned
            adjusted_scores = []
            for agent_name, base_score in agent_scores:
                # Penalty increases with each assignment to this agent
                penalty = agent_assignment_count[agent_name] * diversity_weight
                adjusted_score = base_score * (1.0 - min(penalty, 0.9))  # Cap penalty at 90%
                adjusted_scores.append((agent_name, adjusted_score, base_score))
            
            # Sort by adjusted score
            adjusted_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Take the best agent (after diversity adjustment)
            best_agent, adjusted_score, original_score = adjusted_scores[0]
            
            # Get categorization for the learning
            categories = self._categorize_learning(learning)
            category_names = [cat for cat, _ in categories[:3]]
            
            # Create assignment
            learning_with_score = learning.copy()
            learning_with_score['relevance_score'] = original_score
            learning_with_score['matched_categories'] = category_names
            
            assignments.append({
                'agent_id': best_agent,
                'agent_name': self.agents[best_agent].get('focus_areas', [best_agent])[0],
                'learning': learning_with_score,
                'score': original_score,
                'categories': category_names,
                'adjusted_score': adjusted_score,
                'assignment_rank': agent_assignment_count[best_agent] + 1
            })
            
            # Update tracking
            agent_assignment_count[best_agent] += 1
            assigned_learning_ids.add(learning_id)
        
        return assignments


# Convenience functions

def load_learnings_from_file(filepath: str) -> List[Dict]:
    """
    Load learnings from a JSON file.
    
    Args:
        filepath: Path to JSON file containing learnings
        
    Returns:
        List of learning dictionaries
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Handle different file formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Check for common keys
        if 'learnings' in data:
            return data['learnings']
        elif 'items' in data:
            return data['items']
        elif 'stories' in data:
            return data['stories']
    
    return []


def load_all_learnings(learnings_dir: str = None) -> List[Dict]:
    """
    Load all learnings from the learnings directory.
    
    Args:
        learnings_dir: Path to learnings directory (None = auto-detect)
        
    Returns:
        List of all learning dictionaries from all JSON files
    """
    if learnings_dir is None:
        # Try to find learnings directory
        current_dir = Path(__file__).parent.parent
        learnings_dir = current_dir / "learnings"
    else:
        learnings_dir = Path(learnings_dir)
    
    all_learnings = []
    
    # Load from JSON files
    for json_file in learnings_dir.glob("*.json"):
        try:
            learnings = load_learnings_from_file(str(json_file))
            # Add source metadata
            for learning in learnings:
                if 'source_file' not in learning:
                    learning['source_file'] = json_file.name
            all_learnings.extend(learnings)
        except Exception as e:
            print(f"Warning: Could not load {json_file}: {e}")
    
    return all_learnings


# Example usage
if __name__ == '__main__':
    import sys
    
    print("🔍 Agent Learning Matcher - @investigate-champion")
    print("=" * 60)
    
    # Initialize matcher
    matcher = AgentLearningMatcher()
    print(f"✅ Loaded config with {len(matcher.agents)} agents")
    print(f"✅ Loaded {len(matcher.categories)} learning categories")
    print()
    
    # Example 1: Match specific agent to learnings
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
        print(f"🤖 Finding learnings for agent: {agent_name}")
        print()
        
        # Load learnings
        learnings = load_all_learnings()
        print(f"📚 Loaded {len(learnings)} total learnings")
        print()
        
        # Get matches
        matches = matcher.match_agent_to_learnings(agent_name, learnings, max_results=10)
        
        print(f"🎯 Top {len(matches)} matches for @{agent_name}:")
        print()
        
        for i, match in enumerate(matches, 1):
            score = match['relevance_score']
            title = match.get('title', 'Untitled')
            categories = ', '.join(match.get('matched_categories', []))
            
            # Score indicator
            if score >= matcher.thresholds['perfect_match']:
                indicator = "🌟"
            elif score >= matcher.thresholds['high_relevance']:
                indicator = "⭐"
            else:
                indicator = "•"
            
            print(f"{indicator} {i}. [{score:.2f}] {title}")
            print(f"   Categories: {categories}")
            print(f"   Source: {match.get('source', 'Unknown')}")
            if 'url' in match:
                print(f"   URL: {match['url']}")
            print()
        
        # Summary
        summary = matcher.get_agent_learning_summary(agent_name, learnings)
        print("📊 Summary:")
        print(f"   Total relevant: {summary['total_relevant']}")
        print(f"   High relevance: {summary['high_relevance']}")
        print(f"   Perfect matches: {summary['perfect_matches']}")
        print(f"   Average score: {summary['average_score']:.2f}")
        print(f"   Top categories: {', '.join(summary['top_categories'][:3])}")
        print(f"   Top sources: {', '.join(summary['top_sources'])}")
    
    else:
        print("Usage: python agent_learning_matcher.py <agent-name>")
        print()
        print("Available agents:")
        for agent in sorted(matcher.agents.keys()):
            focus = ', '.join(matcher.agents[agent]['focus_areas'][:2])
            print(f"  • {agent} - {focus}")
