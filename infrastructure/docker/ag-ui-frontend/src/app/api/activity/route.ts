/**
 * Activity API Route
 *
 * Fetches real-time agent activity from GCP-deployed A2A agents.
 * Sources data from the actual Cloud Run services, NOT GitHub.
 *
 * GET /api/activity
 *
 * Returns:
 * - agents: Status of all deployed agents (health, version, etc.)
 * - systemStatus: Overall system health
 * - lastUpdated: Timestamp of the check
 */

import { NextRequest } from "next/server";

// =============================================================================
// GCP Cloud Run Agent Configuration
// =============================================================================

// Agent endpoints - these are the ACTUAL deployed agents on GCP Cloud Run
// The ADK API Server URL is set via environment variable
const ADK_API_URL = process.env.NEXT_PUBLIC_ADK_API_URL || "https://chained-adk-api-server-sguacxy5gq-uc.a.run.app";

// Individual agent URLs (can be overridden via env vars or discovered from ADK API)
const AGENT_ENDPOINTS = {
  "academic-research": {
    url: process.env.AGENT_ACADEMIC_RESEARCH_URL || "https://chained-academic-research-sguacxy5gq-uc.a.run.app",
    displayName: "Academic Research",
    icon: "🔬",
    description: "Discovers and analyzes research topics",
  },
  "google-trends": {
    url: process.env.AGENT_GOOGLE_TRENDS_URL || "https://chained-google-trends-sguacxy5gq-uc.a.run.app",
    displayName: "Google Trends",
    icon: "📈",
    description: "Analyzes trends for SEO optimization",
  },
  "blog-writer": {
    url: process.env.AGENT_BLOG_WRITER_URL || "https://chained-blog-writer-sguacxy5gq-uc.a.run.app",
    displayName: "Blog Writer",
    icon: "✍️",
    description: "Writes and publishes blog posts",
  },
  "adk-api-server": {
    url: ADK_API_URL,
    displayName: "ADK API Server",
    icon: "🌐",
    description: "A2A coordination and routing",
  },
};

// =============================================================================
// Types
// =============================================================================

export interface AgentHealth {
  status: "healthy" | "unhealthy" | "unknown";
  agent: string;
  version?: string;
  ai_mode?: string;
  timestamp?: string;
  responseTimeMs?: number;
}

export interface AgentInfo {
  id: string;
  name: string;
  displayName: string;
  icon: string;
  description: string;
  url: string;
  health: AgentHealth;
  agentCard?: {
    name: string;
    version: string;
    skills: Array<{ id: string; name: string; description: string }>;
  };
}

export interface ActivityResponse {
  agents: AgentInfo[];
  systemStatus: {
    healthy: number;
    unhealthy: number;
    total: number;
    overallHealth: "healthy" | "degraded" | "unhealthy";
  };
  adkApiUrl: string;
  lastUpdated: string;
  source: "gcp-cloudrun";
}

// =============================================================================
// API Handler
// =============================================================================

/**
 * GET /api/activity
 *
 * Fetches real-time status from GCP-deployed A2A agents.
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const includeAgentCards = searchParams.get("includeCards") === "true";

  const agents: AgentInfo[] = [];
  
  // Check health of each agent
  for (const [agentId, config] of Object.entries(AGENT_ENDPOINTS)) {
    const agentInfo = await checkAgentStatus(agentId, config, includeAgentCards);
    agents.push(agentInfo);
  }

  // Calculate system status
  const healthyCount = agents.filter((a) => a.health.status === "healthy").length;
  const unhealthyCount = agents.filter((a) => a.health.status === "unhealthy").length;
  const total = agents.length;

  const overallHealth: "healthy" | "degraded" | "unhealthy" = 
    healthyCount === total ? "healthy" :
    healthyCount > 0 ? "degraded" : "unhealthy";

  const response: ActivityResponse = {
    agents,
    systemStatus: {
      healthy: healthyCount,
      unhealthy: unhealthyCount,
      total,
      overallHealth,
    },
    adkApiUrl: ADK_API_URL,
    lastUpdated: new Date().toISOString(),
    source: "gcp-cloudrun",
  };

  return new Response(JSON.stringify(response), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "public, s-maxage=15, stale-while-revalidate=30",
    },
  });
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Check the status of a single agent by calling its health endpoint
 */
async function checkAgentStatus(
  agentId: string,
  config: { url: string; displayName: string; icon: string; description: string },
  includeAgentCard: boolean
): Promise<AgentInfo> {
  const startTime = Date.now();
  
  // Default agent info
  const agentInfo: AgentInfo = {
    id: agentId,
    name: agentId,
    displayName: config.displayName,
    icon: config.icon,
    description: config.description,
    url: config.url,
    health: {
      status: "unknown",
      agent: agentId,
    },
  };

  try {
    // Check health endpoint
    const healthResponse = await fetch(`${config.url}/health`, {
      method: "GET",
      headers: { "Accept": "application/json" },
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    const responseTimeMs = Date.now() - startTime;

    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      agentInfo.health = {
        status: healthData.status === "healthy" ? "healthy" : "unhealthy",
        agent: healthData.agent || agentId,
        version: healthData.version,
        ai_mode: healthData.ai_mode,
        timestamp: healthData.timestamp,
        responseTimeMs,
      };
    } else {
      agentInfo.health = {
        status: "unhealthy",
        agent: agentId,
        responseTimeMs,
      };
    }

    // Optionally fetch agent card
    if (includeAgentCard && agentInfo.health.status === "healthy") {
      try {
        const cardResponse = await fetch(`${config.url}/.well-known/agent.json`, {
          method: "GET",
          headers: { "Accept": "application/json" },
          signal: AbortSignal.timeout(3000),
        });

        if (cardResponse.ok) {
          const cardData = await cardResponse.json();
          agentInfo.agentCard = {
            name: cardData.name,
            version: cardData.version,
            skills: cardData.skills || [],
          };
        }
      } catch {
        // Agent card fetch failed, but health is still valid
        console.log(`[Activity API] Could not fetch agent card for ${agentId}`);
      }
    }

  } catch (error) {
    const responseTimeMs = Date.now() - startTime;
    agentInfo.health = {
      status: "unhealthy",
      agent: agentId,
      responseTimeMs,
    };
    console.error(`[Activity API] Health check failed for ${agentId}:`, error);
  }

  return agentInfo;
}
