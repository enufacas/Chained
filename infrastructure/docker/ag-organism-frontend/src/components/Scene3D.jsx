import React, { useEffect, useRef } from 'react';
import { OrbitControls as DreiOrbitControls } from '@react-three/drei';
import { useThree } from '@react-three/fiber';
import AgentHumanoid from './AgentHumanoid';
import AgentLabel from './AgentLabel';
import ConnectionLines from './ConnectionLines';
import PostProcessing from './PostProcessing';

function Scene3D({ agents, selectedAgents, agentStates, enableBloom, showConnections }) {
  const { camera, gl } = useThree();
  const controlsRef = useRef();

  // Handle camera reset event
  useEffect(() => {
    const handleResetCamera = () => {
      if (controlsRef.current) {
        camera.position.set(0, 15, 40);
        controlsRef.current.target.set(0, 0, 0);
        controlsRef.current.update();
      }
    };

    window.addEventListener('reset-camera', handleResetCamera);
    return () => window.removeEventListener('reset-camera', handleResetCamera);
  }, [camera]);

  // Arrange agents in a circle
  const agentPositions = agents.map((agent, index) => {
    const radius = 20;
    const angle = (index / agents.length) * Math.PI * 2;
    const x = Math.cos(angle) * radius;
    const z = Math.sin(angle) * radius;
    return [x, 0, z];
  });

  return (
    <>
      {/* Fog */}
      <fog attach="fog" args={[0x0a0e1a, 30, 100]} />

      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <directionalLight
        position={[30, 40, 20]}
        intensity={1.5}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      <pointLight position={[25, 20, 25]} color={0x00ffff} intensity={2} distance={100} />
      <pointLight position={[-25, -10, -25]} color={0xff00ff} intensity={2} distance={100} />

      {/* Ground plane (invisible but receives shadows) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -5, 0]} receiveShadow>
        <planeGeometry args={[200, 200]} />
        <shadowMaterial opacity={0.3} />
      </mesh>

      {/* Agent Humanoids */}
      {agents.map((agent, index) => {
        const position = agentPositions[index];
        const isSelected = selectedAgents.has(agent.id);
        const state = agentStates.get(agent.id) || 'idle';

        return (
          <group key={agent.id}>
            <AgentHumanoid
              agent={agent}
              position={position}
              isSelected={isSelected}
              state={state}
            />
            <AgentLabel text={agent.displayName} position={position} />
          </group>
        );
      })}

      {/* Connection Lines */}
      <ConnectionLines
        agents={agents}
        selectedAgents={selectedAgents}
        agentStates={agentStates}
        showConnections={showConnections}
      />

      {/* Controls */}
      <DreiOrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.05}
        minDistance={20}
        maxDistance={100}
        args={[camera, gl.domElement]}
      />

      {/* Post-processing */}
      {enableBloom && <PostProcessing />}
    </>
  );
}

export default Scene3D;
