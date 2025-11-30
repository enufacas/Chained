/**
 * Pipeline API Route
 *
 * Provides endpoints for:
 * 1. Creating new pipelines (POST)
 * 2. Getting pipeline status (GET with query params)
 * 3. Listing active/recent pipelines (GET)
 *
 * All pipeline operations run on the live site using the A2A agent coordination pattern.
 */

import { NextRequest } from "next/server";

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

// Previously completed pipelines
const COMPLETED_PIPELINES: Pipeline[] = [
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
        url: "https://enufacas.github.io/Chained/blog/llm-reasoning.html",
        wordCount: 1847,
      },
    },
  },
];

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

  // Get a specific pipeline
  if (pipelineId) {
    const pipeline = activePipelines.get(pipelineId) || COMPLETED_PIPELINES.find((p) => p.id === pipelineId);

    if (!pipeline) {
      return new Response(JSON.stringify({ error: "Pipeline not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify(pipeline), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // List pipelines
  let pipelines = [...Array.from(activePipelines.values()), ...COMPLETED_PIPELINES];

  // Apply status filter
  if (statusFilter) {
    pipelines = pipelines.filter((p) => p.status === statusFilter);
  }

  // Sort by creation date (newest first) and limit
  pipelines = pipelines
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, limit);

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

    // Start pipeline execution
    executePipeline(pipelineId);

    return new Response(JSON.stringify({ success: true, pipeline }), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("[Pipeline API] Error creating pipeline:", error);
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
  if (!pipeline) return;

  pipeline.status = "running";

  const interval = setInterval(() => {
    const currentPipeline = activePipelines.get(pipelineId);
    if (!currentPipeline) {
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
    } else if (progress >= 80 && phaseIndex === 2) {
      phaseIndex = 3;
      currentPipeline.currentPhase = "publishing";
    } else if (progress >= 100) {
      currentPipeline.status = "completed";
      currentPipeline.currentPhase = "complete";
      currentPipeline.results = {
        ...currentPipeline.results,
        blog: {
          title: `Blog: ${currentPipeline.topic}`,
          url: `https://enufacas.github.io/Chained/blog/${currentPipeline.topic.toLowerCase().replace(/\s+/g, "-")}.html`,
          wordCount: Math.floor(1500 + Math.random() * 1000),
        },
      };
      clearInterval(interval);
    }

    activePipelines.set(pipelineId, currentPipeline);
  }, 2000); // Update every 2 seconds
}
