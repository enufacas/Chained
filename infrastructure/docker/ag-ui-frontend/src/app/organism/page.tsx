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
import { useCopilotAction, useCopilotReadable, CopilotKit } from "@copilotkit/react-core";
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

  // Load available agents from API
  useEffect(() => {
    fetch('/api/registry')
      .then(res => res.json())
      .then(data => {
        if (data.agents) {
          setAgents(data.agents.map((a: any) => ({
            ...a,
            status: 'idle' as const,
          })));
          addLog('system', `Loaded ${data.agents.length} available agents`);
        }
      })
      .catch(err => {
        console.error('Failed to load agents:', err);
        addLog('error', `Failed to load agents: ${err.message}`);
      });
  }, []);

  const addLog = useCallback((type: string, message: string) => {
    setActivityLog(prev => [
      { timestamp: new Date().toLocaleTimeString(), type, message },
      ...prev.slice(0, 49), // Keep last 50 entries
    ]);
  }, []);

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
      const pipelineId = data.pipeline.id;
      addLog('system', `Pipeline created: ${pipelineId}`);

      // Poll for updates
      pollPipeline(pipelineId);

    } catch (error: any) {
      addLog('error', `Pipeline failed: ${error.message}`);
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

  const updateFromPipeline = (pipeline: any) => {
    if (!pipeline.a2aSteps) return;

    pipeline.a2aSteps.forEach((step: any) => {
      const agentId = step.agentName;
      const status = step.status?.state || 'pending';

      // Update agent status
      setAgents(prev => prev.map(a => 
        a.id === agentId ? { ...a, status: status as any } : a
      ));

      // Process artifacts
      if (step.artifacts && step.artifacts.length > 0) {
        step.artifacts.forEach((artifact: any) => {
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
            <div className="w-80 bg-[rgba(10,14,26,0.95)] border-r-2 border-cyan-400 overflow-y-auto">
              <div className="sticky top-0 bg-cyan-400/10 border-b border-cyan-400 p-4 z-10">
                <h2 className="text-sm uppercase tracking-widest text-cyan-400 mb-2">Available Agents</h2>
                <p className="text-xs text-gray-500">Click to select agents for execution</p>
              </div>
              
              <div className="p-3">
                {agents.map(agent => (
                  <div
                    key={agent.id}
                    onClick={() => toggleAgentSelection(agent.id)}
                    className={`p-3 mb-2 rounded cursor-pointer transition-all border-l-4 ${
                      selectedAgents.has(agent.id)
                        ? 'bg-magenta-400/20 border-magenta-400'
                        : 'bg-cyan-400/5 border-cyan-400'
                    } hover:bg-cyan-400/15 hover:translate-x-1`}
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-2xl">{agent.icon}</span>
                      <div className="flex-1">
                        <div className="font-bold text-cyan-400 text-sm mb-1">{agent.displayName}</div>
                        <div className="text-xs text-gray-500 mb-1">{agent.description}</div>
                        <span className={`inline-block px-2 py-1 text-[10px] uppercase rounded ${
                          agent.status === 'working' ? 'bg-green-400/20 text-green-400' :
                          agent.status === 'completed' ? 'bg-cyan-400/20 text-cyan-400' :
                          'bg-gray-400/20 text-gray-400'
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
            <div className="w-[350px] bg-[rgba(10,14,26,0.95)] border-l-2 border-cyan-400 p-5 overflow-y-auto">
              
              {/* Selected Agents */}
              <div className="mb-5">
                <h3 className="text-sm uppercase text-magenta-400 mb-2">Selected Agents</h3>
                <div className="text-xs text-gray-500">
                  {selectedAgents.size === 0 ? (
                    <em>No agents selected</em>
                  ) : (
                    <div className="flex flex-wrap gap-1">
                      {Array.from(selectedAgents).map(id => {
                        const agent = agents.find(a => a.id === id);
                        return agent ? (
                          <span key={id} className="inline-block px-2 py-1 bg-magenta-400/20 border border-magenta-400 rounded text-magenta-400">
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
                <h3 className="text-sm uppercase text-magenta-400 mb-2">Execution Prompt</h3>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your prompt for the selected agents...

Example: Research the latest trends in AI and create a blog post about them."
                  className="w-full min-h-[150px] p-3 bg-black/70 border border-cyan-400 rounded text-cyan-400 font-mono text-xs resize-vertical placeholder:text-gray-600"
                />
              </div>

              {/* Execute Button */}
              <button
                onClick={executePipeline}
                disabled={selectedAgents.size === 0 || !prompt.trim() || isExecuting}
                className="w-full py-3 bg-gradient-to-r from-magenta-500 to-cyan-500 rounded text-white font-bold uppercase transition-all hover:shadow-[0_0_20px_rgba(255,0,255,0.8)] hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {isExecuting ? 'EXECUTING...' : 'Execute Pipeline'}
              </button>

              {/* Activity Log */}
              <div className="mt-5">
                <h3 className="text-sm uppercase text-magenta-400 mb-2">Activity Log</h3>
                <div className="max-h-[300px] overflow-y-auto text-xs font-mono bg-black/50 border border-cyan-400 rounded p-2">
                  {activityLog.map((log, i) => (
                    <div key={i} className={`mb-2 pb-2 border-l-2 pl-2 ${
                      log.type === 'agent' ? 'border-magenta-400' :
                      log.type === 'artifact' ? 'border-green-400' :
                      log.type === 'error' ? 'border-red-400' :
                      'border-cyan-400'
                    }`}>
                      <span className="text-gray-600 mr-2">[{log.timestamp}]</span>
                      <span className="text-cyan-400">{log.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Control Panel */}
          <div className="absolute bottom-5 left-1/2 transform -translate-x-1/2 bg-[rgba(10,14,26,0.95)] border-2 border-cyan-400 rounded-lg px-5 py-3 flex gap-4 items-center shadow-[0_4px_20px_rgba(0,255,255,0.3)] z-40">
            <button
              onClick={() => {/* Reset camera */}}
              className={`px-4 py-2 border border-cyan-400 text-cyan-400 rounded text-xs uppercase transition-all hover:bg-cyan-400/30`}
            >
              Reset View
            </button>
            <button
              onClick={() => setEnableBloom(!enableBloom)}
              className={`px-4 py-2 border rounded text-xs uppercase transition-all ${
                enableBloom ? 'bg-magenta-400/30 border-magenta-400 text-magenta-400' : 'border-cyan-400 text-cyan-400'
              } hover:bg-cyan-400/30`}
            >
              Bloom: {enableBloom ? 'ON' : 'OFF'}
            </button>
            <button
              onClick={() => setShowConnections(!showConnections)}
              className={`px-4 py-2 border rounded text-xs uppercase transition-all ${
                showConnections ? 'bg-magenta-400/30 border-magenta-400 text-magenta-400' : 'border-cyan-400 text-cyan-400'
              } hover:bg-cyan-400/30`}
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
