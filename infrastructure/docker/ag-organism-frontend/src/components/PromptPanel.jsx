import React, { useState, useEffect, useRef } from 'react';
import { executePipeline, getPipelineStatus } from '../api/agentApi';
import './PromptPanel.css';

function PromptPanel({ 
  selectedAgents, 
  availableAgents, 
  activePipeline,
  activityLog,
  collapsed, 
  onToggleCollapse,
  onLogActivity,
  onUpdateAgentState,
  onSetSystemStatus,
  onSetActivePipeline,
  onAddA2AMessage,
  onUpdatePipelineSteps
}) {
  const [prompt, setPrompt] = useState('');
  const pollingIntervalRef = useRef(null);

  useEffect(() => {
    // Cleanup polling on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const startPipelinePolling = (pipelineId) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    pollingIntervalRef.current = setInterval(async () => {
      try {
        const pipeline = await getPipelineStatus(pipelineId);
        updatePipelineVisualization(pipeline);

        if (pipeline.status === 'completed' || pipeline.status === 'failed') {
          stopPipelinePolling();
          onSetSystemStatus(pipeline.status.toUpperCase());
          onSetActivePipeline(null);
        }
      } catch (error) {
        console.error('Pipeline polling failed:', error);
      }
    }, 2000);
  };

  const stopPipelinePolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  const updatePipelineVisualization = (pipeline) => {
    if (!pipeline || !pipeline.a2aSteps) return;

    // Update pipeline steps for A2A visualization
    if (onUpdatePipelineSteps) {
      const steps = pipeline.a2aSteps.map(step => ({
        agentId: step.agentName,
        status: step.status?.state || 'pending',
        taskId: step.taskId
      }));
      onUpdatePipelineSteps(steps);
    }

    pipeline.a2aSteps.forEach((step, index) => {
      const agentId = step.agentName;
      const status = step.status?.state || 'pending';

      onUpdateAgentState(agentId, status);
      
      // Create A2A message visualization for task handoffs
      if (index > 0 && onAddA2AMessage) {
        const prevStep = pipeline.a2aSteps[index - 1];
        onAddA2AMessage({
          type: 'task',
          from: prevStep.agentName,
          to: agentId,
          label: 'Handoff',
          timestamp: Date.now()
        });
      }

      // Log artifacts
      if (step.artifacts && step.artifacts.length > 0) {
        step.artifacts.forEach(artifact => {
          onLogActivity('artifact', `${step.agentName} created: ${artifact.name} (${artifact.type})`);
          
          // Visualize artifact creation as message
          if (onAddA2AMessage) {
            onAddA2AMessage({
              type: 'artifact',
              from: agentId,
              to: agentId,
              label: artifact.type,
              timestamp: Date.now()
            });
          }
        });
      }

      // Log messages
      if (step.status?.message) {
        const messageText = step.status.message.parts?.[0]?.text || '';
        if (messageText) {
          onLogActivity('agent', `${step.agentName}: ${messageText.substring(0, 100)}...`);
        }
      }
    });
  };

  const handleExecute = async () => {
    if (selectedAgents.size === 0 || !prompt.trim() || activePipeline) return;

    onSetSystemStatus('EXECUTING');
    onLogActivity('system', `Starting pipeline with ${selectedAgents.size} agents`);

    try {
      const pipeline = await executePipeline(prompt.trim(), Array.from(selectedAgents));
      onSetActivePipeline(pipeline);
      onLogActivity('system', `Pipeline created: ${pipeline.id}`);
      startPipelinePolling(pipeline.id);
    } catch (error) {
      console.error('Pipeline execution failed:', error);
      onLogActivity('error', `Pipeline failed: ${error.message}`);
      onSetSystemStatus('ERROR');
      onSetActivePipeline(null);
    }
  };

  const isExecuteDisabled = selectedAgents.size === 0 || !prompt.trim() || activePipeline !== null;

  return (
    <>
      <button 
        className="toggle-sidebar toggle-prompt" 
        style={{ right: collapsed ? '20px' : '350px' }}
        onClick={onToggleCollapse}
      >
        {collapsed ? '◀' : '▶'}
      </button>

      <div className={`prompt-panel ${collapsed ? 'collapsed' : ''}`}>
        <div className="prompt-section">
          <h3>Selected Agents</h3>
          <div className="selected-agents-list">
            {selectedAgents.size === 0 ? (
              <em style={{ color: '#666' }}>No agents selected</em>
            ) : (
              Array.from(selectedAgents).map(agentId => {
                const agent = availableAgents.find(a => a.id === agentId);
                return agent ? (
                  <span key={agentId} className="selected-agent-badge">
                    {agent.icon} {agent.displayName}
                  </span>
                ) : null;
              })
            )}
          </div>
        </div>

        <div className="prompt-section">
          <h3>Execution Prompt</h3>
          <textarea
            className="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your prompt for the selected agents...

Example: Research the latest trends in AI and create a blog post about them."
          />
        </div>

        <button 
          className="execute-btn" 
          onClick={handleExecute}
          disabled={isExecuteDisabled}
        >
          Execute Pipeline
        </button>

        <div className="prompt-section">
          <h3>Activity Log</h3>
          <div className="activity-log">
            {activityLog.length === 0 ? (
              <div className="log-entry">
                <span className="log-timestamp">[READY]</span>
                <span className="log-message">System initialized. Select agents and enter a prompt to begin.</span>
              </div>
            ) : (
              activityLog.map(entry => (
                <div key={entry.id} className={`log-entry ${entry.type}`}>
                  <span className="log-timestamp">[{entry.timestamp}]</span>
                  <span className="log-message">{entry.message}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default PromptPanel;
