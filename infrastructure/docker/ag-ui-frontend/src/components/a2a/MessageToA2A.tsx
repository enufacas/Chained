/**
 * Displays outgoing A2A messages (Orchestrator → Agent).
 * Shows the task being sent to an agent with animated status.
 */

"use client";

import React from "react";
import { getAgentStyle, truncateTask, getAgentDisplayName } from "./agent-styles";

type MessageActionRenderProps = {
  status: string;
  args: {
    agentName?: string;
    task?: string;
  };
};

export const MessageToA2A: React.FC<MessageActionRenderProps> = ({ status, args }) => {
  // Only render for executing or complete states
  if (status !== "executing" && status !== "complete") {
    return null;
  }

  if (!args.agentName || !args.task) {
    return null;
  }

  const agentStyle = getAgentStyle(args.agentName);
  const displayName = getAgentDisplayName(args.agentName);
  const isExecuting = status === "executing";

  return (
    <div className={`bg-emerald-500/10 border border-emerald-500/30 rounded-lg px-4 py-3 my-2 ${isExecuting ? "animate-pulse" : ""}`}>
      <div className="flex items-start gap-3">
        {/* Sender/Receiver badges */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <div className="flex flex-col items-center">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-700 text-slate-200 border border-slate-600">
              🎯 Orchestrator
            </span>
            <span className="text-[9px] text-slate-500 mt-0.5">ADK</span>
          </div>

          <span className="text-slate-500 text-sm">→</span>

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
        </div>

        {/* Task message */}
        <div className="flex-1 min-w-0">
          <span className="text-slate-300 text-sm break-words" title={args.task}>
            {truncateTask(args.task)}
          </span>
          {isExecuting && (
            <span className="ml-2 text-xs text-emerald-400">
              ⏳ Processing...
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
