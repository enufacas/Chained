"""
Vector Database Operations Module

This module provides utilities for working with vector embeddings in the state-db.
It handles:
- Embedding generation (using OpenAI or local models)
- Pattern storage with vector embeddings
- Semantic similarity search
- Pattern retrieval and ranking

Dependencies:
- pgvector extension in PostgreSQL
- OpenAI API (or alternative embedding provider)
- psycopg2 for database connection

Author: AI-Native Control Plane
Date: 2025-12-06
Phase: 6 (Production Integration) - Step 3
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Optional dependencies - graceful fallback if not installed
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from db import get_connection, execute_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI model
EMBEDDING_DIMENSION = 1536  # OpenAI ada-002 dimension
LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"  # Lightweight local model (384 dimensions)

# Cache for local models (lazy loading)
_local_model_cache: Optional[Any] = None


def generate_embedding(text: str, provider: str = "openai") -> List[float]:
    """
    Generate vector embedding for given text.
    
    Args:
        text: Input text to embed
        provider: Embedding provider ('openai' or 'local')
        
    Returns:
        List of floats representing the embedding vector
        
    Raises:
        ValueError: If provider is invalid or API keys are missing
        RuntimeError: If embedding generation fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if provider == "openai":
        return _generate_openai_embedding(text)
    elif provider == "local":
        return _generate_local_embedding(text)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")


def _generate_openai_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI API."""
    if not OPENAI_AVAILABLE:
        raise RuntimeError(
            "OpenAI library not installed. Install with: pip install openai"
        )
    
    try:
        client = openai.OpenAI()  # Uses OPENAI_API_KEY env var
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        embedding = response.data[0].embedding
        
        # Validate dimension
        if len(embedding) != EMBEDDING_DIMENSION:
            raise RuntimeError(
                f"Expected {EMBEDDING_DIMENSION} dimensions, got {len(embedding)}"
            )
        
        return embedding
        
    except Exception as e:
        logger.error(f"OpenAI embedding generation failed: {e}")
        raise RuntimeError(f"Failed to generate OpenAI embedding: {e}")


def _generate_local_embedding(text: str) -> List[float]:
    """Generate embedding using local sentence-transformers model."""
    global _local_model_cache
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise RuntimeError(
            "sentence-transformers not installed. "
            "Install with: pip install sentence-transformers"
        )
    
    try:
        # Lazy load model (only load once)
        if _local_model_cache is None:
            logger.info(f"Loading local embedding model: {LOCAL_MODEL_NAME}")
            _local_model_cache = SentenceTransformer(LOCAL_MODEL_NAME)
        
        embedding = _local_model_cache.encode(text, convert_to_numpy=True)
        
        # Convert to list and pad/truncate to match expected dimension
        embedding_list = embedding.tolist()
        
        # For local models, we may need to adjust dimension
        # This is a simple strategy - in production you might want to use
        # a model that matches your vector dimension or use dimensionality reduction
        if len(embedding_list) < EMBEDDING_DIMENSION:
            # Pad with zeros
            embedding_list.extend([0.0] * (EMBEDDING_DIMENSION - len(embedding_list)))
        elif len(embedding_list) > EMBEDDING_DIMENSION:
            # Truncate
            embedding_list = embedding_list[:EMBEDDING_DIMENSION]
        
        return embedding_list
        
    except Exception as e:
        logger.error(f"Local embedding generation failed: {e}")
        raise RuntimeError(f"Failed to generate local embedding: {e}")


def generate_pattern_id(description: str, created_at: datetime) -> str:
    """
    Generate deterministic pattern ID from description and timestamp.
    
    Args:
        description: Natural language description
        created_at: Creation timestamp
        
    Returns:
        SHA256 hash as hex string (64 characters)
    """
    content = f"{description}:{created_at.isoformat()}"
    return hashlib.sha256(content.encode()).hexdigest()


def store_pattern(
    pattern_type: str,
    natural_language_description: str,
    content: Dict[str, Any],
    embedding: Optional[List[float]] = None,
    source_operation_id: Optional[str] = None,
    source_plan_hash: Optional[str] = None,
    app_type: Optional[str] = None,
    gcp_services_used: Optional[List[str]] = None,
    success_score: float = 1.0,
    system_version: str = "v0.1.0",
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    embedding_provider: str = "openai"
) -> str:
    """
    Store a pattern with its vector embedding in the database.
    
    Args:
        pattern_type: Type of pattern (template, style, intent, etc.)
        natural_language_description: Human-readable description
        content: Pattern details as JSONB
        embedding: Pre-computed embedding (if None, will be generated)
        source_operation_id: Optional link to source operation
        source_plan_hash: Optional link to source plan
        app_type: Optional application type
        gcp_services_used: Optional list of GCP services
        success_score: Quality metric (0-1)
        system_version: Control plane version
        tags: Optional list of tags
        metadata: Optional additional metadata
        embedding_provider: Provider to use if generating embedding
        
    Returns:
        Pattern ID (SHA256 hash)
        
    Raises:
        ValueError: If pattern_type is invalid or required fields are missing
        RuntimeError: If storage fails
    """
    # Validate pattern type
    valid_types = [
        'template', 'style', 'intent', 
        'system_upgrade_proposal', 'migration_plan', 'error_repair'
    ]
    if pattern_type not in valid_types:
        raise ValueError(
            f"Invalid pattern_type: {pattern_type}. Must be one of {valid_types}"
        )
    
    # Generate embedding if not provided
    if embedding is None:
        logger.info(f"Generating embedding for pattern: {natural_language_description[:50]}...")
        embedding = generate_embedding(natural_language_description, embedding_provider)
    
    # Validate embedding dimension
    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Embedding dimension mismatch: expected {EMBEDDING_DIMENSION}, got {len(embedding)}"
        )
    
    # Generate deterministic ID
    created_at = datetime.utcnow()
    pattern_id = generate_pattern_id(natural_language_description, created_at)
    
    # Prepare SQL
    query = """
    INSERT INTO patterns (
        pattern_id, embedding, pattern_type, natural_language_description, content,
        source_operation_id, source_plan_hash, app_type, gcp_services_used,
        success_score, system_version, created_at, updated_at, tags, metadata
    ) VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (pattern_id) DO NOTHING
    RETURNING pattern_id;
    """
    
    params = (
        pattern_id,
        embedding,  # pgvector handles list conversion
        pattern_type,
        natural_language_description,
        json.dumps(content),
        source_operation_id,
        source_plan_hash,
        app_type,
        gcp_services_used,
        success_score,
        system_version,
        created_at,
        created_at,  # updated_at
        tags,
        json.dumps(metadata) if metadata else None
    )
    
    try:
        with get_connection() as conn:
            result = execute_query(conn, query, params, fetch=True)
            if not result:
                logger.warning(f"Pattern {pattern_id} already exists, skipping insert")
            else:
                logger.info(f"Stored pattern {pattern_id} ({pattern_type})")
        
        return pattern_id
        
    except Exception as e:
        logger.error(f"Failed to store pattern: {e}")
        raise RuntimeError(f"Pattern storage failed: {e}")


def search_similar_patterns(
    query_text: str,
    top_k: int = 10,
    similarity_threshold: float = 0.7,
    filter_pattern_type: Optional[str] = None,
    filter_app_type: Optional[str] = None,
    min_success_score: float = 0.5,
    embedding_provider: str = "openai"
) -> List[Dict[str, Any]]:
    """
    Search for patterns similar to the query text.
    
    Args:
        query_text: Natural language query
        top_k: Number of results to return
        similarity_threshold: Minimum cosine similarity (0-1)
        filter_pattern_type: Optional pattern type filter
        filter_app_type: Optional app type filter
        min_success_score: Minimum success score filter
        embedding_provider: Provider for embedding generation
        
    Returns:
        List of pattern dictionaries with similarity scores
        
    Example:
        >>> results = search_similar_patterns(
        ...     "Create a blog with authentication",
        ...     top_k=5,
        ...     filter_pattern_type='template'
        ... )
        >>> for pattern in results:
        ...     print(f"{pattern['similarity_score']:.2f} - {pattern['description']}")
    """
    # Generate query embedding
    logger.info(f"Searching for patterns similar to: {query_text[:50]}...")
    query_embedding = generate_embedding(query_text, embedding_provider)
    
    # Use the search_similar_patterns PostgreSQL function
    query = """
    SELECT * FROM search_similar_patterns(
        %s::vector,  -- query_embedding
        %s,          -- similarity_threshold
        %s,          -- result_limit
        %s,          -- filter_pattern_type
        %s,          -- filter_app_type
        %s           -- min_success_score
    );
    """
    
    params = (
        query_embedding,
        similarity_threshold,
        top_k,
        filter_pattern_type,
        filter_app_type,
        min_success_score
    )
    
    try:
        with get_connection() as conn:
            results = execute_query(conn, query, params, fetch=True)
            
            if not results:
                logger.info("No similar patterns found")
                return []
            
            # Convert to list of dicts
            patterns = []
            for row in results:
                patterns.append({
                    'pattern_id': row[0],
                    'similarity_score': float(row[1]),
                    'pattern_type': row[2],
                    'description': row[3],
                    'success_score': float(row[4]),
                    'usage_count': int(row[5]),
                    'content': row[6],
                    'metadata': row[7]
                })
            
            logger.info(f"Found {len(patterns)} similar patterns")
            return patterns
            
    except Exception as e:
        logger.error(f"Pattern search failed: {e}")
        raise RuntimeError(f"Failed to search patterns: {e}")


def increment_pattern_usage(pattern_id: str) -> None:
    """
    Increment the usage count for a pattern.
    
    This should be called whenever a pattern is successfully reused
    to track which patterns are most valuable.
    
    Args:
        pattern_id: ID of the pattern to increment
    """
    query = "SELECT increment_pattern_usage(%s);"
    
    try:
        with get_connection() as conn:
            execute_query(conn, query, (pattern_id,))
            logger.info(f"Incremented usage count for pattern {pattern_id}")
            
    except Exception as e:
        logger.error(f"Failed to increment pattern usage: {e}")
        # Don't raise - this is not critical


def get_pattern(pattern_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific pattern by ID.
    
    Args:
        pattern_id: Pattern ID to retrieve
        
    Returns:
        Pattern dictionary or None if not found
    """
    query = """
    SELECT 
        pattern_id, pattern_type, natural_language_description,
        content, source_operation_id, source_plan_hash,
        app_type, gcp_services_used, success_score, usage_count,
        last_used_at, system_version, created_at, updated_at,
        tags, metadata
    FROM patterns
    WHERE pattern_id = %s AND deleted_at IS NULL;
    """
    
    try:
        with get_connection() as conn:
            result = execute_query(conn, query, (pattern_id,), fetch=True)
            
            if not result:
                return None
            
            row = result[0]
            return {
                'pattern_id': row[0],
                'pattern_type': row[1],
                'description': row[2],
                'content': row[3],
                'source_operation_id': row[4],
                'source_plan_hash': row[5],
                'app_type': row[6],
                'gcp_services_used': row[7],
                'success_score': float(row[8]),
                'usage_count': int(row[9]),
                'last_used_at': row[10],
                'system_version': row[11],
                'created_at': row[12],
                'updated_at': row[13],
                'tags': row[14],
                'metadata': row[15]
            }
            
    except Exception as e:
        logger.error(f"Failed to get pattern: {e}")
        return None


def list_patterns(
    pattern_type: Optional[str] = None,
    app_type: Optional[str] = None,
    min_success_score: float = 0.0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    List patterns with optional filters.
    
    Args:
        pattern_type: Optional pattern type filter
        app_type: Optional app type filter
        min_success_score: Minimum success score
        limit: Maximum number of results
        
    Returns:
        List of pattern dictionaries
    """
    query = """
    SELECT 
        pattern_id, pattern_type, natural_language_description,
        success_score, usage_count, created_at, tags
    FROM patterns
    WHERE deleted_at IS NULL
        AND ($1::VARCHAR IS NULL OR pattern_type = $1)
        AND ($2::VARCHAR IS NULL OR app_type = $2)
        AND success_score >= $3
    ORDER BY usage_count DESC, success_score DESC, created_at DESC
    LIMIT $4;
    """
    
    try:
        with get_connection() as conn:
            results = execute_query(
                conn, query, 
                (pattern_type, app_type, min_success_score, limit),
                fetch=True
            )
            
            patterns = []
            for row in results:
                patterns.append({
                    'pattern_id': row[0],
                    'pattern_type': row[1],
                    'description': row[2],
                    'success_score': float(row[3]),
                    'usage_count': int(row[4]),
                    'created_at': row[5],
                    'tags': row[6]
                })
            
            return patterns
            
    except Exception as e:
        logger.error(f"Failed to list patterns: {e}")
        return []


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    """
    Example usage demonstrating vector operations.
    
    Prerequisites:
    - PostgreSQL with pgvector extension installed
    - Migration 002 applied
    - OPENAI_API_KEY environment variable set (or use provider='local')
    """
    
    print("🧪 Testing Vector Operations\n")
    
    # Example 1: Store a pattern
    print("1. Storing a sample pattern...")
    try:
        pattern_id = store_pattern(
            pattern_type='template',
            natural_language_description='Deploy a static blog site with posts and categories',
            content={
                'plan_steps': [
                    'Create GCS bucket',
                    'Generate HTML files',
                    'Upload to bucket',
                    'Configure public access'
                ],
                'estimated_duration_seconds': 60,
                'required_resources': ['gcs_bucket']
            },
            app_type='static',
            gcp_services_used=['gcs'],
            success_score=0.95,
            tags=['blog', 'static', 'simple'],
            embedding_provider='openai'  # or 'local' if no API key
        )
        print(f"✅ Stored pattern: {pattern_id}\n")
    except Exception as e:
        print(f"❌ Failed to store pattern: {e}\n")
    
    # Example 2: Search for similar patterns
    print("2. Searching for similar patterns...")
    try:
        results = search_similar_patterns(
            query_text='Create a news website',
            top_k=3,
            filter_pattern_type='template',
            embedding_provider='openai'  # or 'local'
        )
        
        if results:
            print(f"Found {len(results)} similar patterns:")
            for i, pattern in enumerate(results, 1):
                print(f"  {i}. [{pattern['similarity_score']:.2f}] {pattern['description']}")
                print(f"     Type: {pattern['pattern_type']}, Score: {pattern['success_score']:.2f}")
        else:
            print("No similar patterns found")
        print()
    except Exception as e:
        print(f"❌ Search failed: {e}\n")
    
    # Example 3: Increment usage count
    if 'pattern_id' in locals():
        print("3. Incrementing pattern usage...")
        try:
            increment_pattern_usage(pattern_id)
            print("✅ Usage count incremented\n")
        except Exception as e:
            print(f"❌ Failed to increment: {e}\n")
    
    print("✅ Vector operations test complete!")
