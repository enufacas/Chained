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

# =============================================================================
# AI-Native Control Plane Outputs
# =============================================================================

output "ai_native_control_plane_url" {
  description = "URL of the AI Control Plane service"
  value       = var.deploy_ai_native_control_plane ? try(google_cloud_run_v2_service.ai_control_plane[0].uri, "Not deployed") : "Not enabled"
}

output "ai_native_infra_runner_url" {
  description = "URL of the Infra Runner service"
  value       = var.deploy_ai_native_control_plane ? try(google_cloud_run_v2_service.infra_runner[0].uri, "Not deployed") : "Not enabled"
}

output "ai_native_database_instance" {
  description = "Cloud SQL instance name for AI-Native Control Plane"
  value       = var.deploy_ai_native_control_plane ? try(google_sql_database_instance.ai_native_db[0].name, "Not deployed") : "Not enabled"
}

output "ai_native_database_connection" {
  description = "Cloud SQL connection name"
  value       = var.deploy_ai_native_control_plane ? try(google_sql_database_instance.ai_native_db[0].connection_name, "Not deployed") : "Not enabled"
}

output "ai_native_database_private_ip" {
  description = "Private IP address of Cloud SQL instance"
  value       = var.deploy_ai_native_control_plane ? try(google_sql_database_instance.ai_native_db[0].private_ip_address, "Not deployed") : "Not enabled"
  sensitive   = true
}

output "ai_native_vpc_connector" {
  description = "VPC Access Connector for Cloud Run"
  value       = var.deploy_ai_native_control_plane ? try(google_vpc_access_connector.ai_native_connector[0].name, "Not deployed") : "Not enabled"
}

output "ai_native_deployment_summary" {
  description = "Summary of AI-Native Control Plane deployment"
  value = var.deploy_ai_native_control_plane ? <<-EOT
    
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║              AI-NATIVE CONTROL PLANE INFRASTRUCTURE DEPLOYED                ║
    ╠════════════════════════════════════════════════════════════════════════════╣
    ║                                                                             ║
    ║  🧠 AI Control Plane:   ${try(google_cloud_run_v2_service.ai_control_plane[0].uri, "Not deployed")}
    ║                                                                             ║
    ║  🏗️  Infra Runner:       ${try(google_cloud_run_v2_service.infra_runner[0].uri, "Not deployed")}
    ║                                                                             ║
    ║  🗄️  Database:           ${try(google_sql_database_instance.ai_native_db[0].name, "Not deployed")}
    ║      Database Name:     ai_native_control_plane
    ║      Database User:     ai_native_admin
    ║                                                                             ║
    ║  🔐 Secrets (Manual Setup Required):                                        ║
    ║      - ai-native-openai-api-key                                            ║
    ║      - ai-native-gemini-api-key                                            ║
    ║                                                                             ║
    ║  🔧 VPC Connector:      ${try(google_vpc_access_connector.ai_native_connector[0].name, "Not deployed")}
    ║                                                                             ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    
    Next Steps:
    1. Set API keys in Secret Manager:
       echo -n "YOUR_KEY" | gcloud secrets versions add ai-native-openai-api-key --data-file=-
       echo -n "YOUR_KEY" | gcloud secrets versions add ai-native-gemini-api-key --data-file=-
    
    2. Run database migrations:
       kubectl run psql --image=postgres:15 --rm -it -- psql "${try(format("postgresql://ai_native_admin@%s/ai_native_control_plane", google_sql_database_instance.ai_native_db[0].private_ip_address), "")}"
       \i /migrations/001_initial_schema.sql
       \i /migrations/002_add_vector_support.sql
    
    3. Test the API:
       curl -X POST ${try(google_cloud_run_v2_service.ai_control_plane[0].uri, "")}/execute \
         -H "Content-Type: application/json" \
         -d '{"user_request": "Create a simple blog website", "user_id": "test-user"}'
    
  EOT
  : "AI-Native Control Plane deployment is disabled (deploy_ai_native_control_plane = false)"
}
