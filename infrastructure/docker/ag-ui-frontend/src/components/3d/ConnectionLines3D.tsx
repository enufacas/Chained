/**
 * ConnectionLines3D Component
 * 
 * Renders connection lines between selected agents in 3D space
 */

import * as THREE from 'three';
import { useMemo } from 'react';
import { Line } from '@react-three/drei';

interface ConnectionLines3DProps {
  positions: Array<[number, number, number]>;
  color?: number;
  opacity?: number;
}

export default function ConnectionLines3D({
  positions,
  color = 0x3b82f6,
  opacity = 0.6,
}: ConnectionLines3DProps) {
  const points = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i < positions.length; i++) {
      pts.push(new THREE.Vector3(...positions[i]));
    }
    return pts;
  }, [positions]);

  if (points.length < 2) return null;

  return (
    <Line
      points={points}
      color={color}
      lineWidth={2}
      transparent
      opacity={opacity}
    />
  );
}
