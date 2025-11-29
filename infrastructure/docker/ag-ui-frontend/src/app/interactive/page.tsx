"use client";

import { useState, useCallback } from "react";
import Link from "next/link";
import { 
  InteractivePipelineChat, 
  ResearchData, 
  TrendsData, 
  BlogData 
} from "@/components/InteractivePipelineChat";

// Agent status type
type AgentStatus = "idle" | "working" | "completed" | "failed";

interface AgentState {
  name: string;
  displayName: string;
  icon: string;
  description: string;
  status: AgentStatus;
  framework: string;
}

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

export default function InteractivePage() {
  const [agents, setAgents] = useState<AgentState[]>(INITIAL_AGENTS);
  const [researchData, setResearchData] = useState<ResearchData | null>(null);
  const [trendsData, setTrendsData] = useState<TrendsData | null>(null);
  const [blogData, setBlogData] = useState<BlogData | null>(null);

  // Callback to update agent status
  const handleAgentActivity = useCallback((agentName: string, status: "working" | "completed" | "failed") => {
    setAgents(prev => prev.map(agent => 
      agent.name.toLowerCase().includes(agentName.toLowerCase()) ||
      agentName.toLowerCase().includes(agent.name.toLowerCase())
        ? { ...agent, status }
        : agent
    ));
  }, []);

  // Reset pipeline
  const resetPipeline = () => {
    setAgents(INITIAL_AGENTS);
    setResearchData(null);
    setTrendsData(null);
    setBlogData(null);
  };

  const getStatusColor = (status: AgentStatus) => {
    switch (status) {
      case "working": return "border-yellow-500/50 bg-yellow-500/10";
      case "completed": return "border-green-500/50 bg-green-500/10";
      case "failed": return "border-red-500/50 bg-red-500/10";
      default: return "border-slate-700 bg-slate-800";
    }
  };

  const getStatusBadge = (status: AgentStatus) => {
    switch (status) {
      case "working": return <span className="px-2 py-0.5 text-xs rounded-full bg-yellow-500/20 text-yellow-400 animate-pulse">Working...</span>;
      case "completed": return <span className="px-2 py-0.5 text-xs rounded-full bg-green-500/20 text-green-400">✓ Complete</span>;
      case "failed": return <span className="px-2 py-0.5 text-xs rounded-full bg-red-500/20 text-red-400">✗ Failed</span>;
      default: return <span className="px-2 py-0.5 text-xs rounded-full bg-slate-700 text-slate-400">Idle</span>;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-xl hover:text-accent-400 transition">
              🏠
            </Link>
            <h1 className="text-xl font-bold text-accent-400">
              🚀 Interactive A2A Pipeline
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={resetPipeline}
              className="px-4 py-2 text-sm rounded-lg bg-slate-700 hover:bg-slate-600 transition"
            >
              🔄 Reset Pipeline
            </button>
            <Link 
              href="/"
              className="px-4 py-2 text-sm rounded-lg bg-slate-700 hover:bg-slate-600 transition"
            >
              📊 View Historical Runs
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Info banner */}
        <div className="bg-gradient-to-r from-accent-500/10 to-primary-500/10 rounded-xl p-4 border border-accent-500/30 mb-6">
          <p className="text-slate-300 text-sm">
            <strong className="text-accent-400">Interactive Mode:</strong> Ask the AI to write a blog post and watch the agents coordinate in real-time.
            The agents use the <strong>A2A Protocol</strong> to communicate and pass data between each other.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left column - Chat */}
          <div className="lg:col-span-1 bg-slate-800 rounded-xl border border-slate-700 overflow-hidden h-[700px]">
            <div className="p-4 border-b border-slate-700 bg-slate-900/50">
              <h2 className="font-semibold text-accent-400">💬 Pipeline Assistant</h2>
              <p className="text-xs text-slate-500 mt-1">
                Ask to write a blog post or research a topic
              </p>
            </div>
            <div className="h-[calc(100%-73px)]">
              <InteractivePipelineChat
                onResearchUpdate={setResearchData}
                onTrendsUpdate={setTrendsData}
                onBlogUpdate={setBlogData}
                onAgentActivity={handleAgentActivity}
              />
            </div>
          </div>

          {/* Right column - Agent Cards & Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Agent Pipeline Visualization */}
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
              <h3 className="text-lg font-semibold text-accent-400 mb-4">
                🤖 Agent Pipeline Status
              </h3>
              <div className="flex items-center justify-between gap-4">
                {agents.map((agent, index) => (
                  <div key={agent.name} className="flex items-center flex-1">
                    <div className={`flex-1 p-4 rounded-xl border transition-all ${getStatusColor(agent.status)}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-2xl">{agent.icon}</span>
                        {getStatusBadge(agent.status)}
                      </div>
                      <h4 className="font-semibold text-white">{agent.displayName}</h4>
                      <p className="text-xs text-slate-400 mt-1">{agent.description}</p>
                      <span className="text-[10px] text-slate-500 mt-2 block">{agent.framework}</span>
                    </div>
                    {index < agents.length - 1 && (
                      <div className="text-2xl text-slate-600 px-4">→</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Results Grid */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Research Results */}
              <div className={`bg-slate-800 rounded-xl border p-6 transition-all ${researchData ? "border-emerald-500/30" : "border-slate-700"}`}>
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">🔬</span>
                  <h3 className="font-semibold text-emerald-400">Research Findings</h3>
                </div>
                {researchData ? (
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Recommended Topic</p>
                      <p className="text-white font-medium">{researchData.findings.recommendedTopic.topic}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Domain</p>
                      <p className="text-slate-300">{researchData.findings.recommendedTopic.domain}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Key Points</p>
                      <ul className="text-sm text-slate-400 list-disc list-inside">
                        {researchData.findings.recommendedTopic.keyPoints.slice(0, 3).map((point, i) => (
                          <li key={i}>{point}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="text-slate-500 text-sm text-center py-8">
                    Waiting for research results...
                  </div>
                )}
              </div>

              {/* Trends Results */}
              <div className={`bg-slate-800 rounded-xl border p-6 transition-all ${trendsData ? "border-blue-500/30" : "border-slate-700"}`}>
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">📈</span>
                  <h3 className="font-semibold text-blue-400">Trends Analysis</h3>
                </div>
                {trendsData ? (
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Topics Analyzed</p>
                      <p className="text-white font-medium">{trendsData.trendsData.topicsAnalyzed}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Trending Keywords</p>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {trendsData.trendsData.trendingKeywords.slice(0, 5).map((kw, i) => (
                          <span key={i} className="px-2 py-1 text-xs rounded-full bg-blue-500/20 text-blue-400">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Recommended Focus</p>
                      <p className="text-slate-300 text-sm">{trendsData.trendsData.recommendedFocus}</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-slate-500 text-sm text-center py-8">
                    Waiting for trends analysis...
                  </div>
                )}
              </div>
            </div>

            {/* Blog Results */}
            <div className={`bg-slate-800 rounded-xl border p-6 transition-all ${blogData ? "border-violet-500/30" : "border-slate-700"}`}>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xl">✍️</span>
                <h3 className="font-semibold text-violet-400">Blog Output</h3>
              </div>
              {blogData ? (
                <div className="space-y-4">
                  <div className="grid md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Title</p>
                      <p className="text-white font-medium">{blogData.blogMetadata?.title || "Untitled"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Word Count</p>
                      <p className="text-slate-300">{blogData.blogMetadata?.wordCount || "N/A"} words</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Read Time</p>
                      <p className="text-slate-300">{blogData.blogMetadata?.readTimeMinutes || "N/A"} min</p>
                    </div>
                  </div>
                  {blogData.blogMetadata?.tags && (
                    <div>
                      <p className="text-xs text-slate-500 uppercase">Tags</p>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {blogData.blogMetadata.tags.map((tag, i) => (
                          <span key={i} className="px-2 py-1 text-xs rounded-full bg-violet-500/20 text-violet-400">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {blogData.deploymentInfo?.url && (
                    <div>
                      <p className="text-xs text-slate-500 uppercase mb-1">Deployment URL</p>
                      <a 
                        href={blogData.deploymentInfo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-accent-400 hover:underline text-sm"
                      >
                        {blogData.deploymentInfo.url} ↗
                      </a>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-slate-500 text-sm text-center py-8">
                  Waiting for blog content...
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="mt-8 text-center text-slate-500 text-sm">
          <p>
            Powered by{" "}
            <a href="https://github.com/CopilotKit/CopilotKit" className="text-accent-400 hover:underline" target="_blank" rel="noopener noreferrer">
              CopilotKit
            </a>
            {" "}+{" "}
            <a href="https://a2a-protocol.org/" className="text-accent-400 hover:underline" target="_blank" rel="noopener noreferrer">
              A2A Protocol
            </a>
            {" "}+{" "}
            <a href="https://google.github.io/adk-docs/" className="text-accent-400 hover:underline" target="_blank" rel="noopener noreferrer">
              Google ADK
            </a>
          </p>
        </div>
      </main>
    </div>
  );
}
