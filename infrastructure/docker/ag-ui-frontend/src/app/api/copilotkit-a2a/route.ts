/**
 * CopilotKit API Route with A2A Middleware
 *
 * Sets up the connection between:
 * - Frontend (CopilotKit) → A2A Middleware → Orchestrator → A2A Agents
 *
 * KEY CONCEPTS:
 * - AG-UI Protocol: Agent-UI communication (CopilotKit ↔ Orchestrator)
 * - A2A Protocol: Agent-to-agent communication (Orchestrator ↔ Specialized Agents)
 * - A2A Middleware: Injects send_message_to_a2a_agent tool to bridge AG-UI and A2A
 */

import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { A2AMiddlewareAgent } from "@ag-ui/a2a-middleware";
import { NextRequest } from "next/server";

// Get the ADK API Server URL (which proxies to our A2A agents)
const ADK_API_URL = process.env.NEXT_PUBLIC_ADK_API_URL || "https://chained-adk-api-server-sguacxy5gq-uc.a.run.app";

// Individual agent URLs (deployed on Cloud Run)
const ACADEMIC_RESEARCH_URL = process.env.ACADEMIC_RESEARCH_URL || "https://chained-academic-research-sguacxy5gq-uc.a.run.app";
const GOOGLE_TRENDS_URL = process.env.GOOGLE_TRENDS_URL || "https://chained-google-trends-sguacxy5gq-uc.a.run.app";
const BLOG_WRITER_URL = process.env.BLOG_WRITER_URL || "https://chained-blog-writer-sguacxy5gq-uc.a.run.app";

export async function POST(request: NextRequest) {
  // STEP 1: Create an HTTP agent that connects to our ADK API Server
  // This acts as the orchestrator for our A2A pipeline
  const orchestrationAgent = new HttpAgent({
    url: ADK_API_URL,
  });

  // STEP 2: Create A2A Middleware Agent
  // This bridges AG-UI and A2A protocols by:
  // 1. Wrapping the orchestrator
  // 2. Registering all A2A agents
  // 3. Injecting send_message_to_a2a_agent tool
  // 4. Routing messages between orchestrator and A2A agents
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

  // STEP 3: Create CopilotKit Runtime
  const runtime = new CopilotRuntime({
    agents: {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      blog_pipeline: a2aMiddlewareAgent as any, // Must match frontend: <CopilotKit agent="blog_pipeline">
    },
  });

  // STEP 4: Set up Next.js endpoint handler
  // When using A2A middleware, use ExperimentalEmptyAdapter
  // The orchestrator (ADK API Server) handles all LLM communication
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: new ExperimentalEmptyAdapter(),
    endpoint: "/api/copilotkit-a2a",
  });

  return handleRequest(request);
}

// GET endpoint to check A2A integration status (for debugging)
export async function GET() {
  return new Response(JSON.stringify({
    adkApiServer: ADK_API_URL,
    agents: {
      academicResearch: ACADEMIC_RESEARCH_URL,
      googleTrends: GOOGLE_TRENDS_URL,
      blogWriter: BLOG_WRITER_URL,
    },
  }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
