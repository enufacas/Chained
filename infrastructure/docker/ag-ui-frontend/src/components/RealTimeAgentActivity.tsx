/**
 * RealTimeAgentActivity Component
 *
 * Displays real-time agent activity based on actual GCP Cloud Run deployed agents.
 * Fetches health status from /api/activity periodically and shows:
 * - Live agent status with health indicators
 * - Response times and version info
 * - System health overview
 */

"use client";

import { useState, useEffect, useCallback } from "react";

interface AgentHealth {
  status: "healthy" | "unhealthy" | "unknown";
  agent: string;
  version?: string;
  ai_mode?: string;
  timestamp?: string;
  responseTimeMs?: number;
}

interface AgentInfo {
  id: string;
  name: string;
  displayName: string;
  icon: string;
  description: string;
  url: string;
  health: AgentHealth;
  agentCard?: {
    name: string;
    version: string;
    skills: Array<{ id: string; name: string; description: string }>;
  };
}

interface ActivityData {
  agents: AgentInfo[];
  systemStatus: {
    healthy: number;
    unhealthy: number;
    total: number;
    overallHealth: "healthy" | "degraded" | "unhealthy";
  };
  adkApiUrl: string;
  lastUpdated: string;
  source: "gcp-cloudrun";
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffMs / 60000);

  if (diffSecs < 10) return "just now";
  if (diffSecs < 60) return `${diffSecs}s ago`;
  if (diffMins < 60) return `${diffMins}m ago`;
  return date.toLocaleTimeString();
}

export default function RealTimeAgentActivity() {
  const [activity, setActivity] = useState<ActivityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActivity = useCallback(async () => {
    try {
      const response = await fetch("/api/activity");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      setActivity(data);
      setError(null);
    } catch (err) {
      console.error("[RealTimeAgentActivity] Fetch error:", err);
      setError(err instanceof Error ? err.message : "Failed to load activity");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActivity();
    
    // Refresh every 5 seconds for more real-time updates
    let interval: NodeJS.Timeout | null = null;
    
    const startPolling = () => {
      if (!interval) {
        interval = setInterval(fetchActivity, 5000);
      }
    };
    
    const stopPolling = () => {
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    };
    
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        fetchActivity(); // Refresh immediately when becoming visible
        startPolling();
      } else {
        stopPolling();
      }
    };
    
    // Start polling if visible
    if (document.visibilityState === "visible") {
      startPolling();
    }
    
    document.addEventListener("visibilitychange", handleVisibilityChange);
    
    return () => {
      stopPolling();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [fetchActivity]);

  if (loading) {
    return (
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 mb-6 animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-12 bg-slate-700 rounded"></div>
          <div className="h-12 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (error && !activity) {
    return (
      <div className="bg-slate-800 rounded-xl border border-red-500/30 p-6 mb-6">
        <div className="flex items-center gap-2 text-red-400">
          <span>⚠️</span>
          <span>Failed to load agent activity: {error}</span>
        </div>
      </div>
    );
  }

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "unhealthy":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      default:
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    }
  };

  const getOverallHealthBadge = (health: string) => {
    switch (health) {
      case "healthy":
        return (
          <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full border border-green-500/30">
            ✓ All Healthy
          </span>
        );
      case "degraded":
        return (
          <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full border border-yellow-500/30">
            ⚠ Degraded
          </span>
        );
      default:
        return (
          <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full border border-red-500/30">
            ✗ Unhealthy
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden mb-6">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">☁️</span>
          <div>
            <h3 className="font-semibold text-white flex items-center gap-2">
              GCP Cloud Run Agents
              {activity && getOverallHealthBadge(activity.systemStatus.overallHealth)}
            </h3>
            <p className="text-xs text-slate-500">
              Live status from deployed A2A agents
            </p>
          </div>
        </div>
        <div className="text-xs text-slate-500">
          Updated {activity ? formatTimeAgo(activity.lastUpdated) : "..."}
        </div>
      </div>

      {/* Stats Bar */}
      {activity && (
        <div className="px-4 py-3 bg-slate-900/50 border-b border-slate-700 flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full"></span>
            <span className="text-green-400 font-semibold">{activity.systemStatus.healthy}</span>
            <span className="text-slate-400">Healthy</span>
          </div>
          {activity.systemStatus.unhealthy > 0 && (
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-red-400 rounded-full"></span>
              <span className="text-red-400 font-semibold">{activity.systemStatus.unhealthy}</span>
              <span className="text-slate-400">Unhealthy</span>
            </div>
          )}
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-semibold">{activity.systemStatus.total}</span>
            <span className="text-slate-400">Total Agents</span>
          </div>
        </div>
      )}

      {/* Agent List */}
      {activity && (
        <div className="p-4">
          <h4 className="text-xs text-slate-500 uppercase tracking-wider mb-3">
            Deployed Agents
          </h4>
          <div className="space-y-2">
            {activity.agents.map((agent) => (
              <div
                key={agent.id}
                className={`flex items-center gap-3 p-3 rounded-lg border transition ${getHealthStatusColor(agent.health.status)}`}
              >
                <span className="text-xl">{agent.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-white truncate">{agent.displayName}</div>
                  <div className="text-xs text-slate-400 truncate">
                    {agent.description}
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-2">
                    {agent.health.status === "healthy" ? (
                      <span className="flex items-center gap-1 text-xs text-green-400">
                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
                        Online
                      </span>
                    ) : agent.health.status === "unhealthy" ? (
                      <span className="flex items-center gap-1 text-xs text-red-400">
                        <span className="w-1.5 h-1.5 bg-red-400 rounded-full"></span>
                        Offline
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-yellow-400">
                        <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full"></span>
                        Unknown
                      </span>
                    )}
                  </div>
                  {agent.health.responseTimeMs !== undefined && (
                    <div className="text-xs text-slate-500 mt-0.5">
                      {agent.health.responseTimeMs}ms
                    </div>
                  )}
                  {agent.health.version && (
                    <div className="text-xs text-slate-500">
                      v{agent.health.version}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer with ADK API URL */}
      {activity && (
        <div className="px-4 py-3 bg-slate-900/30 border-t border-slate-700">
          <div className="text-xs text-slate-500 text-center">
            <span>ADK API: </span>
            <code className="bg-black/30 px-1.5 py-0.5 rounded text-accent-400">
              {activity.adkApiUrl}
            </code>
          </div>
        </div>
      )}
    </div>
  );
}
