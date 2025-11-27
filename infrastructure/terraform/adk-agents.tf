# =============================================================================
# Chained ADK Agents - Cloud Run Terraform Configuration
# =============================================================================
# This configuration deploys the ADK-based A2A agents to Cloud Run:
# - academic-research: Discovers research topics
# - blog-writer: Writes blog posts
# - google-trends: Analyzes Google Trends
#
# Reference:
# - ADK Cloud Run Deployment: https://google.github.io/adk-docs/deploy/cloud-run/
# - A2A Protocol: https://a2a-protocol.org/
#
# NOTE: This file uses variables and providers defined in main.tf and variables.tf
# =============================================================================

# =============================================================================
# Additional Variables for ADK Agents
# =============================================================================

variable "gemini_api_key_secret" {
  description = "Secret Manager resource name for Gemini API key"
  type        = string
  default     = ""
}

variable "google_api_key_secret" {
  description = "Secret Manager resource name for Google API key"
  type        = string
  default     = ""
}

# =============================================================================
# Service Account for ADK Agents
# =============================================================================

resource "google_service_account" "adk_agents" {
  account_id   = "chained-adk-agents"
  display_name = "Chained ADK Agents Service Account"
  description  = "Service account for ADK A2A agents on Cloud Run"
}

# Grant access to Secret Manager
resource "google_project_iam_member" "adk_agents_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.adk_agents.email}"
}

# Grant access to Cloud Trace (for observability)
resource "google_project_iam_member" "adk_agents_trace" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.adk_agents.email}"
}

# =============================================================================
# Cloud Run: Academic Research Agent
# =============================================================================

resource "google_cloud_run_v2_service" "academic_research" {
  name     = "chained-academic-research"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/academic-research:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_NAME"
        value = "academic-research"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      dynamic "env" {
        for_each = var.gemini_api_key_secret != "" ? [1] : []
        content {
          name = "GEMINI_API_KEY"
          value_source {
            secret_key_ref {
              secret  = var.gemini_api_key_secret
              version = "latest"
            }
          }
        }
      }

      ports {
        container_port = 8080
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 5
        timeout_seconds       = 3
        period_seconds        = 5
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        period_seconds    = 30
        timeout_seconds   = 3
        failure_threshold = 3
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    service_account = google_service_account.adk_agents.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_v2_service_iam_member" "academic_research_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.academic_research.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run: Blog Writer Agent
# =============================================================================

resource "google_cloud_run_v2_service" "blog_writer" {
  name     = "chained-blog-writer"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/blog-writer:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_NAME"
        value = "blog-writer"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "WEBSITE_DEPLOY_URL"
        value = "https://enufacas.github.io/Chained"
      }

      dynamic "env" {
        for_each = var.gemini_api_key_secret != "" ? [1] : []
        content {
          name = "GEMINI_API_KEY"
          value_source {
            secret_key_ref {
              secret  = var.gemini_api_key_secret
              version = "latest"
            }
          }
        }
      }

      ports {
        container_port = 8080
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 5
        timeout_seconds       = 3
        period_seconds        = 5
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        period_seconds    = 30
        timeout_seconds   = 3
        failure_threshold = 3
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    service_account = google_service_account.adk_agents.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_v2_service_iam_member" "blog_writer_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.blog_writer.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run: Google Trends Agent
# =============================================================================

resource "google_cloud_run_v2_service" "google_trends" {
  name     = "chained-google-trends"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/google-trends:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_NAME"
        value = "google-trends"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      dynamic "env" {
        for_each = var.google_api_key_secret != "" ? [1] : []
        content {
          name = "GOOGLE_API_KEY"
          value_source {
            secret_key_ref {
              secret  = var.google_api_key_secret
              version = "latest"
            }
          }
        }
      }

      ports {
        container_port = 8080
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 5
        timeout_seconds       = 3
        period_seconds        = 5
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        period_seconds    = 30
        timeout_seconds   = 3
        failure_threshold = 3
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    service_account = google_service_account.adk_agents.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_v2_service_iam_member" "google_trends_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.google_trends.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Outputs
# =============================================================================

output "academic_research_url" {
  description = "URL of the Academic Research Agent"
  value       = google_cloud_run_v2_service.academic_research.uri
}

output "blog_writer_url" {
  description = "URL of the Blog Writer Agent"
  value       = google_cloud_run_v2_service.blog_writer.uri
}

output "google_trends_url" {
  description = "URL of the Google Trends Agent"
  value       = google_cloud_run_v2_service.google_trends.uri
}

output "adk_dev_ui_info" {
  description = "ADK Dev UI access information"
  value       = <<-EOT
    ADK Dev UI is accessible at each agent's root endpoint:
    - Academic Research: ${google_cloud_run_v2_service.academic_research.uri}
    - Blog Writer: ${google_cloud_run_v2_service.blog_writer.uri}
    - Google Trends: ${google_cloud_run_v2_service.google_trends.uri}

    Health checks available at /health endpoint for each service.
    A2A Agent Cards available at /.well-known/agent.json
  EOT
}
