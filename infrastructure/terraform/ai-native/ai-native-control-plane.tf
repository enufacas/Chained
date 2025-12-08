# =============================================================================
# AI-Native Control Plane - Terraform Configuration
# =============================================================================
# This Terraform configuration deploys the complete AI-Native Control Plane
# system to Google Cloud Platform, including:
# - Cloud SQL (PostgreSQL with pgvector extension)
# - Cloud Run services (ai-control-plane, infra-runner, state-db API)
# - Secret Manager for API keys (OpenAI, Gemini)
# - Service accounts with least privilege IAM
# - VPC networking and private services
# - Cloud Monitoring and logging
#
# Architecture: Autonomous AI-driven infrastructure operations
# =============================================================================

# =============================================================================
# Enable Required APIs for AI-Native Control Plane
# =============================================================================

resource "google_project_service" "ai_native_apis" {
  for_each = toset([
    "sqladmin.googleapis.com",       # Cloud SQL
    "servicenetworking.googleapis.com", # VPC Peering for Cloud SQL
    "vpcaccess.googleapis.com",      # VPC Access Connector for Cloud Run
    "compute.googleapis.com",         # Compute for VPC
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# =============================================================================
# VPC Network for Private Services
# =============================================================================

resource "google_compute_network" "ai_native_vpc" {
  name                    = "ai-native-control-plane-vpc"
  auto_create_subnetworks = false
  
  depends_on = [google_project_service.ai_native_apis]
}

resource "google_compute_subnetwork" "ai_native_subnet" {
  name          = "ai-native-subnet"
  ip_cidr_range = "10.8.0.0/28"
  region        = var.region
  network       = google_compute_network.ai_native_vpc.id

  private_ip_google_access = true
}

# Private IP allocation for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "ai-native-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.ai_native_vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.ai_native_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# VPC Access Connector for Cloud Run to Cloud SQL
resource "google_vpc_access_connector" "ai_native_connector" {
  name          = "ai-native-vpc-connector"
  region        = var.region
  network       = google_compute_network.ai_native_vpc.name
  ip_cidr_range = "10.8.0.0/28"
  
  depends_on = [
    google_project_service.ai_native_apis,
    google_compute_subnetwork.ai_native_subnet
  ]
}

# =============================================================================
# Cloud SQL Instance (PostgreSQL with pgvector)
# =============================================================================

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database_instance" "ai_native_db" {
  name             = "ai-native-control-plane-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_15"
  region           = var.region
  
  deletion_protection = var.environment == "production"

  settings {
    tier              = var.ai_native_db_tier
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = var.ai_native_db_disk_size
    disk_autoresize   = true

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = var.environment == "production"
      transaction_log_retention_days = 7

      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.ai_native_vpc.id
      require_ssl     = true
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }

    database_flags {
      name  = "shared_preload_libraries"
      value = "pgvector"
    }

    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
    }
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# Database
resource "google_sql_database" "ai_native_database" {
  name     = "ai_native_control_plane"
  instance = google_sql_database_instance.ai_native_db.name
}

# Database user
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "google_sql_user" "ai_native_user" {
  name     = "ai_native_admin"
  instance = google_sql_database_instance.ai_native_db.name
  password = random_password.db_password.result
}

# Store database credentials in Secret Manager
resource "google_secret_manager_secret" "db_connection_string" {
  secret_id = "ai-native-db-connection-string"

  replication {
    auto {}
  }

  depends_on = [google_project_service.ai_native_apis]
}

resource "google_secret_manager_secret_version" "db_connection_string" {
  secret = google_secret_manager_secret.db_connection_string.id
  secret_data = "postgresql://${google_sql_user.ai_native_user.name}:${random_password.db_password.result}@${google_sql_database_instance.ai_native_db.private_ip_address}/${google_sql_database.ai_native_database.name}"
}

# =============================================================================
# Secret Manager for API Keys
# =============================================================================

# OpenAI API Key
resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "ai-native-openai-api-key"

  replication {
    auto {}
  }

  depends_on = [google_project_service.ai_native_apis]
}

# Gemini API Key
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "ai-native-gemini-api-key"

  replication {
    auto {}
  }

  depends_on = [google_project_service.ai_native_apis]
}

# Note: Actual secret values must be added manually via:
# echo -n "your-openai-key" | gcloud secrets versions add ai-native-openai-api-key --data-file=-
# echo -n "your-gemini-key" | gcloud secrets versions add ai-native-gemini-api-key --data-file=-

# =============================================================================
# Service Accounts
# =============================================================================

# AI Control Plane Service Account
resource "google_service_account" "ai_control_plane" {
  account_id   = "ai-control-plane-sa"
  display_name = "AI Control Plane Service Account"
  description  = "Service account for AI Control Plane Cloud Run service"
}

# Infra Runner Service Account
resource "google_service_account" "infra_runner" {
  account_id   = "infra-runner-sa"
  display_name = "Infra Runner Service Account"
  description  = "Service account for Infra Runner Cloud Run service"
}

# State DB API Service Account
resource "google_service_account" "state_db_api" {
  account_id   = "state-db-api-sa"
  display_name = "State DB API Service Account"
  description  = "Service account for State DB API Cloud Run service"
}

# =============================================================================
# IAM Permissions
# =============================================================================

# AI Control Plane permissions
resource "google_project_iam_member" "ai_control_plane_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.ai_control_plane.email}"
}

resource "google_secret_manager_secret_iam_member" "ai_control_plane_openai" {
  secret_id = google_secret_manager_secret.openai_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ai_control_plane.email}"
}

resource "google_secret_manager_secret_iam_member" "ai_control_plane_gemini" {
  secret_id = google_secret_manager_secret.gemini_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ai_control_plane.email}"
}

resource "google_secret_manager_secret_iam_member" "ai_control_plane_db" {
  secret_id = google_secret_manager_secret.db_connection_string.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ai_control_plane.email}"
}

# Infra Runner permissions
resource "google_project_iam_member" "infra_runner_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.infra_runner.email}"
}

resource "google_project_iam_member" "infra_runner_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.infra_runner.email}"
}

resource "google_project_iam_member" "infra_runner_compute_viewer" {
  project = var.project_id
  role    = "roles/compute.viewer"
  member  = "serviceAccount:${google_service_account.infra_runner.email}"
}

resource "google_secret_manager_secret_iam_member" "infra_runner_db" {
  secret_id = google_secret_manager_secret.db_connection_string.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.infra_runner.email}"
}

# State DB API permissions
resource "google_project_iam_member" "state_db_api_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.state_db_api.email}"
}

resource "google_secret_manager_secret_iam_member" "state_db_api_db" {
  secret_id = google_secret_manager_secret.db_connection_string.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.state_db_api.email}"
}

# =============================================================================
# Cloud Run Services
# =============================================================================

# Infra Runner Service
resource "google_cloud_run_v2_service" "infra_runner" {
  name     = "ai-native-infra-runner"
  location = var.region

  template {
    containers {
      image = var.ai_native_infra_runner_image

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
        startup_cpu_boost = true
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "LOG_LEVEL"
        value = var.environment == "production" ? "INFO" : "DEBUG"
      }

      ports {
        container_port = 8080
      }
    }

    scaling {
      min_instance_count = var.environment == "production" ? 1 : 0
      max_instance_count = 10
    }

    max_instance_request_concurrency = 80
    timeout                          = "300s"
    service_account                  = google_service_account.infra_runner.email

    vpc_access {
      connector = google_vpc_access_connector.ai_native_connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.required_apis,
    google_vpc_access_connector.ai_native_connector
  ]
}

# AI Control Plane Service
resource "google_cloud_run_v2_service" "ai_control_plane" {
  name     = "ai-native-control-plane"
  location = var.region

  template {
    containers {
      image = var.ai_native_control_plane_image

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
        startup_cpu_boost = true
      }

      env {
        name  = "INFRA_RUNNER_URL"
        value = google_cloud_run_v2_service.infra_runner.uri
      }

      env {
        name = "STATE_DB_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_connection_string.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.openai_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "LLM_PROVIDER"
        value = var.ai_native_llm_provider
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "LOG_LEVEL"
        value = var.environment == "production" ? "INFO" : "DEBUG"
      }

      ports {
        container_port = 8081
      }
    }

    scaling {
      min_instance_count = var.environment == "production" ? 1 : 0
      max_instance_count = 10
    }

    max_instance_request_concurrency = 80
    timeout                          = "600s"
    service_account                  = google_service_account.ai_control_plane.email

    vpc_access {
      connector = google_vpc_access_connector.ai_native_connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.required_apis,
    google_cloud_run_v2_service.infra_runner,
    google_vpc_access_connector.ai_native_connector
  ]
}

# Allow public access to AI Control Plane (API endpoint)
resource "google_cloud_run_v2_service_iam_member" "ai_control_plane_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.ai_control_plane.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Allow AI Control Plane to invoke Infra Runner
resource "google_cloud_run_v2_service_iam_member" "infra_runner_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.infra_runner.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.ai_control_plane.email}"
}

# =============================================================================
# Cloud Monitoring - AI-Native Control Plane
# =============================================================================

resource "google_monitoring_alert_policy" "ai_native_high_error_rate" {
  count        = var.alert_email != "" ? 1 : 0
  display_name = "AI-Native Control Plane - High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run 5xx Error Rate > 5%"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name =~ \"ai-native-.*\" AND metric.type = \"run.googleapis.com/request_count\" AND metric.labels.response_code_class = \"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

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

resource "google_monitoring_alert_policy" "ai_native_db_connections" {
  count        = var.alert_email != "" ? 1 : 0
  display_name = "AI-Native Control Plane - High DB Connections"
  combiner     = "OR"

  conditions {
    display_name = "Cloud SQL Connections > 80%"

    condition_threshold {
      filter          = "resource.type = \"cloudsql_database\" AND resource.labels.database_id = \"${var.project_id}:${google_sql_database_instance.ai_native_db.name}\" AND metric.type = \"cloudsql.googleapis.com/database/postgresql/num_backends\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 80

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MAX"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email[0].name]

  alert_strategy {
    auto_close = "1800s"
  }
}
