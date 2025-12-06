import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import Scene3D from './components/Scene3D';
import Header from './components/Header';
import AgentPanel from './components/AgentPanel';
import PromptPanel from './components/PromptPanel';
import ControlPanel from './components/ControlPanel';
import LoadingScreen from './components/LoadingScreen';
import { loadAgents } from './api/agentApi';
import './App.css';

function App() {
  const [loading, setLoading] = useState(true);
  const [availableAgents, setAvailableAgents] = useState([]);
  const [selectedAgents, setSelectedAgents] = useState(new Set());
  const [agentStates, setAgentStates] = useState(new Map());
  const [activePipeline, setActivePipeline] = useState(null);
  const [activityLog, setActivityLog] = useState([]);
  const [systemStatus, setSystemStatus] = useState('IDLE');
  const [enableBloom, setEnableBloom] = useState(true);
  const [showConnections, setShowConnections] = useState(true);
  const [agentPanelCollapsed, setAgentPanelCollapsed] = useState(false);
  const [promptPanelCollapsed, setPromptPanelCollapsed] = useState(false);

  // Load agents on mount
  useEffect(() => {
    const initialize = async () => {
      try {
        const agents = await loadAgents();
        setAvailableAgents(agents);
        
        // Initialize agent states
        const states = new Map();
        agents.forEach(agent => {
          states.set(agent.id, 'idle');
        });
        setAgentStates(states);
        
        logActivity('system', `Loaded ${agents.length} available agents`);
      } catch (error) {
        console.error('Failed to load agents:', error);
        logActivity('error', `Failed to load agents: ${error.message}`);
      } finally {
        setTimeout(() => setLoading(false), 1000);
      }
    };

    initialize();
  }, []);

  const toggleAgentSelection = (agentId) => {
    const newSelected = new Set(selectedAgents);
    if (newSelected.has(agentId)) {
      newSelected.delete(agentId);
    } else {
      newSelected.add(agentId);
    }
    setSelectedAgents(newSelected);
  };

  const logActivity = (type, message) => {
    const entry = {
      type,
      message,
      timestamp: new Date().toLocaleTimeString(),
      id: Date.now() + Math.random(),
    };
    setActivityLog(prev => [entry, ...prev.slice(0, 49)]);
  };

  const updateAgentState = (agentId, status) => {
    setAgentStates(prev => {
      const newStates = new Map(prev);
      newStates.set(agentId, status);
      return newStates;
    });
  };

  return (
    <div className="app">
      {loading && <LoadingScreen />}
      
      <Header systemStatus={systemStatus} />
      
      <div className="main-container">
        <AgentPanel
          agents={availableAgents}
          selectedAgents={selectedAgents}
          agentStates={agentStates}
          onToggleSelection={toggleAgentSelection}
          collapsed={agentPanelCollapsed}
          onToggleCollapse={() => setAgentPanelCollapsed(!agentPanelCollapsed)}
        />

        <div className="canvas-container">
          <Canvas
            camera={{ position: [0, 15, 40], fov: 75 }}
            gl={{ 
              antialias: true, 
              alpha: true, 
              powerPreference: "high-performance" 
            }}
          >
            <Scene3D
              agents={availableAgents}
              selectedAgents={selectedAgents}
              agentStates={agentStates}
              enableBloom={enableBloom}
              showConnections={showConnections}
            />
          </Canvas>
        </div>

        <PromptPanel
          selectedAgents={selectedAgents}
          availableAgents={availableAgents}
          activePipeline={activePipeline}
          activityLog={activityLog}
          collapsed={promptPanelCollapsed}
          onToggleCollapse={() => setPromptPanelCollapsed(!promptPanelCollapsed)}
          onExecute={(prompt) => {
            setActivePipeline({ id: 'temp', status: 'running' });
            setSystemStatus('EXECUTING');
            logActivity('system', `Starting pipeline with ${selectedAgents.size} agents`);
          }}
          onLogActivity={logActivity}
          onUpdateAgentState={updateAgentState}
          onSetSystemStatus={setSystemStatus}
          onSetActivePipeline={setActivePipeline}
        />
      </div>

      <ControlPanel
        enableBloom={enableBloom}
        showConnections={showConnections}
        onToggleBloom={() => setEnableBloom(!enableBloom)}
        onToggleConnections={() => setShowConnections(!showConnections)}
      />
    </div>
  );
}

export default App;
