/**
 * Environment Debug API Endpoint
 * 
 * Returns environment variable status for debugging configuration issues.
 * This endpoint helps diagnose why ERROR_OBSERVER_URL might not be set.
 * 
 * SECURITY NOTE: Only returns boolean status, not actual values, to avoid
 * exposing sensitive information.
 * 
 * Updated: 2025-12-04 - Force rebuild to pick up ERROR_OBSERVER_URL from Terraform
 */

import { NextResponse } from "next/server";

export async function GET() {
  // Check all error observer related environment variables
  const envStatus = {
    ERROR_OBSERVER_URL: {
      set: !!process.env.ERROR_OBSERVER_URL,
      value: process.env.ERROR_OBSERVER_URL ? "configured" : "not set",
      length: process.env.ERROR_OBSERVER_URL?.length || 0,
    },
    // Other related environment variables
    ENVIRONMENT: process.env.ENVIRONMENT || "not set",
    NODE_ENV: process.env.NODE_ENV || "not set",
    GOOGLE_CLOUD_PROJECT: {
      set: !!process.env.GOOGLE_CLOUD_PROJECT,
      value: process.env.GOOGLE_CLOUD_PROJECT ? "configured" : "not set",
    },
    USE_VERTEX_AI: process.env.USE_VERTEX_AI || "not set",
  };

  return NextResponse.json({
    endpoint: "/api/debug/env",
    timestamp: new Date().toISOString(),
    envStatus,
    recommendations: [
      "ERROR_OBSERVER_URL should be set via Terraform: google_cloud_run_v2_service.error_observer.uri",
      "Check Cloud Run service configuration in GCP Console",
      "Verify error_observer service is deployed and running",
      "Check that ag-ui-frontend service has latest revision deployed",
    ],
  });
}
