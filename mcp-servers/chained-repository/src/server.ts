#!/usr/bin/env node

/**
 * Chained Repository MCP Server
 * 
 * Provides access to Chained repository data for autonomous agents:
 * - Agent system (registry, metrics, hall of fame)
 * - Learning data (TLDR, HN, GitHub Trending, discussions)
 * - Repository insights (code patterns, file navigation)
 * - Workflow & automation tools (issue matching, agent selection)
 * - GitHub Pages data (stats, visualization data)
 * 
 * Created by @investigate-champion (Ada Lovelace)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Repository root (assuming server runs from mcp-servers/chained-repository/dist)
const REPO_ROOT = path.resolve(__dirname, "../../../");

interface AgentInfo {
  id: string;
  name: string;
  specialization: string;
  status: string;
  metrics?: Record<string, any>;
}

interface LearningData {
  source: string;
  timestamp: string;
  data: any;
}

/**
 * Utility: Read JSON file safely
 */
async function readJsonFile(filePath: string): Promise<any> {
  try {
    const content = await fs.readFile(filePath, "utf-8");
    return JSON.parse(content);
  } catch (error) {
    throw new Error(`Failed to read ${filePath}: ${error}`);
  }
}

/**
 * Utility: List files in directory
 */
async function listFiles(dirPath: string, pattern?: RegExp): Promise<string[]> {
  try {
    const files = await fs.readdir(dirPath);
    if (pattern) {
      return files.filter((f) => pattern.test(f));
    }
    return files;
  } catch (error) {
    throw new Error(`Failed to list directory ${dirPath}: ${error}`);
  }
}

/**
 * Tool: Get agent registry
 */
async function getAgentRegistry(): Promise<any> {
  const registryPath = path.join(REPO_ROOT, ".github/agent-system/registry.json");
  return await readJsonFile(registryPath);
}

/**
 * Tool: Get agent metrics
 */
async function getAgentMetrics(agentId?: string): Promise<any> {
  const metricsDir = path.join(REPO_ROOT, ".github/agent-system/metrics");
  
  if (agentId) {
    const agentMetricsDir = path.join(metricsDir, agentId);
    const latestPath = path.join(agentMetricsDir, "latest.json");
    return await readJsonFile(latestPath);
  }
  
  // Return all agent metrics
  const agents = await listFiles(metricsDir);
  const allMetrics: Record<string, any> = {};
  
  for (const agentDir of agents) {
    const latestPath = path.join(metricsDir, agentDir, "latest.json");
    try {
      allMetrics[agentDir] = await readJsonFile(latestPath);
    } catch {
      // Skip if no latest.json
    }
  }
  
  return allMetrics;
}

/**
 * Tool: Get Hall of Fame
 */
async function getHallOfFame(): Promise<any> {
  const hofPath = path.join(REPO_ROOT, ".github/agent-system/hall_of_fame.json");
  return await readJsonFile(hofPath);
}

/**
 * Tool: List agent specializations
 */
async function listSpecializations(): Promise<string[]> {
  const agentsDir = path.join(REPO_ROOT, ".github/agents");
  const files = await listFiles(agentsDir, /\.md$/);
  return files
    .filter((f) => f !== "README.md")
    .map((f) => f.replace(".md", ""));
}

/**
 * Tool: Get learning data
 */
async function getLearningData(source?: string, limit?: number): Promise<LearningData[]> {
  const learningsDir = path.join(REPO_ROOT, "learnings");
  let files = await listFiles(learningsDir, /\.json$/);
  
  // Filter by source if specified
  if (source) {
    const sourcePrefix = source.toLowerCase();
    files = files.filter((f) => f.toLowerCase().startsWith(sourcePrefix));
  }
  
  // Sort by date (most recent first)
  files.sort().reverse();
  
  // Limit results
  if (limit && limit > 0) {
    files = files.slice(0, limit);
  }
  
  const learnings: LearningData[] = [];
  for (const file of files) {
    const filePath = path.join(learningsDir, file);
    const data = await readJsonFile(filePath);
    
    // Parse source and timestamp from filename
    // Format: {source}_{YYYYMMDD}_{HHMMSS}.json
    const match = file.match(/^([a-z_]+)_(\d{8})_(\d{6})\.json$/);
    const sourceType = match ? match[1] : "unknown";
    const timestamp = match ? `${match[2]}_${match[3]}` : file;
    
    learnings.push({
      source: sourceType,
      timestamp,
      data,
    });
  }
  
  return learnings;
}

/**
 * Tool: Get thematic analysis
 */
async function getThematicAnalysis(): Promise<any> {
  const analysisFiles = await listFiles(
    path.join(REPO_ROOT, "learnings"),
    /^analysis_.*\.json$/
  );
  
  if (analysisFiles.length === 0) {
    return { error: "No thematic analysis found" };
  }
  
  // Get most recent analysis
  analysisFiles.sort().reverse();
  const latestPath = path.join(REPO_ROOT, "learnings", analysisFiles[0]);
  return await readJsonFile(latestPath);
}

/**
 * Tool: Search agent specialization patterns
 */
async function searchAgentPatterns(keywords: string[]): Promise<any> {
  const matcherPath = path.join(REPO_ROOT, "tools/match-issue-to-agent.py");
  
  try {
    const content = await fs.readFile(matcherPath, "utf-8");
    
    // Find AGENT_PATTERNS dictionary start
    const startMatch = content.match(/AGENT_PATTERNS\s*=\s*\{/);
    if (!startMatch) {
      return { error: "Could not find AGENT_PATTERNS" };
    }
    
    const startIndex = startMatch.index! + startMatch[0].length;
    let braceCount = 1;
    let endIndex = startIndex;
    
    // Find matching closing brace
    for (let i = startIndex; i < content.length && braceCount > 0; i++) {
      if (content[i] === '{') braceCount++;
      if (content[i] === '}') braceCount--;
      endIndex = i;
    }
    
    const patternsText = content.substring(startIndex, endIndex);
    const results: Record<string, any> = {};
    
    // Parse each agent's patterns - handle nested braces properly
    const agentRegex = /'([^']+)':\s*\{/g;
    let agentMatch;
    
    while ((agentMatch = agentRegex.exec(patternsText)) !== null) {
      const agentName = agentMatch[1];
      const agentStart = agentMatch.index + agentMatch[0].length;
      
      // Find the closing brace for this agent
      let depth = 1;
      let agentEnd = agentStart;
      for (let i = agentStart; i < patternsText.length && depth > 0; i++) {
        if (patternsText[i] === '{') depth++;
        if (patternsText[i] === '}') depth--;
        if (depth === 0) agentEnd = i;
      }
      
      const agentBlock = patternsText.substring(agentStart, agentEnd);
      
      // Extract keywords
      const keywordsMatch = agentBlock.match(/'keywords':\s*\[([^\]]+)\]/);
      
      if (keywordsMatch) {
        const agentKeywords = keywordsMatch[1]
          .split(",")
          .map((k) => {
            let cleaned = k.trim().replace(/['"]/g, "");
            // Remove 'r' prefix from regex patterns if present
            if (cleaned.startsWith("r'") || cleaned.startsWith('r"')) {
              cleaned = cleaned.substring(2);
            }
            return cleaned;
          })
          .filter((k) => k.length > 0 && !k.startsWith("\\"));
        
        // Check if any search keyword matches agent keywords
        const matches = keywords.filter((k) =>
          agentKeywords.some((ak) => ak.toLowerCase().includes(k.toLowerCase()))
        );
        
        if (matches.length > 0) {
          results[agentName] = {
            keywords: agentKeywords,
            matchedKeywords: matches,
          };
        }
      }
    }
    
    return results;
  } catch (error) {
    return { error: `Failed to search patterns: ${error}` };
  }
}

/**
 * Tool: Get GitHub Pages data
 */
async function getGitHubPagesData(dataType: string): Promise<any> {
  const dataPath = path.join(REPO_ROOT, "docs/data", `${dataType}.json`);
  return await readJsonFile(dataPath);
}

/**
 * Tool: List available tools
 */
async function listAvailableTools(): Promise<string[]> {
  const toolsDir = path.join(REPO_ROOT, "tools");
  const files = await listFiles(toolsDir, /\.py$/);
  return files.filter((f) => !f.startsWith("test_"));
}

/**
 * Tool: Get tool documentation
 */
async function getToolDocumentation(toolName: string): Promise<string> {
  const readmePath = path.join(REPO_ROOT, "tools", `${toolName.toUpperCase()}_README.md`);
  
  try {
    return await fs.readFile(readmePath, "utf-8");
  } catch {
    // Try alternate naming
    const altPath = path.join(REPO_ROOT, "tools", `${toolName}_README.md`);
    try {
      return await fs.readFile(altPath, "utf-8");
    } catch {
      return `No documentation found for tool: ${toolName}`;
    }
  }
}

/**
 * Tool: Get workflow execution data
 */
async function getWorkflowData(): Promise<any> {
  const workflowPath = path.join(REPO_ROOT, "docs/data/workflows.json");
  return await readJsonFile(workflowPath);
}

/**
 * Tool: Get mission reports
 */
async function getMissionReports(): Promise<any> {
  const reportsPath = path.join(REPO_ROOT, "docs/data/mission-reports.json");
  return await readJsonFile(reportsPath);
}

/**
 * Main server implementation
 */
const server = new Server(
  {
    name: "chained-repository-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
const TOOLS: Tool[] = [
  {
    name: "get_agent_registry",
    description: "Get the complete agent registry with all active agents, their metrics, and status",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_agent_metrics",
    description: "Get performance metrics for a specific agent or all agents",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: {
          type: "string",
          description: "Optional agent ID to get specific metrics",
        },
      },
    },
  },
  {
    name: "get_hall_of_fame",
    description: "Get the Hall of Fame - top performing agents (score >= 85%)",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "list_specializations",
    description: "List all available agent specializations",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_learning_data",
    description: "Get learning data from external sources (TLDR, Hacker News, GitHub Trending, Copilot)",
    inputSchema: {
      type: "object",
      properties: {
        source: {
          type: "string",
          description: "Optional: filter by source (tldr, hn, github_trending, copilot)",
        },
        limit: {
          type: "number",
          description: "Optional: limit number of results (default: 10)",
        },
      },
    },
  },
  {
    name: "get_thematic_analysis",
    description: "Get the latest thematic analysis of trending topics",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "search_agent_patterns",
    description: "Search for agents matching specific keywords",
    inputSchema: {
      type: "object",
      properties: {
        keywords: {
          type: "array",
          items: { type: "string" },
          description: "Keywords to search for in agent patterns",
        },
      },
      required: ["keywords"],
    },
  },
  {
    name: "get_github_pages_data",
    description: "Get data from GitHub Pages (stats, issues, pulls, workflows, etc.)",
    inputSchema: {
      type: "object",
      properties: {
        data_type: {
          type: "string",
          enum: ["stats", "issues", "pulls", "workflows", "agent-registry", "mission-reports"],
          description: "Type of data to retrieve",
        },
      },
      required: ["data_type"],
    },
  },
  {
    name: "list_available_tools",
    description: "List all Python tools available in the tools/ directory",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_tool_documentation",
    description: "Get documentation for a specific tool",
    inputSchema: {
      type: "object",
      properties: {
        tool_name: {
          type: "string",
          description: "Name of the tool (without .py extension)",
        },
      },
      required: ["tool_name"],
    },
  },
  {
    name: "get_workflow_data",
    description: "Get workflow execution data and history",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "get_mission_reports",
    description: "Get mission reports and outcomes",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
];

// Handle tool list requests
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "get_agent_registry":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(await getAgentRegistry(), null, 2),
            },
          ],
        };

      case "get_agent_metrics":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                await getAgentMetrics(args?.agent_id as string | undefined),
                null,
                2
              ),
            },
          ],
        };

      case "get_hall_of_fame":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(await getHallOfFame(), null, 2),
            },
          ],
        };

      case "list_specializations":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(await listSpecializations(), null, 2),
            },
          ],
        };

      case "get_learning_data":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                await getLearningData(
                  args?.source as string | undefined,
                  args?.limit as number | undefined
                ),
                null,
                2
              ),
            },
          ],
        };

      case "get_thematic_analysis":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(await getThematicAnalysis(), null, 2),
            },
          ],
        };

      case "search_agent_patterns":
        if (!args?.keywords || !Array.isArray(args.keywords)) {
          throw new Error("keywords parameter is required and must be an array");
        }
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                await searchAgentPatterns(args.keywords as string[]),
                null,
                2
              ),
            },
          ],
        };

      case "get_github_pages_data":
        if (!args?.data_type) {
          throw new Error("data_type parameter is required");
        }
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                await getGitHubPagesData(args.data_type as string),
                null,
                2
              ),
            },
          ],
        };

      case "list_available_tools":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(await listAvailableTools(), null, 2),
            },
          ],
        };

      case "get_tool_documentation":
        if (!args?.tool_name) {
          throw new Error("tool_name parameter is required");
        }
        return {
          content: [
            {
              type: "text",
              text: await getToolDocumentation(args.tool_name as string),
            },
          ],
        };

      case "get_workflow_data":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(await getWorkflowData(), null, 2),
            },
          ],
        };

      case "get_mission_reports":
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(await getMissionReports(), null, 2),
            },
          ],
        };

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            error: String(error),
          }),
        },
      ],
      isError: true,
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Chained Repository MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
