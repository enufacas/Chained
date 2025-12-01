/**
 * Shared types for AG-UI Frontend
 * 
 * @see docs/a2a-ui/README.md for documentation
 */

// Agent types
export interface Agent {
  name: string;
  id: string;
  icon: string;
  description: string;
  skills: string[];
  status: "pending" | "working" | "completed" | "failed";
  taskId?: string;
  artifacts: { name: string; type: string }[];
}

// =============================================================================
// A2A Protocol Types
// =============================================================================

/**
 * A2A Agent Card - Standard agent.json structure
 * @see https://a2a-protocol.org/spec/agent-card
 */
export interface A2AAgentCard {
  name: string;
  description: string;
  version: string;
  protocolVersion: string;
  provider?: string;
  skills: Array<{
    id: string;
    name: string;
    description: string;
    tags: string[];
    inputModes?: string[];
    outputModes?: string[];
  }>;
  capabilities?: {
    streaming?: boolean;
    pushNotifications?: boolean;
    stateTransitionHistory?: boolean;
  };
  defaultInputModes?: string[];
  defaultOutputModes?: string[];
  url?: string;
}

/**
 * A2A Task - Represents a task in the A2A protocol
 */
export interface A2ATask {
  id: string;
  contextId: string;
  status: {
    state: "submitted" | "working" | "input_required" | "completed" | "failed" | "canceled";
    message?: {
      role: "agent" | "user";
      parts: Array<{ type?: string; text?: string; data?: string; mimeType?: string }>;
    };
    timestamp?: string;
  };
  artifacts?: Array<{
    name: string;
    parts: Array<{ type?: string; text?: string; data?: string; mimeType?: string }>;
  }>;
  history?: Array<{
    state: string;
    message?: object;
    timestamp?: string;
  }>;
}

/**
 * A2A Message - Standard message structure in A2A protocol
 */
export interface A2AMessage {
  id?: string;
  role: "user" | "agent";
  parts: Array<{
    type?: string;
    text?: string;
    data?: string;
    mimeType?: string;
    metadata?: Record<string, unknown>;
  }>;
  timestamp?: string;
  taskId?: string;
  agentName?: string;
}

// Pipeline run from GitHub Actions
export interface PipelineRun {
  id: number;
  runNumber: number;
  createdAt: string;
  conclusion: "success" | "failure";
  htmlUrl: string;
}

// Pipeline data structure
export interface PipelineData {
  contextId: string;
  success: boolean;
  tasksCompleted: number;
  completedAt: string;
  research: {
    taskId: string;
    status: string;
    findings: {
      topicsFound: number;
      recommendedTopic: {
        topic: string;
        domain: string;
        blogAngle: string;
        keyPoints: string[];
        seoKeywords: string[];
      };
    };
  };
  trends: {
    taskId: string;
    status: string;
    trendsData: {
      topicsAnalyzed: number;
      trendingKeywords: string[];
      recommendedFocus: string;
    };
  };
  blog: {
    taskId: string;
    status: string;
    deploymentInfo: {
      url: string;
      status: string;
    };
    blogMetadata: {
      title: string;
      wordCount: number;
      readTimeMinutes: number;
      tags: string[];
    };
  };
}

// API Status
export interface ApiStatus {
  checking: boolean;
  available: boolean;
  provider: "vertex-ai" | "gemini" | "openai" | "none";
  model: string;
  error?: string;
  timestamp: string;
}

// =============================================================================
// A2A Step Detail Types (shared between API and components)
// =============================================================================

/**
 * Artifact captured from an A2A agent task
 */
export interface A2AStepArtifact {
  name: string;
  type: string;
  data: string;
  preview?: string;  // First 200 chars for UI preview
}

/**
 * Detailed information about a single A2A step in a pipeline
 * Captures task ID, timing, artifacts, and response for deep dive capability
 */
export interface A2AStepDetail {
  taskId: string;
  agentName: string;
  phase: string;
  status: "pending" | "running" | "completed" | "failed";
  startTime: string;
  endTime?: string;
  durationMs?: number;
  message?: string;
  artifacts: A2AStepArtifact[];
  rawResponse?: object;  // Full A2A task response for debugging
}

// =============================================================================
// Pipeline Types
// =============================================================================

export type PipelineStatus = "pending" | "running" | "completed" | "failed";

/**
 * Pipeline result interface - used by both API route and UI components
 */
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
  // Detailed A2A step history for deep dive into runs
  a2aSteps?: A2AStepDetail[];
  // Total execution time
  totalDurationMs?: number;
}
