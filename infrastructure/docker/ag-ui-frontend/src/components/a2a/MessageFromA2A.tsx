/**
 * Displays incoming A2A responses (Agent → Orchestrator).
 * Shows when an agent has completed processing and returned results.
 */

"use client";

import React from "react";
import { getAgentStyle, getAgentDisplayName } from "./agent-styles";

type MessageActionRenderProps = {
  status: string;
  args: {
    agentName?: string;
  };
};

export const MessageFromA2A: React.FC<MessageActionRenderProps> = ({ status, args }) => {
  // Only render when complete
  if (status !== "complete") {
    return null;
  }

  if (!args.agentName) {
    return null;
  }

  const agentStyle = getAgentStyle(args.agentName);
  const displayName = getAgentDisplayName(args.agentName);

  return (
    <div className="my-2">
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg px-4 py-3">
        <div className="flex items-center gap-3">
          {/* Sender/Receiver badges */}
          <div className="flex items-center gap-2 min-w-[200px] flex-shrink-0">
            <div className="flex flex-col items-center">
              <span
                className={`px-3 py-1 rounded-full text-xs font-semibold border ${agentStyle.bgColor} ${agentStyle.textColor} ${agentStyle.borderColor} flex items-center gap-1`}
              >
                <span>{agentStyle.icon}</span>
                <span>{displayName}</span>
              </span>
              {agentStyle.framework && (
                <span className="text-[9px] text-slate-500 mt-0.5">{agentStyle.framework}</span>
              )}
            </div>

            <span className="text-slate-500 text-sm">→</span>

            <div className="flex flex-col items-center">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-700 text-slate-200 border border-slate-600">
                🎯 Orchestrator
              </span>
              <span className="text-[9px] text-slate-500 mt-0.5">ADK</span>
            </div>
          </div>

          {/* Status message */}
          <span className="text-xs text-blue-400 flex items-center gap-1">
            <span className="text-green-400">✓</span> Response received
          </span>
        </div>
      </div>
    </div>
  );
};
