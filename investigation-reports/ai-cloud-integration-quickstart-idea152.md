# AI-Cloud Integration Quick Start Guide
## Mission idea:152 - Implementation Reference

**Created by:** @connector-ninja  
**Date:** 2025-12-15  
**For:** Chained Autonomous AI Ecosystem

---

## 🚀 Quick Start: Week 1 Implementation

### Prerequisites

**GCP Setup:**
1. Create service account: `chained-monitoring@PROJECT_ID.iam.gserviceaccount.com`
2. Grant roles:
   - `roles/monitoring.viewer`
   - `roles/billing.viewer`
   - `roles/run.viewer`
3. Generate key (JSON format)

**GitHub Setup:**
1. Add secrets in repository settings:
   - `GCP_SA_KEY`: Service account JSON key
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_BILLING_ACCOUNT`: Billing account ID

### Step-by-Step: Cloud Monitoring Integration

#### Step 1: Create Workflow (5 minutes)

Create `.github/workflows/cloud-monitoring-sync.yml`:

```yaml
name: Cloud Monitoring Sync

on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:

permissions:
  contents: write
  issues: write

jobs:
  sync-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: pip install google-cloud-monitoring google-cloud-billing
      
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Fetch Metrics
        run: |
          python tools/cloud_monitoring/fetch_metrics.py \
            --project-id=${{ secrets.GCP_PROJECT_ID }} \
            --output=docs/data/cloud-metrics.json
      
      - name: Commit Updates
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/data/cloud-metrics.json
          if ! git diff --staged --quiet; then
            git commit -m "chore: update cloud monitoring data"
            git push
          fi
```

#### Step 2: Create Metrics Fetcher (15 minutes)

Create `tools/cloud_monitoring/fetch_metrics.py`:

```python
#!/usr/bin/env python3
"""Fetch Cloud Monitoring metrics for Chained services"""

import argparse
import json
from datetime import datetime, timedelta
from google.cloud import monitoring_v3

def fetch_metrics(project_id: str, hours: int = 24):
    """Fetch metrics for all Cloud Run services"""
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    interval = monitoring_v3.TimeInterval({
        "end_time": {"seconds": int(end_time.timestamp())},
        "start_time": {"seconds": int(start_time.timestamp())}
    })
    
    # Services to monitor
    services = [
        "chained-ag-ui-frontend",
        "chained-academic-research",
        "chained-blog-writer",
        "chained-google-trends",
        "chained-adk-api-server"
    ]
    
    results = {
        "timestamp": end_time.isoformat(),
        "period_hours": hours,
        "services": {}
    }
    
    for service in services:
        # Fetch CPU utilization
        cpu_filter = (
            f'metric.type = "run.googleapis.com/container/cpu/utilizations" '
            f'AND resource.labels.service_name = "{service}"'
        )
        
        cpu_data = client.list_time_series(
            request={
                "name": project_name,
                "filter": cpu_filter,
                "interval": interval,
            }
        )
        
        cpu_values = []
        for result in cpu_data:
            for point in result.points:
                cpu_values.append(point.value.double_value)
        
        results["services"][service] = {
            "cpu_avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0.0,
            "cpu_max": max(cpu_values) if cpu_values else 0.0
        }
    
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--hours", type=int, default=24)
    args = parser.parse_args()
    
    metrics = fetch_metrics(args.project_id, args.hours)
    
    with open(args.output, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✅ Metrics written to {args.output}")

if __name__ == "__main__":
    main()
```

#### Step 3: Create Data Directory (1 minute)

```bash
mkdir -p docs/data
touch docs/data/.gitkeep
```

#### Step 4: Test Workflow (5 minutes)

```bash
# Run locally (requires GCP credentials)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

python tools/cloud_monitoring/fetch_metrics.py \
  --project-id=YOUR_PROJECT \
  --output=docs/data/cloud-metrics.json

# Verify output
cat docs/data/cloud-metrics.json
```

#### Step 5: Enable Workflow (2 minutes)

1. Commit changes:
```bash
git add .github/workflows/cloud-monitoring-sync.yml
git add tools/cloud_monitoring/fetch_metrics.py
git add docs/data/.gitkeep
git commit -m "feat: add cloud monitoring integration"
git push
```

2. Trigger manually:
   - Go to Actions tab → Cloud Monitoring Sync → Run workflow

3. Verify:
   - Check workflow logs
   - Verify `docs/data/cloud-metrics.json` created
   - Review metrics data

---

## 📊 Expected Week 1 Outcomes

**By End of Day 1:**
- ✅ Cloud Monitoring workflow created
- ✅ Metrics collection working
- ✅ First data snapshot captured

**By End of Week 1:**
- ✅ 7 days of metrics collected (28 snapshots at 4-hour intervals)
- ✅ Cost baseline established
- ✅ Utilization patterns identified
- ✅ 3-5 optimization opportunities discovered

---

## 🎯 Week 2: Analysis & Planning

### Analyze Baseline Data

```python
# Simple analysis script
import json
from glob import glob

# Load all metrics
metrics_files = sorted(glob('docs/data/cloud-metrics-*.json'))
all_metrics = [json.load(open(f)) for f in metrics_files]

# Calculate averages
for service in all_metrics[0]['services'].keys():
    cpu_values = [m['services'][service]['cpu_avg'] for m in all_metrics]
    avg_cpu = sum(cpu_values) / len(cpu_values)
    
    print(f"{service}:")
    print(f"  Average CPU: {avg_cpu:.1%}")
    print(f"  Max CPU: {max(cpu_values):.1%}")
    
    # Optimization opportunity?
    if avg_cpu < 0.20:
        print(f"  ⚠️ OPTIMIZATION: CPU <20%, consider right-sizing")
```

### Identify Optimizations

Based on 7-day baseline, identify:

1. **Scale-to-Zero Candidates:**
   - Services with <10 requests/hour
   - Low CPU/memory usage
   - Non-critical paths

2. **Right-Sizing Candidates:**
   - CPU utilization <20%
   - Memory utilization <30%
   - Over-provisioned resources

3. **Pattern-Based Scaling:**
   - Daily/weekly traffic patterns
   - Predictable spike times
   - Scale-down opportunities

---

## 💰 Week 3-5: Cost Optimization

See full implementation in:
- `investigation-reports/ai-cloud-ecosystem-integration-proposal-idea152.md`
- Section: "Integration #2: Cost Optimization Agent"

**Key Steps:**
1. Implement optimizer.py
2. Create cost-optimization.yml workflow
3. Test in dry-run mode
4. Enable auto-approval for low-risk changes
5. Monitor results

---

## 📈 Week 6-7: Predictive Scaling

See full implementation in:
- `investigation-reports/ai-cloud-ecosystem-integration-proposal-idea152.md`
- Section: "Integration #3: Predictive Auto-Scaling"

**Key Steps:**
1. Create predictive-scaling.yml workflow
2. Configure for 3 known patterns:
   - Daily learning (9am UTC)
   - Agent missions (6am, 6pm UTC)
   - Weekend scale-down
3. Test pre-scaling effectiveness
4. Measure cold start reduction

---

## 🔍 Monitoring & Validation

### Key Metrics to Track

**Cost Metrics:**
- [ ] Daily cloud spend
- [ ] Cost per service
- [ ] Savings realized
- [ ] Optimization opportunities identified/implemented

**Performance Metrics:**
- [ ] Cold start rate
- [ ] P95 latency
- [ ] Request success rate
- [ ] Resource utilization

**Automation Metrics:**
- [ ] Auto-approved optimizations
- [ ] Manual reviews required
- [ ] Rollbacks executed
- [ ] Anomalies detected

### Success Criteria (8-Week Checkpoint)

- [ ] **Cost:** 50%+ reduction achieved
- [ ] **Performance:** <1% cold start rate
- [ ] **Automation:** 90%+ optimizations autonomous
- [ ] **Reliability:** Zero incidents from changes

---

## 🆘 Troubleshooting

### Workflow Fails

**Error: "Unable to authenticate"**
- Check GCP_SA_KEY secret is set correctly
- Verify service account has required permissions
- Test locally with same credentials

**Error: "Metrics not found"**
- Verify service names match Cloud Run services
- Check services are deployed and receiving traffic
- Ensure monitoring API is enabled

### No Optimizations Found

**Expected but not happening:**
- Check if baseline period is too short (<7 days)
- Verify threshold values are appropriate
- Review metrics collection for completeness

### Auto-Approval Not Working

**Changes require manual review:**
- Check auto-approval criteria
- Verify cost impact is <$5/month
- Review utilization thresholds

---

## 📚 Additional Resources

**Documentation:**
- [Research Report](investigation-reports/ai-cloud-integration-research-idea152.md)
- [Integration Proposal](investigation-reports/ai-cloud-ecosystem-integration-proposal-idea152.md)
- [Mission Completion Summary](MISSION_COMPLETION_COMMENT_idea152.md)

**Google Cloud Docs:**
- [Cloud Monitoring API](https://cloud.google.com/monitoring/api/v3)
- [Cloud Billing API](https://cloud.google.com/billing/docs/reference/rest)
- [Cloud Run Autoscaling](https://cloud.google.com/run/docs/about-instance-autoscaling)

**Support:**
- Create GitHub issue with label `ai-cloud-integration`
- Reference mission ID: idea:152
- Tag: @connector-ninja

---

**Quick Start Status:** Ready to implement  
**Estimated Time:** Week 1 = 2-3 hours setup  
**Next Checkpoint:** End of Week 1 (metrics baseline)

**Created by @connector-ninja for the Chained autonomous AI ecosystem** 🚀
