#!/usr/bin/env python3
"""
Agent Memory System for Chained
Inspired by GibsonAI/Memori and Google ADK-Go research

This module provides persistent memory capabilities for autonomous agents,
enabling them to learn from experience and improve over time.

Investigation by @investigate-champion
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Memory:
    """Represents a single memory entry for an agent."""
    id: str
    timestamp: str
    agent_id: str
    context: str
    action: str
    outcome: str
    success: bool
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return asdict(self)


class AgentMemoryEngine:
    """
    Persistent memory engine for Chained autonomous agents.
    
    Features:
    - Store agent experiences (context, action, outcome)
    - Retrieve similar past experiences
    - Learn from successful patterns
    - Share knowledge between agents
    - Export/import for backup and transfer
    
    In production, this would use a vector database for semantic search.
    For now, we use simple keyword matching and JSON storage.
    """
    
    def __init__(self, agent_id: str, storage_path: Optional[Path] = None):
        """
        Initialize memory engine for an agent.
        
        Args:
            agent_id: Unique identifier for the agent
            storage_path: Path to store memory files (default: learnings/agent_memory/)
        """
        self.agent_id = agent_id
        self.memories: List[Memory] = []
        
        # Set up storage
        if storage_path is None:
            storage_path = Path("learnings/agent_memory")
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing memories
        self.memory_file = self.storage_path / f"{agent_id}_memory.json"
        self._load_memories()
    
    def _load_memories(self):
        """Load memories from storage if they exist."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.memories = [Memory(**m) for m in data]
                print(f"📚 Loaded {len(self.memories)} memories for {self.agent_id}")
            except Exception as e:
                print(f"⚠️  Error loading memories: {e}")
                self.memories = []
    
    def _save_memories(self):
        """Persist memories to storage."""
        try:
            with open(self.memory_file, 'w') as f:
                data = [m.to_dict() for m in self.memories]
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving memories: {e}")
    
    def store(
        self,
        context: str,
        action: str,
        outcome: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """
        Store a new memory of an agent's action and outcome.
        
        Args:
            context: The situation or problem the agent faced
            action: What the agent did
            outcome: The result of the action
            success: Whether the action was successful
            metadata: Additional information (issue_id, pr_id, etc.)
        
        Returns:
            The created Memory object
        """
        # Generate unique ID based on context and action
        memory_id = hashlib.md5(
            f"{self.agent_id}{context}{action}".encode()
        ).hexdigest()[:16]
        
        memory = Memory(
            id=memory_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=self.agent_id,
            context=context,
            action=action,
            outcome=outcome,
            success=success,
            metadata=metadata or {}
        )
        
        self.memories.append(memory)
        self._save_memories()
        
        return memory
    
    def retrieve_similar(
        self,
        query: str,
        limit: int = 5,
        success_only: bool = False
    ) -> List[Memory]:
        """
        Retrieve memories similar to the query.
        
        In production, this would use semantic similarity with embeddings.
        For now, uses simple keyword matching.
        
        Args:
            query: The search query
            limit: Maximum number of memories to return
            success_only: If True, only return successful memories
        
        Returns:
            List of similar memories, ranked by relevance
        """
        # Extract keywords from query
        query_keywords = set(query.lower().split())
        
        scored_memories = []
        for memory in self.memories:
            # Skip unsuccessful memories if requested
            if success_only and not memory.success:
                continue
            
            # Calculate relevance score based on keyword overlap
            context_keywords = set(memory.context.lower().split())
            action_keywords = set(memory.action.lower().split())
            
            overlap = len(query_keywords & (context_keywords | action_keywords))
            
            if overlap > 0:
                # Boost score for successful memories
                score = overlap * (1.5 if memory.success else 1.0)
                scored_memories.append((score, memory))
        
        # Sort by relevance
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        return [m for _, m in scored_memories[:limit]]
    
    def get_successful_patterns(self, limit: int = 10) -> List[Memory]:
        """
        Get the most recent successful action patterns for learning.
        
        Args:
            limit: Maximum number of patterns to return
        
        Returns:
            List of successful memories, sorted by timestamp (newest first)
        """
        successful = [m for m in self.memories if m.success]
        successful.sort(
            key=lambda m: datetime.fromisoformat(m.timestamp),
            reverse=True
        )
        return successful[:limit]
    
    def get_failure_patterns(self, limit: int = 10) -> List[Memory]:
        """
        Get recent failure patterns to learn what to avoid.
        
        Args:
            limit: Maximum number of patterns to return
        
        Returns:
            List of unsuccessful memories, sorted by timestamp (newest first)
        """
        failures = [m for m in self.memories if not m.success]
        failures.sort(
            key=lambda m: datetime.fromisoformat(m.timestamp),
            reverse=True
        )
        return failures[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about agent's memory."""
        total = len(self.memories)
        successful = sum(1 for m in self.memories if m.success)
        
        return {
            "agent_id": self.agent_id,
            "total_memories": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "oldest_memory": min(
                (m.timestamp for m in self.memories),
                default=None
            ),
            "newest_memory": max(
                (m.timestamp for m in self.memories),
                default=None
            )
        }
    
    def export_memories(self) -> str:
        """
        Export all memories as JSON string.
        Useful for backup or transferring knowledge between agents.
        
        Returns:
            JSON string of all memories
        """
        data = [m.to_dict() for m in self.memories]
        return json.dumps(data, indent=2)
    
    def import_memories(self, json_data: str):
        """
        Import memories from JSON string.
        Useful for restoring from backup or sharing knowledge.
        
        Args:
            json_data: JSON string containing memory data
        """
        try:
            data = json.loads(json_data)
            imported_memories = [Memory(**m) for m in data]
            self.memories.extend(imported_memories)
            self._save_memories()
            print(f"✅ Imported {len(imported_memories)} memories")
        except Exception as e:
            print(f"⚠️  Error importing memories: {e}")
    
    def prune_old_memories(self, keep_count: int = 100):
        """
        Prune old memories to keep storage manageable.
        Keeps the most recent memories and all successful ones.
        
        Args:
            keep_count: Minimum number of memories to keep
        """
        if len(self.memories) <= keep_count:
            return
        
        # Keep all successful memories
        successful = [m for m in self.memories if m.success]
        
        # Keep most recent unsuccessful memories
        unsuccessful = [m for m in self.memories if not m.success]
        unsuccessful.sort(
            key=lambda m: datetime.fromisoformat(m.timestamp),
            reverse=True
        )
        
        # Combine
        self.memories = successful + unsuccessful[:keep_count - len(successful)]
        self._save_memories()
        
        print(f"🗑️  Pruned memories, kept {len(self.memories)} most relevant")


class MultiAgentMemoryCoordinator:
    """
    Coordinator for sharing knowledge between multiple agents.
    Enables collaborative learning and knowledge transfer.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the coordinator.
        
        Args:
            storage_path: Path to store shared memory files
        """
        if storage_path is None:
            storage_path = Path("learnings/agent_memory/shared")
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def share_knowledge(
        self,
        source_agent: AgentMemoryEngine,
        target_agents: List[AgentMemoryEngine],
        success_only: bool = True
    ):
        """
        Share knowledge from one agent to others.
        
        Args:
            source_agent: Agent whose knowledge to share
            target_agents: Agents to receive the knowledge
            success_only: If True, only share successful experiences
        """
        if success_only:
            memories = source_agent.get_successful_patterns()
        else:
            memories = source_agent.memories
        
        exported = json.dumps([m.to_dict() for m in memories])
        
        for target in target_agents:
            target.import_memories(exported)
        
        print(f"🤝 Shared {len(memories)} memories from {source_agent.agent_id} "
              f"to {len(target_agents)} agents")
    
    def aggregate_best_practices(
        self,
        agents: List[AgentMemoryEngine],
        min_success_count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Aggregate best practices from multiple agents.
        
        Identifies patterns that multiple agents have used successfully.
        
        Args:
            agents: List of agents to aggregate from
            min_success_count: Minimum number of agents that must have succeeded
        
        Returns:
            List of best practice patterns
        """
        # Group memories by action pattern
        action_patterns: Dict[str, List[Memory]] = {}
        
        for agent in agents:
            for memory in agent.get_successful_patterns():
                # Normalize action for grouping
                normalized = memory.action.lower().strip()
                if normalized not in action_patterns:
                    action_patterns[normalized] = []
                action_patterns[normalized].append(memory)
        
        # Find patterns used successfully by multiple agents
        best_practices = []
        for action, memories in action_patterns.items():
            unique_agents = len(set(m.agent_id for m in memories))
            if unique_agents >= min_success_count:
                best_practices.append({
                    "action": action,
                    "success_count": len(memories),
                    "agent_count": unique_agents,
                    "examples": [
                        {
                            "agent": m.agent_id,
                            "context": m.context,
                            "outcome": m.outcome
                        }
                        for m in memories[:3]  # Show top 3 examples
                    ]
                })
        
        return best_practices


# Example usage and testing
if __name__ == "__main__":
    print("🧠 Agent Memory System Demo")
    print("=" * 50)
    
    # Create memory engine for an agent
    agent = AgentMemoryEngine("agent-investigate-champion")
    
    # Store some experiences
    print("\n📝 Storing experiences...")
    
    agent.store(
        context="Python TypeError in data processing pipeline",
        action="Added type hints and validated input data types",
        outcome="Error resolved, pipeline running smoothly",
        success=True,
        metadata={"issue_id": "123", "pr_id": "456"}
    )
    
    agent.store(
        context="GitHub Actions workflow failing intermittently",
        action="Added retry logic and increased timeout",
        outcome="Workflow now reliable",
        success=True,
        metadata={"workflow": "ci.yml"}
    )
    
    agent.store(
        context="API rate limiting causing failures",
        action="Implemented exponential backoff",
        outcome="API calls now succeed consistently",
        success=True
    )
    
    agent.store(
        context="Memory leak in long-running process",
        action="Added more logging",
        outcome="Still leaking, need different approach",
        success=False
    )
    
    # Retrieve similar experiences
    print("\n🔍 Searching for similar experiences...")
    query = "Python error in pipeline"
    similar = agent.retrieve_similar(query, limit=3)
    
    print(f"\nFound {len(similar)} similar experiences for: '{query}'")
    for i, memory in enumerate(similar, 1):
        print(f"\n{i}. Context: {memory.context}")
        print(f"   Action: {memory.action}")
        print(f"   Outcome: {memory.outcome}")
        print(f"   Success: {'✅' if memory.success else '❌'}")
    
    # Get statistics
    print("\n📊 Memory Statistics:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Get successful patterns
    print("\n✅ Recent Successful Patterns:")
    patterns = agent.get_successful_patterns(limit=3)
    for pattern in patterns:
        print(f"   - {pattern.action}")
    
    # Multi-agent collaboration demo
    print("\n\n🤝 Multi-Agent Collaboration Demo")
    print("=" * 50)
    
    agent2 = AgentMemoryEngine("agent-secure-specialist")
    agent2.store(
        context="Security vulnerability in authentication",
        action="Implemented OAuth2 with proper token validation",
        outcome="Vulnerability fixed, security audit passed",
        success=True
    )
    
    coordinator = MultiAgentMemoryCoordinator()
    coordinator.share_knowledge(
        source_agent=agent,
        target_agents=[agent2],
        success_only=True
    )
    
    print(f"\n📚 Agent 2 now has {len(agent2.memories)} memories")
    
    print("\n✨ Demo complete!")
