import React from 'react';
import './AgentPanel.css';

function AgentPanel({ agents, selectedAgents, agentStates, onToggleSelection, collapsed, onToggleCollapse }) {
  return (
    <>
      <div className={`agent-panel ${collapsed ? 'collapsed' : ''}`}>
        <div className="panel-header">
          <h2>Available Agents</h2>
          <p style={{ fontSize: '11px', color: '#888', marginTop: '5px' }}>
            Click to select agents for execution
          </p>
        </div>
        <div className="agent-selector">
          {agents.map(agent => {
            const isSelected = selectedAgents.has(agent.id);
            const state = agentStates.get(agent.id) || 'idle';
            const cardClass = `agent-card ${isSelected ? 'selected' : ''} ${
              state === 'processing' ? 'working' : state === 'completed' ? 'completed' : ''
            }`;

            return (
              <div
                key={agent.id}
                className={cardClass}
                onClick={() => onToggleSelection(agent.id)}
              >
                <div className="agent-icon">{agent.icon || '🤖'}</div>
                <div className="agent-name">{agent.displayName}</div>
                <div className="agent-description">{agent.description}</div>
                <span className={`agent-status ${state}`}>{state}</span>
              </div>
            );
          })}
        </div>
      </div>
      
      <button 
        className="toggle-sidebar toggle-agents" 
        style={{ left: collapsed ? '20px' : '320px' }}
        onClick={onToggleCollapse}
      >
        {collapsed ? '▶' : '◀'}
      </button>
    </>
  );
}

export default AgentPanel;
