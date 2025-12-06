-- AI-Native Control Plane - Initial Database Schema
-- Migration: 001_initial_schema
-- Created: 2025-12-06
-- Description: Production-ready database schema for state-db (PostgreSQL/Cloud SQL)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- For JSONB indexing

-- =============================================================================
-- USERS TABLE
-- =============================================================================

CREATE TABLE users (
    user_id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'developer',
    CONSTRAINT role_check CHECK (role IN ('admin', 'developer', 'viewer'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE users IS 'User accounts and authentication';
COMMENT ON COLUMN users.user_id IS 'Deterministic hash from identity provider';
COMMENT ON COLUMN users.role IS 'User role: admin (full control), developer (create/update), viewer (read-only)';

-- =============================================================================
-- APPS TABLE
-- =============================================================================

CREATE TABLE apps (
    app_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    app_type VARCHAR(50) NOT NULL,
    owner_user_id VARCHAR(64) NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    metadata JSONB,
    current_version VARCHAR(64),
    CONSTRAINT app_type_check CHECK (app_type IN ('static', 'dynamic', 'hybrid')),
    CONSTRAINT status_check CHECK (status IN ('draft', 'deploying', 'active', 'failed', 'archived'))
);

CREATE INDEX idx_apps_owner ON apps(owner_user_id);
CREATE INDEX idx_apps_status ON apps(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_apps_name ON apps(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_apps_metadata ON apps USING GIN (metadata);

COMMENT ON TABLE apps IS 'Applications managed by the control plane';
COMMENT ON COLUMN apps.app_id IS 'Deterministic SHA256(name + creation_timestamp)';
COMMENT ON COLUMN apps.app_type IS 'static (GCS), dynamic (Cloud Run), or hybrid';
COMMENT ON COLUMN apps.current_version IS 'References plan_versions(version_hash)';
COMMENT ON COLUMN apps.metadata IS 'Flexible JSONB for tags, custom fields';

-- =============================================================================
-- INFRA_OBJECTS TABLE
-- =============================================================================

CREATE TABLE infra_objects (
    object_id VARCHAR(64) PRIMARY KEY,
    app_id VARCHAR(64) NOT NULL REFERENCES apps(app_id),
    object_type VARCHAR(100) NOT NULL,
    gcp_resource_name VARCHAR(500) NOT NULL,
    gcp_resource_id VARCHAR(500),
    region VARCHAR(50),
    configuration JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    health_status VARCHAR(50),
    last_health_check TIMESTAMP,
    CONSTRAINT object_type_check CHECK (object_type IN ('gcs_bucket', 'cloud_run_service', 'domain_mapping', 'cdn', 'database', 'secret', 'load_balancer'))
);

CREATE INDEX idx_infra_app ON infra_objects(app_id);
CREATE INDEX idx_infra_type ON infra_objects(object_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_infra_health ON infra_objects(health_status) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_infra_gcp_name ON infra_objects(gcp_resource_name) WHERE deleted_at IS NULL;
CREATE INDEX idx_infra_config ON infra_objects USING GIN (configuration);

COMMENT ON TABLE infra_objects IS 'GCP infrastructure resources created by control plane';
COMMENT ON COLUMN infra_objects.object_id IS 'Deterministic hash';
COMMENT ON COLUMN infra_objects.gcp_resource_name IS 'Full GCP resource name (e.g., projects/my-project/buckets/my-bucket)';
COMMENT ON COLUMN infra_objects.configuration IS 'Complete JSONB snapshot of resource config';

-- =============================================================================
-- PLAN_VERSIONS TABLE
-- =============================================================================

CREATE TABLE plan_versions (
    version_hash VARCHAR(64) PRIMARY KEY,
    app_id VARCHAR(64) NOT NULL REFERENCES apps(app_id),
    plan_content JSONB NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by_actor_type VARCHAR(50) NOT NULL,
    created_by_actor_id VARCHAR(64) NOT NULL,
    validated_at TIMESTAMP,
    validation_status VARCHAR(50),
    validation_errors JSONB,
    executed_at TIMESTAMP,
    execution_operation_id VARCHAR(64),
    CONSTRAINT plan_type_check CHECK (plan_type IN ('initial_deploy', 'update', 'scale', 'migration')),
    CONSTRAINT validation_status_check CHECK (validation_status IN ('pending', 'valid', 'invalid'))
);

CREATE INDEX idx_plans_app ON plan_versions(app_id);
CREATE INDEX idx_plans_created ON plan_versions(created_at DESC);
CREATE INDEX idx_plans_validation ON plan_versions(validation_status);
CREATE INDEX idx_plans_content ON plan_versions USING GIN (plan_content);

COMMENT ON TABLE plan_versions IS 'Validated plans before execution';
COMMENT ON COLUMN plan_versions.version_hash IS 'SHA256 of plan content';
COMMENT ON COLUMN plan_versions.plan_content IS 'Complete plan specification (JSONB)';

-- =============================================================================
-- OPERATIONS TABLE (Event Log)
-- =============================================================================

CREATE TABLE operations (
    operation_id VARCHAR(64) PRIMARY KEY,
    operation_type VARCHAR(100) NOT NULL,
    actor_type VARCHAR(50) NOT NULL,
    actor_id VARCHAR(64) NOT NULL,
    app_id VARCHAR(64) REFERENCES apps(app_id),
    plan_hash VARCHAR(64) NOT NULL,
    object_id VARCHAR(64) REFERENCES infra_objects(object_id),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    before_snapshot JSONB,
    after_snapshot JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    parent_operation_id VARCHAR(64) REFERENCES operations(operation_id),
    vector_embedding_id VARCHAR(64),
    metadata JSONB,
    CONSTRAINT actor_type_check CHECK (actor_type IN ('user', 'ai_agent', 'system')),
    CONSTRAINT status_check CHECK (status IN ('pending', 'running', 'success', 'failed', 'rolled_back'))
);

CREATE INDEX idx_operations_app ON operations(app_id);
CREATE INDEX idx_operations_actor ON operations(actor_id, actor_type);
CREATE INDEX idx_operations_plan ON operations(plan_hash);
CREATE INDEX idx_operations_status ON operations(status);
CREATE INDEX idx_operations_time ON operations(started_at DESC);
CREATE INDEX idx_operations_embedding ON operations(vector_embedding_id) WHERE vector_embedding_id IS NOT NULL;
CREATE INDEX idx_operations_parent ON operations(parent_operation_id) WHERE parent_operation_id IS NOT NULL;
CREATE INDEX idx_operations_snapshots ON operations USING GIN (before_snapshot, after_snapshot);

COMMENT ON TABLE operations IS 'Immutable event log of all infrastructure mutations (replaces Git)';
COMMENT ON COLUMN operations.plan_hash IS 'SHA256 of the plan that generated this operation';
COMMENT ON COLUMN operations.before_snapshot IS 'State before mutation (for rollback)';
COMMENT ON COLUMN operations.after_snapshot IS 'State after mutation (NULL if failed)';
COMMENT ON COLUMN operations.vector_embedding_id IS 'Link to vector-db for pattern learning';

-- Add foreign key after operations table is created
ALTER TABLE plan_versions ADD CONSTRAINT fk_execution_operation FOREIGN KEY (execution_operation_id) REFERENCES operations(operation_id);

-- =============================================================================
-- POLICIES TABLE
-- =============================================================================

CREATE TABLE policies (
    policy_id VARCHAR(64) PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL UNIQUE,
    policy_type VARCHAR(50) NOT NULL,
    scope VARCHAR(50) NOT NULL,
    scope_id VARCHAR(64),
    rules JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT policy_type_check CHECK (policy_type IN ('resource_limit', 'region_restriction', 'cost_cap', 'security_rule')),
    CONSTRAINT scope_check CHECK (scope IN ('global', 'user', 'app'))
);

CREATE INDEX idx_policies_active ON policies(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_policies_scope ON policies(scope, scope_id);
CREATE INDEX idx_policies_rules ON policies USING GIN (rules);

COMMENT ON TABLE policies IS 'Constraints and rules that AI must respect';
COMMENT ON COLUMN policies.rules IS 'Policy rules in structured JSONB format';

-- =============================================================================
-- SCHEMA_VERSIONS TABLE
-- =============================================================================

CREATE TABLE schema_versions (
    version_id VARCHAR(64) PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
    migration_script TEXT NOT NULL,
    rollback_script TEXT,
    status VARCHAR(50) NOT NULL,
    CONSTRAINT status_check CHECK (status IN ('applied', 'failed', 'rolled_back'))
);

CREATE INDEX idx_schema_applied ON schema_versions(applied_at DESC);

COMMENT ON TABLE schema_versions IS 'Database schema evolution tracking';
COMMENT ON COLUMN schema_versions.version_id IS 'Format: schema_{timestamp}_{description}';

-- =============================================================================
-- INSERT INITIAL SCHEMA VERSION RECORD
-- =============================================================================

INSERT INTO schema_versions (version_id, migration_script, rollback_script, status)
VALUES (
    'schema_20251206_001_initial_schema',
    '001_initial_schema.sql',
    '001_initial_schema_rollback.sql',
    'applied'
);

-- =============================================================================
-- CREATE SAMPLE ADMIN USER (For Development)
-- =============================================================================

-- Insert a default admin user for development/testing
INSERT INTO users (user_id, email, display_name, role, is_active, created_at)
VALUES (
    'user:admin:dev',
    'admin@ai-native-control-plane.local',
    'System Administrator',
    'admin',
    TRUE,
    NOW()
) ON CONFLICT (user_id) DO NOTHING;

COMMENT ON TABLE users IS 'Contains default admin user for development';

-- =============================================================================
-- CREATE SAMPLE GLOBAL POLICIES
-- =============================================================================

-- Insert default global policies
INSERT INTO policies (policy_id, policy_name, policy_type, scope, rules, is_active)
VALUES
    (
        'policy:global:max_instances',
        'max_cloud_run_instances',
        'resource_limit',
        'global',
        '{"max_instances": 100, "per_service": 10}'::JSONB,
        TRUE
    ),
    (
        'policy:global:allowed_regions',
        'allowed_gcp_regions',
        'region_restriction',
        'global',
        '{"allowed_regions": ["us-central1", "us-east1", "us-west1", "europe-west1"]}'::JSONB,
        TRUE
    ),
    (
        'policy:global:cost_cap',
        'monthly_cost_cap',
        'cost_cap',
        'global',
        '{"max_monthly_usd": 1000, "alert_threshold_pct": 80}'::JSONB,
        TRUE
    )
ON CONFLICT (policy_id) DO NOTHING;

-- =============================================================================
-- GRANT PERMISSIONS (Application User)
-- =============================================================================

-- Create application user role if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ai_control_plane_app') THEN
        CREATE ROLE ai_control_plane_app WITH LOGIN PASSWORD 'changeme_in_production';
    END IF;
END
$$;

-- Grant appropriate permissions to application user
GRANT CONNECT ON DATABASE postgres TO ai_control_plane_app;
GRANT USAGE ON SCHEMA public TO ai_control_plane_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_control_plane_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_control_plane_app;

-- Ensure future tables also get permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ai_control_plane_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ai_control_plane_app;

-- =============================================================================
-- INITIAL SCHEMA COMPLETE
-- =============================================================================

-- Verify table creation
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
