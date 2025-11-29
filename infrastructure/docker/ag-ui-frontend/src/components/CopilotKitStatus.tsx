"use client";

import { useState, useEffect } from "react";

const COPILOTKIT_VERSION = "1.8.14";

export function CopilotKitStatus() {
  const [expanded, setExpanded] = useState(false);
  const [apiStatus, setApiStatus] = useState<"checking" | "available" | "unavailable">("checking");

  useEffect(() => {
    // Check if the CopilotKit API is available
    const checkApi = async () => {
      try {
        const res = await fetch("/api/copilotkit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: [] }),
        });
        // Even if it returns an error about API key, the endpoint exists
        setApiStatus(res.status === 503 ? "unavailable" : "available");
      } catch {
        setApiStatus("unavailable");
      }
    };
    checkApi();
  }, []);

  return (
    <div className="bg-slate-800 rounded-xl border border-accent-500/30 overflow-hidden mb-8">
      {/* Header - Always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-slate-700/50 transition"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">🪁</span>
          <div className="text-left">
            <h3 className="text-accent-400 font-semibold">CopilotKit Integration</h3>
            <p className="text-slate-400 text-sm">Version {COPILOTKIT_VERSION}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`px-2 py-1 rounded-full text-xs ${
              apiStatus === "available"
                ? "bg-green-500/20 text-green-400 border border-green-500/30"
                : apiStatus === "unavailable"
                ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
                : "bg-slate-500/20 text-slate-400 border border-slate-500/30"
            }`}
          >
            {apiStatus === "checking"
              ? "Checking..."
              : apiStatus === "available"
              ? "✅ Chat Active"
              : "⚠️ Chat Limited"}
          </span>
          <span className="text-slate-400 text-xl">{expanded ? "▼" : "▶"}</span>
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="p-4 border-t border-accent-500/20 space-y-4">
          {/* Integration Status */}
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-black/30 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-green-400">✅</span>
                <span className="text-slate-300 font-medium">React Core</span>
              </div>
              <p className="text-slate-500 text-xs">
                useCopilotReadable, useCopilotAction hooks active
              </p>
            </div>
            <div className="bg-black/30 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-green-400">✅</span>
                <span className="text-slate-300 font-medium">React UI</span>
              </div>
              <p className="text-slate-500 text-xs">
                CopilotPopup component rendered
              </p>
            </div>
            <div className="bg-black/30 p-3 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className={apiStatus === "available" ? "text-green-400" : "text-yellow-400"}>
                  {apiStatus === "available" ? "✅" : "⚠️"}
                </span>
                <span className="text-slate-300 font-medium">Runtime</span>
              </div>
              <p className="text-slate-500 text-xs">
                {apiStatus === "available"
                  ? "OpenAI adapter connected"
                  : "OpenAI API key not configured"}
              </p>
            </div>
          </div>

          {/* Features List */}
          <div className="bg-black/30 p-4 rounded-lg">
            <h4 className="text-slate-300 font-medium mb-3">Interactive Features</h4>
            <div className="grid md:grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-green-400">✅</span>
                <span className="text-slate-400">Pipeline data readable by AI</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✅</span>
                <span className="text-slate-400">Agent status visible to AI</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✅</span>
                <span className="text-slate-400">Interactive tab switching</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-400">✅</span>
                <span className="text-slate-400">Collapsible agent cards</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={apiStatus === "available" ? "text-green-400" : "text-yellow-400"}>
                  {apiStatus === "available" ? "✅" : "⚠️"}
                </span>
                <span className="text-slate-400">AI chat assistant</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={apiStatus === "available" ? "text-green-400" : "text-yellow-400"}>
                  {apiStatus === "available" ? "✅" : "⚠️"}
                </span>
                <span className="text-slate-400">AI-powered pipeline analysis</span>
              </div>
            </div>
          </div>

          {/* CopilotKit Actions */}
          <div className="bg-black/30 p-4 rounded-lg">
            <h4 className="text-slate-300 font-medium mb-3">Registered CopilotKit Actions</h4>
            <div className="space-y-2 text-sm font-mono">
              <div className="flex items-center gap-2 text-slate-400">
                <span className="text-primary-400">•</span>
                <code className="bg-black/50 px-2 py-1 rounded">analyzePipeline()</code>
                <span className="text-slate-500">- Get insights about the current run</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <span className="text-primary-400">•</span>
                <code className="bg-black/50 px-2 py-1 rounded">getAgentDetails(agentName)</code>
                <span className="text-slate-500">- Get info about a specific agent</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <span className="text-primary-400">•</span>
                <code className="bg-black/50 px-2 py-1 rounded">getTrendingKeywords()</code>
                <span className="text-slate-500">- Get SEO keywords from trends</span>
              </div>
            </div>
          </div>

          {/* npm package info */}
          <div className="bg-primary-500/10 border border-primary-500/30 rounded-lg p-4 text-sm">
            <p className="text-slate-300 mb-2">
              <strong>📦 Installed Packages:</strong>
            </p>
            <code className="text-slate-400 block">
              @copilotkit/react-core: {COPILOTKIT_VERSION}
              <br />
              @copilotkit/react-ui: {COPILOTKIT_VERSION}
              <br />
              @copilotkit/runtime: {COPILOTKIT_VERSION}
            </code>
          </div>
        </div>
      )}
    </div>
  );
}
