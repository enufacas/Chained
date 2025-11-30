# 🔐 gcloud-mcp Copilot Environment Setup Guide

This guide explains how to configure the environment secrets and variables needed for GitHub Copilot to use the gcloud-mcp server for Google Cloud Platform operations.

## 📋 Prerequisites

Before configuring secrets, ensure you have:

1. **GCP Account** with a project ([Create Project](https://console.cloud.google.com/projectcreate))
2. **gcloud CLI** installed locally ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **GitHub repository** access with admin permissions

---

## 🔑 Required Secrets & Variables

### Repository Secrets

Add these secrets in **Settings** → **Secrets and variables** → **Actions** → **Repository secrets**:

| Secret Name | Required | Description |
|-------------|----------|-------------|
| `GCP_PROJECT_ID` | ✅ Yes | Your GCP project ID |
| `GCP_SA_KEY` | ✅ Yes | Service account key JSON |
| `GCP_REGION` | ⚪ Optional | GCP region (default: `us-central1`) |
| `GOOGLE_API_KEY` | ⚪ Optional | Gemini API key for AI features |

### Copilot Environment Variables

Add these in **Settings** → **Environments** → **github-copilot** (or create if doesn't exist):

| Variable Name | Required | Description |
|---------------|----------|-------------|
| `CLOUDSDK_CORE_PROJECT` | ⚪ Optional | Default GCP project for gcloud commands |
| `CLOUDSDK_COMPUTE_REGION` | ⚪ Optional | Default region for compute resources |

---

## 🚀 Step-by-Step Setup

### Step 1: Create a GCP Service Account

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create service account for Copilot
gcloud iam service-accounts create copilot-agent \
  --display-name="GitHub Copilot Agent" \
  --description="Service account for Copilot MCP operations" \
  --project=$PROJECT_ID

# Get the service account email
export SA_EMAIL="copilot-agent@${PROJECT_ID}.iam.gserviceaccount.com"
```

### Step 2: Grant Required Permissions

Grant only the permissions needed for your use case:

```bash
# Read-only access (safest for exploration)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/viewer"

# Cloud Run management
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Storage management
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

# Compute Engine (if needed)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/compute.viewer"

# Kubernetes Engine (if needed)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/container.clusterViewer"
```

### Step 3: Generate and Download Service Account Key

```bash
# Create and download the key
gcloud iam service-accounts keys create ~/copilot-gcp-key.json \
  --iam-account=$SA_EMAIL \
  --project=$PROJECT_ID

echo "✅ Service account key saved to ~/copilot-gcp-key.json"

# Display the key (copy this for GitHub secrets)
cat ~/copilot-gcp-key.json
```

### Step 4: Add GitHub Repository Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

**GCP_PROJECT_ID:**
```
your-project-id
```

**GCP_SA_KEY:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
```
(Paste the entire JSON from `~/copilot-gcp-key.json`)

**GCP_REGION (optional):**
```
us-central1
```

### Step 5: Configure Copilot Environment

1. Go to **Settings** → **Environments**
2. Click **New environment** and name it `github-copilot`
3. Add environment variables:

**CLOUDSDK_CORE_PROJECT:**
```
your-project-id
```

**CLOUDSDK_COMPUTE_REGION:**
```
us-central1
```

---

## 🔧 Workflow Configuration

### Basic Workflow with gcloud-mcp

Here's how to configure a workflow that uses gcloud-mcp:

```yaml
name: "Copilot with GCP Access"

on:
  issues:
    types: [opened, labeled]

jobs:
  copilot-gcp:
    runs-on: ubuntu-latest
    environment: github-copilot
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Setup gcloud CLI
        uses: google-github-actions/setup-gcloud@v2
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      
      - name: Configure MCP for Copilot
        run: |
          mkdir -p /tmp/copilot-config
          
          cat > /tmp/copilot-config/mcp.json << 'EOF'
          {
            "mcpServers": {
              "gcloud": {
                "command": "npx",
                "args": ["-y", "@google-cloud/gcloud-mcp"],
                "description": "Google Cloud Platform CLI"
              },
              "chained-repository": {
                "command": "chained-repository-mcp",
                "description": "Chained Repository Access"
              }
            }
          }
          EOF
          
          echo "MCP_SERVERS_CONFIG=/tmp/copilot-config/mcp.json" >> $GITHUB_ENV
      
      - name: Verify GCP Access
        run: |
          echo "🔍 Verifying GCP authentication..."
          gcloud auth list
          gcloud config list project
          gcloud run services list --limit=3 || echo "No Cloud Run services found"
          echo "✅ GCP access verified"
```

---

## 🔐 Security Best Practices

### Principle of Least Privilege

Only grant the permissions Copilot needs:

```bash
# For read-only operations (recommended starting point)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/viewer"

# Add write permissions only as needed
# Example: Cloud Run deployment
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.developer"
```

### Restrict gcloud-mcp Commands

The gcloud-mcp server has built-in restrictions that prevent:
- Commands that run arbitrary code
- Interactive session commands
- Potentially destructive operations without confirmation

See the [gcloud-mcp security documentation](https://github.com/googleapis/gcloud-mcp#-mcp-permissions) for the full list of restricted commands.

### Rotate Keys Regularly

```bash
# List existing keys
gcloud iam service-accounts keys list \
  --iam-account=$SA_EMAIL

# Create a new key
gcloud iam service-accounts keys create ~/new-copilot-key.json \
  --iam-account=$SA_EMAIL

# Delete old key (after updating GitHub secrets)
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=$SA_EMAIL
```

### Use Workload Identity (Production)

For production environments, consider using Workload Identity instead of service account keys:

```yaml
- name: Authenticate to Google Cloud (Workload Identity)
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123456/locations/global/workloadIdentityPools/github/providers/github'
    service_account: 'copilot-agent@your-project.iam.gserviceaccount.com'
```

---

## 🧪 Testing Your Configuration

### Verify Secrets Are Set

```bash
# In a GitHub Actions workflow
- name: Verify secrets
  run: |
    if [ -z "${{ secrets.GCP_PROJECT_ID }}" ]; then
      echo "❌ GCP_PROJECT_ID not set"
      exit 1
    fi
    
    if [ -z "${{ secrets.GCP_SA_KEY }}" ]; then
      echo "❌ GCP_SA_KEY not set"
      exit 1
    fi
    
    echo "✅ Required secrets are configured"
```

### Test gcloud-mcp Locally

```bash
# Authenticate locally
gcloud auth application-default login

# Test gcloud-mcp server
npx @google-cloud/gcloud-mcp

# In Claude Desktop or another MCP client, try:
# "List all Cloud Run services in my project"
```

---

## 📊 Common Use Cases

### 1. List Cloud Resources

```
"Show me all the Cloud Run services in my project"
"List all GCS buckets"
"What compute instances are running?"
```

### 2. Deploy Services

```
"Deploy my application to Cloud Run"
"Create a new Cloud Storage bucket named my-bucket in us-central1"
```

### 3. Monitor Resources

```
"Show me recent Cloud Run deployment logs"
"What's the CPU usage of my compute instances?"
```

### 4. Manage Infrastructure

```
"Scale my Cloud Run service to handle more traffic"
"Update the environment variables for my service"
```

---

## 🛠️ Troubleshooting

### "Permission denied" Errors

```bash
# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:copilot-agent@" \
  --format="table(bindings.role)"
```

### "gcloud not found" in Workflow

Ensure you have the gcloud setup step:
```yaml
- uses: google-github-actions/setup-gcloud@v2
  with:
    project_id: ${{ secrets.GCP_PROJECT_ID }}
```

### MCP Server Not Connecting

1. Verify Node.js version is 20+
2. Check that gcloud CLI is authenticated
3. Ensure `CLOUDSDK_CORE_PROJECT` is set

---

## 📚 Related Documentation

- [GCP Setup Guide](./GCP_SETUP_GUIDE.md) - Full GCP infrastructure setup
- [gcloud-mcp GitHub](https://github.com/googleapis/gcloud-mcp) - Official documentation
- [MCP Servers README](../../mcp-servers/README.md) - All available MCP servers
- [GitHub Copilot Integration](../../mcp-servers/chained-repository/GITHUB_COPILOT.md) - Copilot workflow examples

---

## 🔗 Quick Reference

### Required Secrets Checklist

- [ ] `GCP_PROJECT_ID` - Your GCP project identifier
- [ ] `GCP_SA_KEY` - Service account JSON key

### Optional Configuration

- [ ] `GCP_REGION` - Default region (us-central1)
- [ ] `GOOGLE_API_KEY` - For Gemini AI features
- [ ] Copilot environment with `CLOUDSDK_*` variables

### IAM Roles for Common Tasks

| Task | Minimum Role |
|------|-------------|
| View resources | `roles/viewer` |
| Cloud Run deployment | `roles/run.developer` |
| Storage management | `roles/storage.objectAdmin` |
| Compute instances | `roles/compute.instanceAdmin` |
| Full admin | `roles/owner` (not recommended) |

---

*Created for the Chained autonomous AI ecosystem - Enabling AI agents to interact with Google Cloud Platform* ☁️🤖
