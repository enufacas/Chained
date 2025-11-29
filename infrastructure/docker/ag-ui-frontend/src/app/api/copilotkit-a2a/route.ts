/**
 * CopilotKit API Route with A2A Middleware
 *
 * This connects the frontend to our deployed A2A agents using two protocols:
 * - AG-UI Protocol: Frontend ↔ Orchestrator (via CopilotKit)
 * - A2A Protocol: Orchestrator ↔ Specialized Agents (Research, Trends, Blog)
 *
 * The A2A middleware injects send_message_to_a2a_agent tool into the orchestrator,
 * enabling seamless agent-to-agent communication.
 */

import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { A2AMiddlewareAgent } from "@ag-ui/a2a-middleware";
import { NextRequest } from "next/server";
import { createServiceAdapter, useGemini, useOpenAI } from "@/lib/copilotkit-config";

// Get the ADK API Server URL (which proxies to our A2A agents)
const ADK_API_URL = process.env.NEXT_PUBLIC_ADK_API_URL || "https://chained-adk-api-server-sguacxy5gq-uc.a.run.app";

// Individual agent URLs (deployed on Cloud Run)
const ACADEMIC_RESEARCH_URL = process.env.ACADEMIC_RESEARCH_URL || "https://chained-academic-research-sguacxy5gq-uc.a.run.app";
const GOOGLE_TRENDS_URL = process.env.GOOGLE_TRENDS_URL || "https://chained-google-trends-sguacxy5gq-uc.a.run.app";
const BLOG_WRITER_URL = process.env.BLOG_WRITER_URL || "https://chained-blog-writer-sguacxy5gq-uc.a.run.app";

export async function POST(request: NextRequest) {
  // Create an HTTP agent that connects to our ADK API Server
  // This acts as the orchestrator for our A2A pipeline
  const orchestrationAgent = new HttpAgent({
    url: ADK_API_URL,
  });

  // A2A Middleware: Wraps orchestrator and injects send_message_to_a2a_agent tool
  // This allows the AI to communicate with our deployed A2A agents
  const a2aMiddlewareAgent = new A2AMiddlewareAgent({
    description:
      "Blog writing assistant with 3 specialized A2A agents: Academic Research, Google Trends, and Blog Writer",
    agentUrls: [
      ACADEMIC_RESEARCH_URL,
      GOOGLE_TRENDS_URL,
      BLOG_WRITER_URL,
    ],
    orchestrationAgent,
    instructions: `
      You are a blog writing assistant that orchestrates 3 specialized A2A agents.

      AVAILABLE AGENTS:

      - Academic Research Agent (academic-research): Discovers and analyzes research topics for tech blog content
      - Google Trends Agent (google-trends): Analyzes Google Trends data for SEO optimization
      - Blog Writer Agent (blog-writer): Writes and publishes engaging blog posts

      WORKFLOW STRATEGY (SEQUENTIAL - ONE AT A TIME):

      When the user asks to write a blog post:

      1. Academic Research Agent - First, discover research topics
         - Ask about trending research topics in the domain requested
         - The agent will return findings with recommended topics

      2. Google Trends Agent - Then, analyze trends for SEO
         - Pass the recommended topic from step 1
         - The agent will return trending keywords and SEO recommendations

      3. Blog Writer Agent - Finally, write the blog post
         - Pass the research findings and trends data
         - The agent will write and deploy the blog post

      4. Present the complete result to the user with:
         - Research findings
         - SEO keywords
         - Blog URL if deployed

      CRITICAL RULES:
      - Call agents ONE AT A TIME, wait for results before making next call
      - Pass information from earlier agents to later agents
      - If an agent fails, report the error and continue with available data
      - Synthesize all gathered information in final response
      
      EXAMPLE PROMPTS:
      - "Write a blog post about AI agents"
      - "Research quantum computing and write a blog about it"
      - "What are the trending topics for a tech blog?"
    `,
  });

  // CopilotKit runtime connects frontend to agent system
  // Note: Using type assertion for A2A middleware compatibility
  const runtime = new CopilotRuntime({
    agents: {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      blog_pipeline: a2aMiddlewareAgent as any, // Agent name matches <CopilotKit agent="blog_pipeline">
    },
  });

  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: createServiceAdapter(),
    endpoint: "/api/copilotkit-a2a",
  });

  return handleRequest(request);
}

// GET endpoint to check A2A integration status
export async function GET() {
  const agentStatus = {
    adkApiServer: {
      url: ADK_API_URL,
      available: false,
    },
    agents: {
      academicResearch: {
        url: ACADEMIC_RESEARCH_URL,
        available: false,
      },
      googleTrends: {
        url: GOOGLE_TRENDS_URL,
        available: false,
      },
      blogWriter: {
        url: BLOG_WRITER_URL,
        available: false,
      },
    },
    llmProvider: useGemini ? "gemini" : useOpenAI ? "openai" : "none",
    // Add LLM availability flag so chat can show even if A2A agents are down
    llmAvailable: useGemini || useOpenAI,
  };

  // Run all health checks in parallel with short timeout (2 seconds each)
  // This prevents slow external services from blocking the response
  const healthCheckTimeout = 2000;
  
  const healthChecks = [
    // ADK API Server check
    fetch(`${ADK_API_URL}/health`, { 
      method: "GET",
      signal: AbortSignal.timeout(healthCheckTimeout),
    }).then(res => {
      agentStatus.adkApiServer.available = res.ok;
    }).catch(() => {
      // Agent not available
    }),
    
    // Individual agent checks
    ...Object.entries(agentStatus.agents).map(([key, agent]) =>
      fetch(`${agent.url}/health`, {
        method: "GET",
        signal: AbortSignal.timeout(healthCheckTimeout),
      }).then(res => {
        (agentStatus.agents as Record<string, { url: string; available: boolean }>)[key].available = res.ok;
      }).catch(() => {
        // Agent not available
      })
    ),
  ];

  // Wait for all checks to complete (or timeout)
  await Promise.allSettled(healthChecks);

  return new Response(JSON.stringify(agentStatus), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
