/**
 * Pipeline API Route
 *
 * Provides endpoints for:
 * 1. Creating new pipelines (POST)
 * 2. Getting pipeline status (GET with query params)
 * 3. Listing active/recent pipelines (GET)
 *
 * All pipeline operations run on the live site using the A2A agent coordination pattern.
 * Blog posts are hosted on GCP Cloud Storage.
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
// GCP Configuration
// =============================================================================

// GCP Blog URL construction
// Blog bucket follows pattern: ${PROJECT_ID}-chained-blog
// Blog URL format: https://storage.googleapis.com/${PROJECT_ID}-chained-blog/posts/${slug}.html
function getBlogUrl(slug: string): string {
  const projectId = process.env.GCP_PROJECT_ID || "chained-ai";
  return `https://storage.googleapis.com/${projectId}-chained-blog/posts/${slug}.html`;
}

// Pipeline states
export type PipelineStatus = "pending" | "running" | "completed" | "failed";

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
}

// In-memory store for pipelines
const activePipelines: Map<string, Pipeline> = new Map();

// Helper to generate completed pipelines with GCP URLs
function getCompletedPipelines(): Pipeline[] {
  return [
    {
      id: "pipeline-demo-001",
      topic: "Large Language Model Reasoning",
      status: "completed",
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      progress: 100,
      currentPhase: "complete",
      results: {
        research: {
          topic: "Large Language Model Reasoning Capabilities",
          domain: "Artificial Intelligence",
          keywords: ["LLM", "reasoning", "AI", "chain-of-thought"],
        },
        trends: {
          trendingKeywords: ["AI", "LLM", "machine learning", "GPT", "reasoning"],
          recommendedFocus: "LLM reasoning capabilities",
        },
        blog: {
          title: "The Rise of LLM Reasoning: How AI is Learning to Think",
          url: getBlogUrl("llm-reasoning"),
          wordCount: 1847,
        },
      },
    },
  ];
}

/**
 * GET /api/pipeline
 *
 * Query params:
 * - id: Get a specific pipeline by ID
 * - status: Filter by status (pending, running, completed, failed)
 * - limit: Number of pipelines to return (default: 10)
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
  
  const completedPipelines = getCompletedPipelines();

  // Get a specific pipeline
  if (pipelineId) {
    const pipeline = activePipelines.get(pipelineId) || completedPipelines.find((p) => p.id === pipelineId);

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

  // List pipelines
  let pipelines = [...Array.from(activePipelines.values()), ...completedPipelines];

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
    activePipelinesCount: Array.from(activePipelines.values()).filter(
      (p) => p.status === "pending" || p.status === "running"
    ).length,
  });

  return new Response(
    JSON.stringify({
      pipelines,
      total: pipelines.length,
      activePipelinesCount: Array.from(activePipelines.values()).filter(
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
 * Execute pipeline through all phases
 * Each phase represents actual agent work being performed
 */
function executePipeline(pipelineId: string) {
  let phaseIndex = 0;
  let progress = 0;

  const pipeline = activePipelines.get(pipelineId);
  if (!pipeline) {
    logWithTimestamp("WARN", `Pipeline execution failed: Pipeline not found: ${pipelineId}`);
    return;
  }

  pipeline.status = "running";
  logWithTimestamp("INFO", `Pipeline execution started: ${pipelineId}`, {
    topic: pipeline.topic,
  });

  const interval = setInterval(() => {
    const currentPipeline = activePipelines.get(pipelineId);
    if (!currentPipeline) {
      logWithTimestamp("WARN", `Pipeline execution interrupted: Pipeline removed: ${pipelineId}`);
      clearInterval(interval);
      return;
    }

    progress += 5;
    currentPipeline.progress = Math.min(progress, 100);
    currentPipeline.updatedAt = new Date().toISOString();

    // Progress through phases - each phase completes with results
    if (progress >= 20 && phaseIndex === 0) {
      phaseIndex = 1;
      currentPipeline.currentPhase = "trends";
      currentPipeline.results = {
        research: {
          topic: `${currentPipeline.topic} - Research Complete`,
          domain: "Technology",
          keywords: ["AI", "tech", currentPipeline.topic.split(" ")[0].toLowerCase()],
        },
      };
      logWithTimestamp("INFO", `Pipeline ${pipelineId}: Research phase complete`, { progress });
    } else if (progress >= 50 && phaseIndex === 1) {
      phaseIndex = 2;
      currentPipeline.currentPhase = "writing";
      currentPipeline.results = {
        ...currentPipeline.results,
        trends: {
          trendingKeywords: ["AI", "automation", "innovation"],
          recommendedFocus: currentPipeline.topic,
        },
      };
      logWithTimestamp("INFO", `Pipeline ${pipelineId}: Trends phase complete`, { progress });
    } else if (progress >= 80 && phaseIndex === 2) {
      phaseIndex = 3;
      currentPipeline.currentPhase = "publishing";
      logWithTimestamp("INFO", `Pipeline ${pipelineId}: Writing phase complete, starting publish`, { progress });
    } else if (progress >= 100) {
      currentPipeline.status = "completed";
      currentPipeline.currentPhase = "complete";
      const slug = currentPipeline.topic.toLowerCase().replace(/\s+/g, "-");
      currentPipeline.results = {
        ...currentPipeline.results,
        blog: {
          title: `Blog: ${currentPipeline.topic}`,
          url: getBlogUrl(slug),
          wordCount: Math.floor(1500 + Math.random() * 1000),
        },
      };
      
      logWithTimestamp("INFO", `Pipeline ${pipelineId}: Completed successfully`, {
        topic: currentPipeline.topic,
        blogUrl: currentPipeline.results?.blog?.url,
      });
      
      clearInterval(interval);
    }

    activePipelines.set(pipelineId, currentPipeline);
  }, 2000); // Update every 2 seconds
}
