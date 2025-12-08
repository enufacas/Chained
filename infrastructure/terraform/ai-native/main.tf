# =============================================================================
# AI-Native Control Plane - Terraform Root Configuration
# =============================================================================
# This is the entry point for deploying ONLY the AI-Native Control Plane.
#
# This configuration is separate from the base infrastructure and includes:
# - Provider configuration
# - Backend configuration (optional)
# - Include the AI-Native Control Plane resources
#
# To deploy: cd infrastructure/terraform/ai-native && terraform init && terraform apply
# =============================================================================

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Backend configuration for state storage
  # Uncomment and configure for production use
  # backend "gcs" {
  #   bucket = "chained-terraform-state"
  #   prefix = "terraform/ai-native/state"
  # }
}

# =============================================================================
# Provider Configuration
# =============================================================================

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# =============================================================================
# Data Sources
# =============================================================================

data "google_project" "current" {
  project_id = var.project_id
}

# =============================================================================
# Enable Required Base APIs
# =============================================================================

resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",  # Required for Vertex AI (Gemini models)
    "monitoring.googleapis.com",
    "logging.googleapis.com",
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
