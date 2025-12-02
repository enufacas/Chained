/**
 * Frontend Error Logging Utilities
 * 
 * Provides structured error logging that sends errors to the backend
 * for persistent logging in GCP Cloud Run logs.
 */

interface ErrorContext {
  component?: string;
  action?: string;
  userId?: string;
  sessionId?: string;
  [key: string]: unknown;
}

interface LogErrorOptions {
  sendToBackend?: boolean;
  context?: ErrorContext;
}

/**
 * Log an error with structured format
 */
export function logError(
  error: Error | unknown,
  type: "react-error" | "api-error" | "storage-error" | "generic" = "generic",
  options: LogErrorOptions = {}
) {
  const timestamp = new Date().toISOString();
  const errorObj = error instanceof Error ? error : new Error(String(error));
  
  const errorData = {
    type,
    timestamp,
    error: {
      name: errorObj.name,
      message: errorObj.message,
      stack: errorObj.stack,
    },
    url: typeof window !== "undefined" ? window.location.href : "unknown",
    userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "unknown",
    context: options.context,
  };
  
  // Always log to console for browser DevTools
  console.error(`[${timestamp}] [Frontend Error] [${type}]`, errorData);
  
  // Optionally send to backend for persistent logging
  if (options.sendToBackend !== false) {
    sendErrorToBackend(errorData).catch((err) => {
      console.warn("[Frontend Error] Failed to send error to backend:", err);
    });
  }
}

/**
 * Send error to backend API
 */
async function sendErrorToBackend(errorData: object): Promise<void> {
  try {
    // Send to debug endpoint for logging
    await fetch("/api/debug/log-error", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(errorData),
    });
    
    // Also send to error observer for A2A error reporting
    await sendErrorToA2AObserver(errorData);
  } catch (err) {
    // Silently fail - error is already logged to console
    // We don't re-throw because this is fire-and-forget logging
    console.warn("[Frontend Error] Backend logging failed:", err);
  }
}

/**
 * Send error to A2A Error Observer
 */
async function sendErrorToA2AObserver(errorData: any): Promise<void> {
  try {
    const errorObj = errorData.error || {};
    
    await fetch("/api/ui-error-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: errorObj.message || "Unknown error",
        stack: errorObj.stack,
        url: errorData.url,
        user_agent: errorData.userAgent,
        extra: {
          type: errorData.type,
          context: errorData.context,
          timestamp: errorData.timestamp,
        },
      }),
    });
  } catch (err) {
    // Silently fail - error is already logged to console
    // This is a fire-and-forget operation
    console.warn("[Frontend Error] Failed to send to A2A observer:", err);
  }
}

/**
 * Log API call errors with request details
 */
export function logApiError(
  error: Error | unknown,
  endpoint: string,
  method: string = "GET",
  context?: ErrorContext
) {
  logError(error, "api-error", {
    sendToBackend: true,
    context: {
      ...context,
      endpoint,
      method,
    },
  });
}

/**
 * Log storage operation errors
 */
export function logStorageError(
  error: Error | unknown,
  operation: string,
  key?: string,
  context?: ErrorContext
) {
  logError(error, "storage-error", {
    sendToBackend: true,
    context: {
      ...context,
      operation,
      key,
    },
  });
}

/**
 * Wrap an async function with error logging
 */
export function withErrorLogging<T extends (...args: Parameters<T>) => ReturnType<T>>(
  fn: T,
  errorType: "api-error" | "storage-error" | "generic" = "generic",
  context?: ErrorContext
): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args);
    } catch (error) {
      logError(error, errorType, { sendToBackend: true, context });
      throw error; // Re-throw to allow caller to handle
    }
  }) as T;
}

/**
 * Setup global error handlers
 */
export function setupGlobalErrorHandlers() {
  if (typeof window === "undefined") return;
  
  // Catch unhandled promise rejections
  window.addEventListener("unhandledrejection", (event) => {
    logError(
      event.reason,
      "generic",
      {
        sendToBackend: true,
        context: {
          type: "unhandled-promise-rejection",
          promise: String(event.promise),
        },
      }
    );
  });
  
  // Catch global errors
  window.addEventListener("error", (event) => {
    logError(
      event.error || new Error(event.message),
      "generic",
      {
        sendToBackend: true,
        context: {
          type: "global-error",
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
        },
      }
    );
  });
}
