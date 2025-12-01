/**
 * Team Page - Multi-Agent Team Orchestration UI
 *
 * Interactive page for:
 * - Selecting agents to form a team
 * - Choosing and executing recipes
 * - Viewing real-time team execution
 * - Analyzing session results
 */

"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import AgentCanvas from "@/components/AgentCanvas";
import RecipeBuilder from "@/components/RecipeBuilder";
import TeamVisualization from "@/components/TeamVisualization";
import TurnIndicator from "@/components/TurnIndicator";

interface Recipe {
  id: string;
  name: string;
  description: string;
  goal: string;
  steps: Array<{
    agentId: string;
    instruction: string;
    required: boolean;
    dependsOn: string[];
  }>;
  tags: string[];
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
  turnResults: Array<{
    stepIndex: number;
    agentId: string;
    agentName: string;
    status: "pending" | "running" | "completed" | "failed" | "skipped";
    startedAt: string;
    completedAt?: string;
    durationMs?: number;
    message?: string;
    error?: string;
    artifacts: Array<{ name: string; type: string; data: string }>;
  }>;
}

const AGENT_ICONS: Record<string, string> = {
  "academic-research": "🔬",
  "google-trends": "📈",
  "blog-writer": "✍️",
  "code-reviewer": "🔍",
  "data-analyst": "📊",
  "image-generator": "🎨",
};

export default function TeamPage() {
  const [activeTab, setActiveTab] = useState<"canvas" | "recipe" | "session">("recipe");
  const [selectedTeam, setSelectedTeam] = useState<string[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [activeSession, setActiveSession] = useState<TeamSession | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Handle team changes from canvas
  const handleTeamChange = useCallback((team: string[]) => {
    setSelectedTeam(team);
  }, []);
  
  // Handle recipe selection
  const handleRecipeSelect = useCallback((recipe: Recipe) => {
    setSelectedRecipe(recipe);
    // Extract agent IDs from recipe steps
    const agentIds = recipe.steps.map((s) => s.agentId);
    setSelectedTeam(agentIds);
  }, []);
  
  // Poll for session updates
  const pollSession = useCallback(async (sessionId: string) => {
    const poll = async () => {
      try {
        const response = await fetch(`/api/team?session=${sessionId}`);
        if (response.ok) {
          const session = await response.json();
          setActiveSession(session);
          
          if (session.status === "running") {
            setTimeout(poll, 2000);
          }
        }
      } catch (err) {
        console.error("Poll error:", err);
      }
    };
    
    setTimeout(poll, 2000);
  }, []);
  
  // Execute a team session
  const handleExecute = useCallback(async (recipeId: string, goal: string) => {
    setError(null);
    setActiveTab("session");
    
    try {
      const response = await fetch("/api/team", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipeId, goal }),
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Failed to execute recipe");
      }
      
      const data = await response.json();
      setActiveSession(data.session);
      
      // Poll for updates while running
      if (data.session.status === "running") {
        pollSession(data.session.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }, [pollSession]);
  
  // Execute custom team from AgentCanvas
  const handleCanvasExecute = useCallback(async (
    goal: string,
    config: { maxTurnsPerAgent: number; executionMode: "sequential" | "parallel" }
  ) => {
    if (selectedTeam.length === 0) {
      setError("Please select at least one agent");
      return;
    }
    
    setError(null);
    setActiveTab("session");
    
    try {
      const response = await fetch("/api/team", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agentIds: selectedTeam,
          goal,
          config,
        }),
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Failed to execute team");
      }
      
      const data = await response.json();
      setActiveSession(data.session);
      
      // Poll for updates while running
      if (data.session.status === "running") {
        pollSession(data.session.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }, [selectedTeam, pollSession]);
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur border-b border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="text-2xl hover:scale-110 transition"
              title="Back to Main"
            >
              🏠
            </Link>
            <div>
              <h1 className="text-xl font-bold text-accent-400">🎭 Agent Team</h1>
              <p className="text-xs text-slate-500">Multi-Agent Orchestration</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-400">
              {selectedTeam.length} agents selected
            </span>
            <Link
              href="/"
              className="px-4 py-2 text-sm rounded-lg bg-slate-700 hover:bg-slate-600 transition"
            >
              ← Back to Chat
            </Link>
          </div>
        </div>
      </header>
      
      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex gap-2 bg-slate-800/50 p-1 rounded-xl w-fit">
          <button
            onClick={() => setActiveTab("canvas")}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
              activeTab === "canvas"
                ? "bg-slate-700 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            🎨 Agent Canvas
          </button>
          <button
            onClick={() => setActiveTab("recipe")}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
              activeTab === "recipe"
                ? "bg-slate-700 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            📋 Recipe Builder
          </button>
          <button
            onClick={() => setActiveTab("session")}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
              activeTab === "session"
                ? "bg-slate-700 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            🎭 Session View
          </button>
        </div>
      </div>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 pb-8">
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
            <p className="text-red-400">⚠️ {error}</p>
          </div>
        )}
        
        {activeTab === "canvas" && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AgentCanvas
                onTeamChange={handleTeamChange}
                onExecute={handleCanvasExecute}
                initialTeam={selectedTeam}
              />
            </div>
            <div>
              <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">
                  📋 Selected Team
                </h3>
                {selectedTeam.length === 0 ? (
                  <p className="text-slate-400 text-sm">
                    Click on agents in the canvas to build your team
                  </p>
                ) : (
                  <div className="space-y-3">
                    {selectedTeam.map((agentId, index) => (
                      <div
                        key={agentId}
                        className="flex items-center gap-3 p-3 bg-slate-700/50 rounded-lg"
                      >
                        <span className="w-6 h-6 rounded-full bg-purple-500 text-white text-xs flex items-center justify-center font-bold">
                          {index + 1}
                        </span>
                        <span className="text-xl">{AGENT_ICONS[agentId] || "🤖"}</span>
                        <span className="text-white">{agentId}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        
        {activeTab === "recipe" && (
          <div className="grid lg:grid-cols-2 gap-6">
            <RecipeBuilder
              onRecipeSelect={handleRecipeSelect}
              onGoalSubmit={handleExecute}
            />
            <div className="space-y-6">
              {/* Recipe Preview */}
              {selectedRecipe && (
                <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">
                    🔍 Recipe Preview
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <span className="text-slate-500 text-sm">Goal:</span>
                      <p className="text-white">{selectedRecipe.goal}</p>
                    </div>
                    <div>
                      <span className="text-slate-500 text-sm">Steps:</span>
                      <div className="mt-2 flex items-center gap-2 flex-wrap">
                        {selectedRecipe.steps.map((step, i) => (
                          <div key={i} className="flex items-center">
                            {i > 0 && <span className="text-slate-600 mx-1">→</span>}
                            <div className="flex items-center gap-1 px-2 py-1 bg-slate-700/50 rounded">
                              <span>{AGENT_ICONS[step.agentId] || "🤖"}</span>
                              <span className="text-sm text-white">{step.agentId}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Recent Sessions */}
              <RecentSessions
                onSelectSession={(session) => {
                  setActiveSession(session);
                  setActiveTab("session");
                }}
              />
            </div>
          </div>
        )}
        
        {activeTab === "session" && (
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              {activeSession ? (
                <TeamVisualization sessionId={activeSession.id} />
              ) : (
                <div className="bg-slate-800 rounded-xl border border-slate-700 p-12 text-center">
                  <span className="text-5xl">🎭</span>
                  <h3 className="text-lg font-medium text-white mt-4">
                    No Active Session
                  </h3>
                  <p className="text-slate-400 mt-2">
                    Select a recipe and execute it to see the team in action
                  </p>
                  <button
                    onClick={() => setActiveTab("recipe")}
                    className="mt-6 px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition"
                  >
                    📋 Choose a Recipe
                  </button>
                </div>
              )}
            </div>
            <div>
              {activeSession && (
                <TurnIndicator
                  currentTurn={activeSession.currentTurn}
                  totalTurns={activeSession.totalTurns}
                  turnResults={activeSession.turnResults}
                  agentIcons={AGENT_ICONS}
                  sessionStatus={activeSession.status}
                />
              )}
            </div>
          </div>
        )}
      </main>
      
      {/* Footer */}
      <footer className="text-center text-slate-500 text-sm py-6">
        <p>
          🎭 Multi-Agent Team Orchestration •{" "}
          <Link href="/" className="text-purple-400 hover:underline">
            Back to Main UI
          </Link>
        </p>
      </footer>
    </div>
  );
}

// Recent Sessions Component
function RecentSessions({
  onSelectSession,
}: {
  onSelectSession: (session: TeamSession) => void;
}) {
  const [sessions, setSessions] = useState<TeamSession[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Fetch recent sessions
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await fetch("/api/team?sessions=true");
        if (response.ok) {
          const data = await response.json();
          setSessions(data.sessions || []);
        }
      } catch (err) {
        console.error("Failed to fetch sessions:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSessions();
  }, []);
  
  if (loading) {
    return (
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 animate-pulse">
        <div className="h-4 bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-12 bg-slate-700 rounded"></div>
          <div className="h-12 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">📜 Recent Sessions</h3>
      {sessions.length === 0 ? (
        <p className="text-slate-400 text-sm">No sessions yet. Execute a recipe to start!</p>
      ) : (
        <div className="space-y-2">
          {sessions.slice(0, 5).map((session) => (
            <button
              key={session.id}
              onClick={() => onSelectSession(session)}
              className="w-full p-3 rounded-lg border border-slate-700 hover:border-slate-600 bg-slate-800/50 text-left transition"
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-medium text-white">{session.recipeName}</span>
                  <p className="text-xs text-slate-400 truncate">{session.goal}</p>
                </div>
                <span
                  className={`px-2 py-0.5 text-xs rounded-full ${
                    session.status === "completed"
                      ? "bg-green-500/20 text-green-400"
                      : session.status === "running"
                      ? "bg-blue-500/20 text-blue-400"
                      : session.status === "failed"
                      ? "bg-red-500/20 text-red-400"
                      : "bg-slate-500/20 text-slate-400"
                  }`}
                >
                  {session.status}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
