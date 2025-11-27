# =============================================================================
# Identity-Aware Proxy (IAP) for ADK API Server
# =============================================================================
# This configuration enables browser-based authentication for the ADK API Server
# using Google Cloud Identity-Aware Proxy.
#
# Prerequisites:
# 1. A custom domain (e.g., adk-api.yourdomain.com)
# 2. OAuth consent screen configured in GCP Console
# 3. OAuth client ID and secret
#
# Reference:
# - IAP for Cloud Run: https://cloud.google.com/iap/docs/enabling-cloud-run
# =============================================================================

# =============================================================================
# Variables for IAP Configuration
# =============================================================================

variable "enable_iap" {
  description = "Enable Identity-Aware Proxy for browser-based authentication"
  type        = bool
  default     = false
}

variable "iap_oauth_client_id" {
  description = "OAuth2 client ID for IAP"
  type        = string
  default     = ""
  sensitive   = true
}

variable "iap_oauth_client_secret" {
  description = "OAuth2 client secret for IAP"
  type        = string
  default     = ""
  sensitive   = true
}

variable "iap_domain" {
  description = "Custom domain for the ADK API Server with IAP (e.g., adk-api.yourdomain.com)"
  type        = string
  default     = ""
}

variable "iap_allowed_members" {
  description = "List of members allowed to access the IAP-protected service (e.g., ['user:email@domain.com', 'group:devs@domain.com'])"
  type        = list(string)
  default     = []
}

# =============================================================================
# Enable Required APIs for IAP
# =============================================================================

resource "google_project_service" "iap_apis" {
  for_each = var.enable_iap ? toset([
    "iap.googleapis.com",
    "compute.googleapis.com",
  ]) : toset([])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# =============================================================================
# Serverless NEG for Cloud Run
# =============================================================================

resource "google_compute_region_network_endpoint_group" "adk_api_server_neg" {
  count = var.enable_iap ? 1 : 0

  name                  = "chained-adk-api-server-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id

  cloud_run {
    service = google_cloud_run_v2_service.adk_api_server.name
  }

  depends_on = [google_project_service.iap_apis]
}

# =============================================================================
# Backend Service with IAP
# =============================================================================

resource "google_compute_backend_service" "adk_api_server" {
  count = var.enable_iap ? 1 : 0

  name        = "chained-adk-api-server-backend"
  project     = var.project_id
  protocol    = "HTTPS"
  timeout_sec = 300

  backend {
    group = google_compute_region_network_endpoint_group.adk_api_server_neg[0].id
  }

  iap {
    oauth2_client_id     = var.iap_oauth_client_id
    oauth2_client_secret = var.iap_oauth_client_secret
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }

  depends_on = [google_project_service.iap_apis]
}

# =============================================================================
# URL Map (Load Balancer Routing)
# =============================================================================

resource "google_compute_url_map" "adk_api_server" {
  count = var.enable_iap ? 1 : 0

  name            = "chained-adk-api-server-url-map"
  project         = var.project_id
  default_service = google_compute_backend_service.adk_api_server[0].id
}

# =============================================================================
# SSL Certificate (Managed)
# =============================================================================

resource "google_compute_managed_ssl_certificate" "adk_api_server" {
  count = var.enable_iap && var.iap_domain != "" ? 1 : 0

  name    = "chained-adk-api-server-cert"
  project = var.project_id

  managed {
    domains = [var.iap_domain]
  }
}

# =============================================================================
# HTTPS Proxy
# =============================================================================

resource "google_compute_target_https_proxy" "adk_api_server" {
  count = var.enable_iap && var.iap_domain != "" ? 1 : 0

  name             = "chained-adk-api-server-https-proxy"
  project          = var.project_id
  url_map          = google_compute_url_map.adk_api_server[0].id
  ssl_certificates = [google_compute_managed_ssl_certificate.adk_api_server[0].id]
}

# =============================================================================
# Global IP Address
# =============================================================================

resource "google_compute_global_address" "adk_api_server" {
  count = var.enable_iap ? 1 : 0

  name    = "chained-adk-api-server-ip"
  project = var.project_id
}

# =============================================================================
# Global Forwarding Rule (Frontend)
# =============================================================================

resource "google_compute_global_forwarding_rule" "adk_api_server" {
  count = var.enable_iap && var.iap_domain != "" ? 1 : 0

  name       = "chained-adk-api-server-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_https_proxy.adk_api_server[0].id
  port_range = "443"
  ip_address = google_compute_global_address.adk_api_server[0].address
}

# =============================================================================
# IAP Access Policy
# =============================================================================

resource "google_iap_web_backend_service_iam_binding" "adk_api_server" {
  count = var.enable_iap && length(var.iap_allowed_members) > 0 ? 1 : 0

  project             = var.project_id
  web_backend_service = google_compute_backend_service.adk_api_server[0].name
  role                = "roles/iap.httpsResourceAccessor"
  members             = var.iap_allowed_members
}

# =============================================================================
# Remove public access when IAP is enabled
# =============================================================================
# Note: When IAP is enabled, you should remove the allUsers invoker binding
# from the ADK API Server Cloud Run service. This is handled by making the
# public IAM binding conditional.

# Update the public access in adk-agents.tf to be conditional:
# member = var.enable_iap ? "serviceAccount:${google_service_account.adk_agents.email}" : "allUsers"

# =============================================================================
# Outputs
# =============================================================================

output "iap_load_balancer_ip" {
  description = "Global IP address for the IAP-protected load balancer"
  value       = var.enable_iap ? google_compute_global_address.adk_api_server[0].address : null
}

output "iap_url" {
  description = "URL for the IAP-protected ADK API Server"
  value       = var.enable_iap && var.iap_domain != "" ? "https://${var.iap_domain}" : null
}

output "iap_setup_instructions" {
  description = "Instructions to complete IAP setup"
  value       = var.enable_iap ? <<-EOT
    IAP Setup Instructions:
    
    1. DNS Configuration:
       Point your domain (${var.iap_domain}) to IP: ${google_compute_global_address.adk_api_server[0].address}
       
       DNS Record: A ${var.iap_domain} -> ${google_compute_global_address.adk_api_server[0].address}
    
    2. Wait for SSL Certificate:
       The managed SSL certificate may take 15-30 minutes to provision.
       Check status: gcloud compute ssl-certificates describe chained-adk-api-server-cert
    
    3. Configure OAuth Consent Screen (if not already done):
       - Go to: https://console.cloud.google.com/apis/credentials/consent
       - Configure as Internal (for organization) or External
       - Add authorized domains
    
    4. Access the Service:
       Once DNS propagates and SSL is ready, access: https://${var.iap_domain}
       Users will be prompted to authenticate via Google.
    
    5. Authorized Users:
       Members with access: ${join(", ", var.iap_allowed_members)}
  EOT : null
}
