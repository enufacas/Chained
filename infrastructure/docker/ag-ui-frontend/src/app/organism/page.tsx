/**
 * AG-UI 3D Organism Page
 * 
 * A complete redesign of the AG-UI using react-three-fiber for 3D visualization.
 * Component-by-component recreation of the standard AG-UI with 3D humanoid agents.
 * 
 * Based on:
 * - docs/organism.html (3D humanoid agents, cyberpunk style)
 * - docs/ag-organism.html (AG-UI integration patterns)
 * - infrastructure/docker/ag-ui-frontend/src/app/page.tsx (AG-UI logic)
 * 
 * IMPORTANT: This UI uses REAL data only - no simulations or fake data.
 */

"use client";

import { CopilotPopup } from "@copilotkit/react-ui";
import { CopilotKit } from "@copilotkit/react-core";
import { useState, useEffect, useCallback } from "react";
import dynamic from 'next/dynamic';
import ErrorBoundary from "@/components/ErrorBoundary";

// Dynamically import 3D components (client-side only to avoid SSR issues)
const AgentCanvas3D = dynamic(
  () => import('@/components/3d/AgentCanvas3D'),
  { ssr: false, loading: () => <div className="w-full h-full bg-[#0a0e1a] flex items-center justify-center text-cyan-400">LOADING 3D SCENE...</div> }
);

// =============================================================================
// Types
// =============================================================================

interface Agent {
  id: string;
  displayName: string;
  name: string;
  description: string;
  icon: string;
  framework: string;
  status: 'idle' | 'working' | 'completed' | 'failed';
}

interface Artifact {
  id: string;
  agentId: string;
  name: string;
  type: string;
  data: string;
  createdAt: number;
}

// =============================================================================
// Initial Data
// =============================================================================

const INITIAL_AGENTS: Agent[] = [
  {
    id: 'academic-research',
    displayName: 'Academic Research',
    name: 'research-agent',
    description: 'Conducts deep research on academic topics',
    icon: '🔬',
    framework: 'LangGraph',
    status: 'idle',
  },
  {
    id: 'google-trends',
    displayName: 'Google Trends',
    name: 'trends-agent',
    description: 'Analyzes trending topics and search data',
    icon: '📈',
    framework: 'ADK',
    status: 'idle',
  },
  {
    id: 'blog-writer',
    displayName: 'Blog Writer',
    name: 'writer-agent',
    description: 'Creates engaging blog content',
    icon: '✍️',
    framework: 'LangGraph',
    status: 'idle',
  },
];

// =============================================================================
// Main Component
// =============================================================================

export default function OrganismPage() {
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());
  const [prompt, setPrompt] = useState('');
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [systemStatus, setSystemStatus] = useState('IDLE');
  const [activityLog, setActivityLog] = useState<Array<{ timestamp: string; type: string; message: string }>>([
    { timestamp: new Date().toLocaleTimeString(), type: 'system', message: 'System initialized. Select agents and enter a prompt to begin.' }
  ]);

  // Settings
  const [enableBloom, setEnableBloom] = useState(true);
  const [showConnections, setShowConnections] = useState(true);

  const addLog = useCallback((type: string, message: string) => {
    setActivityLog(prev => [
      { timestamp: new Date().toLocaleTimeString(), type, message },
      ...prev.slice(0, 49), // Keep last 50 entries
    ]);
  }, []);

  // Load available agents from API
  useEffect(() => {
    fetch('/api/registry')
      .then(res => res.json())
      .then(data => {
        if (data.agents) {
          setAgents(data.agents.map((a: { id: string; displayName: string; name: string; description: string; icon: string; framework: string }) => ({
            ...a,
            status: 'idle' as const,
          })));
          addLog('system', `Loaded ${data.agents.length} available agents`);
        }
      })
      .catch((err: Error) => {
        console.error('Failed to load agents:', err);
        addLog('error', `Failed to load agents: ${err.message}`);
      });
  }, [addLog]);

  const toggleAgentSelection = (agentId: string) => {
    setSelectedAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentId)) {
        newSet.delete(agentId);
      } else {
        newSet.add(agentId);
      }
      return newSet;
    });
  };

  const executePipeline = async () => {
    if (selectedAgents.size === 0 || !prompt.trim()) {
      addLog('error', 'Please select at least one agent and enter a prompt');
      return;
    }

    setIsExecuting(true);
    setSystemStatus('EXECUTING');
    addLog('system', `Starting pipeline with ${selectedAgents.size} agents`);

    try {
      const response = await fetch('/api/pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: prompt,
          agents: Array.from(selectedAgents),
        }),
      });

      if (!response.ok) {
        throw new Error(`Pipeline failed: ${response.statusText}`);
      }

      const data = await response.json();
      const pipelineId = data.pipeline.id as string;
      addLog('system', `Pipeline created: ${pipelineId}`);

      // Poll for updates
      pollPipeline(pipelineId);

    } catch (error) {
      addLog('error', `Pipeline failed: ${error instanceof Error ? error.message : String(error)}`);
      setSystemStatus('ERROR');
      setIsExecuting(false);
    }
  };

  const pollPipeline = async (pipelineId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/pipeline?id=${pipelineId}`);
        if (!response.ok) return;

        const data = await response.json();
        updateFromPipeline(data.pipeline);

        if (data.pipeline.status === 'completed' || data.pipeline.status === 'failed') {
          clearInterval(pollInterval);
          setSystemStatus(data.pipeline.status.toUpperCase());
          setIsExecuting(false);
        }
      } catch (error) {
        console.error('Pipeline polling failed:', error);
      }
    }, 2000);
  };

  const updateFromPipeline = (pipeline: { a2aSteps?: Array<{
    agentName: string;
    status?: { state?: string; message?: { parts?: Array<{ text?: string }> } };
    artifacts?: Array<{ name: string; type: string; data: string }>;
  }> }) => {
    if (!pipeline.a2aSteps) return;

    pipeline.a2aSteps.forEach((step) => {
      const agentId = step.agentName;
      const status = step.status?.state || 'pending';

      // Update agent status
      setAgents(prev => prev.map(a => 
        a.id === agentId ? { ...a, status: (status === 'idle' || status === 'working' || status === 'completed' || status === 'failed' ? status : 'idle') } : a
      ));

      // Process artifacts
      if (step.artifacts && step.artifacts.length > 0) {
        step.artifacts.forEach((artifact: { name: string; type: string; data: string }) => {
          addLog('artifact', `${step.agentName} created: ${artifact.name} (${artifact.type})`);
          
          const newArtifact: Artifact = {
            id: `${Date.now()}-${Math.random()}`,
            agentId,
            name: artifact.name,
            type: artifact.type,
            data: artifact.data,
            createdAt: Date.now(),
          };
          
          setArtifacts(prev => [...prev, newArtifact]);
        });
      }

      // Log messages
      if (step.status?.message) {
        const messageText = step.status.message.parts?.[0]?.text || '';
        if (messageText) {
          addLog('agent', `${step.agentName}: ${messageText.substring(0, 100)}...`);
        }
      }
    });
  };

  return (
    <ErrorBoundary>
      <CopilotKit runtimeUrl="/api/copilotkit">
        <div className="fixed inset-0 flex flex-col bg-[#0a0e1a] text-cyan-400 overflow-hidden">
          
          {/* Header */}
          <div className="h-[60px] bg-gradient-to-br from-[#0a0e1a] to-[#1a1f3a] border-b-2 border-cyan-400 shadow-[0_2px_20px_rgba(0,255,255,0.3)] flex items-center justify-between px-5 z-50">
            <div className="flex items-center gap-4">
              <a href="/" className="border border-cyan-400 text-cyan-400 px-3 py-2 rounded text-sm hover:bg-cyan-400/20 transition-all">
                🏠 Home
              </a>
              <h1 className="text-2xl font-bold text-cyan-400 [text-shadow:0_0_10px_rgba(0,255,255,0.5)]">
                🤖 AG-ORGANISM 3D - AGENT COORDINATION
              </h1>
            </div>
            <div className="text-sm font-mono text-magenta-400">
              STATUS: {systemStatus}
            </div>
          </div>

          {/* Main Container */}
          <div className="flex-1 flex overflow-hidden">
            
            {/* Left Panel - Agent Selection */}
            <div className="w-80 bg-slate-800/95 border-r border-slate-700 overflow-y-auto">
              <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-4 z-10">
                <h2 className="text-sm font-semibold text-white mb-2">Available Agents</h2>
                <p className="text-xs text-slate-400">Click to select agents for execution</p>
              </div>
              
              <div className="p-3">
                {agents.map(agent => (
                  <div
                    key={agent.id}
                    onClick={() => toggleAgentSelection(agent.id)}
                    className={`p-3 mb-2 rounded cursor-pointer transition-all border-l-2 ${
                      selectedAgents.has(agent.id)
                        ? 'bg-blue-500/20 border-blue-500'
                        : 'bg-slate-700/30 border-slate-600'
                    } hover:bg-slate-700/50`}
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-2xl">{agent.icon}</span>
                      <div className="flex-1">
                        <div className="font-semibold text-white text-sm mb-1">{agent.displayName}</div>
                        <div className="text-xs text-slate-400 mb-1">{agent.description}</div>
                        <span className={`inline-block px-2 py-1 text-[10px] uppercase rounded ${
                          agent.status === 'working' ? 'bg-blue-500/20 text-blue-400' :
                          agent.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                          agent.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          'bg-slate-600/20 text-slate-400'
                        }`}>
                          {agent.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Center - 3D Canvas */}
            <div className="flex-1 relative">
              <AgentCanvas3D
                agents={agents}
                selectedAgents={selectedAgents}
                onAgentClick={toggleAgentSelection}
                artifacts={artifacts}
                enableBloom={enableBloom}
                showConnections={showConnections}
              />
            </div>

            {/* Right Panel - Prompt & Activity */}
            <div className="w-[350px] bg-slate-800/95 border-l border-slate-700 p-5 overflow-y-auto">
              
              {/* Selected Agents */}
              <div className="mb-5">
                <h3 className="text-sm font-semibold text-white mb-2">Selected Agents</h3>
                <div className="text-xs text-slate-400">
                  {selectedAgents.size === 0 ? (
                    <em>No agents selected</em>
                  ) : (
                    <div className="flex flex-wrap gap-1">
                      {Array.from(selectedAgents).map(id => {
                        const agent = agents.find(a => a.id === id);
                        return agent ? (
                          <span key={id} className="inline-block px-2 py-1 bg-blue-500/20 border border-blue-500 rounded text-blue-400 text-xs">
                            {agent.icon} {agent.displayName}
                          </span>
                        ) : null;
                      })}
                    </div>
                  )}
                </div>
              </div>

              {/* Execution Prompt */}
              <div className="mb-5">
                <h3 className="text-sm font-semibold text-white mb-2">Execution Prompt</h3>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your prompt for the selected agents...

Example: Research the latest trends in AI and create a blog post about them."
                  className="w-full min-h-[150px] p-3 bg-slate-900/70 border border-slate-600 rounded text-white text-xs resize-vertical placeholder:text-slate-500"
                />
              </div>

              {/* Execute Button */}
              <button
                onClick={executePipeline}
                disabled={selectedAgents.size === 0 || !prompt.trim() || isExecuting}
                className="w-full py-3 bg-blue-500 rounded text-white font-semibold uppercase transition-all hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-500"
              >
                {isExecuting ? 'Executing...' : 'Execute Pipeline'}
              </button>

              {/* Activity Log */}
              <div className="mt-5">
                <h3 className="text-sm font-semibold text-white mb-2">Activity Log</h3>
                <div className="max-h-[300px] overflow-y-auto text-xs bg-slate-900/50 border border-slate-700 rounded p-2">
                  {activityLog.map((log, i) => (
                    <div key={i} className={`mb-2 pb-2 border-l-2 pl-2 ${
                      log.type === 'agent' ? 'border-blue-500' :
                      log.type === 'artifact' ? 'border-green-500' :
                      log.type === 'error' ? 'border-red-500' :
                      'border-slate-600'
                    }`}>
                      <span className="text-slate-500 mr-2">[{log.timestamp}]</span>
                      <span className="text-slate-300">{log.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Control Panel */}
          <div className="absolute bottom-5 left-1/2 transform -translate-x-1/2 bg-slate-800/95 border border-slate-700 rounded-lg px-5 py-3 flex gap-4 items-center z-40">
            <button
              onClick={() => {/* Reset camera */}}
              className="px-4 py-2 border border-slate-600 text-slate-300 rounded text-xs font-medium transition-all hover:bg-slate-700"
            >
              Reset View
            </button>
            <button
              onClick={() => setEnableBloom(!enableBloom)}
              className={`px-4 py-2 border rounded text-xs font-medium transition-all ${
                enableBloom ? 'bg-blue-500/20 border-blue-500 text-blue-400' : 'border-slate-600 text-slate-300'
              } hover:bg-slate-700`}
            >
              Bloom: {enableBloom ? 'ON' : 'OFF'}
            </button>
            <button
              onClick={() => setShowConnections(!showConnections)}
              className={`px-4 py-2 border rounded text-xs font-medium transition-all ${
                showConnections ? 'bg-blue-500/20 border-blue-500 text-blue-400' : 'border-slate-600 text-slate-300'
              } hover:bg-slate-700`}
            >
              Connections: {showConnections ? 'ON' : 'OFF'}
            </button>
          </div>

          {/* CopilotKit Chat */}
          <CopilotPopup
            labels={{
              title: "AG-UI Assistant",
              initial: "How can I help you with agent workflows?",
            }}
          />
        </div>
      </CopilotKit>
    </ErrorBoundary>
  );
}
