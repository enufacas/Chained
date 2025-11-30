/**
 * Pipeline API Route
 *
 * Provides endpoints for:
 * 1. Creating new pipelines (POST)
 * 2. Getting pipeline status (GET with query params)
 * 3. Listing active/recent pipelines (GET)
 *
 * This bridges the AG-UI frontend with the GitHub Actions workflows and
 * GitHub Issues that track pipeline execution.
 */

import { NextRequest } from "next/server";

// GitHub API configuration
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
const GITHUB_REPO = process.env.GITHUB_REPO || "enufacas/Chained";

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
  workflowRunId?: number;
  issueNumber?: number;
  results?: {
    research?: { topic: string; domain: string; keywords: string[] };
    trends?: { trendingKeywords: string[]; recommendedFocus: string };
    blog?: { title: string; url: string; wordCount: number };
  };
}

// In-memory store for demo pipelines (in production, use a database)
const activePipelines: Map<string, Pipeline> = new Map();

// Simulated pipelines for demo purposes
const DEMO_PIPELINES: Pipeline[] = [
  {
    id: "pipeline-demo-001",
    topic: "Large Language Model Reasoning",
    status: "completed",
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1 hour ago
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
    const pipeline = activePipelines.get(pipelineId) || DEMO_PIPELINES.find((p) => p.id === pipelineId);

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
  let pipelines = [...Array.from(activePipelines.values()), ...DEMO_PIPELINES];

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
 * Body:
 * - topic: The topic to research (required)
 * - triggerWorkflow: Whether to trigger the GitHub Actions workflow (optional, default: false)
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { topic, triggerWorkflow = false } = body;

    if (!topic || typeof topic !== "string" || topic.trim().length === 0) {
      return new Response(JSON.stringify({ error: "Topic is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Generate a unique pipeline ID
    const pipelineId = `pipeline-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
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

    // If we have GitHub credentials and want to trigger a workflow
    if (triggerWorkflow && GITHUB_TOKEN) {
      try {
        // Trigger the GitHub Actions workflow
        const [owner, repo] = GITHUB_REPO.split("/");
        const dispatchResponse = await fetch(
          `https://api.github.com/repos/${owner}/${repo}/actions/workflows/adk-a2a-blog-pipeline.yml/dispatches`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${GITHUB_TOKEN}`,
              Accept: "application/vnd.github.v3+json",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              ref: "main",
              inputs: {
                topic_query: topic.trim(),
                dry_run: "false",
                debug: "false",
              },
            }),
          }
        );

        if (dispatchResponse.ok || dispatchResponse.status === 204) {
          pipeline.status = "running";
          console.log(`[Pipeline API] Workflow dispatched for topic: ${topic}`);
        } else {
          const errorText = await dispatchResponse.text();
          console.error(`[Pipeline API] Failed to dispatch workflow: ${errorText}`);
          // Continue anyway, pipeline will be in pending state
        }
      } catch (workflowError) {
        console.error("[Pipeline API] Error dispatching workflow:", workflowError);
        // Continue anyway, pipeline will be in pending state
      }
    }

    // Store the pipeline
    activePipelines.set(pipelineId, pipeline);

    // Start simulated progress if not triggering real workflow
    if (!triggerWorkflow || !GITHUB_TOKEN) {
      simulatePipelineProgress(pipelineId);
    }

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
 * Simulate pipeline progress for demo purposes
 */
function simulatePipelineProgress(pipelineId: string) {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const phases: Array<Pipeline["currentPhase"]> = ["research", "trends", "writing", "publishing", "complete"];
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

    // Progress through phases
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
  }, 2000); // Update every 2 seconds for demo
}
