# Deployment Pipeline Separation - Implementation Summary

## Problem Statement

The `deploy-gcp-infrastructure.yml` workflow was deploying ALL infrastructure including the AI-native control plane. The workflow run https://github.com/enufacas/Chained/actions/runs/20015206748/job/57391402717 should NOT deal with or deploy AI control plane infrastructure.

## Solution Implemented

Completely separated the Terraform configurations into two independent directories with separate deployment workflows.

## Changes Made

### 1. New Directory Structure

Created two separate Terraform configuration directories:

```
infrastructure/terraform/
├── base/                          # Base Infrastructure
│   ├── main.tf                    # Provider + Cloud Run services  
│   ├── adk-agents.tf              # 8 ADK agents
│   ├── blog.tf                    # Blog storage
│   ├── variables.tf               # Base-specific variables
│   ├── outputs.tf                 # Base-specific outputs
│   ├── terraform.tfvars.example
│   └── README.md
│
└── ai-native/                     # AI-Native Control Plane
    ├── main.tf                    # Provider + API services
    ├── ai-native-control-plane.tf # Cloud SQL, VPC, AI services
    ├── variables.tf               # AI-native variables
    ├── outputs.tf                 # AI-native outputs
    ├── terraform.tfvars.example
    └── README.md
```

### 2. Base Infrastructure (`infrastructure/terraform/base/`)

**Includes:**
- Cloud Run: Website, Agent Gateway, Agent Worker
- ADK Agents: Academic Research, Blog Writer, Google Trends, Code Reviewer, Data Analyst, Image Generator
- AG-UI Frontend, AG-Organism Frontend
- Error Observer, Log Consumer
- ADK API Server
- Cloud Pub/Sub (agent messaging)
- Firestore (agent state)
- Cloud Storage (blog bucket)
- Artifact Registry
- Monitoring & Alerting

**Cost:** $10-25/month (scales to zero)

### 3. AI-Native Control Plane (`infrastructure/terraform/ai-native/`)

**Includes:**
- Cloud SQL (PostgreSQL + pgvector)
- VPC Network + Subnet
- VPC Access Connector
- AI Control Plane Service
- Infra Runner Service
- Service Accounts
- Secret Manager (API keys)
- Monitoring & Alerting

**Cost:** $15-50/month (Cloud SQL always running)

### 4. Workflow Updates

#### `deploy-gcp-infrastructure.yml`
- **Working directory**: Changed to `infrastructure/terraform/base/`
- **Path triggers**: Now only triggers on:
  - `infrastructure/terraform/base/**`
  - `infrastructure/docker/website/**`
  - `infrastructure/docker/agent-gateway/**`
  - `infrastructure/docker/agent-worker/**`
  - `infrastructure/docker/adk-agents/**`
  - `.github/workflows/deploy-gcp-infrastructure.yml`
- **Behavior**: Deploys ONLY base infrastructure, never touches AI control plane

#### `ai-native-deploy.yml`
- **Working directory**: Changed to `infrastructure/terraform/ai-native/`
- **Path triggers**: Now only triggers on:
  - `infrastructure/terraform/ai-native/**`
  - `services/**` (AI control plane services)
  - `.github/workflows/ai-native-deploy.yml`
- **Behavior**: Deploys ONLY AI control plane infrastructure

### 5. Documentation

Created comprehensive READMEs:
- `infrastructure/terraform/README.md` - Overview of separation
- `infrastructure/terraform/base/README.md` - Base infrastructure guide
- `infrastructure/terraform/ai-native/README.md` - AI control plane guide

## Benefits

1. **Independent Lifecycle**: Can deploy/destroy AI control plane without affecting base infrastructure
2. **Cost Control**: Can disable AI control plane ($15-50/month savings) when not needed
3. **Clear Ownership**: Each workflow only triggers for relevant changes
4. **Faster Deployments**: Only deploy what changed (smaller, faster runs)
5. **Reduced Complexity**: Each deployment is simpler to understand and debug
6. **Better Testing**: Can test base infrastructure without AI control plane dependencies
7. **Separate State Files**: No risk of accidentally destroying one when working on the other

## Deployment Guide

### Initial Setup (New Installation)

1. **Deploy base infrastructure first**:
   ```bash
   cd infrastructure/terraform/base
   terraform init
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   terraform apply
   ```

2. **Optionally deploy AI-Native Control Plane**:
   ```bash
   cd infrastructure/terraform/ai-native
   terraform init
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   terraform apply
   ```

### Via GitHub Actions

Both workflows run automatically:

- **Base infrastructure**: Push changes to `infrastructure/terraform/base/` or related Docker files
- **AI-Native**: Push changes to `infrastructure/terraform/ai-native/` or `services/`

Or trigger manually via workflow_dispatch.

## Verification

The separation ensures that:

✅ The `deploy-gcp-infrastructure.yml` workflow (run ID 20015206748) now:
- Works in `infrastructure/terraform/base/` directory
- Only deploys base Cloud Run services, ADK agents, Pub/Sub, Firestore, Storage
- Never touches Cloud SQL, VPC, or AI control plane services
- Runs faster and with less complexity

✅ The `ai-native-deploy.yml` workflow:
- Works in `infrastructure/terraform/ai-native/` directory  
- Only deploys Cloud SQL, VPC, AI control plane services
- Independent of base infrastructure
- Can be disabled to save costs

## Migration from Old Structure

If you were using the old monolithic Terraform configuration:

1. **Backup state**: `cp infrastructure/terraform/terraform.tfstate terraform.tfstate.backup`
2. **Deploy base first**: All existing resources (except AI-native) will be managed by base/
3. **Deploy AI-native separately**: If you need it, deploy it to the ai-native/ directory
4. **Import existing resources**: Use `terraform import` if needed for resources that already exist

## Cost Comparison

| Deployment | Monthly Cost | Scale to Zero? |
|------------|-------------|----------------|
| Base only | $10-25 | ✅ Yes |
| AI-Native only | $15-50 | ❌ No (Cloud SQL) |
| Both | $25-75 | Partial |

## Testing Recommendations

Before merging to main:

1. Test base infrastructure deployment in a clean GCP project
2. Verify all base services deploy correctly
3. Test AI-native deployment separately
4. Verify workflows trigger only for their respective paths
5. Confirm state files are independent

## Future Considerations

- Consider using GCS backend for Terraform state (currently local)
- May want to add dependency outputs (e.g., base exports project_id that ai-native imports)
- Could add a "deploy all" workflow that runs both in sequence

## Related Issues

Fixes the issue where `deploy-gcp-infrastructure.yml` was deploying AI control plane infrastructure when it shouldn't.

## Files Changed

- `.github/workflows/deploy-gcp-infrastructure.yml` - Updated to use base/
- `.github/workflows/ai-native-deploy.yml` - Updated to use ai-native/
- `infrastructure/terraform/base/*` - New directory with base infrastructure
- `infrastructure/terraform/ai-native/*` - New directory with AI control plane
- `infrastructure/terraform/README.md` - New overview documentation

## Files Unchanged

The original files remain in `infrastructure/terraform/` for backward compatibility:
- `main.tf`, `adk-agents.tf`, `blog.tf`, `ai-native-control-plane.tf`, `variables.tf`, `outputs.tf`

These can be removed in a future cleanup PR once the new structure is validated.
