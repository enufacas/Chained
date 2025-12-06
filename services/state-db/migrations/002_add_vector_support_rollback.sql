-- Rollback Migration: 002_add_vector_support
-- Description: Remove pgvector extension and patterns table
-- Date: 2025-12-06

-- ============================================================================
-- STEP 1: Drop triggers
-- ============================================================================

DROP TRIGGER IF EXISTS trigger_patterns_updated_at ON patterns;
DROP FUNCTION IF EXISTS update_patterns_timestamp();

-- ============================================================================
-- STEP 2: Drop helper functions
-- ============================================================================

DROP FUNCTION IF EXISTS search_similar_patterns(vector, FLOAT, INTEGER, VARCHAR, VARCHAR, FLOAT);
DROP FUNCTION IF EXISTS increment_pattern_usage(VARCHAR);

-- ============================================================================
-- STEP 3: Drop patterns table (cascades to indexes)
-- ============================================================================

DROP TABLE IF EXISTS patterns CASCADE;

-- ============================================================================
-- STEP 4: Drop pgvector extension
-- ============================================================================

-- Note: Be careful with this in production!
-- Other tables might be using pgvector.
-- Only drop if you're sure no other tables depend on it.
DROP EXTENSION IF EXISTS vector CASCADE;

-- ============================================================================
-- STEP 5: Remove schema version entry
-- ============================================================================

DELETE FROM schema_versions WHERE version_number = 2;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify patterns table is dropped
SELECT COUNT(*) AS patterns_table_exists
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'patterns';
-- Should return 0

-- Verify extension is dropped
SELECT COUNT(*) AS vector_extension_exists
FROM pg_extension WHERE extname = 'vector';
-- Should return 0

-- Display rollback summary
SELECT 'Migration 002 rolled back successfully' AS status;
