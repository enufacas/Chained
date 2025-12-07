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
  const [a2aMessages, setA2aMessages] = useState([]);
  const [pipelineSteps, setPipelineSteps] = useState([]);

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
        
        // Fallback to mock agents for demo purposes
        const mockAgents = [
          { id: 'academic-research', displayName: 'Academic Research', icon: '🔬', description: 'Researches academic papers and trends' },
          { id: 'google-trends', displayName: 'Google Trends', icon: '📊', description: 'Analyzes trending topics' },
          { id: 'blog-writer', displayName: 'Blog Writer', icon: '✍️', description: 'Creates blog content' },
          { id: 'code-reviewer', displayName: 'Code Reviewer', icon: '👁️', description: 'Reviews code quality' },
          { id: 'data-analyst', displayName: 'Data Analyst', icon: '📈', description: 'Analyzes data patterns' },
          { id: 'image-generator', displayName: 'Image Generator', icon: '🎨', description: 'Generates images' },
        ];
        setAvailableAgents(mockAgents);
        
        const states = new Map();
        mockAgents.forEach(agent => {
          states.set(agent.id, 'idle');
        });
        setAgentStates(states);
        
        logActivity('system', 'Using demo agents (backend not available)');
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
  
  const addA2AMessage = (message) => {
    setA2aMessages(prev => [...prev, { ...message, id: Date.now() + Math.random() }]);
  };
  
  const updatePipelineSteps = (steps) => {
    setPipelineSteps(steps || []);
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
              a2aMessages={a2aMessages}
              pipelineSteps={pipelineSteps}
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
            
            // Add initial A2A message for pipeline start
            addA2AMessage({
              type: 'task',
              from: 'system',
              to: Array.from(selectedAgents)[0],
              label: 'Start',
              timestamp: Date.now()
            });
          }}
          onLogActivity={logActivity}
          onUpdateAgentState={updateAgentState}
          onSetSystemStatus={setSystemStatus}
          onSetActivePipeline={setActivePipeline}
          onAddA2AMessage={addA2AMessage}
          onUpdatePipelineSteps={updatePipelineSteps}
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
