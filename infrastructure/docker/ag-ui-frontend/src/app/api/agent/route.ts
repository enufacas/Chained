/**
 * Agent Interaction API Route
 *
 * Provides endpoints for:
 * 1. Listing available agents (GET)
 * 2. Sending messages to specific agents (POST)
 *
 * Supports @agent-name syntax for direct agent interaction.
 * ALL agent operations call REAL A2A agents deployed on Cloud Run.
 * No simulated responses - all data comes from actual agent execution.
 */

import { NextRequest } from "next/server";

// =============================================================================
// Configuration
// =============================================================================

const isDevelopment = process.env.NODE_ENV === "development";

// Agent URLs - prioritize environment variables, fall back to Cloud Run URLs in production
const AGENT_ENDPOINTS = {
  "research-agent": {
    url: process.env.AGENT_ACADEMIC_RESEARCH_URL || 
      (isDevelopment ? "" : "https://chained-academic-research-sguacxy5gq-uc.a.run.app"),
    displayName: "Academic Research",
    description: "Discovers and analyzes research topics for tech blog content",
    icon: "🔬",
  },
  "seo-agent": {
    url: process.env.AGENT_GOOGLE_TRENDS_URL || 
      (isDevelopment ? "" : "https://chained-google-trends-sguacxy5gq-uc.a.run.app"),
    displayName: "Google Trends",
    description: "Analyzes trends and provides SEO keyword recommendations",
    icon: "📈",
  },
  "writer-agent": {
    url: process.env.AGENT_BLOG_WRITER_URL || 
      (isDevelopment ? "" : "https://chained-blog-writer-sguacxy5gq-uc.a.run.app"),
    displayName: "Blog Writer",
    description: "Writes and publishes engaging blog posts",
    icon: "✍️",
  },
};

// =============================================================================
// Types
// =============================================================================

// Available agents that users can interact with
export interface AgentInfo {
  name: string;
  displayName: string;
  description: string;
  icon: string;
  capabilities: string[];
  examplePrompts: string[];
  url?: string;
}

// A2A Protocol types
interface A2AMessagePart {
  text: string;
}

interface A2AMessage {
  role: string;
  parts: A2AMessagePart[];
}

interface A2ASendMessageRequest {
  message: A2AMessage;
  contextId?: string;
  metadata?: Record<string, unknown>;
}

interface A2AArtifact {
  name: string;
  type: string;
  data: string;
}

interface A2ATaskStatus {
  state: string;
  timestamp: string;
  message?: A2AMessage;
}

interface A2ATask {
  id: string;
  contextId?: string;
  status: A2ATaskStatus;
  artifacts: A2AArtifact[];
}

// =============================================================================
// Agent Registry
// =============================================================================

const AVAILABLE_AGENTS: AgentInfo[] = [
  {
    name: "research-agent",
    displayName: "Academic Research",
    description: "Discovers and analyzes research topics for tech blog content",
    icon: "🔬",
    capabilities: [
      "Topic discovery",
      "Academic paper analysis",
      "Research summarization",
      "Key points extraction",
    ],
    examplePrompts: [
      "@research-agent What are the latest trends in AI?",
      "@research-agent Summarize recent research on embeddings",
      "@research-agent Find papers about vector databases",
    ],
    url: AGENT_ENDPOINTS["research-agent"].url,
  },
  {
    name: "seo-agent",
    displayName: "Google Trends",
    description: "Analyzes trends and provides SEO keyword recommendations",
    icon: "📈",
    capabilities: [
      "Trending keywords",
      "SEO optimization",
      "Topic popularity analysis",
      "Content strategy suggestions",
    ],
    examplePrompts: [
      "@seo-agent Suggest keywords for machine learning",
      "@seo-agent What topics are trending in tech?",
      "@seo-agent Analyze SEO for AI automation",
    ],
    url: AGENT_ENDPOINTS["seo-agent"].url,
  },
  {
    name: "writer-agent",
    displayName: "Blog Writer",
    description: "Writes and publishes engaging blog posts",
    icon: "✍️",
    capabilities: [
      "Blog post writing",
      "Content structuring",
      "Engaging narratives",
      "Technical explanations",
    ],
    examplePrompts: [
      "@writer-agent Draft an introduction on transformers",
      "@writer-agent Write about the benefits of AI",
      "@writer-agent Create an outline for an LLM blog post",
    ],
    url: AGENT_ENDPOINTS["writer-agent"].url,
  },
];

// Parse @agent-name from message
function parseAgentMention(message: string): { agentName: string | null; query: string } {
  // Using [\s\S]* instead of .* with /s flag for broader compatibility
  const mentionMatch = message.match(/^@([\w-]+)\s+([\s\S]*)/);
  if (mentionMatch) {
    return {
      agentName: mentionMatch[1],
      query: mentionMatch[2].trim(),
    };
  }
  return { agentName: null, query: message };
}

// Find agent by name (with fuzzy matching)
function findAgent(name: string): AgentInfo | undefined {
  const normalizedName = name.toLowerCase().replace(/-/g, "").replace(/_/g, "");
  return AVAILABLE_AGENTS.find((agent) => {
    const agentNormalized = agent.name.toLowerCase().replace(/-/g, "").replace(/_/g, "");
    return (
      agentNormalized === normalizedName ||
      agentNormalized.includes(normalizedName) ||
      normalizedName.includes(agentNormalized)
    );
  });
}

/**
 * GET /api/agent
 *
 * Lists all available agents that users can interact with.
 */
export async function GET() {
  return new Response(
    JSON.stringify({
      agents: AVAILABLE_AGENTS,
      usage: {
        syntax: "@agent-name your query here",
        examples: [
          "@research-agent What's trending in AI?",
          "@seo-agent Suggest keywords for machine learning",
          "@writer-agent Draft an introduction on transformers",
        ],
      },
    }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
}

/**
 * POST /api/agent
 *
 * Send a message to a specific agent.
 *
 * Body:
 * - message: The full message (can include @agent-name syntax)
 * - agentName: Optional explicit agent name (overrides @mention in message)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, agentName: explicitAgentName } = body;

    if (!message || typeof message !== "string") {
      return new Response(JSON.stringify({ error: "Message is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Parse the message for @agent-name
    const { agentName: parsedAgentName, query } = parseAgentMention(message);
    const targetAgentName = explicitAgentName || parsedAgentName;

    // If no agent specified, return help
    if (!targetAgentName) {
      return new Response(
        JSON.stringify({
          type: "help",
          message: "Please specify an agent using @agent-name syntax",
          availableAgents: AVAILABLE_AGENTS.map((a) => ({
            mention: `@${a.name}`,
            displayName: a.displayName,
            description: a.description,
          })),
          examples: [
            "@research-agent What's trending in AI?",
            "@seo-agent Suggest keywords for embeddings",
            "@writer-agent Draft a blog intro about LLMs",
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Find the agent
    const agent = findAgent(targetAgentName);
    if (!agent) {
      return new Response(
        JSON.stringify({
          type: "error",
          message: `Agent "${targetAgentName}" not found`,
          availableAgents: AVAILABLE_AGENTS.map((a) => `@${a.name}`),
        }),
        {
          status: 404,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Call the REAL A2A agent - no simulated responses
    const response = await callRealAgent(agent, query);

    return new Response(
      JSON.stringify({
        type: "agent_response",
        agent: {
          name: agent.name,
          displayName: agent.displayName,
          icon: agent.icon,
        },
        query,
        response,
        timestamp: new Date().toISOString(),
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("[Agent API] Error:", error);
    return new Response(JSON.stringify({ error: "Failed to process agent request" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}

/**
 * Call a real A2A agent via the Cloud Run endpoint.
 * No simulated responses - all data comes from actual agent execution.
 */
async function callRealAgent(agent: AgentInfo, query: string): Promise<string> {
  const agentConfig = AGENT_ENDPOINTS[agent.name as keyof typeof AGENT_ENDPOINTS];
  
  if (!agentConfig?.url) {
    return `⚠️ Agent ${agent.displayName} is not configured. Set the appropriate environment variable to enable this agent.

**Required configuration:**
- research-agent: AGENT_ACADEMIC_RESEARCH_URL
- seo-agent: AGENT_GOOGLE_TRENDS_URL
- writer-agent: AGENT_BLOG_WRITER_URL

This agent requires a deployed Cloud Run service to function.`;
  }
  
  try {
    const request: A2ASendMessageRequest = {
      message: {
        role: "user",
        parts: [{ text: query }],
      },
      contextId: `agent-${Date.now()}-${crypto.randomUUID().substring(0, 8)}`,
      metadata: { query },
    };
    
    console.log(`[Agent API] Calling ${agent.name} at ${agentConfig.url}/a2a/tasks`);
    
    const response = await fetch(`${agentConfig.url}/a2a/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      console.error(`[Agent API] ${agent.name} returned ${response.status}`);
      return `⚠️ Agent ${agent.displayName} returned an error (${response.status}). The agent may be temporarily unavailable.`;
    }
    
    const task: A2ATask = await response.json();
    
    console.log(`[Agent API] ${agent.name} task completed:`, {
      taskId: task.id,
      state: task.status.state,
      artifactsCount: task.artifacts?.length || 0,
    });
    
    // Extract response from task
    if (task.status.message?.parts?.length) {
      const responseText = task.status.message.parts.map(p => p.text).join("\n");
      
      // Include artifact data if available
      if (task.artifacts?.length) {
        let response = responseText;
        for (const artifact of task.artifacts) {
          if (artifact.type === "text/markdown" || artifact.type === "text/plain") {
            response += `\n\n---\n\n${artifact.data}`;
          }
        }
        return response;
      }
      
      return responseText;
    }
    
    // Fallback to artifact data
    if (task.artifacts?.length) {
      const textArtifact = task.artifacts.find(a => 
        a.type === "text/markdown" || a.type === "text/plain"
      );
      if (textArtifact) {
        return textArtifact.data;
      }
      
      // Try JSON artifact
      const jsonArtifact = task.artifacts.find(a => a.type === "application/json");
      if (jsonArtifact) {
        try {
          const data = JSON.parse(jsonArtifact.data);
          return `## ${agent.displayName} Response\n\n\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\``;
        } catch {
          return jsonArtifact.data;
        }
      }
    }
    
    return `${agent.displayName} completed the task but returned no response content.`;
    
  } catch (error) {
    console.error(`[Agent API] Error calling ${agent.name}:`, error);
    return `⚠️ Failed to reach ${agent.displayName}. The agent service may be offline or unreachable.

**Error:** ${error instanceof Error ? error.message : String(error)}

Please ensure the agent is deployed and the environment is configured correctly.`;
  }
}
