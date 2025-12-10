/**
 * AgentCanvas3D Component
 * 
 * Main 3D visualization of agents using react-three-fiber
 * Replaces the 2D AgentCanvas with a 3D scene featuring humanoid agents
 */

'use client';

import React, { Suspense, useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import AgentHumanoid3D from './AgentHumanoid3D';
import SceneSetup from './SceneSetup';
import ConnectionLines3D from './ConnectionLines3D';
import ArtifactVisualization3D from './ArtifactVisualization3D';

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
  position?: [number, number, number];
  createdAt: number;
}

interface AgentCanvas3DProps {
  agents: Agent[];
  selectedAgents: Set<string>;
  onAgentClick?: (agentId: string) => void;
  artifacts?: Artifact[];
  enableBloom?: boolean;
  showConnections?: boolean;
}

// Color mapping for different agent types - clean, professional colors
const getAgentColor = (agentId: string): number => {
  const colors: Record<string, number> = {
    'academic-research': 0x3b82f6, // blue-500
    'google-trends': 0x10b981,     // green-500
    'blog-writer': 0x8b5cf6,       // purple-500
    'code-reviewer': 0xf59e0b,     // yellow-500
    'data-analyst': 0x06b6d4,      // cyan-500
    'image-generator': 0xec4899,   // pink-500
  };
  return colors[agentId] || 0x6366f1; // indigo-500 default
};

export default function AgentCanvas3D({
  agents,
  selectedAgents,
  onAgentClick,
  artifacts = [],
  showConnections = true,
}: AgentCanvas3DProps) {
  const [agentPositions, setAgentPositions] = useState<Map<string, [number, number, number]>>(new Map());

  // Calculate agent positions in a circle
  useEffect(() => {
    const radius = 20;
    const positions = new Map<string, [number, number, number]>();
    
    agents.forEach((agent, index) => {
      const angle = (index / agents.length) * Math.PI * 2;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      positions.set(agent.id, [x, 0, z]);
    });
    
    setAgentPositions(positions);
  }, [agents]);

  // Get selected agent positions for connection lines
  const selectedPositions = Array.from(selectedAgents)
    .map(id => agentPositions.get(id))
    .filter((pos) => pos !== undefined) as Array<[number, number, number]>;

  return (
    <><div style={{ width: '100%', height: '100%', background: '#0f172a' }}>
      <Canvas
        shadows
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance',
        }}
        camera={{ position: [0, 15, 40], fov: 75 }}
      >
        <Suspense fallback={<LoadingFallback />}>
          <SceneSetup />

          {agents.map((agent) => {
            const position = agentPositions.get(agent.id);
            if (!position) return null;

            const isSelected = selectedAgents.has(agent.id);
            const color = getAgentColor(agent.id);

            return (
              <group key={agent.id}>
                <AgentHumanoid3D
                  position={position}
                  color={color}
                  size={isSelected ? 1.4 : 1.2}
                  status={agent.status}
                  onClick={() => onAgentClick?.(agent.id)}
                  lookAt={[0, 0, 0]}
                />
                
                <Html
                  position={[position[0], position[1] + 4, position[2]]}
                  center
                  distanceFactor={10}
                  style={{
                    color: '#f1f5f9', // slate-100
                    fontSize: '12px',
                    fontFamily: 'system-ui, sans-serif',
                    background: 'rgba(15, 23, 42, 0.9)', // slate-900
                    padding: '4px 8px',
                    borderRadius: '4px',
                    border: '1px solid #475569', // slate-600
                    whiteSpace: 'nowrap',
                    pointerEvents: 'none',
                  }}
                >
                  {agent.icon} {agent.displayName}
                </Html>
              </group>
            );
          })}

          {showConnections && selectedPositions.length > 1 && (
            <ConnectionLines3D positions={selectedPositions} color={0x3b82f6} />
          )}

          {artifacts.map((artifact) => (
            <ArtifactVisualization3D
              key={artifact.id}
              artifact={artifact}
              agentPosition={agentPositions.get(artifact.agentId)}
            />
          ))}
        </Suspense>
      </Canvas>
    </div></>
  );
}

// Loading fallback component
function LoadingFallback() {
  return (
    <Html center>
      <div style={{
        color: '#94a3b8', // slate-400
        fontSize: '14px',
        fontFamily: 'system-ui, sans-serif',
      }}>
        Loading 3D Scene...
      </div>
    </Html>
  );
}
