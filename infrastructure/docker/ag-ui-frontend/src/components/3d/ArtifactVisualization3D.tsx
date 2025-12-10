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

  // Determine color based on artifact type
  const color = useMemo(() => {
    switch (artifact.type) {
      case 'text':
        return 0x00ffff;
      case 'json':
        return 0xff00ff;
      case 'image':
        return 0x00ff00;
      default:
        return 0xffaa00;
    }
  }, [artifact.type]);

  // Animation
  useFrame((state) => {
    if (!meshRef.current) return;

    // Rotate artifact
    meshRef.current.rotation.x += 0.015;
    meshRef.current.rotation.y += 0.01;

    // Float upward
    meshRef.current.position.y += 0.01;

    // Check if artifact is too old (10 seconds) and fade out
    const age = Date.now() - startTime.current;
    if (age > 9000) {
      const fadeProgress = (age - 9000) / 1000;
      meshRef.current.material.opacity = Math.max(0, 1 - fadeProgress);
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <octahedronGeometry args={[0.5]} />
      <meshPhongMaterial
        color={color}
        emissive={color}
        emissiveIntensity={0.6}
        transparent
        opacity={0.8}
      />
    </mesh>
  );
}
