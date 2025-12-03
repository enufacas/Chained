# 🏗️ Chained GCP Infrastructure

This directory contains Infrastructure as Code (IaC) and container configurations for deploying the Chained autonomous AI ecosystem on Google Cloud Platform.

## 📂 Directory Structure

```
infrastructure/
├── terraform/           # Terraform IaC for GCP resources
│   ├── main.tf          # Main infrastructure configuration
│   ├── variables.tf     # Input variables
│   ├── outputs.tf       # Output values
│   └── terraform.tfvars.example  # Example variable values
│
└── docker/              # Container configurations
    ├── website/         # Main website service
    │   ├── Dockerfile
    │   ├── main.py
    │   └── requirements.txt
    │
    ├── agent-gateway/   # A2A task gateway
    │   ├── Dockerfile
    │   ├── main.py
    │   └── requirements.txt
    │
    └── agent-worker/    # Task processing workers
        ├── Dockerfile
        ├── main.py
        └── requirements.txt
```

## 🚀 Quick Start

1. **Set up GCP credentials** - See [GCP Setup Guide](../docs/guides/GCP_SETUP_GUIDE.md)

2. **Configure GitHub Secrets**:
   - `GCP_PROJECT_ID` - Your GCP project ID
   - `GCP_SA_KEY` - Service account key JSON
   - `GCP_REGION` - Deployment region (default: us-central1)

3. **Configure GitHub Repository Variables** (Settings → Secrets and variables → Actions → Variables):
   - `GITHUB_REPO` - Repository for error-observer dispatch (format: `owner/repository`, e.g., `enufacas/Chained`)

4. **Deploy via GitHub Actions**:
   - Go to Actions → Deploy GCP Infrastructure → Run workflow

5. **Or deploy locally**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   terraform init
   terraform apply
   ```

## 💰 Estimated Costs

| Component | Monthly Cost |
|-----------|-------------|
| Cloud Run (3 services, scale-to-zero) | $5-15 |
| Pub/Sub | $0-2 |
| Firestore (free tier) | $0 |
| Artifact Registry | $1-3 |
| **Total** | **$6-20** |

Well under the $300 credit budget, leaving room for Gemini API usage.

## 🔧 Services

### Website (`chained-website`)
- Main dashboard and landing page
- Displays agent activity and system status
- Endpoints: `/`, `/health`, `/api/agents`, `/api/tasks`

### Agent Gateway (`chained-agent-gateway`)
- A2A-compatible task submission API
- Routes tasks to appropriate agents via Pub/Sub
- Stores task state in Firestore
- Endpoints: `/a2a/task`, `/agents`, `/health`

### Agent Worker (`chained-agent-worker`)
- Processes tasks from Pub/Sub queue
- Implements agent behaviors (analyze, implement, review, document)
- Updates task status in Firestore

## 📚 Documentation

- [GCP Setup Guide](../docs/guides/GCP_SETUP_GUIDE.md) - Complete setup instructions
- [GCP Infrastructure Brainstorm](../docs/proposals/GCP_INFRASTRUCTURE_BRAINSTORM.md) - Architecture decisions
- [Deploy Workflow](../.github/workflows/deploy-gcp-infrastructure.yml) - CI/CD configuration

## 🛠️ Local Development

```bash
# Build and run website locally
cd docker/website
docker build -t chained-website .
docker run -p 8080:8080 chained-website

# Test health endpoint
curl http://localhost:8080/health
```

## 🔄 CI/CD Pipeline

The deployment pipeline (`deploy-gcp-infrastructure.yml`):

1. **Validate** - Check configuration and secrets
2. **Terraform** - Deploy/update GCP infrastructure
3. **Build** - Build container images for each service
4. **Deploy** - Push to Artifact Registry, deploy to Cloud Run
5. **Verify** - Health check all services

Triggers:
- Push to `main` (changes to `infrastructure/`)
- Manual workflow dispatch
