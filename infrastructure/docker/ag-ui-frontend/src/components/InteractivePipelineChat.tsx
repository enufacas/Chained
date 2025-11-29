/**
 * Interactive Pipeline Chat Component
 * 
 * Uses CopilotKit with A2A middleware to enable interactive agent execution.
 * Users can request work like "write a new blog post" and see agents coordinate in real-time.
 */

"use client";

import React, { useEffect, useState } from "react";
import { CopilotKit, useCopilotChat, useCopilotAction } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { MessageToA2A, MessageFromA2A } from "./a2a";

// Types for pipeline results
export type ResearchData = {
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

export type TrendsData = {
  taskId: string;
  status: string;
  trendsData: {
    topicsAnalyzed: number;
    trendingKeywords: string[];
    recommendedFocus: string;
  };
};

export type BlogData = {
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

type PipelineCallbacks = {
  onResearchUpdate: (data: ResearchData | null) => void;
  onTrendsUpdate: (data: TrendsData | null) => void;
  onBlogUpdate: (data: BlogData | null) => void;
  onAgentActivity: (agentName: string, status: "working" | "completed" | "failed") => void;
};

const ChatInner = ({ onResearchUpdate, onTrendsUpdate, onBlogUpdate, onAgentActivity }: PipelineCallbacks) => {
  const { visibleMessages } = useCopilotChat();

  // Extract structured JSON from A2A agent responses and pass to parent
  useEffect(() => {
    const extractDataFromMessages = () => {
      for (const message of visibleMessages) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const msg = message as any;

        if (msg.type === "ResultMessage" && msg.actionName === "send_message_to_a2a_agent") {
          try {
            const result = msg.result;
            let parsed;

            if (typeof result === "string") {
              let cleanResult = result;
              if (result.startsWith("A2A Agent Response: ")) {
                cleanResult = result.substring("A2A Agent Response: ".length);
              }
              try {
                parsed = JSON.parse(cleanResult);
              } catch {
                continue;
              }
            } else if (typeof result === "object") {
              parsed = result;
            } else {
              continue;
            }

            // Detect response type by structure
            if (parsed.findings && parsed.findings.recommendedTopic) {
              onResearchUpdate(parsed as ResearchData);
              onAgentActivity("academic-research", "completed");
            } else if (parsed.trendsData && parsed.trendsData.trendingKeywords) {
              onTrendsUpdate(parsed as TrendsData);
              onAgentActivity("google-trends", "completed");
            } else if (parsed.deploymentInfo || parsed.blogMetadata) {
              onBlogUpdate(parsed as BlogData);
              onAgentActivity("blog-writer", "completed");
            }
          } catch (e) {
            console.error("Failed to extract data from message:", e);
          }
        }
      }
    };

    extractDataFromMessages();
  }, [visibleMessages, onResearchUpdate, onTrendsUpdate, onBlogUpdate, onAgentActivity]);

  // Register action to render A2A message flow visualization
  useCopilotAction({
    name: "send_message_to_a2a_agent",
    description: "Sends a message to an A2A agent",
    available: "frontend",
    parameters: [
      {
        name: "agentName",
        type: "string",
        description: "The name of the A2A agent to send the message to",
      },
      {
        name: "task",
        type: "string",
        description: "The message to send to the A2A agent",
      },
    ],
    render: (actionRenderProps) => {
      // Notify parent about agent activity
      if (actionRenderProps.args.agentName) {
        const status = actionRenderProps.status === "complete" ? "completed" : "working";
        onAgentActivity(actionRenderProps.args.agentName, status);
      }
      
      return (
        <>
          <MessageToA2A {...actionRenderProps} />
          <MessageFromA2A {...actionRenderProps} />
        </>
      );
    },
  });

  return (
    <CopilotChat
      labels={{
        title: "A2A Pipeline Assistant",
        initial: `👋 Hi! I'm your A2A pipeline assistant. I can coordinate multiple agents to write blog posts.

**Try these commands:**
• "Write a blog post about AI agents"
• "Research quantum computing trends"
• "What topics are trending in tech?"

I'll orchestrate 3 specialized agents:
🔬 **Academic Research** - Discovers topics
📈 **Google Trends** - SEO optimization
✍️ **Blog Writer** - Creates content`,
      }}
      className="h-full"
    />
  );
};

type InteractivePipelineChatProps = PipelineCallbacks & {
  className?: string;
};

export function InteractivePipelineChat({ 
  onResearchUpdate, 
  onTrendsUpdate, 
  onBlogUpdate,
  onAgentActivity,
  className = "",
}: InteractivePipelineChatProps) {
  const [status, setStatus] = useState<{
    llmAvailable: boolean;
    a2aAvailable: boolean;
    checked: boolean;
  }>({ llmAvailable: false, a2aAvailable: false, checked: false });

  // Check if LLM and A2A endpoints are available
  // This runs in background - we show chat immediately if LLM is likely available
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch("/api/copilotkit-a2a");
        const data = await res.json();
        setStatus({
          // LLM is available if Gemini or OpenAI is configured
          llmAvailable: data.llmAvailable || data.llmProvider !== "none",
          // A2A agents are available if the ADK API server responds
          a2aAvailable: data.adkApiServer?.available || false,
          checked: true,
        });
      } catch {
        setStatus({ llmAvailable: false, a2aAvailable: false, checked: true });
      }
    };
    checkStatus();
  }, []);

  // Determine the status banner message
  const getStatusBanner = () => {
    if (!status.checked) {
      return null; // Still checking, don't show banner yet
    }
    
    if (!status.llmAvailable) {
      return (
        <div className="bg-red-500/10 border-b border-red-500/30 px-4 py-2 text-sm text-red-400">
          ❌ No LLM configured. Set GOOGLE_API_KEY or OPENAI_API_KEY to enable chat.
        </div>
      );
    }
    
    if (!status.a2aAvailable) {
      return (
        <div className="bg-yellow-500/10 border-b border-yellow-500/30 px-4 py-2 text-sm text-yellow-400">
          ⚠️ A2A agents not available. Chat works but agent coordination is limited.
        </div>
      );
    }
    
    return null; // All systems go
  };

  // Show chat immediately - don't block on status check
  // The chat will work as long as the LLM is configured (checked at build time)
  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Status banner (shows after check completes) */}
      {getStatusBanner()}
      
      {/* CopilotKit with A2A middleware - always render */}
      <div className="flex-1 overflow-hidden">
        <CopilotKit
          runtimeUrl="/api/copilotkit-a2a"
          agent="blog_pipeline"
        >
          <ChatInner
            onResearchUpdate={onResearchUpdate}
            onTrendsUpdate={onTrendsUpdate}
            onBlogUpdate={onBlogUpdate}
            onAgentActivity={onAgentActivity}
          />
        </CopilotKit>
      </div>
    </div>
  );
}
