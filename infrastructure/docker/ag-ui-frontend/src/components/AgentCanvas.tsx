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
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-32 bg-slate-700 rounded"></div>
          ))}
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 bg-gradient-to-r from-indigo-500/10 to-purple-500/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎨</span>
            <div>
              <h3 className="font-semibold text-white">Agent Canvas</h3>
              <p className="text-xs text-slate-400">
                Click to add agents to your team • {teamAgents.length} selected
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              setTeamAgents([]);
              setAgents((prev) => prev.map((a) => ({ ...a, selected: false, order: undefined })));
              onTeamChange?.([]);
            }}
            className="px-3 py-1 text-xs rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition"
          >
            Clear Team
          </button>
        </div>
      </div>
      
      {/* Category Filter */}
      <div className="p-3 border-b border-slate-700 flex gap-2 overflow-x-auto">
        <button
          onClick={() => setFilter(null)}
          className={`px-3 py-1 text-xs rounded-full whitespace-nowrap transition ${
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
            className={`px-3 py-1 text-xs rounded-full whitespace-nowrap transition ${
              filter === cat.id
                ? `bg-gradient-to-r ${cat.color} text-white`
                : "bg-slate-700 text-slate-400 hover:bg-slate-600"
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>
      
      {/* Team Preview */}
      {orderedTeamAgents.length > 0 && (
        <div
          className="p-4 border-b border-slate-700 bg-slate-900/50"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDropOnTeam}
        >
          <h4 className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">
            Your Team (Execution Order)
          </h4>
          <div className="flex items-center gap-3 flex-wrap">
            {orderedTeamAgents.map((agent, index) => (
              <div
                key={agent.id}
                className="flex items-center gap-2 px-3 py-2 bg-slate-800 rounded-lg border border-slate-700"
              >
                <span className="w-5 h-5 rounded-full bg-purple-500 text-white text-xs flex items-center justify-center font-bold">
                  {index + 1}
                </span>
                <span className="text-lg">{agent.icon}</span>
                <span className="text-sm text-white">{agent.displayName}</span>
                <button
                  onClick={() => toggleAgent(agent.id)}
                  className="ml-1 text-slate-500 hover:text-red-400"
                >
                  ×
                </button>
              </div>
            ))}
            <div className="text-slate-500 text-xs">
              → {executionMode} execution
            </div>
          </div>
        </div>
      )}
      
      {/* Agent Grid */}
      <div className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {filteredAgents.map((agent) => {
            const category = CATEGORIES.find((c) => c.id === agent.category);
            
            return (
              <div
                key={agent.id}
                draggable={agent.configured}
                onDragStart={() => handleDragStart(agent.id)}
                onDragEnd={handleDragEnd}
                onClick={() => toggleAgent(agent.id)}
                className={`relative p-4 rounded-xl border transition-all cursor-pointer ${
                  agent.selected
                    ? "border-purple-500 bg-purple-500/10 ring-2 ring-purple-500/30"
                    : agent.configured
                    ? "border-slate-700 bg-slate-800/50 hover:border-slate-600 hover:bg-slate-700/50"
                    : "border-slate-700/50 bg-slate-800/20 opacity-50 cursor-not-allowed"
                } ${draggedAgent === agent.id ? "opacity-50 scale-95" : ""}`}
              >
                {/* Status Indicator */}
                {agent.health && (
                  <div
                    className={`absolute top-2 right-2 w-2.5 h-2.5 rounded-full ${getStatusColor(
                      agent.health.status
                    )} ${agent.health.status === "healthy" ? "animate-pulse" : ""}`}
                    title={`${agent.health.status}${
                      agent.health.responseTimeMs ? ` (${agent.health.responseTimeMs}ms)` : ""
                    }`}
                  />
                )}
                
                {/* Selection Order */}
                {agent.selected && agent.order !== undefined && agent.order >= 0 && (
                  <div className="absolute top-2 left-2 w-6 h-6 rounded-full bg-purple-500 text-white text-xs flex items-center justify-center font-bold">
                    {agent.order + 1}
                  </div>
                )}
                
                {/* Agent Icon */}
                <div className="text-4xl mb-3">{agent.icon}</div>
                
                {/* Agent Info */}
                <div>
                  <h4 className="font-medium text-white">{agent.displayName}</h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                    {agent.description}
                  </p>
                </div>
                
                {/* Category Badge */}
                {category && (
                  <div
                    className={`mt-3 px-2 py-0.5 text-xs rounded bg-gradient-to-r ${category.color} text-white inline-block`}
                  >
                    {category.label}
                  </div>
                )}
                
                {/* Skills */}
                <div className="mt-2 flex flex-wrap gap-1">
                  {agent.skills.slice(0, 2).map((skill) => (
                    <span
                      key={skill}
                      className="px-1.5 py-0.5 text-xs rounded bg-slate-700/50 text-slate-400"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
                
                {/* Not Configured Warning */}
                {!agent.configured && (
                  <div className="mt-2 text-xs text-yellow-400">
                    ⚠️ Not configured
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Workflow Configuration & Execution */}
      {teamAgents.length > 0 && (
        <div className="p-4 border-t border-slate-700 bg-slate-900/30">
          {/* Execution Configuration */}
          <div className="mb-4 flex flex-wrap gap-4">
            {/* Turns Per Agent */}
            <div className="flex items-center gap-2">
              <label className="text-xs text-slate-400">Turns per agent:</label>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((turns) => (
                  <button
                    key={turns}
                    onClick={() => setMaxTurnsPerAgent(turns)}
                    className={`w-8 h-8 text-xs rounded transition ${
                      maxTurnsPerAgent === turns
                        ? "bg-purple-500 text-white"
                        : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                    }`}
                  >
                    {turns}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Execution Mode */}
            <div className="flex items-center gap-2">
              <label className="text-xs text-slate-400">Mode:</label>
              <div className="flex rounded-lg overflow-hidden border border-slate-600">
                <button
                  onClick={() => setExecutionMode("sequential")}
                  className={`px-3 py-1.5 text-xs transition ${
                    executionMode === "sequential"
                      ? "bg-purple-500 text-white"
                      : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                  }`}
                >
                  Sequential →
                </button>
                <button
                  onClick={() => setExecutionMode("parallel")}
                  className={`px-3 py-1.5 text-xs transition ${
                    executionMode === "parallel"
                      ? "bg-purple-500 text-white"
                      : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                  }`}
                >
                  Parallel ⇉
                </button>
              </div>
            </div>
          </div>
          
          {/* Goal Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="Enter your goal (e.g., 'Write a blog post about AI trends')..."
              className="flex-1 px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder:text-slate-500 focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
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
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-all"
            >
              {executing ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin">⏳</span>
                  Running...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  🚀 Start
                </span>
              )}
            </button>
          </div>
          
          {/* Configuration Summary */}
          <div className="mt-2 text-xs text-slate-500">
            {teamAgents.length} agents • {maxTurnsPerAgent} turn{maxTurnsPerAgent > 1 ? "s" : ""} per agent • {executionMode} mode
          </div>
        </div>
      )}
    </div>
  );
}
