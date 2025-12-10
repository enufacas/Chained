/**
 * AgentHumanoid3D Component
 * 
 * Renders a humanoid agent in 3D space with cyberpunk aesthetics.
 * Based on the humanoid shape from organism.html
 */

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface AgentHumanoid3DProps {
  position: [number, number, number];
  color: number;
  size?: number;
  status?: 'idle' | 'working' | 'completed' | 'failed';
  onClick?: () => void;
  lookAt?: [number, number, number];
}

export default function AgentHumanoid3D({
  position,
  color,
  size = 1,
  status = 'idle',
  onClick,
  lookAt
}: AgentHumanoid3DProps) {
  const groupRef = useRef<THREE.Group>(null);
  const floatOffset = useRef(Math.random() * Math.PI * 2);
  const originalY = useRef(position[1]);

  // Calculate emissive intensity based on status
  const emissiveIntensity = status === 'working' ? 0.3 : 0.1;

  // Animation
  useFrame((state) => {
    if (!groupRef.current) return;

    // Floating animation
    floatOffset.current += 0.02;
    groupRef.current.position.y = originalY.current + Math.sin(floatOffset.current) * 1;

    // Working animation - gentle sway
    if (status === 'working') {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime) * 0.1;
    }

    // Make humanoid look at target
    if (lookAt && groupRef.current) {
      groupRef.current.lookAt(new THREE.Vector3(...lookAt));
    }
  });

  return (
    <group
      ref={groupRef}
      position={position}
      onClick={onClick}
      onPointerOver={() => document.body.style.cursor = 'pointer'}
      onPointerOut={() => document.body.style.cursor = 'default'}
    >
      {/* Head */}
      <mesh position={[0, size * 1.5, 0]} castShadow receiveShadow>
        <sphereGeometry args={[size * 0.4, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>

      {/* Visor/Eyes */}
      <mesh position={[0, size * 1.5, size * 0.4]}>
        <planeGeometry args={[size * 0.6, size * 0.15]} />
        <meshBasicMaterial
          color={0x3b82f6}
          transparent
          opacity={0.6}
        />
      </mesh>

      {/* Torso */}
      <mesh position={[0, size * 0.6, 0]} castShadow receiveShadow>
        <capsuleGeometry args={[size * 0.35, size * 0.8, 8, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>

      {/* Chest Light */}
      <mesh position={[0, size * 0.8, size * 0.35]}>
        <circleGeometry args={[size * 0.15, 8]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Left Arm */}
      <mesh
        position={[-size * 0.55, size * 0.7, 0]}
        rotation={[0, 0, Math.PI * 0.15]}
        castShadow
        receiveShadow
      >
        <capsuleGeometry args={[size * 0.15, size * 0.7, 4, 8]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>

      {/* Right Arm */}
      <mesh
        position={[size * 0.55, size * 0.7, 0]}
        rotation={[0, 0, -Math.PI * 0.15]}
        castShadow
        receiveShadow
      >
        <capsuleGeometry args={[size * 0.15, size * 0.7, 4, 8]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>

      {/* Left Leg */}
      <mesh
        position={[-size * 0.2, size * -0.4, 0]}
        castShadow
        receiveShadow
      >
        <capsuleGeometry args={[size * 0.18, size * 0.8, 4, 8]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>

      {/* Right Leg */}
      <mesh
        position={[size * 0.2, size * -0.4, 0]}
        castShadow
        receiveShadow
      >
        <capsuleGeometry args={[size * 0.18, size * 0.8, 4, 8]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>

      {/* Subtle highlight (minimal, not glowing) */}
      <mesh position={[0, size * 0.5, 0]}>
        <sphereGeometry args={[size * 1.15, 16, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.1}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  );
}
