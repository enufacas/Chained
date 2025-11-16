#!/usr/bin/env python3
"""
Agent Memory System - Production Implementation
By @coach-master for AI/ML Innovation Mission (idea:27)

Provides persistent memory for Chained agents, enabling:
- Learning from past experiences
- Retrieval of similar issues/solutions
- Performance improvement over time
- Knowledge sharing across agent team

Usage:
    from agent_memory import AgentMemory
    
    memory = AgentMemory("coach-master")
    
    # Store experience after completing work
    memory.store_experience(
        issue={"number": 123, "title": "Add auth", "body": "..."},
        solution={"approach": "JWT tokens", "pr_number": 456},
        success=True
    )
    
    # Retrieve similar experiences before starting work
    similar = memory.retrieve_similar("authentication system")
    for exp in similar:
        print(f"Past approach: {exp['solution_approach']}")
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path


class AgentMemory:
    """
    File-based memory system for individual agents
    
    Features:
    - Persistent storage in JSON format
    - Keyword-based similarity search
    - Success/failure tracking
    - Memory consolidation (pruning old/irrelevant)
    - Export/import for knowledge sharing
    """
    
    def __init__(self, agent_id: str, memory_dir: str = ".github/agent-system/memory"):
        """
        Initialize agent memory
        
        Args:
            agent_id: Unique identifier for agent (e.g., "coach-master")
            memory_dir: Directory for storing memory files
        """
        self.agent_id = agent_id
        self.memory_dir = Path(memory_dir)
        self.memory_file = self.memory_dir / f"{agent_id}.json"
        
        # Ensure directory exists
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing memories
        self.memories: List[Dict[str, Any]] = self.load_memories()
        
        # Statistics
        self.stats = self.calculate_stats()
    
    def load_memories(self) -> List[Dict[str, Any]]:
        """Load memories from file"""
        if not self.memory_file.exists():
            return []
        
        try:
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
                
                # Handle both list and dict formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("memories", [])
                else:
                    return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Error loading memories for {self.agent_id}: {e}")
            return []
    
    def save_memories(self):
        """Persist memories to file"""
        try:
            data = {
                "agent_id": self.agent_id,
                "last_updated": datetime.utcnow().isoformat(),
                "total_memories": len(self.memories),
                "stats": self.stats,
                "memories": self.memories
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"❌ Error saving memories for {self.agent_id}: {e}")
    
    def store_experience(
        self,
        issue: Dict[str, Any],
        solution: Dict[str, Any],
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a memory of agent's work
        
        Args:
            issue: Issue data (number, title, body, labels, etc.)
            solution: Solution data (approach, pr_number, outcome, etc.)
            success: Whether the solution was successful (PR merged)
            metadata: Additional context (time_taken, difficulty, etc.)
        
        Returns:
            Memory ID (for reference)
        """
        # Generate unique ID
        timestamp = datetime.utcnow().isoformat()
        id_source = f"{self.agent_id}{issue.get('title', '')}{timestamp}"
        memory_id = hashlib.md5(id_source.encode()).hexdigest()
        
        # Create memory record
        memory = {
            "id": memory_id,
            "timestamp": timestamp,
            "agent_id": self.agent_id,
            
            # Issue context
            "issue_number": issue.get("number"),
            "issue_title": issue.get("title", ""),
            "issue_description": issue.get("body", "")[:500],  # First 500 chars
            "issue_labels": issue.get("labels", []),
            "issue_url": issue.get("url", ""),
            
            # Solution details
            "solution_approach": solution.get("approach", ""),
            "pr_number": solution.get("pr_number"),
            "pr_url": solution.get("pr_url", ""),
            "outcome": solution.get("outcome", ""),
            "changes_summary": solution.get("changes", ""),
            
            # Result
            "success": success,
            
            # Metadata
            "metadata": metadata or {},
            
            # For retrieval
            "access_count": 0,
            "last_accessed": None
        }
        
        # Add to memories
        self.memories.append(memory)
        
        # Update stats
        self.stats = self.calculate_stats()
        
        # Save to file
        self.save_memories()
        
        return memory_id
    
    def retrieve_similar(
        self,
        query: str,
        limit: int = 5,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories similar to query
        
        Args:
            query: Search query (issue description, keywords, etc.)
            limit: Maximum number of results
            success_only: Only return successful experiences
        
        Returns:
            List of similar memories, sorted by relevance
        """
        if not self.memories:
            return []
        
        # Extract query keywords
        query_keywords = set(self.extract_keywords(query))
        
        if not query_keywords:
            return []
        
        # Score each memory
        scored_memories = []
        for memory in self.memories:
            # Skip failed experiences if only want successes
            if success_only and not memory.get("success"):
                continue
            
            # Build memory text for comparison
            memory_text = " ".join([
                memory.get("issue_title", ""),
                memory.get("issue_description", ""),
                memory.get("solution_approach", ""),
                " ".join(memory.get("issue_labels", []))
            ])
            
            memory_keywords = set(self.extract_keywords(memory_text))
            
            # Calculate relevance score
            keyword_overlap = len(query_keywords & memory_keywords)
            
            if keyword_overlap > 0:
                # Base score from keyword overlap
                score = keyword_overlap
                
                # Bonus for successful memories
                if memory.get("success"):
                    score *= 1.5
                
                # Bonus for recent memories (decay over time)
                age_days = self.get_memory_age_days(memory)
                recency_bonus = max(0, 1 - (age_days / 90))  # 90 day decay
                score += recency_bonus
                
                # Bonus for frequently accessed memories
                access_bonus = min(memory.get("access_count", 0) / 10, 1.0)
                score += access_bonus
                
                scored_memories.append((score, memory))
        
        # Sort by score (descending)
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        # Update access tracking for returned memories
        result_memories = []
        for score, memory in scored_memories[:limit]:
            memory["access_count"] = memory.get("access_count", 0) + 1
            memory["last_accessed"] = datetime.utcnow().isoformat()
            result_memories.append(memory)
        
        # Save updated access counts
        if result_memories:
            self.save_memories()
        
        return result_memories
    
    def get_successful_patterns(self, min_occurrences: int = 2) -> List[Dict[str, Any]]:
        """
        Identify patterns from successful experiences
        
        Args:
            min_occurrences: Minimum times a pattern must appear
        
        Returns:
            List of common successful approaches
        """
        successful = [m for m in self.memories if m.get("success")]
        
        if len(successful) < min_occurrences:
            return []
        
        # Group by similar approaches
        approach_groups = {}
        for memory in successful:
            approach = memory.get("solution_approach", "")
            keywords = tuple(sorted(self.extract_keywords(approach)))
            
            if keywords not in approach_groups:
                approach_groups[keywords] = []
            approach_groups[keywords].append(memory)
        
        # Find patterns that appear multiple times
        patterns = []
        for keywords, memories in approach_groups.items():
            if len(memories) >= min_occurrences:
                patterns.append({
                    "pattern_keywords": list(keywords),
                    "occurrences": len(memories),
                    "success_rate": 1.0,  # All are successful by definition
                    "example_issues": [
                        {
                            "title": m.get("issue_title"),
                            "approach": m.get("solution_approach"),
                            "pr": m.get("pr_number")
                        }
                        for m in memories[:3]  # First 3 examples
                    ]
                })
        
        # Sort by occurrence frequency
        patterns.sort(key=lambda x: x["occurrences"], reverse=True)
        
        return patterns
    
    def consolidate(
        self,
        max_age_days: int = 180,
        min_relevance: int = 0,
        keep_successful: bool = True
    ):
        """
        Consolidate memories by removing old/irrelevant ones
        
        Args:
            max_age_days: Remove memories older than this
            min_relevance: Minimum access count to keep
            keep_successful: Always keep successful memories
        """
        original_count = len(self.memories)
        
        # Filter memories
        consolidated = []
        for memory in self.memories:
            age_days = self.get_memory_age_days(memory)
            access_count = memory.get("access_count", 0)
            is_successful = memory.get("success", False)
            
            # Keep if:
            # - Recent (< max_age_days)
            # - Frequently accessed (>= min_relevance)
            # - Successful (if keep_successful is True)
            keep = (
                age_days < max_age_days or
                access_count >= min_relevance or
                (keep_successful and is_successful)
            )
            
            if keep:
                consolidated.append(memory)
        
        # Update memories
        self.memories = consolidated
        removed_count = original_count - len(consolidated)
        
        # Update stats and save
        self.stats = self.calculate_stats()
        self.save_memories()
        
        return {
            "original_count": original_count,
            "removed_count": removed_count,
            "retained_count": len(consolidated)
        }
    
    def export_to_shared(self) -> Dict[str, Any]:
        """
        Export memories for team knowledge sharing
        
        Returns:
            Dictionary with agent's successful patterns and key memories
        """
        return {
            "agent_id": self.agent_id,
            "exported_at": datetime.utcnow().isoformat(),
            "statistics": self.stats,
            "successful_patterns": self.get_successful_patterns(),
            "top_memories": sorted(
                self.memories,
                key=lambda m: (
                    m.get("success", False),
                    m.get("access_count", 0)
                ),
                reverse=True
            )[:10]  # Top 10 memories
        }
    
    def import_from_shared(self, shared_data: Dict[str, Any], merge: bool = True):
        """
        Import memories from shared team knowledge
        
        Args:
            shared_data: Exported data from another agent
            merge: If True, merge with existing; if False, replace
        """
        if not merge:
            self.memories = []
        
        # Import memories, avoiding duplicates
        existing_ids = {m["id"] for m in self.memories}
        
        imported_memories = shared_data.get("top_memories", [])
        imported_count = 0
        
        for memory in imported_memories:
            if memory["id"] not in existing_ids:
                # Mark as imported from another agent
                memory["imported_from"] = shared_data.get("agent_id")
                memory["imported_at"] = datetime.utcnow().isoformat()
                
                self.memories.append(memory)
                imported_count += 1
        
        # Update stats and save
        self.stats = self.calculate_stats()
        self.save_memories()
        
        return {"imported_count": imported_count}
    
    def calculate_stats(self) -> Dict[str, Any]:
        """Calculate statistics about memories"""
        if not self.memories:
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0
            }
        
        successful = sum(1 for m in self.memories if m.get("success"))
        failed = len(self.memories) - successful
        
        return {
            "total": len(self.memories),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.memories) if self.memories else 0.0,
            "oldest_memory": min(
                (self.parse_timestamp(m["timestamp"]) for m in self.memories),
                default=datetime.utcnow()
            ).isoformat(),
            "newest_memory": max(
                (self.parse_timestamp(m["timestamp"]) for m in self.memories),
                default=datetime.utcnow()
            ).isoformat()
        }
    
    def get_memory_age_days(self, memory: Dict[str, Any]) -> int:
        """Calculate age of memory in days"""
        timestamp = self.parse_timestamp(memory["timestamp"])
        age = datetime.utcnow() - timestamp
        return age.days
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> datetime:
        """Parse ISO format timestamp"""
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extract meaningful keywords from text
        Simple word filtering - can be enhanced with NLP
        """
        # Stopwords to exclude
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "as", "is", "was", "are", "be", "have",
            "has", "had", "do", "does", "did", "will", "can", "could",
            "should", "would", "this", "that", "from", "by", "not", "all"
        }
        
        # Clean and split
        text = text.lower()
        words = text.split()
        
        # Filter
        keywords = []
        for word in words:
            # Remove punctuation
            clean = ''.join(c for c in word if c.isalnum() or c in '-_')
            
            if (clean and
                len(clean) > 3 and
                clean not in stop_words):
                keywords.append(clean)
        
        return list(set(keywords))  # Deduplicate
    
    def __str__(self) -> str:
        """String representation"""
        return (
            f"AgentMemory({self.agent_id}): "
            f"{self.stats['total']} memories, "
            f"{self.stats['successful']} successful "
            f"({self.stats['success_rate']:.1%})"
        )


def demo():
    """Demonstration of AgentMemory usage"""
    print("=" * 70)
    print("🧠 Agent Memory System Demo - @coach-master")
    print("=" * 70)
    
    # Create memory for coach-master
    memory = AgentMemory("coach-master")
    print(f"\n✅ Initialized: {memory}")
    
    # Store some example experiences
    print("\n📝 Storing experiences...")
    
    memory.store_experience(
        issue={
            "number": 123,
            "title": "Add JWT authentication",
            "body": "Need to implement JWT-based authentication for API",
            "labels": ["enhancement", "security"]
        },
        solution={
            "approach": "Implemented JWT with refresh tokens using PyJWT library",
            "pr_number": 456,
            "outcome": "Successfully merged after security review"
        },
        success=True,
        metadata={"time_taken_hours": 8, "difficulty": "medium"}
    )
    
    memory.store_experience(
        issue={
            "number": 124,
            "title": "Fix authentication bug",
            "body": "JWT tokens not validating correctly",
            "labels": ["bug", "security"]
        },
        solution={
            "approach": "Fixed token validation logic, added expiration check",
            "pr_number": 457,
            "outcome": "Bug fixed, tests added"
        },
        success=True,
        metadata={"time_taken_hours": 2, "difficulty": "low"}
    )
    
    memory.store_experience(
        issue={
            "number": 125,
            "title": "Add OAuth2 support",
            "body": "Integrate OAuth2 for third-party authentication",
            "labels": ["enhancement", "integration"]
        },
        solution={
            "approach": "Attempted OAuth2 integration with Google/GitHub",
            "pr_number": 458,
            "outcome": "PR closed - too complex for current scope"
        },
        success=False,
        metadata={"time_taken_hours": 16, "difficulty": "high"}
    )
    
    print(f"✅ Stored 3 experiences")
    print(f"   Updated stats: {memory}")
    
    # Retrieve similar experiences
    print("\n🔍 Retrieving similar experiences...")
    
    query = "authentication token validation"
    similar = memory.retrieve_similar(query, limit=3)
    
    print(f"\n   Query: '{query}'")
    print(f"   Found {len(similar)} similar experiences:\n")
    
    for i, exp in enumerate(similar, 1):
        print(f"   {i}. {exp['issue_title']}")
        print(f"      ✓ Success: {exp['success']}")
        print(f"      📝 Approach: {exp['solution_approach'][:60]}...")
        print(f"      🔗 PR #{exp['pr_number']}")
        print()
    
    # Get successful patterns
    print("🎯 Successful patterns:")
    patterns = memory.get_successful_patterns(min_occurrences=1)
    
    for pattern in patterns[:3]:
        print(f"\n   Pattern: {', '.join(pattern['pattern_keywords'][:5])}")
        print(f"   Occurrences: {pattern['occurrences']}")
        print(f"   Success Rate: {pattern['success_rate']:.1%}")
    
    # Export for sharing
    print("\n📤 Exporting knowledge for team...")
    exported = memory.export_to_shared()
    
    print(f"   ✅ Exported {len(exported['top_memories'])} top memories")
    print(f"   ✅ Identified {len(exported['successful_patterns'])} patterns")
    
    print("\n" + "=" * 70)
    print("✅ Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo()
