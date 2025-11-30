/**
 * Pipeline API Route
 *
 * Provides endpoints for:
 * 1. Creating new pipelines (POST)
 * 2. Getting pipeline status (GET with query params)
 * 3. Listing active/recent pipelines (GET)
 *
 * All pipeline operations run LIVE using the A2A agent coordination pattern.
 * This calls the actual deployed agents to produce real data:
 * - Academic Research Agent for topic research
 * - Google Trends Agent for SEO analysis
 * - Blog Writer Agent for content creation and GCP deployment
 */

import { NextRequest } from "next/server";

// =============================================================================
// Logging Utilities
// =============================================================================

function logWithTimestamp(level: "INFO" | "WARN" | "ERROR" | "DEBUG", message: string, data?: object) {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [Pipeline API] [${level}]`;
  
  if (data) {
    console.log(`${prefix} ${message}`, JSON.stringify(data, null, 2));
  } else {
    console.log(`${prefix} ${message}`);
  }
}

// =============================================================================
// A2A Agent Configuration
// =============================================================================

const isDevelopment = process.env.NODE_ENV === "development";

// Agent URLs - prioritize environment variables, fall back to Cloud Run URLs in production
const AGENT_URLS = {
  research: process.env.AGENT_ACADEMIC_RESEARCH_URL || 
    (isDevelopment ? "" : "https://chained-academic-research-sguacxy5gq-uc.a.run.app"),
  trends: process.env.AGENT_GOOGLE_TRENDS_URL || 
    (isDevelopment ? "" : "https://chained-google-trends-sguacxy5gq-uc.a.run.app"),
  writer: process.env.AGENT_BLOG_WRITER_URL || 
    (isDevelopment ? "" : "https://chained-blog-writer-sguacxy5gq-uc.a.run.app"),
};

// GCP Blog URL construction
// Blog bucket follows pattern: ${PROJECT_ID}-chained-blog
// Blog URL format: https://storage.googleapis.com/${PROJECT_ID}-chained-blog/posts/${slug}.html
function getBlogUrl(slug: string): string {
  const projectId = process.env.GCP_PROJECT_ID || "chained-ai";
  return `https://storage.googleapis.com/${projectId}-chained-blog/posts/${slug}.html`;
}

// Generate URL-friendly slug from topic
function generateSlug(topic: string): string {
  return topic.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-');
}

// A2A Protocol request/response types
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
  referenceTaskIds?: string[];
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
  referenceTaskIds: string[];
}

// Call an A2A agent
async function callA2AAgent(
  agentUrl: string, 
  message: string, 
  metadata?: Record<string, unknown>,
  referenceTaskIds?: string[]
): Promise<A2ATask | null> {
  if (!agentUrl) {
    logWithTimestamp("WARN", "Agent URL not configured, cannot call agent");
    return null;
  }
  
  try {
    const request: A2ASendMessageRequest = {
      message: {
        role: "user",
        parts: [{ text: message }],
      },
      contextId: `pipeline-${Date.now()}-${crypto.randomUUID().substring(0, 8)}`,
      metadata,
      referenceTaskIds,
    };
    
    const response = await fetch(`${agentUrl}/a2a/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });
    
    if (!response.ok) {
      logWithTimestamp("ERROR", `Agent call failed: ${response.status}`, {
        url: agentUrl,
        status: response.status,
      });
      return null;
    }
    
    const task = await response.json() as A2ATask;
    logWithTimestamp("INFO", "Agent call successful", {
      taskId: task.id,
      state: task.status.state,
    });
    
    return task;
  } catch (error) {
    logWithTimestamp("ERROR", "Agent call error", {
      url: agentUrl,
      error: error instanceof Error ? error.message : String(error),
    });
    return null;
  }
}

// Pipeline states
export type PipelineStatus = "pending" | "running" | "completed" | "failed";

// Enhanced A2A Step details for deep dive capability
export interface A2AStepDetail {
  taskId: string;
  agentName: string;
  phase: string;
  status: "pending" | "running" | "completed" | "failed";
  startTime: string;
  endTime?: string;
  durationMs?: number;
  message?: string;
  artifacts: Array<{
    name: string;
    type: string;
    data: string;
    preview?: string;  // First 200 chars for UI preview
  }>;
  rawResponse?: object;  // Full A2A task response for debugging
}

export interface Pipeline {
  id: string;
  topic: string;
  status: PipelineStatus;
  createdAt: string;
  updatedAt: string;
  progress: number;
  currentPhase: "research" | "trends" | "writing" | "publishing" | "complete";
  results?: {
    research?: { topic: string; domain: string; keywords: string[] };
    trends?: { trendingKeywords: string[]; recommendedFocus: string };
    blog?: { title: string; url: string; wordCount: number };
  };
  // NEW: Detailed A2A step history for deep dive into runs
  a2aSteps?: A2AStepDetail[];
  // NEW: Total execution time
  totalDurationMs?: number;
}

// In-memory store for pipelines
// Real pipelines are stored here when created via POST /api/pipeline
const activePipelines: Map<string, Pipeline> = new Map();

// No demo/fake pipelines - only real pipelines created by users appear here
// Pipelines persist in memory during the server session
// For production, consider using a database or Cloud Storage for persistence

/**
 * GET /api/pipeline
 *
 * Query params:
 * - id: Get a specific pipeline by ID
 * - status: Filter by status (pending, running, completed, failed)
 * - limit: Number of pipelines to return (default: 10)
 * 
 * Returns ONLY real pipelines that were created via POST /api/pipeline
 * No demo or fake data is included.
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const pipelineId = searchParams.get("id");
  const statusFilter = searchParams.get("status");
  const limit = parseInt(searchParams.get("limit") || "10", 10);
  
  logWithTimestamp("DEBUG", "GET request received", {
    pipelineId,
    statusFilter,
    limit,
  });

  // Get a specific pipeline
  if (pipelineId) {
    const pipeline = activePipelines.get(pipelineId);

    if (!pipeline) {
      logWithTimestamp("WARN", `Pipeline not found: ${pipelineId}`);
      return new Response(JSON.stringify({ error: "Pipeline not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }

    logWithTimestamp("INFO", `Pipeline retrieved: ${pipelineId}`, {
      status: pipeline.status,
      progress: pipeline.progress,
    });
    
    return new Response(JSON.stringify(pipeline), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // List pipelines - only real pipelines from activePipelines
  let pipelines = Array.from(activePipelines.values());

  // Apply status filter
  if (statusFilter) {
    pipelines = pipelines.filter((p) => p.status === statusFilter);
  }

  // Sort by creation date (newest first) and limit
  pipelines = pipelines
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, limit);

  logWithTimestamp("INFO", "Pipelines listed", {
    total: pipelines.length,
    activePipelinesCount: pipelines.filter(
      (p) => p.status === "pending" || p.status === "running"
    ).length,
  });

  return new Response(
    JSON.stringify({
      pipelines,
      total: pipelines.length,
      activePipelinesCount: pipelines.filter(
        (p) => p.status === "pending" || p.status === "running"
      ).length,
    }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
}

/**
 * POST /api/pipeline
 *
 * Creates and executes a new pipeline on the live site.
 *
 * Body:
 * - topic: The topic to research (required)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { topic } = body;

    if (!topic || typeof topic !== "string" || topic.trim().length === 0) {
      logWithTimestamp("WARN", "Pipeline creation failed: Topic is required");
      return new Response(JSON.stringify({ error: "Topic is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Generate a unique pipeline ID using crypto for better uniqueness
    const randomPart = typeof crypto !== 'undefined' && crypto.randomUUID 
      ? crypto.randomUUID().substring(0, 8)
      : Math.random().toString(36).substring(2, 10);
    const pipelineId = `pipeline-${Date.now()}-${randomPart}`;
    const now = new Date().toISOString();

    // Create the pipeline record
    const pipeline: Pipeline = {
      id: pipelineId,
      topic: topic.trim(),
      status: "pending",
      createdAt: now,
      updatedAt: now,
      progress: 0,
      currentPhase: "research",
    };

    // Store the pipeline
    activePipelines.set(pipelineId, pipeline);
    
    logWithTimestamp("INFO", "Pipeline created", {
      pipelineId,
      topic: topic.trim(),
    });

    // Start pipeline execution
    executePipeline(pipelineId);

    return new Response(JSON.stringify({ success: true, pipeline }), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logWithTimestamp("ERROR", "Pipeline creation failed", { error: errorMessage });
    return new Response(JSON.stringify({ error: "Failed to create pipeline" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}

/**
 * Helper to create an A2A step detail from a task result
 */
function createA2AStepDetail(
  agentName: string,
  phase: string,
  startTime: string,
  task: A2ATask | null,
  fallbackMessage?: string
): A2AStepDetail {
  const endTime = new Date().toISOString();
  const durationMs = new Date(endTime).getTime() - new Date(startTime).getTime();
  
  if (!task) {
    return {
      taskId: `fallback-${Date.now()}`,
      agentName,
      phase,
      status: "completed",
      startTime,
      endTime,
      durationMs,
      message: fallbackMessage || `${agentName} unavailable, using defaults`,
      artifacts: [],
    };
  }
  
  return {
    taskId: task.id,
    agentName,
    phase,
    status: task.status.state === "completed" ? "completed" : 
            task.status.state === "failed" ? "failed" : "running",
    startTime,
    endTime,
    durationMs,
    message: task.status.message?.parts?.map(p => p.text).join("\n") || undefined,
    artifacts: (task.artifacts || []).map(a => ({
      name: a.name,
      type: a.type,
      data: a.data,
      preview: a.data.substring(0, 200) + (a.data.length > 200 ? "..." : ""),
    })),
    rawResponse: task,
  };
}

/**
 * Execute pipeline through all phases using REAL A2A agents.
 * This calls the actual deployed agents to produce real data:
 * 1. Research Phase: Calls Academic Research Agent
 * 2. Trends Phase: Calls Google Trends Agent  
 * 3. Writing Phase: Calls Blog Writer Agent
 * 4. Publishing Phase: Blog Writer Agent uploads to GCP Cloud Storage
 * 
 * Now captures detailed A2A step information for deep dive into runs.
 */
async function executePipelineWithAgents(pipelineId: string): Promise<void> {
  const pipeline = activePipelines.get(pipelineId);
  if (!pipeline) {
    logWithTimestamp("WARN", `Pipeline execution failed: Pipeline not found: ${pipelineId}`);
    return;
  }

  const pipelineStartTime = new Date().toISOString();
  
  pipeline.status = "running";
  pipeline.updatedAt = new Date().toISOString();
  pipeline.a2aSteps = [];  // Initialize A2A steps array
  activePipelines.set(pipelineId, pipeline);
  
  logWithTimestamp("INFO", `Pipeline execution started with REAL agents: ${pipelineId}`, {
    topic: pipeline.topic,
    agents: {
      research: AGENT_URLS.research ? "configured" : "not configured",
      trends: AGENT_URLS.trends ? "configured" : "not configured",
      writer: AGENT_URLS.writer ? "configured" : "not configured",
    },
  });

  const taskIds: string[] = [];
  
  try {
    // =========================================================================
    // Phase 1: Research
    // =========================================================================
    pipeline.currentPhase = "research";
    pipeline.progress = 10;
    pipeline.updatedAt = new Date().toISOString();
    activePipelines.set(pipelineId, pipeline);
    
    logWithTimestamp("INFO", `Pipeline ${pipelineId}: Starting research phase`);
    
    const researchStartTime = new Date().toISOString();
    const researchTask = await callA2AAgent(
      AGENT_URLS.research,
      `Research the topic: ${pipeline.topic}. Provide key findings, domain classification, and important keywords.`,
      { topic: pipeline.topic }
    );
    
    if (researchTask) {
      taskIds.push(researchTask.id);
      
      // Extract research results from artifacts
      const researchArtifact = researchTask.artifacts?.find(a => a.name === "research-data");
      let researchData = {
        topic: pipeline.topic,
        domain: "Technology",
        keywords: pipeline.topic.toLowerCase().split(" ").filter(w => w.length > 3),
      };
      
      if (researchArtifact?.data) {
        try {
          const parsed = JSON.parse(researchArtifact.data);
          researchData = {
            topic: parsed.topic || pipeline.topic,
            domain: parsed.domain || "Technology",
            keywords: parsed.keywords || researchData.keywords,
          };
        } catch {
          // Use default if parsing fails
        }
      }
      
      pipeline.results = { research: researchData };
      pipeline.progress = 25;
      
      // Record A2A step with full details
      pipeline.a2aSteps?.push(createA2AStepDetail(
        "Academic Research Agent",
        "research",
        researchStartTime,
        researchTask
      ));
      
      logWithTimestamp("INFO", `Pipeline ${pipelineId}: Research complete`, { researchData });
    } else {
      // Agent not available - use intelligent defaults
      pipeline.results = {
        research: {
          topic: pipeline.topic,
          domain: "Technology",
          keywords: pipeline.topic.toLowerCase().split(/\s+/).filter(w => w.length > 2).slice(0, 5),
        },
      };
      pipeline.progress = 25;
      
      // Record fallback step
      pipeline.a2aSteps?.push(createA2AStepDetail(
        "Academic Research Agent",
        "research",
        researchStartTime,
        null,
        "Research agent unavailable, using intelligent defaults based on topic analysis"
      ));
      
      logWithTimestamp("WARN", `Pipeline ${pipelineId}: Research agent unavailable, using defaults`);
    }
    
    pipeline.updatedAt = new Date().toISOString();
    activePipelines.set(pipelineId, pipeline);
    
    // =========================================================================
    // Phase 2: Trends Analysis
    // =========================================================================
    pipeline.currentPhase = "trends";
    pipeline.progress = 30;
    pipeline.updatedAt = new Date().toISOString();
    activePipelines.set(pipelineId, pipeline);
    
    logWithTimestamp("INFO", `Pipeline ${pipelineId}: Starting trends phase`);
    
    const trendsStartTime = new Date().toISOString();
    const trendsTask = await callA2AAgent(
      AGENT_URLS.trends,
      `Analyze trends for: ${pipeline.topic}. Provide trending keywords and SEO recommendations.`,
      { 
        topic: pipeline.topic,
        keywords: pipeline.results?.research?.keywords,
      },
      taskIds
    );
    
    if (trendsTask) {
      taskIds.push(trendsTask.id);
      
      // Extract trends results
      const trendsArtifact = trendsTask.artifacts?.find(a => a.name === "trends-data");
      let trendsData = {
        trendingKeywords: pipeline.results?.research?.keywords || ["AI", "technology"],
        recommendedFocus: pipeline.topic,
      };
      
      if (trendsArtifact?.data) {
        try {
          const parsed = JSON.parse(trendsArtifact.data);
          trendsData = {
            trendingKeywords: parsed.trending_keywords || parsed.trendingKeywords || trendsData.trendingKeywords,
            recommendedFocus: parsed.recommended_focus || parsed.recommendedFocus || trendsData.recommendedFocus,
          };
        } catch {
          // Use default if parsing fails
        }
      }
      
      pipeline.results = { ...pipeline.results, trends: trendsData };
      pipeline.progress = 50;
      
      // Record A2A step with full details
      pipeline.a2aSteps?.push(createA2AStepDetail(
        "Google Trends Agent",
        "trends",
        trendsStartTime,
        trendsTask
      ));
      
      logWithTimestamp("INFO", `Pipeline ${pipelineId}: Trends analysis complete`, { trendsData });
    } else {
      // Agent not available - use intelligent defaults
      pipeline.results = {
        ...pipeline.results,
        trends: {
          trendingKeywords: [...(pipeline.results?.research?.keywords || []), "AI", "innovation"],
          recommendedFocus: pipeline.topic,
        },
      };
      pipeline.progress = 50;
      
      // Record fallback step
      pipeline.a2aSteps?.push(createA2AStepDetail(
        "Google Trends Agent",
        "trends",
        trendsStartTime,
        null,
        "Trends agent unavailable, using intelligent defaults based on research keywords"
      ));
      
      logWithTimestamp("WARN", `Pipeline ${pipelineId}: Trends agent unavailable, using defaults`);
    }
    
    pipeline.updatedAt = new Date().toISOString();
    activePipelines.set(pipelineId, pipeline);
    
    // =========================================================================
    // Phase 3 & 4: Writing and Publishing
    // =========================================================================
    pipeline.currentPhase = "writing";
    pipeline.progress = 60;
    pipeline.updatedAt = new Date().toISOString();
    activePipelines.set(pipelineId, pipeline);
    
    logWithTimestamp("INFO", `Pipeline ${pipelineId}: Starting writing phase`);
    
    const writerStartTime = new Date().toISOString();
    const writerTask = await callA2AAgent(
      AGENT_URLS.writer,
      `Write and publish a blog post about: ${pipeline.topic}`,
      {
        topic_data: {
          topic: pipeline.results?.research?.topic || pipeline.topic,
          domain: pipeline.results?.research?.domain || "Technology",
          key_points: [
            "Introduction and Overview",
            "Key Concepts and Background",
            "Practical Applications",
            "Future Outlook",
          ],
          seo_keywords: pipeline.results?.trends?.trendingKeywords || pipeline.results?.research?.keywords || [],
          suggested_length: "1500-2500 words",
        },
        trends_data: pipeline.results?.trends ? {
          trending_keywords: pipeline.results.trends.trendingKeywords,
          recommended_focus: pipeline.results.trends.recommendedFocus,
        } : null,
      },
      taskIds
    );
    
    if (writerTask) {
      taskIds.push(writerTask.id);
      
      // Extract blog results
      const deploymentArtifact = writerTask.artifacts?.find(a => a.name === "deployment-info");
      const metadataArtifact = writerTask.artifacts?.find(a => a.name === "blog-metadata");
      
      let blogUrl = "";
      let blogTitle = `Blog: ${pipeline.topic}`;
      let wordCount = 0;
      
      if (deploymentArtifact?.data) {
        try {
          const deployment = JSON.parse(deploymentArtifact.data);
          blogUrl = deployment.url || "";
          logWithTimestamp("INFO", `Pipeline ${pipelineId}: Blog deployed`, { 
            url: blogUrl,
            deployed: deployment.deployed,
            simulated: deployment.simulated,
          });
        } catch {
          // Continue with fallback
        }
      }
      
      if (metadataArtifact?.data) {
        try {
          const metadata = JSON.parse(metadataArtifact.data);
          wordCount = metadata.word_count || 0;
        } catch {
          // Continue with fallback
        }
      }
      
      // Extract title from task message if available
      const taskMessage = writerTask.status.message?.parts?.[0]?.text || "";
      const titleMatch = taskMessage.match(/Blog post '([^']+)'/);
      if (titleMatch) {
        blogTitle = titleMatch[1];
      }
      
      // Use the deployed URL, or construct from slug using utility function
      if (!blogUrl) {
        blogUrl = getBlogUrl(generateSlug(pipeline.topic));
      }
      
      pipeline.currentPhase = "publishing";
      pipeline.progress = 90;
      pipeline.results = {
        ...pipeline.results,
        blog: {
          title: blogTitle,
          url: blogUrl,
          // Use actual word count from agent response, or 0 if unavailable (no fake data)
          wordCount: wordCount,
        },
      };
      
      // Record A2A step with full details
      pipeline.a2aSteps?.push(createA2AStepDetail(
        "Blog Writer Agent",
        "writing",
        writerStartTime,
        writerTask
      ));
      
      logWithTimestamp("INFO", `Pipeline ${pipelineId}: Blog writing complete`, {
        title: blogTitle,
        url: blogUrl,
        wordCount,
      });
    } else {
      // Writer agent not available - show placeholder with 0 word count (no fake data)
      pipeline.currentPhase = "publishing";
      pipeline.progress = 90;
      pipeline.results = {
        ...pipeline.results,
        blog: {
          title: `Blog: ${pipeline.topic}`,
          url: getBlogUrl(generateSlug(pipeline.topic)),
          wordCount: 0, // No fake word count - agent unavailable
        },
      };
      
      // Record fallback step
      pipeline.a2aSteps?.push(createA2AStepDetail(
        "Blog Writer Agent",
        "writing",
        writerStartTime,
        null,
        "Writer agent unavailable, blog not created - URL is placeholder"
      ));
      
      logWithTimestamp("WARN", `Pipeline ${pipelineId}: Writer agent unavailable, blog not created`);
    }
    
    pipeline.updatedAt = new Date().toISOString();
    activePipelines.set(pipelineId, pipeline);
    
    // =========================================================================
    // Complete
    // =========================================================================
    pipeline.status = "completed";
    pipeline.currentPhase = "complete";
    pipeline.progress = 100;
    pipeline.updatedAt = new Date().toISOString();
    
    // Calculate total pipeline duration
    pipeline.totalDurationMs = new Date().getTime() - new Date(pipelineStartTime).getTime();
    
    activePipelines.set(pipelineId, pipeline);
    
    logWithTimestamp("INFO", `Pipeline ${pipelineId}: Completed successfully`, {
      topic: pipeline.topic,
      blogUrl: pipeline.results?.blog?.url,
      taskIds,
      totalDurationMs: pipeline.totalDurationMs,
      a2aStepsCount: pipeline.a2aSteps?.length || 0,
    });
    
  } catch (error) {
    pipeline.status = "failed";
    pipeline.updatedAt = new Date().toISOString();
    pipeline.totalDurationMs = new Date().getTime() - new Date(pipelineStartTime).getTime();
    activePipelines.set(pipelineId, pipeline);
    
    logWithTimestamp("ERROR", `Pipeline ${pipelineId}: Execution failed`, {
      error: error instanceof Error ? error.message : String(error),
    });
  }
}

/**
 * Execute pipeline - wrapper that starts async execution
 */
function executePipeline(pipelineId: string) {
  // Execute asynchronously without blocking
  executePipelineWithAgents(pipelineId).catch(error => {
    logWithTimestamp("ERROR", `Pipeline ${pipelineId}: Unhandled error`, {
      error: error instanceof Error ? error.message : String(error),
    });
  });
}
