# =============================================================================
# Chained GCP Infrastructure - Outputs
# =============================================================================

output "website_url" {
  description = "URL of the deployed website"
  value       = google_cloud_run_v2_service.website.uri
}

output "agent_gateway_url" {
  description = "URL of the agent gateway API"
  value       = google_cloud_run_v2_service.agent_gateway.uri
}

output "agent_worker_url" {
  description = "URL of the agent worker service"
  value       = google_cloud_run_v2_service.agent_worker.uri
}

output "artifact_registry_repository" {
  description = "Artifact Registry repository for container images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.chained.repository_id}"
}

output "pubsub_topic" {
  description = "Pub/Sub topic for agent task messages"
  value       = google_pubsub_topic.agent_tasks.name
}

output "pubsub_subscription" {
  description = "Pub/Sub subscription for agent workers"
  value       = google_pubsub_subscription.agent_tasks.name
}

output "agent_gateway_service_account" {
  description = "Service account email for agent gateway"
  value       = google_service_account.agent_gateway.email
}

output "agent_worker_service_account" {
  description = "Service account email for agent workers"
  value       = google_service_account.agent_worker.email
}

output "project_number" {
  description = "GCP project number"
  value       = data.google_project.current.number
}

# =============================================================================
# Summary Output
# =============================================================================

output "deployment_summary" {
  description = "Summary of deployed infrastructure"
  value = <<-EOT
    
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                    CHAINED GCP INFRASTRUCTURE DEPLOYED                      ║
    ╠════════════════════════════════════════════════════════════════════════════╣
    ║                                                                             ║
    ║  🌐 Website URL:        ${google_cloud_run_v2_service.website.uri}
    ║                                                                             ║
    ║  🤖 Agent Gateway:      ${google_cloud_run_v2_service.agent_gateway.uri}
    ║                                                                             ║
    ║  📦 Container Registry: ${var.region}-docker.pkg.dev/${var.project_id}/chained
    ║                                                                             ║
    ║  📨 Pub/Sub Topic:      ${google_pubsub_topic.agent_tasks.name}
    ║                                                                             ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    Next Steps:
    1. Build and push container images to Artifact Registry
    2. Update terraform.tfvars with image paths
    3. Run 'terraform apply' to update services
    
  EOT
}
