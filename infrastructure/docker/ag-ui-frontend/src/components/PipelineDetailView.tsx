/**
 * PipelineDetailView Component
 *
 * Displays a detailed view of a pipeline run with A2A cards and lifecycle visualization.
 * Shows the full journey of how agents collaborated to complete the pipeline.
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

interface PipelineDetailViewProps {
  pipelineId: string;
  onClose: () => void;
}

// A2A Agent Cards data
const A2A_AGENTS = [
  {
    id: "academic-research",
    name: "Academic Research Agent",
    icon: "🔬",
    phase: "research",
    color: "blue",
    description: "Discovers and analyzes research topics",
    capabilities: ["Topic Discovery", "Domain Analysis", "Keyword Extraction"],
  },
  {
    id: "google-trends",
    name: "Google Trends Agent",
    icon: "📈",
    phase: "trends",
    color: "green",
    description: "Analyzes trends for SEO optimization",
    capabilities: ["Trend Analysis", "Keyword Ranking", "SEO Recommendations"],
  },
  {
    id: "blog-writer",
    name: "Blog Writer Agent",
    icon: "✍️",
    phase: "writing",
    color: "purple",
    description: "Writes and publishes blog posts",
    capabilities: ["Content Generation", "SEO Optimization", "Publishing"],
  },
];

const PHASES = [
  { id: "research", label: "Research", icon: "🔬", color: "blue" },
  { id: "trends", label: "SEO Analysis", icon: "📈", color: "green" },
  { id: "writing", label: "Writing", icon: "✍️", color: "purple" },
  { id: "publishing", label: "Publishing", icon: "🚀", color: "orange" },
  { id: "complete", label: "Complete", icon: "🎉", color: "emerald" },
];

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

function getPhaseIndex(phase: string): number {
  return PHASES.findIndex((p) => p.id === phase);
}

export default function PipelineDetailView({ pipelineId, onClose }: PipelineDetailViewProps) {
  const [pipeline, setPipeline] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPipeline = useCallback(async () => {
    try {
      const response = await fetch(`/api/pipeline?id=${pipelineId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const result = await response.json();
      setPipeline(result);
      setError(null);
    } catch (err) {
      console.error("[PipelineDetailView] Fetch error:", err);
      setError(err instanceof Error ? err.message : "Failed to load pipeline");
    } finally {
      setLoading(false);
    }
  }, [pipelineId]);

  useEffect(() => {
    fetchPipeline();

    // Poll every 5 seconds for active pipelines (consistent with other components)
    // Only poll when pipeline is in active state to reduce server load
    const interval = setInterval(() => {
      fetchPipeline();
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchPipeline]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-slate-800 rounded-2xl border border-slate-700 p-8 max-w-4xl w-full animate-pulse">
          <div className="h-8 bg-slate-700 rounded w-1/3 mb-6"></div>
          <div className="h-48 bg-slate-700 rounded mb-6"></div>
          <div className="h-32 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !pipeline) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-slate-800 rounded-2xl border border-red-500/30 p-8 max-w-lg w-full">
          <div className="text-red-400 mb-4">⚠️ {error || "Pipeline not found"}</div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  const currentPhaseIndex = getPhaseIndex(pipeline.currentPhase);
  const isComplete = pipeline.status === "completed";
  const isRunning = pipeline.status === "running";

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 max-w-4xl w-full my-8">
        {/* Header */}
        <div className="p-6 border-b border-slate-700 flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">{pipeline.topic}</h2>
            <div className="flex items-center gap-3 text-sm text-slate-400">
              <span>ID: {pipeline.id}</span>
              <span>•</span>
              <span>Created {formatTimeAgo(pipeline.createdAt)}</span>
              <span>•</span>
              <span className={`px-2 py-0.5 rounded-full text-xs ${
                isComplete
                  ? "bg-green-500/20 text-green-400"
                  : isRunning
                  ? "bg-yellow-500/20 text-yellow-400"
                  : "bg-slate-500/20 text-slate-400"
              }`}>
                {pipeline.status.charAt(0).toUpperCase() + pipeline.status.slice(1)}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded-lg transition text-slate-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        {/* Pipeline Lifecycle Visualization */}
        <div className="p-6 border-b border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <span>🔄</span>
            Pipeline Lifecycle
            {isRunning && (
              <span className="ml-2 flex items-center gap-1 text-xs text-yellow-400">
                <span className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></span>
                Live
              </span>
            )}
          </h3>

          {/* Progress bar */}
          <div className="mb-6">
            <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
              <span>Progress</span>
              <span>{pipeline.progress}%</span>
            </div>
            <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  isComplete
                    ? "bg-gradient-to-r from-green-500 to-emerald-400"
                    : "bg-gradient-to-r from-yellow-500 to-orange-400"
                }`}
                style={{ width: `${pipeline.progress}%` }}
              />
            </div>
          </div>

          {/* Phase indicators */}
          <div className="flex items-center justify-between relative">
            {/* Connection line */}
            <div className="absolute left-0 right-0 top-6 h-0.5 bg-slate-700" />
            <div
              className={`absolute left-0 top-6 h-0.5 transition-all duration-500 ${
                isComplete
                  ? "bg-gradient-to-r from-green-500 to-emerald-400"
                  : "bg-gradient-to-r from-yellow-500 to-orange-400"
              }`}
              style={{ width: `${pipeline.progress}%` }}
            />

            {PHASES.map((phase, index) => {
              const isActive = index === currentPhaseIndex && !isComplete;
              const isDone = index < currentPhaseIndex || isComplete;

              return (
                <div key={phase.id} className="relative z-10 flex flex-col items-center">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-xl transition-all duration-500 ${
                      isDone
                        ? "bg-green-500/20 border-2 border-green-500 text-green-400"
                        : isActive
                        ? "bg-yellow-500/20 border-2 border-yellow-500 text-yellow-400 animate-pulse scale-110"
                        : "bg-slate-700 border-2 border-slate-600 text-slate-500"
                    }`}
                  >
                    {isDone ? "✓" : phase.icon}
                  </div>
                  <span
                    className={`mt-2 text-xs ${
                      isDone
                        ? "text-green-400"
                        : isActive
                        ? "text-yellow-400 font-semibold"
                        : "text-slate-500"
                    }`}
                  >
                    {phase.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* A2A Agent Cards */}
        <div className="p-6 border-b border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span>🤖</span>
            A2A Agent Cards
          </h3>
          <div className="grid md:grid-cols-3 gap-4">
            {A2A_AGENTS.map((agent) => {
              const phaseIndex = getPhaseIndex(agent.phase);
              const isAgentActive = phaseIndex === currentPhaseIndex && !isComplete;
              const isAgentDone = phaseIndex < currentPhaseIndex || isComplete;

              return (
                <div
                  key={agent.id}
                  className={`p-4 rounded-xl border transition-all duration-500 ${
                    isAgentActive
                      ? "bg-yellow-500/10 border-yellow-500/50 ring-2 ring-yellow-500/20 transform scale-105"
                      : isAgentDone
                      ? "bg-green-500/10 border-green-500/30"
                      : "bg-slate-700/30 border-slate-600/50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">{agent.icon}</span>
                    <div className="flex-1">
                      <h4 className="font-semibold text-white">{agent.name}</h4>
                      <p className="text-xs text-slate-400 mt-1">{agent.description}</p>
                      <div className="mt-3 flex flex-wrap gap-1">
                        {agent.capabilities.map((cap) => (
                          <span
                            key={cap}
                            className="text-xs px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-300"
                          >
                            {cap}
                          </span>
                        ))}
                      </div>
                      <div className="mt-3">
                        {isAgentDone ? (
                          <span className="text-xs text-green-400 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-green-400 rounded-full"></span>
                            Completed
                          </span>
                        ) : isAgentActive ? (
                          <span className="text-xs text-yellow-400 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full animate-pulse"></span>
                            Working...
                          </span>
                        ) : (
                          <span className="text-xs text-slate-500 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-slate-500 rounded-full"></span>
                            Waiting
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Results Section */}
        {pipeline.results && (
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span>📊</span>
              Pipeline Results
            </h3>
            <div className="space-y-4">
              {/* Research Results */}
              {pipeline.results.research && (
                <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
                  <h4 className="font-semibold text-blue-400 mb-2 flex items-center gap-2">
                    🔬 Research Findings
                  </h4>
                  <div className="text-sm text-slate-300 space-y-1">
                    <p><span className="text-slate-500">Topic:</span> {pipeline.results.research.topic}</p>
                    <p><span className="text-slate-500">Domain:</span> {pipeline.results.research.domain}</p>
                    {pipeline.results.research.keywords?.length > 0 && (
                      <p><span className="text-slate-500">Keywords:</span> {pipeline.results.research.keywords.join(", ")}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Trends Results */}
              {pipeline.results.trends && (
                <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                  <h4 className="font-semibold text-green-400 mb-2 flex items-center gap-2">
                    📈 SEO & Trends Analysis
                  </h4>
                  <div className="text-sm text-slate-300 space-y-1">
                    <p><span className="text-slate-500">Trending:</span> {pipeline.results.trends.trendingKeywords?.join(", ")}</p>
                    <p><span className="text-slate-500">Recommended Focus:</span> {pipeline.results.trends.recommendedFocus}</p>
                  </div>
                </div>
              )}

              {/* Blog Results */}
              {pipeline.results.blog && (
                <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
                  <h4 className="font-semibold text-purple-400 mb-2 flex items-center gap-2">
                    ✍️ Blog Output
                  </h4>
                  <div className="text-sm text-slate-300 space-y-2">
                    <p><span className="text-slate-500">Title:</span> {pipeline.results.blog.title}</p>
                    <p><span className="text-slate-500">Word Count:</span> {pipeline.results.blog.wordCount} words</p>
                    <a
                      href={pipeline.results.blog.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 transition mt-2"
                    >
                      📄 View Blog Post ↗
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-6 bg-slate-900/50 border-t border-slate-700 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            Last updated: {formatTimeAgo(pipeline.updatedAt)}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition text-white"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
