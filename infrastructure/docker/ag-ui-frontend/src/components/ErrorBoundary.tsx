/**
 * Error Boundary Component
 * 
 * Catches React component errors and logs them for debugging.
 * Displays a fallback UI when errors occur.
 * 
 * Based on React Error Boundary pattern:
 * https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary
 */

"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Log error with structured format for GCP logs
 */
function logErrorToConsole(error: Error, errorInfo: ErrorInfo, context?: string) {
  const timestamp = new Date().toISOString();
  const errorData = {
    timestamp,
    context: context || "ErrorBoundary",
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack,
    },
    componentStack: errorInfo.componentStack,
    userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "unknown",
  };
  
  // Log to console for GCP Cloud Run logs
  console.error(`[${timestamp}] [ErrorBoundary] React component error:`, JSON.stringify(errorData, null, 2));
}

/**
 * Send error to backend API for persistent logging
 */
async function sendErrorToBackend(error: Error, errorInfo: ErrorInfo) {
  try {
    const errorPayload = {
      type: "react-error",
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "unknown",
      url: typeof window !== "undefined" ? window.location.href : "unknown",
    };
    
    // Send to debug endpoint
    await fetch("/api/debug/log-error", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(errorPayload),
    });
    
    // Also send to A2A error observer
    await fetch("/api/ui-error-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: error.message,
        stack: error.stack,
        url: errorPayload.url,
        user_agent: errorPayload.userAgent,
        extra: {
          type: "react-error",
          componentStack: errorInfo.componentStack,
          errorName: error.name,
        },
      }),
    });
  } catch (err) {
    // Failed to send error - just log to console
    console.warn("[ErrorBoundary] Failed to send error to backend:", err);
  }
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details
    logErrorToConsole(error, errorInfo);
    
    // Send to backend for persistent logging
    sendErrorToBackend(error, errorInfo).catch(() => {
      // Ignore backend logging failures
    });
    
    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    
    // Update state with error info
    this.setState({
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Render custom fallback or default error UI
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <div className="bg-slate-800 border border-red-500/30 rounded-xl p-6 max-w-2xl w-full">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-4xl">⚠️</span>
              <div>
                <h2 className="text-xl font-bold text-red-400">Something went wrong</h2>
                <p className="text-slate-400 text-sm">The application encountered an unexpected error</p>
              </div>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-4 mb-4 font-mono text-sm">
              <div className="text-red-400 mb-2">
                {this.state.error?.name || "Error"}
              </div>
              <div className="text-slate-300">
                {this.state.error?.message || "Unknown error"}
              </div>
              {process.env.NODE_ENV === "development" && this.state.error?.stack && (
                <details className="mt-3">
                  <summary className="text-slate-500 cursor-pointer hover:text-slate-400">
                    Stack trace
                  </summary>
                  <pre className="mt-2 text-xs text-slate-500 whitespace-pre-wrap">
                    {this.state.error.stack}
                  </pre>
                </details>
              )}
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={this.handleReset}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Try again
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Reload page
              </button>
            </div>
            
            <div className="mt-4 text-xs text-slate-500">
              Error logged to console. Check browser DevTools for details.
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Higher-order component to wrap components with error boundary
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
) {
  return function WithErrorBoundary(props: P) {
    return (
      <ErrorBoundary fallback={fallback}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}
