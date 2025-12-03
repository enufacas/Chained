/**
 * Unified AG-UI Frontend - Mobile-First Redesign
 *
 * This is a streamlined, mobile-friendly version that prioritizes:
 * 1. Agent Canvas (primary interaction)
 * 2. Outcomes & Session Progress (combined, with expandable details)
 * 3. Chat (always accessible)
 * 4. Status panels (de-emphasized, at bottom)
 *
 * Key UX Improvements:
 * - Smaller, mobile-friendly buttons
 * - Immediate visual feedback on button press
 * - Slide-in panels for important content
 * - Non-sticky header (scrolls away)
 * - CopilotKit Status & GCP agents moved to bottom
 * - Combined session progress + pipeline outcomes
 *
 * Based on CopilotKit examples: https://github.com/CopilotKit/CopilotKit/tree/main/examples/coagents-starter
 * 
 * IMPORTANT: This UI uses REAL data only - no simulations or fake data.
 * All pipeline data comes from actual A2A agent execution.
 */

"use client";

import { CopilotChat, CopilotPopup } from "@copilotkit/react-ui";
import { useCopilotAction, useCopilotReadable, CopilotKit } from "@copilotkit/react-core";
import { useState, useEffect, useCallback, useRef } from "react";
import { ApiStatus } from "@/types";
import AgentCanvas from "@/components/AgentCanvas";
import RecipeBuilder from "@/components/RecipeBuilder";
import ArtifactPreviewOverlay from "@/components/ArtifactPreviewOverlay";
import ArtifactStream from "@/components/ArtifactStream";
import ErrorObserverStatus from "@/components/ErrorObserverStatus";
import { saveArtifact, saveSession, getStoredSessions, StoredArtifact } from "@/lib/storage";
import ErrorBoundary from "@/components/ErrorBoundary";
import { setupGlobalErrorHandlers } from "@/lib/error-logging";

// =============================================================================
// Types (Local types not shared across components)
// =============================================================================

type AgentStatus = "idle" | "working" | "completed" | "failed";

interface AgentState {
  name: string;
  displayName: string;
  icon: string;
  description: string;
  status: AgentStatus;
  framework: string;
}

// Team-related types for integrated view
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
    taskId?: string;
    contextId?: string;
    message?: string;
    error?: string;
    turnNumber?: number;
    artifacts: Array<{ name: string; type: string; data: string }>;
    // A2A Protocol objects
    agentCard?: object;
    task?: object;
    userMessage?: object;
    agentMessage?: object;
  }>;
  config?: {
    maxTurnsPerAgent: number;
    executionMode: "sequential" | "parallel";
  };
  context?: Record<string, unknown>;
  finalResult?: Record<string, unknown>;
}

// Helper function to check if a session is still active (running or pending)
function isSessionActive(session: TeamSession | null): boolean {
  return session?.status === "running" || session?.status === "pending";
}

// Helper function to check if a session has finished (completed or failed)
function isSessionFinished(session: TeamSession | null): boolean {
  return session?.status === "completed" || session?.status === "failed";
}

const AGENT_ICONS: Record<string, string> = {
  "academic-research": "🔬",
  "google-trends": "📈",
  "blog-writer": "✍️",
  "code-reviewer": "🔍",
  "data-analyst": "📊",
  "image-generator": "🎨",
};

// =============================================================================
// Constants
// =============================================================================

const CHAT_INSTRUCTIONS = `You are an AI assistant helping users with A2A (Agent-to-Agent) workflows and multi-agent team orchestration.

## Your Capabilities

### 1. Workflow Creation
When users want to create/start a new workflow, use the createWorkflow action.
- "Create a workflow on embeddings" → Call createWorkflow with topic="embeddings"
- "Research AI agents" → Call createWorkflow with topic="AI agents"

### 2. Direct Agent Interaction
When users mention @agent-name, use the talkToAgent action.
- "@research-agent what's trending?" → Call talkToAgent
- "@seo-agent suggest keywords" → Call talkToAgent
- "@writer-agent draft intro" → Call talkToAgent

### 3. Workflow Status
When users ask about status, use getWorkflowStatus.
- "What's happening?" / "Workflow status?" → Call getWorkflowStatus

### 4. List Agents
When users ask about available agents, use listAgents.
- "What agents are available?" → Call listAgents

### 5. Analyze ANY Workflow (IMPORTANT!)
You can analyze ANY workflow by topic or ID. Use analyzeWorkflow with the topic name.
All workflows are REAL - created by actual A2A agents with real data.
- "Analyze the fractal art workflow" → Call analyzeWorkflow with workflowIdentifier="fractal art"
- "What steps did the embeddings workflow take?" → Call analyzeWorkflow with workflowIdentifier="embeddings"
- "Break down the previous workflow" → Call analyzeWorkflow (without identifier to get most recent)

### 6. Workflow Data Queries
Query specific data from any workflow:
- "Trending keywords for fractal art" → Call getTrendingKeywords with workflowIdentifier="fractal art"
- "Research summary for embeddings" → Call getResearchSummary with workflowIdentifier="embeddings"

### 7. A2A Artifacts & Protocol Objects
You can access A2A protocol artifacts generated during workflow execution:
- **Agent Cards**: Metadata about each agent (capabilities, skills, protocol version)
- **Tasks**: A2A task objects showing request/response structure
- **Messages**: User and agent messages exchanged during execution
- "Show me the agent card for research-agent" → Call getArtifacts with filter="agent-card"
- "What artifacts were generated?" → Call listWorkflowArtifacts

### 8. Multi-Agent Team Orchestration
Execute team recipes with multiple agents working together:
- "What recipes are available?" → Call listRecipes
- "Execute blog-pipeline recipe for AI safety" → Call executeTeamRecipe
- "Run technical-review recipe to analyze Kubernetes" → Call executeTeamRecipe
- "Check agent registry" → Call getAgentRegistry

Available recipes:
- **blog-pipeline**: Research → Trends → Blog Writing
- **technical-review**: Research → Data Analysis → Writing → Code Review
- **visual-content**: Research → Image Generation → Content Writing
- **data-analysis**: Data Analysis → Visualization → Report Writing

### 9. Canvas & Recipe Awareness
You are aware of the Agent Canvas and Recipe Builder sections. When users build teams or select recipes:
- Reference the selected agents in your responses
- Suggest appropriate recipes based on their goals
- Link to artifacts generated from canvas/recipe runs

For complex workflows with multiple agents, use the Agent Canvas section on the left for visual team building.

Be helpful, concise, and proactive. When users ask about a specific workflow, always use the workflowIdentifier parameter.
Link to generated artifacts when discussing workflow results.`;


// =============================================================================
// Initial Data
// =============================================================================

const INITIAL_AGENTS: AgentState[] = [
  {
    name: "academic-research",
    displayName: "Academic Research",
    icon: "🔬",
    description: "Discovers and analyzes research topics",
    status: "idle",
    framework: "ADK",
  },
  {
    name: "google-trends",
    displayName: "Google Trends",
    icon: "📈",
    description: "Analyzes trends for SEO optimization",
    status: "idle",
    framework: "ADK",
  },
  {
    name: "blog-writer",
    displayName: "Blog Writer",
    icon: "✍️",
    description: "Writes and publishes blog posts",
    status: "idle",
    framework: "ADK",
  },
];

// Note: No SAMPLE_DATA or demo pipelines - all data comes from real A2A agent execution

// =============================================================================
// Compact API Status Checker Component (de-emphasized, collapsible)
// =============================================================================

function CompactApiStatus({ onStatusChange }: { onStatusChange: (status: ApiStatus) => void }) {
  const [status, setStatus] = useState<ApiStatus>({
    checking: true,
    available: false,
    provider: "none",
    model: "",
    timestamp: new Date().toISOString(),
  });
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const checkApi = async () => {
      try {
        const infoRes = await fetch("/api/copilotkit", {
          method: "GET",
          headers: { "Accept": "application/json" },
        });

        if (infoRes.ok) {
          const info = await infoRes.json();
          const newStatus: ApiStatus = {
            checking: false,
            available: info.available === true,
            provider: info.provider || "none",
            model: info.model || "",
            timestamp: new Date().toISOString(),
            error: !info.available ? "No LLM API key configured" : undefined,
          };
          setStatus(newStatus);
          onStatusChange(newStatus);
          return;
        }

        const newStatus: ApiStatus = {
          checking: false,
          available: false,
          provider: "none",
          model: "",
          error: "API check failed",
          timestamp: new Date().toISOString(),
        };
        setStatus(newStatus);
        onStatusChange(newStatus);
      } catch (error) {
        const newStatus: ApiStatus = {
          checking: false,
          available: false,
          provider: "none",
          model: "",
          error: error instanceof Error ? error.message : String(error),
          timestamp: new Date().toISOString(),
        };
        setStatus(newStatus);
        onStatusChange(newStatus);
      }
    };

    checkApi();
    const interval = setInterval(checkApi, 60000);
    return () => clearInterval(interval);
  }, [onStatusChange]);

  const getProviderInfo = (provider: string) => {
    switch (provider) {
      case "vertex-ai": return { emoji: "☁️", name: "Vertex" };
      case "gemini": return { emoji: "🔷", name: "Gemini" };
      case "openai": return { emoji: "🟢", name: "OpenAI" };
      default: return { emoji: "⚪", name: provider };
    }
  };

  const providerInfo = getProviderInfo(status.provider);

  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700/50 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-2 flex items-center justify-between hover:bg-slate-700/30 transition text-xs"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm">🪁</span>
          <span className="text-slate-400">CopilotKit</span>
        </div>
        <div className="flex items-center gap-2">
          {status.checking ? (
            <span className="px-2 py-0.5 rounded-full text-xs bg-slate-700 text-slate-400 animate-pulse">...</span>
          ) : status.available ? (
            <span className="px-2 py-0.5 rounded-full text-xs bg-green-500/20 text-green-400">{providerInfo.emoji} {providerInfo.name}</span>
          ) : (
            <span className="px-2 py-0.5 rounded-full text-xs bg-yellow-500/20 text-yellow-400">⚠️ No Key</span>
          )}
          <span className={`text-slate-500 transition-transform text-xs ${expanded ? "rotate-180" : ""}`}>▼</span>
        </div>
      </button>
      {expanded && (
        <div className="px-3 py-2 border-t border-slate-700/50 text-xs text-slate-500">
          {status.available ? (
            <div className="flex items-center gap-2">
              <span>Model:</span>
              <code className="bg-black/30 px-1.5 py-0.5 rounded text-green-400">{status.model}</code>
            </div>
          ) : (
            <p>Set <code className="bg-black/20 px-1 rounded">USE_VERTEX_AI=true</code>, <code className="bg-black/20 px-1 rounded">GEMINI_API_KEY</code>, or <code className="bg-black/20 px-1 rounded">OPENAI_API_KEY</code></p>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Compact GCP Agent Status Component (de-emphasized)
// =============================================================================

function CompactAgentStatus() {
  const [expanded, setExpanded] = useState(false);
  const [data, setData] = useState<{ healthy: number; total: number; agents: Array<{ displayName: string; icon: string; health: { status: string } }> } | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch("/api/activity");
        if (res.ok) {
          const result = await res.json();
          setData({
            healthy: result.systemStatus?.healthy || 0,
            total: result.systemStatus?.total || 0,
            agents: result.agents || [],
          });
        }
      } catch (e) {
        console.error("Agent status fetch failed:", e);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700/50 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-2 flex items-center justify-between hover:bg-slate-700/30 transition text-xs"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm">☁️</span>
          <span className="text-slate-400">GCP Agents</span>
        </div>
        <div className="flex items-center gap-2">
          {data ? (
            <span className={`px-2 py-0.5 rounded-full text-xs ${
              data.healthy === data.total && data.total > 0
                ? "bg-green-500/20 text-green-400"
                : data.healthy > 0
                ? "bg-yellow-500/20 text-yellow-400"
                : "bg-red-500/20 text-red-400"
            }`}>
              {data.healthy}/{data.total}
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded-full text-xs bg-slate-700 text-slate-400 animate-pulse">...</span>
          )}
          <span className={`text-slate-500 transition-transform text-xs ${expanded ? "rotate-180" : ""}`}>▼</span>
        </div>
      </button>
      {expanded && data && (
        <div className="px-3 py-2 border-t border-slate-700/50 space-y-1 max-h-64 overflow-y-auto">
          {data.agents.map((agent, i) => (
            <div key={i} className="flex items-center gap-2 text-xs text-slate-400">
              <span>{agent.icon}</span>
              <span className="flex-1 truncate">{agent.displayName}</span>
              <span className={agent.health.status === "healthy" ? "text-green-400" : "text-red-400"}>
                {agent.health.status === "healthy" ? "●" : "○"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Unified Outcomes Component (Pipeline + Session Progress combined)
// =============================================================================

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

const PHASE_ICONS: { [key: string]: { icon: string; color: string } } = {
  research: { icon: "🔬", color: "blue" },
  trends: { icon: "📈", color: "green" },
  writing: { icon: "✍️", color: "purple" },
  publishing: { icon: "🚀", color: "orange" },
  complete: { icon: "🎉", color: "emerald" },
};

function UnifiedOutcomes({ 
  activeSession, 
  completedSessions,
  agentIcons,
  onSelectArtifact,
}: { 
  activeSession: TeamSession | null;
  completedSessions: TeamSession[];
  agentIcons: Record<string, string>;
  onSelectArtifact?: (artifact: { name: string; type: string; data: string }) => void;
}) {
  const [pipelines, setPipelines] = useState<PipelineResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedItem, setExpandedItem] = useState<string | null>(null);
  const [expandedStepIndex, setExpandedStepIndex] = useState<number | null>(null);

  const fetchPipelines = useCallback(async () => {
    try {
      const response = await fetch("/api/pipeline?limit=10");
      if (response.ok) {
        const result = await response.json();
        setPipelines(result.pipelines || []);
      }
    } catch (err) {
      console.error("[UnifiedOutcomes] Fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPipelines();
    const interval = setInterval(fetchPipelines, 5000);
    return () => clearInterval(interval);
  }, [fetchPipelines]);

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  const activePipelines = pipelines.filter(p => p.status === "running" || p.status === "pending");
  const completedPipelines = pipelines.filter(p => p.status === "completed");
  const hasActiveWork = activeSession?.status === "running" || activePipelines.length > 0;

  if (loading) {
    return (
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-4 animate-pulse">
        <div className="h-5 bg-slate-700 rounded w-1/3 mb-3"></div>
        <div className="space-y-2">
          <div className="h-12 bg-slate-700 rounded"></div>
          <div className="h-12 bg-slate-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="px-3 py-2 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">📊</span>
          <h3 className="text-sm font-semibold text-white">Progress & Outcomes</h3>
        </div>
        {hasActiveWork && (
          <span className="px-2 py-0.5 text-xs rounded-full bg-blue-500/20 text-blue-400 animate-pulse">
            Active
          </span>
        )}
      </div>

      {/* Active Session Progress - Prominent when running */}
      {activeSession && (
        <div className={`border-b border-slate-700 ${activeSession.status === "running" ? "bg-gradient-to-r from-blue-500/10 to-purple-500/10" : ""}`}>
          <button
            onClick={() => setExpandedItem(expandedItem === `session-${activeSession.id}` ? null : `session-${activeSession.id}`)}
            className="w-full px-3 py-3 flex items-center gap-3 hover:bg-slate-700/30 transition"
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
              activeSession.status === "running" ? "bg-blue-500 animate-pulse" :
              activeSession.status === "completed" ? "bg-green-500" :
              activeSession.status === "failed" ? "bg-red-500" : "bg-slate-600"
            }`}>
              {activeSession.status === "running" ? "⏳" : activeSession.status === "completed" ? "✅" : activeSession.status === "failed" ? "❌" : "⏸️"}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <div className="font-medium text-white text-sm truncate">{activeSession.recipeName}</div>
              <div className="text-xs text-slate-400 truncate">{activeSession.goal}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-400">
                Turn {activeSession.currentTurn}/{activeSession.totalTurns}
              </div>
              <div className="w-16 h-1.5 bg-slate-700 rounded-full mt-1 overflow-hidden">
                <div 
                  className={`h-full transition-all duration-500 ${
                    activeSession.status === "running" ? "bg-blue-500" :
                    activeSession.status === "completed" ? "bg-green-500" : "bg-slate-500"
                  }`}
                  style={{ width: `${(activeSession.currentTurn / activeSession.totalTurns) * 100}%` }}
                />
              </div>
            </div>
            <span className={`text-slate-500 transition-transform text-xs ${expandedItem === `session-${activeSession.id}` ? "rotate-180" : ""}`}>▼</span>
          </button>
          
          {/* Expanded Session Details with Artifact Selection */}
          {expandedItem === `session-${activeSession.id}` && (
            <div className="px-3 pb-3 space-y-2">
              {activeSession.turnResults.map((turn, idx) => {
                const icon = agentIcons[turn.agentId] || "🤖";
                const isStepExpanded = expandedStepIndex === idx;
                const hasArtifacts = turn.artifacts && turn.artifacts.length > 0;
                
                return (
                  <div key={turn.stepIndex} className="space-y-1">
                    {/* Step Header - Click to expand */}
                    <button
                      onClick={() => setExpandedStepIndex(isStepExpanded ? null : idx)}
                      className={`w-full flex items-center gap-2 p-2 rounded text-xs transition ${
                        turn.status === "running" ? "bg-blue-500/10 border border-blue-500/30" :
                        turn.status === "completed" ? "bg-green-500/5 border border-green-500/20" :
                        turn.status === "failed" ? "bg-red-500/5 border border-red-500/20" :
                        "bg-slate-700/30 border border-slate-600/30"
                      } ${hasArtifacts ? "cursor-pointer hover:bg-slate-700/50" : ""}`}
                      disabled={!hasArtifacts && turn.status !== "completed"}
                    >
                      <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
                        turn.status === "running" ? "bg-blue-500 text-white animate-pulse" :
                        turn.status === "completed" ? "bg-green-500 text-white" :
                        turn.status === "failed" ? "bg-red-500 text-white" :
                        "bg-slate-600 text-slate-300"
                      }`}>
                        {idx + 1}
                      </span>
                      <span>{icon}</span>
                      <span className="flex-1 truncate text-slate-300 text-left">{turn.agentName}</span>
                      {turn.status === "running" && <span className="text-blue-400 animate-pulse">Working...</span>}
                      {turn.status === "completed" && <span className="text-green-400">✓</span>}
                      {turn.status === "failed" && <span className="text-red-400">✗</span>}
                      {turn.durationMs && <span className="text-slate-500">{(turn.durationMs / 1000).toFixed(1)}s</span>}
                      {hasArtifacts && (
                        <span className="px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400">
                          {turn.artifacts.length} 📦
                        </span>
                      )}
                      {hasArtifacts && (
                        <span className={`text-slate-500 transition-transform ${isStepExpanded ? "rotate-180" : ""}`}>▼</span>
                      )}
                    </button>
                    
                    {/* Expanded Step Details with Artifacts */}
                    {isStepExpanded && (
                      <div className="ml-7 p-2 rounded bg-slate-800/50 border border-slate-700 space-y-2">
                        {/* Message */}
                        {turn.message && (
                          <div className="text-xs text-slate-400">
                            <span className="text-slate-500 block mb-1">Message:</span>
                            <p className="line-clamp-3">{turn.message}</p>
                          </div>
                        )}
                        
                        {/* Artifacts List */}
                        {hasArtifacts && (
                          <div>
                            <span className="text-[10px] text-slate-500 block mb-1.5">Artifacts:</span>
                            <div className="grid grid-cols-2 gap-1">
                              {turn.artifacts.map((artifact, artifactIdx) => {
                                // Determine icon based on A2A protocol type (vendor MIME types)
                                const icon = artifact.type.includes("a2a.agent-card") ? "🪪" :
                                             artifact.type.includes("a2a.task") ? "📋" :
                                             artifact.type.includes("a2a.message") ? "💬" :
                                             artifact.type.includes("json") ? "📋" :
                                             artifact.type.includes("svg") ? "🖼️" :
                                             artifact.type.includes("markdown") ? "📝" :
                                             artifact.type.includes("html") ? "🌐" : "📄";
                                
                                // Determine type label for A2A artifacts
                                const typeLabel = artifact.type.includes("a2a.agent-card") ? "agent card" :
                                                  artifact.type.includes("a2a.task") ? "task" :
                                                  artifact.type.includes("a2a.message") ? "message" :
                                                  artifact.type.split("/").pop();
                                
                                return (
                                  <button
                                    key={artifactIdx}
                                    onClick={() => onSelectArtifact?.(artifact)}
                                    className="flex items-center gap-1.5 p-1.5 rounded bg-slate-700/50 hover:bg-slate-600/50 text-left transition"
                                  >
                                    <span className="text-sm">{icon}</span>
                                    <div className="flex-1 min-w-0">
                                      <div className="text-[10px] text-white truncate">{artifact.name}</div>
                                      <div className="text-[10px] text-slate-500">{typeLabel}</div>
                                    </div>
                                    <span className="text-[10px] text-purple-400">View</span>
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        )}
                        
                        {/* Error message if failed */}
                        {turn.error && (
                          <div className="text-[10px] text-red-400 bg-red-500/10 p-1.5 rounded">
                            Error: {turn.error}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
              
              {/* Overall Result Section */}
              {activeSession.status === "completed" && activeSession.turnResults.some(t => t.artifacts?.length > 0) && (
                <div className="mt-3 p-2 rounded bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-purple-300">📦 All Session Artifacts</span>
                    <span className="text-[10px] text-slate-500">
                      {activeSession.turnResults.reduce((acc, t) => acc + (t.artifacts?.length || 0), 0)} total
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {activeSession.turnResults.flatMap(t => t.artifacts || []).slice(0, 6).map((artifact, i) => (
                      <button
                        key={i}
                        onClick={() => onSelectArtifact?.(artifact)}
                        className="px-2 py-1 text-[10px] rounded bg-purple-500/20 text-purple-300 hover:bg-purple-500/30 transition"
                      >
                        {artifact.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Completed Team Sessions (history) */}
      {completedSessions.length > 0 && (
        <div className="border-b border-slate-700">
          <div className="px-3 py-2 bg-slate-900/30">
            <h4 className="text-[10px] text-slate-500 uppercase tracking-wider">Recent Team Sessions</h4>
          </div>
          <div className="max-h-48 overflow-y-auto">
            {completedSessions.filter(s => !activeSession || s.id !== activeSession.id).slice(0, 5).map((session) => {
              const isExpanded = expandedItem === `completed-session-${session.id}`;
              return (
                <div key={session.id} className="border-b border-slate-700/30 last:border-b-0">
                  <button
                    onClick={() => setExpandedItem(isExpanded ? null : `completed-session-${session.id}`)}
                    className="w-full px-3 py-2 flex items-center gap-2 hover:bg-slate-700/30 transition text-xs"
                  >
                    <span className={session.status === "completed" ? "text-green-400" : "text-red-400"}>
                      {session.status === "completed" ? "✓" : "✗"}
                    </span>
                    <span className="flex-1 truncate text-slate-300 text-left">{session.recipeName} - {session.goal?.substring(0, 30) || "No goal"}</span>
                    <span className="text-slate-500">{formatTimeAgo(session.updatedAt)}</span>
                    <span className={`text-slate-500 transition-transform ${isExpanded ? "rotate-180" : ""}`}>▼</span>
                  </button>
                  
                  {isExpanded && (
                    <div className="px-3 pb-2 space-y-1 text-xs">
                      <div className="text-slate-400">
                        {session.turnResults.filter(t => t.status === "completed").length}/{session.turnResults.length} steps completed
                      </div>
                      {session.turnResults.some(t => t.artifacts && t.artifacts.length > 0) && (
                        <div className="flex flex-wrap gap-1">
                          {session.turnResults.flatMap(t => t.artifacts || []).slice(0, 4).map((artifact, i) => (
                            <button
                              key={i}
                              onClick={(e) => {
                                e.stopPropagation();
                                onSelectArtifact?.(artifact);
                              }}
                              className="px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 transition"
                            >
                              📦 {artifact.name}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Active Pipelines */}
      {activePipelines.map((pipeline) => {
        const phaseInfo = PHASE_ICONS[pipeline.currentPhase] || { icon: "⏳", color: "slate" };
        const isExpanded = expandedItem === `pipeline-${pipeline.id}`;
        
        return (
          <div key={pipeline.id} className="border-b border-slate-700 bg-yellow-500/5">
            <button
              onClick={() => setExpandedItem(isExpanded ? null : `pipeline-${pipeline.id}`)}
              className="w-full px-3 py-3 flex items-center gap-3 hover:bg-slate-700/30 transition"
            >
              <div className="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center animate-bounce">
                <span className="text-sm">{phaseInfo.icon}</span>
              </div>
              <div className="flex-1 min-w-0 text-left">
                <div className="font-medium text-white text-sm truncate">{pipeline.topic}</div>
                <div className="text-xs text-slate-400">{pipeline.currentPhase} • {pipeline.progress}%</div>
              </div>
              <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-yellow-400 to-orange-400 transition-all duration-500 animate-pulse"
                  style={{ width: `${pipeline.progress}%` }}
                />
              </div>
              <span className={`text-slate-500 transition-transform text-xs ${isExpanded ? "rotate-180" : ""}`}>▼</span>
            </button>
            
            {isExpanded && (
              <div className="px-3 pb-3">
                <div className="flex items-center gap-1 text-xs">
                  {["research", "trends", "writing", "publishing", "complete"].map((phase, idx) => {
                    const phases = ["research", "trends", "writing", "publishing", "complete"];
                    const currentIdx = phases.indexOf(pipeline.currentPhase);
                    const isDone = idx < currentIdx;
                    const isCurrent = idx === currentIdx;
                    return (
                      <div key={phase} className="flex items-center">
                        {idx > 0 && <span className="text-slate-600 mx-1">→</span>}
                        <span className={`${isDone ? "text-green-400" : isCurrent ? "text-yellow-400 animate-pulse" : "text-slate-600"}`}>
                          {PHASE_ICONS[phase]?.icon || "○"}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Completed Pipelines */}
      {completedPipelines.length > 0 ? (
        <div className="max-h-64 overflow-y-auto">
          {completedPipelines.slice(0, 5).map((pipeline) => {
            const isExpanded = expandedItem === `completed-${pipeline.id}`;
            
            return (
              <div key={pipeline.id} className="border-b border-slate-700/50 last:border-b-0">
                <button
                  onClick={() => setExpandedItem(isExpanded ? null : `completed-${pipeline.id}`)}
                  className="w-full px-3 py-2 flex items-center gap-2 hover:bg-slate-700/30 transition text-xs"
                >
                  <span className="text-green-400">✓</span>
                  <span className="flex-1 truncate text-slate-300 text-left">{pipeline.topic}</span>
                  <span className="text-slate-500">{formatTimeAgo(pipeline.updatedAt)}</span>
                  <span className={`text-slate-500 transition-transform ${isExpanded ? "rotate-180" : ""}`}>▼</span>
                </button>
                
                {isExpanded && pipeline.results && (
                  <div className="px-3 pb-2 space-y-1 text-xs">
                    {pipeline.results.blog && (
                      <a
                        href={pipeline.results.blog.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 p-2 rounded bg-accent-500/10 border border-accent-500/20 hover:bg-accent-500/20 transition"
                      >
                        <span>📝</span>
                        <span className="flex-1 truncate text-accent-300">{pipeline.results.blog.title}</span>
                        <span className="text-slate-500">{pipeline.results.blog.wordCount}w</span>
                        <span>↗</span>
                      </a>
                    )}
                    {pipeline.results.research && (
                      <div className="text-slate-400">
                        🔬 {pipeline.results.research.domain} • {pipeline.results.research.keywords?.slice(0, 3).join(", ")}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : !activeSession && activePipelines.length === 0 && (
        <div className="px-3 py-6 text-center text-slate-500 text-xs">
          <span className="text-2xl block mb-2">📭</span>
          No outcomes yet. Start a task to see progress here.
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Chat Panel (works with or without LLM key)
// =============================================================================

function ChatPanel({ apiAvailable }: { apiAvailable: boolean }) {
  if (!apiAvailable) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center">
        <div className="text-6xl mb-4">🔑</div>
        <h3 className="text-lg font-semibold text-white mb-2">Chat Unavailable</h3>
        <p className="text-slate-400 text-sm max-w-xs">
          Configure an LLM API key to enable the AI chat assistant.
        </p>
        <div className="mt-4 p-4 bg-black/30 rounded-lg text-left w-full max-w-xs">
          <p className="text-xs text-slate-500 mb-2">Required environment variables:</p>
          <code className="text-xs text-accent-400 block">USE_VERTEX_AI=true</code>
          <span className="text-xs text-slate-600 block my-1">or</span>
          <code className="text-xs text-accent-400 block">GEMINI_API_KEY=...</code>
          <span className="text-xs text-slate-600 block my-1">or</span>
          <code className="text-xs text-accent-400 block">OPENAI_API_KEY=...</code>
        </div>
      </div>
    );
  }

  return (
    <CopilotChat
      labels={{
        title: "A2A Workflow Assistant",
        initial: `👋 Hi! I'm your A2A workflow assistant.

**🚀 Workflow Creation:**
• "Create a workflow on vector embeddings"
• "Start researching AI agents"

**💬 Talk to Agents:**
• "@research-agent What's trending in AI?"
• "@seo-agent Suggest keywords for ML"
• "@writer-agent Draft an intro on LLMs"

**📊 Workflow Status:**
• "What's the workflow status?"
• "Show active workflows"
• "List available agents"

**📦 A2A Artifacts:**
• "Show me the agent cards"
• "What artifacts were generated?"

**📈 Existing Data:**
• "Analyze this workflow"
• "What are the trending keywords?"
• "Show me the artifacts"`,
      }}
      className="h-full"
    />
  );
}

// =============================================================================
// Main Content (with CopilotKit hooks)
// =============================================================================

function MainContent({
  agents,
  apiStatus,
  onApiStatusChange,
}: {
  agents: AgentState[];
  apiStatus: ApiStatus;
  onApiStatusChange: (status: ApiStatus) => void;
}) {
  // Team Mode state for progressive disclosure
  const [teamModeTab, setTeamModeTab] = useState<"canvas" | "recipe">("canvas");
  const [selectedTeam, setSelectedTeam] = useState<string[]>([]);
  const [activeSession, setActiveSession] = useState<TeamSession | null>(null);
  const [completedSessions, setCompletedSessions] = useState<TeamSession[]>([]);
  const [teamError, setTeamError] = useState<string | null>(null);
  const [chatExpanded, setChatExpanded] = useState(true);
  const [isTeamExecuting, setIsTeamExecuting] = useState(false);
  const [selectedArtifact, setSelectedArtifact] = useState<{ name: string; type: string; data: string } | null>(null);
  const [allSessionArtifacts, setAllSessionArtifacts] = useState<Array<{ name: string; type: string; data: string }>>([]);
  const [resumePollingSessionId, setResumePollingSessionId] = useState<string | null>(null);
  
  // Track saved artifact IDs to avoid duplicates during incremental saving
  const savedArtifactIdsRef = useRef<Set<string>>(new Set());
  
  // Track if we've verified the restored session with backend
  const sessionVerifiedRef = useRef(false);

  // ============================================================================
  // Session State Persistence
  // ============================================================================
  
  // Restore sessions from localStorage on mount
  useEffect(() => {
    const storedSessions = getStoredSessions();
    if (storedSessions.length > 0) {
      // Find any active/running session and restore it
      const activeStoredSession = storedSessions.find(
        s => s.status === "running" || s.status === "pending"
      );
      
      // Get completed sessions (excluding any active one)
      const completedStoredSessions = storedSessions
        .filter(s => s.status === "completed" || s.status === "failed")
        .slice(0, 10)
        .map(s => ({
          id: s.id,
          recipeId: s.metadata?.recipeId as string || "",
          recipeName: s.name,
          goal: s.topic,
          status: s.status as "pending" | "running" | "completed" | "failed",
          currentTurn: s.metadata?.currentTurn as number || 0,
          totalTurns: s.metadata?.totalTurns as number || 0,
          createdAt: s.createdAt,
          updatedAt: s.completedAt || s.createdAt,
          // Restore full turnResults with all A2A protocol objects
          // Backward compatible: defaults to empty array if not present
          turnResults: (s.metadata?.turnResults as Array<{
            stepIndex: number;
            agentId: string;
            agentName: string;
            status: "pending" | "running" | "completed" | "failed" | "skipped";
            startedAt: string;
            completedAt?: string;
            durationMs?: number;
            taskId?: string;
            contextId?: string;
            message?: string;
            error?: string;
            turnNumber?: number;
            artifacts: Array<{ name: string; type: string; data: string }>;
            agentCard?: object;
            task?: object;
            userMessage?: object;
            agentMessage?: object;
          }>) || [],
          config: s.metadata?.config as { maxTurnsPerAgent: number; executionMode: "sequential" | "parallel" } | undefined,
          context: {} as Record<string, unknown>,
          finalResult: s.metadata?.finalResult as Record<string, unknown> | undefined,
        }));
      
      setCompletedSessions(completedStoredSessions);
      
      // If there's an active session, restore it
      // Backend verification happens in a separate effect below
      if (activeStoredSession && activeStoredSession.metadata) {
        const restoredSession: TeamSession = {
          id: activeStoredSession.id,
          recipeId: activeStoredSession.metadata.recipeId as string || "",
          recipeName: activeStoredSession.name,
          goal: activeStoredSession.topic,
          status: activeStoredSession.status as "pending" | "running" | "completed" | "failed",
          currentTurn: activeStoredSession.metadata.currentTurn as number || 0,
          totalTurns: activeStoredSession.metadata.totalTurns as number || 0,
          createdAt: activeStoredSession.createdAt,
          updatedAt: activeStoredSession.completedAt || activeStoredSession.createdAt,
          // Restore full turnResults with all A2A protocol objects
          // Backward compatible: defaults to empty array if not present
          turnResults: (activeStoredSession.metadata.turnResults as Array<{
            stepIndex: number;
            agentId: string;
            agentName: string;
            status: "pending" | "running" | "completed" | "failed" | "skipped";
            startedAt: string;
            completedAt?: string;
            durationMs?: number;
            taskId?: string;
            contextId?: string;
            message?: string;
            error?: string;
            turnNumber?: number;
            artifacts: Array<{ name: string; type: string; data: string }>;
            agentCard?: object;
            task?: object;
            userMessage?: object;
            agentMessage?: object;
          }>) || [],
          config: activeStoredSession.metadata.config as { maxTurnsPerAgent: number; executionMode: "sequential" | "parallel" } | undefined,
          context: {} as Record<string, unknown>,
          finalResult: activeStoredSession.metadata.finalResult as Record<string, unknown> | undefined,
        };
        setActiveSession(restoredSession);
      }
    }
  }, []); // Empty dependency array - only run on mount
  
  // Verify restored session with backend and resume polling if needed
  // This runs after pollSession is defined
  useEffect(() => {
    // Only run verification once on mount
    if (sessionVerifiedRef.current) return;
    if (!activeSession) return;
    
    // Only verify sessions that were restored from localStorage (running or pending)
    // Skip completed/failed sessions as they don't need verification
    if (!isSessionActive(activeSession)) return;
    
    // Mark as verified to prevent re-running
    sessionVerifiedRef.current = true;
    
    // Verify session still exists on backend
    fetch(`/api/team?session=${activeSession.id}`)
      .then(res => {
        if (res.ok) {
          return res.json();
        } else if (res.status === 404) {
          // Session not found on backend (server restart, etc.)
          // Mark local copy as completed to avoid confusion
          console.warn(`Session ${activeSession.id} not found on backend, marking as stale`);
          setActiveSession(prev => {
            if (!prev) return null;
            return {
              ...prev,
              status: "completed",
              currentTurn: prev.totalTurns,
            };
          });
          return null;
        }
        throw new Error(`Backend returned ${res.status}`);
      })
      .then(backendSession => {
        if (backendSession) {
          // Use backend state as source of truth
          setActiveSession(backendSession);
          
          // Signal to resume polling if session is still active on backend
          if (isSessionActive(backendSession)) {
            setIsTeamExecuting(true);
            setResumePollingSessionId(backendSession.id);
          }
        }
      })
      .catch(err => {
        console.warn("Failed to verify session with backend:", err);
        // Keep localStorage state on error, but mark as completed to avoid confusion
        setActiveSession(prev => {
          if (!prev) return null;
          return {
            ...prev,
            status: "completed",
            currentTurn: prev.totalTurns,
          };
        });
      });
  }, [activeSession]); // Only depends on activeSession, not pollSession
  
  // Save active session to localStorage whenever it changes
  useEffect(() => {
    if (activeSession) {
      saveSession({
        id: activeSession.id,
        type: "team",
        name: activeSession.recipeName,
        topic: activeSession.goal,
        status: activeSession.status,
        completedAt: activeSession.status === "completed" || activeSession.status === "failed" 
          ? activeSession.updatedAt 
          : undefined,
        artifacts: [], // Artifacts are saved separately
        metadata: {
          recipeId: activeSession.recipeId,
          currentTurn: activeSession.currentTurn,
          totalTurns: activeSession.totalTurns,
          turnResults: activeSession.turnResults,
          config: activeSession.config,
          finalResult: activeSession.finalResult,
        },
      });
    }
  }, [activeSession]);
  
  // Save completed sessions to localStorage whenever they change
  useEffect(() => {
    completedSessions.forEach(session => {
      saveSession({
        id: session.id,
        type: "team",
        name: session.recipeName,
        topic: session.goal,
        status: session.status,
        completedAt: session.updatedAt,
        artifacts: [], // Artifacts are saved separately
        metadata: {
          recipeId: session.recipeId,
          currentTurn: session.currentTurn,
          totalTurns: session.totalTurns,
          turnResults: session.turnResults,
          config: session.config,
          finalResult: session.finalResult,
        },
      });
    });
  }, [completedSessions]);

  // Handle artifact selection for preview
  const handleSelectArtifact = useCallback((artifact: { name: string; type: string; data: string }) => {
    setSelectedArtifact(artifact);
    // Update all session artifacts for navigation
    if (activeSession) {
      const allArtifacts = activeSession.turnResults.flatMap(t => t.artifacts || []);
      setAllSessionArtifacts(allArtifacts);
    }
  }, [activeSession]);

  // Handle artifact selection from storage (ArtifactStream)
  const handleSelectStoredArtifact = useCallback((artifact: StoredArtifact) => {
    setSelectedArtifact({
      name: artifact.name,
      type: artifact.type,
      data: artifact.data,
    });
  }, []);

  // Poll for session updates
  const pollSession = useCallback(async (sessionId: string) => {
    // Reset saved artifacts tracking for new session
    savedArtifactIdsRef.current = new Set();
    
    const poll = async () => {
      try {
        const response = await fetch(`/api/team?session=${sessionId}`);
        if (response.ok) {
          const session = await response.json();
          setActiveSession(session);
          
          // Save new artifacts incrementally during execution (not just at end)
          if (session.turnResults) {
            for (const turn of session.turnResults) {
              if (turn.artifacts && turn.artifacts.length > 0) {
                for (const artifact of turn.artifacts) {
                  // Create unique ID based on session, step, and artifact name
                  const artifactKey = `${sessionId}-${turn.stepIndex}-${artifact.name}`;
                  
                  if (!savedArtifactIdsRef.current.has(artifactKey)) {
                    savedArtifactIdsRef.current.add(artifactKey);
                    
                    // Determine A2A artifact type from the vendor MIME type (RFC 6838)
                    let a2aType: "agent-card" | "task" | "message" | "artifact" | undefined;
                    if (artifact.type.includes("a2a.agent-card")) {
                      a2aType = "agent-card";
                    } else if (artifact.type.includes("a2a.task")) {
                      a2aType = "task";
                    } else if (artifact.type.includes("a2a.message")) {
                      a2aType = "message";
                    }
                    
                    // Save artifact incrementally with A2A metadata
                    saveArtifact({
                      name: artifact.name,
                      type: artifact.type,
                      data: artifact.data,
                      source: "team",
                      sourceId: session.id,
                      sourceName: session.recipeName || "Custom Team",
                      agentName: turn.agentName || turn.agentId,
                      phase: turn.status,
                      a2aType,
                      taskId: turn.taskId,
                      contextId: turn.contextId,
                    });
                  }
                }
              }
            }
          }
          
          // Continue polling only if session is still active (running or pending)
          // Check status explicitly rather than relying on currentTurn vs totalTurns
          // to avoid race conditions
          if (isSessionActive(session)) {
            setTimeout(poll, 2000);
          } else {
            // Session completed or failed - stop polling and update UI
            setIsTeamExecuting(false);
            if (isSessionFinished(session)) {
              setCompletedSessions(prev => {
                // Avoid duplicates
                if (prev.some(s => s.id === session.id)) return prev;
                // Add new session at the beginning, keep max 10
                return [session, ...prev].slice(0, 10);
              });
            }
          }
        } else if (response.status === 404) {
          // Session not found on backend - likely server restarted
          // Stop polling and mark execution as finished
          console.warn(`Session ${sessionId} not found on backend`);
          setIsTeamExecuting(false);
        }
      } catch (err) {
        console.error("Poll error:", err);
        // On error, stop polling to avoid infinite error loops
        setIsTeamExecuting(false);
      }
    };
    
    setTimeout(poll, 1000); // Start polling after 1 second
  }, []);

  // Resume polling for restored session (triggered by verification effect above)
  useEffect(() => {
    if (resumePollingSessionId) {
      pollSession(resumePollingSessionId);
      setResumePollingSessionId(null); // Clear the signal
    }
  }, [resumePollingSessionId, pollSession]);

  // Handle team changes from canvas
  const handleTeamChange = useCallback((team: string[]) => {
    setSelectedTeam(team);
  }, []);

  // Handle recipe selection
  const handleRecipeSelect = useCallback((recipe: Recipe) => {
    const agentIds = recipe.steps.map((s) => s.agentId);
    setSelectedTeam(agentIds);
  }, []);

  // Execute a team session
  const handleRecipeExecute = useCallback(async (recipeId: string, goal: string) => {
    setTeamError(null);
    setIsTeamExecuting(true);
    
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
      
      if (data.session.status === "running") {
        pollSession(data.session.id);
      } else {
        setIsTeamExecuting(false);
      }
    } catch (err) {
      setTeamError(err instanceof Error ? err.message : "Unknown error");
      setIsTeamExecuting(false);
    }
  }, [pollSession]);

  // Execute custom team from AgentCanvas
  const handleCanvasExecute = useCallback(async (
    goal: string,
    config: { maxTurnsPerAgent: number; executionMode: "sequential" | "parallel" }
  ) => {
    if (selectedTeam.length === 0) {
      setTeamError("Please select at least one agent");
      return;
    }
    
    setTeamError(null);
    setIsTeamExecuting(true);
    
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
      
      if (data.session.status === "running") {
        pollSession(data.session.id);
      } else {
        setIsTeamExecuting(false);
      }
    } catch (err) {
      setTeamError(err instanceof Error ? err.message : "Unknown error");
      setIsTeamExecuting(false);
    }
  }, [selectedTeam, pollSession]);

  // Note: Pipeline data is fetched from the real API - no static data used
  // Use useCopilotReadable to provide context about how to interact with agents
  // Provide context about the current UI state to the chat AI
  useCopilotReadable({
    description: "Instructions for interacting with the A2A workflow system. All data is real - no simulations.",
    value: JSON.stringify({
      note: "All workflow data comes from real A2A agent execution. Use the API to fetch current workflows.",
      agents: agents.map(a => ({ name: a.name, displayName: a.displayName, description: a.description })),
      actions: [
        "Use getWorkflowStatus to see current workflows",
        "Use analyzeWorkflow with workflowIdentifier to analyze any workflow",
        "Use createWorkflow to start new workflow runs with real A2A agents",
        "Use listWorkflowArtifacts to see A2A protocol artifacts (agent cards, tasks, messages)",
      ],
    }, null, 2),
  });

  useCopilotReadable({
    description: "List of A2A agents available in the workflow",
    value: JSON.stringify(agents, null, 2),
  });

  // Provide context about current canvas selection and active session
  useCopilotReadable({
    description: "Current Agent Canvas state - selected team and active workflow session",
    value: JSON.stringify({
      selectedTeam: selectedTeam.length > 0 ? selectedTeam : null,
      selectedTeamCount: selectedTeam.length,
      activeSession: activeSession ? {
        id: activeSession.id,
        recipeName: activeSession.recipeName,
        goal: activeSession.goal,
        status: activeSession.status,
        currentTurn: activeSession.currentTurn,
        totalTurns: activeSession.totalTurns,
        completedSteps: activeSession.turnResults.filter(t => t.status === "completed").length,
        totalArtifacts: activeSession.turnResults.reduce((acc, t) => acc + (t.artifacts?.length || 0), 0),
        a2aArtifactTypes: {
          agentCards: activeSession.turnResults.filter(t => t.agentCard).length,
          tasks: activeSession.turnResults.filter(t => t.task).length,
          messages: activeSession.turnResults.filter(t => t.agentMessage).length,
        }
      } : null,
      completedSessionsCount: completedSessions.length,
    }, null, 2),
  });

  // CopilotKit actions
  useCopilotAction({
    name: "analyzePipeline",
    description: "Analyze a specific pipeline run by topic name or ID, or the most recent pipeline if none specified. Use this when users want to understand what happened in a pipeline.",
    parameters: [
      {
        name: "pipelineIdentifier",
        type: "string",
        description: "Optional: The pipeline topic or ID to analyze. Leave empty to analyze the most recent pipeline.",
        required: false,
      },
    ],
    handler: async ({ pipelineIdentifier }) => {
      try {
        // Fetch all pipelines
        const response = await fetch("/api/pipeline?limit=20");
        if (!response.ok) {
          return `❌ Failed to fetch pipelines: ${response.statusText}`;
        }
        
        const data = await response.json();
        
        if (data.pipelines.length === 0) {
          return `📭 No pipelines found. Create one with "Create a pipeline on [topic]"!`;
        }
        
        // Find the target pipeline
        let targetPipeline = null;
        
        if (pipelineIdentifier && pipelineIdentifier.trim()) {
          const searchTerm = pipelineIdentifier.toLowerCase().trim();
          // Use word boundary matching for more precise search results
          // First try exact ID match, then word-boundary topic match
          targetPipeline = data.pipelines.find((p: { id: string; topic: string }) => {
            // Exact match on ID
            if (p.id.toLowerCase() === searchTerm) return true;
            // Word-boundary match on topic (matches whole words only)
            const topicWords = p.topic.toLowerCase().split(/\s+/);
            const searchWords = searchTerm.split(/\s+/);
            return searchWords.every(sw => 
              topicWords.some(tw => tw === sw || tw.startsWith(sw))
            );
          });
          
          if (!targetPipeline) {
            const availablePipelines = data.pipelines
              .slice(0, 5)
              .map((p: { topic: string; status: string }) => `- "${p.topic}" (${p.status})`)
              .join("\n");
            return `❌ No pipeline found matching "${pipelineIdentifier}"

**Available pipelines:**
${availablePipelines}`;
          }
        } else {
          // Get the most recent completed pipeline, or most recent overall
          targetPipeline = data.pipelines.find((p: { status: string }) => p.status === "completed") || data.pipelines[0];
        }
        
        // Format the pipeline analysis
        const p = targetPipeline;
        const statusEmoji = p.status === "completed" ? "✅" : p.status === "running" ? "🔄" : p.status === "failed" ? "❌" : "⏳";
        const createdAt = new Date(p.createdAt).toLocaleString();
        const updatedAt = new Date(p.updatedAt).toLocaleString();
        
        let analysis = `## 🔍 Pipeline Analysis: "${p.topic}"

**Pipeline ID:** \`${p.id}\`
**Status:** ${statusEmoji} ${p.status.charAt(0).toUpperCase() + p.status.slice(1)}
**Progress:** ${p.progress}%
**Current Phase:** ${p.currentPhase}
**Created:** ${createdAt}
**Last Updated:** ${updatedAt}

### 🔄 Pipeline Lifecycle

`;

        // Show A2A lifecycle stages
        const phases = ["research", "trends", "writing", "publishing", "complete"];
        const currentPhaseIndex = phases.indexOf(p.currentPhase);
        
        const phaseInfo = [
          { phase: "research", icon: "🔬", name: "Research", agent: "Academic Research Agent" },
          { phase: "trends", icon: "📈", name: "SEO Analysis", agent: "Google Trends Agent" },
          { phase: "writing", icon: "✍️", name: "Blog Writing", agent: "Blog Writer Agent" },
          { phase: "publishing", icon: "🚀", name: "Publishing", agent: "Blog Publisher" },
          { phase: "complete", icon: "🎉", name: "Complete", agent: "Pipeline Complete" },
        ];
        
        for (let i = 0; i < phaseInfo.length; i++) {
          const pi = phaseInfo[i];
          const isComplete = i < currentPhaseIndex || p.status === "completed";
          const isCurrent = i === currentPhaseIndex && p.status !== "completed";
          const statusIcon = isComplete ? "✅" : isCurrent ? "⏳" : "⬜";
          analysis += `${statusIcon} **${pi.icon} ${pi.name}** - ${pi.agent}\n`;
        }

        // Show results if available
        if (p.results) {
          analysis += `\n### 📊 Results\n\n`;
          
          if (p.results.research) {
            analysis += `#### 🔬 Research Findings
- **Topic:** ${p.results.research.topic}
- **Domain:** ${p.results.research.domain}
- **Keywords:** ${p.results.research.keywords?.join(", ") || "N/A"}

`;
          }
          
          if (p.results.trends) {
            analysis += `#### 📈 Trends Analysis
- **Trending Keywords:** ${p.results.trends.trendingKeywords?.join(", ") || "N/A"}
- **Recommended Focus:** ${p.results.trends.recommendedFocus || "N/A"}

`;
          }
          
          if (p.results.blog) {
            analysis += `#### ✍️ Blog Output
- **Title:** ${p.results.blog.title}
- **Word Count:** ${p.results.blog.wordCount} words
- **📄 [View Blog Post](${p.results.blog.url})

`;
          }
        }

        return analysis;
      } catch (error) {
        return `❌ Error analyzing pipeline: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  useCopilotAction({
    name: "getTrendingKeywords",
    description: "Get the trending keywords from a specific pipeline's Google Trends analysis",
    parameters: [
      {
        name: "pipelineIdentifier",
        type: "string",
        description: "Optional: The pipeline topic or ID. Leave empty for most recent completed pipeline.",
        required: false,
      },
    ],
    handler: async ({ pipelineIdentifier }) => {
      try {
        const response = await fetch("/api/pipeline?limit=20");
        if (!response.ok) {
          return `❌ Failed to fetch pipelines`;
        }
        
        const data = await response.json();
        
        let pipeline = null;
        if (pipelineIdentifier) {
          const searchTerm = pipelineIdentifier.toLowerCase().trim();
          // Use word boundary matching for more precise results
          pipeline = data.pipelines.find((p: { id: string; topic: string }) => {
            if (p.id.toLowerCase() === searchTerm) return true;
            const topicWords = p.topic.toLowerCase().split(/\s+/);
            const searchWords = searchTerm.split(/\s+/);
            return searchWords.every(sw => 
              topicWords.some(tw => tw === sw || tw.startsWith(sw))
            );
          });
        } else {
          pipeline = data.pipelines.find((p: { status: string; results?: { trends?: object } }) => 
            p.status === "completed" && p.results?.trends
          );
        }
        
        if (!pipeline) {
          return `❌ No pipeline with trends data found.`;
        }
        
        if (!pipeline.results?.trends) {
          return `⏳ Pipeline "${pipeline.topic}" hasn't completed trends analysis yet (${pipeline.progress}% complete)`;
        }
        
        return `## 📈 Trending Keywords: "${pipeline.topic}"

**Trending Keywords:**
${pipeline.results.trends.trendingKeywords?.map((k: string) => `- ${k}`).join("\n") || "No keywords available"}

**Recommended Focus:** ${pipeline.results.trends.recommendedFocus || "N/A"}`;
      } catch (error) {
        return `❌ Error: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  useCopilotAction({
    name: "getResearchSummary",
    description: "Get a summary of the research findings from a specific pipeline",
    parameters: [
      {
        name: "pipelineIdentifier",
        type: "string",
        description: "Optional: The pipeline topic or ID. Leave empty for most recent completed pipeline.",
        required: false,
      },
    ],
    handler: async ({ pipelineIdentifier }) => {
      try {
        const response = await fetch("/api/pipeline?limit=20");
        if (!response.ok) {
          return `❌ Failed to fetch pipelines`;
        }
        
        const data = await response.json();
        
        let pipeline = null;
        if (pipelineIdentifier) {
          const searchTerm = pipelineIdentifier.toLowerCase().trim();
          // Use word boundary matching for more precise results
          pipeline = data.pipelines.find((p: { id: string; topic: string }) => {
            if (p.id.toLowerCase() === searchTerm) return true;
            const topicWords = p.topic.toLowerCase().split(/\s+/);
            const searchWords = searchTerm.split(/\s+/);
            return searchWords.every(sw => 
              topicWords.some(tw => tw === sw || tw.startsWith(sw))
            );
          });
        } else {
          pipeline = data.pipelines.find((p: { status: string; results?: { research?: object } }) => 
            p.status === "completed" && p.results?.research
          );
        }
        
        if (!pipeline) {
          return `❌ No pipeline with research data found.`;
        }
        
        if (!pipeline.results?.research) {
          return `⏳ Pipeline "${pipeline.topic}" hasn't completed research phase yet (${pipeline.progress}% complete)`;
        }
        
        const research = pipeline.results.research;
        return `## 🔬 Research Summary: "${pipeline.topic}"

**Topic:** ${research.topic || pipeline.topic}
**Domain:** ${research.domain || "N/A"}

**Keywords:**
${research.keywords?.map((k: string) => `- ${k}`).join("\n") || "No keywords available"}`;
      } catch (error) {
        return `❌ Error: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  // ============================================================================
  // NEW FEATURE 1: Create Pipeline Action
  // ============================================================================
  useCopilotAction({
    name: "createPipeline",
    description: "Create a new research pipeline on a specific topic. Use this when the user wants to start a new research or blog creation process.",
    parameters: [
      {
        name: "topic",
        type: "string",
        description: "The topic to research and create content about",
        required: true,
      },
    ],
    handler: async ({ topic }) => {
      try {
        const response = await fetch("/api/pipeline", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic }),
        });

        if (!response.ok) {
          return `❌ Failed to create pipeline: ${response.statusText}`;
        }

        const data = await response.json();
        return `## 🚀 Pipeline Created!

**Pipeline ID:** ${data.pipeline.id}
**Topic:** ${data.pipeline.topic}
**Status:** ${data.pipeline.status === "running" ? "🔄 Running" : "⏳ Pending"}
**Phase:** ${data.pipeline.currentPhase}

### What's happening:
1. 🔬 **Research Agent** - Analyzing "${topic}"
2. 📈 **SEO Agent** - Generating keywords
3. ✍️ **Writer Agent** - Preparing blog draft

Use "What's the pipeline status?" to check progress.`;
      } catch (error) {
        return `❌ Error creating pipeline: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  // ============================================================================
  // NEW FEATURE 2: Direct Agent Interaction
  // ============================================================================
  useCopilotAction({
    name: "talkToAgent",
    description: "Send a message directly to a specific agent. Use @agent-name syntax. Available agents: @research-agent, @seo-agent, @writer-agent",
    parameters: [
      {
        name: "message",
        type: "string",
        description: "The message to send, optionally with @agent-name prefix",
        required: true,
      },
    ],
    handler: async ({ message }) => {
      try {
        const response = await fetch("/api/agent", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        });

        if (!response.ok) {
          return `❌ Failed to contact agent: ${response.statusText}`;
        }

        const data = await response.json();
        
        if (data.type === "help") {
          return `## 💡 Agent Interaction Help

Use **@agent-name** syntax to talk directly to an agent:

${data.availableAgents.map((a: { mention: string; displayName: string; description: string }) => 
  `- **${a.mention}** - ${a.displayName}: ${a.description}`
).join("\n")}

### Examples:
${data.examples.map((e: string) => `- "${e}"`).join("\n")}`;
        }

        if (data.type === "error") {
          return `❌ ${data.message}\n\nAvailable agents: ${data.availableAgents.join(", ")}`;
        }

        return `## ${data.agent.icon} ${data.agent.displayName} Response

${data.response}`;
      } catch (error) {
        return `❌ Error contacting agent: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  // ============================================================================
  // NEW FEATURE 3: Real-Time Pipeline Status
  // ============================================================================
  useCopilotAction({
    name: "getPipelineStatus",
    description: "Get the current status of all active pipelines and recent completions",
    parameters: [],
    handler: async () => {
      try {
        const response = await fetch("/api/pipeline?limit=5");
        
        if (!response.ok) {
          return `❌ Failed to get pipeline status: ${response.statusText}`;
        }

        const data = await response.json();
        
        if (data.pipelines.length === 0) {
          return `## 📊 Pipeline Status

No pipelines found. Create one with "Create a pipeline on [topic]"!`;
        }

        const activeCount = data.activePipelinesCount || 0;
        const completedPipelines = data.pipelines.filter((p: { status: string }) => p.status === "completed");
        const runningPipelines = data.pipelines.filter((p: { status: string }) => p.status === "running" || p.status === "pending");

        let statusReport = `## 📊 Pipeline Status

**Active Pipelines:** ${activeCount}

`;

        if (runningPipelines.length > 0) {
          statusReport += `### 🔄 In Progress\n`;
          for (const p of runningPipelines) {
            const progressBar = "█".repeat(Math.floor(p.progress / 10)) + "░".repeat(10 - Math.floor(p.progress / 10));
            statusReport += `- **${p.topic}** [${progressBar}] ${p.progress}%\n  Phase: ${p.currentPhase}\n`;
          }
          statusReport += "\n";
        }

        if (completedPipelines.length > 0) {
          statusReport += `### ✅ Recent Completions\n`;
          for (const p of completedPipelines.slice(0, 3)) {
            const completedTime = new Date(p.updatedAt).toLocaleString();
            statusReport += `- **${p.topic}** - Completed ${completedTime}\n`;
            if (p.results?.blog?.url) {
              statusReport += `  📄 [View Blog](${p.results.blog.url})\n`;
            }
          }
        }

        return statusReport;
      } catch (error) {
        return `❌ Error getting pipeline status: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  // ============================================================================
  // List Available Agents Action
  // ============================================================================
  useCopilotAction({
    name: "listAgents",
    description: "List all available agents that can be interacted with directly",
    parameters: [],
    handler: async () => {
      try {
        const response = await fetch("/api/agent");
        
        if (!response.ok) {
          return `❌ Failed to get agents list`;
        }

        const data = await response.json();
        
        return `## 🤖 Available Agents

You can talk directly to these agents using **@agent-name** syntax:

${data.agents.map((agent: { name: string; displayName: string; icon: string; description: string; capabilities: string[] }) => 
  `### ${agent.icon} ${agent.displayName}
**Mention:** @${agent.name}
${agent.description}

**Capabilities:**
${agent.capabilities.map((c: string) => `- ${c}`).join("\n")}`
).join("\n\n")}

### How to Use
Just type a message like: "@research-agent What's trending in AI?"`;
      } catch (error) {
        return `❌ Error listing agents: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  // ============================================================================
  // Team Features
  // ============================================================================
  useCopilotAction({
    name: "listRecipes",
    description: "List available team recipes (workflows) for multi-agent orchestration",
    parameters: [],
    handler: async () => {
      try {
        const response = await fetch("/api/team");
        
        if (!response.ok) {
          return `❌ Failed to get recipes list`;
        }

        const data = await response.json();
        
        return `## 📋 Available Team Recipes

${data.recipes.map((recipe: { id: string; name: string; description: string; goal: string; steps: Array<{ agentId: string }>; tags: string[] }) => 
  `### ${recipe.name}
**ID:** \`${recipe.id}\`
**Goal:** ${recipe.goal}
**Agents:** ${recipe.steps.map(s => s.agentId).join(" → ")}
**Tags:** ${recipe.tags.join(", ")}
`
).join("\n")}

### How to Use
Try: "Execute blog-pipeline recipe to write about AI safety"
Or visit the [Team Mode](/team) for interactive recipe building.`;
      } catch (error) {
        return `❌ Error listing recipes: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  useCopilotAction({
    name: "executeTeamRecipe",
    description: "Execute a team recipe with multiple agents working together in turn-based orchestration",
    parameters: [
      {
        name: "recipeId",
        type: "string",
        description: "The recipe ID to execute (e.g., blog-pipeline, technical-review, visual-content)",
        required: true,
      },
      {
        name: "goal",
        type: "string",
        description: "The specific goal for this team execution",
        required: true,
      },
    ],
    handler: async ({ recipeId, goal }) => {
      try {
        const response = await fetch("/api/team", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ recipeId, goal }),
        });

        if (!response.ok) {
          const data = await response.json();
          return `❌ Failed to execute recipe: ${data.error || response.statusText}`;
        }

        const data = await response.json();
        const session = data.session;
        
        const statusEmoji = session.status === "completed" ? "✅" : 
                           session.status === "running" ? "🔄" : 
                           session.status === "failed" ? "❌" : "⏳";
        
        return `## 🎭 Team Execution ${statusEmoji}

**Recipe:** ${session.recipeName}
**Goal:** ${session.goal}
**Session ID:** \`${session.id}\`
**Status:** ${session.status}
**Progress:** Turn ${session.currentTurn}/${session.totalTurns}

### Turn Results
${session.turnResults.map((turn: { agentName: string; status: string; message?: string; durationMs?: number }, i: number) => 
  `${i + 1}. **${turn.agentName}** - ${turn.status === "completed" ? "✅" : turn.status === "failed" ? "❌" : "⏳"} ${turn.status}
   ${turn.message ? `   _${turn.message.substring(0, 100)}..._` : ""}
   ${turn.durationMs ? `   ⏱️ ${(turn.durationMs / 1000).toFixed(1)}s` : ""}`
).join("\n")}

View detailed results in [Team Mode](/team)`;
      } catch (error) {
        return `❌ Error executing recipe: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  useCopilotAction({
    name: "getAgentRegistry",
    description: "Get detailed information about all registered agents including health status",
    parameters: [
      {
        name: "includeHealth",
        type: "boolean",
        description: "Whether to include real-time health checks (slower but more accurate)",
        required: false,
      },
    ],
    handler: async ({ includeHealth }) => {
      try {
        const response = await fetch(`/api/registry?health=${includeHealth || false}`);
        
        if (!response.ok) {
          return `❌ Failed to get agent registry`;
        }

        const data = await response.json();
        
        return `## 🤖 Agent Registry

**Total Agents:** ${data.stats.total}
**Configured:** ${data.stats.configured}
${includeHealth ? `**Healthy:** ${data.stats.healthy}` : ""}

### Agents by Category
${data.agents.map((agent: { id: string; displayName: string; icon: string; category: string; configured: boolean; health?: { status: string; responseTimeMs?: number } }) => 
  `- ${agent.icon} **${agent.displayName}** (${agent.category})
  ${agent.configured ? "✅ Configured" : "⚠️ Not configured"}${agent.health ? ` | ${agent.health.status === "healthy" ? "🟢" : "🔴"} ${agent.health.status}${agent.health.responseTimeMs ? ` (${agent.health.responseTimeMs}ms)` : ""}` : ""}`
).join("\n")}

### Categories
${data.stats.categories.map((cat: string) => `- ${cat}`).join("\n")}`;
      } catch (error) {
        return `❌ Error getting registry: ${error instanceof Error ? error.message : "Unknown error"}`;
      }
    },
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header - NOT sticky, scrolls with content */}
      <header className="bg-slate-900/80 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-3 py-2 sm:px-4 sm:py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <a
              href="https://enufacas.github.io/Chained/"
              className="text-xl sm:text-2xl hover:scale-110 transition"
              title="Back to Chained"
            >
              🏠
            </a>
            <div>
              <h1 className="text-base sm:text-lg font-bold text-accent-400">🤖 Chained AG-UI</h1>
              <p className="text-[10px] sm:text-xs text-slate-500 hidden sm:block">A2A Pipeline • CopilotKit v1.8.14</p>
            </div>
          </div>
          <div className="flex items-center gap-2 sm:gap-4">
            <a
              href="https://github.com/CopilotKit/CopilotKit"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[10px] sm:text-xs text-slate-400 hover:text-accent-400 transition hidden sm:inline"
            >
              Docs ↗
            </a>
            <a
              href="https://a2a-protocol.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[10px] sm:text-xs text-slate-400 hover:text-accent-400 transition hidden sm:inline"
            >
              A2A ↗
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-2 sm:px-4 py-3 sm:py-4">
        {/* Mobile-First Layout: Primary content first */}
        <div className="space-y-3 sm:space-y-4 lg:grid lg:grid-cols-3 lg:gap-4 lg:space-y-0">
          
          {/* Column 1: Agent Canvas (Primary - Takes 2 cols on large screens) */}
          <div className="lg:col-span-2 space-y-3 sm:space-y-4">
            {/* Agent Canvas - Main interaction area */}
            <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
              {/* Tab Navigation for Canvas/Recipe */}
              <div className="px-3 py-2 border-b border-slate-700 bg-slate-900/30 flex items-center justify-between">
                <div className="flex gap-1 sm:gap-2">
                  <button
                    onClick={() => setTeamModeTab("canvas")}
                    className={`px-2 py-1 sm:px-3 sm:py-1.5 text-xs font-medium rounded transition-all active:scale-95 ${
                      teamModeTab === "canvas"
                        ? "bg-purple-500 text-white shadow-lg shadow-purple-500/20"
                        : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                    }`}
                  >
                    🎨 Canvas
                  </button>
                  <button
                    onClick={() => setTeamModeTab("recipe")}
                    className={`px-2 py-1 sm:px-3 sm:py-1.5 text-xs font-medium rounded transition-all active:scale-95 ${
                      teamModeTab === "recipe"
                        ? "bg-purple-500 text-white shadow-lg shadow-purple-500/20"
                        : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                    }`}
                  >
                    📋 Recipe
                  </button>
                </div>
                {selectedTeam.length > 0 && (
                  <span className="px-2 py-0.5 text-xs rounded-full bg-purple-500/20 text-purple-400">
                    {selectedTeam.length} agents
                  </span>
                )}
              </div>

              {/* Error Display */}
              {teamError && (
                <div className="mx-2 my-2 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
                  ⚠️ {teamError}
                </div>
              )}

              {/* Tab Content */}
              <div className="p-2 sm:p-3">
                {teamModeTab === "canvas" && (
                  <AgentCanvas
                    onTeamChange={handleTeamChange}
                    onExecute={handleCanvasExecute}
                    initialTeam={selectedTeam}
                    isExecuting={isTeamExecuting}
                  />
                )}
                {teamModeTab === "recipe" && (
                  <RecipeBuilder
                    onRecipeSelect={handleRecipeSelect}
                    onGoalSubmit={handleRecipeExecute}
                    isExecuting={isTeamExecuting}
                  />
                )}
              </div>
            </div>

            {/* Combined Outcomes & Session Progress - Slide-in when active */}
            <div className={`transition-all duration-300 ${activeSession?.status === "running" ? "ring-2 ring-blue-500/50 shadow-lg shadow-blue-500/10" : ""}`}>
              <UnifiedOutcomes 
                activeSession={activeSession}
                completedSessions={completedSessions}
                agentIcons={AGENT_ICONS}
                onSelectArtifact={handleSelectArtifact}
              />
            </div>
            
            {/* Artifact Stream - Shows all persisted artifacts */}
            <ArtifactStream 
              onSelectArtifact={handleSelectStoredArtifact}
              maxItems={15}
            />
          </div>

          {/* Column 2: Chat + Status (Secondary) */}
          <div className="lg:col-span-1 space-y-3 sm:space-y-4">
            {/* Chat Panel - Collapsible on mobile */}
            <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
              <button
                onClick={() => setChatExpanded(!chatExpanded)}
                className="w-full px-3 py-2 flex items-center justify-between hover:bg-slate-700/30 transition lg:cursor-default"
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">💬</span>
                  <span className="text-sm font-semibold text-white">AI Chat</span>
                  {apiStatus.available && (
                    <span className="px-1.5 py-0.5 text-[10px] rounded bg-green-500/20 text-green-400">Ready</span>
                  )}
                </div>
                <span className={`text-slate-500 transition-transform text-xs lg:hidden ${chatExpanded ? "rotate-180" : ""}`}>▼</span>
              </button>
              <div className={`${chatExpanded ? "block" : "hidden"} lg:block`}>
                <div className="h-[300px] sm:h-[400px] lg:h-[500px] border-t border-slate-700">
                  <ChatPanel apiAvailable={apiStatus.available} />
                </div>
              </div>
            </div>

            {/* De-emphasized Status Panels at Bottom */}
            <div className="space-y-2 opacity-75 hover:opacity-100 transition-opacity">
              <p className="text-[10px] text-slate-500 uppercase tracking-wider px-1">System Status</p>
              
              {/* Error Observer Status */}
              <ErrorObserverStatus />
              
              {/* Compact CopilotKit Status */}
              <CompactApiStatus onStatusChange={onApiStatusChange} />
              
              {/* Compact GCP Agents Status */}
              <CompactAgentStatus />
            </div>

            {/* Quick Links - Very compact */}
            <div className="bg-slate-800/50 rounded-lg border border-slate-700/50 p-2">
              <div className="grid grid-cols-2 gap-1 text-[10px] sm:text-xs">
                <a href="https://enufacas.github.io/Chained/a2a-pipeline.html" target="_blank" rel="noopener noreferrer"
                   className="flex items-center gap-1 p-1.5 rounded bg-slate-700/30 hover:bg-slate-700/50 transition text-slate-400 hover:text-white">
                  📐 Docs
                </a>
                <a href="/api/registry?health=true" target="_blank" rel="noopener noreferrer"
                   className="flex items-center gap-1 p-1.5 rounded bg-slate-700/30 hover:bg-slate-700/50 transition text-slate-400 hover:text-white">
                  🤖 API
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Footer - Minimal */}
        <div className="text-center text-slate-600 text-[10px] py-4 mt-4">
          <p>
            <a href="https://github.com/CopilotKit/CopilotKit" className="hover:text-slate-400">CopilotKit</a>
            {" • "}
            <a href="https://a2a-protocol.org/" className="hover:text-slate-400">A2A</a>
            {" • "}
            <a href="https://google.github.io/adk-docs/" className="hover:text-slate-400">ADK</a>
          </p>
        </div>
      </main>

      {/* CopilotKit Popup (alternative chat UI) */}
      {apiStatus.available && (
        <CopilotPopup
          instructions={CHAT_INSTRUCTIONS}
          labels={{
            title: "A2A Pipeline Assistant",
            initial:
              "👋 Hi! I can help with A2A pipelines!\n\n🚀 Try:\n• Create a pipeline on [topic]\n• @research-agent [query]\n• What's the pipeline status?",
          }}
        />
      )}
      
      {/* Artifact Preview Overlay */}
      <ArtifactPreviewOverlay
        artifact={selectedArtifact}
        onClose={() => setSelectedArtifact(null)}
        allArtifacts={allSessionArtifacts}
        onSelectArtifact={(artifact) => setSelectedArtifact(artifact)}
      />
    </div>
  );
}

// =============================================================================
// Home Page (wraps content with CopilotKit if API available)
// =============================================================================

export default function Home() {
  const [agents] = useState<AgentState[]>(INITIAL_AGENTS);
  const [apiStatus, setApiStatus] = useState<ApiStatus>({
    checking: true,
    available: false,
    provider: "none",
    model: "",
    timestamp: new Date().toISOString(),
  });

  // Setup global error handlers on mount
  useEffect(() => {
    setupGlobalErrorHandlers();
  }, []);

  return (
    <ErrorBoundary>
      <CopilotKit runtimeUrl="/api/copilotkit">
        <MainContent
          agents={agents}
          apiStatus={apiStatus}
          onApiStatusChange={setApiStatus}
        />
      </CopilotKit>
    </ErrorBoundary>
  );
}
