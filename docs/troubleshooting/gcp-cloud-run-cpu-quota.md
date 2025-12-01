# GCP Cloud Run CPU Quota Troubleshooting

## Issue: Quota Exceeded for Total Allowable CPU

### Problem Description

When deploying multiple Cloud Run services via Terraform, you may encounter this error:

```
Error: Error waiting for Updating Service: Error code 9, message: Quota exceeded for total allowable CPU per project per region.
```

### Root Cause

GCP Cloud Run has a quota limit on the total amount of CPU that can be allocated across all services in a project per region. The default quota varies by region but is typically 8-10 CPUs.

In our case:
- **8 Cloud Run services** each configured with **1 CPU** = **8 total CPUs**
- This exceeded the available quota in the region

### Services Affected

1. `chained-academic-research`
2. `chained-blog-writer`
3. `chained-google-trends`
4. `chained-code-reviewer`
5. `chained-data-analyst`
6. `chained-image-generator`
7. `chained-adk-api-server`
8. `chained-ag-ui-frontend`

## Solution

### Option 1: Reduce CPU Allocation (Recommended)

Since all services use `cpu_idle = true` (scale to zero when idle), they don't need a full CPU core. Reducing CPU allocation to **0.5 CPU per service** cuts total usage in half:

- **Before**: 8 services × 1 CPU = 8 CPUs
- **After**: 8 services × 0.5 CPU = 4 CPUs

**Implementation**:

Edit `infrastructure/terraform/adk-agents.tf` and change each service's CPU limit:

```hcl
resources {
  limits = {
    cpu    = "0.5"  # Changed from "1"
    memory = "512Mi"
  }
  cpu_idle          = true
  startup_cpu_boost = true
}
```

**Performance Impact**: Minimal. These are AI agents with:
- Moderate request volumes
- CPU-idle enabled (no CPU used when idle)
- startup_cpu_boost enabled (extra CPU during cold starts)
- Most workload is I/O bound (API calls to Gemini/Vertex AI)

### Option 2: Request Quota Increase

If you need more CPU:

1. Go to [GCP Quotas Page](https://console.cloud.google.com/iam-admin/quotas)
2. Filter by:
   - Service: Cloud Run
   - Metric: `CPU allocation per project per region`
3. Select your region
4. Click "Edit Quotas"
5. Request an increase (e.g., 16 CPUs)

**Note**: Approval can take 2-3 business days.

### Option 3: Distribute Services Across Regions

Deploy some services to different regions to spread CPU usage:

- Primary services (frequently used): `us-central1`
- Secondary services: `us-east1` or `us-west1`

**Considerations**:
- Increased latency between services
- More complex Terraform configuration
- Higher egress costs for cross-region traffic

## Verification

After applying the fix, verify the deployment:

```bash
# Check service status
gcloud run services list --region=us-central1

# Check CPU allocation
gcloud run services describe chained-academic-research \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].resources.limits.cpu)"
```

Expected output: `0.5` or `500m` (both represent 0.5 CPU)

## Monitoring CPU Usage

Check actual CPU usage in Cloud Console:

1. Navigate to [Cloud Run Console](https://console.cloud.google.com/run)
2. Select a service
3. Go to "Metrics" tab
4. View "Container CPU utilization"

Typical idle CPU usage should be near 0% with `cpu_idle = true`.

## Best Practices

1. **Right-size CPU allocation**: Start with minimal CPU and increase if needed
2. **Use CPU idle**: Enable `cpu_idle = true` for services with variable load
3. **Monitor usage**: Set up alerts for high CPU utilization
4. **Plan for scale**: Request quota increases before deploying many services
5. **Document quotas**: Keep track of quota limits for each region/project

## Related Resources

- [Cloud Run Quotas](https://cloud.google.com/run/quotas)
- [Cloud Run CPU Allocation](https://cloud.google.com/run/docs/configuring/cpu)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [GCP Quotas Management](https://cloud.google.com/docs/quota)

## Troubleshooting Failed Workflow

**Workflow Run**: https://github.com/enufacas/Chained/actions/runs/19841202235

**Error in logs**:
```
Error: Error waiting for Updating Service: Error code 9, message: 
Quota exceeded for total allowable CPU per project per region.
```

**Fixed by**: Reducing Cloud Run CPU allocation from 1 to 0.5 per service

## Prevention

To avoid this issue in the future:

1. **Default to 0.5 CPU** for new services unless profiling shows higher needs
2. **Check quotas** before deploying multiple services: `gcloud compute project-info describe --project=PROJECT_ID`
3. **Use Terraform plan** to preview resource changes before applying
4. **Set up alerts** for quota usage approaching limits
5. **Document** CPU requirements for each service in terraform comments

## Additional Notes

- **Memory**: 512Mi is sufficient for these Python/Node.js AI agents
- **Scaling**: Services scale from 0 to 3 instances based on load
- **Timeout**: 300s timeout is appropriate for AI workloads with API calls
- **Cost**: Reducing CPU from 1 to 0.5 cuts CPU costs by 50%
