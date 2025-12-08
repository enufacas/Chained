# Base Infrastructure - Terraform Configuration

This directory contains the **base infrastructure** for the Chained autonomous AI ecosystem, excluding the AI-Native Control Plane.

## What's Included

- **Cloud Run Services**: Website, Agent Gateway, Agent Worker
- **ADK Agents**: Academic Research, Blog Writer, Google Trends, Code Reviewer, Data Analyst, Image Generator
- **ADK API Server**: Bridge for google/adk-web
- **AG-UI Frontend**: CopilotKit-powered visualization
- **AG-Organism Frontend**: 3D visualization
- **Error Observer & Log Consumer**: A2A error handling
- **Cloud Pub/Sub**: Agent messaging
- **Firestore**: Agent state and memory
- **Cloud Storage**: Blog bucket
- **Artifact Registry**: Container images
- **Monitoring & Alerting**: Cloud Monitoring alerts

## What's NOT Included

- **AI-Native Control Plane**: Cloud SQL, VPC, AI Control Plane services (see `../ai-native/`)

## Deployment

### Prerequisites

1. GCP project with billing enabled
2. GCP service account with appropriate permissions
3. GitHub secrets configured (GCP_PROJECT_ID, GCP_SA_KEY, GOOGLE_API_KEY)

### Manual Deployment

```bash
cd infrastructure/terraform/base

# Initialize Terraform
terraform init

# Create terraform.tfvars from example
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Plan changes
terraform plan

# Apply changes
terraform apply
```

### Automated Deployment

The `.github/workflows/deploy-gcp-infrastructure.yml` workflow automatically deploys this infrastructure on:
- Push to `main` branch (if paths match)
- Manual workflow dispatch

## Directory Structure

```
base/
├── main.tf                    # Provider config + base Cloud Run services
├── adk-agents.tf              # ADK A2A agents
├── blog.tf                    # Blog storage bucket
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example configuration
└── README.md                  # This file
```

## Cost Estimation

**Monthly cost**: $10-25 (with scale-to-zero enabled)

- Cloud Run services: ~$5-10 (minimal usage)
- Firestore: Free tier
- Pub/Sub: Free tier
- Storage: ~$0.026/GB/month
- Artifact Registry: ~$0.10/GB/month

## Related Documentation

- [Main Infrastructure README](../../README.md)
- [AI-Native Control Plane](../ai-native/README.md)
- [GCP Setup Guide](../../../docs/guides/GCP_SETUP_GUIDE.md)
