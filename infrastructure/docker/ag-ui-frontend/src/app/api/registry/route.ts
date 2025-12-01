/**
 * Registry API Route
 *
 * Provides endpoints for agent registry operations:
 * 1. List all registered agents (GET)
 * 2. Get agent details (GET ?id=agent-id)
 * 3. Check agent health (POST)
 *
 * All operations query REAL A2A agents deployed on Cloud Run.
 */

import { NextRequest } from "next/server";

// =============================================================================
// Configuration
// =============================================================================

const isDevelopment = process.env.NODE_ENV === "development";

// Agent registry configuration
const AGENT_REGISTRY: Record<string, AgentConfig> = {
  "academic-research": {
    id: "academic-research",
    displayName: "Academic Research",
    description: "Discovers and analyzes research topics for tech blog content",
    icon: "🔬",
    category: "research",
    urlEnv: "AGENT_ACADEMIC_RESEARCH_URL",
    defaultUrl: isDevelopment ? "" : "https://chained-academic-research-sguacxy5gq-uc.a.run.app",
    skills: ["topic-discovery", "research-analysis", "content-research"],
  },
  "google-trends": {
    id: "google-trends",
    displayName: "Google Trends",
    description: "Analyzes trends and provides SEO keyword recommendations",
    icon: "📈",
    category: "seo",
    urlEnv: "AGENT_GOOGLE_TRENDS_URL",
    defaultUrl: isDevelopment ? "" : "https://chained-google-trends-sguacxy5gq-uc.a.run.app",
    skills: ["trending-keywords", "seo-optimization", "topic-analysis"],
  },
  "blog-writer": {
    id: "blog-writer",
    displayName: "Blog Writer",
    description: "Writes and publishes engaging blog posts",
    icon: "✍️",
    category: "content",
    urlEnv: "AGENT_BLOG_WRITER_URL",
    defaultUrl: isDevelopment ? "" : "https://chained-blog-writer-sguacxy5gq-uc.a.run.app",
    skills: ["blog-writing", "content-structuring", "technical-writing"],
  },
  "code-reviewer": {
    id: "code-reviewer",
    displayName: "Code Reviewer",
    description: "Reviews code snippets and suggests improvements",
    icon: "🔍",
    category: "development",
    urlEnv: "AGENT_CODE_REVIEWER_URL",
    defaultUrl: isDevelopment ? "" : "https://chained-code-reviewer-sguacxy5gq-uc.a.run.app",
    skills: ["code-review", "best-practices", "security-check"],
  },
  "data-analyst": {
    id: "data-analyst",
    displayName: "Data Analyst",
    description: "Analyzes data and generates insights",
    icon: "📊",
    category: "analytics",
    urlEnv: "AGENT_DATA_ANALYST_URL",
    defaultUrl: isDevelopment ? "" : "https://chained-data-analyst-sguacxy5gq-uc.a.run.app",
    skills: ["data-analysis", "pattern-detection", "recommendations"],
  },
  "image-generator": {
    id: "image-generator",
    displayName: "Image Generator",
    description: "Creates visual content and diagram specifications",
    icon: "🎨",
    category: "visual",
    urlEnv: "AGENT_IMAGE_GENERATOR_URL",
    defaultUrl: isDevelopment ? "" : "https://chained-image-generator-sguacxy5gq-uc.a.run.app",
    skills: ["diagram-generation", "infographic-design", "visual-content"],
  },
};

// =============================================================================
// Types
// =============================================================================

interface AgentConfig {
  id: string;
  displayName: string;
  description: string;
  icon: string;
  category: string;
  urlEnv: string;
  defaultUrl: string;
  skills: string[];
}

interface AgentHealth {
  status: "healthy" | "unhealthy" | "unknown";
  responseTimeMs?: number;
  version?: string;
  aiMode?: string;
}

interface RegisteredAgent {
  id: string;
  displayName: string;
  description: string;
  icon: string;
  category: string;
  url: string | null;
  configured: boolean;
  skills: string[];
  health?: AgentHealth;
  agentCard?: AgentCard | null;
}

interface AgentCard {
  name: string;
  description: string;
  version: string;
  protocolVersion: string;
  skills: Array<{ id: string; name: string; description: string; tags: string[] }>;
  capabilities: Record<string, boolean>;
}

// =============================================================================
// Helpers
// =============================================================================

function getAgentUrl(config: AgentConfig): string | null {
  const url = process.env[config.urlEnv];
  if (url) return url;
  if (config.defaultUrl) return config.defaultUrl;
  return null;
}

async function fetchAgentCard(url: string): Promise<AgentCard | null> {
  try {
    const response = await fetch(`${url}/.well-known/agent.json`, {
      signal: AbortSignal.timeout(5000),
    });
    if (response.ok) {
      return await response.json();
    }
  } catch {
    // Agent card fetch failed
  }
  return null;
}

async function checkAgentHealth(url: string): Promise<AgentHealth> {
  try {
    const startTime = Date.now();
    const response = await fetch(`${url}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    const responseTimeMs = Date.now() - startTime;
    
    if (response.ok) {
      const data = await response.json();
      return {
        status: "healthy",
        responseTimeMs,
        version: data.version,
        aiMode: data.ai_mode,
      };
    }
    return { status: "unhealthy", responseTimeMs };
  } catch {
    return { status: "unknown" };
  }
}

async function getRegisteredAgent(config: AgentConfig, includeHealth: boolean = false): Promise<RegisteredAgent> {
  const url = getAgentUrl(config);
  const agent: RegisteredAgent = {
    id: config.id,
    displayName: config.displayName,
    description: config.description,
    icon: config.icon,
    category: config.category,
    url,
    configured: url !== null,
    skills: config.skills,
  };
  
  if (url && includeHealth) {
    const [health, agentCard] = await Promise.all([
      checkAgentHealth(url),
      fetchAgentCard(url),
    ]);
    agent.health = health;
    agent.agentCard = agentCard;
  }
  
  return agent;
}

// =============================================================================
// API Routes
// =============================================================================

/**
 * GET /api/registry
 *
 * Query params:
 * - id: Get specific agent by ID
 * - category: Filter by category
 * - health: Include health check (true/false)
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const agentId = searchParams.get("id");
  const category = searchParams.get("category");
  const includeHealth = searchParams.get("health") === "true";
  
  // Get specific agent
  if (agentId) {
    const config = AGENT_REGISTRY[agentId];
    if (!config) {
      return new Response(JSON.stringify({ error: "Agent not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }
    
    const agent = await getRegisteredAgent(config, includeHealth);
    return new Response(JSON.stringify(agent), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }
  
  // Get all agents
  let configs = Object.values(AGENT_REGISTRY);
  
  // Filter by category
  if (category) {
    configs = configs.filter((c) => c.category === category);
  }
  
  // Get agent details
  const agents = await Promise.all(
    configs.map((config) => getRegisteredAgent(config, includeHealth))
  );
  
  // Calculate stats
  const categories = agents.map((a) => a.category);
  const uniqueCategories = categories.filter((cat, i) => categories.indexOf(cat) === i);
  
  const stats = {
    total: agents.length,
    configured: agents.filter((a) => a.configured).length,
    healthy: includeHealth ? agents.filter((a) => a.health?.status === "healthy").length : undefined,
    categories: uniqueCategories,
  };
  
  return new Response(
    JSON.stringify({
      agents,
      stats,
      timestamp: new Date().toISOString(),
    }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
}

/**
 * POST /api/registry
 *
 * Perform health checks on agents
 *
 * Body:
 * - agentIds: Array of agent IDs to check (optional, all if not specified)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { agentIds } = body;
    
    let configs = Object.values(AGENT_REGISTRY);
    
    if (agentIds && Array.isArray(agentIds)) {
      configs = configs.filter((c) => agentIds.includes(c.id));
    }
    
    const results = await Promise.all(
      configs.map(async (config) => {
        const url = getAgentUrl(config);
        if (!url) {
          return {
            id: config.id,
            displayName: config.displayName,
            status: "not_configured" as const,
          };
        }
        
        const health = await checkAgentHealth(url);
        return {
          id: config.id,
          displayName: config.displayName,
          url,
          ...health,
        };
      })
    );
    
    const summary = {
      checked: results.length,
      healthy: results.filter((r) => r.status === "healthy").length,
      unhealthy: results.filter((r) => r.status === "unhealthy").length,
      notConfigured: results.filter((r) => r.status === "not_configured").length,
    };
    
    return new Response(
      JSON.stringify({
        results,
        summary,
        timestamp: new Date().toISOString(),
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("[Registry API] Error:", error);
    return new Response(JSON.stringify({ error: "Failed to check agent health" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
