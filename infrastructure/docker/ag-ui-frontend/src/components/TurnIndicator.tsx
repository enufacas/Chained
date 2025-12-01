/**
 * TurnIndicator Component
 *
 * Shows the current turn in a multi-agent team execution.
 * Displays turn number, agent, and status.
 */

"use client";

import { useState, useEffect } from "react";

interface TurnResult {
  stepIndex: number;
  agentId: string;
  agentName: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
  message?: string;
  error?: string;
}

interface TurnIndicatorProps {
  currentTurn: number;
  totalTurns: number;
  turnResults: TurnResult[];
  agentIcons: Record<string, string>;
  sessionStatus: "pending" | "running" | "completed" | "failed";
}

const statusConfig = {
  pending: { color: "bg-slate-500", icon: "⏳", label: "Pending" },
  running: { color: "bg-blue-500 animate-pulse", icon: "🔄", label: "Running" },
  completed: { color: "bg-green-500", icon: "✅", label: "Completed" },
  failed: { color: "bg-red-500", icon: "❌", label: "Failed" },
  skipped: { color: "bg-yellow-500", icon: "⏭️", label: "Skipped" },
};

export default function TurnIndicator({
  currentTurn,
  totalTurns,
  turnResults,
  agentIcons,
  sessionStatus,
}: TurnIndicatorProps) {
  const [expandedTurn, setExpandedTurn] = useState<number | null>(null);
  
  // Auto-expand the current running turn
  useEffect(() => {
    const runningTurn = turnResults.find((t) => t.status === "running");
    if (runningTurn) {
      setExpandedTurn(runningTurn.stepIndex);
    }
  }, [turnResults]);
  
  const progressPercent = totalTurns > 0 ? (currentTurn / totalTurns) * 100 : 0;
  
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 bg-gradient-to-r from-blue-500/10 to-purple-500/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎯</span>
            <div>
              <h3 className="font-semibold text-white">Turn Progress</h3>
              <p className="text-xs text-slate-400">
                Turn {currentTurn} of {totalTurns}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusConfig[sessionStatus].color} text-white`}>
              {statusConfig[sessionStatus].icon} {statusConfig[sessionStatus].label}
            </span>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-4 h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>
      
      {/* Turn Timeline */}
      <div className="p-4 space-y-2">
        {turnResults.length === 0 ? (
          <div className="text-center text-slate-500 py-4">
            <span className="text-2xl">⏳</span>
            <p className="mt-2">Waiting for turns to execute...</p>
          </div>
        ) : (
          turnResults.map((turn, index) => {
            const config = statusConfig[turn.status];
            const isExpanded = expandedTurn === turn.stepIndex;
            const agentIcon = agentIcons[turn.agentId] || "🤖";
            
            return (
              <div
                key={turn.stepIndex}
                className={`rounded-lg border transition-all ${
                  turn.status === "running"
                    ? "border-blue-500/50 bg-blue-500/10"
                    : "border-slate-700 bg-slate-800/50"
                }`}
              >
                {/* Turn Header */}
                <button
                  onClick={() => setExpandedTurn(isExpanded ? null : turn.stepIndex)}
                  className="w-full p-3 flex items-center gap-3 text-left hover:bg-slate-700/30 transition"
                >
                  {/* Turn Number */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${config.color} text-white`}>
                    {index + 1}
                  </div>
                  
                  {/* Agent Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{agentIcon}</span>
                      <span className="font-medium text-white truncate">
                        {turn.agentName}
                      </span>
                    </div>
                    {turn.message && (
                      <p className="text-xs text-slate-400 truncate mt-1">
                        {turn.message}
                      </p>
                    )}
                  </div>
                  
                  {/* Status & Duration */}
                  <div className="flex flex-col items-end">
                    <span className={`text-xs ${config.color.replace("bg-", "text-").replace(" animate-pulse", "")}`}>
                      {config.icon} {config.label}
                    </span>
                    {turn.durationMs && (
                      <span className="text-xs text-slate-500 mt-1">
                        {(turn.durationMs / 1000).toFixed(1)}s
                      </span>
                    )}
                  </div>
                  
                  {/* Expand Indicator */}
                  <span className="text-slate-500 text-sm">
                    {isExpanded ? "▼" : "▶"}
                  </span>
                </button>
                
                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-3 pb-3 border-t border-slate-700/50 mt-2 pt-3">
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div>
                        <span className="text-slate-500">Started:</span>
                        <span className="text-slate-300 ml-2">
                          {new Date(turn.startedAt).toLocaleTimeString()}
                        </span>
                      </div>
                      {turn.completedAt && (
                        <div>
                          <span className="text-slate-500">Completed:</span>
                          <span className="text-slate-300 ml-2">
                            {new Date(turn.completedAt).toLocaleTimeString()}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {turn.error && (
                      <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
                        <strong>Error:</strong> {turn.error}
                      </div>
                    )}
                    
                    {turn.message && (
                      <div className="mt-3 p-2 bg-slate-700/30 rounded text-xs text-slate-300">
                        {turn.message}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
