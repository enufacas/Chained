/**
 * AgentHumanoid3D Component
 * 
 * Renders a humanoid agent in 3D space with cyberpunk aesthetics.
 * Based on the humanoid shape from organism.html
 */

import { useRef, useMemo } from 'react';
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

  // Material for the humanoid
  const material = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color(color),
        emissive: new THREE.Color(color),
        emissiveIntensity: status === 'working' ? 0.8 : 0.6,
        metalness: 0.9,
        roughness: 0.1,
      }),
    [color, status]
  );

  // Visor material
  const visorMaterial = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: 0x00ffff,
        transparent: true,
        opacity: 0.8,
      }),
    []
  );

  // Glow material
  const glowMaterial = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: new THREE.Color(color),
        transparent: true,
        opacity: 0.3,
        side: THREE.BackSide,
      }),
    [color]
  );

  // Animation
  useFrame((state) => {
    if (!groupRef.current) return;

    // Floating animation
    floatOffset.current += 0.02;
    groupRef.current.position.y = originalY.current + Math.sin(floatOffset.current) * 1;

    // Working animation - gentle sway
    if (status === 'working') {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime) * 0.1;
      
      // Pulse emissive intensity
      const pulse = (Math.sin(state.clock.elapsedTime * 3) + 1) / 2;
      material.emissiveIntensity = 0.3 + pulse * 0.5;
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
      <mesh position={[0, size * 1.5, 0]} castShadow receiveShadow material={material}>
        <sphereGeometry args={[size * 0.4, 16, 16]} />
      </mesh>

      {/* Visor/Eyes */}
      <mesh position={[0, size * 1.5, size * 0.4]} material={visorMaterial}>
        <planeGeometry args={[size * 0.6, size * 0.15]} />
      </mesh>

      {/* Torso */}
      <mesh position={[0, size * 0.6, 0]} castShadow receiveShadow material={material}>
        <capsuleGeometry args={[size * 0.35, size * 0.8, 8, 16]} />
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
        material={material}
      >
        <capsuleGeometry args={[size * 0.15, size * 0.7, 4, 8]} />
      </mesh>

      {/* Right Arm */}
      <mesh
        position={[size * 0.55, size * 0.7, 0]}
        rotation={[0, 0, -Math.PI * 0.15]}
        castShadow
        receiveShadow
        material={material}
      >
        <capsuleGeometry args={[size * 0.15, size * 0.7, 4, 8]} />
      </mesh>

      {/* Left Leg */}
      <mesh
        position={[-size * 0.2, size * -0.4, 0]}
        castShadow
        receiveShadow
        material={material}
      >
        <capsuleGeometry args={[size * 0.18, size * 0.8, 4, 8]} />
      </mesh>

      {/* Right Leg */}
      <mesh
        position={[size * 0.2, size * -0.4, 0]}
        castShadow
        receiveShadow
        material={material}
      >
        <capsuleGeometry args={[size * 0.18, size * 0.8, 4, 8]} />
      </mesh>

      {/* Glow Effect */}
      <mesh position={[0, size * 0.5, 0]} material={glowMaterial}>
        <sphereGeometry args={[size * 1.3, 16, 16]} />
      </mesh>

      {/* Wireframe overlay for cyberpunk effect */}
      <mesh position={[0, size * 0.5, 0]}>
        <sphereGeometry args={[size * 1.1, 8, 8]} />
        <meshBasicMaterial
          color={color}
          wireframe
          transparent
          opacity={0.2}
        />
      </mesh>

      {/* Data ring around agent */}
      <mesh position={[0, size * 0.5, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[size * 1.4, size * 0.03, 8, 32]} />
        <meshBasicMaterial
          color={0x00ffff}
          transparent
          opacity={0.5}
        />
      </mesh>
    </group>
  );
}
