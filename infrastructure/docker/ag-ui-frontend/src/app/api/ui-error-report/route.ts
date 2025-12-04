/**
 * UI Error Report API Route
 *
 * This endpoint receives error reports from the frontend and translates them
 * into error_event A2A tasks sent to the error_observer agent.
 *
 * Workflow:
 * 1. Frontend captures unhandled error
 * 2. Frontend POSTs error details to this endpoint
 * 3. Backend creates error_event payload
 * 4. Backend sends A2A task to error_observer agent
 * 5. error_observer processes and forwards to GitHub
 */

import { NextRequest, NextResponse } from "next/server";

// =============================================================================
// Configuration
// =============================================================================

const ERROR_OBSERVER_URL = process.env.ERROR_OBSERVER_URL || "";

// =============================================================================
// Types
// =============================================================================

interface UIErrorReport {
  message: string;
  stack?: string;
  url?: string;
  user_agent?: string;
  extra?: Record<string, unknown>;
}

interface ErrorEvent {
  service: string;
  region: string;
  environment: string;
  error_message: string;
  stack_trace?: string;
  logs: string[];
  error_hash: string;
  first_seen: string;
  last_seen: string;
  occurrences: number;
  source_agent?: string;
  source_channel: string;
  a2a_ui_url?: string;
  metadata?: Record<string, unknown>;
}

// =============================================================================
// Helper Functions
// =============================================================================

async function computeErrorHash(service: string, errorMessage: string, taskType: string = "error"): Promise<string> {
  /**
   * Compute error hash using SHA-256 (consistent with Python implementation).
   * Uses Web Crypto API for proper cryptographic hashing.
   */
  const hashInput = `${service}|${errorMessage}|${taskType}`;
  const encoder = new TextEncoder();
  const data = encoder.encode(hashInput);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  
  // Return first 32 characters (same as Python implementation)
  return hashHex.substring(0, 32);
}

async function createErrorEventFromUIError(report: UIErrorReport): Promise<ErrorEvent> {
  const now = new Date().toISOString();
  const errorHash = await computeErrorHash("a2a-ui", report.message, "ui-error");
  
  const logs: string[] = [];
  if (report.user_agent) {
    logs.push(`User-Agent: ${report.user_agent}`);
  }
  if (report.extra) {
    logs.push(`Extra: ${JSON.stringify(report.extra)}`);
  }
  
  return {
    service: "a2a-ui",
    region: "us-central1",
    environment: process.env.NODE_ENV || "production",
    error_message: report.message,
    stack_trace: report.stack,
    logs,
    error_hash: errorHash,
    first_seen: now,
    last_seen: now,
    occurrences: 1,
    source_agent: "a2a-ui-backend",
    source_channel: "ui",
    a2a_ui_url: report.url,
    metadata: report.extra || {},
  };
}

async function sendErrorToObserver(errorEvent: ErrorEvent): Promise<boolean> {
  if (!ERROR_OBSERVER_URL) {
    console.warn("⚠️ ERROR_OBSERVER_URL not configured, cannot send error event");
    return false;
  }
  
  try {
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
        contextId: `ui-error-${Date.now()}`,
        metadata: {
          error_event: errorEvent,
        },
      }),
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => "Unknown error");
      console.error(`❌ Failed to send error to observer: HTTP ${response.status} - ${errorText}`);
      return false;
    }
    
    const result = await response.json();
    console.log(`✅ Error event sent to observer: ${result.id || "unknown"}`);
    return true;
  
  } catch (error) {
    console.error(`❌ Error sending to observer:`, error);
    return false;
  }
}

// =============================================================================
// API Route Handler
// =============================================================================

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as UIErrorReport;
    
    // Validate required fields
    if (!body.message) {
      return NextResponse.json(
        { error: "Missing required field: message" },
        { status: 400 }
      );
    }
    
    console.log(`📨 UI Error Report received:`, {
      message: body.message.substring(0, 100),
      url: body.url,
      hasStack: !!body.stack,
    });
    
    // Create error event from UI error (async because of hash computation)
    const errorEvent = await createErrorEventFromUIError(body);
    
    // Send to error observer (fire and forget - don't block response)
    // The observer will handle GitHub dispatch
    sendErrorToObserver(errorEvent).catch((error) => {
      console.error("Failed to send error to observer (non-blocking):", error);
    });
    
    // Return success immediately
    return NextResponse.json(
      {
        success: true,
        message: "Error report received",
        error_hash: errorEvent.error_hash,
      },
      { status: 200 }
    );
  
  } catch (error) {
    console.error("❌ Error processing UI error report:", error);
    
    // Even if processing fails, return 200 to not block the UI
    return NextResponse.json(
      {
        success: false,
        message: "Error report received but processing failed",
      },
      { status: 200 }
    );
  }
}

// Health check for the endpoint
export async function GET() {
  return NextResponse.json({
    endpoint: "/api/ui-error-report",
    status: "operational",
    observer_configured: !!ERROR_OBSERVER_URL,
    observer_url: ERROR_OBSERVER_URL ? "configured" : "not configured",
  });
}
