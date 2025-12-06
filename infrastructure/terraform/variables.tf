# =============================================================================
# Chained GCP Infrastructure - Variables
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

variable "firestore_location" {
  description = "The location for Firestore database (must be multi-region or single region)"
  type        = string
  default     = "nam5"  # US multi-region (free tier eligible)
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# =============================================================================
# Container Images
# =============================================================================

variable "website_image" {
  description = "Container image for the website service (leave empty for placeholder)"
  type        = string
  default     = ""
}

variable "agent_gateway_image" {
  description = "Container image for the agent gateway service (leave empty for placeholder)"
  type        = string
  default     = ""
}

variable "agent_worker_image" {
  description = "Container image for the agent worker service (leave empty for placeholder)"
  type        = string
  default     = ""
}

# =============================================================================
# Alerting Configuration
# =============================================================================

variable "alert_email" {
  description = "Email address for infrastructure alerts (leave empty to skip alerting)"
  type        = string
  default     = ""
}

# =============================================================================
# Budget Configuration
# =============================================================================

variable "monthly_budget" {
  description = "Monthly budget in USD for cost alerting"
  type        = number
  default     = 50  # Conservative default, leaving room for Gemini API
}

# =============================================================================
# GitHub Configuration
# =============================================================================

variable "git_repo" {
  description = "GitHub repository for error-observer repository_dispatch (format: owner/repository)"
  type        = string
  default     = ""
}

# =============================================================================
# AI-Native Control Plane Configuration
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

variable "ai_native_llm_provider" {
  description = "LLM provider for AI Control Plane (openai or gemini)"
  type        = string
  default     = "gemini"
}
