-- AI-Native Control Plane - Rollback Initial Database Schema
-- Migration Rollback: 001_initial_schema
-- Created: 2025-12-06
-- Description: Rollback script to undo initial schema migration

-- =============================================================================
-- DROP TABLES IN REVERSE ORDER (respecting foreign keys)
-- =============================================================================

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS schema_versions CASCADE;
DROP TABLE IF EXISTS policies CASCADE;
DROP TABLE IF EXISTS operations CASCADE;
DROP TABLE IF EXISTS plan_versions CASCADE;
DROP TABLE IF EXISTS infra_objects CASCADE;
DROP TABLE IF EXISTS apps CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =============================================================================
-- DROP EXTENSIONS
-- =============================================================================

DROP EXTENSION IF EXISTS "btree_gin";
DROP EXTENSION IF EXISTS "pg_trgm";
DROP EXTENSION IF EXISTS "uuid-ossp";

-- =============================================================================
-- REVOKE PERMISSIONS
-- =============================================================================

-- Revoke permissions from application user
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM ai_control_plane_app;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM ai_control_plane_app;
REVOKE USAGE ON SCHEMA public FROM ai_control_plane_app;
REVOKE CONNECT ON DATABASE postgres FROM ai_control_plane_app;

-- Drop application user role (optional - comment out if you want to preserve it)
-- DROP ROLE IF EXISTS ai_control_plane_app;

-- =============================================================================
-- ROLLBACK COMPLETE
-- =============================================================================

SELECT 'Rollback of 001_initial_schema completed successfully' AS status;
