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
# CPU Quota and Concurrency Constraints:
# - Each service uses 0.5 CPU (total: 4 CPUs for 8 services)
# - All services have cpu_idle=true (scale to zero when not in use)
# - GCP default quota: varies by region, typically 8-10 CPUs
# - To increase quota: https://cloud.google.com/run/quotas
#
# IMPORTANT: Cloud Run Constraint
# - When CPU < 1, max_instance_request_concurrency MUST be set to 1
# - Reference: https://cloud.google.com/run/docs/configuring/cpu
# - Error if violated: "Total cpu < 1 is not supported with concurrency > 1"
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

# Direct API key values (passed from GitHub secrets)
# These take precedence over Secret Manager references if both are set
variable "google_api_key" {
  description = "Google API key value (direct, from GitHub secrets)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Gemini API key value (direct, from GitHub secrets)"
  type        = string
  default     = ""
  sensitive   = true
}

# Secret Manager references (alternative to direct values)
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

# Grant access to Vertex AI (for Gemini model access via ADC)
# Required for the AG-UI Frontend CopilotKit chat feature when USE_VERTEX_AI=true
resource "google_project_iam_member" "adk_agents_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
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
          cpu    = "0.5"
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

      # Enable Vertex AI mode - uses Application Default Credentials (ADC) from service account
      # This is the preferred mode on Cloud Run as it uses OAuth2 instead of API keys
      env {
        name  = "USE_VERTEX_AI"
        value = "true"
      }

      # Set Google Cloud Project ID - required for Vertex AI with ADC
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      # Error Observer URL for agent error reporting
      env {
        name  = "ERROR_OBSERVER_URL"
        value = google_cloud_run_v2_service.error_observer.uri
      }

      # Direct API key value (from GitHub secrets) - fallback if Vertex AI is not used
      dynamic "env" {
        for_each = toset(var.google_api_key != "" ? ["enabled"] : [])
        content {
          name  = "GOOGLE_API_KEY"
          value = var.google_api_key
        }
      }

      # Direct Gemini API key value (from GitHub secrets)
      dynamic "env" {
        for_each = toset(var.gemini_api_key != "" && var.google_api_key == "" ? ["enabled"] : [])
        content {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
        }
      }

      # Secret Manager reference (fallback if no direct value)
      dynamic "env" {
        for_each = toset(var.gemini_api_key_secret != "" && var.google_api_key == "" && var.gemini_api_key == "" ? ["enabled"] : [])
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
      min_instance_count              = 0
      max_instance_count              = 3
    }

    max_instance_request_concurrency = 1  # Required when CPU < 1

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
          cpu    = "0.5"
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

      # Enable Vertex AI mode - uses Application Default Credentials (ADC) from service account
      # This is the preferred mode on Cloud Run as it uses OAuth2 instead of API keys
      env {
        name  = "USE_VERTEX_AI"
        value = "true"
      }

      # Set Google Cloud Project ID - required for Vertex AI with ADC
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      # Error Observer URL for agent error reporting
      env {
        name  = "ERROR_OBSERVER_URL"
        value = google_cloud_run_v2_service.error_observer.uri
      }

      # Direct API key value (from GitHub secrets) - fallback if Vertex AI is not used
      dynamic "env" {
        for_each = toset(var.google_api_key != "" ? ["enabled"] : [])
        content {
          name  = "GOOGLE_API_KEY"
          value = var.google_api_key
        }
      }

      # Direct Gemini API key value (from GitHub secrets)
      dynamic "env" {
        for_each = toset(var.gemini_api_key != "" && var.google_api_key == "" ? ["enabled"] : [])
        content {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
        }
      }

      # Secret Manager reference (fallback if no direct value)
      dynamic "env" {
        for_each = toset(var.gemini_api_key_secret != "" && var.google_api_key == "" && var.gemini_api_key == "" ? ["enabled"] : [])
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
      min_instance_count              = 0
      max_instance_count              = 3
    }

    max_instance_request_concurrency = 1  # Required when CPU < 1

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
          cpu    = "0.5"
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

      # Enable Vertex AI mode - uses Application Default Credentials (ADC) from service account
      # This is the preferred mode on Cloud Run as it uses OAuth2 instead of API keys
      env {
        name  = "USE_VERTEX_AI"
        value = "true"
      }

      # Set Google Cloud Project ID - required for Vertex AI with ADC
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      # Error Observer URL for agent error reporting
      env {
        name  = "ERROR_OBSERVER_URL"
        value = google_cloud_run_v2_service.error_observer.uri
      }

      # Direct API key value (from GitHub secrets) - fallback if Vertex AI is not used
      dynamic "env" {
        for_each = toset(var.google_api_key != "" ? ["enabled"] : [])
        content {
          name  = "GOOGLE_API_KEY"
          value = var.google_api_key
        }
      }

      # Direct Gemini API key value (from GitHub secrets)
      dynamic "env" {
        for_each = toset(var.gemini_api_key != "" && var.google_api_key == "" ? ["enabled"] : [])
        content {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
        }
      }

      # Secret Manager reference (fallback if no direct value)
      dynamic "env" {
        for_each = toset(var.google_api_key_secret != "" && var.google_api_key == "" && var.gemini_api_key == "" ? ["enabled"] : [])
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
      min_instance_count              = 0
      max_instance_count              = 3
    }

    max_instance_request_concurrency = 1  # Required when CPU < 1

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
# Cloud Run: Code Reviewer Agent
# =============================================================================

resource "google_cloud_run_v2_service" "code_reviewer" {
  name     = "chained-code-reviewer"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/code-reviewer:${var.image_tag}"

      resources {
        limits = {
          cpu    = "0.5"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_NAME"
        value = "code-reviewer"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "USE_VERTEX_AI"
        value = "true"
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      dynamic "env" {
        for_each = toset(var.google_api_key != "" ? ["enabled"] : [])
        content {
          name  = "GOOGLE_API_KEY"
          value = var.google_api_key
        }
      }

      dynamic "env" {
        for_each = toset(var.gemini_api_key != "" && var.google_api_key == "" ? ["enabled"] : [])
        content {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
        }
      }

      dynamic "env" {
        for_each = toset(var.gemini_api_key_secret != "" && var.google_api_key == "" && var.gemini_api_key == "" ? ["enabled"] : [])
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
      min_instance_count              = 0
      max_instance_count              = 3
    }

    max_instance_request_concurrency = 1  # Required when CPU < 1

    service_account = google_service_account.adk_agents.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_v2_service_iam_member" "code_reviewer_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.code_reviewer.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run: Data Analyst Agent
# =============================================================================

resource "google_cloud_run_v2_service" "data_analyst" {
  name     = "chained-data-analyst"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/data-analyst:${var.image_tag}"

      resources {
        limits = {
          cpu    = "0.5"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_NAME"
        value = "data-analyst"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "USE_VERTEX_AI"
        value = "true"
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      dynamic "env" {
        for_each = toset(var.google_api_key != "" ? ["enabled"] : [])
        content {
          name  = "GOOGLE_API_KEY"
          value = var.google_api_key
        }
      }

      dynamic "env" {
        for_each = toset(var.gemini_api_key != "" && var.google_api_key == "" ? ["enabled"] : [])
        content {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
        }
      }

      dynamic "env" {
        for_each = toset(var.gemini_api_key_secret != "" && var.google_api_key == "" && var.gemini_api_key == "" ? ["enabled"] : [])
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
      min_instance_count              = 0
      max_instance_count              = 3
    }

    max_instance_request_concurrency = 1  # Required when CPU < 1

    service_account = google_service_account.adk_agents.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_v2_service_iam_member" "data_analyst_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.data_analyst.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run: Image Generator Agent
# =============================================================================

resource "google_cloud_run_v2_service" "image_generator" {
  name     = "chained-image-generator"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/image-generator:${var.image_tag}"

      resources {
        limits = {
          cpu    = "0.5"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_NAME"
        value = "image-generator"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "USE_VERTEX_AI"
        value = "true"
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      dynamic "env" {
        for_each = toset(var.google_api_key != "" ? ["enabled"] : [])
        content {
          name  = "GOOGLE_API_KEY"
          value = var.google_api_key
        }
      }

      dynamic "env" {
        for_each = toset(var.gemini_api_key != "" && var.google_api_key == "" ? ["enabled"] : [])
        content {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
        }
      }

      dynamic "env" {
        for_each = toset(var.gemini_api_key_secret != "" && var.google_api_key == "" && var.gemini_api_key == "" ? ["enabled"] : [])
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
      min_instance_count              = 0
      max_instance_count              = 3
    }

    max_instance_request_concurrency = 1  # Required when CPU < 1

    service_account = google_service_account.adk_agents.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_v2_service_iam_member" "image_generator_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.image_generator.name
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
          cpu    = "0.5"
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

      # New agents: Code Reviewer, Data Analyst, Image Generator
      env {
        name  = "AGENT_CODE_REVIEWER_URL"
        value = google_cloud_run_v2_service.code_reviewer.uri
      }

      env {
        name  = "AGENT_CODE_REVIEWER_DESCRIPTION"
        value = "Reviews code snippets, suggests improvements, and identifies best practices"
      }

      env {
        name  = "AGENT_DATA_ANALYST_URL"
        value = google_cloud_run_v2_service.data_analyst.uri
      }

      env {
        name  = "AGENT_DATA_ANALYST_DESCRIPTION"
        value = "Analyzes data and generates insights, statistics, and visualizations"
      }

      env {
        name  = "AGENT_IMAGE_GENERATOR_URL"
        value = google_cloud_run_v2_service.image_generator.uri
      }

      env {
        name  = "AGENT_IMAGE_GENERATOR_DESCRIPTION"
        value = "Generates visual content descriptions, diagrams, and image specifications"
      }

      # CORS configuration for adk-web and AG-UI Frontend
      # Production: Uses predictable pattern with project ID for AG-UI frontend
      # Development: Uses actual Cloud Run service URL (hash 'sguacxy5gq' is auto-generated on service creation)
      # The dev URL is stable once the service is created; it only changes if the service is deleted and recreated
      env {
        name  = "CORS_ORIGINS"
        value = var.environment == "prod" ? "https://enufacas.github.io,https://chained-ag-ui-frontend-${var.project_id}.${var.region}.run.app" : "http://localhost:4200,http://localhost:4201,http://127.0.0.1:4200,https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app"
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
      min_instance_count              = 0
      max_instance_count              = 3
    }

    max_instance_request_concurrency = 1  # Required when CPU < 1

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
    google_cloud_run_v2_service.code_reviewer,
    google_cloud_run_v2_service.data_analyst,
    google_cloud_run_v2_service.image_generator,
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
          cpu    = "0.5"
          memory = "1Gi"  # Increased from 512Mi to 1Gi to prevent OOM errors
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

      # Set Google Cloud Project ID - required by @langchain/google-gauth library when using
      # Vertex AI with Application Default Credentials (ADC). Without this environment variable,
      # you get the error: "Unable to detect a Project Id in the current environment"
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      # Configure ADK API Server URL for agent communication
      env {
        name  = "NEXT_PUBLIC_ADK_API_URL"
        value = google_cloud_run_v2_service.adk_api_server.uri
      }

      # Configure A2A Agent URLs for real pipeline execution
      # These are required for the AG-UI Frontend to call actual agents
      env {
        name  = "AGENT_ACADEMIC_RESEARCH_URL"
        value = google_cloud_run_v2_service.academic_research.uri
      }

      env {
        name  = "AGENT_GOOGLE_TRENDS_URL"
        value = google_cloud_run_v2_service.google_trends.uri
      }

      env {
        name  = "AGENT_BLOG_WRITER_URL"
        value = google_cloud_run_v2_service.blog_writer.uri
      }

      # New agents: Code Reviewer, Data Analyst, Image Generator
      env {
        name  = "AGENT_CODE_REVIEWER_URL"
        value = google_cloud_run_v2_service.code_reviewer.uri
      }

      env {
        name  = "AGENT_DATA_ANALYST_URL"
        value = google_cloud_run_v2_service.data_analyst.uri
      }

      env {
        name  = "AGENT_IMAGE_GENERATOR_URL"
        value = google_cloud_run_v2_service.image_generator.uri
      }

      # Error Observer URL for UI error reporting
      env {
        name  = "ERROR_OBSERVER_URL"
        value = google_cloud_run_v2_service.error_observer.uri
      }

      # GCP Project ID for blog URL construction in pipeline route
      # Blog URLs: https://storage.googleapis.com/${GCP_PROJECT_ID}-chained-blog/posts/${slug}.html
      # NOTE: This is different from GOOGLE_CLOUD_PROJECT which is used by the Google Auth library.
      # Both are needed:
      #   - GOOGLE_CLOUD_PROJECT: Used by @langchain/google-gauth for Vertex AI authentication
      #   - GCP_PROJECT_ID: Used by pipeline route for blog bucket URL construction
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      # Note: GOOGLE_API_KEY is NOT used when USE_VERTEX_AI=true
      # The GoogleGenerativeAIAdapter will use ADC from the service account instead
      # Keeping these for backward compatibility if USE_VERTEX_AI is disabled

      # Direct API key value (from GitHub secrets) - takes precedence
      dynamic "env" {
        for_each = toset(var.google_api_key != "" ? ["enabled"] : [])
        content {
          name  = "GOOGLE_API_KEY"
          value = var.google_api_key
        }
      }

      # Direct Gemini API key value (from GitHub secrets)
      dynamic "env" {
        for_each = toset(var.gemini_api_key != "" && var.google_api_key == "" ? ["enabled"] : [])
        content {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
        }
      }

      # Secret Manager reference for Google API Key (fallback if no direct value)
      dynamic "env" {
        for_each = toset(var.google_api_key_secret != "" && var.google_api_key == "" && var.gemini_api_key == "" ? ["enabled"] : [])
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

      # Secret Manager reference for Gemini API Key (fallback if no direct value)
      dynamic "env" {
        for_each = toset(var.gemini_api_key_secret != "" && var.google_api_key == "" && var.gemini_api_key == "" && var.google_api_key_secret == "" ? ["enabled"] : [])
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
        for_each = toset(var.openai_api_key_secret != "" ? ["enabled"] : [])
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
      min_instance_count              = 0
      max_instance_count              = 3
    }

    max_instance_request_concurrency = 1  # Required when CPU < 1

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
    google_cloud_run_v2_service.academic_research,
    google_cloud_run_v2_service.blog_writer,
    google_cloud_run_v2_service.google_trends,
    google_cloud_run_v2_service.code_reviewer,
    google_cloud_run_v2_service.data_analyst,
    google_cloud_run_v2_service.image_generator,
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
# Cloud Run: Error Observer Agent
# =============================================================================

resource "google_cloud_run_v2_service" "error_observer" {
  name     = "chained-error-observer"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/error-observer:${var.image_tag}"

      resources {
        limits = {
          cpu    = "0.5"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_NAME"
        value = "error-observer"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      # GitHub PAT for repository_dispatch API calls
      # This is required for the error observer to forward errors to GitHub
      env {
        name  = "GITHUB_PAT"
        value_source {
          secret_key_ref {
            secret  = "github-pat"
            version = "latest"
          }
        }
      }

      # GitHub repository for repository_dispatch
      env {
        name  = "GITHUB_REPO"
        value = var.github_repo != "" ? var.github_repo : "enufacas/Chained"
      }

      # Service URL for agent card
      env {
        name  = "SERVICE_URL"
        value = "https://chained-error-observer-${data.google_project.current.number}.${var.region}.run.app"
      }

      ports {
        container_port = 8090
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8090
        }
        initial_delay_seconds = 5
        timeout_seconds       = 3
        period_seconds        = 5
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8090
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

    max_instance_request_concurrency = 1 # Required when CPU < 1

    service_account = google_service_account.adk_agents.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_run_v2_service_iam_member" "error_observer_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.error_observer.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run: Log Consumer Agent
# =============================================================================

resource "google_cloud_run_v2_service" "log_consumer" {
  name     = "chained-log-consumer"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/chained/log-consumer:${var.image_tag}"

      resources {
        limits = {
          cpu    = "0.5"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_NAME"
        value = "log-consumer"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      # Error Observer URL for sending error events
      env {
        name  = "ERROR_OBSERVER_URL"
        value = google_cloud_run_v2_service.error_observer.uri
      }

      ports {
        container_port = 8091
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8091
        }
        initial_delay_seconds = 5
        timeout_seconds       = 3
        period_seconds        = 5
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8091
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

    max_instance_request_concurrency = 1 # Required when CPU < 1

    service_account = google_service_account.adk_agents.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.required_apis,
    google_cloud_run_v2_service.error_observer,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "log_consumer_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.log_consumer.name
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

output "code_reviewer_url" {
  description = "URL of the Code Reviewer Agent"
  value       = google_cloud_run_v2_service.code_reviewer.uri
}

output "data_analyst_url" {
  description = "URL of the Data Analyst Agent"
  value       = google_cloud_run_v2_service.data_analyst.uri
}

output "image_generator_url" {
  description = "URL of the Image Generator Agent"
  value       = google_cloud_run_v2_service.image_generator.uri
}

output "adk_api_server_url" {
  description = "URL of the ADK API Server (for google/adk-web)"
  value       = google_cloud_run_v2_service.adk_api_server.uri
}

output "ag_ui_frontend_url" {
  description = "URL of the AG-UI Frontend (CopilotKit Visualization)"
  value       = google_cloud_run_v2_service.ag_ui_frontend.uri
}

output "error_observer_url" {
  description = "URL of the Error Observer Agent"
  value       = google_cloud_run_v2_service.error_observer.uri
}

output "log_consumer_url" {
  description = "URL of the Log Consumer Agent"
  value       = google_cloud_run_v2_service.log_consumer.uri
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
    - Code Reviewer: ${google_cloud_run_v2_service.code_reviewer.uri}
    - Data Analyst: ${google_cloud_run_v2_service.data_analyst.uri}
    - Image Generator: ${google_cloud_run_v2_service.image_generator.uri}
    - Error Observer: ${google_cloud_run_v2_service.error_observer.uri}
    - Log Consumer: ${google_cloud_run_v2_service.log_consumer.uri}

    Health checks available at /health endpoint for each service.
    A2A Agent Cards available at /.well-known/agent.json
  EOT
}
