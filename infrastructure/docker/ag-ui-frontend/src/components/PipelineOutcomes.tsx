/**
 * PipelineOutcomes Component
 *
 * Displays completed pipeline outcomes from the A2A system.
 * Shows blog posts, artifacts, and other results from agent work.
 * Sources data from the /api/pipeline endpoint.
 * 
 * Enhanced with:
 * - 5-second polling for real-time updates
 * - Creative state representations with animations
 * - Click-to-expand detailed pipeline view
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import PipelineDetailView from "./PipelineDetailView";
import { getArtifactsBySourceId, getStoredSessions, getArtifactById, type StoredSession } from "@/lib/storage";
import { logApiError } from "@/lib/error-logging";


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
  a2aSteps?: Array<{
    taskId: string;
    agentName: string;
    phase: string;
    status: string;
    startTime: string;
    endTime?: string;
    durationMs?: number;
    message?: string;
    artifacts: Array<{ name: string; type: string; preview?: string }>;
  }>;
  totalDurationMs?: number;
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

// Phase icons for visual representation
const PHASE_ICONS: { [key: string]: { icon: string; color: string } } = {
  research: { icon: "🔬", color: "blue" },
  trends: { icon: "📈", color: "green" },
  writing: { icon: "✍️", color: "purple" },
  publishing: { icon: "🚀", color: "orange" },
  complete: { icon: "🎉", color: "emerald" },
};

/**
 * Convert a StoredSession from localStorage to PipelineResult format
 * Reconstructs full pipeline data from stored session and artifacts
 */
function sessionToPipelineResult(session: StoredSession): PipelineResult {
  // Extract blog URL from metadata or artifacts
  let blogUrl: string | undefined;
  
  if (session.metadata?.blogUrl) {
    blogUrl = session.metadata.blogUrl as string;
  } else if (session.artifacts && session.artifacts.length > 0) {
    // Try to find blog artifact
    for (const artifactId of session.artifacts) {
      const artifact = getArtifactById(artifactId);
      if (artifact?.name?.toLowerCase().includes("blog") && artifact?.data) {
        try {
          const parsed = JSON.parse(artifact.data);
          if (parsed.url) {
            blogUrl = parsed.url;
            break;
          }
        } catch {
          // Ignore parse errors
        }
      }
    }
  }
  
  // Reconstruct a2aSteps from metadata if available
  let a2aSteps: Array<{
    taskId: string;
    agentName: string;
    phase: string;
    status: string;
    startTime: string;
    endTime?: string;
    durationMs?: number;
    message?: string;
    artifacts: Array<{ name: string; type: string; preview?: string }>;
  }> | undefined;
  
  if (session.metadata?.a2aSteps && Array.isArray(session.metadata.a2aSteps)) {
    a2aSteps = session.metadata.a2aSteps as typeof a2aSteps;
  }
  
  return {
    id: session.id,
    topic: session.topic,
    status: session.status as PipelineResult["status"],
    createdAt: session.createdAt,
    updatedAt: session.completedAt || session.createdAt,
    progress: session.status === "completed" ? 100 : 
              session.status === "failed" ? 0 : 50,
    currentPhase: session.status === "completed" ? "complete" : "writing",
    results: blogUrl ? {
      blog: {
        title: session.topic,
        url: blogUrl,
        wordCount: 0, // Not stored in session
      },
    } : undefined,
    // Include a2aSteps if available from metadata
    a2aSteps,
    totalDurationMs: session.metadata?.totalDurationMs as number | undefined,
  };
}

export default function PipelineOutcomes() {
  const [data, setData] = useState<PipelineListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPipelineId, setSelectedPipelineId] = useState<string | null>(null);

  const fetchPipelines = useCallback(async () => {
    try {
      // First, get sessions from localStorage
      const storedSessions = getStoredSessions();
      const storedWorkflows = storedSessions.filter(s => s.type === "workflow");
      
      // Convert stored sessions to pipeline results
      const localPipelines = storedWorkflows
        .map(sessionToPipelineResult)
        .slice(0, 20); // Limit to most recent 20
      
      console.log(`[PipelineOutcomes] Loaded ${localPipelines.length} pipelines from localStorage`);
      
      // Try to fetch from API for active pipelines
      let apiPipelines: PipelineResult[] = [];
      try {
        const response = await fetch("/api/pipeline?limit=10");
        if (response.ok) {
          const result = await response.json();
          apiPipelines = result.pipelines || [];
          console.log(`[PipelineOutcomes] Loaded ${apiPipelines.length} pipelines from API`);
        }
      } catch (apiError) {
        console.warn("[PipelineOutcomes] API fetch failed, using localStorage only:", apiError);
      }
      
      // Merge: API pipelines (active) + localStorage pipelines (completed/historical)
      // Remove duplicates by ID, preferring API version for active pipelines
      const apiIds = new Set(apiPipelines.map(p => p.id));
      const uniqueLocalPipelines = localPipelines.filter(p => !apiIds.has(p.id));
      
      const allPipelines = [...apiPipelines, ...uniqueLocalPipelines]
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
        .slice(0, 10); // Show top 10
      
      const activePipelinesCount = allPipelines.filter(
        p => p.status === "pending" || p.status === "running"
      ).length;
      
      setData({
        pipelines: allPipelines,
        total: allPipelines.length,
        activePipelinesCount,
      });
      setError(null);
      
      console.log(`[PipelineOutcomes] Total pipelines: ${allPipelines.length} (${activePipelinesCount} active)`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to load pipelines";
      console.error("[PipelineOutcomes] Fetch error:", err);
      
      // Log error to backend for persistent logging
      logApiError(err, "/api/pipeline", "GET", {
        component: "PipelineOutcomes",
        action: "fetchPipelines",
      });
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPipelines();
    
    // Refresh every 5 seconds for more real-time updates
    let interval: NodeJS.Timeout | null = null;
    
    const startPolling = () => {
      if (!interval) {
        interval = setInterval(fetchPipelines, 5000);
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
    <>
      {/* Pipeline Detail Modal */}
      {selectedPipelineId && (
        <PipelineDetailView
          pipelineId={selectedPipelineId}
          onClose={() => setSelectedPipelineId(null)}
        />
      )}

      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📦</span>
            <div>
              <h3 className="font-semibold text-white">Pipeline Outcomes</h3>
              <p className="text-xs text-slate-500">
                Completed work and artifacts • Click to view details
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {activePipelines.length > 0 && (
              <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full border border-yellow-500/30 animate-pulse">
                {activePipelines.length} in progress
              </span>
            )}
            <span className="text-xs text-slate-500">
              {completedPipelines.length} completed
            </span>
          </div>
        </div>

        {/* Active Pipelines with Enhanced Visual */}
        {activePipelines.length > 0 && (
          <div className="p-4 border-b border-slate-700 bg-gradient-to-r from-yellow-500/5 to-orange-500/5">
            <h4 className="text-xs text-yellow-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <span className="relative">
                <span className="w-2 h-2 bg-yellow-400 rounded-full animate-ping absolute"></span>
                <span className="w-2 h-2 bg-yellow-400 rounded-full relative"></span>
              </span>
              In Progress
            </h4>
            <div className="space-y-3">
              {activePipelines.map((pipeline) => {
                const phaseInfo = PHASE_ICONS[pipeline.currentPhase] || { icon: "⏳", color: "slate" };
                return (
                  <div
                    key={pipeline.id}
                    onClick={() => setSelectedPipelineId(pipeline.id)}
                    className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/20 hover:border-yellow-500/40 cursor-pointer transition-all hover:scale-[1.01] hover:shadow-lg hover:shadow-yellow-500/10"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-2xl animate-bounce">{phaseInfo.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-white truncate">{pipeline.topic}</div>
                        <div className="text-xs text-slate-400 flex items-center gap-2">
                          <span className="flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full animate-pulse"></span>
                            {pipeline.currentPhase.charAt(0).toUpperCase() + pipeline.currentPhase.slice(1)}
                          </span>
                          <span>•</span>
                          <span>{pipeline.progress}%</span>
                        </div>
                      </div>
                      <span className="text-xs text-slate-500">Click for details →</span>
                    </div>
                    
                    {/* Creative progress visualization */}
                    <div className="relative">
                      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-yellow-400 via-orange-400 to-yellow-400 transition-all duration-500 bg-[length:200%_100%] animate-[gradient_2s_ease_infinite]"
                          style={{ width: `${pipeline.progress}%` }}
                        />
                      </div>
                      {/* Phase markers */}
                      <div className="flex justify-between mt-1">
                        {["research", "trends", "writing", "publishing", "complete"].map((phase, idx) => {
                          const phases = ["research", "trends", "writing", "publishing", "complete"];
                          const currentIdx = phases.indexOf(pipeline.currentPhase);
                          const isDone = idx < currentIdx;
                          const isCurrent = idx === currentIdx;
                          return (
                            <div key={phase} className="flex flex-col items-center">
                              <span className={`text-xs ${isDone ? "text-green-400" : isCurrent ? "text-yellow-400" : "text-slate-600"}`}>
                                {isDone ? "✓" : PHASE_ICONS[phase]?.icon || "○"}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                );
              })}
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
            {completedPipelines.map((pipeline) => {
              // Get artifact count from localStorage
              const artifacts = getArtifactsBySourceId(pipeline.id);
              const artifactCount = artifacts.length;
              
              return (
              <div
                key={pipeline.id}
                className="p-4 rounded-lg bg-slate-700/30 border border-slate-600/50 hover:border-green-500/30 transition-all hover:shadow-lg hover:shadow-green-500/5"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h5 className="font-medium text-white flex items-center gap-2">
                      {pipeline.topic}
                    </h5>
                    <p className="text-xs text-slate-500">
                      Completed {formatTimeAgo(pipeline.updatedAt)}
                      {artifactCount > 0 && (
                        <span className="ml-2 px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 border border-purple-500/30">
                          📦 {artifactCount} artifact{artifactCount !== 1 ? 's' : ''}
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full border border-green-500/30">
                      ✓ Complete
                    </span>
                    {/* Prominent View Details Button */}
                    <button
                      onClick={() => setSelectedPipelineId(pipeline.id)}
                      className="text-xs bg-accent-500/20 text-accent-400 px-3 py-1.5 rounded-lg border border-accent-500/30 hover:bg-accent-500/30 hover:border-accent-500/50 transition flex items-center gap-1"
                    >
                      🔍 View Details
                    </button>
                  </div>
                </div>

                {/* Results */}
                {pipeline.results && (
                  <div className="mt-3 space-y-2">
                    {/* Artifacts Link */}
                    {artifactCount > 0 && (
                      <a
                        href="/history"
                        className="flex items-center gap-3 p-2 rounded bg-purple-500/10 border border-purple-500/20 hover:bg-purple-500/20 transition group"
                      >
                        <span className="text-lg">📦</span>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm text-purple-300 truncate group-hover:text-purple-200">
                            View Artifacts &amp; Session Details
                          </div>
                          <div className="text-xs text-slate-500">
                            {artifactCount} artifact{artifactCount !== 1 ? 's' : ''} saved • includes ultimate summary
                          </div>
                        </div>
                        <span className="text-slate-400 opacity-0 group-hover:opacity-100 transition">→</span>
                      </a>
                    )}
                    
                    {/* Blog Post - External link opens in new tab */}
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
              );
            })}
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
    </>
  );
}
