/**
 * Shared types for AG-UI Frontend
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
  provider: "gemini" | "openai" | "none";
  model: string;
  error?: string;
  timestamp: string;
}
