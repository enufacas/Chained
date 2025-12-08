# Deployment Pipeline Separation - Visual Guide

## Before (Monolithic)

```
┌─────────────────────────────────────────────────────────────┐
│  deploy-gcp-infrastructure.yml                              │
│  Working Directory: infrastructure/terraform/               │
│                                                              │
│  Deploys EVERYTHING:                                         │
│  • Base infrastructure (Cloud Run, Pub/Sub, Firestore)      │
│  • ADK agents (8 services)                                   │
│  • AI-Native Control Plane (Cloud SQL, VPC)                 │
│                                                              │
│  Problem: Cannot deploy base without deploying AI control   │
│           plane (which costs $15-50/month even when idle)   │
└─────────────────────────────────────────────────────────────┘
```

## After (Separated)

```
┌─────────────────────────────────────────────────────────────┐
│  deploy-gcp-infrastructure.yml                              │
│  Working Directory: infrastructure/terraform/base/          │
│                                                              │
│  Deploys BASE ONLY:                                          │
│  ✅ Cloud Run services (website, gateway, worker)           │
│  ✅ ADK agents (8 services)                                  │
│  ✅ Pub/Sub, Firestore, Storage                             │
│  ✅ Artifact Registry                                        │
│  ✅ Monitoring & Alerting                                    │
│                                                              │
│  Cost: $10-25/month (scales to zero)                        │
│  Triggers on: infrastructure/terraform/base/**              │
└─────────────────────────────────────────────────────────────┘

                              +

┌─────────────────────────────────────────────────────────────┐
│  ai-native-deploy.yml                                       │
│  Working Directory: infrastructure/terraform/ai-native/     │
│                                                              │
│  Deploys AI CONTROL PLANE ONLY:                             │
│  ✅ Cloud SQL (PostgreSQL + pgvector)                       │
│  ✅ VPC Network + Subnet                                     │
│  ✅ VPC Access Connector                                     │
│  ✅ AI Control Plane Service                                 │
│  ✅ Infra Runner Service                                     │
│  ✅ Service Accounts                                         │
│  ✅ Secret Manager                                           │
│                                                              │
│  Cost: $15-50/month (Cloud SQL always running)             │
│  Triggers on: infrastructure/terraform/ai-native/**         │
└─────────────────────────────────────────────────────────────┘
```

## File Organization

```
infrastructure/terraform/
│
├── 📁 base/                           ← Base Infrastructure
│   ├── main.tf                        (Provider + Cloud Run services)
│   ├── adk-agents.tf                  (8 ADK A2A agents)
│   ├── blog.tf                        (Blog storage bucket)
│   ├── variables.tf                   (Base-specific variables)
│   ├── outputs.tf                     (Base-specific outputs)
│   ├── terraform.tfvars.example       (Configuration template)
│   ├── terraform.tfstate              (Separate state file)
│   └── README.md                      (Base infrastructure guide)
│
└── 📁 ai-native/                      ← AI-Native Control Plane
    ├── main.tf                        (Provider + API services)
    ├── ai-native-control-plane.tf     (Cloud SQL, VPC, AI services)
    ├── variables.tf                   (AI-native variables)
    ├── outputs.tf                     (AI-native outputs)
    ├── terraform.tfvars.example       (Configuration template)
    ├── terraform.tfstate              (Separate state file)
    └── README.md                      (AI control plane guide)
```

## Deployment Flows

### Base Infrastructure Deployment

```
┌─────────────────┐
│ Developer       │
│ pushes change   │
│ to base/**      │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│ deploy-gcp-infrastructure.yml           │
│ - Validate configuration                │
│ - Setup Terraform                       │
│ - Import existing resources             │
│ - Plan changes                          │
│ - Apply changes                         │
└────────┬────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│ GCP - Base Infrastructure               │
│ ✅ Website                               │
│ ✅ Agent Gateway                         │
│ ✅ Agent Worker                          │
│ ✅ 8 ADK Agents                          │
│ ✅ Pub/Sub                               │
│ ✅ Firestore                             │
│ ✅ Storage                               │
└─────────────────────────────────────────┘
```

### AI-Native Control Plane Deployment

```
┌─────────────────┐
│ Developer       │
│ pushes change   │
│ to ai-native/** │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│ ai-native-deploy.yml                    │
│ - Build container images                │
│ - Setup Terraform                       │
│ - Create terraform.tfvars               │
│ - Plan changes                          │
│ - Apply changes                         │
└────────┬────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│ GCP - AI-Native Control Plane           │
│ ✅ Cloud SQL (PostgreSQL)               │
│ ✅ VPC Network                           │
│ ✅ VPC Connector                         │
│ ✅ AI Control Plane                      │
│ ✅ Infra Runner                          │
└─────────────────────────────────────────┘
```

## State Management

### Independent State Files

```
infrastructure/terraform/
│
├── base/
│   ├── terraform.tfstate          ← Manages base infrastructure
│   └── .terraform/                ← Base Terraform cache
│
└── ai-native/
    ├── terraform.tfstate          ← Manages AI control plane
    └── .terraform/                ← AI-native Terraform cache

⚠️  These are SEPARATE state files
    Changes to one do NOT affect the other
```

## Cost Breakdown

```
┌──────────────────┬──────────────┬──────────────┬─────────────┐
│ Component        │ Base         │ AI-Native    │ Scale to 0? │
├──────────────────┼──────────────┼──────────────┼─────────────┤
│ Cloud Run        │ $5-10/mo     │ $5-10/mo     │ ✅ Yes      │
│ Cloud SQL        │ -            │ $10-50/mo    │ ❌ No       │
│ Storage          │ $1-5/mo      │ -            │ N/A         │
│ Pub/Sub          │ Free tier    │ -            │ N/A         │
│ Firestore        │ Free tier    │ -            │ N/A         │
│ VPC Connector    │ -            │ $0.50-1/mo   │ N/A         │
│ Other            │ $1-5/mo      │ $1-5/mo      │ N/A         │
├──────────────────┼──────────────┼──────────────┼─────────────┤
│ Total            │ $10-25/mo    │ $15-65/mo    │ Partial     │
└──────────────────┴──────────────┴──────────────┴─────────────┘

💡 Can disable AI-Native to save $15-65/month when not needed
```

## Use Cases

### Scenario 1: Development (Base Only)

```
Developer working on ADK agents
↓
Only need base infrastructure
↓
Deploy only base/ → Costs $10-25/month
↓
AI control plane disabled → Save $15-65/month
```

### Scenario 2: Full Production

```
Production deployment with all features
↓
Deploy base/ → $10-25/month
↓
Deploy ai-native/ → $15-65/month
↓
Total: $25-90/month
```

### Scenario 3: Cost Optimization

```
Testing completed, AI control plane not needed
↓
Keep base/ running → $10-25/month
↓
Destroy ai-native/ → Save $15-65/month
↓
Total: $10-25/month (61-73% cost reduction)
```

## Migration Path

For existing deployments using the old monolithic structure:

```
Old Structure                    New Structure
─────────────────               ─────────────────
terraform/                      terraform/
├── main.tf             →       ├── base/
├── adk-agents.tf       →       │   ├── main.tf
├── blog.tf             →       │   ├── adk-agents.tf
├── ai-native-...tf     →       │   └── blog.tf
├── variables.tf                │
└── outputs.tf                  └── ai-native/
                                    ├── main.tf
                                    └── ai-native-control-plane.tf

Migration Steps:
1. Backup state: terraform.tfstate
2. Deploy base/ (imports existing resources)
3. Deploy ai-native/ if needed
4. Verify both work independently
5. Remove old structure
```

## Verification Checklist

To verify the separation is working:

✅ Workflow Triggers
- [ ] Push to base/** triggers deploy-gcp-infrastructure.yml only
- [ ] Push to ai-native/** triggers ai-native-deploy.yml only
- [ ] Each workflow works in its own directory

✅ State Independence
- [ ] base/ has its own terraform.tfstate
- [ ] ai-native/ has its own terraform.tfstate
- [ ] Can destroy one without affecting the other

✅ Resource Isolation
- [ ] deploy-gcp-infrastructure.yml doesn't create Cloud SQL
- [ ] deploy-gcp-infrastructure.yml doesn't create VPC
- [ ] ai-native-deploy.yml doesn't touch base services

✅ Documentation
- [ ] READMEs exist in both directories
- [ ] terraform.tfvars.example in both directories
- [ ] Clear cost breakdown documented
