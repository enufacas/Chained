/**
 * Simplified AG-UI Frontend - Unified Single Page
 *
 * This is a streamlined version that combines all features into a single page
 * with improved logging, error handling, and robust fallback behavior.
 *
 * Based on CopilotKit examples: https://github.com/CopilotKit/CopilotKit/tree/main/examples/coagents-starter
 */

"use client";

import { CopilotChat, CopilotPopup } from "@copilotkit/react-ui";
import { useCopilotAction, useCopilotReadable, CopilotKit } from "@copilotkit/react-core";
import { useState, useEffect, useCallback } from "react";
import { PipelineData, ApiStatus } from "@/types";
import RealTimeAgentActivity from "@/components/RealTimeAgentActivity";
import PipelineOutcomes from "@/components/PipelineOutcomes";

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

// =============================================================================
// Constants
// =============================================================================

const CHAT_INSTRUCTIONS = `You are an AI assistant helping users with the A2A (Agent-to-Agent) pipeline.

## Your Capabilities

### 1. Pipeline Creation (NEW!)
When users want to create/start a new pipeline, use the createPipeline action.
- "Create a pipeline on embeddings" → Call createPipeline with topic="embeddings"
- "Research AI agents" → Call createPipeline with topic="AI agents"

### 2. Direct Agent Interaction (NEW!)
When users mention @agent-name, use the talkToAgent action.
- "@research-agent what's trending?" → Call talkToAgent
- "@seo-agent suggest keywords" → Call talkToAgent
- "@writer-agent draft intro" → Call talkToAgent

### 3. Pipeline Status (NEW!)
When users ask about status, use getPipelineStatus.
- "What's happening?" / "Pipeline status?" → Call getPipelineStatus

### 4. List Agents
When users ask about available agents, use listAgents.
- "What agents are available?" → Call listAgents

### 5. Existing Pipeline Data
For questions about the current demo pipeline:
- "Analyze this pipeline" → Call analyzePipeline
- "Trending keywords?" → Call getTrendingKeywords
- "Research summary?" → Call getResearchSummary

Be helpful, concise, and proactive. Suggest relevant actions based on context.`;

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

const SAMPLE_DATA: PipelineData = {
  contextId: "blog-pipeline-demo",
  success: true,
  tasksCompleted: 3,
  completedAt: new Date().toISOString(),
  research: {
    taskId: "task-research-demo",
    status: "completed",
    findings: {
      topicsFound: 3,
      recommendedTopic: {
        topic: "Large Language Model Reasoning Capabilities",
        domain: "Artificial Intelligence",
        blogAngle: "How LLM Reasoning is changing the industry",
        keyPoints: [
          "Introduction to LLM reasoning",
          "Current state of research",
          "Practical implications",
          "Future directions",
        ],
        seoKeywords: ["LLM", "reasoning", "AI", "chain-of-thought"],
      },
    },
  },
  trends: {
    taskId: "task-trends-demo",
    status: "completed",
    trendsData: {
      topicsAnalyzed: 5,
      trendingKeywords: ["AI", "LLM", "machine learning", "GPT", "reasoning"],
      recommendedFocus: "LLM reasoning capabilities",
    },
  },
  blog: {
    taskId: "task-blog-demo",
    status: "completed",
    deploymentInfo: {
      url: "https://enufacas.github.io/Chained/blog/llm-reasoning.html",
      status: "published",
    },
    blogMetadata: {
      title: "The Rise of LLM Reasoning: How AI is Learning to Think",
      wordCount: 1847,
      readTimeMinutes: 8,
      tags: ["AI", "LLM", "Reasoning", "Machine Learning"],
    },
  },
};

// =============================================================================
// API Status Checker Component
// =============================================================================

function ApiStatusPanel({ onStatusChange }: { onStatusChange: (status: ApiStatus) => void }) {
  const [status, setStatus] = useState<ApiStatus>({
    checking: true,
    available: false,
    provider: "none",
    model: "",
    timestamp: new Date().toISOString(),
  });
  const [logs, setLogs] = useState<string[]>([]);
  const [showLogs, setShowLogs] = useState(false);

  const addLog = useCallback((message: string) => {
    const timestamp = new Date().toISOString().split("T")[1].split(".")[0];
    setLogs((prev) => [...prev.slice(-19), `[${timestamp}] ${message}`]);
  }, []);

  useEffect(() => {
    const checkApi = async () => {
      addLog("Starting API status check...");

      try {
        // First, try the GET endpoint for provider info
        addLog("Checking /api/copilotkit (GET)...");
        const infoRes = await fetch("/api/copilotkit", {
          method: "GET",
          headers: { "Accept": "application/json" },
        });

        addLog(`GET response: HTTP ${infoRes.status}`);

        if (infoRes.ok) {
          const info = await infoRes.json();
          addLog(`Provider info: ${JSON.stringify(info)}`);

          const newStatus: ApiStatus = {
            checking: false,
            available: info.available === true,
            provider: info.provider || "none",
            model: info.model || "",
            timestamp: new Date().toISOString(),
          };

          if (!info.available) {
            newStatus.error = "No LLM API key configured";
            addLog("⚠️ No LLM API key - chat will be limited");
          } else {
            addLog(`✅ Using ${info.provider} (${info.model})`);
          }

          setStatus(newStatus);
          onStatusChange(newStatus);
          return;
        }

        // Fallback: try a minimal POST to check if API is responsive
        addLog("GET failed, trying POST health check...");
        const postRes = await fetch("/api/copilotkit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: [] }),
        });

        addLog(`POST response: HTTP ${postRes.status}`);

        const newStatus: ApiStatus = {
          checking: false,
          available: postRes.status !== 503,
          provider: postRes.status === 503 ? "none" : "openai", // Assume OpenAI if we can't determine
          model: "",
          error: postRes.status === 503 ? "API returned 503 - No LLM key" : undefined,
          timestamp: new Date().toISOString(),
        };

        setStatus(newStatus);
        onStatusChange(newStatus);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        addLog(`❌ Error: ${errorMsg}`);

        const newStatus: ApiStatus = {
          checking: false,
          available: false,
          provider: "none",
          model: "",
          error: errorMsg,
          timestamp: new Date().toISOString(),
        };

        setStatus(newStatus);
        onStatusChange(newStatus);
      }
    };

    checkApi();
    // Re-check every 60 seconds
    const interval = setInterval(checkApi, 60000);
    return () => clearInterval(interval);
  }, [addLog, onStatusChange]);

  const getStatusBadge = () => {
    if (status.checking) {
      return (
        <span className="px-3 py-1 rounded-full text-sm bg-slate-700 text-slate-300 animate-pulse">
          ⏳ Checking...
        </span>
      );
    }
    if (status.available) {
      // Handle different provider types
      const getProviderInfo = (provider: string) => {
        switch (provider) {
          case "vertex-ai":
            return { emoji: "☁️", name: "Vertex AI" };
          case "gemini":
            return { emoji: "🔷", name: "Gemini" };
          case "openai":
            return { emoji: "🟢", name: "OpenAI" };
          default:
            return { emoji: "✅", name: provider };
        }
      };
      const { emoji, name } = getProviderInfo(status.provider);
      return (
        <span className="px-3 py-1 rounded-full text-sm bg-green-500/20 text-green-400 border border-green-500/30">
          {emoji} {name} Ready
        </span>
      );
    }
    return (
      <span className="px-3 py-1 rounded-full text-sm bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
        ⚠️ No LLM Key
      </span>
    );
  };

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden mb-6">
      {/* Header */}
      <div className="p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🪁</span>
          <div>
            <h3 className="font-semibold text-white">CopilotKit Status</h3>
            <p className="text-xs text-slate-500">v1.8.14 • /api/copilotkit</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {getStatusBadge()}
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="px-3 py-1 text-xs rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 transition"
          >
            {showLogs ? "Hide Logs" : "Show Logs"}
          </button>
        </div>
      </div>

      {/* Debug Logs */}
      {showLogs && (
        <div className="border-t border-slate-700 p-4 bg-black/30">
          <h4 className="text-xs text-slate-500 uppercase tracking-wider mb-2">Debug Logs</h4>
          <div className="font-mono text-xs text-slate-400 space-y-1 max-h-48 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-slate-600 italic">No logs yet...</p>
            ) : (
              logs.map((log, i) => (
                <div key={i} className={log.includes("❌") ? "text-red-400" : log.includes("✅") ? "text-green-400" : ""}>
                  {log}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Error Display */}
      {status.error && !status.checking && (
        <div className="border-t border-yellow-500/30 p-4 bg-yellow-500/5">
          <div className="flex items-start gap-2">
            <span className="text-yellow-400">⚠️</span>
            <div>
              <p className="text-yellow-400 text-sm font-medium">Configuration Issue</p>
              <p className="text-slate-400 text-xs mt-1">{status.error}</p>
              <p className="text-slate-500 text-xs mt-2">
                Set <code className="bg-black/30 px-1 rounded">USE_VERTEX_AI=true</code> (for Cloud Run),{" "}
                <code className="bg-black/30 px-1 rounded">GEMINI_API_KEY</code>, or{" "}
                <code className="bg-black/30 px-1 rounded">OPENAI_API_KEY</code> for AI chat features.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Success Info */}
      {status.available && status.model && (
        <div className="border-t border-green-500/30 p-4 bg-green-500/5">
          <div className="flex items-center gap-4 text-sm">
            <div>
              <span className="text-slate-500">Provider:</span>{" "}
              <span className="text-green-400 font-medium">
                {status.provider === "vertex-ai"
                  ? "Vertex AI"
                  : status.provider === "gemini"
                  ? "Google Gemini"
                  : "OpenAI"}
              </span>
            </div>
            <div>
              <span className="text-slate-500">Model:</span>{" "}
              <code className="bg-black/30 px-2 py-0.5 rounded text-green-400">{status.model}</code>
            </div>
          </div>
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
        title: "A2A Pipeline Assistant",
        initial: `👋 Hi! I'm your A2A pipeline assistant.

**🚀 New! Pipeline Creation:**
• "Create a pipeline on vector embeddings"
• "Start researching AI agents"

**💬 Talk to Agents:**
• "@research-agent What's trending in AI?"
• "@seo-agent Suggest keywords for ML"
• "@writer-agent Draft an intro on LLMs"

**📊 Pipeline Status:**
• "What's the pipeline status?"
• "Show active pipelines"
• "List available agents"

**📈 Existing Data:**
• "Analyze this pipeline"
• "What are the trending keywords?"`,
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
  pipelineData,
  apiStatus,
  onApiStatusChange,
}: {
  agents: AgentState[];
  pipelineData: PipelineData;
  apiStatus: ApiStatus;
  onApiStatusChange: (status: ApiStatus) => void;
}) {
  // Make pipeline data available to CopilotKit
  useCopilotReadable({
    description: "Current A2A pipeline run data including research findings, trends analysis, and blog output",
    value: JSON.stringify(pipelineData, null, 2),
  });

  useCopilotReadable({
    description: "List of agents in the A2A pipeline with their status",
    value: JSON.stringify(agents, null, 2),
  });

  // CopilotKit actions
  useCopilotAction({
    name: "analyzePipeline",
    description: "Analyze the current A2A pipeline run and provide insights",
    parameters: [],
    handler: async () => {
      return `## Pipeline Analysis

**Context ID:** ${pipelineData.contextId}
**Status:** ${pipelineData.success ? "✅ Success" : "❌ Failed"}
**Tasks Completed:** ${pipelineData.tasksCompleted}

### Research Findings
- **Topic:** ${pipelineData.research.findings.recommendedTopic.topic}
- **Domain:** ${pipelineData.research.findings.recommendedTopic.domain}
- **SEO Keywords:** ${pipelineData.research.findings.recommendedTopic.seoKeywords.join(", ")}

### Blog Output
- **Title:** ${pipelineData.blog.blogMetadata.title}
- **Word Count:** ${pipelineData.blog.blogMetadata.wordCount}
- **URL:** ${pipelineData.blog.deploymentInfo.url}`;
    },
  });

  useCopilotAction({
    name: "getTrendingKeywords",
    description: "Get the trending keywords from the Google Trends analysis",
    parameters: [],
    handler: async () => {
      return `**Trending Keywords:**
${pipelineData.trends.trendsData.trendingKeywords.map((k) => `- ${k}`).join("\n")}

**Recommended Focus:** ${pipelineData.trends.trendsData.recommendedFocus}`;
    },
  });

  useCopilotAction({
    name: "getResearchSummary",
    description: "Get a summary of the research findings",
    parameters: [],
    handler: async () => {
      const research = pipelineData.research.findings.recommendedTopic;
      return `## Research Summary

**Topic:** ${research.topic}
**Domain:** ${research.domain}
**Blog Angle:** ${research.blogAngle}

**Key Points:**
${research.keyPoints.map((p) => `- ${p}`).join("\n")}`;
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur border-b border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a
              href="https://enufacas.github.io/Chained/"
              className="text-2xl hover:scale-110 transition"
              title="Back to Chained"
            >
              🏠
            </a>
            <div>
              <h1 className="text-xl font-bold text-accent-400">🤖 Chained AG-UI</h1>
              <p className="text-xs text-slate-500">A2A Pipeline Visualization • CopilotKit v1.8.14</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/CopilotKit/CopilotKit"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-slate-400 hover:text-accent-400 transition"
            >
              CopilotKit Docs ↗
            </a>
            <a
              href="https://a2a-protocol.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-slate-400 hover:text-accent-400 transition"
            >
              A2A Protocol ↗
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Main Layout: Chat + Activity panels side by side */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Left Column - Chat (Always Visible) */}
          <div className="order-2 lg:order-1">
            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden h-[600px] lg:h-[800px] sticky top-24">
              <div className="p-4 border-b border-slate-700 bg-slate-900/50 flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-accent-400">💬 AI Assistant</h2>
                  <p className="text-xs text-slate-500 mt-1">
                    {apiStatus.available
                      ? `Powered by ${
                          apiStatus.provider === "vertex-ai"
                            ? "Vertex AI"
                            : apiStatus.provider === "gemini"
                            ? "Gemini"
                            : "OpenAI"
                        } • Commands update panels in real-time`
                      : "Configure API key to enable"}
                  </p>
                </div>
              </div>
              <div className="h-[calc(100%-65px)]">
                <ChatPanel apiAvailable={apiStatus.available} />
              </div>
            </div>
          </div>

          {/* Right Column - Work & Coordination + Outcomes */}
          <div className="order-1 lg:order-2 space-y-6">
            {/* API Status (compact) */}
            <ApiStatusPanel onStatusChange={onApiStatusChange} />

            {/* Work & Coordination Section */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-xl">⚡</span>
                <h2 className="text-lg font-semibold text-white">Work & Coordination</h2>
                <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full">Live</span>
              </div>
              <RealTimeAgentActivity />
            </div>

            {/* Outcomes Section */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-xl">🎯</span>
                <h2 className="text-lg font-semibold text-white">Outcomes</h2>
                <span className="text-xs text-slate-500">Pipeline results & artifacts</span>
              </div>
              <PipelineOutcomes />
            </div>

            {/* Quick Links (compact) */}
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-4">
              <h3 className="text-sm font-semibold text-slate-400 mb-3">🔗 Quick Links</h3>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <a
                  href="https://enufacas.github.io/Chained/a2a-pipeline.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 p-2 rounded bg-slate-700/50 hover:bg-slate-700 transition"
                >
                  📐 Pipeline Docs
                </a>
                <a
                  href="https://enufacas.github.io/Chained/a2a.html"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 p-2 rounded bg-slate-700/50 hover:bg-slate-700 transition"
                >
                  📘 A2A Docs
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-slate-500 text-sm py-6 mt-6">
          <p>
            Powered by{" "}
            <a href="https://github.com/CopilotKit/CopilotKit" className="text-accent-400 hover:underline">
              CopilotKit
            </a>
            {" • "}
            <a href="https://a2a-protocol.org/" className="text-accent-400 hover:underline">
              A2A Protocol
            </a>
            {" • "}
            <a href="https://google.github.io/adk-docs/" className="text-accent-400 hover:underline">
              Google ADK
            </a>
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
              "👋 Hi! I can help you with the A2A pipeline!\n\n🚀 **New Commands:**\n• Create a pipeline on [topic]\n• @research-agent [query]\n• What's the pipeline status?\n\n📊 **Existing:**\n• Analyze this pipeline\n• What are the trending keywords?",
          }}
        />
      )}
    </div>
  );
}

// =============================================================================
// Home Page (wraps content with CopilotKit if API available)
// =============================================================================

export default function Home() {
  const [agents] = useState<AgentState[]>(INITIAL_AGENTS);
  const [pipelineData] = useState<PipelineData>(SAMPLE_DATA);
  const [apiStatus, setApiStatus] = useState<ApiStatus>({
    checking: true,
    available: false,
    provider: "none",
    model: "",
    timestamp: new Date().toISOString(),
  });

  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <MainContent
        agents={agents}
        pipelineData={pipelineData}
        apiStatus={apiStatus}
        onApiStatusChange={setApiStatus}
      />
    </CopilotKit>
  );
}
