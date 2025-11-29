# =============================================================================
# Chained ADK Agents - Cloud Run Terraform Configuration
# =============================================================================
# This configuration deploys the ADK-based A2A agents to Cloud Run:
# - academic-research: Discovers research topics
# - blog-writer: Writes blog posts
# - google-trends: Analyzes Google Trends
# - ag-ui-frontend: CopilotKit-powered A2A Pipeline Visualization UI
#
# Reference:
# - ADK Cloud Run Deployment: https://google.github.io/adk-docs/deploy/cloud-run/
# - A2A Protocol: https://a2a-protocol.org/
# - AG-UI Protocol: https://docs.ag-ui.com/
#
# NOTE: This file uses variables and providers defined in main.tf and variables.tf
# =============================================================================

# =============================================================================
# Additional Variables for ADK Agents
# =============================================================================

variable "image_tag" {
  description = "Container image tag (use commit SHA to force updates)"
  type        = string
  default     = "latest"
}

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

variable "openai_api_key_secret" {
  description = "Secret Manager resource name for OpenAI API key (optional - only needed for CopilotKit chat feature)"
  type        = string
  default     = ""
}

# =============================================================================
# Service Account for ADK Agents
# =============================================================================

# Import existing service account if it already exists
# Use `terraform import google_service_account.adk_agents projects/${var.project_id}/serviceAccounts/chained-adk-agents@${var.project_id}.iam.gserviceaccount.com`
resource "google_service_account" "adk_agents" {
  account_id   = "chained-adk-agents"
  display_name = "Chained ADK Agents Service Account"
  description  = "Service account for ADK A2A agents on Cloud Run"

  lifecycle {
    # Allow Terraform to adopt existing service accounts without forcing updates
    # Note: Intentional changes to display_name/description should be made directly in GCP console
    # or by temporarily removing these from ignore_changes
    ignore_changes = [
      display_name,
      description,
    ]
  }
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
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/academic-research:${var.image_tag}"

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
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/blog-writer:${var.image_tag}"

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
        value = "https://storage.googleapis.com/${google_storage_bucket.blog.name}"
      }

      # Blog bucket for publishing posts
      env {
        name  = "BLOG_BUCKET_NAME"
        value = google_storage_bucket.blog.name
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

  depends_on = [
    google_project_service.required_apis,
    google_storage_bucket.blog,
  ]
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
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/google-trends:${var.image_tag}"

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
# Cloud Run: ADK API Server (Bridge for google/adk-web)
# =============================================================================

resource "google_cloud_run_v2_service" "adk_api_server" {
  name     = "chained-adk-api-server"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/adk-api-server:${var.image_tag}"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      # Configure agent URLs dynamically from other Cloud Run services
      env {
        name  = "AGENT_ACADEMIC_RESEARCH_URL"
        value = google_cloud_run_v2_service.academic_research.uri
      }

      env {
        name  = "AGENT_ACADEMIC_RESEARCH_DESCRIPTION"
        value = "Discovers and analyzes academic research topics for blog content"
      }

      env {
        name  = "AGENT_BLOG_WRITER_URL"
        value = google_cloud_run_v2_service.blog_writer.uri
      }

      env {
        name  = "AGENT_BLOG_WRITER_DESCRIPTION"
        value = "Writes engaging blog posts from research and trend data"
      }

      env {
        name  = "AGENT_GOOGLE_TRENDS_URL"
        value = google_cloud_run_v2_service.google_trends.uri
      }

      env {
        name  = "AGENT_GOOGLE_TRENDS_DESCRIPTION"
        value = "Analyzes Google Trends data to identify trending topics for SEO"
      }

      # CORS configuration for adk-web
      # In production, restrict to specific origins. For development, allow localhost.
      # Configure CORS_ORIGINS environment variable to comma-separated allowed origins.
      env {
        name  = "CORS_ORIGINS"
        value = var.environment == "prod" ? "https://enufacas.github.io" : "http://localhost:4200,http://localhost:4201,http://127.0.0.1:4200"
      }

      # Use Firestore for session persistence in production
      env {
        name  = "USE_FIRESTORE"
        value = var.environment == "prod" ? "true" : "false"
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
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

  depends_on = [
    google_project_service.required_apis,
    google_cloud_run_v2_service.academic_research,
    google_cloud_run_v2_service.blog_writer,
    google_cloud_run_v2_service.google_trends,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "adk_api_server_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.adk_api_server.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run: AG-UI Frontend (CopilotKit Visualization)
# =============================================================================

resource "google_cloud_run_v2_service" "ag_ui_frontend" {
  name     = "chained-ag-ui-frontend"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/ag-ui-frontend:${var.image_tag}"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      # Enable Vertex AI mode - uses Application Default Credentials (ADC) from service account
      # This is the preferred mode on Cloud Run as it doesn't require API keys
      env {
        name  = "USE_VERTEX_AI"
        value = "true"
      }

      # Configure ADK API Server URL for agent communication
      env {
        name  = "NEXT_PUBLIC_ADK_API_URL"
        value = google_cloud_run_v2_service.adk_api_server.uri
      }

      # Note: GOOGLE_API_KEY is NOT used when USE_VERTEX_AI=true
      # The GoogleGenerativeAIAdapter will use ADC from the service account instead
      # Keeping these for backward compatibility if USE_VERTEX_AI is disabled
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

      # Gemini API Key from Secret Manager (fallback if GOOGLE_API_KEY not set)
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

      # OpenAI API Key from Secret Manager (fallback for CopilotKit chat feature)
      dynamic "env" {
        for_each = var.openai_api_key_secret != "" ? [1] : []
        content {
          name = "OPENAI_API_KEY"
          value_source {
            secret_key_ref {
              secret  = var.openai_api_key_secret
              version = "latest"
            }
          }
        }
      }

      ports {
        container_port = 3000
      }

      startup_probe {
        http_get {
          path = "/"
          port = 3000
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/"
          port = 3000
        }
        period_seconds    = 30
        timeout_seconds   = 5
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

  depends_on = [
    google_project_service.required_apis,
    google_cloud_run_v2_service.adk_api_server,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "ag_ui_frontend_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.ag_ui_frontend.name
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

output "adk_api_server_url" {
  description = "URL of the ADK API Server (for google/adk-web)"
  value       = google_cloud_run_v2_service.adk_api_server.uri
}

output "ag_ui_frontend_url" {
  description = "URL of the AG-UI Frontend (CopilotKit Visualization)"
  value       = google_cloud_run_v2_service.ag_ui_frontend.uri
}

output "adk_dev_ui_info" {
  description = "ADK Dev UI access information"
  value       = <<-EOT
    AG-UI Frontend (CopilotKit Visualization):
    - URL: ${google_cloud_run_v2_service.ag_ui_frontend.uri}
    - CopilotKit API: ${google_cloud_run_v2_service.ag_ui_frontend.uri}/api/copilotkit

    ADK API Server (for google/adk-web):
    - API Server: ${google_cloud_run_v2_service.adk_api_server.uri}

    To use with google/adk-web (alternative):
    1. Clone: git clone https://github.com/google/adk-web
    2. Configure API URL: ${google_cloud_run_v2_service.adk_api_server.uri}
    3. Run: npm start

    Available A2A Agents:
    - Academic Research: ${google_cloud_run_v2_service.academic_research.uri}
    - Blog Writer: ${google_cloud_run_v2_service.blog_writer.uri}
    - Google Trends: ${google_cloud_run_v2_service.google_trends.uri}

    Health checks available at /health endpoint for each service.
    A2A Agent Cards available at /.well-known/agent.json
  EOT
}
