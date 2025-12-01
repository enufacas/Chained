/**
 * TeamVisualization Component
 *
 * Real-time visualization of team execution showing:
 * - Agent status and activity
 * - Message flow between agents
 * - Artifact creation timeline with rich preview
 * - Turn progression
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import AssetPreview from "./AssetPreview";

interface TurnResult {
  stepIndex: number;
  agentId: string;
  agentName: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
  taskId?: string;
  message?: string;
  artifacts: Array<{ name: string; type: string; data: string }>;
  error?: string;
}

interface TeamSession {
  id: string;
  recipeId: string;
  recipeName: string;
  goal: string;
  status: "pending" | "running" | "completed" | "failed";
  currentTurn: number;
  totalTurns: number;
  createdAt: string;
  updatedAt: string;
  turnResults: TurnResult[];
}

interface TeamVisualizationProps {
  sessionId?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const AGENT_ICONS: Record<string, string> = {
  "academic-research": "🔬",
  "google-trends": "📈",
  "blog-writer": "✍️",
  "code-reviewer": "🔍",
  "data-analyst": "📊",
  "image-generator": "🎨",
};

const STATUS_CONFIG = {
  pending: { color: "bg-slate-500", ring: "ring-slate-400", icon: "⏳" },
  running: { color: "bg-blue-500 animate-pulse", ring: "ring-blue-400", icon: "🔄" },
  completed: { color: "bg-green-500", ring: "ring-green-400", icon: "✅" },
  failed: { color: "bg-red-500", ring: "ring-red-400", icon: "❌" },
  skipped: { color: "bg-yellow-500", ring: "ring-yellow-400", icon: "⏭️" },
};

export default function TeamVisualization({
  sessionId,
  autoRefresh = true,
  refreshInterval = 2000,
}: TeamVisualizationProps) {
  const [session, setSession] = useState<TeamSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedArtifact, setSelectedArtifact] = useState<{
    turnIndex: number;
    artifactIndex: number;
  } | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Fetch session data
  const fetchSession = useCallback(async () => {
    if (!sessionId) {
      setLoading(false);
      return;
    }
    
    try {
      const response = await fetch(`/api/team?session=${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setSession(data);
        setError(null);
      } else if (response.status === 404) {
        setError("Session not found");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load session");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);
  
  // Initial fetch
  useEffect(() => {
    fetchSession();
  }, [fetchSession]);
  
  // Auto-refresh while running
  useEffect(() => {
    if (!autoRefresh || !session || session.status !== "running") return;
    
    const interval = setInterval(fetchSession, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, session, fetchSession]);
  
  // Auto-scroll to current turn
  useEffect(() => {
    if (containerRef.current && session?.turnResults.length) {
      const runningTurn = containerRef.current.querySelector("[data-status='running']");
      if (runningTurn) {
        runningTurn.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }
  }, [session?.currentTurn, session?.turnResults.length]);
  
  if (loading) {
    return (
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-4">
          <div className="h-24 bg-slate-700 rounded"></div>
          <div className="h-24 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }
  
  if (!sessionId || !session) {
    return (
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-8 text-center">
        <span className="text-4xl">🎭</span>
        <h3 className="text-lg font-medium text-white mt-4">No Active Session</h3>
        <p className="text-sm text-slate-400 mt-2">
          Execute a recipe to see the team visualization
        </p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-slate-800 rounded-xl border border-red-500/30 p-6">
        <div className="flex items-center gap-2 text-red-400">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      </div>
    );
  }
  
  const statusConfig = STATUS_CONFIG[session.status];
  
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 bg-gradient-to-r from-green-500/10 to-teal-500/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎭</span>
            <div>
              <h3 className="font-semibold text-white">{session.recipeName}</h3>
              <p className="text-xs text-slate-400">{session.goal}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusConfig.color} text-white`}>
              {statusConfig.icon} {session.status}
            </span>
          </div>
        </div>
        
        {/* Progress */}
        <div className="mt-4 flex items-center gap-4">
          <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className={`h-full ${statusConfig.color.replace(" animate-pulse", "")} transition-all duration-500`}
              style={{ width: `${(session.currentTurn / session.totalTurns) * 100}%` }}
            />
          </div>
          <span className="text-sm text-slate-400">
            {session.currentTurn}/{session.totalTurns}
          </span>
        </div>
      </div>
      
      {/* Timeline Visualization */}
      <div ref={containerRef} className="p-4 max-h-[600px] overflow-y-auto">
        <div className="relative">
          {/* Vertical Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-slate-700" />
          
          {/* Turns */}
          <div className="space-y-6">
            {session.turnResults.map((turn, index) => {
              const config = STATUS_CONFIG[turn.status];
              const agentIcon = AGENT_ICONS[turn.agentId] || "🤖";
              
              return (
                <div
                  key={turn.stepIndex}
                  data-status={turn.status}
                  className="relative pl-20"
                >
                  {/* Node */}
                  <div
                    className={`absolute left-5 w-6 h-6 rounded-full ${config.color} ring-2 ${config.ring} flex items-center justify-center z-10`}
                  >
                    <span className="text-xs text-white font-bold">{index + 1}</span>
                  </div>
                  
                  {/* Card */}
                  <div
                    className={`rounded-xl border transition-all ${
                      turn.status === "running"
                        ? "border-blue-500/50 bg-blue-500/10"
                        : "border-slate-700 bg-slate-800/50"
                    }`}
                  >
                    {/* Turn Header */}
                    <div className="p-4 flex items-center gap-4">
                      <span className="text-3xl">{agentIcon}</span>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-white">{turn.agentName}</h4>
                        <div className="flex items-center gap-3 mt-1">
                          <span className={`text-xs ${config.color.replace("bg-", "text-").replace(" animate-pulse", "")}`}>
                            {config.icon} {turn.status}
                          </span>
                          {turn.durationMs && (
                            <span className="text-xs text-slate-500">
                              {(turn.durationMs / 1000).toFixed(1)}s
                            </span>
                          )}
                          {turn.taskId && (
                            <code className="text-xs text-slate-500 font-mono truncate max-w-[150px]">
                              {turn.taskId}
                            </code>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Message */}
                    {turn.message && (
                      <div className="px-4 pb-4">
                        <div className="p-3 bg-slate-900/50 rounded-lg text-sm text-slate-300">
                          {turn.message}
                        </div>
                      </div>
                    )}
                    
                    {/* Error */}
                    {turn.error && (
                      <div className="px-4 pb-4">
                        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-400">
                          <strong>Error:</strong> {turn.error}
                        </div>
                      </div>
                    )}
                    
                    {/* Artifacts */}
                    {turn.artifacts.length > 0 && (
                      <div className="px-4 pb-4">
                        <h5 className="text-xs text-slate-500 uppercase tracking-wider mb-2">
                          Artifacts ({turn.artifacts.length})
                        </h5>
                        <div className="flex flex-wrap gap-2">
                          {turn.artifacts.map((artifact, ai) => (
                            <button
                              key={ai}
                              onClick={() =>
                                setSelectedArtifact(
                                  selectedArtifact?.turnIndex === index && selectedArtifact?.artifactIndex === ai
                                    ? null
                                    : { turnIndex: index, artifactIndex: ai }
                                )
                              }
                              className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
                                selectedArtifact?.turnIndex === index && selectedArtifact?.artifactIndex === ai
                                  ? "bg-purple-500/30 border border-purple-500/50 text-purple-300"
                                  : "bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700"
                              }`}
                            >
                              📄 {artifact.name}
                              <span className="ml-2 text-slate-500">({artifact.type.split("/")[1] || artifact.type})</span>
                            </button>
                          ))}
                        </div>
                        
                        {/* Rich Artifact Preview with AssetPreview component */}
                        {selectedArtifact?.turnIndex === index && (
                          <div className="mt-3">
                            <AssetPreview
                              name={turn.artifacts[selectedArtifact.artifactIndex].name}
                              type={turn.artifacts[selectedArtifact.artifactIndex].type}
                              data={turn.artifacts[selectedArtifact.artifactIndex].data}
                              onClose={() => setSelectedArtifact(null)}
                              maxHeight="400px"
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            
            {/* Pending turns placeholder */}
            {session.turnResults.length < session.totalTurns && session.status === "running" && (
              <div className="relative pl-20 opacity-50">
                <div className="absolute left-5 w-6 h-6 rounded-full bg-slate-700 ring-2 ring-slate-600 flex items-center justify-center z-10">
                  <span className="text-xs text-slate-400 font-bold">
                    {session.turnResults.length + 1}
                  </span>
                </div>
                <div className="p-4 rounded-xl border border-slate-700 border-dashed bg-slate-800/30">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl opacity-50">🤖</span>
                    <div className="text-sm text-slate-500">
                      Waiting for next agent...
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <div className="p-4 border-t border-slate-700 bg-slate-900/30">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <div>
            <span>Session:</span>{" "}
            <code className="font-mono text-slate-400">{session.id}</code>
          </div>
          <div>
            <span>Started:</span>{" "}
            <span className="text-slate-400">{new Date(session.createdAt).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
