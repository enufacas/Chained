/**
 * History Page
 *
 * Displays all persisted artifacts and sessions from team, recipe, and pipeline runs.
 * Provides an index-style view of all work completed with artifact previews.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import {
  getStoredArtifacts,
  getStoredSessions,
  clearAllStorage,
  getStorageStats,
  StoredArtifact,
  StoredSession,
  deleteArtifact,
  deleteSession,
} from "@/lib/storage";
import ArtifactPreviewOverlay from "@/components/ArtifactPreviewOverlay";

// Get icon for artifact type
function getArtifactIcon(type: string, name: string): string {
  const lowerType = type.toLowerCase();
  const lowerName = name.toLowerCase();

  if (lowerType.includes("svg") || lowerName.endsWith(".svg")) return "🖼️";
  if (lowerType.includes("markdown") || lowerType.includes("md") || lowerName.endsWith(".md"))
    return "📝";
  if (lowerType.includes("html") || lowerName.endsWith(".html")) return "🌐";
  if (lowerType.includes("json") || lowerName.endsWith(".json")) return "📋";
  if (lowerType.includes("image") || /\.(png|jpg|jpeg|gif|webp)$/i.test(lowerName)) return "🖼️";
  if (lowerType.includes("text") || lowerType.includes("plain")) return "📄";

  return "📄";
}

// Get color class for source type
function getSourceColor(source: string): string {
  switch (source) {
    case "pipeline":
      return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    case "team":
      return "bg-purple-500/20 text-purple-400 border-purple-500/30";
    case "recipe":
      return "bg-pink-500/20 text-pink-400 border-pink-500/30";
    case "chat":
      return "bg-green-500/20 text-green-400 border-green-500/30";
    default:
      return "bg-slate-500/20 text-slate-400 border-slate-500/30";
  }
}

// Format time
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

type ViewMode = "all" | "artifacts" | "sessions";
type FilterSource = "all" | "pipeline" | "team" | "recipe" | "chat";
type A2AFilter = "all" | "agent-card" | "task" | "message" | "standard";

export default function HistoryPage() {
  const [artifacts, setArtifacts] = useState<StoredArtifact[]>([]);
  const [sessions, setSessions] = useState<StoredSession[]>([]);
  const [stats, setStats] = useState({ artifactsCount: 0, sessionsCount: 0, estimatedSize: "0 B" });
  const [viewMode, setViewMode] = useState<ViewMode>("all");
  const [filterSource, setFilterSource] = useState<FilterSource>("all");
  const [filterA2AType, setFilterA2AType] = useState<A2AFilter>("all");
  const [selectedArtifact, setSelectedArtifact] = useState<StoredArtifact | null>(null);
  const [expandedSession, setExpandedSession] = useState<string | null>(null);

  // Load data
  const loadData = useCallback(() => {
    setArtifacts(getStoredArtifacts());
    setSessions(getStoredSessions());
    setStats(getStorageStats());
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Filter artifacts by source
  let filteredArtifacts =
    filterSource === "all"
      ? artifacts
      : artifacts.filter((a) => a.source === filterSource);
  
  // Filter artifacts by A2A type
  if (filterA2AType !== "all") {
    filteredArtifacts = filteredArtifacts.filter((a) => {
      if (filterA2AType === "standard") {
        return !a.a2aType; // Standard artifacts have no a2aType
      }
      return a.a2aType === filterA2AType;
    });
  }

  // Filter sessions
  const filteredSessions =
    filterSource === "all"
      ? sessions
      : sessions.filter(
          (s) =>
            s.type === filterSource ||
            (filterSource === "team" && s.type === "recipe")
        );

  // Handle clear all
  const handleClearAll = () => {
    if (confirm("Clear all stored data? This cannot be undone.")) {
      clearAllStorage();
      loadData();
    }
  };

  // Handle delete artifact
  const handleDeleteArtifact = (id: string) => {
    deleteArtifact(id);
    loadData();
  };

  // Handle delete session
  const handleDeleteSession = (id: string) => {
    deleteSession(id);
    loadData();
  };

  // Get all artifacts as array for navigation
  const allArtifactsArray = filteredArtifacts.map((a) => ({
    name: a.name,
    type: a.type,
    data: a.data,
    preview: a.preview,
  }));

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <a
                href="/"
                className="text-slate-400 hover:text-white transition"
              >
                ← Back
              </a>
              <div>
                <h1 className="text-xl font-bold">📦 Work History</h1>
                <p className="text-xs text-slate-500">
                  {stats.artifactsCount} artifacts • {stats.sessionsCount} sessions •{" "}
                  {stats.estimatedSize}
                </p>
              </div>
            </div>
            <button
              onClick={handleClearAll}
              className="px-3 py-1.5 text-xs rounded bg-red-500/10 text-red-400 hover:bg-red-500/20 transition border border-red-500/30"
            >
              Clear All
            </button>
          </div>

          {/* Filters */}
          <div className="mt-4 flex flex-wrap gap-2">
            {/* View Mode */}
            <div className="flex rounded overflow-hidden border border-slate-700">
              {(["all", "artifacts", "sessions"] as ViewMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`px-3 py-1.5 text-xs transition ${
                    viewMode === mode
                      ? "bg-purple-500 text-white"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                  }`}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>

            {/* Source Filter */}
            <div className="flex rounded overflow-hidden border border-slate-700">
              {(
                ["all", "pipeline", "team", "recipe", "chat"] as FilterSource[]
              ).map((source) => (
                <button
                  key={source}
                  onClick={() => setFilterSource(source)}
                  className={`px-3 py-1.5 text-xs transition ${
                    filterSource === source
                      ? "bg-purple-500 text-white"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                  }`}
                >
                  {source.charAt(0).toUpperCase() + source.slice(1)}
                </button>
              ))}
            </div>
            
            {/* A2A Artifact Type Filter */}
            {viewMode !== "sessions" && (
              <div className="flex rounded overflow-hidden border border-slate-700">
                {(
                  ["all", "agent-card", "task", "message", "standard"] as A2AFilter[]
                ).map((a2aType) => (
                  <button
                    key={a2aType}
                    onClick={() => setFilterA2AType(a2aType)}
                    className={`px-3 py-1.5 text-xs transition ${
                      filterA2AType === a2aType
                        ? "bg-cyan-500 text-white"
                        : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                    }`}
                    title={
                      a2aType === "agent-card" ? "🪪 A2A Agent Cards" :
                      a2aType === "task" ? "📋 A2A Tasks" :
                      a2aType === "message" ? "💬 A2A Messages" :
                      a2aType === "standard" ? "📄 Standard Artifacts" : "All Types"
                    }
                  >
                    {a2aType === "agent-card" ? "🪪 Cards" :
                     a2aType === "task" ? "📋 Tasks" :
                     a2aType === "message" ? "💬 Messages" :
                     a2aType === "standard" ? "📄 Standard" : "All Types"}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Sessions Section */}
        {(viewMode === "all" || viewMode === "sessions") && filteredSessions.length > 0 && (
          <section>
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Sessions ({filteredSessions.length})
            </h2>
            <div className="space-y-2">
              {filteredSessions.map((session) => (
                <div
                  key={session.id}
                  className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden"
                >
                  <button
                    onClick={() =>
                      setExpandedSession(
                        expandedSession === session.id ? null : session.id
                      )
                    }
                    className="w-full px-4 py-3 flex items-center gap-3 hover:bg-slate-700/30 transition text-left"
                  >
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        session.status === "completed"
                          ? "bg-green-500/20"
                          : session.status === "failed"
                          ? "bg-red-500/20"
                          : "bg-blue-500/20"
                      }`}
                    >
                      {session.status === "completed"
                        ? "✅"
                        : session.status === "failed"
                        ? "❌"
                        : "⏳"}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-white">{session.name}</div>
                      <div className="text-xs text-slate-400 truncate">
                        {session.topic}
                      </div>
                    </div>
                    <div className="text-right">
                      <span
                        className={`px-2 py-0.5 text-xs rounded ${getSourceColor(
                          session.type
                        )}`}
                      >
                        {session.type}
                      </span>
                      <div className="text-xs text-slate-500 mt-1">
                        {formatDate(session.createdAt)}
                      </div>
                    </div>
                    <span
                      className={`text-slate-500 transition-transform ${
                        expandedSession === session.id ? "rotate-180" : ""
                      }`}
                    >
                      ▼
                    </span>
                  </button>

                  {expandedSession === session.id && (
                    <div className="px-4 pb-4 border-t border-slate-700">
                      <div className="mt-3 flex items-center justify-between">
                        <span className="text-xs text-slate-500">
                          {session.artifacts.length} artifacts
                        </span>
                        <button
                          onClick={() => handleDeleteSession(session.id)}
                          className="text-xs text-red-400 hover:text-red-300"
                        >
                          Delete
                        </button>
                      </div>
                      {session.artifacts.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {session.artifacts.map((artifactId) => {
                            const artifact = artifacts.find(
                              (a) => a.id === artifactId
                            );
                            if (!artifact) return null;
                            return (
                              <button
                                key={artifactId}
                                onClick={() => setSelectedArtifact(artifact)}
                                className="px-2 py-1 text-xs rounded bg-slate-700 hover:bg-slate-600 text-slate-300"
                              >
                                {artifact.name}
                              </button>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Artifacts Section */}
        {(viewMode === "all" || viewMode === "artifacts") && filteredArtifacts.length > 0 && (
          <section>
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Artifacts ({filteredArtifacts.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredArtifacts.map((artifact) => (
                <div
                  key={artifact.id}
                  className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden group hover:border-purple-500/50 transition"
                >
                  <button
                    onClick={() => setSelectedArtifact(artifact)}
                    className="w-full p-4 text-left"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">
                        {getArtifactIcon(artifact.type, artifact.name)}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-white truncate">
                          {artifact.name}
                        </div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          {artifact.type}
                        </div>
                        <div className="flex items-center gap-2 mt-2 flex-wrap">
                          <span
                            className={`px-1.5 py-0.5 text-[10px] rounded ${getSourceColor(
                              artifact.source
                            )}`}
                          >
                            {artifact.source}
                          </span>
                          {artifact.a2aType && (
                            <span className={`px-1.5 py-0.5 text-[10px] rounded ${
                              artifact.a2aType === "agent-card" ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" :
                              artifact.a2aType === "task" ? "bg-amber-500/20 text-amber-400 border-amber-500/30" :
                              artifact.a2aType === "message" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" :
                              "bg-purple-500/20 text-purple-400 border-purple-500/30"
                            }`}>
                              {artifact.a2aType === "agent-card" ? "🪪 A2A Card" :
                               artifact.a2aType === "task" ? "📋 A2A Task" :
                               artifact.a2aType === "message" ? "💬 A2A Message" :
                               `A2A ${artifact.a2aType}`}
                            </span>
                          )}
                          {artifact.agentName && (
                            <span className="text-[10px] text-slate-500">
                              {artifact.agentName}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Preview */}
                    {artifact.preview && (
                      <div className="mt-3 p-2 rounded bg-slate-900/50 text-xs text-slate-400 font-mono line-clamp-3 overflow-hidden">
                        {artifact.preview}
                      </div>
                    )}
                  </button>

                  <div className="px-4 pb-3 flex items-center justify-between border-t border-slate-700">
                    <span className="text-[10px] text-slate-500">
                      {formatDate(artifact.createdAt)} •{" "}
                      {Math.ceil(artifact.data.length / 1024)} KB
                    </span>
                    <button
                      onClick={() => handleDeleteArtifact(artifact.id)}
                      className="text-[10px] text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Empty State */}
        {filteredArtifacts.length === 0 && filteredSessions.length === 0 && (
          <div className="text-center py-12">
            <span className="text-4xl block mb-4">📭</span>
            <h3 className="text-lg font-medium text-white mb-2">No history yet</h3>
            <p className="text-sm text-slate-400">
              Run a team, recipe, or pipeline to start building your work history.
            </p>
            <a
              href="/"
              className="inline-block mt-4 px-4 py-2 rounded bg-purple-500 hover:bg-purple-600 text-white text-sm transition"
            >
              Go to Dashboard
            </a>
          </div>
        )}
      </main>

      {/* Artifact Preview Overlay */}
      <ArtifactPreviewOverlay
        artifact={
          selectedArtifact
            ? {
                name: selectedArtifact.name,
                type: selectedArtifact.type,
                data: selectedArtifact.data,
              }
            : null
        }
        onClose={() => setSelectedArtifact(null)}
        allArtifacts={allArtifactsArray}
        onSelectArtifact={(artifact) => {
          const found = filteredArtifacts.find(
            (a) => a.name === artifact.name && a.type === artifact.type
          );
          if (found) setSelectedArtifact(found);
        }}
      />
    </div>
  );
}
