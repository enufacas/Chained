/**
 * AgentCanvas Component
 *
 * Interactive canvas for visualizing and managing agent teams.
 * Shows agents in a grid/canvas layout with drag-and-drop capabilities
 * and real-time status updates.
 * 
 * Features:
 * - Drag-and-drop team building
 * - Text input for workflow goals
 * - Turn configuration (default 2, max 5)
 * - Execution mode (sequential or parallel)
 */

"use client";

import { useState, useEffect, useCallback } from "react";

interface AgentInfo {
  id: string;
  displayName: string;
  description: string;
  icon: string;
  category: string;
  configured: boolean;
  skills: string[];
  health?: {
    status: "healthy" | "unhealthy" | "unknown";
    responseTimeMs?: number;
    version?: string;
  };
}

interface CanvasAgent extends AgentInfo {
  position: { x: number; y: number };
  selected: boolean;
  order?: number;
}

interface ExecutionConfig {
  maxTurnsPerAgent: number;
  executionMode: "sequential" | "parallel";
}

interface AgentCanvasProps {
  onTeamChange?: (teamAgents: string[]) => void;
  onExecute?: (goal: string, config: ExecutionConfig) => void;
  initialTeam?: string[];
}

const CATEGORIES = [
  { id: "research", label: "Research", color: "from-blue-500 to-cyan-500" },
  { id: "seo", label: "SEO", color: "from-green-500 to-emerald-500" },
  { id: "content", label: "Content", color: "from-purple-500 to-pink-500" },
  { id: "development", label: "Development", color: "from-orange-500 to-red-500" },
  { id: "analytics", label: "Analytics", color: "from-yellow-500 to-amber-500" },
  { id: "visual", label: "Visual", color: "from-indigo-500 to-violet-500" },
];

const DEFAULT_TURNS = 2;

export default function AgentCanvas({ onTeamChange, onExecute, initialTeam = [] }: AgentCanvasProps) {
  const [agents, setAgents] = useState<CanvasAgent[]>([]);
  const [teamAgents, setTeamAgents] = useState<string[]>(initialTeam);
  const [loading, setLoading] = useState(true);
  const [draggedAgent, setDraggedAgent] = useState<string | null>(null);
  const [filter, setFilter] = useState<string | null>(null);
  const [goal, setGoal] = useState("");
  const [maxTurnsPerAgent, setMaxTurnsPerAgent] = useState(DEFAULT_TURNS);
  const [executionMode, setExecutionMode] = useState<"sequential" | "parallel">("sequential");
  const [executing, setExecuting] = useState(false);
  
  // Fetch agents from registry
  const fetchAgents = useCallback(async () => {
    try {
      const response = await fetch("/api/registry?health=true");
      if (response.ok) {
        const data = await response.json();
        const canvasAgents: CanvasAgent[] = data.agents.map((agent: AgentInfo, index: number) => ({
          ...agent,
          position: { x: (index % 3) * 220 + 20, y: Math.floor(index / 3) * 180 + 20 },
          selected: initialTeam.includes(agent.id),
          order: initialTeam.indexOf(agent.id),
        }));
        setAgents(canvasAgents);
      }
    } catch (error) {
      console.error("Failed to fetch agents:", error);
    } finally {
      setLoading(false);
    }
  }, [initialTeam]);
  
  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);
  
  // Handle agent selection
  const toggleAgent = (agentId: string) => {
    const agent = agents.find((a) => a.id === agentId);
    if (!agent || !agent.configured) return;
    
    let newTeam: string[];
    if (teamAgents.includes(agentId)) {
      newTeam = teamAgents.filter((id) => id !== agentId);
    } else {
      newTeam = [...teamAgents, agentId];
    }
    
    setTeamAgents(newTeam);
    onTeamChange?.(newTeam);
    
    // Update agent selection state
    setAgents((prev) =>
      prev.map((a) => ({
        ...a,
        selected: newTeam.includes(a.id),
        order: newTeam.indexOf(a.id),
      }))
    );
  };
  
  // Handle drag start
  const handleDragStart = (agentId: string) => {
    setDraggedAgent(agentId);
  };
  
  // Handle drag end
  const handleDragEnd = () => {
    setDraggedAgent(null);
  };
  
  // Handle drop on team area
  const handleDropOnTeam = () => {
    if (draggedAgent && !teamAgents.includes(draggedAgent)) {
      const agent = agents.find((a) => a.id === draggedAgent);
      if (agent?.configured) {
        toggleAgent(draggedAgent);
      }
    }
  };
  
  // Handle workflow execution
  const handleExecute = async () => {
    if (!goal.trim() || teamAgents.length === 0) return;
    
    setExecuting(true);
    try {
      onExecute?.(goal.trim(), {
        maxTurnsPerAgent,
        executionMode,
      });
    } finally {
      setExecuting(false);
    }
  };
  
  // Get filtered agents
  const filteredAgents = filter
    ? agents.filter((a) => a.category === filter)
    : agents;
  
  // Get team agents in order
  const orderedTeamAgents = teamAgents
    .map((id) => agents.find((a) => a.id === id))
    .filter(Boolean) as CanvasAgent[];
  
  const getStatusColor = (status?: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-500";
      case "unhealthy":
        return "bg-red-500";
      default:
        return "bg-yellow-500";
    }
  };
  
  if (loading) {
    return (
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-3 sm:p-4 animate-pulse">
        <div className="h-5 bg-slate-700 rounded w-1/3 mb-3"></div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-20 sm:h-28 bg-slate-700 rounded"></div>
          ))}
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700 overflow-hidden">
      {/* Header - Compact */}
      <div className="px-2 py-2 sm:px-3 sm:py-2 border-b border-slate-700 bg-gradient-to-r from-indigo-500/10 to-purple-500/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg sm:text-xl">🎨</span>
            <div>
              <h3 className="text-sm font-semibold text-white">Agent Canvas</h3>
              <p className="text-[10px] sm:text-xs text-slate-400">
                Tap to select • {teamAgents.length} agents
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              setTeamAgents([]);
              setAgents((prev) => prev.map((a) => ({ ...a, selected: false, order: undefined })));
              onTeamChange?.([]);
            }}
            className="px-2 py-1 text-[10px] sm:text-xs rounded bg-slate-700 hover:bg-slate-600 active:bg-slate-500 active:scale-95 text-slate-300 transition"
          >
            Clear
          </button>
        </div>
      </div>
      
      {/* Category Filter - Smaller */}
      <div className="px-2 py-1.5 sm:p-2 border-b border-slate-700 flex gap-1 sm:gap-2 overflow-x-auto">
        <button
          onClick={() => setFilter(null)}
          className={`px-2 py-0.5 sm:px-2.5 sm:py-1 text-[10px] sm:text-xs rounded-full whitespace-nowrap transition active:scale-95 ${
            filter === null
              ? "bg-slate-600 text-white"
              : "bg-slate-700 text-slate-400 hover:bg-slate-600"
          }`}
        >
          All
        </button>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setFilter(cat.id)}
            className={`px-2 py-0.5 sm:px-2.5 sm:py-1 text-[10px] sm:text-xs rounded-full whitespace-nowrap transition active:scale-95 ${
              filter === cat.id
                ? `bg-gradient-to-r ${cat.color} text-white shadow-lg`
                : "bg-slate-700 text-slate-400 hover:bg-slate-600"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>
      
      {/* Team Preview - Compact */}
      {orderedTeamAgents.length > 0 && (
        <div
          className="px-2 py-2 sm:px-3 sm:py-2 border-b border-slate-700 bg-slate-900/50"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDropOnTeam}
        >
          <h4 className="text-[10px] sm:text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
            Team Order
          </h4>
          <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
            {orderedTeamAgents.map((agent, index) => (
              <div
                key={agent.id}
                className="flex items-center gap-1 sm:gap-1.5 px-1.5 py-1 sm:px-2 sm:py-1.5 bg-slate-800 rounded border border-slate-700"
              >
                <span className="w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-purple-500 text-white text-[10px] sm:text-xs flex items-center justify-center font-bold">
                  {index + 1}
                </span>
                <span className="text-sm sm:text-base">{agent.icon}</span>
                <span className="text-[10px] sm:text-xs text-white hidden sm:inline">{agent.displayName}</span>
                <button
                  onClick={() => toggleAgent(agent.id)}
                  className="ml-0.5 text-slate-500 hover:text-red-400 active:text-red-500 text-sm"
                >
                  ×
                </button>
              </div>
            ))}
            <div className="text-slate-500 text-[10px] sm:text-xs">
              {executionMode}
            </div>
          </div>
        </div>
      )}
      
      {/* Agent Grid - Smaller cards on mobile */}
      <div className="p-2 sm:p-3">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3">
          {filteredAgents.map((agent) => {
            const category = CATEGORIES.find((c) => c.id === agent.category);
            
            return (
              <div
                key={agent.id}
                draggable={agent.configured}
                onDragStart={() => handleDragStart(agent.id)}
                onDragEnd={handleDragEnd}
                onClick={() => toggleAgent(agent.id)}
                className={`relative p-2 sm:p-3 rounded-lg border transition-all cursor-pointer active:scale-95 ${
                  agent.selected
                    ? "border-purple-500 bg-purple-500/10 ring-2 ring-purple-500/30 shadow-lg shadow-purple-500/10"
                    : agent.configured
                    ? "border-slate-700 bg-slate-800/50 hover:border-slate-600 hover:bg-slate-700/50"
                    : "border-slate-700/50 bg-slate-800/20 opacity-50 cursor-not-allowed"
                } ${draggedAgent === agent.id ? "opacity-50 scale-95" : ""}`}
              >
                {/* Status Indicator */}
                {agent.health && (
                  <div
                    className={`absolute top-1.5 right-1.5 sm:top-2 sm:right-2 w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full ${getStatusColor(
                      agent.health.status
                    )} ${agent.health.status === "healthy" ? "animate-pulse" : ""}`}
                    title={`${agent.health.status}${
                      agent.health.responseTimeMs ? ` (${agent.health.responseTimeMs}ms)` : ""
                    }`}
                  />
                )}
                
                {/* Selection Order */}
                {agent.selected && agent.order !== undefined && agent.order >= 0 && (
                  <div className="absolute top-1.5 left-1.5 sm:top-2 sm:left-2 w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-purple-500 text-white text-[10px] sm:text-xs flex items-center justify-center font-bold">
                    {agent.order + 1}
                  </div>
                )}
                
                {/* Agent Icon */}
                <div className="text-2xl sm:text-3xl mb-1 sm:mb-2">{agent.icon}</div>
                
                {/* Agent Info */}
                <div>
                  <h4 className="text-xs sm:text-sm font-medium text-white">{agent.displayName}</h4>
                  <p className="text-[10px] sm:text-xs text-slate-400 mt-0.5 line-clamp-1 sm:line-clamp-2">
                    {agent.description}
                  </p>
                </div>
                
                {/* Category Badge - Hidden on smallest screens */}
                {category && (
                  <div
                    className={`hidden sm:inline-block mt-2 px-1.5 py-0.5 text-[10px] rounded bg-gradient-to-r ${category.color} text-white`}
                  >
                    {category.label}
                  </div>
                )}
                
                {/* Skills - Hidden on mobile */}
                <div className="hidden sm:flex mt-1.5 flex-wrap gap-1">
                  {agent.skills.slice(0, 2).map((skill) => (
                    <span
                      key={skill}
                      className="px-1 py-0.5 text-[10px] rounded bg-slate-700/50 text-slate-400"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
                
                {/* Not Configured Warning */}
                {!agent.configured && (
                  <div className="mt-1 text-[10px] sm:text-xs text-yellow-400">
                    ⚠️ Not configured
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Workflow Configuration & Execution - Compact */}
      {teamAgents.length > 0 && (
        <div className="px-2 py-2 sm:px-3 sm:py-3 border-t border-slate-700 bg-slate-900/30">
          {/* Execution Configuration - Compact layout */}
          <div className="mb-2 sm:mb-3 flex flex-wrap gap-2 sm:gap-3">
            {/* Turns Per Agent */}
            <div className="flex items-center gap-1 sm:gap-2">
              <label className="text-[10px] sm:text-xs text-slate-400">Turns:</label>
              <div className="flex items-center gap-0.5 sm:gap-1">
                {[1, 2, 3, 4, 5].map((turns) => (
                  <button
                    key={turns}
                    onClick={() => setMaxTurnsPerAgent(turns)}
                    className={`w-6 h-6 sm:w-7 sm:h-7 text-[10px] sm:text-xs rounded transition active:scale-95 ${
                      maxTurnsPerAgent === turns
                        ? "bg-purple-500 text-white shadow-lg shadow-purple-500/20"
                        : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                    }`}
                  >
                    {turns}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Execution Mode */}
            <div className="flex items-center gap-1 sm:gap-2">
              <label className="text-[10px] sm:text-xs text-slate-400">Mode:</label>
              <div className="flex rounded overflow-hidden border border-slate-600">
                <button
                  onClick={() => setExecutionMode("sequential")}
                  className={`px-2 py-1 sm:px-2.5 sm:py-1 text-[10px] sm:text-xs transition active:scale-95 ${
                    executionMode === "sequential"
                      ? "bg-purple-500 text-white"
                      : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                  }`}
                >
                  Seq →
                </button>
                <button
                  onClick={() => setExecutionMode("parallel")}
                  className={`px-2 py-1 sm:px-2.5 sm:py-1 text-[10px] sm:text-xs transition active:scale-95 ${
                    executionMode === "parallel"
                      ? "bg-purple-500 text-white"
                      : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                  }`}
                >
                  Par ⇉
                </button>
              </div>
            </div>
          </div>
          
          {/* Goal Input - Immediate visual feedback */}
          <div className="flex gap-1.5 sm:gap-2">
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="Enter goal (e.g., 'Write about AI')..."
              className="flex-1 px-2 py-2 sm:px-3 sm:py-2.5 bg-slate-900 border border-slate-700 rounded text-sm text-white placeholder:text-slate-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
              disabled={executing}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleExecute();
                }
              }}
            />
            <button
              onClick={handleExecute}
              disabled={!goal.trim() || executing}
              className={`px-3 py-2 sm:px-4 sm:py-2.5 text-sm font-medium rounded transition-all active:scale-95 ${
                executing 
                  ? "bg-blue-500 text-white animate-pulse shadow-lg shadow-blue-500/30"
                  : goal.trim()
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/20"
                  : "bg-slate-600 text-slate-400 cursor-not-allowed"
              }`}
            >
              {executing ? (
                <span className="flex items-center gap-1">
                  <span className="animate-spin">⏳</span>
                  <span className="hidden sm:inline">Working...</span>
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  🚀
                  <span className="hidden sm:inline">Start</span>
                </span>
              )}
            </button>
          </div>
          
          {/* Configuration Summary - Very compact */}
          <div className="mt-1.5 text-[10px] sm:text-xs text-slate-500">
            {teamAgents.length} agents • {maxTurnsPerAgent} turn{maxTurnsPerAgent > 1 ? "s" : ""} • {executionMode}
          </div>
        </div>
      )}
    </div>
  );
}
