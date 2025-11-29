"use client";

import { CopilotPopup } from "@copilotkit/react-ui";
import { useCopilotAction, useCopilotReadable } from "@copilotkit/react-core";
import { useState } from "react";
import Link from "next/link";
import { AgentCard } from "@/components/AgentCard";
import { PipelineResult } from "@/components/PipelineResult";
import { DataPreview } from "@/components/DataPreview";
import { RunSelector } from "@/components/RunSelector";
import { CopilotKitStatus } from "@/components/CopilotKitStatus";

// Types
export interface Agent {
  name: string;
  id: string;
  icon: string;
  description: string;
  skills: string[];
  status: "pending" | "working" | "completed" | "failed";
  taskId?: string;
  artifacts: { name: string; type: string }[];
}

export interface PipelineRun {
  id: number;
  runNumber: number;
  createdAt: string;
  conclusion: "success" | "failure";
  htmlUrl: string;
}

export interface PipelineData {
  contextId: string;
  success: boolean;
  tasksCompleted: number;
  completedAt: string;
  research: {
    taskId: string;
    status: string;
    findings: {
      topicsFound: number;
      recommendedTopic: {
        topic: string;
        domain: string;
        blogAngle: string;
        keyPoints: string[];
        seoKeywords: string[];
      };
    };
  };
  trends: {
    taskId: string;
    status: string;
    trendsData: {
      topicsAnalyzed: number;
      trendingKeywords: string[];
      recommendedFocus: string;
    };
  };
  blog: {
    taskId: string;
    status: string;
    deploymentInfo: {
      url: string;
      status: string;
    };
    blogMetadata: {
      title: string;
      wordCount: number;
      readTimeMinutes: number;
      tags: string[];
    };
  };
}

// Sample data - will be replaced with real API calls
const SAMPLE_RUNS: PipelineRun[] = [
  {
    id: 19776783774,
    runNumber: 9,
    createdAt: "2025-11-29T01:04:33Z",
    conclusion: "success",
    htmlUrl: "https://github.com/enufacas/Chained/actions/runs/19776783774",
  },
  {
    id: 19776000000,
    runNumber: 8,
    createdAt: "2025-11-28T18:04:33Z",
    conclusion: "success",
    htmlUrl: "https://github.com/enufacas/Chained/actions/runs/19776000000",
  },
  {
    id: 19775000000,
    runNumber: 7,
    createdAt: "2025-11-28T12:04:33Z",
    conclusion: "failure",
    htmlUrl: "https://github.com/enufacas/Chained/actions/runs/19775000000",
  },
];

const SAMPLE_RESULT: PipelineData = {
  contextId: "blog-pipeline-20251129-010433",
  success: true,
  tasksCompleted: 3,
  completedAt: "2025-11-29T01:05:54Z",
  research: {
    taskId: "task-abc123def456",
    status: "completed",
    findings: {
      topicsFound: 3,
      recommendedTopic: {
        topic: "Large Language Model Reasoning Capabilities",
        domain: "Artificial Intelligence",
        blogAngle: "How LLM Reasoning is changing the industry",
        keyPoints: [
          "Introduction to LLM",
          "Current state of research",
          "Practical implications",
          "Future directions",
        ],
        seoKeywords: ["LLM", "reasoning", "AI", "chain-of-thought"],
      },
    },
  },
  trends: {
    taskId: "task-def456ghi789",
    status: "completed",
    trendsData: {
      topicsAnalyzed: 5,
      trendingKeywords: ["AI", "LLM", "machine learning", "GPT", "reasoning"],
      recommendedFocus: "LLM reasoning capabilities",
    },
  },
  blog: {
    taskId: "task-ghi789jkl012",
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

const AGENTS: Agent[] = [
  {
    name: "Academic Research",
    id: "academic-research-agent",
    icon: "🔬",
    description: "Discovers and analyzes academic research topics for blog content.",
    skills: ["discover-topics", "analyze-topic"],
    status: "completed",
    taskId: "task-abc123def456",
    artifacts: [{ name: "research-findings", type: "JSON" }],
  },
  {
    name: "Google Trends",
    id: "google-trends-agent",
    icon: "📈",
    description: "Analyzes Google Trends data for SEO optimization.",
    skills: ["analyze-trends", "get-keywords"],
    status: "completed",
    taskId: "task-def456ghi789",
    artifacts: [{ name: "trends-analysis", type: "JSON" }],
  },
  {
    name: "Blog Writer",
    id: "blog-writer-agent",
    icon: "✍️",
    description: "Writes and publishes engaging blog posts based on research.",
    skills: ["write-blog", "deploy-blog"],
    status: "completed",
    taskId: "task-ghi789jkl012",
    artifacts: [
      { name: "blog-metadata", type: "JSON" },
      { name: "deployment-info", type: "JSON" },
    ],
  },
];

export default function Home() {
  const [selectedRun, setSelectedRun] = useState<number>(SAMPLE_RUNS[0].id);
  // TODO: Replace sample data with API calls to fetch actual pipeline data
  const [pipelineData] = useState<PipelineData>(SAMPLE_RESULT);
  const [agents] = useState<Agent[]>(AGENTS);

  // Make pipeline data available to CopilotKit
  useCopilotReadable({
    description: "Current A2A pipeline run data including research findings, trends analysis, and blog output",
    value: JSON.stringify(pipelineData, null, 2),
  });

  useCopilotReadable({
    description: "List of agents in the A2A pipeline with their status and artifacts",
    value: JSON.stringify(agents, null, 2),
  });

  // CopilotKit action to analyze pipeline
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

  // CopilotKit action to get agent details
  useCopilotAction({
    name: "getAgentDetails",
    description: "Get detailed information about a specific agent in the pipeline",
    parameters: [
      {
        name: "agentName",
        type: "string",
        description: "Name of the agent (research, trends, or blog)",
        required: true,
      },
    ],
    handler: async ({ agentName }) => {
      const agentMap: Record<string, Agent> = {
        research: agents[0],
        trends: agents[1],
        blog: agents[2],
      };
      const agent = agentMap[agentName.toLowerCase()];
      if (!agent) return "Agent not found. Available: research, trends, blog";
      return JSON.stringify(agent, null, 2);
    },
  });

  // CopilotKit action to get trending keywords
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

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-600 to-primary-500 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <a 
            href="https://enufacas.github.io/Chained/" 
            className="text-2xl hover:scale-110 transition"
            title="Back to Chained"
          >
            🏠
          </a>
          <h1 className="text-xl font-bold text-white">🤖 Chained AG-UI</h1>
          <span className="text-primary-100 text-sm bg-primary-700/50 px-2 py-1 rounded">
            Powered by CopilotKit v1.8.14
          </span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-primary-500/15 to-accent-500/10 rounded-2xl p-8 mb-8 border-2 border-primary-500/30 text-center">
          <h1 className="text-3xl font-bold text-primary-400 mb-2">
            🔄 A2A Pipeline Visualization
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto mb-4">
            Visualize agent-to-agent coordination flows using CopilotKit Agentic Generative UI. 
            Click on cards to expand/collapse, switch data tabs, and use the AI chat assistant.
          </p>
          <div className="flex justify-center gap-4 text-sm">
            <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full border border-green-500/30">
              ✅ Interactive UI
            </span>
            <span className="bg-accent-500/20 text-accent-400 px-3 py-1 rounded-full border border-accent-500/30">
              🪁 CopilotKit Hooks
            </span>
            <span className="bg-primary-500/20 text-primary-400 px-3 py-1 rounded-full border border-primary-500/30">
              💬 AI Chat
            </span>
          </div>
        </div>

        {/* CopilotKit Status Panel */}
        <CopilotKitStatus />

        {/* Run Selector */}
        <RunSelector 
          runs={SAMPLE_RUNS} 
          selectedRun={selectedRun} 
          onSelectRun={setSelectedRun} 
        />

        {/* Pipeline Flow - Agent Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {agents.map((agent, index) => (
            <div key={agent.id} className="relative">
              <AgentCard agent={agent} />
              {index < agents.length - 1 && (
                <div className="hidden md:flex absolute top-1/2 -right-4 text-primary-400 text-2xl z-10 transform -translate-y-1/2">
                  →
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Pipeline Result */}
        <PipelineResult data={pipelineData} />

        {/* Data Preview */}
        <DataPreview data={pipelineData} />

        {/* External Links */}
        <div className="flex flex-wrap gap-4 mb-8">
          <Link
            href="/interactive"
            className="flex items-center gap-2 px-4 py-2 bg-accent-500/20 border border-accent-500/50 rounded-lg text-accent-300 hover:bg-accent-500/30 transition font-medium"
          >
            🚀 Interactive Pipeline (NEW)
          </Link>
          <a
            href="https://github.com/enufacas/Chained/actions/workflows/adk-a2a-blog-pipeline.yml"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/30 rounded-lg text-slate-300 hover:bg-primary-500/20 transition"
          >
            ⚙️ View Workflow Runs
          </a>
          <a
            href="https://enufacas.github.io/Chained/a2a-pipeline.html"
            className="flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/30 rounded-lg text-slate-300 hover:bg-primary-500/20 transition"
          >
            📐 Pipeline Architecture
          </a>
          <a
            href="https://enufacas.github.io/Chained/a2a.html"
            className="flex items-center gap-2 px-4 py-2 bg-primary-500/10 border border-primary-500/30 rounded-lg text-slate-300 hover:bg-primary-500/20 transition"
          >
            📘 A2A Documentation
          </a>
        </div>

        {/* CopilotKit Reference */}
        <div className="bg-gradient-to-r from-accent-500/10 to-primary-500/10 rounded-xl p-6 border border-accent-500/30">
          <h4 className="text-accent-400 font-semibold mb-2 flex items-center gap-2">
            🪁 CopilotKit Integration Details
          </h4>
          <p className="text-slate-400 text-sm mb-4">
            This application uses <strong className="text-accent-300">CopilotKit v1.8.14</strong> with the following integration:
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-sm mb-4">
            <div className="bg-black/30 p-3 rounded-lg">
              <p className="text-slate-300 font-medium mb-1">Frontend Components</p>
              <ul className="text-slate-400 space-y-1">
                <li>• <code className="text-accent-400">CopilotKit</code> - Provider wrapper</li>
                <li>• <code className="text-accent-400">CopilotPopup</code> - Chat interface</li>
                <li>• <code className="text-accent-400">useCopilotReadable</code> - Data sharing</li>
                <li>• <code className="text-accent-400">useCopilotAction</code> - Custom actions</li>
              </ul>
            </div>
            <div className="bg-black/30 p-3 rounded-lg">
              <p className="text-slate-300 font-medium mb-1">Backend Runtime</p>
              <ul className="text-slate-400 space-y-1">
                <li>• <code className="text-accent-400">CopilotRuntime</code> - Server runtime</li>
                <li>• <code className="text-accent-400">GoogleGenerativeAIAdapter</code> / <code className="text-accent-400">OpenAIAdapter</code></li>
                <li>• API endpoint: <code className="text-accent-400">/api/copilotkit</code></li>
              </ul>
            </div>
          </div>
          <div className="bg-black/30 p-3 rounded-lg mb-4">
            <p className="text-slate-300 font-medium mb-1">Supported LLM Providers</p>
            <ul className="text-slate-400 space-y-1 text-sm">
              <li>• <strong className="text-blue-400">Google Gemini</strong> - Set <code className="text-accent-400">GOOGLE_API_KEY</code> (preferred)</li>
              <li>• <strong className="text-green-400">OpenAI</strong> - Set <code className="text-accent-400">OPENAI_API_KEY</code> (fallback)</li>
            </ul>
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            <a
              href="https://github.com/CopilotKit/CopilotKit"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent-400 hover:underline"
            >
              CopilotKit GitHub
            </a>
            <span className="text-slate-600">|</span>
            <a
              href="https://docs.copilotkit.ai/adk/generative-ui/agentic"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent-400 hover:underline"
            >
              Agentic UI Docs
            </a>
            <span className="text-slate-600">|</span>
            <a
              href="https://a2a-protocol.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent-400 hover:underline"
            >
              A2A Protocol
            </a>
          </div>
        </div>
      </main>

      {/* CopilotKit Chat Popup */}
      <CopilotPopup
        instructions={`You are an AI assistant helping users understand the A2A (Agent-to-Agent) pipeline visualization. 
        
You have access to:
- Pipeline data including research findings, trends analysis, and blog output
- Agent information including their status, tasks, and artifacts
- Actions to analyze the pipeline and get specific details

Be helpful, concise, and informative. Use markdown formatting for clear responses.`}
        labels={{
          title: "A2A Pipeline Assistant",
          initial: "👋 Hi! I can help you understand the A2A pipeline. Try asking:\n\n• Analyze this pipeline run\n• What are the trending keywords?\n• Tell me about the blog agent",
        }}
      />
    </div>
  );
}
