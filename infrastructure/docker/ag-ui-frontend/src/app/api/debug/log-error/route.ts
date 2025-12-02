/**
 * Error Logging API Endpoint
 * 
 * Accepts frontend errors and logs them to GCP Cloud Run logs.
 * This provides a centralized place to capture client-side errors
 * that would otherwise be invisible in server logs.
 */

import { NextRequest, NextResponse } from "next/server";

interface ErrorLogRequest {
  type: "react-error" | "api-error" | "storage-error" | "generic";
  error: {
    name: string;
    message: string;
    stack?: string;
  };
  componentStack?: string;
  timestamp: string;
  userAgent: string;
  url: string;
  context?: Record<string, unknown>;
}

function logWithTimestamp(level: "ERROR" | "WARN", message: string, data?: object) {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [Frontend Error Logger] [${level}]`;
  
  if (data) {
    console.log(`${prefix} ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`${prefix} ${message}`);
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as ErrorLogRequest;
    
    // Validate required fields
    if (!body.type || !body.error || !body.timestamp) {
      logWithTimestamp("WARN", "Invalid error log request - missing required fields", { body });
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }
    
    // Extract error details
    const errorData = {
      type: body.type,
      errorName: body.error.name,
      errorMessage: body.error.message,
      errorStack: body.error.stack,
      componentStack: body.componentStack,
      timestamp: body.timestamp,
      userAgent: body.userAgent,
      url: body.url,
      context: body.context,
    };
    
    // Log to GCP Cloud Run logs based on error type
    if (body.type === "react-error") {
      logWithTimestamp("ERROR", "React component error captured", errorData);
    } else if (body.type === "api-error") {
      logWithTimestamp("ERROR", "API call error captured", errorData);
    } else if (body.type === "storage-error") {
      logWithTimestamp("WARN", "Storage operation error captured", errorData);
    } else {
      logWithTimestamp("ERROR", "Generic frontend error captured", errorData);
    }
    
    return NextResponse.json({ success: true, logged: true });
  } catch (error) {
    logWithTimestamp("ERROR", "Failed to process error log request", {
      error: error instanceof Error ? error.message : String(error),
    });
    
    return NextResponse.json(
      { error: "Failed to log error" },
      { status: 500 }
    );
  }
}
