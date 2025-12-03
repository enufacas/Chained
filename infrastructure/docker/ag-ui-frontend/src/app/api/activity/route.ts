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
// Logging Utilities
// =============================================================================

function logWithTimestamp(level: "INFO" | "WARN" | "ERROR" | "DEBUG", message: string, data?: object) {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [Activity API] [${level}]`;
  
  if (data) {
    console.log(`${prefix} ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`${prefix} ${message}`);
  }
}

// =============================================================================
// GCP Cloud Run Agent Configuration
// =============================================================================

// Determine if we're in development mode
const isDevelopment = process.env.NODE_ENV === "development";

// Agent endpoints - these are the ACTUAL deployed agents on GCP Cloud Run
// In development, require explicit configuration via environment variables
// In production, fall back to known Cloud Run URLs
const ADK_API_URL = process.env.NEXT_PUBLIC_ADK_API_URL || 
  (isDevelopment ? "" : "https://chained-adk-api-server-sguacxy5gq-uc.a.run.app");

// Individual agent URLs (can be overridden via env vars or discovered from ADK API)
// In development without env vars, agents will show as "unknown" status
const AGENT_ENDPOINTS = {
  "academic-research": {
    url: process.env.AGENT_ACADEMIC_RESEARCH_URL || 
      (isDevelopment ? "" : "https://chained-academic-research-sguacxy5gq-uc.a.run.app"),
    displayName: "Academic Research",
    icon: "🔬",
    description: "Discovers and analyzes research topics",
  },
  "google-trends": {
    url: process.env.AGENT_GOOGLE_TRENDS_URL || 
      (isDevelopment ? "" : "https://chained-google-trends-sguacxy5gq-uc.a.run.app"),
    displayName: "Google Trends",
    icon: "📈",
    description: "Analyzes trends for SEO optimization",
  },
  "blog-writer": {
    url: process.env.AGENT_BLOG_WRITER_URL || 
      (isDevelopment ? "" : "https://chained-blog-writer-sguacxy5gq-uc.a.run.app"),
    displayName: "Blog Writer",
    icon: "✍️",
    description: "Writes and publishes blog posts",
  },
  "code-reviewer": {
    url: process.env.AGENT_CODE_REVIEWER_URL || 
      (isDevelopment ? "" : "https://chained-code-reviewer-sguacxy5gq-uc.a.run.app"),
    displayName: "Code Reviewer",
    icon: "👀",
    description: "Reviews code and provides feedback",
  },
  "data-analyst": {
    url: process.env.AGENT_DATA_ANALYST_URL || 
      (isDevelopment ? "" : "https://chained-data-analyst-sguacxy5gq-uc.a.run.app"),
    displayName: "Data Analyst",
    icon: "📊",
    description: "Analyzes data and generates insights",
  },
  "image-generator": {
    url: process.env.AGENT_IMAGE_GENERATOR_URL || 
      (isDevelopment ? "" : "https://chained-image-generator-sguacxy5gq-uc.a.run.app"),
    displayName: "Image Generator",
    icon: "🎨",
    description: "Generates images using AI",
  },
  "error-observer": {
    url: process.env.ERROR_OBSERVER_URL ||
      (isDevelopment ? "" : "https://chained-error-observer-sguacxy5gq-uc.a.run.app"),
    displayName: "Error Observer",
    icon: "🔍",
    description: "Monitors and reports system errors",
  },
  "log-consumer": {
    url: process.env.AGENT_LOG_CONSUMER_URL || 
      (isDevelopment ? "" : "https://chained-log-consumer-sguacxy5gq-uc.a.run.app"),
    displayName: "Log Consumer",
    icon: "📝",
    description: "Consumes and processes Cloud Run logs",
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
  const startTime = Date.now();
  const { searchParams } = new URL(request.url);
  const includeAgentCards = searchParams.get("includeCards") === "true";

  logWithTimestamp("INFO", "Activity check started", {
    includeAgentCards,
    isDevelopment,
    configuredAgents: Object.keys(AGENT_ENDPOINTS),
  });

  const agents: AgentInfo[] = [];
  
  // Check health of each agent in parallel for faster response
  const agentChecks = Object.entries(AGENT_ENDPOINTS).map(
    async ([agentId, config]) => {
      const agentInfo = await checkAgentStatus(agentId, config, includeAgentCards);
      return agentInfo;
    }
  );
  
  const agentResults = await Promise.all(agentChecks);
  agents.push(...agentResults);

  // Calculate system status
  const healthyCount = agents.filter((a) => a.health.status === "healthy").length;
  const unhealthyCount = agents.filter((a) => a.health.status === "unhealthy").length;
  const unknownCount = agents.filter((a) => a.health.status === "unknown").length;
  const total = agents.length;

  const overallHealth: "healthy" | "degraded" | "unhealthy" = 
    healthyCount === total ? "healthy" :
    healthyCount > 0 ? "degraded" : "unhealthy";

  const totalTime = Date.now() - startTime;

  logWithTimestamp("INFO", "Activity check completed", {
    totalTimeMs: totalTime,
    healthyCount,
    unhealthyCount,
    unknownCount,
    overallHealth,
  });

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

  // If no URL configured, return unknown status immediately
  if (!config.url) {
    logWithTimestamp("DEBUG", `Agent ${agentId}: No URL configured, skipping health check`);
    agentInfo.health = {
      status: "unknown",
      agent: agentId,
    };
    return agentInfo;
  }

  try {
    logWithTimestamp("DEBUG", `Agent ${agentId}: Checking health at ${config.url}/health`);
    
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
      
      logWithTimestamp("DEBUG", `Agent ${agentId}: Health check successful`, {
        status: agentInfo.health.status,
        responseTimeMs,
        version: healthData.version,
      });
    } else {
      agentInfo.health = {
        status: "unhealthy",
        agent: agentId,
        responseTimeMs,
      };
      
      logWithTimestamp("WARN", `Agent ${agentId}: Health check returned non-OK status`, {
        httpStatus: healthResponse.status,
        responseTimeMs,
      });
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
          logWithTimestamp("DEBUG", `Agent ${agentId}: Agent card fetched successfully`);
        }
      } catch (cardError) {
        // Agent card fetch failed, but health is still valid
        logWithTimestamp("WARN", `Agent ${agentId}: Could not fetch agent card`, {
          error: cardError instanceof Error ? cardError.message : String(cardError),
        });
      }
    }

  } catch (error) {
    const responseTimeMs = Date.now() - startTime;
    agentInfo.health = {
      status: "unhealthy",
      agent: agentId,
      responseTimeMs,
    };
    
    const errorMessage = error instanceof Error ? error.message : String(error);
    const isTimeout = error instanceof Error && error.name === "AbortError";
    
    logWithTimestamp("ERROR", `Agent ${agentId}: Health check failed`, {
      error: errorMessage,
      isTimeout,
      responseTimeMs,
      url: config.url,
    });
  }

  return agentInfo;
}
