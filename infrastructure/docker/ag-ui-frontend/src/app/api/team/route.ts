/**
 * Team API Route
 *
 * Provides endpoints for team orchestration:
 * 1. List recipes (GET)
 * 2. Get recipe details (GET ?recipe=id)
 * 3. List sessions (GET ?sessions=true)
 * 4. Create/execute team session (POST)
 *
 * All operations coordinate REAL A2A agents in turn-based execution.
 * Persists artifacts and sessions to localStorage for cross-page persistence.
 */

import { NextRequest } from "next/server";
import {
  saveArtifact,
  saveSession,
} from "@/lib/storage";

// =============================================================================
// Configuration
// =============================================================================

const isDevelopment = process.env.NODE_ENV === "development";

// Agent URLs
const AGENT_URLS: Record<string, string | undefined> = {
  "academic-research": process.env.AGENT_ACADEMIC_RESEARCH_URL || 
    (isDevelopment ? "" : "https://chained-academic-research-sguacxy5gq-uc.a.run.app"),
  "google-trends": process.env.AGENT_GOOGLE_TRENDS_URL || 
    (isDevelopment ? "" : "https://chained-google-trends-sguacxy5gq-uc.a.run.app"),
  "blog-writer": process.env.AGENT_BLOG_WRITER_URL || 
    (isDevelopment ? "" : "https://chained-blog-writer-sguacxy5gq-uc.a.run.app"),
  "code-reviewer": process.env.AGENT_CODE_REVIEWER_URL ||
    (isDevelopment ? "" : "https://chained-code-reviewer-sguacxy5gq-uc.a.run.app"),
  "data-analyst": process.env.AGENT_DATA_ANALYST_URL ||
    (isDevelopment ? "" : "https://chained-data-analyst-sguacxy5gq-uc.a.run.app"),
  "image-generator": process.env.AGENT_IMAGE_GENERATOR_URL ||
    (isDevelopment ? "" : "https://chained-image-generator-sguacxy5gq-uc.a.run.app"),
};

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_TURNS_PER_AGENT = 2;
const MAX_TURNS_PER_AGENT = 5;
const MIN_TURNS_PER_AGENT = 1;

// =============================================================================
// Types
// =============================================================================

interface RecipeStep {
  agentId: string;
  instruction: string;
  required: boolean;
  timeoutSeconds: number;
  dependsOn: string[];
}

interface Recipe {
  id: string;
  name: string;
  description: string;
  goal: string;
  steps: RecipeStep[];
  tags: string[];
}

interface ExecutionConfig {
  maxTurnsPerAgent: number;
  executionMode: "sequential" | "parallel";
}

type TurnStatus = "pending" | "running" | "completed" | "failed" | "skipped";

interface TurnResult {
  stepIndex: number;
  agentId: string;
  agentName: string;
  status: TurnStatus;
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
  taskId?: string;
  contextId?: string;
  message?: string;
  artifacts: Array<{ name: string; type: string; data: string }>;
  error?: string;
  turnNumber?: number;
  // A2A Protocol objects
  agentCard?: object;
  task?: object;
  userMessage?: object;
  agentMessage?: object;
}

interface TeamSession {
  id: string;
  recipeId: string;
  recipeName: string;
  goal: string;
  status: TurnStatus;
  currentTurn: number;
  totalTurns: number;
  createdAt: string;
  updatedAt: string;
  context: Record<string, unknown>;
  turnResults: TurnResult[];
  finalResult?: Record<string, unknown>;
  config?: ExecutionConfig;
}

// =============================================================================
// Built-in Recipes
// =============================================================================

const BUILTIN_RECIPES: Recipe[] = [
  {
    id: "blog-pipeline",
    name: "Blog Writing Pipeline",
    description: "Research, analyze trends, and write a blog post",
    goal: "Create a well-researched, SEO-optimized blog post",
    steps: [
      {
        agentId: "academic-research",
        instruction: "Research the topic thoroughly and identify key concepts, trends, and insights.",
        required: true,
        timeoutSeconds: 120,
        dependsOn: [],
      },
      {
        agentId: "google-trends",
        instruction: "Analyze trending keywords and SEO opportunities based on the research.",
        required: true,
        timeoutSeconds: 120,
        dependsOn: ["academic-research"],
      },
      {
        agentId: "blog-writer",
        instruction: "Write a comprehensive blog post using the research and SEO insights.",
        required: true,
        timeoutSeconds: 180,
        dependsOn: ["academic-research", "google-trends"],
      },
    ],
    tags: ["content", "blog", "seo"],
  },
  {
    id: "technical-review",
    name: "Technical Content Review",
    description: "Research, write, and review technical content with code examples",
    goal: "Create reviewed technical content with code samples",
    steps: [
      {
        agentId: "academic-research",
        instruction: "Research the technical topic and gather key information.",
        required: true,
        timeoutSeconds: 120,
        dependsOn: [],
      },
      {
        agentId: "data-analyst",
        instruction: "Analyze the research data and identify key statistics and patterns.",
        required: false,
        timeoutSeconds: 120,
        dependsOn: ["academic-research"],
      },
      {
        agentId: "blog-writer",
        instruction: "Write technical content including code examples.",
        required: true,
        timeoutSeconds: 180,
        dependsOn: ["academic-research", "data-analyst"],
      },
      {
        agentId: "code-reviewer",
        instruction: "Review any code examples for best practices and correctness.",
        required: false,
        timeoutSeconds: 120,
        dependsOn: ["blog-writer"],
      },
    ],
    tags: ["technical", "code", "review"],
  },
  {
    id: "visual-content",
    name: "Visual Content Creation",
    description: "Research and create visual content with diagrams",
    goal: "Create informative content with supporting visuals",
    steps: [
      {
        agentId: "academic-research",
        instruction: "Research the topic and identify key concepts to visualize.",
        required: true,
        timeoutSeconds: 120,
        dependsOn: [],
      },
      {
        agentId: "image-generator",
        instruction: "Create diagrams and visual content based on the research.",
        required: false,
        timeoutSeconds: 120,
        dependsOn: ["academic-research"],
      },
      {
        agentId: "blog-writer",
        instruction: "Write content that incorporates and explains the visuals.",
        required: true,
        timeoutSeconds: 180,
        dependsOn: ["academic-research", "image-generator"],
      },
    ],
    tags: ["visual", "diagrams", "content"],
  },
  {
    id: "data-analysis",
    name: "Data Analysis Pipeline",
    description: "Analyze data and create visualizations with insights",
    goal: "Generate comprehensive data analysis with visual reports",
    steps: [
      {
        agentId: "data-analyst",
        instruction: "Analyze the provided data and generate key insights.",
        required: true,
        timeoutSeconds: 120,
        dependsOn: [],
      },
      {
        agentId: "image-generator",
        instruction: "Create charts and visualizations based on the analysis.",
        required: false,
        timeoutSeconds: 120,
        dependsOn: ["data-analyst"],
      },
      {
        agentId: "blog-writer",
        instruction: "Write a report summarizing the analysis and visualizations.",
        required: true,
        timeoutSeconds: 180,
        dependsOn: ["data-analyst", "image-generator"],
      },
    ],
    tags: ["data", "analysis", "visualization"],
  },
];

// In-memory session storage
const activeSessions: Map<string, TeamSession> = new Map();

// =============================================================================
// Helpers
// =============================================================================

function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
}

/**
 * Fetch agent card from an agent's well-known endpoint
 */
async function fetchAgentCard(agentUrl: string): Promise<object | null> {
  try {
    const response = await fetch(`${agentUrl}/.well-known/agent.json`, {
      signal: AbortSignal.timeout(5000),
    });
    if (response.ok) {
      return await response.json();
    }
    console.warn(`[Team API] Agent card fetch returned status ${response.status} for ${agentUrl}`);
  } catch (error) {
    console.warn(`[Team API] Failed to fetch agent card from ${agentUrl}:`, error instanceof Error ? error.message : error);
  }
  return null;
}

/**
 * Agent call result with full A2A protocol data
 */
interface AgentCallResult {
  taskId?: string;
  contextId?: string;
  message?: string;
  artifacts: Array<{ name: string; type: string; data: string }>;
  error?: string;
  // A2A Protocol objects
  agentCard?: object;
  task?: object;
  userMessage?: object;
  agentMessage?: object;
}

async function callAgent(
  agentId: string,
  message: string,
  context: Record<string, unknown>,
  referenceTaskIds: string[] = []
): Promise<AgentCallResult> {
  const agentUrl = AGENT_URLS[agentId];
  
  if (!agentUrl) {
    return { error: `Agent ${agentId} not configured`, artifacts: [] };
  }
  
  try {
    // Fetch agent card for A2A protocol compliance
    const agentCard = await fetchAgentCard(agentUrl);
    
    const contextId = (context.contextId as string) || `team-${Date.now()}`;
    const userMessage = {
      role: "user",
      parts: [{ text: message }],
      timestamp: new Date().toISOString(),
    };
    
    const response = await fetch(`${agentUrl}/a2a/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userMessage,
        contextId,
        metadata: context,
        referenceTaskIds,
      }),
    });
    
    if (!response.ok) {
      return { error: `Agent returned ${response.status}`, artifacts: [], agentCard: agentCard || undefined };
    }
    
    const task = await response.json();
    
    // Extract agent message from task response
    const agentMessage = task.status?.message ? {
      ...task.status.message,
      timestamp: new Date().toISOString(),
      taskId: task.id,
    } : undefined;
    
    return {
      taskId: task.id,
      contextId,
      message: task.status?.message?.parts?.[0]?.text,
      artifacts: task.artifacts || [],
      // A2A Protocol objects
      agentCard: agentCard || undefined,
      task,
      userMessage,
      agentMessage,
    };
  } catch (error) {
    return { error: error instanceof Error ? error.message : "Unknown error", artifacts: [] };
  }
}

async function executeTurn(
  session: TeamSession,
  step: RecipeStep,
  stepIndex: number
): Promise<TurnResult> {
  const startedAt = new Date().toISOString();
  
  const turnResult: TurnResult = {
    stepIndex,
    agentId: step.agentId,
    agentName: step.agentId,
    status: "running",
    startedAt,
    artifacts: [],
  };
  
  // Build instruction with context
  const fullInstruction = `Goal: ${session.goal}

${step.instruction}

Previous context and findings:
${JSON.stringify(session.context, null, 2)}`;
  
  // Get reference task IDs from dependencies
  const referenceTaskIds: string[] = [];
  for (const dep of step.dependsOn) {
    const prevResult = session.turnResults.find((r) => r.agentId === dep && r.taskId);
    if (prevResult?.taskId) {
      referenceTaskIds.push(prevResult.taskId);
    }
  }
  
  // Call the agent
  const result = await callAgent(step.agentId, fullInstruction, session.context, referenceTaskIds);
  
  const completedAt = new Date().toISOString();
  const durationMs = new Date(completedAt).getTime() - new Date(startedAt).getTime();
  
  turnResult.completedAt = completedAt;
  turnResult.durationMs = durationMs;
  turnResult.taskId = result.taskId;
  turnResult.contextId = result.contextId;
  turnResult.message = result.message;
  turnResult.artifacts = result.artifacts;
  
  // Store A2A protocol objects
  turnResult.agentCard = result.agentCard;
  turnResult.task = result.task;
  turnResult.userMessage = result.userMessage;
  turnResult.agentMessage = result.agentMessage;
  
  // Add A2A protocol objects as artifacts using vendor MIME types (RFC 6838)
  if (result.agentCard) {
    turnResult.artifacts.push({
      name: `${step.agentId}-agent-card`,
      type: "application/vnd.a2a.agent-card+json",
      data: JSON.stringify(result.agentCard, null, 2),
    });
  }
  
  if (result.task) {
    turnResult.artifacts.push({
      name: `${step.agentId}-task`,
      type: "application/vnd.a2a.task+json",
      data: JSON.stringify(result.task, null, 2),
    });
  }
  
  if (result.userMessage) {
    turnResult.artifacts.push({
      name: `${step.agentId}-user-message`,
      type: "application/vnd.a2a.message+json",
      data: JSON.stringify(result.userMessage, null, 2),
    });
  }
  
  if (result.agentMessage) {
    turnResult.artifacts.push({
      name: `${step.agentId}-agent-message`,
      type: "application/vnd.a2a.message+json",
      data: JSON.stringify(result.agentMessage, null, 2),
    });
  }
  
  if (result.error) {
    turnResult.status = step.required ? "failed" : "skipped";
    turnResult.error = result.error;
  } else {
    turnResult.status = "completed";
    
    // Update context with artifacts
    session.context[`${step.agentId}_artifacts`] = result.artifacts;
    session.context[`${step.agentId}_task_id`] = result.taskId;
    
    // Parse JSON artifacts into context
    for (const artifact of result.artifacts) {
      if (artifact.type === "application/json") {
        try {
          const data = JSON.parse(artifact.data);
          session.context[`${step.agentId}_${artifact.name.replace(/-/g, "_")}`] = data;
        } catch {
          // Skip non-JSON artifacts
        }
      }
    }
    
    // Persist artifacts to localStorage
    persistTurnArtifacts(turnResult, session);
  }
  
  return turnResult;
}

/**
 * Persist turn artifacts to localStorage for cross-page access
 */
function persistTurnArtifacts(turnResult: TurnResult, session: TeamSession): void {
  try {
    const sourceType = session.recipeId.startsWith("custom-") ? "team" : "recipe";
    const storedArtifactIds: string[] = [];
    
    // Save all artifacts from this turn
    for (const artifact of turnResult.artifacts) {
      const stored = saveArtifact({
        name: artifact.name,
        type: artifact.type,
        data: artifact.data,
        preview: artifact.data.substring(0, 200),
        source: sourceType,
        sourceId: session.id,
        sourceName: session.recipeName,
        agentName: turnResult.agentName,
        phase: `Turn ${turnResult.turnNumber || 1}`,
        // A2A Protocol metadata
        a2aType: artifact.type.includes("vnd.a2a.agent-card") ? "agent-card" :
                 artifact.type.includes("vnd.a2a.task") ? "task" :
                 artifact.type.includes("vnd.a2a.message") ? "message" : undefined,
        taskId: turnResult.taskId,
        contextId: turnResult.contextId,
      });
      storedArtifactIds.push(stored.id);
    }
    
    // Update or create session record with artifact IDs
    const existingSession = typeof window !== 'undefined' ? 
      (() => {
        try {
          const data = localStorage.getItem("ag-ui-sessions");
          const sessions = data ? JSON.parse(data) : [];
          return sessions.find((s: { id: string }) => s.id === session.id);
        } catch {
          return null;
        }
      })() : null;
    
    const artifactIds = existingSession?.artifacts || [];
    saveSession({
      id: session.id,
      type: sourceType,
      name: session.recipeName,
      topic: session.goal,
      status: session.status,
      completedAt: session.status === "completed" ? session.updatedAt : undefined,
      artifacts: [...artifactIds, ...storedArtifactIds],
      metadata: {
        currentTurn: session.currentTurn,
        totalTurns: session.totalTurns,
        recipeId: session.recipeId,
        // Include turnResults progressively as they complete
        // This ensures data is available even if session is interrupted
        turnResults: session.turnResults,
        config: session.config,
      },
      a2aContextId: session.context.contextId as string,
    });
  } catch (error) {
    console.warn("[Team API] Failed to persist artifacts:", error);
  }
}

// =============================================================================
// API Routes
// =============================================================================

/**
 * GET /api/team
 *
 * Query params:
 * - recipe: Get specific recipe by ID
 * - sessions: List active sessions (true/false)
 * - session: Get specific session by ID
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const recipeId = searchParams.get("recipe");
  const showSessions = searchParams.get("sessions") === "true";
  const sessionId = searchParams.get("session");
  
  // Get specific session
  if (sessionId) {
    const session = activeSessions.get(sessionId);
    if (!session) {
      return new Response(JSON.stringify({ error: "Session not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }
    return new Response(JSON.stringify(session), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }
  
  // List sessions
  if (showSessions) {
    const sessions = Array.from(activeSessions.values())
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    
    return new Response(
      JSON.stringify({
        sessions,
        total: sessions.length,
        active: sessions.filter((s) => s.status === "running").length,
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
  
  // Get specific recipe
  if (recipeId) {
    const recipe = BUILTIN_RECIPES.find((r) => r.id === recipeId);
    if (!recipe) {
      return new Response(JSON.stringify({ error: "Recipe not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }
    return new Response(JSON.stringify(recipe), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }
  
  // List all recipes
  return new Response(
    JSON.stringify({
      recipes: BUILTIN_RECIPES,
      total: BUILTIN_RECIPES.length,
    }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
}

/**
 * Initialize a session (does not start execution)
 */
function initializeSession(
  recipeId: string,
  recipeName: string,
  goal: string,
  totalTurns: number,
  initialContext: Record<string, unknown>,
  config: ExecutionConfig
): TeamSession {
  const sessionId = generateSessionId();
  const now = new Date().toISOString();
  
  const session: TeamSession = {
    id: sessionId,
    recipeId,
    recipeName,
    goal,
    status: "pending",
    currentTurn: 0,
    totalTurns,
    createdAt: now,
    updatedAt: now,
    context: { ...initialContext, goal, contextId: sessionId },
    turnResults: [],
    config,
  };
  
  activeSessions.set(sessionId, session);
  return session;
}

/**
 * Execute session asynchronously (updates activeSessions in place)
 */
async function executeSessionAsync(
  sessionId: string,
  recipe: Recipe,
  config: ExecutionConfig
): Promise<void> {
  const session = activeSessions.get(sessionId);
  if (!session) return;
  
  session.status = "running";
  session.updatedAt = new Date().toISOString();
  activeSessions.set(sessionId, session);
  
  if (config.executionMode === "parallel") {
    // Parallel execution - run all agents in parallel for each turn
    for (let turn = 0; turn < config.maxTurnsPerAgent; turn++) {
      const turnPromises = recipe.steps.map(async (step, i) => {
        const turnResult = await executeTurn(session, step, i + turn * recipe.steps.length);
        turnResult.turnNumber = turn + 1;
        return turnResult;
      });
      
      const turnResults = await Promise.all(turnPromises);
      session.turnResults.push(...turnResults);
      session.currentTurn = (turn + 1) * recipe.steps.length;
      session.updatedAt = new Date().toISOString();
      activeSessions.set(sessionId, session);
      
      // Check for required failures
      const hasRequiredFailure = turnResults.some((result, i) => 
        result.status === "failed" && recipe.steps[i].required
      );
      if (hasRequiredFailure) {
        session.status = "failed";
        break;
      }
    }
  } else {
    // Sequential execution - run agents one at a time
    let stepIndex = 0;
    for (let turn = 0; turn < config.maxTurnsPerAgent; turn++) {
      for (let i = 0; i < recipe.steps.length; i++) {
        const step = recipe.steps[i];
        
        const turnResult = await executeTurn(session, step, stepIndex);
        turnResult.turnNumber = turn + 1;
        session.turnResults.push(turnResult);
        
        // Update currentTurn AFTER turn execution completes (not before)
        // This ensures consistency with parallel mode and avoids showing
        // progress that hasn't been achieved yet
        stepIndex++;
        session.currentTurn = stepIndex;
        session.updatedAt = new Date().toISOString();
        activeSessions.set(sessionId, session);
        
        // Stop on required failure
        if (turnResult.status === "failed" && step.required) {
          session.status = "failed";
          break;
        }
      }
      
      if (session.status === "failed") break;
    }
  }
  
  // Mark complete - atomically update status, currentTurn, and timestamp
  // to avoid race conditions where polling sees inconsistent state
  if (session.status !== "failed") {
    session.status = "completed";
    // Ensure currentTurn equals totalTurns when completed
    session.currentTurn = session.totalTurns;
  }
  
  session.updatedAt = new Date().toISOString();
  
  // Build final result
  session.finalResult = {
    sessionId,
    recipe: recipe.name,
    goal: session.goal,
    status: session.status,
    turnsCompleted: session.turnResults.filter((t) => t.status === "completed").length,
    turnsTotal: session.totalTurns,
    context: session.context,
    config,
  };
  
  // Atomically persist the completed session state to activeSessions
  activeSessions.set(sessionId, session);
  
  // Final persistence update with completion status
  try {
    const sourceType = recipe.id.startsWith("custom-") ? "team" : "recipe";
    saveSession({
      id: session.id,
      type: sourceType,
      name: session.recipeName,
      topic: session.goal,
      status: session.status,
      completedAt: session.status === "completed" ? session.updatedAt : undefined,
      artifacts: [], // Artifacts already saved during turns
      metadata: {
        currentTurn: session.currentTurn,
        totalTurns: session.totalTurns,
        recipeId: session.recipeId,
        finalResult: session.finalResult,
        // CRITICAL: Include complete turnResults with all A2A protocol objects
        // This preserves high-fidelity data for session history after page reloads
        turnResults: session.turnResults,
        config: session.config,
      },
      a2aContextId: session.context.contextId as string,
    });
  } catch (error) {
    console.warn("[Team API] Failed to persist final session state:", error);
  }
}

/**
 * POST /api/team
 *
 * Execute a team session
 *
 * Body:
 * - recipeId: Recipe to execute (optional if agentIds provided)
 * - agentIds: Custom agent IDs (optional if recipeId provided)
 * - goal: Specific goal for this session
 * - context: Optional initial context
 * - config: Optional execution configuration
 *   - maxTurnsPerAgent: Number of turns per agent (1-5, default 2)
 *   - executionMode: "sequential" or "parallel" (default "sequential")
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { recipeId, agentIds, goal, context, config } = body;
    
    // Validate goal
    if (!goal) {
      return new Response(JSON.stringify({ error: "goal is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }
    
    // Validate execution config
    const executionConfig: ExecutionConfig = {
      maxTurnsPerAgent: Math.min(
        Math.max(config?.maxTurnsPerAgent || DEFAULT_TURNS_PER_AGENT, MIN_TURNS_PER_AGENT),
        MAX_TURNS_PER_AGENT
      ),
      executionMode: config?.executionMode === "parallel" ? "parallel" : "sequential",
    };
    
    let recipe: Recipe;
    
    // Check for custom team execution
    if (agentIds && Array.isArray(agentIds) && agentIds.length > 0) {
      // Create custom recipe from agent IDs
      const customRecipeId = `custom-${Date.now()}`;
      recipe = {
        id: customRecipeId,
        name: "Custom Team",
        description: "Custom team execution from Agent Canvas",
        goal,
        steps: agentIds.map((agentId: string) => ({
          agentId,
          instruction: `Execute your specialized task for: ${goal}`,
          required: false,
          timeoutSeconds: 120,
          dependsOn: [],
        })),
        tags: ["custom"],
      };
    } else if (recipeId) {
      // Recipe-based execution
      const foundRecipe = BUILTIN_RECIPES.find((r) => r.id === recipeId);
      if (!foundRecipe) {
        return new Response(
          JSON.stringify({ error: `Recipe ${recipeId} not found` }),
          {
            status: 404,
            headers: { "Content-Type": "application/json" },
          }
        );
      }
      recipe = foundRecipe;
    } else {
      return new Response(
        JSON.stringify({ error: "Either recipeId or agentIds is required" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
    
    // Calculate total turns based on config
    const totalTurns = recipe.steps.length * executionConfig.maxTurnsPerAgent;
    
    // Initialize session without executing
    const session = initializeSession(
      recipe.id,
      recipe.name,
      goal,
      totalTurns,
      context || {},
      executionConfig
    );
    
    // Start execution asynchronously (don't await)
    // The execution updates activeSessions in place, allowing polling to work
    executeSessionAsync(session.id, recipe, executionConfig).catch((error) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      const errorStack = error instanceof Error ? error.stack : undefined;
      console.error(`[Team API] Async execution error for session ${session.id}:`, {
        sessionId: session.id,
        recipeId: recipe.id,
        error: errorMessage,
        stack: errorStack,
      });
      const s = activeSessions.get(session.id);
      if (s) {
        s.status = "failed";
        s.updatedAt = new Date().toISOString();
        activeSessions.set(session.id, s);
      }
    });
    
    // Return immediately with the pending session
    return new Response(JSON.stringify({ success: true, session }), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("[Team API] Error:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Failed to execute team session",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
