import React, { useEffect, useRef } from 'react';
import { 
  OrbitControls as DreiOrbitControls, 
  Grid, 
  ContactShadows,
  Sparkles,
  Float,
  MeshReflectorMaterial
} from '@react-three/drei';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import AgentHumanoid from './AgentHumanoid';
import AgentLabel from './AgentLabel';
import ConnectionLines from './ConnectionLines';
import PostProcessing from './PostProcessing';

// Factory Platform Component with optimized reflective surface
function FactoryPlatform() {
  return (
    <group position={[0, -2, 0]}>
      {/* Main platform with simpler reflective finish */}
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.5, 0]}>
        <circleGeometry args={[26, 64]} />
        <MeshReflectorMaterial
          blur={[400, 100]}
          resolution={512}
          mixBlur={0.8}
          mixStrength={20}
          roughness={0.5}
          depthScale={0.8}
          minDepthThreshold={0.5}
          maxDepthThreshold={1.2}
          color="#2a3142"
          metalness={0.8}
        />
      </mesh>
      
      {/* Platform base */}
      <mesh receiveShadow>
        <cylinderGeometry args={[25, 26, 0.5, 32]} />
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
          emissiveIntensity={0.8}
          metalness={0.5}
          roughness={0.2}
        />
      </mesh>
      
      {/* Inner glow ring */}
      <mesh position={[0, 0.6, 0]}>
        <torusGeometry args={[15, 0.2, 16, 64]} />
        <meshStandardMaterial 
          color="#6dd5ff"
          emissive="#6dd5ff"
          emissiveIntensity={0.6}
          transparent
          opacity={0.7}
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

// Enhanced particle effects using Sparkles from Drei
function EnhancedParticles() {
  return (
    <>
      {/* Main sparkles cloud */}
      <Sparkles
        count={100}
        scale={[35, 20, 35]}
        size={2}
        speed={0.3}
        opacity={0.6}
        color="#4a9eff"
      />
      
      {/* Secondary sparkles for depth */}
      <Sparkles
        count={50}
        scale={[25, 15, 25]}
        size={1.5}
        speed={0.5}
        opacity={0.4}
        color="#6dd5ff"
      />
      
      {/* Accent sparkles */}
      <Sparkles
        count={30}
        scale={[20, 10, 20]}
        size={3}
        speed={0.2}
        opacity={0.8}
        color="#8fe3ff"
      />
    </>
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

      {/* Lighting - factory style */}
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

      {/* Enhanced particle effects */}
      <EnhancedParticles />

      {/* Contact shadows for better depth */}
      <ContactShadows
        position={[0, -2.4, 0]}
        opacity={0.5}
        scale={50}
        blur={2}
        far={10}
        resolution={256}
        color="#4a9eff"
      />

      {/* Agent Humanoids with Float animation */}
      {agents.map((agent, index) => {
        const position = agentPositions[index];
        const isSelected = selectedAgents.has(agent.id);
        const state = agentStates.get(agent.id) || 'idle';

        return (
          <Float
            key={agent.id}
            speed={1.5}
            rotationIntensity={state === 'processing' ? 0.5 : 0.1}
            floatIntensity={0.5}
            floatingRange={[-0.5, 0.5]}
          >
            <group>
              <AgentHumanoid
                agent={agent}
                position={position}
                isSelected={isSelected}
                state={state}
              />
              <AgentLabel text={agent.displayName} position={position} />
            </group>
          </Float>
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
