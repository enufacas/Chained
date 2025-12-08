# ⚠️ DEPRECATED: Root Terraform Directory

**This directory is DEPRECATED as of PR #3704.**

## New Structure

The Terraform configuration has been split into two separate directories for better separation of concerns:

### 1. Base Infrastructure (`base/`)
Location: `infrastructure/terraform/base/`

Contains:
- Cloud Run services (website, agent-gateway, agent-worker)
- ADK agents (academic-research, blog-writer, google-trends, etc.)
- AG-UI frontend (CopilotKit visualization)
- Pub/Sub messaging
- Firestore database
- Blog storage bucket
- Artifact Registry

**Deployed by:**
- `.github/workflows/deploy-gcp-infrastructure.yml`
- `.github/workflows/deploy-adk-agents.yml`

**Cost:** ~$10-25/month (scales to zero)

### 2. AI-Native Control Plane (`ai-native/`)
Location: `infrastructure/terraform/ai-native/`

Contains:
- AI Control Plane service
- Infrastructure Runner service
- Cloud SQL database (PostgreSQL)
- VPC networking
- Private IP connectivity

**Deployed by:**
- `.github/workflows/ai-native-deploy.yml`

**Cost:** ~$15-50/month (always-on database)

## Migration Guide

**DO NOT** use the files in this root directory. They are kept temporarily for reference but will be removed.

### For Base Infrastructure
```bash
cd infrastructure/terraform/base
terraform init
terraform plan
terraform apply
```

### For AI-Native Control Plane
```bash
cd infrastructure/terraform/ai-native
terraform init
terraform plan
terraform apply
```

## Files to be Removed

The following files in this directory are deprecated and should not be used:
- `main.tf` - Split between `base/main.tf` and `ai-native/main.tf`
- `adk-agents.tf` - Moved to `base/adk-agents.tf`
- `ai-native-control-plane.tf` - Moved to `ai-native/ai-native-control-plane.tf`
- `blog.tf` - Moved to `base/blog.tf`
- `outputs.tf` - Split between `base/outputs.tf` and `ai-native/outputs.tf`
- `variables.tf` - Split between `base/variables.tf` and `ai-native/variables.tf`

## Why the Split?

**Independent Lifecycle Management:**
- Base infrastructure can be deployed/destroyed without affecting AI control plane
- AI control plane has expensive always-on components (Cloud SQL)
- Allows disabling AI control plane to save costs when not in use
- Separate Terraform state prevents cross-contamination

**Cost Control:**
- Base: $10-25/month, scales to zero
- AI-Native: $15-50/month, always-on database
- Can disable AI-Native to save ~$20-30/month when not needed

## Questions?

See:
- `infrastructure/terraform/base/README.md`
- `infrastructure/terraform/ai-native/README.md`
- PR #3704 for the original separation work
