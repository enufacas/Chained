/**
 * AgentCanvas3D Component
 * 
 * Main 3D visualization of agents using react-three-fiber
 * Replaces the 2D AgentCanvas with a 3D scene featuring humanoid agents
 */

'use client';

import { Canvas } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import { Suspense, useState, useEffect } from 'react';
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

// Color mapping for different agent types
const getAgentColor = (agentId: string): number => {
  const colors: Record<string, number> = {
    'academic-research': 0x00ffff,
    'google-trends': 0xff00ff,
    'blog-writer': 0x00ff00,
    'code-reviewer': 0xffaa00,
    'data-analyst': 0x9900ff,
    'image-generator': 0xff0099,
  };
  return colors[agentId] || 0x00ffff;
};

export default function AgentCanvas3D({
  agents,
  selectedAgents,
  onAgentClick,
  artifacts = [],
  enableBloom = true,
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
    .filter((pos): pos is [number, number, number] => pos !== undefined);

  return (
    <div style={{ width: '100%', height: '100%', background: '#0a0e1a' }}>
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

          {/* Render all agents as humanoids */}
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
                
                {/* Agent Label */}
                <Html
                  position={[position[0], position[1] + 4, position[2]]}
                  center
                  distanceFactor={10}
                  style={{
                    color: '#00ffff',
                    fontSize: '12px',
                    fontFamily: 'Segoe UI, sans-serif',
                    background: 'rgba(10, 14, 26, 0.8)',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    border: '1px solid #00ffff',
                    whiteSpace: 'nowrap',
                    pointerEvents: 'none',
                    textShadow: '0 0 5px rgba(0, 255, 255, 0.5)',
                  }}
                >
                  {agent.icon} {agent.displayName}
                </Html>
              </group>
            );
          })}

          {/* Connection lines between selected agents */}
          {showConnections && selectedPositions.length > 1 && (
            <ConnectionLines3D positions={selectedPositions} color={0xff00ff} />
          )}

          {/* Artifact visualizations */}
          {artifacts.map((artifact) => (
            <ArtifactVisualization3D
              key={artifact.id}
              artifact={artifact}
              agentPosition={agentPositions.get(artifact.agentId)}
            />
          ))}
        </Suspense>
      </Canvas>
    </div>
  );
}

// Loading fallback component
function LoadingFallback() {
  return (
    <Html center>
      <div style={{
        color: '#00ffff',
        fontSize: '16px',
        fontFamily: 'Courier New, monospace',
      }}>
        INITIALIZING 3D SCENE...
      </div>
    </Html>
  );
}
