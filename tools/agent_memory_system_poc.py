#!/usr/bin/env python3
"""
Agent Memory System - Proof of Concept
Part of Mission idea:28 - AI/ML Agents Innovation

This module provides a working prototype of the agent memory system
inspired by GibsonAI/Memori, adapted for the Chained autonomous AI ecosystem.

Features:
- Short-term and long-term memory storage
- SQL-based persistence (SQLite)
- Memory retrieval with relevance scoring
- Learning from success/failure patterns
- Entity and rule memory

Author: @meta-coordinator
Date: November 16, 2025
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Memory:
    """
    Represents a single memory entry for an agent
    """
    id: str
    agent_id: str
    timestamp: str
    
    # Context
    issue_id: Optional[str]
    pr_id: Optional[str]
    context: str
    
    # Action taken
    action: str
    tools_used: List[str]
    
    # Outcome
    outcome: str
    success: bool
    metrics: Dict[str, Any]
    
    # Learning
    lesson_learned: Optional[str]
    tags: List[str]
    relevance_score: float
    
    # Memory type and expiration
    memory_type: str  # 'short_term', 'long_term', 'rule', 'entity'
    expires_at: Optional[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Entity:
    """
    Represents an entity tracked by the agent (person, project, technology, etc.)
    """
    id: str
    agent_id: str
    entity_type: str  # 'person', 'project', 'technology', 'pattern'
    entity_name: str
    properties: Dict[str, Any]
    first_seen: str
    last_updated: str
    interaction_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Rule:
    """
    Represents a learned rule or guideline
    """
    id: str
    agent_id: str
    rule_type: str  # 'guideline', 'constraint', 'preference'
    rule_text: str
    confidence: float
    created_from_memory_id: Optional[str]
    times_applied: int
    success_rate: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AgentMemorySystem:
    """
    SQL-based memory system for Chained agents
    
    Inspired by GibsonAI/Memori, this provides:
    - Persistent storage of agent experiences
    - Short-term and long-term memory
    - Entity tracking
    - Rule learning
    - Semantic-like retrieval (keyword-based for POC)
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize memory system
        
        Args:
            db_path: Path to SQLite database (":memory:" for in-memory)
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_database()
    
    def _init_database(self):
        """Create database schema if not exists"""
        cursor = self.conn.cursor()
        
        # Agent memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_memories (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                
                issue_id TEXT,
                pr_id TEXT,
                context TEXT NOT NULL,
                
                action TEXT NOT NULL,
                tools_used TEXT,  -- JSON array
                
                outcome TEXT NOT NULL,
                success INTEGER NOT NULL,  -- Boolean as 0/1
                metrics TEXT,  -- JSON object
                
                lesson_learned TEXT,
                tags TEXT,  -- JSON array
                relevance_score REAL DEFAULT 0.5,
                
                memory_type TEXT CHECK(memory_type IN ('short_term', 'long_term', 'rule', 'entity')),
                expires_at TEXT
            )
        """)
        
        # Indexes for fast retrieval
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_memories_agent ON agent_memories(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_memories_success ON agent_memories(success)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_memories_timestamp ON agent_memories(timestamp DESC)")
        
        # Entity table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_entities (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                properties TEXT,  -- JSON
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                interaction_count INTEGER DEFAULT 1
            )
        """)
        
        # Rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_rules (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                rule_text TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                created_from_memory_id TEXT,
                times_applied INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0
            )
        """)
        
        self.conn.commit()
    
    def store_memory(self, memory: Memory):
        """
        Store a memory in the database
        
        Args:
            memory: Memory object to store
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_memories (
                id, agent_id, timestamp, issue_id, pr_id, context,
                action, tools_used, outcome, success, metrics,
                lesson_learned, tags, relevance_score, memory_type, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.agent_id,
            memory.timestamp,
            memory.issue_id,
            memory.pr_id,
            memory.context,
            memory.action,
            json.dumps(memory.tools_used),
            memory.outcome,
            1 if memory.success else 0,
            json.dumps(memory.metrics),
            memory.lesson_learned,
            json.dumps(memory.tags),
            memory.relevance_score,
            memory.memory_type,
            memory.expires_at
        ))
        
        self.conn.commit()
    
    def retrieve_memories(
        self,
        agent_id: str,
        query: str,
        limit: int = 5,
        min_relevance: float = 0.5,
        prefer_successful: bool = True
    ) -> List[Memory]:
        """
        Retrieve relevant memories for a query
        
        Args:
            agent_id: Agent whose memories to search
            query: Query string (keyword-based for POC)
            limit: Maximum number of memories to return
            min_relevance: Minimum relevance score
            prefer_successful: Prioritize successful memories
        
        Returns:
            List of relevant Memory objects
        """
        cursor = self.conn.cursor()
        
        # Simple keyword matching for POC
        # In production, use embeddings and semantic search
        keywords = query.lower().split()
        
        # Build SQL query with keyword matching
        query_parts = []
        params = [agent_id, min_relevance]
        
        for keyword in keywords:
            query_parts.append("(context LIKE ? OR action LIKE ? OR outcome LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " OR ".join(query_parts) if query_parts else "1=1"
        
        sql = f"""
            SELECT * FROM agent_memories
            WHERE agent_id = ? AND relevance_score >= ? AND ({where_clause})
            ORDER BY success DESC, relevance_score DESC, timestamp DESC
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Convert to Memory objects
        memories = []
        for row in rows:
            memory = Memory(
                id=row['id'],
                agent_id=row['agent_id'],
                timestamp=row['timestamp'],
                issue_id=row['issue_id'],
                pr_id=row['pr_id'],
                context=row['context'],
                action=row['action'],
                tools_used=json.loads(row['tools_used']),
                outcome=row['outcome'],
                success=bool(row['success']),
                metrics=json.loads(row['metrics']),
                lesson_learned=row['lesson_learned'],
                tags=json.loads(row['tags']),
                relevance_score=row['relevance_score'],
                memory_type=row['memory_type'],
                expires_at=row['expires_at']
            )
            memories.append(memory)
        
        return memories
    
    def get_successful_patterns(self, agent_id: str, limit: int = 10) -> List[Memory]:
        """
        Get successful action patterns for learning
        
        Args:
            agent_id: Agent whose patterns to retrieve
            limit: Maximum number of patterns
        
        Returns:
            List of successful memories
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM agent_memories
            WHERE agent_id = ? AND success = 1
            ORDER BY relevance_score DESC, timestamp DESC
            LIMIT ?
        """, (agent_id, limit))
        
        rows = cursor.fetchall()
        
        memories = []
        for row in rows:
            memory = Memory(
                id=row['id'],
                agent_id=row['agent_id'],
                timestamp=row['timestamp'],
                issue_id=row['issue_id'],
                pr_id=row['pr_id'],
                context=row['context'],
                action=row['action'],
                tools_used=json.loads(row['tools_used']),
                outcome=row['outcome'],
                success=bool(row['success']),
                metrics=json.loads(row['metrics']),
                lesson_learned=row['lesson_learned'],
                tags=json.loads(row['tags']),
                relevance_score=row['relevance_score'],
                memory_type=row['memory_type'],
                expires_at=row['expires_at']
            )
            memories.append(memory)
        
        return memories
    
    def prune_expired_memories(self):
        """Remove expired short-term memories"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            DELETE FROM agent_memories
            WHERE expires_at IS NOT NULL AND expires_at < ?
        """, (now,))
        
        deleted = cursor.rowcount
        self.conn.commit()
        
        return deleted
    
    def get_memory_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get statistics about an agent's memories
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Dictionary with memory statistics
        """
        cursor = self.conn.cursor()
        
        # Total memories
        cursor.execute("SELECT COUNT(*) FROM agent_memories WHERE agent_id = ?", (agent_id,))
        total = cursor.fetchone()[0]
        
        # Successful memories
        cursor.execute("SELECT COUNT(*) FROM agent_memories WHERE agent_id = ? AND success = 1", (agent_id,))
        successful = cursor.fetchone()[0]
        
        # By type
        cursor.execute("""
            SELECT memory_type, COUNT(*) as count
            FROM agent_memories
            WHERE agent_id = ?
            GROUP BY memory_type
        """, (agent_id,))
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            "total_memories": total,
            "successful_memories": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "by_type": by_type
        }
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def create_memory_id(agent_id: str, context: str, action: str) -> str:
    """Generate unique memory ID"""
    data = f"{agent_id}{context}{action}{datetime.now().isoformat()}"
    return hashlib.md5(data.encode()).hexdigest()


# Example usage and demonstration
def demo_memory_system():
    """Demonstrate the memory system"""
    print("🧠 Agent Memory System - Proof of Concept Demo\n")
    print("=" * 60)
    
    # Create memory system
    memory_system = AgentMemorySystem(":memory:")
    agent_id = "investigate-champion"
    
    print(f"\n1. Storing memories for agent: {agent_id}\n")
    
    # Example 1: Successful bug investigation
    memory1 = Memory(
        id=create_memory_id(agent_id, "Python TypeError", "added type hints"),
        agent_id=agent_id,
        timestamp=datetime.now().isoformat(),
        issue_id="issue-123",
        pr_id="pr-456",
        context="Python TypeError in data processing pipeline when handling None values",
        action="Added type hints and validated input data types before processing",
        tools_used=["python-analyzer", "type-checker", "unit-tests"],
        outcome="Error resolved, pipeline running smoothly, no regressions",
        success=True,
        metrics={"files_changed": 3, "lines_added": 45, "tests_added": 8},
        lesson_learned="Always validate input types before processing, especially for None values",
        tags=["python", "bug-fix", "type-error", "data-processing"],
        relevance_score=0.9,
        memory_type="long_term",
        expires_at=None
    )
    memory_system.store_memory(memory1)
    print("✅ Stored: Python TypeError fix")
    
    # Example 2: Failed approach to security issue
    memory2 = Memory(
        id=create_memory_id(agent_id, "XSS vulnerability", "input sanitization"),
        agent_id=agent_id,
        timestamp=(datetime.now() - timedelta(days=2)).isoformat(),
        issue_id="issue-124",
        pr_id="pr-457",
        context="XSS vulnerability in user input form",
        action="Added basic input sanitization on frontend only",
        tools_used=["frontend-sanitizer"],
        outcome="Security review rejected - backend validation also required",
        success=False,
        metrics={"files_changed": 1, "review_score": 2},
        lesson_learned="Security fixes require both frontend AND backend validation",
        tags=["security", "xss", "validation", "failed-approach"],
        relevance_score=0.85,
        memory_type="long_term",
        expires_at=None
    )
    memory_system.store_memory(memory2)
    print("❌ Stored: Failed XSS fix attempt")
    
    # Example 3: Successful security fix
    memory3 = Memory(
        id=create_memory_id(agent_id, "XSS vulnerability fixed", "full validation"),
        agent_id=agent_id,
        timestamp=(datetime.now() - timedelta(days=1)).isoformat(),
        issue_id="issue-124",
        pr_id="pr-458",
        context="XSS vulnerability in user input form (second attempt)",
        action="Implemented comprehensive input validation on both frontend and backend",
        tools_used=["frontend-sanitizer", "backend-validator", "security-scanner"],
        outcome="Security review passed, vulnerability fixed",
        success=True,
        metrics={"files_changed": 4, "lines_added": 87, "security_score": 9.5},
        lesson_learned="Learned from previous failure - comprehensive validation is key",
        tags=["security", "xss", "validation", "success"],
        relevance_score=0.95,
        memory_type="long_term",
        expires_at=None
    )
    memory_system.store_memory(memory3)
    print("✅ Stored: Successful XSS fix")
    
    print(f"\n2. Memory Statistics\n")
    stats = memory_system.get_memory_stats(agent_id)
    print(f"Total Memories: {stats['total_memories']}")
    print(f"Successful: {stats['successful_memories']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    print(f"By Type: {stats['by_type']}")
    
    print(f"\n3. Retrieving relevant memories for new issue\n")
    
    # Simulate new issue about type errors
    new_issue_query = "TypeError in data processing with None values"
    print(f"Query: '{new_issue_query}'")
    
    relevant_memories = memory_system.retrieve_memories(
        agent_id=agent_id,
        query=new_issue_query,
        limit=3,
        prefer_successful=True
    )
    
    print(f"\nFound {len(relevant_memories)} relevant memories:\n")
    for i, memory in enumerate(relevant_memories, 1):
        print(f"Memory {i}:")
        print(f"  Context: {memory.context[:60]}...")
        print(f"  Action: {memory.action[:60]}...")
        print(f"  Success: {'✅' if memory.success else '❌'}")
        print(f"  Lesson: {memory.lesson_learned}")
        print()
    
    print(f"\n4. Successful Patterns Analysis\n")
    
    patterns = memory_system.get_successful_patterns(agent_id, limit=5)
    print(f"Found {len(patterns)} successful patterns:\n")
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Pattern {i}: {pattern.tags}")
        print(f"  Relevance: {pattern.relevance_score:.2f}")
        print(f"  Lesson: {pattern.lesson_learned}")
        print()
    
    # Close connection
    memory_system.close()
    
    print("=" * 60)
    print("\n✅ Demo complete! Memory system working as expected.\n")


if __name__ == "__main__":
    demo_memory_system()
