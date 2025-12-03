/**
 * Error Observer Status API Route
 *
 * Proxies requests to the error_observer agent's /status endpoint
 * and provides the current state for UI visualization.
 */

import { NextResponse } from "next/server";

// =============================================================================
// API Route Handler
// =============================================================================

export async function GET() {
  // Read environment variable at runtime (not at build time)
  // This ensures Cloud Run environment variables are available
  const ERROR_OBSERVER_URL = 
    process.env.ERROR_OBSERVER_URL || 
    process.env.AGENT_ERROR_OBSERVER_URL ||
    "";
  
  // Log for debugging (will appear in Cloud Run logs)
  console.log("[Error Observer Status] ERROR_OBSERVER_URL:", ERROR_OBSERVER_URL ? "configured" : "not configured");
  
  // Check if error observer is configured
  if (!ERROR_OBSERVER_URL) {
    return NextResponse.json({
      configured: false,
      state: null,
      lastUpdated: new Date().toISOString(),
    });
  }

  try {
    // Fetch status from error_observer agent
    const response = await fetch(`${ERROR_OBSERVER_URL}/status`, {
      method: "GET",
      headers: {
        "Accept": "application/json",
      },
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    if (!response.ok) {
      console.error(`Error observer returned HTTP ${response.status}`);
      
      return NextResponse.json(
        {
          configured: true,
          url: ERROR_OBSERVER_URL,
          state: null,
          error: `HTTP ${response.status}`,
          lastUpdated: new Date().toISOString(),
        },
        { status: 200 } // Return 200 but with error state
      );
    }

    const state = await response.json();

    return NextResponse.json({
      configured: true,
      url: ERROR_OBSERVER_URL,
      state,
      lastUpdated: new Date().toISOString(),
    });

  } catch (error) {
    console.error("Failed to fetch error observer status:", error);
    
    return NextResponse.json(
      {
        configured: true,
        url: ERROR_OBSERVER_URL,
        state: null,
        error: error instanceof Error ? error.message : "Unknown error",
        lastUpdated: new Date().toISOString(),
      },
      { status: 200 } // Return 200 but with error state
    );
  }
}
