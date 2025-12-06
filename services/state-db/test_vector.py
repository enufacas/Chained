#!/usr/bin/env python3
"""
Test script for vector database operations.

This script tests:
1. Migration 002 has been applied
2. Pattern storage works
3. Embedding generation works
4. Semantic search works
5. Memory Agent integration works

Run this after applying migration 002 to verify vector DB is working.

Prerequisites:
- PostgreSQL running locally or Cloud SQL connection
- Migration 002 applied
- OPENAI_API_KEY set (or use --provider=local for local embeddings)

Usage:
    python test_vector.py
    python test_vector.py --provider=local  # Use local embeddings
"""

import argparse
import logging
import os
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test database connection
def test_db_connection():
    """Test that database connection works."""
    logger.info("Testing database connection...")
    try:
        from db import get_connection
        with get_connection() as conn:
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def test_pgvector_extension():
    """Test that pgvector extension is installed."""
    logger.info("Testing pgvector extension...")
    try:
        from db import execute_query, get_connection
        query = "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
        with get_connection() as conn:
            result = execute_query(conn, query, fetch=True)
            if result and len(result) > 0:
                logger.info(f"✅ pgvector extension installed: version {result[0][1]}")
                return True
            else:
                logger.error("❌ pgvector extension not found")
                return False
    except Exception as e:
        logger.error(f"❌ pgvector check failed: {e}")
        return False


def test_patterns_table():
    """Test that patterns table exists."""
    logger.info("Testing patterns table...")
    try:
        from db import execute_query, get_connection
        query = """
        SELECT table_name, table_type 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'patterns';
        """
        with get_connection() as conn:
            result = execute_query(conn, query, fetch=True)
            if result and len(result) > 0:
                logger.info("✅ patterns table exists")
                return True
            else:
                logger.error("❌ patterns table not found")
                return False
    except Exception as e:
        logger.error(f"❌ patterns table check failed: {e}")
        return False


def test_embedding_generation(provider='openai'):
    """Test embedding generation."""
    logger.info(f"Testing embedding generation (provider={provider})...")
    try:
        from vector import generate_embedding
        
        test_text = "Create a blog website with user authentication"
        embedding = generate_embedding(test_text, provider=provider)
        
        if len(embedding) == 1536:
            logger.info(f"✅ Generated embedding: {len(embedding)} dimensions")
            return True, embedding
        else:
            logger.error(f"❌ Unexpected embedding dimension: {len(embedding)}")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        return False, None


def test_pattern_storage(provider='openai'):
    """Test storing a pattern."""
    logger.info("Testing pattern storage...")
    try:
        from vector import store_pattern
        
        pattern_id = store_pattern(
            pattern_type='template',
            natural_language_description='Deploy a simple static blog site with posts and categories',
            content={
                'plan_steps': [
                    'Create GCS bucket with unique name',
                    'Generate HTML files for blog',
                    'Upload files to bucket',
                    'Configure bucket for public access'
                ],
                'estimated_duration_seconds': 60,
                'required_resources': ['gcs_bucket'],
                'gcp_services': ['Cloud Storage']
            },
            app_type='static',
            gcp_services_used=['gcs'],
            success_score=0.95,
            tags=['blog', 'static', 'simple', 'test'],
            metadata={'test': True, 'created_by': 'test_script'},
            embedding_provider=provider
        )
        
        logger.info(f"✅ Stored pattern: {pattern_id}")
        return True, pattern_id
        
    except Exception as e:
        logger.error(f"❌ Pattern storage failed: {e}")
        return False, None


def test_semantic_search(provider='openai'):
    """Test semantic similarity search."""
    logger.info("Testing semantic search...")
    try:
        from vector import search_similar_patterns
        
        # Search for patterns similar to a blog site
        results = search_similar_patterns(
            query_text="Create a news website",
            top_k=5,
            similarity_threshold=0.5,
            filter_pattern_type='template',
            embedding_provider=provider
        )
        
        if results:
            logger.info(f"✅ Found {len(results)} similar patterns:")
            for i, pattern in enumerate(results[:3], 1):
                logger.info(
                    f"   {i}. [{pattern['similarity_score']:.3f}] "
                    f"{pattern['description'][:60]}..."
                )
            return True, results
        else:
            logger.warning("⚠️ No patterns found (this is OK if database is empty)")
            return True, []
            
    except Exception as e:
        logger.error(f"❌ Semantic search failed: {e}")
        return False, None


def test_pattern_usage_increment(pattern_id):
    """Test incrementing pattern usage count."""
    logger.info("Testing pattern usage increment...")
    try:
        from vector import increment_pattern_usage
        
        increment_pattern_usage(pattern_id)
        logger.info(f"✅ Incremented usage count for pattern {pattern_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Usage increment failed: {e}")
        return False


def test_memory_agent(provider='openai'):
    """Test Memory Agent integration."""
    logger.info("Testing Memory Agent...")
    try:
        from memory import MemoryAgent
        
        agent = MemoryAgent(
            embedding_provider=provider,
            system_version='v0.1.0-test'
        )
        
        # Test pattern retrieval
        patterns = agent.retrieve_relevant_patterns(
            user_request="Create a blog platform with authentication",
            intent='create_app',
            context={'app_type': 'static'},
            top_k=3
        )
        
        logger.info(f"✅ Memory Agent retrieved {len(patterns)} patterns")
        
        # Test pattern learning
        operation_result = {
            'user_request': 'Deploy a test portfolio website',
            'plan': {
                'plan_steps': ['Create bucket', 'Upload files'],
                'estimated_duration_seconds': 30
            },
            'operation_id': 'op_test_memory_agent',
            'app_type': 'static',
            'success_score': 0.9,
            'tags': ['test', 'portfolio']
        }
        
        pattern_id = agent.learn_from_operation(operation_result)
        if pattern_id:
            logger.info(f"✅ Memory Agent learned pattern: {pattern_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory Agent test failed: {e}")
        return False


def cleanup_test_patterns():
    """Remove test patterns created during testing."""
    logger.info("Cleaning up test patterns...")
    try:
        from db import execute_query, get_connection
        
        query = """
        DELETE FROM patterns 
        WHERE metadata->>'test' = 'true' 
        OR tags @> ARRAY['test'];
        """
        
        with get_connection() as conn:
            execute_query(conn, query)
            logger.info("✅ Cleaned up test patterns")
            
    except Exception as e:
        logger.warning(f"⚠️ Cleanup failed (non-critical): {e}")


def main():
    """Run all vector database tests."""
    parser = argparse.ArgumentParser(description='Test vector database operations')
    parser.add_argument(
        '--provider',
        choices=['openai', 'local'],
        default='openai',
        help='Embedding provider (default: openai)'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up test patterns after testing'
    )
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🧪 Vector Database Test Suite")
    print("="*70 + "\n")
    
    # Check for API key if using OpenAI
    if args.provider == 'openai' and not os.getenv('OPENAI_API_KEY'):
        logger.warning(
            "⚠️ OPENAI_API_KEY not set. "
            "Use --provider=local for local embeddings or set API key."
        )
        return 1
    
    results = {}
    
    # Run tests
    results['db_connection'] = test_db_connection()
    if not results['db_connection']:
        logger.error("❌ Cannot proceed without database connection")
        return 1
    
    results['pgvector'] = test_pgvector_extension()
    if not results['pgvector']:
        logger.error("❌ pgvector extension required. Run migration 002 first.")
        return 1
    
    results['patterns_table'] = test_patterns_table()
    if not results['patterns_table']:
        logger.error("❌ patterns table required. Run migration 002 first.")
        return 1
    
    success, embedding = test_embedding_generation(args.provider)
    results['embedding'] = success
    
    if results['embedding']:
        success, pattern_id = test_pattern_storage(args.provider)
        results['storage'] = success
        
        if results['storage']:
            success, search_results = test_semantic_search(args.provider)
            results['search'] = success
            
            if pattern_id:
                results['usage_increment'] = test_pattern_usage_increment(pattern_id)
    
    results['memory_agent'] = test_memory_agent(args.provider)
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    # Cleanup
    if args.cleanup:
        cleanup_test_patterns()
    
    print("="*70 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
