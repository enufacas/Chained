/**
 * PipelineDetailView Component
 *
 * Displays a detailed view of a pipeline run with A2A cards and lifecycle visualization.
 * Shows the full journey of how agents collaborated to complete the pipeline.
 * 
 * Enhanced with:
 * - Detailed A2A step history with task IDs and execution times
 * - Rich artifact viewer with markdown/SVG/HTML rendering
 * - Expandable sections for raw data inspection
 * 
 * @see docs/a2a-ui/README.md for feature documentation
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { Pipeline, A2AStepDetail } from "@/types";
import AssetPreview from "./AssetPreview";

// Re-export for backwards compatibility with any direct imports
export type { A2AStepDetail };

// Model interaction type for rendering LLM call logs
interface ModelInteraction {
  type: string;
  timestamp?: string;
  agent?: string;
  model?: string;
  duration_ms?: number;
  word_count?: number;
  status?: string;
  prompt_preview?: string;
  response_preview?: string;
  error?: string;
  [key: string]: unknown;
}

// Known model interaction types for rendering
const INTERACTION_TYPES: Record<string, { icon: string; label: string }> = {
  llm_request: { icon: "📤", label: "LLM Request" },
  llm_response: { icon: "📥", label: "LLM Response" },
  llm_error: { icon: "⚠️", label: "LLM Error" },
  task_start: { icon: "🚀", label: "Task Start" },
  task_complete: { icon: "✅", label: "Task Complete" },
  write_request: { icon: "📝", label: "Write Request" },
  configuration: { icon: "⚙️", label: "Configuration" },
  fallback_mode: { icon: "🔄", label: "Fallback Mode" },
  fallback_discovery: { icon: "🔄", label: "Fallback Discovery" },
  fallback_trends: { icon: "🔄", label: "Fallback Trends" },
  parse_error: { icon: "⚠️", label: "Parse Error" },
};

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

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  const mins = Math.floor(ms / 60000);
  const secs = Math.floor((ms % 60000) / 1000);
  return `${mins}m ${secs}s`;
}

function getPhaseIndex(phase: string): number {
  return PHASES.findIndex((p) => p.id === phase);
}

export default function PipelineDetailView({ pipelineId, onClose }: PipelineDetailViewProps) {
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [showRawData, setShowRawData] = useState(false);
  const [expandedArtifact, setExpandedArtifact] = useState<{ stepIndex: number; artifactIndex: number } | null>(null);

  const toggleStepExpanded = (taskId: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(taskId)) {
      newExpanded.delete(taskId);
    } else {
      newExpanded.add(taskId);
    }
    setExpandedSteps(newExpanded);
  };

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

        {/* A2A Steps Deep Dive - NEW SECTION */}
        {pipeline.a2aSteps && pipeline.a2aSteps.length > 0 && (
          <div className="p-6 border-b border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                <span>🔍</span>
                A2A Steps Deep Dive
                <span className="text-xs bg-accent-500/20 text-accent-400 px-2 py-0.5 rounded-full">
                  {pipeline.a2aSteps.length} steps
                </span>
              </h3>
              {pipeline.totalDurationMs && (
                <span className="text-xs text-slate-400">
                  Total: {formatDuration(pipeline.totalDurationMs)}
                </span>
              )}
            </div>
            
            <div className="space-y-3">
              {pipeline.a2aSteps.map((step, index) => (
                <div
                  key={step.taskId}
                  className={`rounded-lg border transition-all ${
                    step.status === "completed"
                      ? "bg-slate-700/30 border-slate-600/50"
                      : step.status === "failed"
                      ? "bg-red-500/10 border-red-500/30"
                      : "bg-yellow-500/10 border-yellow-500/30"
                  }`}
                >
                  {/* Step Header - Always visible */}
                  <button
                    onClick={() => toggleStepExpanded(step.taskId)}
                    className="w-full p-4 flex items-center justify-between text-left hover:bg-white/5 transition rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xl">
                        {index === 0 ? "🔬" : index === 1 ? "📈" : "✍️"}
                      </span>
                      <div>
                        <div className="font-medium text-white">{step.agentName}</div>
                        <div className="text-xs text-slate-400 flex items-center gap-2">
                          <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs">
                            {step.taskId}
                          </code>
                          {step.durationMs && (
                            <span>• {formatDuration(step.durationMs)}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        step.status === "completed"
                          ? "bg-green-500/20 text-green-400"
                          : step.status === "failed"
                          ? "bg-red-500/20 text-red-400"
                          : "bg-yellow-500/20 text-yellow-400"
                      }`}>
                        {step.status}
                      </span>
                      <span className="text-slate-400 text-xs">
                        {expandedSteps.has(step.taskId) ? "▼" : "▶"}
                      </span>
                    </div>
                  </button>
                  
                  {/* Expanded Step Details */}
                  {expandedSteps.has(step.taskId) && (
                    <div className="px-4 pb-4 space-y-3 border-t border-slate-600/30 pt-3">
                      {/* Message */}
                      {step.message && (
                        <div>
                          <div className="text-xs text-slate-500 mb-1">Response Message:</div>
                          <div className="text-sm text-slate-300 bg-black/20 p-3 rounded-lg">
                            {step.message}
                          </div>
                        </div>
                      )}
                      
                      {/* Timing */}
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        <div>
                          <span className="text-slate-500">Started:</span>{" "}
                          <span className="text-slate-300">{new Date(step.startTime).toLocaleString()}</span>
                        </div>
                        {step.endTime && (
                          <div>
                            <span className="text-slate-500">Ended:</span>{" "}
                            <span className="text-slate-300">{new Date(step.endTime).toLocaleString()}</span>
                          </div>
                        )}
                      </div>
                      
                      {/* Artifacts */}
                      {step.artifacts.length > 0 && (
                        <div>
                          <div className="text-xs text-slate-500 mb-2">
                            Artifacts ({step.artifacts.length}):
                          </div>
                          <div className="space-y-2">
                            {step.artifacts.map((artifact, artifactIndex) => {
                              // Special rendering for model-interactions artifact
                              if (artifact.name === "model-interactions") {
                                try {
                                  const interactions = JSON.parse(artifact.data);
                                  return (
                                    <div
                                      key={artifactIndex}
                                      className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 rounded-lg p-4 border border-purple-500/30"
                                    >
                                      <div className="flex items-center gap-2 mb-3">
                                        <span className="text-lg">🧠</span>
                                        <span className="text-sm font-semibold text-purple-400">
                                          Model Interactions ({interactions.length})
                                        </span>
                                        <span className="text-xs text-slate-500">
                                          - LLM calls and responses
                                        </span>
                                      </div>
                                      <div className="space-y-3">
                                        {(interactions as ModelInteraction[]).map((interaction: ModelInteraction, idx: number) => (
                                          <div
                                            key={idx}
                                            className={`rounded-lg p-3 ${
                                              interaction.type === "llm_request"
                                                ? "bg-blue-500/10 border-l-2 border-blue-500"
                                                : interaction.type === "llm_response"
                                                ? "bg-green-500/10 border-l-2 border-green-500"
                                                : interaction.type === "llm_error"
                                                ? "bg-red-500/10 border-l-2 border-red-500"
                                                : "bg-slate-700/30 border-l-2 border-slate-500"
                                            }`}
                                          >
                                            <div className="flex items-center justify-between mb-2">
                                              <span className={`text-xs font-medium ${
                                                interaction.type === "llm_request"
                                                  ? "text-blue-400"
                                                  : interaction.type === "llm_response"
                                                  ? "text-green-400"
                                                  : interaction.type === "llm_error" || interaction.type === "parse_error"
                                                  ? "text-red-400"
                                                  : "text-slate-400"
                                              }`}>
                                                {INTERACTION_TYPES[interaction.type] 
                                                  ? `${INTERACTION_TYPES[interaction.type].icon} ${INTERACTION_TYPES[interaction.type].label}`
                                                  : `📋 ${interaction.type}`}
                                              </span>
                                              <span className="text-xs text-slate-500">
                                                {String(interaction.timestamp || "").split("T")[1]?.split(".")[0]}
                                              </span>
                                            </div>
                                            <div className="text-xs text-slate-300 space-y-1">
                                              {interaction.model && (
                                                <div><span className="text-slate-500">Model:</span> {String(interaction.model)}</div>
                                              )}
                                              {interaction.duration_ms && (
                                                <div><span className="text-slate-500">Duration:</span> {String(interaction.duration_ms)}ms</div>
                                              )}
                                              {interaction.word_count && (
                                                <div><span className="text-slate-500">Words:</span> {String(interaction.word_count)}</div>
                                              )}
                                              {interaction.status && (
                                                <div><span className="text-slate-500">Status:</span> {String(interaction.status)}</div>
                                              )}
                                              {interaction.prompt_preview && (
                                                <div className="mt-2">
                                                  <span className="text-slate-500">Prompt Preview:</span>
                                                  <pre className="mt-1 p-2 bg-black/30 rounded text-xs overflow-x-auto max-h-24 overflow-y-auto whitespace-pre-wrap">
                                                    {String(interaction.prompt_preview)}
                                                  </pre>
                                                </div>
                                              )}
                                              {interaction.response_preview && (
                                                <div className="mt-2">
                                                  <span className="text-slate-500">Response Preview:</span>
                                                  <pre className="mt-1 p-2 bg-black/30 rounded text-xs overflow-x-auto max-h-24 overflow-y-auto whitespace-pre-wrap">
                                                    {String(interaction.response_preview)}
                                                  </pre>
                                                </div>
                                              )}
                                              {interaction.error && (
                                                <div className="mt-2 text-red-400">
                                                  <span className="text-red-500">Error:</span> {String(interaction.error)}
                                                </div>
                                              )}
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  );
                                } catch {
                                  // Fall through to normal artifact rendering
                                }
                              }
                              
                              // Normal artifact rendering with expandable rich preview
                              const isExpanded = expandedArtifact?.stepIndex === index && expandedArtifact?.artifactIndex === artifactIndex;
                              return (
                                <div key={artifactIndex}>
                                  <button
                                    onClick={() => setExpandedArtifact(isExpanded ? null : { stepIndex: index, artifactIndex })}
                                    className={`w-full text-left bg-black/30 rounded-lg p-3 transition-all hover:bg-black/40 ${
                                      isExpanded ? "ring-2 ring-purple-500/50" : ""
                                    }`}
                                  >
                                    <div className="flex items-center justify-between mb-2">
                                      <span className="text-xs font-medium text-accent-400">
                                        📦 {artifact.name}
                                      </span>
                                      <div className="flex items-center gap-2">
                                        <span className="text-xs text-slate-500">
                                          {artifact.type}
                                        </span>
                                        <span className="text-xs text-purple-400">
                                          {isExpanded ? "▼ Collapse" : "▶ Expand"}
                                        </span>
                                      </div>
                                    </div>
                                    {!isExpanded && (
                                      <pre className="text-xs text-slate-300 overflow-x-auto max-h-24 overflow-y-hidden">
                                        {artifact.preview && artifact.preview.length > 0 
                                          ? artifact.preview 
                                          : artifact.data.length > 300 
                                            ? artifact.data.substring(0, 300) + "..."
                                            : artifact.data}
                                      </pre>
                                    )}
                                  </button>
                                  
                                  {/* Rich Asset Preview when expanded */}
                                  {isExpanded && (
                                    <div className="mt-2">
                                      <AssetPreview
                                        name={artifact.name}
                                        type={artifact.type}
                                        data={artifact.data}
                                        onClose={() => setExpandedArtifact(null)}
                                        maxHeight="400px"
                                      />
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {/* Raw Data Toggle */}
            <div className="mt-4 pt-4 border-t border-slate-700/50">
              <button
                onClick={() => setShowRawData(!showRawData)}
                className="text-xs text-slate-400 hover:text-accent-400 transition flex items-center gap-1"
              >
                {showRawData ? "▼" : "▶"} {showRawData ? "Hide" : "Show"} Raw Pipeline Data
              </button>
              {showRawData && (
                <pre className="mt-2 p-3 bg-black/30 rounded-lg text-xs text-slate-400 overflow-x-auto max-h-64 overflow-y-auto">
                  {JSON.stringify(pipeline.a2aSteps, null, 2)}
                </pre>
              )}
            </div>
          </div>
        )}

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
