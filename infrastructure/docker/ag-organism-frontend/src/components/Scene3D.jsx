import React, { useEffect, useRef } from 'react';
import { OrbitControls as DreiOrbitControls, Grid } from '@react-three/drei';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import AgentHumanoid from './AgentHumanoid';
import AgentLabel from './AgentLabel';
import ConnectionLines from './ConnectionLines';
import PostProcessing from './PostProcessing';

// Factory Platform Component
function FactoryPlatform() {
  return (
    <group position={[0, -2, 0]}>
      {/* Main platform */}
      <mesh receiveShadow>
        <cylinderGeometry args={[25, 26, 1, 32]} />
        <meshStandardMaterial 
          color="#2a3142"
          metalness={0.8}
          roughness={0.3}
        />
      </mesh>
      
      {/* Platform edge glow */}
      <mesh position={[0, 0.5, 0]}>
        <torusGeometry args={[25, 0.3, 16, 64]} />
        <meshStandardMaterial 
          color="#4a9eff"
          emissive="#4a9eff"
          emissiveIntensity={0.5}
          metalness={0.5}
          roughness={0.2}
        />
      </mesh>
    </group>
  );
}

// Rotating factory rings
function FactoryRings() {
  const ring1Ref = useRef();
  const ring2Ref = useRef();
  const ring3Ref = useRef();

  useFrame((state, delta) => {
    if (ring1Ref.current) ring1Ref.current.rotation.y += delta * 0.1;
    if (ring2Ref.current) ring2Ref.current.rotation.y -= delta * 0.15;
    if (ring3Ref.current) ring3Ref.current.rotation.y += delta * 0.08;
  });

  return (
    <group>
      {/* Outer ring */}
      <mesh ref={ring1Ref} position={[0, 0, 0]}>
        <torusGeometry args={[30, 0.2, 8, 64]} />
        <meshStandardMaterial 
          color="#4a9eff"
          emissive="#4a9eff"
          emissiveIntensity={0.3}
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.6}
        />
      </mesh>

      {/* Middle ring */}
      <mesh ref={ring2Ref} position={[0, 5, 0]} rotation={[Math.PI / 4, 0, 0]}>
        <torusGeometry args={[22, 0.15, 8, 64]} />
        <meshStandardMaterial 
          color="#6dd5ff"
          emissive="#6dd5ff"
          emissiveIntensity={0.3}
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.5}
        />
      </mesh>

      {/* Inner ring */}
      <mesh ref={ring3Ref} position={[0, -5, 0]} rotation={[-Math.PI / 6, 0, 0]}>
        <torusGeometry args={[28, 0.18, 8, 64]} />
        <meshStandardMaterial 
          color="#8fe3ff"
          emissive="#8fe3ff"
          emissiveIntensity={0.3}
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.4}
        />
      </mesh>
    </group>
  );
}

// Factory pillars/beams
function FactoryPillars() {
  const pillarPositions = [
    [30, 0, 0],
    [-30, 0, 0],
    [0, 0, 30],
    [0, 0, -30],
  ];

  return (
    <group>
      {pillarPositions.map((pos, i) => (
        <group key={i} position={pos}>
          {/* Pillar */}
          <mesh position={[0, 5, 0]} castShadow>
            <boxGeometry args={[1.5, 20, 1.5]} />
            <meshStandardMaterial 
              color="#353d52"
              metalness={0.8}
              roughness={0.3}
            />
          </mesh>
          
          {/* Pillar light */}
          <pointLight 
            position={[0, 10, 0]} 
            color="#4a9eff" 
            intensity={1} 
            distance={20}
          />
          
          {/* Pillar top indicator */}
          <mesh position={[0, 15, 0]}>
            <sphereGeometry args={[0.5, 16, 16]} />
            <meshStandardMaterial 
              color="#4a9eff"
              emissive="#4a9eff"
              emissiveIntensity={0.8}
            />
          </mesh>
        </group>
      ))}
    </group>
  );
}

// Animated data streams (particles)
function DataStreams() {
  const particlesRef = useRef();
  const particleCount = 50;
  
  const positions = new Float32Array(particleCount * 3);
  const colors = new Float32Array(particleCount * 3);
  
  for (let i = 0; i < particleCount; i++) {
    const i3 = i * 3;
    // Random position in a sphere
    const radius = 15 + Math.random() * 20;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.random() * Math.PI;
    
    positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i3 + 1] = radius * Math.cos(phi);
    positions[i3 + 2] = radius * Math.sin(phi) * Math.sin(theta);
    
    // Blue-ish colors
    colors[i3] = 0.3 + Math.random() * 0.3;
    colors[i3 + 1] = 0.6 + Math.random() * 0.4;
    colors[i3 + 2] = 1.0;
  }

  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array;
      
      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        // Slowly rotate particles
        const angle = state.clock.elapsedTime * 0.1 + i * 0.1;
        const radius = 15 + (i / particleCount) * 20;
        
        positions[i3] = Math.cos(angle) * radius;
        positions[i3 + 1] = Math.sin(state.clock.elapsedTime * 0.5 + i) * 5;
        positions[i3 + 2] = Math.sin(angle) * radius;
      }
      
      particlesRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particleCount}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.3}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

function Scene3D({ agents, selectedAgents, agentStates, enableBloom, showConnections }) {
  const { camera, gl } = useThree();
  const controlsRef = useRef();

  // Handle camera reset event
  useEffect(() => {
    const handleResetCamera = () => {
      if (controlsRef.current) {
        camera.position.set(0, 25, 50);
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
      {/* Background color */}
      <color attach="background" args={['#0d1117']} />
      
      {/* Fog - lighter and more industrial */}
      <fog attach="fog" args={['#0d1117', 40, 120]} />

      {/* Lighting - factory style (no external Environment needed) */}
      <ambientLight intensity={0.4} color="#b8d4ff" />
      
      {/* Main overhead lights */}
      <directionalLight
        position={[30, 50, 20]}
        intensity={1.2}
        color="#ffffff"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-left={-50}
        shadow-camera-right={50}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
      />
      
      {/* Accent lights - blue factory lighting */}
      <pointLight position={[0, 30, 0]} color="#4a9eff" intensity={2} distance={80} />
      <spotLight
        position={[0, 40, 0]}
        angle={Math.PI / 3}
        penumbra={0.5}
        intensity={1}
        color="#6dd5ff"
        castShadow
      />

      {/* Grid floor */}
      <Grid
        position={[0, -2.5, 0]}
        args={[100, 100]}
        cellSize={2}
        cellThickness={0.5}
        cellColor="#2a4d6e"
        sectionSize={10}
        sectionThickness={1}
        sectionColor="#3a6d9e"
        fadeDistance={80}
        fadeStrength={1}
        infiniteGrid={false}
      />

      {/* Factory Platform */}
      <FactoryPlatform />

      {/* Rotating factory rings */}
      <FactoryRings />

      {/* Factory pillars */}
      <FactoryPillars />

      {/* Data streams */}
      <DataStreams />

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
