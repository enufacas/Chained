# AI-Native Control Plane - State Database

This directory contains the production-ready database schema and migrations for the **state-db** component of the AI-Native Control Plane.

## Overview

The **state-db** is the ground truth for all system state, replacing Git history and file-based state management. It uses **PostgreSQL** or **Google Cloud SQL**.

### Key Features

- **Event Sourcing**: Complete audit trail via `operations` table
- **Deterministic IDs**: SHA256-based IDs instead of UUIDs
- **JSONB Flexibility**: Extensible metadata without schema changes
- **Time-Travel Debugging**: Before/after snapshots for every mutation
- **Semantic Memory Integration**: Links to vector-db for pattern learning

## Database Schema

### Tables

| Table | Purpose | Rows (Expected) |
|-------|---------|-----------------|
| `users` | User accounts and authentication | 1-1000 |
| `apps` | Applications managed by control plane | 1-10,000 |
| `infra_objects` | GCP resources (buckets, services, etc.) | 10-100,000 |
| `plan_versions` | Validated deployment plans | 100-1M |
| `operations` | Event log (replaces Git history) | 1K-10M |
| `policies` | AI constraints and rules | 10-1000 |
| `schema_versions` | Database migration history | 10-100 |

### Relationships

```
users
  └─> apps (owner)
       ├─> plan_versions (current version)
       ├─> infra_objects (app resources)
       └─> operations (app events)
            └─> operations (parent operation - hierarchical)

policies -> apps (scope)
policies -> users (scope)
```

## Migrations

Migrations are SQL scripts in `migrations/` directory:

- `NNN_description.sql` - Forward migration
- `NNN_description_rollback.sql` - Rollback script

### Current Migrations

1. **001_initial_schema.sql** - Initial production schema with all 7 tables

## Setup Instructions

### Local Development (PostgreSQL)

#### 1. Install PostgreSQL

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15 postgresql-contrib-15
sudo systemctl start postgresql

# Verify installation
psql --version
```

#### 2. Create Database

```bash
# Create database
createdb ai_native_control_plane

# Or use psql
psql -U postgres
CREATE DATABASE ai_native_control_plane;
\q
```

#### 3. Run Migrations

```bash
# Apply initial schema
psql -U postgres -d ai_native_control_plane -f migrations/001_initial_schema.sql

# Verify tables created
psql -U postgres -d ai_native_control_plane -c "\dt"
```

#### 4. Test Connection

```bash
# Connect to database
psql -U postgres -d ai_native_control_plane

# Check users table
SELECT * FROM users;

# Check policies
SELECT policy_name, policy_type, scope FROM policies;

# Exit
\q
```

### Production Deployment (Google Cloud SQL)

#### 1. Create Cloud SQL Instance

```bash
# Set variables
export PROJECT_ID="your-gcp-project"
export INSTANCE_NAME="ai-native-control-plane-db"
export REGION="us-central1"
export DB_PASSWORD="$(openssl rand -base64 32)"

# Create Cloud SQL instance (PostgreSQL 15)
gcloud sql instances create $INSTANCE_NAME \
  --project=$PROJECT_ID \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=$REGION \
  --network=default \
  --no-assign-ip \
  --availability-type=regional \
  --backup-start-time=03:00 \
  --enable-bin-log \
  --database-flags=max_connections=100

# Create database
gcloud sql databases create ai_native_control_plane \
  --instance=$INSTANCE_NAME \
  --project=$PROJECT_ID

# Set root password
gcloud sql users set-password postgres \
  --instance=$INSTANCE_NAME \
  --password=$DB_PASSWORD \
  --project=$PROJECT_ID
```

#### 2. Run Migrations on Cloud SQL

```bash
# Option 1: Cloud SQL Proxy (Recommended)
cloud_sql_proxy -instances=$PROJECT_ID:$REGION:$INSTANCE_NAME=tcp:5432 &
psql "host=127.0.0.1 port=5432 dbname=ai_native_control_plane user=postgres" \
  -f migrations/001_initial_schema.sql

# Option 2: Direct connection (if public IP enabled)
psql "host=<CLOUD_SQL_IP> port=5432 dbname=ai_native_control_plane user=postgres" \
  -f migrations/001_initial_schema.sql
```

#### 3. Create Application User

```bash
# Connect to database
psql "host=127.0.0.1 port=5432 dbname=ai_native_control_plane user=postgres"

# Application user is created by migration, but update password:
ALTER USER ai_control_plane_app WITH PASSWORD 'secure_password_here';
\q
```

#### 4. Store Credentials in Secret Manager

```bash
# Store database password
echo -n "$DB_PASSWORD" | gcloud secrets create db-password \
  --project=$PROJECT_ID \
  --replication-policy=automatic \
  --data-file=-

# Store connection string
CONNECTION_STRING="postgresql://ai_control_plane_app:secure_password_here@/ai_native_control_plane?host=/cloudsql/$PROJECT_ID:$REGION:$INSTANCE_NAME"
echo -n "$CONNECTION_STRING" | gcloud secrets create db-connection-string \
  --project=$PROJECT_ID \
  --replication-policy=automatic \
  --data-file=-
```

## Connection Strings

### Local Development

```python
# Python (SQLAlchemy)
DATABASE_URL = "postgresql://postgres:@localhost/ai_native_control_plane"

# Node.js
DATABASE_URL = "postgresql://postgres@localhost:5432/ai_native_control_plane"
```

### Production (Cloud SQL via Unix Socket)

```python
# Python (SQLAlchemy)
DATABASE_URL = "postgresql://ai_control_plane_app:PASSWORD@/ai_native_control_plane?host=/cloudsql/PROJECT:REGION:INSTANCE"

# Node.js
DATABASE_URL = "postgresql://ai_control_plane_app:PASSWORD@/ai_native_control_plane?host=/cloudsql/PROJECT:REGION:INSTANCE"
```

### Production (Cloud SQL via Proxy)

```python
# With Cloud SQL Proxy running on localhost:5432
DATABASE_URL = "postgresql://ai_control_plane_app:PASSWORD@localhost:5432/ai_native_control_plane"
```

## Schema Management

### Creating a New Migration

1. **Identify Changes Needed**
   - New table, column, index, or constraint
   - Document rationale and impact

2. **Create Migration Files**

```bash
# Create forward migration
cat > migrations/002_add_feature.sql << 'EOF'
-- Migration: 002_add_feature
-- Description: Add new feature X

ALTER TABLE apps ADD COLUMN new_field VARCHAR(100);
CREATE INDEX idx_apps_new_field ON apps(new_field);

-- Update schema_versions
INSERT INTO schema_versions (version_id, migration_script, rollback_script, status)
VALUES ('schema_20251206_002_add_feature', '002_add_feature.sql', '002_add_feature_rollback.sql', 'applied');
EOF

# Create rollback migration
cat > migrations/002_add_feature_rollback.sql << 'EOF'
-- Rollback: 002_add_feature

DROP INDEX IF EXISTS idx_apps_new_field;
ALTER TABLE apps DROP COLUMN IF EXISTS new_field;
EOF
```

3. **Test Migration**

```bash
# Apply forward
psql -U postgres -d ai_native_control_plane -f migrations/002_add_feature.sql

# Test rollback
psql -U postgres -d ai_native_control_plane -f migrations/002_add_feature_rollback.sql

# Re-apply forward
psql -U postgres -d ai_native_control_plane -f migrations/002_add_feature.sql
```

4. **Document in README**
   - Update "Current Migrations" section
   - Note any breaking changes

### Rollback Strategy

```bash
# Rollback most recent migration
psql -U postgres -d ai_native_control_plane -f migrations/002_add_feature_rollback.sql

# Update schema_versions table
psql -U postgres -d ai_native_control_plane -c \
  "UPDATE schema_versions SET status='rolled_back' WHERE version_id='schema_20251206_002_add_feature';"
```

## Maintenance

### Backup

```bash
# Local backup
pg_dump -U postgres ai_native_control_plane > backup_$(date +%Y%m%d).sql

# Cloud SQL backup (automated)
gcloud sql backups list --instance=$INSTANCE_NAME --project=$PROJECT_ID

# Manual Cloud SQL backup
gcloud sql backups create --instance=$INSTANCE_NAME --project=$PROJECT_ID
```

### Restore

```bash
# Local restore
psql -U postgres ai_native_control_plane < backup_20251206.sql

# Cloud SQL restore
gcloud sql backups restore BACKUP_ID \
  --backup-instance=$INSTANCE_NAME \
  --backup-instance-project=$PROJECT_ID \
  --instance=$INSTANCE_NAME \
  --project=$PROJECT_ID
```

### Monitoring

```bash
# Check database size
psql -U postgres -d ai_native_control_plane -c \
  "SELECT pg_size_pretty(pg_database_size('ai_native_control_plane'));"

# Check table sizes
psql -U postgres -d ai_native_control_plane -c \
  "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Check connections
psql -U postgres -d ai_native_control_plane -c \
  "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

## Troubleshooting

### Connection Issues

```bash
# Verify PostgreSQL is running
pg_isready

# Check listening port
sudo lsof -i :5432

# Test connection
psql -U postgres -d ai_native_control_plane -c "SELECT version();"
```

### Permission Issues

```bash
# Grant all permissions to app user
psql -U postgres -d ai_native_control_plane -c \
  "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_control_plane_app;"
```

### Migration Failures

```bash
# Check schema_versions for failures
psql -U postgres -d ai_native_control_plane -c \
  "SELECT * FROM schema_versions WHERE status='failed';"

# Manually mark migration as rolled back
psql -U postgres -d ai_native_control_plane -c \
  "UPDATE schema_versions SET status='rolled_back' WHERE version_id='schema_20251206_XXX_failed_migration';"
```

## Related Documentation

- **[State and Memory Model](../../docs/ai-native/02_state_and_memory.md)** - Complete data model specification
- **[Services Layout](../../docs/ai-native/03_services_layout.md)** - Service architecture
- **[AI Control Plane](../ai-control-plane/README.md)** - Main service that uses this database
- **[Infra Runner](../infra-runner/README.md)** - Infrastructure execution service

## Status

**Current Version**: 001 (Initial Schema)  
**Status**: 🚀 Production-ready schema  
**PostgreSQL Version**: 15+  
**Cloud SQL Version**: POSTGRES_15

---

*Last Updated: 2025-12-06*
