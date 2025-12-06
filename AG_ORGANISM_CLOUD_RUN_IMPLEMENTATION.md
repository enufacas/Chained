# AG-Organism Cloud Run Migration - Implementation Summary

## Overview

Successfully migrated the AG-Organism visualization from a static HTML file on GitHub Pages to a Cloud Run service with dynamic environment variable injection.

## Problem Statement

The `docs/ag-organism.html` was a static HTML file with hardcoded API URLs. This needed to be hosted on Cloud Run to:
- Access environment variables dynamically
- Ensure all functionality works properly  
- Align with the AG-UI infrastructure pattern
- Enable proper CORS configuration

## Solution

Created a new Cloud Run service `ag-organism-frontend` that:
1. Serves the ag-organism.html via Express.js server
2. Injects environment variables into the HTML at request time
3. Integrates with existing AG-UI and ADK API infrastructure
4. Follows the same deployment pattern as other Cloud Run services

## Implementation Details

### 1. Docker Container (`infrastructure/docker/ag-organism-frontend/`)

**Files Created:**
- `Dockerfile` - Multi-stage Node.js build
- `package.json` - Express dependency
- `server.js` - Express server with environment injection
- `public/ag-organism.html` - Copy of the visualization HTML
- `README.md` - Service documentation

**Key Features:**
- Express server on port 8080
- Environment variable injection via `window.ENV` object
- Health check endpoint at `/health`
- Minimal footprint (Node 20 Alpine, 512Mi memory)

### 2. HTML Updates

Modified `ag-organism.html` to:
- Add `<!-- ENV_INJECTED -->` placeholder in `<head>`
- Use `window.ENV?.AG_UI_FRONTEND_URL` for dynamic API base URL
- Fallback to hardcoded URLs for static version compatibility

**Before:**
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:3000/api'
    : 'https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api';
```

**After:**
```javascript
const API_BASE_URL = window.ENV?.AG_UI_FRONTEND_URL 
    ? `${window.ENV.AG_UI_FRONTEND_URL}/api`
    : (window.location.hostname === 'localhost'
        ? 'http://localhost:3000/api'
        : 'https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api');
```

### 3. Terraform Configuration

**Added to `infrastructure/terraform/adk-agents.tf`:**
- `google_cloud_run_v2_service.ag_organism_frontend` resource
- `google_cloud_run_v2_service_iam_member.ag_organism_frontend_public` IAM binding
- Output: `ag_organism_frontend_url`

**Configuration:**
- CPU: 0.5 (with `cpu_idle=true` for scale to zero)
- Memory: 512Mi
- Port: 8080
- Service Account: `chained-adk-agents` (reused)
- Max Concurrency: 1 (required when CPU < 1)

**Environment Variables:**
- `NEXT_PUBLIC_ADK_API_URL` - From ADK API Server URI
- `AG_UI_FRONTEND_URL` - From AG-UI Frontend URI
- `ENVIRONMENT` - dev/staging/prod

### 4. GitHub Actions Workflow

**Updated `.github/workflows/deploy-adk-agents.yml`:**
- Added `build-ag-organism-frontend` job
- Added build trigger path: `infrastructure/docker/ag-organism-frontend/**`
- Updated `terraform` job dependency chain
- Updated service list in workflow header

**Build Process:**
1. Build Docker image with SHA tag
2. Push to Artifact Registry
3. Deploy via Terraform with dynamic image tag

### 5. Documentation Updates

**Updated Files:**
- `docs/AG_ORGANISM_README.md` - Added deployment section, Cloud Run notice
- `docs/index.html` - Added "☁️ CLOUD RUN" badge and note
- `infrastructure/docker/ag-organism-frontend/README.md` - Complete service docs

## Testing Results

### Docker Build
✅ Build successful (5.7 seconds)
✅ Image size: ~150MB
✅ No vulnerabilities

### Container Runtime
✅ Server starts on port 8080
✅ Health endpoint returns JSON: `{"status":"healthy","service":"ag-organism-frontend"}`
✅ Environment variables injected correctly into HTML
✅ HTML served with proper Content-Type

### Environment Variable Injection
```javascript
window.ENV = {
  ADK_API_URL: 'https://chained-adk-api-server-sguacxy5gq-uc.a.run.app',
  AG_UI_FRONTEND_URL: 'https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app'
};
```

## Deployment Architecture

```
┌─────────────────────────────────────┐
│ GitHub Actions (CI/CD)              │
│ - Build Docker image                │
│ - Push to Artifact Registry         │
│ - Deploy via Terraform              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Cloud Run: ag-organism-frontend     │
│ - Express.js server                 │
│ - Environment injection             │
│ - Health checks                     │
│ - Auto-scaling 0-3 instances        │
└──────────────┬──────────────────────┘
               │
               │ API Calls
               ▼
┌─────────────────────────────────────┐
│ Cloud Run: ag-ui-frontend           │
│ - /api/pipeline                     │
│ - /api/registry                     │
└─────────────────────────────────────┘
```

## Benefits of Cloud Run Deployment

1. **Dynamic Configuration**: Environment variables configured at deployment time
2. **Proper Integration**: Uses Cloud Run service URLs via Terraform references
3. **Security**: Service account permissions, proper CORS, IAM controls
4. **Scalability**: Auto-scales 0-3 instances based on load
5. **Cost Efficiency**: Scales to zero when idle
6. **Observability**: Cloud Logging, Monitoring, and health checks
7. **Consistency**: Same deployment pattern as other services

## Comparison: Static vs Cloud Run

| Aspect | Static (GitHub Pages) | Cloud Run |
|--------|----------------------|-----------|
| **Deployment** | Git push to docs/ | Docker + Terraform |
| **API URLs** | Hardcoded | Environment variables |
| **Configuration** | Fixed at build | Dynamic at runtime |
| **Health Checks** | N/A | /health endpoint |
| **Environment** | Static file server | Node.js Express |
| **Observability** | None | Cloud Logging/Monitoring |
| **Cost** | Free (GitHub Pages) | ~$0.50/month (scales to zero) |
| **Updates** | Manual HTML edit | Automated CI/CD pipeline |

## Files Changed

```
Created:
  infrastructure/docker/ag-organism-frontend/
  ├── Dockerfile                        (520 bytes)
  ├── package.json                      (296 bytes)
  ├── server.js                         (1,753 bytes)
  ├── README.md                         (3,915 bytes)
  └── public/
      └── ag-organism.html              (53,141 bytes - copy)

Modified:
  .github/workflows/deploy-adk-agents.yml
  infrastructure/terraform/adk-agents.tf
  docs/AG_ORGANISM_README.md
  docs/index.html
```

## Next Steps

### For Deployment
1. Merge this PR to main branch
2. GitHub Actions will automatically:
   - Build and push Docker image
   - Deploy via Terraform
   - Output service URL

### For Users
1. Get service URL:
   ```bash
   terraform output ag_organism_frontend_url
   ```
2. Access the Cloud Run version instead of static version
3. Static version remains available as fallback

### For Maintenance
- Update HTML: Edit `infrastructure/docker/ag-organism-frontend/public/ag-organism.html`
- Update environment: Modify Terraform variables or workflow secrets
- Monitor: Check Cloud Run logs and metrics in GCP Console

## Backward Compatibility

- ✅ Static version at `docs/ag-organism.html` still works
- ✅ Marked as deprecated with notice in documentation
- ✅ Links in index.html point to static version (can be updated later)
- ✅ HTML supports both static and Cloud Run deployment modes

## Security Considerations

- ✅ Service account with minimal required permissions
- ✅ Public access enabled (consistent with other frontends)
- ✅ CORS handled by AG-UI Frontend (backend service)
- ✅ No secrets in environment variables
- ✅ Health check for monitoring

## Cost Estimate

**Cloud Run Pricing:**
- Minimum instances: 0 (scales to zero)
- Maximum instances: 3
- CPU: 0.5 per instance
- Memory: 512Mi per instance
- Estimated monthly cost: **$0.50 - $2.00** (mostly idle)

**Cost Breakdown:**
- CPU time: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million (first 2M free)
- Scales to zero = minimal cost when not in use

## Success Criteria

✅ Docker build completes successfully  
✅ Container runs and serves HTML  
✅ Environment variables injected correctly  
✅ Health endpoint responds  
✅ Terraform configuration valid  
✅ Workflow updated and builds added  
✅ Documentation updated  
✅ Static version still functional  

## Conclusion

Successfully migrated AG-Organism from static GitHub Pages to Cloud Run deployment, enabling:
- Dynamic environment configuration
- Proper integration with AG-UI infrastructure
- Consistent deployment pattern across services
- Better observability and monitoring
- Auto-scaling and cost efficiency

The static version remains as a fallback, but the Cloud Run version is now the recommended production deployment.

---

**Implementation Date**: 2024-12-06  
**Status**: ✅ Complete - Ready for Deployment  
**PR**: [Link to PR when created]
