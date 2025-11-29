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
  const [a2aStatus, setA2aStatus] = useState<{
    available: boolean;
    checked: boolean;
  }>({ available: false, checked: false });

  // Check if A2A endpoint is available
  useEffect(() => {
    const checkA2A = async () => {
      try {
        const res = await fetch("/api/copilotkit-a2a");
        const data = await res.json();
        setA2aStatus({
          available: data.adkApiServer?.available || false,
          checked: true,
        });
      } catch {
        setA2aStatus({ available: false, checked: true });
      }
    };
    checkA2A();
  }, []);

  if (!a2aStatus.checked) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="text-slate-400 animate-pulse">
          Checking A2A agents...
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Status banner */}
      {!a2aStatus.available && (
        <div className="bg-yellow-500/10 border-b border-yellow-500/30 px-4 py-2 text-sm text-yellow-400">
          ⚠️ A2A agents not available. Some features may be limited.
        </div>
      )}
      
      {/* CopilotKit with A2A middleware */}
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
