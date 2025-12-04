/**
 * ErrorObserverStatus Component
 *
 * Displays the real-time status of the error_observer agent showing:
 * - Current state (idle, ingesting, dispatching, success, failure)
 * - Last error processed
 * - Recent error history
 * - Dispatch statistics
 *
 * This component integrates with the existing A2A UI patterns and polls
 * the error_observer /status endpoint for live updates.
 */

"use client";

import { useState, useEffect, useCallback } from "react";

// =============================================================================
// Types
// =============================================================================

interface ErrorSummary {
  error_hash: string;
  service: string;
  message: string;
  timestamp: string;
  dispatch_status: string;
}

interface ErrorEventDetail {
  service: string;
  region: string;
  environment: string;
  error_message: string;
  stack_trace?: string | null;
  logs: string[];
  run_console_url?: string | null;
  a2a_ui_url?: string | null;
  error_hash: string;
  first_seen: string;
  last_seen: string;
  occurrences: number;
  source_agent?: string | null;
  source_channel: string;
  metadata: Record<string, unknown>;
}

interface ErrorObserverState {
  status: "idle" | "ingesting" | "dispatching" | "success" | "failure";
  status_message: string;
  last_error: ErrorEventDetail | null;
  last_dispatch_time: string | null;
  last_dispatch_status: string | null;
  errors_handled_24h: number;
  recent_errors: ErrorSummary[];
}

interface ErrorObserverStatusData {
  configured: boolean;
  url?: string;
  state: ErrorObserverState | null;
  lastUpdated: string;
}

// =============================================================================
// Helper Functions
// =============================================================================

function truncateMessage(message: string, maxLength: number = 100): string {
  if (!message) return "";
  if (message.length <= maxLength) return message;
  return message.substring(0, maxLength) + "...";
}

// =============================================================================
// Component
// =============================================================================

export default function ErrorObserverStatus() {
  const [statusData, setStatusData] = useState<ErrorObserverStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [dispatching, setDispatching] = useState(false);
  const [dispatchResult, setDispatchResult] = useState<{ success: boolean; message: string } | null>(null);
  const [webhookDispatching, setWebhookDispatching] = useState(false);
  const [webhookResult, setWebhookResult] = useState<{ success: boolean; message: string } | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      // Call our backend API that proxies to error_observer /status
      const response = await fetch("/api/error-observer/status");
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      setStatusData(data);
      setError(null);
    } catch (err) {
      console.error("[ErrorObserverStatus] Fetch error:", err);
      setError(err instanceof Error ? err.message : "Failed to load status");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleTestDispatch = useCallback(async () => {
    setDispatching(true);
    setDispatchResult(null);

    try {
      // Send a test error to the ui-error-report endpoint
      const response = await fetch("/api/ui-error-report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: "Test error dispatch from Error Observer UI",
          stack: "TestError: This is a placeholder error for testing error observer functionality\n    at handleTestDispatch (ErrorObserverStatus.tsx)",
          url: window.location.href,
          user_agent: navigator.userAgent,
          extra: {
            test: true,
            timestamp: new Date().toISOString(),
            purpose: "Verify error observer dispatch activities",
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setDispatchResult({
          success: true,
          message: `Test error dispatched successfully! Hash: ${data.error_hash || "N/A"}`,
        });
        
        // Refresh status after dispatch
        setTimeout(() => {
          fetchStatus();
        }, 1000);
      } else {
        setDispatchResult({
          success: false,
          message: data.message || "Test dispatch failed",
        });
      }
    } catch (err) {
      console.error("[ErrorObserverStatus] Test dispatch error:", err);
      setDispatchResult({
        success: false,
        message: err instanceof Error ? err.message : "Test dispatch failed",
      });
    } finally {
      setDispatching(false);
      
      // Clear result after 5 seconds
      setTimeout(() => {
        setDispatchResult(null);
      }, 5000);
    }
  }, [fetchStatus]);

  const handleTestWebhook = useCallback(async () => {
    setWebhookDispatching(true);
    setWebhookResult(null);

    try {
      // Send a test webhook to GitHub via error observer
      const response = await fetch("/api/test-github-webhook", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          test_type: "full", // Send full test with stack trace
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setWebhookResult({
          success: true,
          message: `Test webhook dispatched! Check GitHub Actions for workflow run.`,
        });
        
        // Refresh status after webhook
        setTimeout(() => {
          fetchStatus();
        }, 1000);
      } else {
        setWebhookResult({
          success: false,
          message: data.message || "Test webhook failed",
        });
      }
    } catch (err) {
      console.error("[ErrorObserverStatus] Test webhook error:", err);
      setWebhookResult({
        success: false,
        message: err instanceof Error ? err.message : "Test webhook failed",
      });
    } finally {
      setWebhookDispatching(false);
      
      // Clear result after 5 seconds
      setTimeout(() => {
        setWebhookResult(null);
      }, 5000);
    }
  }, [fetchStatus]);

  useEffect(() => {
    fetchStatus();
    
    // Poll every 3 seconds for real-time updates
    const interval = setInterval(fetchStatus, 3000);
    
    return () => clearInterval(interval);
  }, [fetchStatus]);

  // Loading state
  if (loading) {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-slate-600 rounded-full animate-pulse" />
          <span className="text-slate-400 text-sm">Loading Error Observer...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-slate-800/50 border border-red-500/30 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <div className="text-sm font-medium text-red-400">Error Observer Unavailable</div>
            <div className="text-xs text-slate-500">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  // Not configured
  if (!statusData?.configured) {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 space-y-3">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🔧</span>
          <div className="flex-1">
            <div className="text-sm font-medium text-slate-300">Error Observer</div>
            <div className="text-xs text-slate-500">Not configured (ERROR_OBSERVER_URL not set)</div>
          </div>
        </div>
        
        {/* Test Dispatch Section */}
        <div className="border-t border-slate-700/50 pt-3">
          <p className="text-xs text-slate-400 mb-2">
            Test error dispatch to verify configuration:
          </p>
          <button
            onClick={handleTestDispatch}
            disabled={dispatching}
            className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              dispatching
                ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                : "bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 border border-blue-500/30"
            }`}
          >
            {dispatching ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⏳</span>
                Dispatching...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <span>🧪</span>
                Send Test Error
              </span>
            )}
          </button>
          
          {/* Dispatch Result */}
          {dispatchResult && (
            <div
              className={`mt-2 p-2 rounded text-xs ${
                dispatchResult.success
                  ? "bg-green-500/10 border border-green-500/30 text-green-400"
                  : "bg-red-500/10 border border-red-500/30 text-red-400"
              }`}
            >
              <div className="flex items-start gap-2">
                <span>{dispatchResult.success ? "✓" : "✗"}</span>
                <span className="flex-1">{dispatchResult.message}</span>
              </div>
            </div>
          )}
          
          <p className="text-xs text-slate-600 mt-2">
            Check Cloud Run logs if dispatch fails. The error observer URL should be configured in Terraform.
          </p>
          <a 
            href="/api/debug/env" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs text-blue-400 hover:text-blue-300 underline block mt-1"
          >
            🔍 View environment debug info
          </a>
        </div>
        
        {/* Test GitHub Webhook Section */}
        <div className="border-t border-slate-700/50 pt-3">
          <p className="text-xs text-slate-400 mb-2">
            Test GitHub webhook for cloud run errors pipeline:
          </p>
          <button
            onClick={handleTestWebhook}
            disabled={webhookDispatching}
            className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              webhookDispatching
                ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                : "bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 border border-purple-500/30"
            }`}
          >
            {webhookDispatching ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⏳</span>
                Dispatching to GitHub...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <span>🎯</span>
                Test GitHub Webhook
              </span>
            )}
          </button>
          
          {/* Webhook Result */}
          {webhookResult && (
            <div
              className={`mt-2 p-2 rounded text-xs ${
                webhookResult.success
                  ? "bg-green-500/10 border border-green-500/30 text-green-400"
                  : "bg-red-500/10 border border-red-500/30 text-red-400"
              }`}
            >
              <div className="flex items-start gap-2">
                <span>{webhookResult.success ? "✓" : "✗"}</span>
                <span className="flex-1">{webhookResult.message}</span>
              </div>
            </div>
          )}
          
          <p className="text-xs text-slate-600 mt-2">
            This fires a repository_dispatch webhook to GitHub to test the handle-cloudrun-errors workflow.
          </p>
        </div>
      </div>
    );
  }

  const state = statusData.state;
  
  // Configured but error fetching status
  if (statusData.configured && !state && 'error' in statusData) {
    return (
      <div className="bg-slate-800/50 border border-yellow-500/30 rounded-xl p-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <div className="text-sm font-medium text-yellow-400">Error Observer</div>
            <div className="text-xs text-slate-500">
              Configured but unreachable: {statusData.error as string}
            </div>
            <div className="text-xs text-slate-600 mt-1">
              URL: {statusData.url}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!state) {
    return null;
  }

  // Get status color and icon
  const getStatusDisplay = () => {
    switch (state.status) {
      case "idle":
        return {
          color: "text-slate-400",
          bgColor: "bg-slate-600/30",
          icon: "⏸️",
          pulseClass: "",
        };
      case "ingesting":
        return {
          color: "text-blue-400",
          bgColor: "bg-blue-600/30",
          icon: "📥",
          pulseClass: "animate-pulse",
        };
      case "dispatching":
        return {
          color: "text-yellow-400",
          bgColor: "bg-yellow-600/30",
          icon: "📤",
          pulseClass: "animate-pulse",
        };
      case "success":
        return {
          color: "text-green-400",
          bgColor: "bg-green-600/30",
          icon: "✅",
          pulseClass: "",
        };
      case "failure":
        return {
          color: "text-red-400",
          bgColor: "bg-red-600/30",
          icon: "❌",
          pulseClass: "",
        };
      default:
        return {
          color: "text-slate-400",
          bgColor: "bg-slate-600/30",
          icon: "❓",
          pulseClass: "",
        };
    }
  };

  const statusDisplay = getStatusDisplay();

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
      {/* Header - Always visible */}
      <div 
        className="p-4 cursor-pointer hover:bg-slate-800/70 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Status indicator */}
            <div className={`relative ${statusDisplay.pulseClass}`}>
              <div className={`w-3 h-3 ${statusDisplay.bgColor} rounded-full`} />
              <div className="absolute inset-0 flex items-center justify-center text-xs">
                {statusDisplay.icon}
              </div>
            </div>
            
            <div>
              <div className="text-sm font-medium text-slate-200">
                Error Observer
                <span className={`ml-2 ${statusDisplay.color} text-xs`}>
                  {state.status.toUpperCase()}
                </span>
              </div>
              <div className="text-xs text-slate-500">
                {state.status_message}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* 24h count badge */}
            {state.errors_handled_24h > 0 && (
              <div className="flex items-center gap-1 bg-slate-700/50 rounded-full px-2 py-1">
                <span className="text-xs text-slate-400">24h:</span>
                <span className="text-xs font-medium text-slate-300">
                  {state.errors_handled_24h}
                </span>
              </div>
            )}
            
            {/* Expand/collapse indicator */}
            <div className={`text-slate-500 transition-transform ${expanded ? 'rotate-180' : ''}`}>
              ▼
            </div>
          </div>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-slate-700/50 p-4 space-y-3">
          {/* Last error details */}
          {state.last_error && (
            <div className="bg-slate-900/50 rounded-lg p-3">
              <div className="text-xs font-medium text-slate-400 mb-2">
                Last Error Processed
              </div>
              <div className="space-y-1">
                <div className="text-xs">
                  <span className="text-slate-500">Service:</span>
                  <span className="ml-2 text-slate-300 font-mono">
                    {state.last_error.service}
                  </span>
                </div>
                <div className="text-xs">
                  <span className="text-slate-500">Message:</span>
                  <span className="ml-2 text-slate-300">
                    {truncateMessage(state.last_error.error_message)}
                  </span>
                </div>
                <div className="text-xs">
                  <span className="text-slate-500">Hash:</span>
                  <span className="ml-2 text-slate-400 font-mono">
                    {state.last_error.error_hash}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Recent errors */}
          {state.recent_errors && state.recent_errors.length > 0 && (
            <div className="bg-slate-900/50 rounded-lg p-3">
              <div className="text-xs font-medium text-slate-400 mb-2">
                Recent Errors ({state.recent_errors.length})
              </div>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {state.recent_errors.map((err, idx) => (
                  <div 
                    key={idx}
                    className="bg-slate-800/50 rounded p-2 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 font-mono">
                        {err.service}
                      </span>
                      <span className={`text-xs ${
                        err.dispatch_status === "success" 
                          ? "text-green-400" 
                          : "text-red-400"
                      }`}>
                        {err.dispatch_status === "success" ? "✓" : "✗"}
                      </span>
                    </div>
                    <div className="text-slate-500 truncate">
                      {err.message}
                    </div>
                    <div className="text-slate-600 text-[10px]">
                      {new Date(err.timestamp).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dispatch stats */}
          {state.last_dispatch_time && (
            <div className="bg-slate-900/50 rounded-lg p-3">
              <div className="text-xs font-medium text-slate-400 mb-2">
                Last Dispatch
              </div>
              <div className="space-y-1">
                <div className="text-xs">
                  <span className="text-slate-500">Status:</span>
                  <span className={`ml-2 font-medium ${
                    state.last_dispatch_status === "success"
                      ? "text-green-400"
                      : "text-red-400"
                  }`}>
                    {state.last_dispatch_status?.toUpperCase()}
                  </span>
                </div>
                <div className="text-xs text-slate-500">
                  {new Date(state.last_dispatch_time).toLocaleString()}
                </div>
              </div>
            </div>
          )}
          
          {/* Test Dispatch Button - Always available when expanded */}
          <div className="bg-slate-900/50 rounded-lg p-3">
            <div className="text-xs font-medium text-slate-400 mb-2">
              Test Dispatch
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleTestDispatch();
              }}
              disabled={dispatching}
              className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                dispatching
                  ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                  : "bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 border border-blue-500/30"
              }`}
            >
              {dispatching ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">⏳</span>
                  Dispatching...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <span>🧪</span>
                  Send Test Error
                </span>
              )}
            </button>
            
            {/* Dispatch Result */}
            {dispatchResult && (
              <div
                className={`mt-2 p-2 rounded text-xs ${
                  dispatchResult.success
                    ? "bg-green-500/10 border border-green-500/30 text-green-400"
                    : "bg-red-500/10 border border-red-500/30 text-red-400"
                }`}
              >
                <div className="flex items-start gap-2">
                  <span>{dispatchResult.success ? "✓" : "✗"}</span>
                  <span className="flex-1">{dispatchResult.message}</span>
                </div>
              </div>
            )}
            
            <p className="text-xs text-slate-600 mt-2">
              Sends a placeholder error to verify dispatch functionality.
            </p>
          </div>
          
          {/* Test GitHub Webhook Button */}
          <div className="bg-slate-900/50 rounded-lg p-3">
            <div className="text-xs font-medium text-slate-400 mb-2">
              Test GitHub Webhook
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleTestWebhook();
              }}
              disabled={webhookDispatching}
              className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                webhookDispatching
                  ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                  : "bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 border border-purple-500/30"
              }`}
            >
              {webhookDispatching ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">⏳</span>
                  Dispatching to GitHub...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <span>🎯</span>
                  Test GitHub Webhook
                </span>
              )}
            </button>
            
            {/* Webhook Result */}
            {webhookResult && (
              <div
                className={`mt-2 p-2 rounded text-xs ${
                  webhookResult.success
                    ? "bg-green-500/10 border border-green-500/30 text-green-400"
                    : "bg-red-500/10 border border-red-500/30 text-red-400"
                }`}
              >
                <div className="flex items-start gap-2">
                  <span>{webhookResult.success ? "✓" : "✗"}</span>
                  <span className="flex-1">{webhookResult.message}</span>
                </div>
              </div>
            )}
            
            <p className="text-xs text-slate-600 mt-2">
              Fires repository_dispatch to test handle-cloudrun-errors workflow.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
