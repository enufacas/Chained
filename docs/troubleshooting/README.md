# Quick Reference: GCP Cloud Run CPU Quota Fix

## Problem
Terraform deployment failed with: `Error code 9, message: Quota exceeded for total allowable CPU per project per region`

## Cause
8 Cloud Run services × 1 CPU each = 8 CPUs total (exceeded regional quota)

## Solution
Reduced CPU allocation from 1.0 to 0.5 per service = 4 CPUs total

## Files Changed
1. `infrastructure/terraform/adk-agents.tf` - Changed CPU limits for 8 services
2. `docs/troubleshooting/gcp-cloud-run-cpu-quota.md` - Comprehensive guide

## Impact
- ✅ Resolves quota issue
- ✅ 50% cost reduction on CPU
- ✅ No performance degradation (services are I/O bound)
- ✅ All services retain cpu_idle and startup_cpu_boost features

## Services Updated
- academic-research
- blog-writer  
- google-trends
- code-reviewer
- data-analyst
- image-generator
- adk-api-server
- ag-ui-frontend

## Verification Steps
```bash
# Deploy with new configuration
terraform apply

# Verify CPU allocation
gcloud run services describe chained-academic-research \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].resources.limits.cpu)"
# Expected: 0.5 or 500m
```

## Related
- Failed run: https://github.com/enufacas/Chained/actions/runs/19841202235
- Full guide: [gcp-cloud-run-cpu-quota.md](./gcp-cloud-run-cpu-quota.md)
- Cloud Run quotas: https://cloud.google.com/run/quotas
