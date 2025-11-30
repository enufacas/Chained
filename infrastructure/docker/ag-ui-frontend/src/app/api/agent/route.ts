/**
 * Agent Interaction API Route
 *
 * Provides endpoints for:
 * 1. Listing available agents (GET)
 * 2. Sending messages to specific agents (POST)
 *
 * Supports @agent-name syntax for direct agent interaction.
 */

import { NextRequest } from "next/server";

// Available agents that users can interact with
export interface AgentInfo {
  name: string;
  displayName: string;
  description: string;
  icon: string;
  capabilities: string[];
  examplePrompts: string[];
  serviceUrl?: string;
}

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
    serviceUrl: process.env.ACADEMIC_RESEARCH_URL || "https://chained-academic-research-sguacxy5gq-uc.a.run.app",
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
    serviceUrl: process.env.GOOGLE_TRENDS_URL || "https://chained-google-trends-sguacxy5gq-uc.a.run.app",
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
    serviceUrl: process.env.BLOG_WRITER_URL || "https://chained-blog-writer-sguacxy5gq-uc.a.run.app",
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

    // Generate a simulated response based on the agent type
    const response = await generateAgentResponse(agent, query);

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
 * Generate a response from the specified agent.
 * In production, this would call the actual A2A agent service.
 * For now, returns contextual simulated responses.
 */
async function generateAgentResponse(agent: AgentInfo, query: string): Promise<string> {
  const queryLower = query.toLowerCase();

  switch (agent.name) {
    case "research-agent": {
      if (queryLower.includes("trend") || queryLower.includes("latest")) {
        return `## Research Findings

Based on my analysis, here are the current trending topics:

1. **Large Language Models (LLMs)** - Reasoning capabilities and chain-of-thought prompting
2. **AI Agents** - Autonomous task execution and multi-agent coordination
3. **Vector Databases** - Embedding storage and semantic search
4. **RAG Systems** - Retrieval-augmented generation architectures

### Recommended Deep Dive
The intersection of LLMs and agent systems is particularly active, with research focusing on:
- Tool use and function calling
- Multi-step reasoning
- Self-reflection and error correction`;
      }
      
      return `## Research Summary: ${query}

I've analyzed recent academic papers and industry reports on this topic.

### Key Findings
- This is an active area of research with significant developments
- Multiple approaches exist, each with trade-offs
- Industry adoption is accelerating

### Recommended Reading
1. Recent survey papers on the topic
2. Foundational research from leading institutions
3. Industry case studies and benchmarks

Would you like me to dive deeper into any specific aspect?`;
    }

    case "seo-agent": {
      if (queryLower.includes("keyword")) {
        return `## SEO Keyword Analysis

### Primary Keywords
- ${query.split(" ").slice(-2).join(" ")}
- AI ${query.split(" ").pop()}
- ${query.split(" ").pop()} technology

### Secondary Keywords
- machine learning
- artificial intelligence
- automation
- tech innovation

### Content Strategy
Target a word count of 1,500-2,500 words with H2 headings every 300-400 words for optimal SEO.`;
      }

      return `## Trending Analysis: ${query}

### Current Trends
📈 **Rising Topics**
- AI and automation
- Cloud infrastructure
- Developer tools

### SEO Recommendations
1. Focus on long-tail keywords
2. Include relevant technical terms
3. Create comprehensive guides
4. Update content regularly

### Engagement Metrics
Average engagement for similar topics: High
Competition level: Medium`;
    }

    case "writer-agent": {
      if (queryLower.includes("draft") || queryLower.includes("intro") || queryLower.includes("write")) {
        return `## Draft: ${query}

### Introduction

In the rapidly evolving landscape of technology, ${query.includes("about") ? query.split("about")[1].trim() : query} represents a fascinating convergence of innovation and practical application.

This topic has garnered significant attention from both researchers and practitioners, as its implications extend far beyond theoretical considerations into real-world implementations that are reshaping industries.

### Key Points to Cover

1. **Background and Context** - Setting the stage for understanding
2. **Current State of the Art** - Latest developments and capabilities
3. **Practical Applications** - Real-world use cases
4. **Future Directions** - What's next in this space

*This draft provides a starting point. Let me know if you'd like me to expand on any section.*`;
      }

      return `## Content Plan: ${query}

I can help you create compelling content on this topic.

### Suggested Structure
1. **Hook** - Attention-grabbing opening
2. **Problem** - Why this matters
3. **Solution** - Key insights and approaches
4. **Examples** - Real-world applications
5. **Call to Action** - Next steps for readers

### Writing Style
- Clear and engaging
- Technical but accessible
- Well-researched with citations

Would you like me to draft a specific section?`;
    }

    default:
      return `I received your query: "${query}". How can I help you further?`;
  }
}
