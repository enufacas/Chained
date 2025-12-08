# =============================================================================
# AI-Native Control Plane - Variables
# =============================================================================

# =============================================================================
# Core Configuration
# =============================================================================

variable "project_id" {
  description = "The GCP project ID where resources will be created"
  type        = string
}

variable "region" {
  description = "The GCP region for Cloud Run and other regional resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# =============================================================================
# Container Images
# =============================================================================

variable "ai_native_control_plane_image" {
  description = "Container image for AI Control Plane service"
  type        = string
  default     = ""
}

variable "ai_native_infra_runner_image" {
  description = "Container image for Infra Runner service"
  type        = string
  default     = ""
}

# =============================================================================
# Database Configuration
# =============================================================================

variable "ai_native_db_tier" {
  description = "Cloud SQL tier for AI-Native Control Plane database"
  type        = string
  default     = "db-f1-micro"  # Smallest tier for dev, use db-custom-2-7680 for prod
}

variable "ai_native_db_disk_size" {
  description = "Disk size in GB for AI-Native Control Plane database"
  type        = number
  default     = 10
}

# =============================================================================
# LLM Configuration
# =============================================================================

variable "ai_native_llm_provider" {
  description = "LLM provider for AI Control Plane (openai or gemini)"
  type        = string
  default     = "gemini"
}

# =============================================================================
# Alerting Configuration
# =============================================================================

variable "alert_email" {
  description = "Email address for infrastructure alerts (leave empty to skip alerting)"
  type        = string
  default     = ""
}
