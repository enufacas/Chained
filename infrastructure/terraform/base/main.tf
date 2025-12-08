# =============================================================================
# Chained GCP Infrastructure - Base Configuration
# =============================================================================
# This Terraform configuration deploys the base Cloud Run architecture
# for the Chained autonomous AI ecosystem (excluding AI-Native Control Plane).
#
# Architecture:
# - Cloud Run services for website and agent gateway
# - Cloud Pub/Sub for agent messaging
# - Firestore for agent state/memory
# - Cloud Monitoring for observability
#
# Estimated Monthly Cost: $10-25 (well under $300 budget)
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
# Chained GCP Infrastructure - Main Terraform Configuration
# =============================================================================
# This Terraform configuration deploys the recommended Cloud Run architecture
# for the Chained autonomous AI ecosystem.
#
# Architecture:
# - Cloud Run services for website and agent gateway
# - Cloud Pub/Sub for agent messaging
# - Firestore for agent state/memory
# - Cloud Monitoring for observability
#
# Estimated Monthly Cost: $10-25 (well under $300 budget)
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
  #   prefix = "terraform/state"
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
# Enable Required APIs
# =============================================================================

resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "pubsub.googleapis.com",
    "firestore.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",  # Required for Vertex AI (Gemini models)
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# =============================================================================
# Artifact Registry for Container Images
# =============================================================================

resource "google_artifact_registry_repository" "chained" {
  location      = var.region
  repository_id = "chained"
  description   = "Container images for Chained autonomous AI ecosystem"
  format        = "DOCKER"

  depends_on = [google_project_service.required_apis]
}

# =============================================================================
# Cloud Run Service: Website
# =============================================================================

resource "google_cloud_run_v2_service" "website" {
  name     = "chained-website"
  location = var.region

  template {
    containers {
      image = var.website_image != "" ? var.website_image : "gcr.io/cloudrun/hello"

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
        cpu_idle          = true  # Scale to zero when idle
        startup_cpu_boost = true
      }

      env {
        name  = "AGENT_GATEWAY_URL"
        value = "https://chained-agent-gateway-${data.google_project.current.number}.${var.region}.run.app"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      ports {
        container_port = 8080
      }
    }

    scaling {
      min_instance_count = 0  # Scale to zero for cost savings
      max_instance_count = 3
    }

    timeout = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_project_service.required_apis]
}

# Allow unauthenticated access to website
resource "google_cloud_run_v2_service_iam_member" "website_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.website.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run Service: Agent Gateway
# =============================================================================

resource "google_cloud_run_v2_service" "agent_gateway" {
  name     = "chained-agent-gateway"
  location = var.region

  template {
    containers {
      image = var.agent_gateway_image != "" ? var.agent_gateway_image : "gcr.io/cloudrun/hello"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "PUBSUB_TOPIC"
        value = google_pubsub_topic.agent_tasks.name
      }

      env {
        name  = "FIRESTORE_DATABASE"
        value = "(default)"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      ports {
        container_port = 8080
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    service_account = google_service_account.agent_gateway.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.required_apis,
    google_pubsub_topic.agent_tasks,
  ]
}

# Allow unauthenticated access to agent gateway API
resource "google_cloud_run_v2_service_iam_member" "agent_gateway_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.agent_gateway.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run Service: Agent Worker
# =============================================================================

resource "google_cloud_run_v2_service" "agent_worker" {
  name     = "chained-agent-worker"
  location = var.region

  template {
    containers {
      image = var.agent_worker_image != "" ? var.agent_worker_image : "gcr.io/cloudrun/hello"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "PUBSUB_SUBSCRIPTION"
        value = google_pubsub_subscription.agent_tasks.name
      }

      env {
        name  = "FIRESTORE_DATABASE"
        value = "(default)"
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      ports {
        container_port = 8080
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    service_account = google_service_account.agent_worker.email
    timeout         = "300s"
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.required_apis,
    google_pubsub_subscription.agent_tasks,
  ]
}

# =============================================================================
# Service Accounts
# =============================================================================

# Import existing service accounts if they already exist
# Use `terraform import google_service_account.agent_gateway projects/${var.project_id}/serviceAccounts/chained-agent-gateway@${var.project_id}.iam.gserviceaccount.com`
resource "google_service_account" "agent_gateway" {
  account_id   = "chained-agent-gateway"
  display_name = "Chained Agent Gateway Service Account"
  description  = "Service account for the agent gateway Cloud Run service"

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

# Use `terraform import google_service_account.agent_worker projects/${var.project_id}/serviceAccounts/chained-agent-worker@${var.project_id}.iam.gserviceaccount.com`
resource "google_service_account" "agent_worker" {
  account_id   = "chained-agent-worker"
  display_name = "Chained Agent Worker Service Account"
  description  = "Service account for agent worker Cloud Run services"

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

# IAM bindings for agent gateway
resource "google_project_iam_member" "agent_gateway_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.agent_gateway.email}"
}

resource "google_project_iam_member" "agent_gateway_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.agent_gateway.email}"
}

# IAM bindings for agent worker
resource "google_project_iam_member" "agent_worker_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.agent_worker.email}"
}

resource "google_project_iam_member" "agent_worker_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.agent_worker.email}"
}

# =============================================================================
# Cloud Pub/Sub for Agent Messaging
# =============================================================================

resource "google_pubsub_topic" "agent_tasks" {
  name = "chained-agent-tasks"

  message_retention_duration = "86400s"  # 24 hours

  depends_on = [google_project_service.required_apis]
}

# Import existing subscriptions if they already exist
# Use `terraform import google_pubsub_subscription.agent_tasks projects/${var.project_id}/subscriptions/chained-agent-tasks-sub`
resource "google_pubsub_subscription" "agent_tasks" {
  name  = "chained-agent-tasks-sub"
  topic = google_pubsub_topic.agent_tasks.name

  ack_deadline_seconds       = 60
  message_retention_duration = "86400s"

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  expiration_policy {
    ttl = ""  # Never expire
  }

  lifecycle {
    # Allow Terraform to manage existing subscriptions
    ignore_changes = [
      ack_deadline_seconds,
    ]
  }

  depends_on = [google_pubsub_topic.agent_tasks]
}

# Dead letter topic for failed messages
resource "google_pubsub_topic" "agent_tasks_dlq" {
  name = "chained-agent-tasks-dlq"

  depends_on = [google_project_service.required_apis]
}

# =============================================================================
# Firestore Database for Agent Memory
# =============================================================================

# Import existing Firestore database if it already exists
# Use `terraform import google_firestore_database.default projects/${var.project_id}/databases/(default)`
resource "google_firestore_database" "default" {
  project         = var.project_id
  name            = "(default)"
  location_id     = var.firestore_location
  type            = "FIRESTORE_NATIVE"
  deletion_policy = "ABANDON"  # Don't delete the database on terraform destroy

  lifecycle {
    # Prevent accidental deletion of the database
    prevent_destroy = true
    # Ignore changes that can't be updated on existing databases
    ignore_changes = [
      location_id,
      type,
    ]
  }

  depends_on = [google_project_service.required_apis]
}

# =============================================================================
# Cloud Monitoring - Alerting
# =============================================================================

resource "google_monitoring_notification_channel" "email" {
  count        = var.alert_email != "" ? 1 : 0
  display_name = "Chained Infrastructure Alerts"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_alert_policy" "high_error_rate" {
  count        = var.alert_email != "" ? 1 : 0
  display_name = "Chained - High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run 5xx Error Rate > 10%"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND metric.type = \"run.googleapis.com/request_count\" AND metric.labels.response_code_class = \"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.1

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].name]

  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "high_latency" {
  count        = var.alert_email != "" ? 1 : 0
  display_name = "Chained - High Latency"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run P99 Latency > 5s"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND metric.type = \"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5000  # 5 seconds in ms

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_99"
        cross_series_reducer = "REDUCE_MAX"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].name]

  alert_strategy {
    auto_close = "1800s"
  }
}

# =============================================================================
# Data Sources
# =============================================================================

data "google_project" "current" {
  project_id = var.project_id
}
