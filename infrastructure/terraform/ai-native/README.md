# AI-Native Control Plane - Terraform Configuration

This directory contains the **AI-Native Control Plane** infrastructure, which is **separate** from the base infrastructure.

## What's Included

- **Cloud SQL**: PostgreSQL 15 with pgvector extension
- **VPC Network**: Private networking for Cloud SQL
- **VPC Access Connector**: Cloud Run to Cloud SQL connectivity
- **AI Control Plane Service**: Autonomous infrastructure orchestration
- **Infra Runner Service**: Infrastructure execution engine
- **Service Accounts**: Least privilege IAM for services
- **Secret Manager**: API keys (OpenAI, Gemini)
- **Cloud Monitoring**: Alerts for errors and database connections

## Why Separate?

The AI-Native Control Plane is deployed separately because:

1. **Independent Lifecycle**: Can be deployed/destroyed without affecting base infrastructure
2. **Cost Management**: Cloud SQL has ongoing costs; can disable when not needed
3. **Complexity**: Requires VPC, Cloud SQL, and additional setup
4. **Optional**: Base infrastructure works without AI control plane

## Deployment

### Prerequisites

1. GCP project with billing enabled
2. GCP service account with appropriate permissions
3. GitHub secrets configured
4. **Base infrastructure already deployed** (see `../base/`)

### Manual Deployment

```bash
cd infrastructure/terraform/ai-native

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

The `.github/workflows/ai-native-deploy.yml` workflow automatically deploys this infrastructure on:
- Push to `main` branch (if paths match)
- Manual workflow dispatch

### Post-Deployment Setup

After deployment, you must manually set API keys:

```bash
# Set OpenAI API key
echo -n "YOUR_OPENAI_KEY" | gcloud secrets versions add ai-native-openai-api-key --data-file=-

# Set Gemini API key
echo -n "YOUR_GEMINI_KEY" | gcloud secrets versions add ai-native-gemini-api-key --data-file=-
```

## Directory Structure

```
ai-native/
├── main.tf                         # Provider config + API services
├── ai-native-control-plane.tf      # All AI control plane resources
├── variables.tf                    # Input variables
├── outputs.tf                      # Output values
├── terraform.tfvars.example        # Example configuration
└── README.md                       # This file
```

## Cost Estimation

**Monthly cost**: $15-50 (depending on database tier)

- Cloud SQL (db-f1-micro): ~$10-15/month (no scale-to-zero)
- Cloud SQL (db-custom-2-7680): ~$50/month for production
- VPC Access Connector: ~$0.50-1/month
- Cloud Run services: ~$5-10/month

**Note**: Cloud SQL runs continuously and cannot scale to zero, unlike Cloud Run.

## Architecture

```
┌─────────────────────────────────────────┐
│   AI Control Plane (Cloud Run)          │
│   - Receives user requests               │
│   - Plans infrastructure changes         │
│   - Stores state in Cloud SQL            │
└────────────┬────────────────────────────┘
             │ VPC Connector
             ↓
┌─────────────────────────────────────────┐
│   Cloud SQL (PostgreSQL + pgvector)     │
│   - Infrastructure state                │
│   - Vector embeddings for AI context    │
└─────────────────────────────────────────┘
             ↑
             │ Private IP
             ↓
┌─────────────────────────────────────────┐
│   Infra Runner (Cloud Run)              │
│   - Executes infrastructure operations  │
│   - Manages GCP resources                │
└─────────────────────────────────────────┘
```

## Related Documentation

- [Main Infrastructure README](../../README.md)
- [Base Infrastructure](../base/README.md)
- [AI-Native Control Plane Design](../AI_NATIVE_README.md)
