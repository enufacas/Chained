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
