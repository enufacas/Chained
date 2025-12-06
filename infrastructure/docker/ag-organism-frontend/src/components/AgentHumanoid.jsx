import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function AgentHumanoid({ agent, position, isSelected, state }) {
  const groupRef = useRef();
  const floatOffset = useMemo(() => Math.random() * Math.PI * 2, []);

  // Get color based on agent state
  const color = useMemo(() => {
    if (state === 'completed') return 0x00ff00;
    if (state === 'failed') return 0xff0000;
    if (state === 'processing') return 0xffff00;
    
    // Default colors by agent ID
    const colors = {
      'academic-research': 0x00ffff,
      'google-trends': 0xff00ff,
      'blog-writer': 0x00ff00,
      'code-reviewer': 0xffaa00,
      'data-analyst': 0x9900ff,
      'image-generator': 0xff0099,
    };
    return colors[agent.id] || 0x00ffff;
  }, [agent.id, state]);

  const emissiveIntensity = state === 'processing' ? 0.8 : 0.6;

  // Animation
  useFrame(({ clock }) => {
    if (groupRef.current) {
      // Float animation
      groupRef.current.position.y = position[1] + Math.sin(clock.elapsedTime * 2 + floatOffset) * 1;
      
      // Rotate when processing
      if (state === 'processing') {
        groupRef.current.rotation.y += 0.02;
      }
    }
  });

  // Material
  const material = useMemo(() => (
    <meshStandardMaterial
      color={color}
      emissive={color}
      emissiveIntensity={emissiveIntensity}
      metalness={0.9}
      roughness={0.1}
    />
  ), [color, emissiveIntensity]);

  const size = 1.2;

  return (
    <group ref={groupRef} position={position}>
      {/* Head */}
      <mesh position={[0, size * 1.5, 0]} castShadow>
        <sphereGeometry args={[size * 0.4, 16, 16]} />
        {material}
      </mesh>

      {/* Visor */}
      <mesh position={[0, size * 1.5, size * 0.4]}>
        <planeGeometry args={[size * 0.6, size * 0.15]} />
        <meshBasicMaterial color={0x00ffff} transparent opacity={0.8} />
      </mesh>

      {/* Torso */}
      <mesh position={[0, size * 0.6, 0]} castShadow>
        <capsuleGeometry args={[size * 0.35, size * 0.8, 8, 16]} />
        {material}
      </mesh>

      {/* Left Arm */}
      <mesh position={[-size * 0.55, size * 0.7, 0]} rotation={[0, 0, Math.PI * 0.15]} castShadow>
        <capsuleGeometry args={[size * 0.15, size * 0.7, 4, 8]} />
        {material}
      </mesh>

      {/* Right Arm */}
      <mesh position={[size * 0.55, size * 0.7, 0]} rotation={[0, 0, -Math.PI * 0.15]} castShadow>
        <capsuleGeometry args={[size * 0.15, size * 0.7, 4, 8]} />
        {material}
      </mesh>

      {/* Left Leg */}
      <mesh position={[-size * 0.2, size * -0.4, 0]} castShadow>
        <capsuleGeometry args={[size * 0.18, size * 0.8, 4, 8]} />
        {material}
      </mesh>

      {/* Right Leg */}
      <mesh position={[size * 0.2, size * -0.4, 0]} castShadow>
        <capsuleGeometry args={[size * 0.18, size * 0.8, 4, 8]} />
        {material}
      </mesh>

      {/* Glow effect */}
      <mesh position={[0, size * 0.5, 0]}>
        <sphereGeometry args={[size * 1.3, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.3}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  );
}

export default AgentHumanoid;
