-- Migration: 002_add_vector_support
-- Description: Add pgvector extension and patterns table for semantic memory
-- Date: 2025-12-06
-- Phase: 6 (Production Integration) - Step 3

-- ============================================================================
-- STEP 1: Install pgvector extension
-- ============================================================================

-- Enable pgvector for vector similarity search
-- This extension provides the 'vector' type and distance operators
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'vector'
    ) THEN
        RAISE EXCEPTION 'pgvector extension failed to install';
    END IF;
END $$;

-- ============================================================================
-- STEP 2: Create patterns table
-- ============================================================================

-- The patterns table stores learned semantic patterns for reuse
-- Each pattern has a vector embedding for similarity search
CREATE TABLE patterns (
    -- Primary identification
    pattern_id VARCHAR(64) PRIMARY KEY,  -- Deterministic hash: SHA256(content + created_at)
    
    -- Vector embedding (1536 dimensions for OpenAI text-embedding-ada-002)
    embedding vector(1536) NOT NULL,
    
    -- Pattern classification
    pattern_type VARCHAR(50) NOT NULL,
    -- 'template'              - Reusable starting point for common apps
    -- 'style'                 - Coding or architectural preference
    -- 'intent'                - User goal or desired outcome
    -- 'system_upgrade_proposal' - Proposed improvement to control plane
    -- 'migration_plan'        - Strategy for moving between states
    -- 'error_repair'          - Known failure + successful recovery
    
    -- Content and metadata
    natural_language_description TEXT NOT NULL,  -- Human-readable description
    content JSONB NOT NULL,  -- Pattern details (plan, code, config, etc.)
    
    -- Lineage (links to source operation)
    source_operation_id VARCHAR(64) REFERENCES operations(operation_id),
    source_plan_hash VARCHAR(64),
    
    -- Application context
    app_type VARCHAR(50),  -- 'static', 'dynamic', 'hybrid'
    gcp_services_used TEXT[],  -- Array of GCP service types
    
    -- Quality metrics
    success_score FLOAT NOT NULL DEFAULT 1.0,  -- 0-1 (0 = failure, 1 = perfect success)
    usage_count INTEGER NOT NULL DEFAULT 0,  -- How many times reused
    last_used_at TIMESTAMP,
    
    -- Versioning
    system_version VARCHAR(50) NOT NULL,  -- Control plane version that created this
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,  -- Soft delete
    
    -- Tags for filtering
    tags TEXT[],
    
    -- Additional flexible metadata
    metadata JSONB,
    
    -- Constraints
    CONSTRAINT pattern_type_check CHECK (pattern_type IN (
        'template', 'style', 'intent', 'system_upgrade_proposal', 
        'migration_plan', 'error_repair'
    )),
    CONSTRAINT success_score_range CHECK (success_score >= 0.0 AND success_score <= 1.0),
    CONSTRAINT usage_count_non_negative CHECK (usage_count >= 0)
);

-- ============================================================================
-- STEP 3: Create indexes
-- ============================================================================

-- HNSW index for fast approximate nearest neighbor search
-- This is the key index for semantic similarity queries
-- Using cosine distance (most common for text embeddings)
CREATE INDEX idx_patterns_embedding_cosine ON patterns 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Alternative: IVFFlat index (less accurate but faster to build)
-- Uncomment if HNSW is too slow for your dataset size
-- CREATE INDEX idx_patterns_embedding_ivfflat ON patterns 
-- USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);

-- Standard B-tree indexes for filtering
CREATE INDEX idx_patterns_type ON patterns(pattern_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_patterns_app_type ON patterns(app_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_patterns_success_score ON patterns(success_score DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_patterns_usage_count ON patterns(usage_count DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_patterns_created_at ON patterns(created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_patterns_last_used ON patterns(last_used_at DESC) WHERE last_used_at IS NOT NULL;

-- GIN index for array columns (tags, gcp_services_used)
CREATE INDEX idx_patterns_tags ON patterns USING GIN(tags) WHERE deleted_at IS NULL;
CREATE INDEX idx_patterns_gcp_services ON patterns USING GIN(gcp_services_used) WHERE deleted_at IS NULL;

-- GIN index for JSONB metadata
CREATE INDEX idx_patterns_metadata ON patterns USING GIN(metadata) WHERE deleted_at IS NULL;

-- Foreign key index for operations
CREATE INDEX idx_patterns_source_operation ON patterns(source_operation_id) WHERE source_operation_id IS NOT NULL;

-- ============================================================================
-- STEP 4: Update operations table
-- ============================================================================

-- Add index on vector_embedding_id for reverse lookup
-- (This index may already exist from migration 001, but we add it here for completeness)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND indexname = 'idx_operations_embedding_lookup'
    ) THEN
        CREATE INDEX idx_operations_embedding_lookup ON operations(vector_embedding_id) 
        WHERE vector_embedding_id IS NOT NULL;
    END IF;
END $$;

-- ============================================================================
-- STEP 5: Create helper functions
-- ============================================================================

-- Function to search for similar patterns
-- This wraps the vector similarity search for convenience
CREATE OR REPLACE FUNCTION search_similar_patterns(
    query_embedding vector(1536),
    similarity_threshold FLOAT DEFAULT 0.7,
    result_limit INTEGER DEFAULT 10,
    filter_pattern_type VARCHAR DEFAULT NULL,
    filter_app_type VARCHAR DEFAULT NULL,
    min_success_score FLOAT DEFAULT 0.5
)
RETURNS TABLE (
    pattern_id VARCHAR,
    similarity_score FLOAT,
    pattern_type VARCHAR,
    natural_language_description TEXT,
    success_score FLOAT,
    usage_count INTEGER,
    content JSONB,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.pattern_id,
        1 - (p.embedding <=> query_embedding) AS similarity_score,  -- Cosine similarity
        p.pattern_type,
        p.natural_language_description,
        p.success_score,
        p.usage_count,
        p.content,
        p.metadata
    FROM patterns p
    WHERE p.deleted_at IS NULL
        AND (1 - (p.embedding <=> query_embedding)) >= similarity_threshold
        AND (filter_pattern_type IS NULL OR p.pattern_type = filter_pattern_type)
        AND (filter_app_type IS NULL OR p.app_type = filter_app_type)
        AND p.success_score >= min_success_score
    ORDER BY p.embedding <=> query_embedding  -- Order by distance (ascending)
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to increment usage count when a pattern is reused
CREATE OR REPLACE FUNCTION increment_pattern_usage(
    p_pattern_id VARCHAR
)
RETURNS VOID AS $$
BEGIN
    UPDATE patterns
    SET usage_count = usage_count + 1,
        last_used_at = NOW(),
        updated_at = NOW()
    WHERE pattern_id = p_pattern_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 6: Create trigger for updated_at timestamp
-- ============================================================================

-- Automatically update updated_at timestamp on pattern modifications
CREATE OR REPLACE FUNCTION update_patterns_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_patterns_updated_at
    BEFORE UPDATE ON patterns
    FOR EACH ROW
    EXECUTE FUNCTION update_patterns_timestamp();

-- ============================================================================
-- STEP 7: Grant permissions
-- ============================================================================

-- Grant permissions to application user (if exists)
-- In production, you'll want to create a dedicated user with limited permissions
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_control_plane_app') THEN
        GRANT SELECT, INSERT, UPDATE ON patterns TO ai_control_plane_app;
        GRANT EXECUTE ON FUNCTION search_similar_patterns TO ai_control_plane_app;
        GRANT EXECUTE ON FUNCTION increment_pattern_usage TO ai_control_plane_app;
    END IF;
END $$;

-- ============================================================================
-- STEP 8: Insert schema version
-- ============================================================================

INSERT INTO schema_versions (version_number, description, applied_at)
VALUES (2, 'Add pgvector extension and patterns table for semantic memory', NOW());

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify extension is installed
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Verify patterns table exists
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'patterns';

-- Verify indexes exist
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' AND tablename = 'patterns'
ORDER BY indexname;

-- Verify functions exist
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public' 
AND routine_name IN ('search_similar_patterns', 'increment_pattern_usage');

-- Display migration summary
SELECT 
    'Migration 002 completed successfully' AS status,
    COUNT(*) AS pattern_count,
    (SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector') AS vector_extension_installed
FROM patterns;
