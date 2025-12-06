# AI-Native Control Plane — Infra Runner API Contract

This document defines the complete API contract for the **infra-runner** service, which is responsible for deterministic execution of infrastructure plans on Google Cloud Platform.

---

## API Overview

The infra-runner exposes a RESTful API for managing cloud infrastructure. All endpoints:
- Accept and return JSON
- Require service account authentication
- Are idempotent (can be safely retried)
- Return deterministic results
- Log all operations to the event-log
- Include trace and correlation IDs

**Base URL**: `https://infra-runner-{hash}-uc.a.run.app` (internal only)

**Authentication**: Google Cloud IAM service account tokens

**Rate Limits**:
- 60 requests per minute per service account
- 10 concurrent requests per service account

---

## Common Request/Response Patterns

### Standard Request Headers

All requests must include:

```http
POST /deploy_static_site HTTP/1.1
Host: infra-runner-xxx.a.run.app
Content-Type: application/json
Authorization: Bearer {SERVICE_ACCOUNT_TOKEN}
X-Correlation-ID: req_abc123
X-Trace-ID: projects/PROJECT_ID/traces/TRACE_ID
```

### Standard Response Format

#### Success Response (2xx)

```json
{
  "success": true,
  "operation_id": "op_20250106_120000_abc123",
  "resource_id": "app-forum-2025-static-prod",
  "status": "completed",
  "message": "Static site deployed successfully",
  "details": {
    "bucket_name": "app-forum-2025-static-prod",
    "bucket_url": "https://storage.googleapis.com/app-forum-2025-static-prod",
    "files_uploaded": 42,
    "duration_ms": 2500
  },
  "metadata": {
    "plan_hash": "sha256_abc123",
    "app_id": "app-forum-2025",
    "timestamp": "2025-01-06T12:00:00.123Z"
  }
}
```

#### Error Response (4xx, 5xx)

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid bucket name format",
    "details": {
      "field": "bucket_name",
      "value": "invalid@bucket",
      "constraint": "Must match [a-z0-9-]+"
    },
    "retry_after": null,
    "documentation": "https://docs.example.com/errors/validation"
  },
  "operation_id": "op_20250106_120000_abc123",
  "timestamp": "2025-01-06T12:00:00.123Z"
}
```

### Error Codes

| HTTP Status | Error Code | Meaning | Retryable |
|-------------|------------|---------|-----------|
| 400 | VALIDATION_ERROR | Invalid request parameters | No |
| 400 | INVALID_PLAN | Plan validation failed | No |
| 401 | UNAUTHORIZED | Invalid or missing credentials | No |
| 403 | FORBIDDEN | Insufficient permissions | No |
| 404 | RESOURCE_NOT_FOUND | Resource does not exist | No |
| 409 | RESOURCE_CONFLICT | Resource already exists or state conflict | No |
| 422 | UNPROCESSABLE_ENTITY | Valid syntax but semantic error | No |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests | Yes (after delay) |
| 500 | INTERNAL_ERROR | Unexpected server error | Yes |
| 502 | GCP_API_ERROR | GCP API returned error | Yes |
| 503 | SERVICE_UNAVAILABLE | Service temporarily down | Yes |
| 504 | TIMEOUT | Operation took too long | Yes |

---

## Endpoint Specifications

### 1. Deploy Static Site

Deploy a static website to a GCS bucket with public access.

**Endpoint**: `POST /deploy_static_site`

**Request Body**:

```json
{
  "app_id": "app-forum-2025",
  "bucket_name": "app-forum-2025-static-prod",
  "region": "us-central1",
  "files": [
    {
      "path": "index.html",
      "content": "<!DOCTYPE html><html>...",
      "content_type": "text/html",
      "cache_control": "public, max-age=3600"
    },
    {
      "path": "styles.css",
      "content": "body { margin: 0; }",
      "content_type": "text/css",
      "cache_control": "public, max-age=86400"
    },
    {
      "path": "assets/logo.png",
      "content_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
      "content_type": "image/png",
      "cache_control": "public, max-age=604800"
    }
  ],
  "public_access": true,
  "enable_cdn": true,
  "index_page": "index.html",
  "error_page": "404.html",
  "cors_config": {
    "allowed_origins": ["*"],
    "allowed_methods": ["GET", "HEAD"],
    "allowed_headers": ["*"],
    "max_age_seconds": 3600
  },
  "lifecycle_rules": [
    {
      "action": "Delete",
      "condition": {
        "age_days": 90,
        "matches_prefix": "temp/"
      }
    }
  ],
  "plan_hash": "sha256_abc123",
  "idempotency_key": "deploy_app-forum-2025_20250106_120000"
}
```

**Request Schema**:

```typescript
interface DeployStaticSiteRequest {
  app_id: string;                    // Must match /^app-[a-z0-9-]+$/
  bucket_name: string;                // Must match /^[a-z0-9-]+$/, globally unique
  region: string;                     // GCP region (e.g., "us-central1")
  files: FileUpload[];                // 1-10000 files
  public_access: boolean;             // Enable public read access
  enable_cdn?: boolean;               // Enable Cloud CDN (default: false)
  index_page?: string;                // Default index page (default: "index.html")
  error_page?: string;                // 404 error page (default: "404.html")
  cors_config?: CorsConfig;           // CORS configuration (optional)
  lifecycle_rules?: LifecycleRule[];  // Lifecycle management rules (optional)
  plan_hash: string;                  // SHA256 hash of the deployment plan
  idempotency_key: string;            // Unique key for idempotency
}

interface FileUpload {
  path: string;                       // Relative path in bucket (e.g., "assets/logo.png")
  content?: string;                   // Text content (for HTML, CSS, JS, etc.)
  content_base64?: string;            // Base64-encoded binary content (for images, etc.)
  content_type: string;               // MIME type (e.g., "text/html", "image/png")
  cache_control?: string;             // Cache-Control header (default: "public, max-age=3600")
}

interface CorsConfig {
  allowed_origins: string[];          // ["*"] or specific origins
  allowed_methods: string[];          // ["GET", "HEAD", "POST", etc.]
  allowed_headers: string[];          // ["*"] or specific headers
  max_age_seconds: number;            // Preflight cache duration
}

interface LifecycleRule {
  action: "Delete" | "SetStorageClass";
  condition: {
    age_days?: number;                // Age in days
    created_before?: string;          // ISO 8601 date
    matches_prefix?: string;          // Object name prefix
    matches_suffix?: string;          // Object name suffix
  };
  storage_class?: "NEARLINE" | "COLDLINE" | "ARCHIVE";  // Required if action is SetStorageClass
}
```

**Response** (201 Created):

```json
{
  "success": true,
  "operation_id": "op_20250106_120000_abc123",
  "resource_id": "app-forum-2025-static-prod",
  "status": "completed",
  "message": "Static site deployed successfully",
  "details": {
    "bucket_name": "app-forum-2025-static-prod",
    "bucket_url": "https://storage.googleapis.com/app-forum-2025-static-prod",
    "public_url": "https://storage.googleapis.com/app-forum-2025-static-prod/index.html",
    "cdn_enabled": true,
    "cdn_url": "https://cdn.example.com/app-forum-2025",
    "files_uploaded": 42,
    "total_size_bytes": 1024000,
    "duration_ms": 2500,
    "region": "us-central1"
  },
  "metadata": {
    "plan_hash": "sha256_abc123",
    "app_id": "app-forum-2025",
    "timestamp": "2025-01-06T12:00:00.123Z"
  }
}
```

**Idempotency**:
- If bucket already exists with same files and config: return 200 OK (no changes)
- If bucket exists but differs: return 409 Conflict
- Use `idempotency_key` to detect duplicate requests within 24 hours

**Validation Rules**:
- `bucket_name` must be globally unique (check GCS namespace)
- `files` array must contain at least 1 file
- Total size of all files must be < 1GB
- `content` and `content_base64` are mutually exclusive
- `path` must not contain `..` or start with `/`

---

### 2. Deploy Dynamic Service

Deploy a containerized application to Google Cloud Run.

**Endpoint**: `POST /deploy_dynamic_service`

**Request Body**:

```json
{
  "app_id": "app-forum-2025",
  "service_name": "app-forum-2025-dynamic-prod",
  "region": "us-central1",
  "image": "gcr.io/project-id/app-forum:1.0.0",
  "port": 8080,
  "env_vars": {
    "DATABASE_URL": "postgresql://...",
    "REDIS_URL": "redis://...",
    "LOG_LEVEL": "INFO"
  },
  "secrets": [
    {
      "name": "API_KEY",
      "secret_name": "app-forum-api-key",
      "version": "latest"
    }
  ],
  "resources": {
    "cpu": "2",
    "memory": "4Gi"
  },
  "scaling": {
    "min_instances": 1,
    "max_instances": 10,
    "concurrency": 80,
    "cpu_throttling": true
  },
  "timeout_seconds": 300,
  "service_account": "app-forum@project-id.iam.gserviceaccount.com",
  "ingress": "all",
  "allow_unauthenticated": true,
  "vpc_connector": null,
  "health_check": {
    "path": "/health",
    "interval_seconds": 30,
    "timeout_seconds": 5,
    "failure_threshold": 3
  },
  "labels": {
    "app": "forum",
    "env": "prod",
    "managed_by": "ai-control-plane"
  },
  "plan_hash": "sha256_def456",
  "idempotency_key": "deploy_app-forum-2025_20250106_130000"
}
```

**Request Schema**:

```typescript
interface DeployDynamicServiceRequest {
  app_id: string;
  service_name: string;               // Must match /^[a-z0-9-]+$/
  region: string;                     // GCP region
  image: string;                      // Container image (gcr.io/... or docker.io/...)
  port: number;                       // Container port (1-65535)
  env_vars?: Record<string, string>;  // Environment variables
  secrets?: SecretMount[];            // Secret Manager secrets
  resources: ResourceConfig;          // CPU and memory
  scaling: ScalingConfig;             // Min/max instances and concurrency
  timeout_seconds: number;            // Request timeout (1-3600)
  service_account?: string;           // IAM service account email
  ingress: "all" | "internal" | "internal-and-cloud-load-balancing";
  allow_unauthenticated: boolean;     // Enable public access
  vpc_connector?: string;             // VPC connector for private resources
  health_check?: HealthCheckConfig;   // Health check configuration
  labels?: Record<string, string>;    // Resource labels
  plan_hash: string;
  idempotency_key: string;
}

interface SecretMount {
  name: string;                       // Environment variable name
  secret_name: string;                // Secret Manager secret name
  version: string;                    // "latest" or specific version number
}

interface ResourceConfig {
  cpu: string;                        // "1", "2", "4", "8" (vCPUs)
  memory: string;                     // "512Mi", "1Gi", "2Gi", "4Gi", "8Gi", "16Gi", "32Gi"
}

interface ScalingConfig {
  min_instances: number;              // 0-1000
  max_instances: number;              // 1-1000
  concurrency: number;                // 1-1000 requests per instance
  cpu_throttling: boolean;            // Throttle CPU when idle
}

interface HealthCheckConfig {
  path: string;                       // HTTP path for health checks
  interval_seconds: number;           // Check interval (10-300)
  timeout_seconds: number;            // Check timeout (1-300)
  failure_threshold: number;          // Failures before unhealthy (1-10)
}
```

**Response** (201 Created):

```json
{
  "success": true,
  "operation_id": "op_20250106_130000_def456",
  "resource_id": "app-forum-2025-dynamic-prod",
  "status": "completed",
  "message": "Dynamic service deployed successfully",
  "details": {
    "service_name": "app-forum-2025-dynamic-prod",
    "service_url": "https://app-forum-2025-dynamic-prod-abc123-uc.a.run.app",
    "region": "us-central1",
    "revision": "app-forum-2025-dynamic-prod-00001-xyz",
    "image": "gcr.io/project-id/app-forum:1.0.0",
    "resources": {
      "cpu": "2",
      "memory": "4Gi"
    },
    "scaling": {
      "min_instances": 1,
      "max_instances": 10,
      "current_instances": 1
    },
    "health_status": "healthy",
    "duration_ms": 15000
  },
  "metadata": {
    "plan_hash": "sha256_def456",
    "app_id": "app-forum-2025",
    "timestamp": "2025-01-06T13:00:00.456Z"
  }
}
```

**Validation Rules**:
- `image` must be accessible by infra-runner service account
- `service_account` must exist and have necessary permissions
- `secrets` must reference existing Secret Manager secrets
- `cpu` and `memory` must be valid Cloud Run configurations
- `min_instances` ≤ `max_instances`
- If `vpc_connector` is set, it must exist

**Deployment Strategy**:
- Zero-downtime deployment (traffic gradually shifted)
- New revision created for each deployment
- Old revisions retained for rollback (configurable)

---

### 3. Scale Service

Dynamically scale a Cloud Run service by adjusting min/max instances.

**Endpoint**: `POST /scale_service`

**Request Body**:

```json
{
  "service_name": "app-forum-2025-dynamic-prod",
  "region": "us-central1",
  "scaling": {
    "min_instances": 2,
    "max_instances": 20
  },
  "plan_hash": "sha256_ghi789",
  "idempotency_key": "scale_app-forum-2025_20250106_140000"
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "operation_id": "op_20250106_140000_ghi789",
  "resource_id": "app-forum-2025-dynamic-prod",
  "status": "completed",
  "message": "Service scaled successfully",
  "details": {
    "service_name": "app-forum-2025-dynamic-prod",
    "previous_scaling": {
      "min_instances": 1,
      "max_instances": 10
    },
    "new_scaling": {
      "min_instances": 2,
      "max_instances": 20
    },
    "current_instances": 2,
    "duration_ms": 500
  },
  "metadata": {
    "plan_hash": "sha256_ghi789",
    "timestamp": "2025-01-06T14:00:00.789Z"
  }
}
```

**Validation Rules**:
- Service must exist
- `min_instances` ≤ `max_instances`
- Scaling change must be < 10x current capacity (safety limit)

---

### 4. Attach Domain

Attach a custom domain to a Cloud Run service.

**Endpoint**: `POST /attach_domain`

**Request Body**:

```json
{
  "service_name": "app-forum-2025-dynamic-prod",
  "region": "us-central1",
  "domain": "forum.example.com",
  "subdomain": null,
  "certificate_mode": "automatic",
  "plan_hash": "sha256_jkl012",
  "idempotency_key": "attach_domain_app-forum-2025_20250106_150000"
}
```

**Request Schema**:

```typescript
interface AttachDomainRequest {
  service_name: string;
  region: string;
  domain: string;                     // Fully qualified domain name
  subdomain?: string;                 // Optional subdomain (e.g., "www")
  certificate_mode: "automatic" | "manual";  // SSL certificate management
  plan_hash: string;
  idempotency_key: string;
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "operation_id": "op_20250106_150000_jkl012",
  "resource_id": "forum.example.com",
  "status": "completed",
  "message": "Domain attached successfully",
  "details": {
    "domain": "forum.example.com",
    "service_name": "app-forum-2025-dynamic-prod",
    "dns_records": [
      {
        "type": "A",
        "name": "forum.example.com",
        "value": "216.239.32.21"
      },
      {
        "type": "AAAA",
        "name": "forum.example.com",
        "value": "2001:4860:4802:32::15"
      }
    ],
    "certificate_status": "provisioned",
    "certificate_expiry": "2026-01-06T00:00:00Z",
    "duration_ms": 30000
  },
  "metadata": {
    "plan_hash": "sha256_jkl012",
    "timestamp": "2025-01-06T15:00:00.012Z"
  }
}
```

**Validation Rules**:
- `domain` must be verified in Cloud Console
- DNS records must point to Cloud Run before automatic certificate provisioning
- Certificate provisioning may take up to 15 minutes

---

### 5. Validate Plan

Validate an execution plan without executing it (dry-run).

**Endpoint**: `POST /validate_plan`

**Request Body**:

```json
{
  "plan_type": "deploy_static_site",
  "plan": {
    "app_id": "app-test-2025",
    "bucket_name": "app-test-2025-static-prod",
    "region": "us-central1",
    "files": [
      {
        "path": "index.html",
        "content": "<!DOCTYPE html><html>...",
        "content_type": "text/html"
      }
    ],
    "public_access": true,
    "plan_hash": "sha256_mno345"
  }
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "valid": true,
  "issues": [],
  "warnings": [
    "Bucket name 'app-test-2025-static-prod' is very long (>50 chars recommended)"
  ],
  "estimated_cost": {
    "storage_gb_month": 0.01,
    "egress_gb_month": 1.0,
    "operations_count": 42,
    "total_usd_month": 0.05
  },
  "estimated_duration_seconds": 3,
  "timestamp": "2025-01-06T16:00:00.345Z"
}
```

**Response** (200 OK - Validation Failed):

```json
{
  "success": true,
  "valid": false,
  "issues": [
    {
      "severity": "error",
      "field": "bucket_name",
      "message": "Bucket name contains invalid characters",
      "details": "Bucket names can only contain lowercase letters, numbers, and hyphens"
    },
    {
      "severity": "error",
      "field": "files[0].path",
      "message": "File path contains '..' (path traversal)",
      "details": "File paths must be relative and not contain '..' or start with '/'"
    }
  ],
  "warnings": [],
  "timestamp": "2025-01-06T16:00:00.345Z"
}
```

**Validation Checks**:
- Schema validation (all required fields present)
- Naming convention compliance
- Resource quota checks
- Permission verification
- Cost estimation
- Security checks (no path traversal, no XSS, etc.)

---

### 6. Check Service Health

Check the health status of a Cloud Run service.

**Endpoint**: `GET /check_service_health`

**Query Parameters**:
- `service_name` (required): Name of the service
- `region` (required): GCP region

**Request Example**:

```
GET /check_service_health?service_name=app-forum-2025-dynamic-prod&region=us-central1
```

**Response** (200 OK):

```json
{
  "success": true,
  "service_name": "app-forum-2025-dynamic-prod",
  "region": "us-central1",
  "status": "healthy",
  "details": {
    "service_url": "https://app-forum-2025-dynamic-prod-abc123-uc.a.run.app",
    "current_revision": "app-forum-2025-dynamic-prod-00001-xyz",
    "traffic_percent": 100,
    "instances": {
      "min": 1,
      "max": 10,
      "current": 2
    },
    "health_check": {
      "status": "passing",
      "last_check": "2025-01-06T17:00:00Z",
      "consecutive_failures": 0
    },
    "metrics": {
      "request_count_5m": 1500,
      "error_rate_5m": 0.02,
      "avg_latency_ms": 120,
      "p95_latency_ms": 250
    }
  },
  "timestamp": "2025-01-06T17:00:05.678Z"
}
```

**Response** (200 OK - Unhealthy):

```json
{
  "success": true,
  "service_name": "app-forum-2025-dynamic-prod",
  "status": "unhealthy",
  "details": {
    "health_check": {
      "status": "failing",
      "last_check": "2025-01-06T17:00:00Z",
      "consecutive_failures": 5,
      "error_message": "HTTP 500 Internal Server Error"
    },
    "metrics": {
      "request_count_5m": 100,
      "error_rate_5m": 0.95,
      "avg_latency_ms": 5000
    }
  },
  "timestamp": "2025-01-06T17:00:05.678Z"
}
```

**Status Values**:
- `healthy`: Service is operational
- `degraded`: Service is operational but performance is poor
- `unhealthy`: Service is not responding correctly
- `unknown`: Unable to determine health

---

### 7. Check Bucket Health

Check the health status of a GCS bucket.

**Endpoint**: `GET /check_bucket_health`

**Query Parameters**:
- `bucket_name` (required): Name of the bucket

**Request Example**:

```
GET /check_bucket_health?bucket_name=app-forum-2025-static-prod
```

**Response** (200 OK):

```json
{
  "success": true,
  "bucket_name": "app-forum-2025-static-prod",
  "status": "healthy",
  "details": {
    "public_url": "https://storage.googleapis.com/app-forum-2025-static-prod",
    "region": "us-central1",
    "storage_class": "STANDARD",
    "public_access": true,
    "versioning_enabled": true,
    "lifecycle_rules_count": 1,
    "object_count": 42,
    "total_size_bytes": 1024000,
    "last_modified": "2025-01-06T12:00:00Z"
  },
  "timestamp": "2025-01-06T17:00:10.901Z"
}
```

**Response** (404 Not Found):

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Bucket 'app-nonexistent' does not exist"
  },
  "timestamp": "2025-01-06T17:00:10.901Z"
}
```

---

## Plan Validation Rules

The `/validate_plan` endpoint performs comprehensive validation before execution:

### Schema Validation

1. **Required Fields**: All required fields must be present
2. **Type Checking**: Fields must match expected types (string, number, boolean, etc.)
3. **Format Validation**: Fields must match expected formats (email, URL, etc.)

### Naming Conventions

1. **Resource Names**:
   - Lowercase letters, numbers, and hyphens only
   - Must start with a letter
   - Must end with a letter or number
   - Length: 3-63 characters
   - Pattern: `/^[a-z][a-z0-9-]*[a-z0-9]$/`

2. **Bucket Names**:
   - Globally unique across all GCP projects
   - Must not contain `google` or close misspellings
   - Must not resemble IP addresses

3. **Service Names**:
   - Unique within project and region
   - Must not conflict with reserved names

### Security Checks

1. **Path Traversal**: No `..` in file paths
2. **Absolute Paths**: Paths must be relative (not start with `/`)
3. **XSS Prevention**: HTML content is scanned for suspicious scripts
4. **SQL Injection**: Database URLs are validated
5. **Secret Exposure**: No secrets in environment variables (use Secret Manager)

### Resource Limits

1. **File Size**: Individual files ≤ 100MB
2. **Total Upload Size**: ≤ 1GB per deployment
3. **File Count**: ≤ 10,000 files per bucket
4. **Environment Variables**: ≤ 100 per service
5. **Labels**: ≤ 64 per resource

### Cost Estimation

1. **Storage**: GCS storage costs based on file sizes and storage class
2. **Egress**: Estimated based on historical traffic patterns
3. **Compute**: Cloud Run instance-hours based on min instances
4. **Operations**: GCS API operations (uploads, downloads, lists)

### Permission Checks

1. **GCS Buckets**: infra-runner has `storage.buckets.create` permission
2. **Cloud Run**: infra-runner has `run.services.create` permission
3. **IAM**: Service accounts exist and have required roles
4. **Secrets**: Secret Manager secrets are accessible

---

## Retry and Idempotency Rules

### Idempotency

All mutating operations (POST) must include an `idempotency_key` to prevent duplicate execution:

```json
{
  "idempotency_key": "deploy_app-forum-2025_20250106_120000",
  ...
}
```

**Idempotency Key Format**: `{operation}_{resource_id}_{timestamp}`

**Behavior**:
- First request with key: Execute operation
- Duplicate request within 24 hours: Return cached response (200 OK)
- Duplicate request after 24 hours: Execute operation (keys expire)

**Storage**: Idempotency keys stored in state-db with operation results

### Retry Strategy

**Client-Side Retry** (ai-control-plane):

1. **Exponential Backoff**: 1s, 2s, 4s, 8s, 16s
2. **Max Retries**: 5 attempts
3. **Jitter**: Add random 0-1s to avoid thundering herd
4. **Retryable Status Codes**: 429, 500, 502, 503, 504
5. **Non-Retryable**: 400, 401, 403, 404, 409, 422

**Example Retry Logic**:

```python
import httpx
import time
import random

def call_infra_runner_with_retry(endpoint, payload, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = httpx.post(endpoint, json=payload, timeout=60.0)
            
            # Success
            if response.status_code in [200, 201]:
                return response.json()
            
            # Non-retryable error
            if response.status_code in [400, 401, 403, 404, 409, 422]:
                raise Exception(f"Non-retryable error: {response.status_code}")
            
            # Retryable error
            if response.status_code in [429, 500, 502, 503, 504]:
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"Max retries exceeded: {response.status_code}")
        
        except httpx.TimeoutException:
            if attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue
            else:
                raise Exception("Max retries exceeded: timeout")
    
    raise Exception("Unexpected retry loop exit")
```

---

## Safe Mode and Dry Run

### Dry Run Mode

Enable dry-run mode via environment variable:

```bash
DRY_RUN=true
```

**Behavior**:
- All validation checks execute normally
- No actual GCP API calls are made
- Responses include `"dry_run": true` field
- Operation IDs are prefixed with `dry_`

**Example Response**:

```json
{
  "success": true,
  "dry_run": true,
  "operation_id": "dry_op_20250106_120000_abc123",
  "message": "Dry run: Static site would be deployed successfully",
  ...
}
```

### Safe Mode

Safe mode prevents destructive operations:

```bash
SAFE_MODE=true
```

**Behavior**:
- Create operations: Allowed
- Update operations: Allowed (with confirmation)
- Delete operations: Blocked (return 403 Forbidden)
- Scale-down operations: Blocked if > 50% reduction

**Use Cases**:
- Testing new configurations
- Preventing accidental resource deletion
- Gradual rollout of new features

---

## Health Check and Readiness

### Service Health Endpoint

**Endpoint**: `GET /health`

**Response** (200 OK):

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-06T18:00:00.123Z",
  "checks": {
    "gcp_credentials": "ok",
    "state_db_connection": "ok",
    "gcp_apis": "ok"
  }
}
```

**Response** (503 Service Unavailable):

```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2025-01-06T18:00:00.123Z",
  "checks": {
    "gcp_credentials": "ok",
    "state_db_connection": "failed",
    "gcp_apis": "ok"
  },
  "error": "Cannot connect to state-db"
}
```

### Readiness Endpoint

**Endpoint**: `GET /ready`

**Response** (200 OK):

```json
{
  "ready": true,
  "timestamp": "2025-01-06T18:00:00.123Z"
}
```

Used by Cloud Run to determine when service is ready to receive traffic.

---

## Monitoring and Observability

### Structured Logging

Every operation logs to Cloud Logging:

```json
{
  "timestamp": "2025-01-06T12:00:00.123Z",
  "severity": "INFO",
  "service": "infra-runner",
  "version": "1.0.0",
  "trace": "projects/PROJECT/traces/TRACE_ID",
  "span_id": "SPAN_ID",
  "correlation_id": "req_abc123",
  "operation": "deploy_static_site",
  "operation_id": "op_20250106_120000_abc123",
  "resource": {
    "type": "bucket",
    "id": "app-forum-2025-static-prod"
  },
  "actor": "ai-control-plane",
  "duration_ms": 2500,
  "success": true,
  "details": {
    "files_uploaded": 42,
    "total_size_bytes": 1024000
  }
}
```

### Metrics

**Request Metrics**:
- `infra_runner_requests_total` (counter): Total requests by endpoint and status
- `infra_runner_request_duration_seconds` (histogram): Request latency
- `infra_runner_errors_total` (counter): Errors by type and endpoint

**Operation Metrics**:
- `infra_runner_operations_total` (counter): Operations by type and result
- `infra_runner_operation_duration_seconds` (histogram): Operation latency
- `infra_runner_gcp_api_calls_total` (counter): GCP API calls by service

**Resource Metrics**:
- `infra_runner_buckets_managed` (gauge): Number of managed GCS buckets
- `infra_runner_services_managed` (gauge): Number of managed Cloud Run services
- `infra_runner_deployments_in_progress` (gauge): Concurrent deployments

---

## Security Considerations

### Service Account Permissions

infra-runner service account requires:

```yaml
Minimal Required Roles:
  - roles/storage.admin (GCS management)
  - roles/run.admin (Cloud Run management)
  - roles/iam.serviceAccountUser (for deployments)
  - roles/cloudsql.client (state-db access)

Denied Permissions:
  - roles/owner
  - roles/editor
  - roles/iam.serviceAccountAdmin
  - roles/resourcemanager.*
```

### Network Security

- **Ingress**: Internal only (no public access)
- **Egress**: GCP APIs only (no arbitrary internet access)
- **VPC**: Private VPC with Cloud NAT for GCP API access

### Input Validation

All inputs are validated before execution:

1. **SQL Injection**: Parameterized queries only
2. **Command Injection**: No shell commands with user input
3. **Path Traversal**: Sanitize all file paths
4. **XSS**: Escape HTML content
5. **SSRF**: Validate URLs before fetching

### Audit Logging

All operations logged to Cloud Logging with:
- Who (service account)
- What (operation type)
- When (timestamp)
- Where (resource ID)
- Result (success/failure)

---

## API Versioning

**Current Version**: `v1`

**Base URL**: `https://infra-runner-xxx.a.run.app/v1/...`

**Version Header**: `X-API-Version: 1.0.0`

**Deprecation Policy**:
- Old versions supported for 12 months
- Deprecation warnings in response headers:
  ```
  Deprecation: true
  Sunset: Sat, 1 Jan 2027 00:00:00 GMT
  Link: <https://docs.example.com/migration>; rel="sunset"
  ```

---

## Example Request Flows

### Deploy Static Site (End-to-End)

```python
import httpx

# 1. Validate plan
validation = httpx.post(
    "https://infra-runner-xxx.a.run.app/v1/validate_plan",
    json={
        "plan_type": "deploy_static_site",
        "plan": {
            "app_id": "app-blog-2025",
            "bucket_name": "app-blog-2025-static-prod",
            "region": "us-central1",
            "files": [...],
            "public_access": True,
            "plan_hash": "sha256_abc"
        }
    }
).json()

if not validation["valid"]:
    print(f"Validation failed: {validation['issues']}")
    exit(1)

# 2. Deploy
deployment = httpx.post(
    "https://infra-runner-xxx.a.run.app/v1/deploy_static_site",
    json={
        "app_id": "app-blog-2025",
        "bucket_name": "app-blog-2025-static-prod",
        "region": "us-central1",
        "files": [...],
        "public_access": True,
        "plan_hash": "sha256_abc",
        "idempotency_key": "deploy_app-blog-2025_20250106_120000"
    }
).json()

print(f"Deployed to: {deployment['details']['public_url']}")

# 3. Check health
health = httpx.get(
    "https://infra-runner-xxx.a.run.app/v1/check_bucket_health",
    params={"bucket_name": "app-blog-2025-static-prod"}
).json()

print(f"Bucket status: {health['status']}")
```

---

*This document is part of the AI-Native Control Plane specification defined in `.github/copilot/tasks/ai-native-control-plane.md`*

**Last updated**: 2025-12-06
