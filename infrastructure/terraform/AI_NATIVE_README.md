# AI-Native Control Plane - Deployment Guide

This directory contains the complete infrastructure-as-code for deploying the AI-Native Control Plane to Google Cloud Platform.

## 🎯 What Gets Deployed

The AI-Native Control Plane is a fully autonomous AI-driven infrastructure management system that includes:

### Core Services
- **AI Control Plane** (`ai-control-plane`): Multi-agent LangGraph system for natural language infrastructure commands
- **Infra Runner** (`infra-runner`): GCP operations executor (deploys to GCS, Cloud Run, handles scaling)
- **State DB**: Cloud SQL PostgreSQL 15 with pgvector extension for semantic memory

### Infrastructure
- **VPC Network**: Private networking for services
- **VPC Access Connector**: Cloud Run to Cloud SQL connectivity  
- **Cloud SQL**: PostgreSQL 15 with pgvector for operations state and semantic memory
- **Secret Manager**: Secure storage for API keys (OpenAI, Gemini)
- **Service Accounts**: Least-privilege IAM for each service
- **Cloud Monitoring**: Alerts for errors, latency, and database connections

## 📋 Prerequisites

### Local Requirements
- **gcloud CLI** (latest version) - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform** >= 1.0.0 - [Install](https://developer.hashicorp.com/terraform/downloads)
- **Docker** - [Install](https://docs.docker.com/get-docker/)
- **jq** (JSON processor) - `brew install jq` or `apt-get install jq`

### GCP Requirements
- Google Cloud Project with billing enabled
- Owner or Editor permissions on the project
- API services can be enabled (done automatically by script)

### API Keys
- **Gemini API Key** (recommended, free tier) - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- OR **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## 🚀 Quick Start - Automated Deployment

The fastest way to deploy is using the bootstrap script:

```bash
# Navigate to terraform directory
cd infrastructure/terraform

# Run bootstrap deployment
./bootstrap-deploy.sh YOUR_PROJECT_ID us-central1 dev

# Follow the prompts to:
# 1. Set API keys in Secret Manager
# 2. Run database migrations
```

That's it! The script will:
1. ✅ Enable all required GCP APIs
2. ✅ Create Artifact Registry
3. ✅ Build and push Docker images
4. ✅ Deploy all infrastructure with Terraform
5. 📋 Provide commands for manual steps (API keys, migrations)

## 📖 Manual Deployment (Step-by-Step)

If you prefer more control, follow these detailed steps:

### Step 1: Enable APIs

```bash
gcloud config set project YOUR_PROJECT_ID

# Enable required services
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  servicenetworking.googleapis.com \
  vpcaccess.googleapis.com \
  compute.googleapis.com \
  secretmanager.googleapis.com
```

### Step 2: Build and Push Container Images

```bash
# Set variables
PROJECT_ID="your-project-id"
REGION="us-central1"
REGISTRY_URL="$REGION-docker.pkg.dev/$PROJECT_ID/chained"

# Create Artifact Registry
gcloud artifacts repositories create chained \
  --repository-format=docker \
  --location=$REGION \
  --description="AI-Native Control Plane images"

# Configure docker auth
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build and push images (from repo root)
cd ../..

# Infra Runner
docker build -t $REGISTRY_URL/infra-runner:latest \
  -f services/infra-runner/Dockerfile \
  services/infra-runner/
docker push $REGISTRY_URL/infra-runner:latest

# AI Control Plane
docker build -t $REGISTRY_URL/ai-control-plane:latest \
  -f services/ai-control-plane/Dockerfile \
  services/ai-control-plane/
docker push $REGISTRY_URL/ai-control-plane:latest
```

### Step 3: Configure Terraform

```bash
cd infrastructure/terraform

# Copy example tfvars
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars
nano terraform.tfvars
```

Example `terraform.tfvars`:
```hcl
project_id  = "your-gcp-project-id"
region      = "us-central1"
environment = "dev"  # or "staging", "production"

# Container images
ai_native_control_plane_image = "us-central1-docker.pkg.dev/your-project/chained/ai-control-plane:latest"
ai_native_infra_runner_image  = "us-central1-docker.pkg.dev/your-project/chained/infra-runner:latest"

# Database configuration
ai_native_db_tier      = "db-f1-micro"       # Smallest for dev
ai_native_db_disk_size = 10                   # GB

# LLM provider
ai_native_llm_provider = "gemini"  # or "openai"

# Optional: Alert email
alert_email = "your-email@example.com"
```

### Step 4: Deploy with Terraform

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply
```

This will deploy:
- VPC and networking
- Cloud SQL instance with PostgreSQL 15
- Cloud Run services (ai-control-plane, infra-runner)
- Secret Manager secrets (empty, need to be filled)
- Service accounts and IAM bindings
- Monitoring alerts

### Step 5: Set API Keys

```bash
# Set Gemini API Key (recommended)
echo -n 'YOUR_GEMINI_API_KEY' | gcloud secrets versions add ai-native-gemini-api-key --data-file=-

# OR Set OpenAI API Key
echo -n 'YOUR_OPENAI_API_KEY' | gcloud secrets versions add ai-native-openai-api-key --data-file=-
```

Get keys from:
- Gemini: https://aistudio.google.com/app/apikey (free tier available)
- OpenAI: https://platform.openai.com/api-keys

### Step 6: Run Database Migrations

```bash
# Get Cloud SQL instance name
INSTANCE_NAME=$(terraform output -raw ai_native_database_instance)

# Connect to database
gcloud sql connect $INSTANCE_NAME \
  --user=ai_native_admin \
  --database=ai_native_control_plane

# Run migrations (in psql prompt)
\i ../../services/state-db/migrations/001_initial_schema.sql
\i ../../services/state-db/migrations/002_add_vector_support.sql
\q
```

### Step 7: Test the System

```bash
# Get AI Control Plane URL
CONTROL_PLANE_URL=$(terraform output -raw ai_native_control_plane_url)

# Test with a simple request
curl -X POST $CONTROL_PLANE_URL/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "Create a simple blog website",
    "user_id": "test-user",
    "mode": "normal",
    "dry_run": false
  }'
```

Expected response:
```json
{
  "success": true,
  "intent": "create_app",
  "message": "✅ Successfully deployed your application!",
  "urls": [{"label": "Website", "url": "https://..."}],
  "execution_time_seconds": 45
}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI-NATIVE CONTROL PLANE                  │
│                  (Natural Language Interface)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────┐
        │      AI Control Plane Service        │
        │    (Cloud Run - 2 CPU, 2Gi RAM)      │
        │                                      │
        │  LangGraph Multi-Agent System:      │
        │  Planner → Policy → Memory →        │
        │  Builder → Infra → State → Output   │
        └──────────────────────────────────────┘
                 │              │
                 ▼              ▼
    ┌─────────────────┐   ┌──────────────┐
    │  Infra Runner   │   │  Cloud SQL   │
    │   (Cloud Run)   │   │ PostgreSQL   │
    │                 │   │  + pgvector  │
    │ GCP Operations: │   │              │
    │ • GCS Buckets   │   │ State:       │
    │ • Cloud Run     │   │ • Apps       │
    │ • Scaling       │   │ • Operations │
    │ • Domains       │   │ • Patterns   │
    └─────────────────┘   │ • Memory     │
           │              └──────────────┘
           ▼
    ┌─────────────────┐
    │  Google Cloud   │
    │  • Storage      │
    │  • Cloud Run    │
    │  • Domains      │
    └─────────────────┘
```

## 💰 Cost Estimate

### Development Environment
- **Cloud Run**: ~$0-5/month (scales to zero)
- **Cloud SQL**: ~$10-15/month (db-f1-micro)
- **VPC Connector**: ~$10/month
- **Networking**: ~$1-2/month
- **LLM API**: ~$5-10/month (Gemini free tier + OpenAI)

**Total**: ~$26-42/month

### Production Environment
- **Cloud Run**: ~$20-50/month (min instances)
- **Cloud SQL**: ~$50-100/month (db-custom-2-7680, regional)
- **VPC Connector**: ~$30/month (more throughput)
- **Networking**: ~$5-10/month
- **LLM API**: ~$50-200/month (higher usage)

**Total**: ~$155-390/month

## 🔒 Security Best Practices

1. **Least Privilege IAM**: Each service account has only required permissions
2. **Private Networking**: Cloud SQL only accessible via VPC
3. **Secret Manager**: API keys stored encrypted, not in code
4. **SSL/TLS**: All communication encrypted
5. **Deletion Protection**: Production database has deletion protection enabled

## 📊 Monitoring

After deployment, monitor your system:

```bash
# View Cloud Run logs
gcloud run services logs read ai-native-control-plane --limit=50

gcloud run services logs read ai-native-infra-runner --limit=50

# View Cloud SQL metrics
gcloud sql operations list --instance=$INSTANCE_NAME

# Check service health
curl $(terraform output -raw ai_native_control_plane_url)/health
curl $(terraform output -raw ai_native_infra_runner_url)/health
```

Cloud Monitoring dashboards are automatically created for:
- Request rates and latencies
- Error rates (5xx responses)
- Database connections
- Memory and CPU usage

## 🔄 Updating the System

### Update Container Images

```bash
# Rebuild and push
docker build -t $REGISTRY_URL/ai-control-plane:latest services/ai-control-plane/
docker push $REGISTRY_URL/ai-control-plane:latest

# Terraform will detect the change and redeploy
terraform apply
```

### Update Infrastructure

```bash
# Modify terraform files
nano ai-native-control-plane.tf

# Preview changes
terraform plan

# Apply changes
terraform apply
```

### Run New Migrations

```bash
# Connect to database
gcloud sql connect $INSTANCE_NAME --user=ai_native_admin --database=ai_native_control_plane

# Run new migration
\i ../../services/state-db/migrations/003_new_migration.sql
```

## 🧹 Cleanup

To completely remove the infrastructure:

```bash
# Destroy all resources
terraform destroy

# Optionally delete artifact registry
gcloud artifacts repositories delete chained --location=$REGION

# Optionally delete secrets
gcloud secrets delete ai-native-openai-api-key
gcloud secrets delete ai-native-gemini-api-key
gcloud secrets delete ai-native-db-connection-string
```

**Warning**: This will delete the database and all data. Make sure to backup first if needed.

## 🐛 Troubleshooting

### Cloud SQL Connection Issues

```bash
# Check Cloud SQL is running
gcloud sql instances describe $INSTANCE_NAME

# Verify VPC connector
gcloud compute networks vpc-access connectors describe ai-native-vpc-connector --region=$REGION

# Test database connection
gcloud sql connect $INSTANCE_NAME --user=ai_native_admin
```

### Service Deployment Issues

```bash
# Check Cloud Run service status
gcloud run services describe ai-native-control-plane --region=$REGION

# View recent logs
gcloud run services logs read ai-native-control-plane --limit=100
```

### API Key Issues

```bash
# Verify secrets exist
gcloud secrets versions list ai-native-gemini-api-key
gcloud secrets versions list ai-native-openai-api-key

# Test secret access from service account
gcloud secrets versions access latest --secret=ai-native-gemini-api-key \
  --impersonate-service-account=ai-control-plane-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## 📚 Additional Resources

- [Master Control File](../../.github/copilot/tasks/ai-native-control-plane.md) - Complete project specification
- [Phase 6 Implementation](../../docs/ai-native/PHASE_6_IMPLEMENTATION_SUMMARY.md) - Current progress
- [Architecture Overview](../../docs/ai-native/01_overview.md) - System design
- [API Documentation](../../docs/ai-native/04_infra_runner_api.md) - Endpoint specifications

## 🤝 Contributing

When making changes to infrastructure:

1. Test changes in dev environment first
2. Update this README if configuration changes
3. Document any new manual steps
4. Update terraform.tfvars.example
5. Test full deployment with bootstrap script

---

**Status**: Phase 6 Complete - Ready for Production Deployment  
**Last Updated**: 2025-12-06  
**Maintainer**: Chained Development Team
