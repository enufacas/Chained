/**
 * ArtifactStream Component
 *
 * Displays a scrollable stream of artifacts produced during execution.
 * Shows artifacts in a horizontal or grid layout with preview capability.
 * Persists artifacts to localStorage for access between page reloads.
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { getStoredArtifacts, StoredArtifact, clearArtifacts, getStorageStats } from "@/lib/storage";

interface ArtifactStreamProps {
  onSelectArtifact?: (artifact: StoredArtifact) => void;
  maxItems?: number;
  compact?: boolean;
}

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
      return "bg-blue-500/20 text-blue-400";
    case "team":
      return "bg-purple-500/20 text-purple-400";
    case "recipe":
      return "bg-pink-500/20 text-pink-400";
    case "chat":
      return "bg-green-500/20 text-green-400";
    default:
      return "bg-slate-500/20 text-slate-400";
  }
}

// Format time ago
function formatTimeAgo(dateString: string): string {
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

export default function ArtifactStream({
  onSelectArtifact,
  maxItems = 20,
  compact = false,
}: ArtifactStreamProps) {
  const [artifacts, setArtifacts] = useState<StoredArtifact[]>([]);
  const [expanded, setExpanded] = useState(false);
  const [stats, setStats] = useState({ artifactsCount: 0, sessionsCount: 0, estimatedSize: "0 B" });

  // Load artifacts from storage
  const loadArtifacts = useCallback(() => {
    const stored = getStoredArtifacts();
    setArtifacts(stored.slice(0, maxItems));
    setStats(getStorageStats());
  }, [maxItems]);

  useEffect(() => {
    loadArtifacts();
    // Refresh periodically
    const interval = setInterval(loadArtifacts, 5000);
    return () => clearInterval(interval);
  }, [loadArtifacts]);

  // Handle clear all
  const handleClearAll = () => {
    if (confirm("Clear all stored artifacts? This cannot be undone.")) {
      clearArtifacts();
      loadArtifacts();
    }
  };

  if (artifacts.length === 0) {
    return (
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full px-3 py-2 flex items-center justify-between hover:bg-slate-700/30 transition text-xs"
        >
          <div className="flex items-center gap-2">
            <span className="text-sm">📦</span>
            <span className="text-slate-400">Artifacts Stream</span>
          </div>
          <span className="px-2 py-0.5 rounded-full text-xs bg-slate-700 text-slate-500">
            Empty
          </span>
        </button>
        {expanded && (
          <div className="px-3 py-6 border-t border-slate-700 text-center">
            <span className="text-2xl block mb-2">📭</span>
            <p className="text-xs text-slate-500">
              No artifacts yet. Run a team, recipe, or pipeline to generate artifacts.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-2 flex items-center justify-between hover:bg-slate-700/30 transition text-xs"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm">📦</span>
          <span className="text-slate-400">Artifacts Stream</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-full text-xs bg-purple-500/20 text-purple-400">
            {artifacts.length} items
          </span>
          <span className="text-xs text-slate-600">{stats.estimatedSize}</span>
          <span
            className={`text-slate-500 transition-transform ${expanded ? "rotate-180" : ""}`}
          >
            ▼
          </span>
        </div>
      </button>

      {/* Content */}
      {expanded && (
        <div className="border-t border-slate-700">
          {/* Toolbar */}
          <div className="px-3 py-1.5 border-b border-slate-700 flex items-center justify-between bg-slate-900/30">
            <div className="text-[10px] text-slate-500">
              {stats.artifactsCount} artifacts stored
            </div>
            <button
              onClick={handleClearAll}
              className="text-[10px] text-red-400 hover:text-red-300 transition"
            >
              Clear All
            </button>
          </div>

          {/* Artifact List */}
          <div
            className={`overflow-x-auto ${compact ? "max-h-24" : "max-h-48"}`}
            style={{ scrollbarWidth: "thin" }}
          >
            <div className={compact ? "flex gap-2 p-2" : "space-y-1 p-2"}>
              {artifacts.map((artifact) => (
                <div
                  key={artifact.id}
                  onClick={() => onSelectArtifact?.(artifact)}
                  className={`${
                    compact
                      ? "flex-shrink-0 w-32 p-2"
                      : "flex items-center gap-2 p-2"
                  } rounded border border-slate-700 bg-slate-800/50 hover:bg-slate-700/50 cursor-pointer transition group`}
                >
                  {/* Icon */}
                  <span className={compact ? "text-xl block mb-1" : "text-lg"}>
                    {getArtifactIcon(artifact.type, artifact.name)}
                  </span>

                  {/* Info */}
                  <div className={compact ? "" : "flex-1 min-w-0"}>
                    <div
                      className={`text-xs font-medium text-white truncate ${
                        compact ? "w-full" : ""
                      }`}
                    >
                      {artifact.name}
                    </div>
                    <div className="flex items-center gap-1 mt-0.5">
                      <span
                        className={`px-1 py-0.5 rounded text-[10px] ${getSourceColor(
                          artifact.source
                        )}`}
                      >
                        {artifact.source}
                      </span>
                      {!compact && artifact.agentName && (
                        <span className="text-[10px] text-slate-500 truncate">
                          {artifact.agentName}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Time and size */}
                  {!compact && (
                    <div className="text-right">
                      <div className="text-[10px] text-slate-500">
                        {formatTimeAgo(artifact.createdAt)}
                      </div>
                      <div className="text-[10px] text-slate-600">
                        {Math.ceil(artifact.data.length / 1024)} KB
                      </div>
                    </div>
                  )}

                  {/* Preview on hover indicator */}
                  <div
                    className={`${
                      compact ? "mt-1 text-center" : ""
                    } text-[10px] text-purple-400 opacity-0 group-hover:opacity-100 transition`}
                  >
                    Click to view
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer - show more link */}
          {stats.artifactsCount > maxItems && (
            <div className="px-3 py-1.5 border-t border-slate-700 text-center">
              <a
                href="/history"
                className="text-[10px] text-purple-400 hover:text-purple-300 transition"
              >
                View all {stats.artifactsCount} artifacts →
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
