/**
 * Test GitHub Webhook API Endpoint
 * 
 * This endpoint fires a test repository_dispatch event directly to GitHub
 * to test the cloud run errors pipeline ingestion workflow.
 * 
 * This tests the entire pipeline:
 * 1. Frontend → Error Observer (via A2A)
 * 2. Error Observer → GitHub repository_dispatch
 * 3. GitHub → Workflow trigger (handle-cloudrun-errors.yml)
 * 4. Workflow → Process error and create issue/comment
 */

import { NextResponse } from "next/server";

// =============================================================================
// Configuration
// =============================================================================

const ERROR_OBSERVER_URL = process.env.ERROR_OBSERVER_URL || "";

// =============================================================================
// Types
// =============================================================================

interface TestWebhookRequest {
  test_type?: "minimal" | "full";
}

// =============================================================================
// Helper Functions
// =============================================================================

async function computeErrorHash(service: string, errorMessage: string, taskType: string = "error"): Promise<string> {
  const hashInput = `${service}|${errorMessage}|${taskType}`;
  const encoder = new TextEncoder();
  const data = encoder.encode(hashInput);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex.substring(0, 32);
}

async function sendTestWebhook(testType: string): Promise<{ success: boolean; message: string; details?: unknown }> {
  if (!ERROR_OBSERVER_URL) {
    return {
      success: false,
      message: "ERROR_OBSERVER_URL not configured - cannot send test webhook",
    };
  }
  
  try {
    const now = new Date().toISOString();
    const service = "a2a-ui-test";
    const errorMessage = "Test GitHub webhook dispatch from AG-UI Frontend";
    
    const errorHash = await computeErrorHash(service, errorMessage, "test-webhook");
    
    const stackTrace = testType === "full" 
      ? `TestError: This is a test webhook dispatch to verify GitHub pipeline ingestion
    at handleTestWebhook (route.ts)
    at POST /api/test-github-webhook
    
This is a controlled test to verify:
- GitHub repository_dispatch webhook reception  
- handle-cloudrun-errors.yml workflow triggering
- Error processing and issue creation
- End-to-end pipeline functionality`
      : undefined;
    
    const errorEvent = {
      service,
      region: "us-central1",
      environment: "test",
      error_message: errorMessage,
      stack_trace: stackTrace,
      logs: ["Test webhook dispatch initiated from AG-UI Frontend"],
      error_hash: errorHash,
      first_seen: now,
      last_seen: now,
      occurrences: 1,
      source_agent: "a2a-ui-frontend-test",
      source_channel: "test-webhook",
      a2a_ui_url: `${process.env.NEXT_PUBLIC_ADK_API_URL || "https://example.com"}/test-webhook`,
      metadata: {
        test: true,
        test_type: "github-webhook",
        purpose: "Verify GitHub repository_dispatch pipeline ingestion",
        expected_workflow: "handle-cloudrun-errors.yml",
      },
    };
    
    const response = await fetch(`${ERROR_OBSERVER_URL}/a2a/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: {
          role: "user",
          parts: [{ text: JSON.stringify(errorEvent) }],
        },
        contextId: `test-webhook-${Date.now()}`,
        metadata: {
          error_event: errorEvent,
        },
      }),
      signal: AbortSignal.timeout(15000),
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown error");
      return {
        success: false,
        message: `Error observer returned HTTP ${response.status}`,
        details: errorText,
      };
    }
    
    const result = await response.json();
    
    return {
      success: true,
      message: "Test webhook sent to error observer for GitHub dispatch",
      details: {
        error_hash: errorHash,
        task_id: result.id || "unknown",
        expected_workflow: "handle-cloudrun-errors.yml",
        check_github: `https://github.com/${process.env.GIT_REPO || "enufacas/Chained"}/actions`,
      },
    };
    
  } catch (error) {
    console.error("❌ Error sending test webhook:", error);
    return {
      success: false,
      message: error instanceof Error ? error.message : "Failed to send test webhook",
    };
  }
}

// =============================================================================
// API Route Handler
// =============================================================================

export async function POST(request: Request) {
  try {
    const body = await request.json() as TestWebhookRequest;
    const testType = body.test_type || "minimal";
    
    console.log(`📨 Test GitHub webhook requested (type: ${testType})`);
    
    const result = await sendTestWebhook(testType);
    
    if (result.success) {
      console.log(`✅ Test webhook dispatched successfully`);
      return NextResponse.json(
        {
          success: true,
          message: result.message,
          details: result.details,
          next_steps: [
            "Check GitHub Actions workflow runs",
            "Look for 'Handle Cloud Run Errors' workflow",
            "Verify issue/comment was created",
            "Check error observer logs for dispatch confirmation",
          ],
        },
        { status: 200 }
      );
    } else {
      console.error(`❌ Test webhook failed: ${result.message}`);
      return NextResponse.json(
        {
          success: false,
          message: result.message,
          details: result.details,
          troubleshooting: [
            "Verify ERROR_OBSERVER_URL is configured",
            "Check error_observer service is running",
            "Verify GitHub PAT is configured in error_observer",
            "Check Cloud Run logs for error_observer",
          ],
        },
        { status: 200 }
      );
    }
    
  } catch (error) {
    console.error("❌ Error processing test webhook request:", error);
    
    return NextResponse.json(
      {
        success: false,
        message: "Failed to process test webhook request",
        error: error instanceof Error ? error.message : String(error),
      },
      { status: 200 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: "/api/test-github-webhook",
    status: "operational",
    description: "Test GitHub webhook dispatch for cloud run errors pipeline",
    error_observer_configured: !!ERROR_OBSERVER_URL,
    supported_test_types: ["minimal", "full"],
    usage: {
      method: "POST",
      body: {
        test_type: "minimal | full (optional, default: minimal)",
      },
    },
  });
}
