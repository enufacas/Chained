# Terraform Infrastructure - Separated Deployment Pipelines

This directory contains the Terraform infrastructure configurations for the Chained autonomous AI ecosystem, **separated into two independent deployment pipelines**.

## Directory Structure

```
infrastructure/terraform/
├── base/                          # Base Infrastructure (deploy-gcp-infrastructure.yml)
│   ├── main.tf                    # Provider + base Cloud Run services
│   ├── adk-agents.tf              # ADK A2A agents
│   ├── blog.tf                    # Blog storage
│   ├── variables.tf               # Variables
│   ├── outputs.tf                 # Outputs
│   ├── terraform.tfvars.example   # Example config
│   └── README.md
│
├── ai-native/                     # AI-Native Control Plane (ai-native-deploy.yml)
│   ├── main.tf                    # Provider + API services
│   ├── ai-native-control-plane.tf # AI control plane resources
│   ├── variables.tf               # Variables
│   ├── outputs.tf                 # Outputs
│   ├── terraform.tfvars.example   # Example config
│   └── README.md
│
└── README.md                      # This file
```

## Why Separate?

The infrastructure is split into two independent Terraform configurations:

### Base Infrastructure (`base/`)
- **Purpose**: Core platform services
- **Includes**: Cloud Run services, ADK agents, Pub/Sub, Firestore, Storage
- **Cost**: $10-25/month (scales to zero)
- **Deployment**: Always deployed, foundation for everything
- **Workflow**: `.github/workflows/deploy-gcp-infrastructure.yml`

### AI-Native Control Plane (`ai-native/`)
- **Purpose**: Autonomous infrastructure management
- **Includes**: Cloud SQL, VPC, AI control plane services
- **Cost**: $15-50/month (Cloud SQL always running)
- **Deployment**: Optional, can be deployed independently
- **Workflow**: `.github/workflows/ai-native-deploy.yml`

## Benefits of Separation

1. **Independent Lifecycle**: Deploy/destroy AI control plane without affecting base infrastructure
2. **Cost Control**: Can disable expensive AI control plane when not needed
3. **Clear Ownership**: Separate workflows trigger only for relevant changes
4. **Reduced Complexity**: Each deployment is simpler and faster
5. **Better Testing**: Test base infrastructure without AI control plane dependencies

## Deployment Order

### Initial Setup

1. **Deploy base infrastructure first**:
   ```bash
   cd infrastructure/terraform/base
   terraform init
   terraform apply
   ```

2. **Deploy AI-Native Control Plane (optional)**:
   ```bash
   cd infrastructure/terraform/ai-native
   terraform init
   terraform apply
   ```

### Automated Deployments

Both workflows run independently:

- **Base infrastructure**: Triggers on changes to `infrastructure/terraform/base/**`
- **AI-Native**: Triggers on changes to `infrastructure/terraform/ai-native/**` or `services/**`

## State Management

Each directory maintains its own Terraform state:

- **base/**: `terraform.tfstate` (base infrastructure)
- **ai-native/**: `terraform.tfstate` (AI control plane)

**Important**: These are separate state files. Destroying one does not affect the other.

## Cost Comparison

| Component | Base | AI-Native | Total |
|-----------|------|-----------|-------|
| Cloud Run | $5-10/mo | $5-10/mo | $10-20/mo |
| Cloud SQL | - | $10-50/mo | $10-50/mo |
| Storage | $1-5/mo | - | $1-5/mo |
| Other | $1-5/mo | $1-5/mo | $2-10/mo |
| **Total** | **$10-25/mo** | **$15-65/mo** | **$25-90/mo** |

## Migration from Old Structure

If you were using the old monolithic structure:

1. **Backup your state**: `cp terraform.tfstate terraform.tfstate.backup`
2. **Deploy base first**: The base directory includes all the resources from the old structure except AI-Native
3. **Optionally deploy AI-Native**: If you were using it, deploy it separately

## Related Documentation

- [Base Infrastructure README](base/README.md)
- [AI-Native Control Plane README](ai-native/README.md)
- [GCP Setup Guide](../../docs/guides/GCP_SETUP_GUIDE.md)
- [Deployment Workflows](../../.github/workflows/)

## Troubleshooting

### "Resource already exists" errors

If you get conflicts during initial deployment, it means resources were created by the old monolithic configuration. Options:

1. **Import existing resources**: Use `terraform import` to bring them under management
2. **Destroy and recreate**: Delete resources manually and let Terraform create them fresh
3. **Use different project**: Deploy to a clean GCP project

### State file conflicts

Each directory should have its own `.terraform/` directory and state file. If you see conflicts:

```bash
# In each directory
rm -rf .terraform
terraform init
```

## Questions?

- See the README files in `base/` and `ai-native/` for directory-specific docs
- Check workflow files in `.github/workflows/` for CI/CD details
- Review the infrastructure docs in `docs/guides/`
