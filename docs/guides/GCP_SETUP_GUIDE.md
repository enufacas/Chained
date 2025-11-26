# 🔧 GCP Infrastructure Setup Guide

This guide walks you through setting up the GCP infrastructure for the Chained autonomous AI ecosystem.

## 📋 Prerequisites

Before you begin, ensure you have:

1. **GCP Account** with billing enabled (using your $300 credit)
2. **gcloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **Terraform** installed (v1.0+) ([Install Guide](https://developer.hashicorp.com/terraform/install))
4. **GitHub repository** access with admin permissions

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Create a GCP Project

```bash
# Set your project ID (use a unique name)
export PROJECT_ID="chained-ai-demo"

# Create the project
gcloud projects create $PROJECT_ID --name="Chained AI Demo"

# Set as default project
gcloud config set project $PROJECT_ID

# Link billing account (required for Cloud Run)
# List billing accounts
gcloud billing accounts list

# Link billing (replace BILLING_ACCOUNT_ID)
gcloud billing projects link $PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

### Step 2: Enable Required APIs

```bash
# Enable all required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com
```

### Step 3: Create a Service Account

```bash
# Create service account for GitHub Actions
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployer" \
  --description="Service account for CI/CD deployments"

# Get the service account email
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant required permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/pubsub.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.owner"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/monitoring.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/resourcemanager.projectIamAdmin"

# Create and download the key
gcloud iam service-accounts keys create ~/gcp-sa-key.json \
  --iam-account=$SA_EMAIL

echo "✅ Service account key saved to ~/gcp-sa-key.json"
```

### Step 4: Configure GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_PROJECT_ID` | Your project ID (e.g., `chained-ai-demo`) | GCP project identifier |
| `GCP_SA_KEY` | Contents of `~/gcp-sa-key.json` | Service account key JSON |
| `GCP_REGION` | `us-central1` (recommended) | Deployment region |

**To get the SA key contents:**
```bash
cat ~/gcp-sa-key.json
```

Copy the entire JSON output and paste it as the `GCP_SA_KEY` secret value.

### Step 5: Deploy Infrastructure

**Option A: Via GitHub Actions (Recommended)**

1. Go to **Actions** tab in your repository
2. Select **Deploy GCP Infrastructure** workflow
3. Click **Run workflow**
4. Select options and click **Run workflow**

**Option B: Via Terraform Locally**

```bash
cd infrastructure/terraform

# Create terraform.tfvars
cat > terraform.tfvars << EOF
project_id = "$PROJECT_ID"
region     = "us-central1"
environment = "dev"
EOF

# Initialize and apply
terraform init
terraform plan
terraform apply
```

---

## 📦 What Gets Deployed

### Cloud Run Services

| Service | Description | URL Pattern |
|---------|-------------|-------------|
| `chained-website` | Main website and dashboard | `https://chained-website-xxx.run.app` |
| `chained-agent-gateway` | A2A task gateway API | `https://chained-agent-gateway-xxx.run.app` |
| `chained-agent-worker` | Task processing workers | `https://chained-agent-worker-xxx.run.app` |

### Supporting Infrastructure

- **Artifact Registry**: Container image storage
- **Cloud Pub/Sub**: Agent task messaging
- **Firestore**: Agent state and memory
- **Cloud Monitoring**: Metrics and alerting

---

## 💰 Cost Monitoring

### Set Up Budget Alerts

```bash
# Create a budget alert (optional but recommended)
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Chained Infrastructure Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=75 \
  --threshold-rule=percent=90
```

### Expected Costs

| Component | Estimated Monthly Cost |
|-----------|----------------------|
| Cloud Run (scale-to-zero) | $5-15 |
| Pub/Sub | $0-2 |
| Firestore (free tier) | $0 |
| Artifact Registry | $1-3 |
| **Total** | **$6-20** |

This leaves plenty of your $300 credit for Gemini API usage.

---

## 🔍 Verification

After deployment, verify everything is working:

### Check Service URLs

```bash
# Get website URL
gcloud run services describe chained-website \
  --region us-central1 \
  --format 'value(status.url)'

# Get gateway URL  
gcloud run services describe chained-agent-gateway \
  --region us-central1 \
  --format 'value(status.url)'
```

### Test Health Endpoints

```bash
# Test website
curl https://chained-website-xxx.run.app/health

# Test gateway
curl https://chained-agent-gateway-xxx.run.app/health

# Test gateway API
curl -X POST https://chained-agent-gateway-xxx.run.app/a2a/task \
  -H "Content-Type: application/json" \
  -d '{"type": "analyze", "input": {"topic": "test"}}'
```

---

## 🛠️ Troubleshooting

### Common Issues

#### "Permission denied" errors

```bash
# Ensure you're authenticated
gcloud auth login

# Check current project
gcloud config get-value project

# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions@"
```

#### "API not enabled" errors

```bash
# Re-enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

#### Terraform state issues

```bash
# Force unlock if stuck
terraform force-unlock LOCK_ID

# Re-initialize
terraform init -reconfigure
```

#### Container build failures

```bash
# Test local build first
cd infrastructure/docker/website
docker build -t test-website .
docker run -p 8080:8080 test-website
```

---

## 🔄 Updating the Infrastructure

### Update Container Images

Push changes to `infrastructure/docker/*` directories, and the CI/CD pipeline will automatically rebuild and deploy.

### Update Terraform Configuration

1. Modify files in `infrastructure/terraform/`
2. Push changes or run manually:
   ```bash
   terraform plan
   terraform apply
   ```

### Manual Redeployment

```bash
# Redeploy a specific service
gcloud run deploy chained-website \
  --source infrastructure/docker/website \
  --region us-central1
```

---

## 🧹 Cleanup

To avoid ongoing charges, delete resources when not needed:

```bash
# Delete Cloud Run services
gcloud run services delete chained-website --region us-central1 --quiet
gcloud run services delete chained-agent-gateway --region us-central1 --quiet
gcloud run services delete chained-agent-worker --region us-central1 --quiet

# Delete Pub/Sub resources
gcloud pubsub subscriptions delete chained-agent-tasks-sub --quiet
gcloud pubsub topics delete chained-agent-tasks --quiet
gcloud pubsub topics delete chained-agent-tasks-dlq --quiet

# Delete Artifact Registry
gcloud artifacts repositories delete chained --location us-central1 --quiet

# Or use Terraform to destroy everything
cd infrastructure/terraform
terraform destroy
```

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GitHub Actions GCP Authentication](https://github.com/google-github-actions/auth)
- [GCP Free Tier Details](https://cloud.google.com/free)

---

## 🔐 Security Best Practices

1. **Rotate service account keys** periodically
2. **Use Workload Identity** instead of keys for production
3. **Enable Cloud Armor** for DDoS protection
4. **Set up VPC** for private networking
5. **Enable Cloud Audit Logs** for compliance

---

*Last updated: 2025-11-26*
