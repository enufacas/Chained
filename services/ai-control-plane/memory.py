"""
Memory Agent Module

The Memory Agent is responsible for retrieving and managing semantic patterns
from the vector database. It enables the AI Control Plane to learn from past
operations and reuse successful patterns.

Responsibilities:
1. Pattern Retrieval - Find similar patterns for new requests
2. Pattern Ranking - Score patterns by relevance, success, and usage
3. Pattern Selection - Choose best patterns for current context
4. Pattern Learning - Store new patterns after successful operations

Author: AI-Native Control Plane
Date: 2025-12-06
Phase: 6 (Production Integration) - Step 3
"""

import logging
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Add state-db to path for imports
STATE_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'state-db')
sys.path.insert(0, STATE_DB_PATH)

try:
    from vector import (
        generate_embedding,
        search_similar_patterns,
        store_pattern,
        increment_pattern_usage,
        get_pattern,
        list_patterns
    )
    VECTOR_DB_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Vector DB not available: {e}")
    VECTOR_DB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryAgent:
    """
    Memory Agent for pattern retrieval and learning.
    
    This agent acts as the bridge between the AI Control Plane and the
    semantic memory stored in the vector database.
    """
    
    def __init__(
        self, 
        embedding_provider: str = "openai",
        system_version: str = "v0.1.0"
    ):
        """
        Initialize Memory Agent.
        
        Args:
            embedding_provider: Provider for embeddings ('openai' or 'local')
            system_version: Current control plane version
        """
        if not VECTOR_DB_AVAILABLE:
            logger.warning("Vector DB not available - Memory Agent running in stub mode")
        
        self.embedding_provider = embedding_provider
        self.system_version = system_version
        logger.info(
            f"Memory Agent initialized (provider={embedding_provider}, "
            f"version={system_version})"
        )
    
    def retrieve_relevant_patterns(
        self,
        user_request: str,
        intent: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve patterns relevant to a user request.
        
        This is the main entry point for pattern retrieval. It:
        1. Generates embedding for the request
        2. Searches for similar patterns
        3. Ranks patterns by multiple criteria
        4. Returns top-k most relevant patterns
        
        Args:
            user_request: Natural language user request
            intent: Classified intent (create_app, update_app, etc.)
            context: Optional context (app_type, filters, etc.)
            top_k: Number of patterns to return
            
        Returns:
            List of pattern dictionaries with relevance scores
            
        Example:
            >>> agent = MemoryAgent()
            >>> patterns = agent.retrieve_relevant_patterns(
            ...     "Create a blog with user authentication",
            ...     intent='create_app',
            ...     context={'app_type': 'dynamic'}
            ... )
            >>> for p in patterns:
            ...     print(f"{p['relevance_score']:.2f} - {p['description']}")
        """
        if not VECTOR_DB_AVAILABLE:
            logger.warning("Vector DB not available - returning empty patterns")
            return []
        
        logger.info(f"Retrieving patterns for: {user_request[:50]}...")
        
        # Extract context filters
        context = context or {}
        filter_pattern_type = self._infer_pattern_type(intent)
        filter_app_type = context.get('app_type')
        min_success_score = context.get('min_success_score', 0.5)
        
        try:
            # Search for similar patterns (get more than top_k for ranking)
            search_results = search_similar_patterns(
                query_text=user_request,
                top_k=top_k * 2,  # Get 2x for better ranking
                similarity_threshold=0.6,  # Lower threshold, we'll rank after
                filter_pattern_type=filter_pattern_type,
                filter_app_type=filter_app_type,
                min_success_score=min_success_score,
                embedding_provider=self.embedding_provider
            )
            
            if not search_results:
                logger.info("No relevant patterns found")
                return []
            
            # Rank patterns by multiple criteria
            ranked_patterns = self._rank_patterns(
                search_results,
                intent=intent,
                context=context
            )
            
            # Return top-k
            top_patterns = ranked_patterns[:top_k]
            
            logger.info(
                f"Retrieved {len(top_patterns)} patterns "
                f"(avg relevance: {sum(p['relevance_score'] for p in top_patterns) / len(top_patterns):.2f})"
            )
            
            return top_patterns
            
        except Exception as e:
            logger.error(f"Pattern retrieval failed: {e}")
            return []
    
    def _infer_pattern_type(self, intent: str) -> Optional[str]:
        """
        Infer pattern type from intent.
        
        Maps intent classification to pattern types for filtering.
        """
        intent_to_pattern_type = {
            'create_app': 'template',
            'update_app': 'template',
            'deploy': 'template',
            'scale': 'style',
            'system_upgrade': 'system_upgrade_proposal',
            'query_status': None  # No specific pattern type
        }
        return intent_to_pattern_type.get(intent)
    
    def _rank_patterns(
        self,
        patterns: List[Dict[str, Any]],
        intent: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank patterns by multiple criteria.
        
        Ranking factors:
        1. Similarity score (from vector search) - 40%
        2. Success score (quality metric) - 30%
        3. Usage count (popularity) - 20%
        4. Recency (last_used_at) - 10%
        
        Args:
            patterns: List of patterns from search
            intent: User intent
            context: Additional context
            
        Returns:
            Patterns sorted by relevance score (descending)
        """
        if not patterns:
            return []
        
        # Calculate relevance scores
        for pattern in patterns:
            # Factor 1: Similarity (already 0-1)
            similarity = pattern.get('similarity_score', 0.0)
            
            # Factor 2: Success score (already 0-1)
            success = pattern.get('success_score', 0.0)
            
            # Factor 3: Usage count (normalize to 0-1)
            usage = pattern.get('usage_count', 0)
            max_usage = max(p.get('usage_count', 0) for p in patterns)
            usage_normalized = usage / max_usage if max_usage > 0 else 0.0
            
            # Factor 4: Recency (not yet available in pattern, placeholder)
            recency = 0.5  # Neutral for now
            
            # Weighted combination
            relevance_score = (
                0.40 * similarity +
                0.30 * success +
                0.20 * usage_normalized +
                0.10 * recency
            )
            
            pattern['relevance_score'] = relevance_score
        
        # Sort by relevance score (descending)
        ranked = sorted(
            patterns,
            key=lambda p: p['relevance_score'],
            reverse=True
        )
        
        return ranked
    
    def learn_from_operation(
        self,
        operation_result: Dict[str, Any],
        pattern_type: str = 'template'
    ) -> Optional[str]:
        """
        Learn from a successful operation by storing it as a pattern.
        
        This should be called after a successful operation to capture
        the pattern for future reuse.
        
        Args:
            operation_result: Result from successful operation
                - Required fields: user_request, plan, operation_id
                - Optional: app_type, gcp_services_used, etc.
            pattern_type: Type of pattern to store
            
        Returns:
            Pattern ID if stored, None if failed or skipped
            
        Example:
            >>> agent = MemoryAgent()
            >>> result = {
            ...     'user_request': 'Create a blog site',
            ...     'plan': {'steps': [...], 'resources': [...]},
            ...     'operation_id': 'op_abc123',
            ...     'success_score': 0.95
            ... }
            >>> pattern_id = agent.learn_from_operation(result)
        """
        if not VECTOR_DB_AVAILABLE:
            logger.warning("Vector DB not available - cannot store pattern")
            return None
        
        try:
            # Extract required fields
            user_request = operation_result.get('user_request')
            plan = operation_result.get('plan')
            operation_id = operation_result.get('operation_id')
            
            if not all([user_request, plan, operation_id]):
                logger.warning("Missing required fields for pattern learning")
                return None
            
            # Prepare pattern content
            content = {
                'plan': plan,
                'original_request': user_request,
                'execution_metadata': {
                    'duration_seconds': operation_result.get('duration_seconds'),
                    'resources_created': operation_result.get('resources_created', [])
                }
            }
            
            # Store pattern
            pattern_id = store_pattern(
                pattern_type=pattern_type,
                natural_language_description=user_request,
                content=content,
                source_operation_id=operation_id,
                source_plan_hash=operation_result.get('plan_hash'),
                app_type=operation_result.get('app_type'),
                gcp_services_used=operation_result.get('gcp_services_used'),
                success_score=operation_result.get('success_score', 1.0),
                system_version=self.system_version,
                tags=operation_result.get('tags'),
                metadata=operation_result.get('metadata'),
                embedding_provider=self.embedding_provider
            )
            
            logger.info(f"Learned new pattern: {pattern_id}")
            return pattern_id
            
        except Exception as e:
            logger.error(f"Pattern learning failed: {e}")
            return None
    
    def mark_pattern_used(self, pattern_id: str) -> None:
        """
        Mark a pattern as used (increment usage counter).
        
        Call this when a pattern is successfully reused.
        
        Args:
            pattern_id: ID of the pattern that was used
        """
        if not VECTOR_DB_AVAILABLE:
            return
        
        try:
            increment_pattern_usage(pattern_id)
            logger.info(f"Marked pattern {pattern_id} as used")
        except Exception as e:
            logger.error(f"Failed to mark pattern as used: {e}")
    
    def get_pattern_details(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full details of a specific pattern.
        
        Args:
            pattern_id: Pattern ID to retrieve
            
        Returns:
            Pattern dictionary or None if not found
        """
        if not VECTOR_DB_AVAILABLE:
            return None
        
        try:
            return get_pattern(pattern_id)
        except Exception as e:
            logger.error(f"Failed to get pattern: {e}")
            return None
    
    def list_available_patterns(
        self,
        pattern_type: Optional[str] = None,
        app_type: Optional[str] = None,
        min_success_score: float = 0.7,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List available patterns with filters.
        
        Useful for browsing what patterns are available.
        
        Args:
            pattern_type: Optional pattern type filter
            app_type: Optional app type filter
            min_success_score: Minimum success score
            limit: Maximum results
            
        Returns:
            List of pattern summaries
        """
        if not VECTOR_DB_AVAILABLE:
            return []
        
        try:
            return list_patterns(
                pattern_type=pattern_type,
                app_type=app_type,
                min_success_score=min_success_score,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to list patterns: {e}")
            return []
    
    def format_patterns_for_prompt(
        self,
        patterns: List[Dict[str, Any]],
        max_patterns: int = 3
    ) -> str:
        """
        Format patterns as text for LLM prompt inclusion.
        
        This converts pattern data into a format that can be included
        in an LLM prompt to guide planning.
        
        Args:
            patterns: List of patterns to format
            max_patterns: Maximum patterns to include
            
        Returns:
            Formatted text for prompt inclusion
        """
        if not patterns:
            return "No similar patterns found in memory."
        
        lines = ["## Relevant Patterns from Semantic Memory\n"]
        lines.append("The following patterns may be useful for this request:\n")
        
        for i, pattern in enumerate(patterns[:max_patterns], 1):
            lines.append(f"\n### Pattern {i}: {pattern.get('description', 'Unknown')}")
            lines.append(f"- **Type**: {pattern.get('pattern_type', 'unknown')}")
            lines.append(f"- **Relevance**: {pattern.get('relevance_score', 0.0):.2f}")
            lines.append(f"- **Success Score**: {pattern.get('success_score', 0.0):.2f}")
            lines.append(f"- **Usage Count**: {pattern.get('usage_count', 0)}")
            
            # Include plan steps if available
            content = pattern.get('content', {})
            if isinstance(content, dict):
                plan = content.get('plan', {})
                if isinstance(plan, dict):
                    steps = plan.get('plan_steps', [])
                    if steps:
                        lines.append(f"- **Plan Steps**:")
                        for step in steps[:5]:  # Max 5 steps
                            lines.append(f"  - {step}")
        
        lines.append("\n---\n")
        return "\n".join(lines)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    """
    Example usage demonstrating Memory Agent operations.
    
    Prerequisites:
    - PostgreSQL with pgvector extension
    - Migration 002 applied
    - Some patterns stored in the database
    - OPENAI_API_KEY or use embedding_provider='local'
    """
    
    print("🧠 Testing Memory Agent\n")
    
    # Initialize agent
    agent = MemoryAgent(
        embedding_provider='openai',  # or 'local'
        system_version='v0.1.0'
    )
    
    # Example 1: Retrieve relevant patterns
    print("1. Retrieving patterns for a new request...")
    try:
        patterns = agent.retrieve_relevant_patterns(
            user_request="Create a blog platform with user authentication",
            intent='create_app',
            context={'app_type': 'dynamic'},
            top_k=3
        )
        
        if patterns:
            print(f"Found {len(patterns)} relevant patterns:")
            for i, pattern in enumerate(patterns, 1):
                print(f"  {i}. [{pattern['relevance_score']:.2f}] {pattern['description']}")
        else:
            print("No patterns found")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}\n")
    
    # Example 2: Learn from a successful operation
    print("2. Learning from a successful operation...")
    try:
        operation_result = {
            'user_request': 'Deploy a portfolio website',
            'plan': {
                'plan_steps': [
                    'Create GCS bucket',
                    'Generate static HTML',
                    'Upload files',
                    'Configure public access'
                ],
                'estimated_duration_seconds': 45
            },
            'operation_id': 'op_test_12345',
            'plan_hash': 'plan_abc123',
            'app_type': 'static',
            'gcp_services_used': ['gcs'],
            'success_score': 0.92,
            'tags': ['portfolio', 'static', 'simple']
        }
        
        pattern_id = agent.learn_from_operation(operation_result)
        if pattern_id:
            print(f"✅ Learned pattern: {pattern_id}")
        else:
            print("⚠️ Pattern not stored")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}\n")
    
    # Example 3: List available patterns
    print("3. Listing available patterns...")
    try:
        patterns = agent.list_available_patterns(
            pattern_type='template',
            min_success_score=0.7,
            limit=5
        )
        
        if patterns:
            print(f"Found {len(patterns)} template patterns:")
            for pattern in patterns:
                print(f"  - {pattern['description'][:60]}... "
                      f"(score: {pattern['success_score']:.2f}, "
                      f"uses: {pattern['usage_count']})")
        else:
            print("No patterns available")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}\n")
    
    # Example 4: Format patterns for prompt
    if 'patterns' in locals() and patterns:
        print("4. Formatting patterns for LLM prompt...")
        formatted = agent.format_patterns_for_prompt(patterns, max_patterns=2)
        print(formatted)
    
    print("✅ Memory Agent test complete!")
