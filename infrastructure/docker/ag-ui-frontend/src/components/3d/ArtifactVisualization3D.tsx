/**
 * ArtifactVisualization3D Component
 * 
 * Renders artifacts as floating 3D gems/objects near their creating agents
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface Artifact {
  id: string;
  agentId: string;
  name: string;
  type: string;
  data: string;
  position?: [number, number, number];
  createdAt: number;
}

interface ArtifactVisualization3DProps {
  artifact: Artifact;
  agentPosition?: [number, number, number];
}

export default function ArtifactVisualization3D({
  artifact,
  agentPosition,
}: ArtifactVisualization3DProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const startTime = useRef(Date.now());

  // Calculate artifact position near the agent
  const position = useMemo((): [number, number, number] => {
    if (artifact.position) return artifact.position;
    if (!agentPosition) return [0, 0, 0];
    
    const offset = new THREE.Vector3(
      (Math.random() - 0.5) * 4,
      Math.random() * 3 + 2,
      (Math.random() - 0.5) * 4
    );
    
    return [
      agentPosition[0] + offset.x,
      agentPosition[1] + offset.y,
      agentPosition[2] + offset.z,
    ];
  }, [artifact.position, agentPosition]);

  // Determine color based on artifact type - clean, professional colors
  const color = useMemo(() => {
    switch (artifact.type) {
      case 'text':
        return 0x3b82f6; // blue-500
      case 'json':
        return 0x8b5cf6; // purple-500
      case 'image':
        return 0x10b981; // green-500
      default:
        return 0xf59e0b; // yellow-500
    }
  }, [artifact.type]);

  const emissiveIntensity = 0.2;

  // Animation
  useFrame(() => {
    if (!meshRef.current) return;

    // Rotate artifact
    meshRef.current.rotation.x += 0.015;
    meshRef.current.rotation.y += 0.01;

    // Float upward
    meshRef.current.position.y += 0.01;

    // Check if artifact is too old (10 seconds) and fade out
    const age = Date.now() - startTime.current;
    if (age > 9000 && meshRef.current.material) {
      const fadeProgress = (age - 9000) / 1000;
      if ('opacity' in meshRef.current.material) {
        meshRef.current.material.opacity = Math.max(0, 1 - fadeProgress);
      }
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <octahedronGeometry args={[0.5]} />
      <meshPhongMaterial
        color={color}
        emissive={color}
        emissiveIntensity={emissiveIntensity}
        transparent
        opacity={0.7}
      />
    </mesh>
  );
}
