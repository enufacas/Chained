/**
 * PipelineOutcomes Component
 *
 * Displays completed pipeline outcomes from the A2A system.
 * Shows blog posts, artifacts, and other results from agent work.
 * Sources data from the /api/pipeline endpoint.
 */

"use client";

import { useState, useEffect, useCallback } from "react";

interface PipelineResult {
  id: string;
  topic: string;
  status: "pending" | "running" | "completed" | "failed";
  createdAt: string;
  updatedAt: string;
  progress: number;
  currentPhase: string;
  results?: {
    research?: { topic: string; domain: string; keywords: string[] };
    trends?: { trendingKeywords: string[]; recommendedFocus: string };
    blog?: { title: string; url: string; wordCount: number };
  };
}

interface PipelineListResponse {
  pipelines: PipelineResult[];
  total: number;
  activePipelinesCount: number;
}

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
}

export default function PipelineOutcomes() {
  const [data, setData] = useState<PipelineListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPipelines = useCallback(async () => {
    try {
      const response = await fetch("/api/pipeline?limit=10");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      console.error("[PipelineOutcomes] Fetch error:", err);
      setError(err instanceof Error ? err.message : "Failed to load pipelines");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPipelines();
    
    // Refresh every 30 seconds to catch pipeline completions
    let interval: NodeJS.Timeout | null = null;
    
    const startPolling = () => {
      if (!interval) {
        interval = setInterval(fetchPipelines, 30000);
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
        fetchPipelines();
        startPolling();
      } else {
        stopPolling();
      }
    };
    
    if (document.visibilityState === "visible") {
      startPolling();
    }
    
    document.addEventListener("visibilitychange", handleVisibilityChange);
    
    return () => {
      stopPolling();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [fetchPipelines]);

  if (loading) {
    return (
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-16 bg-slate-700 rounded"></div>
          <div className="h-16 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="bg-slate-800 rounded-xl border border-red-500/30 p-6">
        <div className="flex items-center gap-2 text-red-400">
          <span>⚠️</span>
          <span>Failed to load outcomes: {error}</span>
        </div>
      </div>
    );
  }

  const completedPipelines = data?.pipelines.filter(p => p.status === "completed") || [];
  const activePipelines = data?.pipelines.filter(p => p.status === "running" || p.status === "pending") || [];

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📦</span>
          <div>
            <h3 className="font-semibold text-white">Pipeline Outcomes</h3>
            <p className="text-xs text-slate-500">
              Completed work and artifacts
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {activePipelines.length > 0 && (
            <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full border border-yellow-500/30">
              {activePipelines.length} in progress
            </span>
          )}
          <span className="text-xs text-slate-500">
            {completedPipelines.length} completed
          </span>
        </div>
      </div>

      {/* Active Pipelines */}
      {activePipelines.length > 0 && (
        <div className="p-4 border-b border-slate-700 bg-yellow-500/5">
          <h4 className="text-xs text-yellow-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></span>
            In Progress
          </h4>
          <div className="space-y-2">
            {activePipelines.map((pipeline) => (
              <div
                key={pipeline.id}
                className="flex items-center gap-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20"
              >
                <span className="text-xl">⚡</span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-white truncate">{pipeline.topic}</div>
                  <div className="text-xs text-slate-400">
                    Phase: {pipeline.currentPhase} • {pipeline.progress}%
                  </div>
                </div>
                <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-yellow-400 transition-all duration-500"
                    style={{ width: `${pipeline.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Pipelines with Blog Posts */}
      {completedPipelines.length > 0 ? (
        <div className="p-4">
          <h4 className="text-xs text-slate-500 uppercase tracking-wider mb-3">
            Completed Outcomes
          </h4>
          <div className="space-y-3">
            {completedPipelines.map((pipeline) => (
              <div
                key={pipeline.id}
                className="p-4 rounded-lg bg-slate-700/30 border border-slate-600/50 hover:border-accent-500/30 transition"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h5 className="font-medium text-white">{pipeline.topic}</h5>
                    <p className="text-xs text-slate-500">
                      Completed {formatTimeAgo(pipeline.updatedAt)}
                    </p>
                  </div>
                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                    ✓ Complete
                  </span>
                </div>

                {/* Results */}
                {pipeline.results && (
                  <div className="mt-3 space-y-2">
                    {/* Blog Post */}
                    {pipeline.results.blog && (
                      <a
                        href={pipeline.results.blog.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-2 rounded bg-accent-500/10 border border-accent-500/20 hover:bg-accent-500/20 transition group"
                      >
                        <span className="text-lg">📝</span>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm text-accent-300 truncate group-hover:text-accent-200">
                            {pipeline.results.blog.title}
                          </div>
                          <div className="text-xs text-slate-500">
                            {pipeline.results.blog.wordCount} words • GCP Storage
                          </div>
                        </div>
                        <span className="text-slate-400 opacity-0 group-hover:opacity-100 transition">↗</span>
                      </a>
                    )}

                    {/* Research Summary */}
                    {pipeline.results.research && (
                      <div className="flex items-center gap-2 text-xs text-slate-400">
                        <span>🔬</span>
                        <span>Research: {pipeline.results.research.domain}</span>
                        {pipeline.results.research.keywords.length > 0 && (
                          <span className="text-slate-500">
                            • Keywords: {pipeline.results.research.keywords.slice(0, 3).join(", ")}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Trends */}
                    {pipeline.results.trends && (
                      <div className="flex items-center gap-2 text-xs text-slate-400">
                        <span>📈</span>
                        <span>Trending: {pipeline.results.trends.trendingKeywords.slice(0, 3).join(", ")}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="p-6 text-center text-slate-500">
          <span className="text-2xl">📭</span>
          <p className="mt-2 text-sm">No completed pipelines yet</p>
          <p className="text-xs">Create a pipeline via the chat to see outcomes here</p>
        </div>
      )}
    </div>
  );
}
