#!/bin/bash
# =============================================================================
# AI-Native Control Plane - Bootstrap Deployment Script
# =============================================================================
# This script automates the initial deployment of the AI-Native Control Plane
# system to Google Cloud Platform.
#
# Prerequisites:
# - gcloud CLI installed and authenticated
# - Terraform installed (>= 1.0.0)
# - Docker installed (for building images)
# - jq installed (for JSON processing)
#
# Usage:
#   ./bootstrap-deploy.sh <project_id> <region> [environment]
#
# Example:
#   ./bootstrap-deploy.sh my-gcp-project us-central1 dev
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# =============================================================================
# Validate Arguments
# =============================================================================

if [ $# -lt 2 ]; then
    log_error "Usage: $0 <project_id> <region> [environment]"
    log_info "Example: $0 my-gcp-project us-central1 dev"
    exit 1
fi

PROJECT_ID="$1"
REGION="$2"
ENVIRONMENT="${3:-dev}"

log_info "Starting AI-Native Control Plane bootstrap deployment"
log_info "Project ID: $PROJECT_ID"
log_info "Region: $REGION"
log_info "Environment: $ENVIRONMENT"

# =============================================================================
# Check Prerequisites
# =============================================================================

log_info "Checking prerequisites..."
check_command gcloud
check_command terraform
check_command docker
check_command jq

# Set GCP project
gcloud config set project "$PROJECT_ID"
log_success "GCP project set to $PROJECT_ID"

# =============================================================================
# Enable Required APIs
# =============================================================================

log_info "Enabling required GCP APIs..."
APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "sqladmin.googleapis.com"
    "servicenetworking.googleapis.com"
    "vpcaccess.googleapis.com"
    "compute.googleapis.com"
    "secretmanager.googleapis.com"
)

for api in "${APIS[@]}"; do
    log_info "Enabling $api..."
    gcloud services enable "$api" --project="$PROJECT_ID" || true
done

log_success "All required APIs enabled"

# =============================================================================
# Build and Push Container Images
# =============================================================================

log_info "Building and pushing container images..."

# Get or create artifact registry
REGISTRY_NAME="chained"
REGISTRY_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_NAME"

# Create Artifact Registry if it doesn't exist
log_info "Creating Artifact Registry repository..."
gcloud artifacts repositories create "$REGISTRY_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Container images for AI-Native Control Plane" \
    --project="$PROJECT_ID" 2>/dev/null || log_warn "Artifact Registry already exists"

# Configure docker for GCR
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

# Build images
cd "$(dirname "$0")/../.."  # Go to repo root

# Build infra-runner
log_info "Building infra-runner image..."
docker build -t "$REGISTRY_URL/infra-runner:latest" \
    -f services/infra-runner/Dockerfile \
    services/infra-runner/

docker push "$REGISTRY_URL/infra-runner:latest"
log_success "infra-runner image pushed"

# Build ai-control-plane
log_info "Building ai-control-plane image..."
docker build -t "$REGISTRY_URL/ai-control-plane:latest" \
    -f services/ai-control-plane/Dockerfile \
    services/ai-control-plane/

docker push "$REGISTRY_URL/ai-control-plane:latest"
log_success "ai-control-plane image pushed"

# =============================================================================
# Run Terraform
# =============================================================================

log_info "Deploying infrastructure with Terraform..."
cd infrastructure/terraform

# Create terraform.tfvars if it doesn't exist
if [ ! -f terraform.tfvars ]; then
    log_info "Creating terraform.tfvars..."
    cat > terraform.tfvars <<EOF
project_id  = "$PROJECT_ID"
region      = "$REGION"
environment = "$ENVIRONMENT"

# AI-Native Control Plane images
ai_native_control_plane_image = "$REGISTRY_URL/ai-control-plane:latest"
ai_native_infra_runner_image  = "$REGISTRY_URL/infra-runner:latest"

# Database configuration
ai_native_db_tier      = "db-f1-micro"
ai_native_db_disk_size = 10

# LLM provider (gemini or openai)
ai_native_llm_provider = "gemini"

# Alert email (optional)
# alert_email = "your-email@example.com"
EOF
    log_success "terraform.tfvars created"
else
    log_info "terraform.tfvars already exists, skipping creation"
fi

# Initialize Terraform
log_info "Initializing Terraform..."
terraform init

# Plan Terraform
log_info "Planning Terraform deployment..."
terraform plan -out=tfplan

# Apply Terraform
log_info "Applying Terraform deployment..."
terraform apply tfplan

log_success "Infrastructure deployed successfully!"

# =============================================================================
# Set API Keys (Manual Step)
# =============================================================================

log_warn ""
log_warn "==================================================================="
log_warn "MANUAL STEP REQUIRED: Set API keys in Secret Manager"
log_warn "==================================================================="
log_warn ""
log_warn "Run these commands to set your API keys:"
log_warn ""
log_warn "  # OpenAI API Key:"
log_warn "  echo -n 'your-openai-key' | gcloud secrets versions add ai-native-openai-api-key --data-file=- --project=$PROJECT_ID"
log_warn ""
log_warn "  # Gemini API Key:"
log_warn "  echo -n 'your-gemini-key' | gcloud secrets versions add ai-native-gemini-api-key --data-file=- --project=$PROJECT_ID"
log_warn ""
log_warn "Get Gemini API key from: https://aistudio.google.com/app/apikey"
log_warn "Get OpenAI API key from: https://platform.openai.com/api-keys"
log_warn ""

# =============================================================================
# Run Database Migrations
# =============================================================================

log_info "Database migrations need to be run manually..."
log_warn ""
log_warn "==================================================================="
log_warn "MANUAL STEP REQUIRED: Run database migrations"
log_warn "==================================================================="
log_warn ""
log_warn "1. Get the Cloud SQL instance connection name:"
log_warn "   gcloud sql instances describe \$(terraform output -raw ai_native_database_instance) --project=$PROJECT_ID | grep connectionName"
log_warn ""
log_warn "2. Connect to the database:"
log_warn "   gcloud sql connect \$(terraform output -raw ai_native_database_instance) --user=ai_native_admin --database=ai_native_control_plane --project=$PROJECT_ID"
log_warn ""
log_warn "3. Run migrations:"
log_warn "   \i services/state-db/migrations/001_initial_schema.sql"
log_warn "   \i services/state-db/migrations/002_add_vector_support.sql"
log_warn ""

# =============================================================================
# Display Deployment Summary
# =============================================================================

log_success ""
log_success "==================================================================="
log_success "AI-NATIVE CONTROL PLANE BOOTSTRAP DEPLOYMENT COMPLETE!"
log_success "==================================================================="
log_success ""

# Get outputs
terraform output ai_native_deployment_summary

log_success ""
log_success "Quick Test Command:"
log_success ""
AI_CONTROL_PLANE_URL=$(terraform output -raw ai_native_control_plane_url 2>/dev/null || echo "")
if [ -n "$AI_CONTROL_PLANE_URL" ]; then
    log_success "curl -X POST $AI_CONTROL_PLANE_URL/execute \\"
    log_success "  -H 'Content-Type: application/json' \\"
    log_success "  -d '{\"user_request\": \"Create a simple blog website\", \"user_id\": \"test-user\"}'"
    log_success ""
fi

log_success "Deployment complete! Don't forget to set API keys and run database migrations."
